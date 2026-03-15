#!/usr/bin/env python3
"""
FACEBOOK LEAD ADS WEBHOOK HANDLER — The Call Taker
=====================================================
Receives Facebook Lead Ads webhook events and:
  1. Verifies the GET challenge (Facebook ownership verification)
  2. Verifies the POST HMAC-SHA256 signature (Facebook App Secret)
  3. Fetches full lead field data from the Leads Retrieval API
  4. Creates a GHL contact with tags: facebook-lead, hot-lead, pilot-candidate, [industry]
  5. Adds a contact note: "Source: Facebook Lead Ad - [industry]"
  6. Fires ntfy URGENT alert: "[CRITICAL] Facebook Lead: [name] from [company] - [industry]"
  7. Sends immediate SMS welcome to the lead via GHL

Port: 5091  (Stripe webhook is on 5090 — do not conflict)
State: ~/thecalltaker/ops/facebook-lead-state.json
Log:   ~/thecalltaker/ops/facebook-lead-webhook.log

Environment variables (required):
  FB_VERIFY_TOKEN      — string you chose when setting up the Meta webhook subscription
  FB_APP_SECRET        — from Meta App Settings → Basic
  FB_PAGE_ACCESS_TOKEN — long-lived Page Access Token (refresh every 60 days)
  TCT_GHL_API_KEY      — defaults to hardcoded key if not set
  TCT_GHL_LOCATION_ID  — defaults to hardcoded location if not set

Commands:
  python3 facebook-lead-webhook.py          — start server (default)
  python3 facebook-lead-webhook.py status   — print state summary
  python3 facebook-lead-webhook.py leads    — list recent leads
  python3 facebook-lead-webhook.py test     — send a test ntfy alert

Setup:
  1. Set env vars above
  2. Run this script (or load via launchd plist)
  3. Expose port 5091 publicly (ngrok, Cloudflare Tunnel, or reverse proxy)
  4. In Meta App → Webhooks → Callback URL: https://thecalltaker.com/api/facebook-leads
  5. Subscribe to the `leadgen` field on your Page
  6. Click "Test" in Meta dashboard — lead should appear in GHL within 30 seconds
"""

import os
import sys
import json
import hmac
import hashlib
import time
import logging
import requests
import traceback
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ─── PATH SETUP ──────────────────────────────────────────────────────────────
# Allow importing from thecalltaker-ops/ops if tct_common is available
sys.path.insert(0, os.path.expanduser("~/thecalltaker-ops/ops"))

# ─── CONFIGURATION ───────────────────────────────────────────────────────────

PORT = 5091

# Facebook credentials — set via environment variables
FB_VERIFY_TOKEN      = os.environ.get("FB_VERIFY_TOKEN", "")
FB_APP_SECRET        = os.environ.get("FB_APP_SECRET", "")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")

# GHL credentials
GHL_API_KEY     = os.environ.get("TCT_GHL_API_KEY",      "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID",  "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL    = "https://services.leadconnectorhq.com"

# Demo line number (the live AI receptionist)
DEMO_LINE = "(615) 784-5747"
WALLACE_GHL_ID = "DtKLG28VzgUb6q3brILD"

# ntfy topics
NTFY_URGENT = "tct-urgent-Hk9UOEZR"
NTFY_SYSTEM = "tct-system-vRsfXQRQ"

# File paths — use absolute paths so launchd finds them from any cwd
BASE_DIR   = os.path.expanduser("~/thecalltaker/ops")
LOG_FILE   = os.path.join(BASE_DIR, "facebook-lead-webhook.log")
STATE_FILE = os.path.join(BASE_DIR, "facebook-lead-state.json")

# Facebook Graph API base
FB_GRAPH = "https://graph.facebook.com/v19.0"

# Industry display names for mapping form dropdown values to GHL tags
INDUSTRY_MAP = {
    "hvac":             {"tag": "hvac",            "display": "HVAC",              "job": "service call"},
    "plumbing":         {"tag": "plumbing",        "display": "Plumbing",          "job": "service call"},
    "electrical":       {"tag": "electrical",      "display": "Electrical",        "job": "service call"},
    "dental":           {"tag": "dental",          "display": "Dental",            "job": "appointment"},
    "roofing":          {"tag": "roofing",         "display": "Roofing",           "job": "estimate"},
    "locksmith":        {"tag": "locksmith",       "display": "Locksmith",         "job": "job"},
    "pest control":     {"tag": "pest-control",    "display": "Pest Control",      "job": "service call"},
    "towing":           {"tag": "towing",          "display": "Towing",            "job": "call"},
    "med spa":          {"tag": "med-spa",         "display": "Med Spa",           "job": "appointment"},
    "legal":            {"tag": "legal",           "display": "Legal",             "job": "consultation"},
    "veterinary":       {"tag": "veterinary",      "display": "Veterinary",        "job": "appointment"},
    "auto repair":      {"tag": "auto-repair",     "display": "Auto Repair",       "job": "appointment"},
    "cleaning":         {"tag": "cleaning",        "display": "Cleaning",          "job": "booking"},
    "property mgmt":    {"tag": "property-mgmt",   "display": "Property Mgmt",     "job": "inquiry"},
    "water damage":     {"tag": "water-damage",    "display": "Water Damage",      "job": "emergency call"},
    "landscaping":      {"tag": "landscaping",     "display": "Landscaping",       "job": "estimate"},
    "general contractor":{"tag": "general-contractor","display": "General Contractor","job": "estimate"},
    "other":            {"tag": "other-industry",  "display": "Other",             "job": "call"},
}


# ─── LOGGING ─────────────────────────────────────────────────────────────────

def setup_logger():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logger = logging.getLogger("fb-webhook")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        # File handler
        fh = logging.FileHandler(LOG_FILE)
        fh.setLevel(logging.DEBUG)
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] fb-webhook: %(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger

logger = setup_logger()


# ─── STATE MANAGEMENT ────────────────────────────────────────────────────────

def load_state():
    """Load state file. Returns default state if missing or corrupt."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"State load error: {e} — resetting state")
    return {
        "total_leads":     0,
        "leads_today":     0,
        "leads_this_month": 0,
        "ghl_created":     0,
        "ghl_errors":      0,
        "sms_sent":        0,
        "last_lead_at":    None,
        "last_lead_name":  None,
        "last_lead_company": None,
        "leads":           [],         # last 50 leads
        "duplicate_skips": 0,
        "processed_lead_ids": [],      # dedupe list (last 200)
        "date":            datetime.now().strftime("%Y-%m-%d"),
    }


def save_state(state):
    """Atomic state write using temp file + os.replace."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, STATE_FILE)
    except Exception as e:
        logger.error(f"State save error: {e}")


def reset_daily_counts_if_needed(state):
    """Reset daily lead count at midnight."""
    today = datetime.now().strftime("%Y-%m-%d")
    if state.get("date") != today:
        state["leads_today"] = 0
        state["date"] = today
    return state


# ─── NTFY NOTIFICATIONS ───────────────────────────────────────────────────────

def ntfy(topic, title, message, priority="default", tags=None):
    """Send a push notification via ntfy.sh."""
    headers = {
        "Title":    title[:250],
        "Priority": priority,
    }
    if tags:
        headers["Tags"] = ",".join(tags) if isinstance(tags, list) else str(tags)
    try:
        resp = requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers=headers,
            timeout=10,
        )
        if resp.status_code != 200:
            logger.warning(f"ntfy returned {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"ntfy send error: {e}")


def ntfy_facebook_lead(name, company, industry_display, phone, email):
    """Fire URGENT ntfy alert for a new Facebook lead."""
    title   = f"[CRITICAL] Facebook Lead: {name} from {company}"
    message = (
        f"Industry: {industry_display}\n"
        f"Phone: {phone}\n"
        f"Email: {email}\n"
        f"Source: Facebook Lead Ad\n"
        f"Action: Donny speed-to-lead firing — respond within 5 minutes"
    )
    ntfy(NTFY_URGENT, title, message, priority="urgent", tags=["loudspeaker", "facebook"])


# ─── GHL API ─────────────────────────────────────────────────────────────────

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version":       "2021-07-28",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
    "User-Agent":    "TheCallTaker-FacebookWebhook/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version":       "2021-04-15",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
    "User-Agent":    "TheCallTaker-FacebookWebhook/1.0",
}


def ghl_request(method, path, headers=None, params=None, json_body=None, retries=3):
    """
    GHL API request with retry + rate-limit handling.
    Uses 5s/15s/30s backoff on 5xx, 30s/60s/120s on 429.
    """
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    delays = [5, 15, 30]
    rate_delays = [30, 60, 120]

    for attempt in range(retries):
        try:
            resp = requests.request(
                method, url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=30,
            )
            if resp.status_code == 429:
                wait = rate_delays[min(attempt, len(rate_delays) - 1)]
                logger.warning(f"GHL 429 rate limit on {path} — waiting {wait}s")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                wait = delays[min(attempt, len(delays) - 1)]
                logger.warning(f"GHL {resp.status_code} on {path} — retry in {wait}s")
                time.sleep(wait)
                continue
            try:
                return resp.json() if resp.text else {}
            except json.JSONDecodeError:
                return {"_raw": resp.text}
        except requests.exceptions.RequestException as e:
            wait = delays[min(attempt, len(delays) - 1)]
            logger.error(f"GHL request exception on {path}: {e} — retry in {wait}s")
            time.sleep(wait)

    logger.error(f"GHL request failed after {retries} attempts: {method} {path}")
    return None


def find_contact_by_phone(phone):
    """Search GHL for existing contact by phone number."""
    # Normalize phone to +1XXXXXXXXXX
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    normalized = "+" + digits if not digits.startswith("+") else digits

    data = ghl_request("GET", "/contacts/", params={
        "locationId": GHL_LOCATION_ID,
        "query":      normalized,
        "limit":      1,
    })
    if data and "contacts" in data and data["contacts"]:
        return data["contacts"][0]
    return None


def find_contact_by_email(email):
    """Search GHL for existing contact by email."""
    data = ghl_request("GET", "/contacts/", params={
        "locationId": GHL_LOCATION_ID,
        "query":      email,
        "limit":      1,
    })
    if data and "contacts" in data and data["contacts"]:
        return data["contacts"][0]
    return None


def create_ghl_contact(name, phone, email, company, industry_tag, industry_display):
    """
    Create a new GHL contact with Facebook lead tags.
    Returns (contact_id, created_new) or (None, False) on failure.
    """
    # Normalize phone to E.164
    digits = "".join(c for c in (phone or "") if c.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    phone_e164 = ("+" + digits) if digits else None

    # Build name parts
    parts = (name or "").strip().split(None, 1)
    first = parts[0] if parts else "Unknown"
    last  = parts[1] if len(parts) > 1 else ""

    tags = ["facebook-lead", "hot-lead", "pilot-candidate"]
    if industry_tag:
        tags.append(industry_tag)

    payload = {
        "locationId":  GHL_LOCATION_ID,
        "firstName":   first,
        "lastName":    last,
        "companyName": company or "",
        "source":      "Facebook Lead Ad",
        "tags":        tags,
    }
    if phone_e164:
        payload["phone"] = phone_e164
    if email:
        payload["email"] = email

    data = ghl_request("POST", "/contacts/", json_body=payload)
    if data and "contact" in data:
        return data["contact"]["id"], True
    if data and "id" in data:
        return data["id"], True
    logger.error(f"GHL contact creation failed. Response: {data}")
    return None, False


def add_contact_tags(contact_id, tags):
    """Add tags to an existing GHL contact."""
    return ghl_request("POST", f"/contacts/{contact_id}/tags",
                        json_body={"tags": tags})


def add_contact_note(contact_id, note_text):
    """Add a note to a GHL contact."""
    return ghl_request("POST", f"/contacts/{contact_id}/notes",
                        json_body={"body": note_text})


def get_or_create_conversation(contact_id):
    """Get or create a GHL conversation for SMS."""
    data = ghl_request(
        "POST",
        "/conversations/",
        headers=CONVERSATIONS_HEADERS,
        json_body={
            "locationId": GHL_LOCATION_ID,
            "contactId":  contact_id,
        },
    )
    if data and "conversation" in data:
        return data["conversation"].get("id")
    if data and "id" in data:
        return data["id"]
    return None


def send_sms(contact_id, phone, name, company, industry_display):
    """
    Send immediate SMS welcome message via GHL conversations API.
    Uses the job word for the industry for slightly more personalized copy.
    """
    # Normalize phone
    digits = "".join(c for c in (phone or "") if c.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    phone_e164 = ("+" + digits) if digits else None

    if not phone_e164:
        logger.warning(f"Cannot send SMS — no valid phone for contact {contact_id}")
        return False

    first_name = (name or "").split()[0] if name else "there"
    company_str = company or "your business"
    industry_str = industry_display.lower() if industry_display else "your industry"

    message = (
        f"Hey {first_name}! Thanks for reaching out. "
        f"We help {industry_str} businesses like {company_str} never miss another call. "
        f"Want to hear your receptionist live? Call {DEMO_LINE} "
        f"or reply YES for a free 14-day pilot."
    )

    # Get or create conversation
    convo_id = get_or_create_conversation(contact_id)
    if not convo_id:
        logger.error(f"Could not get conversation for contact {contact_id}")
        return False

    resp = ghl_request(
        "POST",
        f"/conversations/{convo_id}/messages",
        headers=CONVERSATIONS_HEADERS,
        json_body={
            "type":    "SMS",
            "message": message,
        },
    )
    if resp is not None:
        logger.info(f"SMS sent to {phone_e164} ({first_name} at {company_str})")
        return True
    else:
        logger.error(f"SMS send failed for contact {contact_id}")
        return False


# ─── FACEBOOK GRAPH API ───────────────────────────────────────────────────────

def fetch_lead_data(lead_id):
    """
    Fetch full lead field data from Facebook Leads Retrieval API.
    Returns a dict of field_name → value, or empty dict on failure.
    """
    if not FB_PAGE_ACCESS_TOKEN:
        logger.warning("FB_PAGE_ACCESS_TOKEN not set — cannot fetch lead field data")
        return {}
    try:
        url  = f"{FB_GRAPH}/{lead_id}"
        resp = requests.get(url, params={
            "fields":       "field_data,created_time,ad_id,form_id",
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }, timeout=15)
        if resp.status_code != 200:
            logger.error(f"Facebook lead fetch HTTP {resp.status_code}: {resp.text[:300]}")
            return {}
        data = resp.json()
        field_data = data.get("field_data", [])
        result = {}
        for field in field_data:
            name   = field.get("name", "").lower().strip()
            values = field.get("values", [])
            result[name] = values[0] if values else ""
        logger.debug(f"Lead {lead_id} fields: {list(result.keys())}")
        return result
    except Exception as e:
        logger.error(f"fetch_lead_data error for {lead_id}: {e}")
        return {}


def parse_lead_fields(fields):
    """
    Extract standardized fields from the Facebook lead form field_data dict.
    Handles common field name variations from different form configurations.
    Returns: (name, phone, email, company, industry_raw)
    """
    def get(*keys):
        for k in keys:
            v = fields.get(k, "").strip()
            if v:
                return v
        return ""

    name     = get("full_name", "name", "first_name")
    # If only first_name captured, try to append last_name
    if not name and fields.get("first_name"):
        last  = fields.get("last_name", "").strip()
        name  = (fields.get("first_name", "").strip() + " " + last).strip()

    phone    = get("phone_number", "phone", "mobile_number", "contact_number")
    email    = get("email", "email_address", "work_email")
    company  = get("company_name", "business_name", "company", "business")
    industry = get("industry", "business_type", "business_industry", "service_type")

    return name, phone, email, company, industry


def normalize_industry(raw):
    """
    Map a raw industry string from the lead form to a known industry key.
    Returns (tag, display_name, job_word).
    """
    raw_lower = (raw or "").lower().strip()
    # Direct key match
    if raw_lower in INDUSTRY_MAP:
        m = INDUSTRY_MAP[raw_lower]
        return m["tag"], m["display"], m["job"]
    # Substring match
    for key, info in INDUSTRY_MAP.items():
        if key in raw_lower or raw_lower in key:
            return info["tag"], info["display"], info["job"]
    # Default fallback
    tag = raw_lower.replace(" ", "-")[:30] if raw_lower else "other-industry"
    return tag, raw.title() if raw else "Other", "call"


# ─── SIGNATURE VERIFICATION ──────────────────────────────────────────────────

def verify_facebook_signature(payload_bytes, signature_header):
    """
    Verify the X-Hub-Signature-256 header from Facebook.
    Format: sha256=<hex_digest>
    Uses the App Secret as the HMAC key.
    """
    if not FB_APP_SECRET:
        logger.warning("FB_APP_SECRET not set — skipping signature verification")
        return True  # Permissive until secret is configured

    if not signature_header:
        logger.error("Missing X-Hub-Signature-256 header")
        return False

    # Header format: "sha256=abcdef..."
    if not signature_header.startswith("sha256="):
        logger.error(f"Unexpected signature format: {signature_header[:50]}")
        return False

    received_sig = signature_header[7:]  # strip "sha256="
    expected_sig = hmac.new(
        FB_APP_SECRET.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    valid = hmac.compare_digest(expected_sig, received_sig)
    if not valid:
        logger.error("Signature mismatch — request may be tampered or App Secret is wrong")
    return valid


# ─── LEAD PROCESSING ─────────────────────────────────────────────────────────

def process_lead(lead_id, state):
    """
    Full lead processing pipeline for a single Facebook lead ID:
      1. Dedupe check
      2. Fetch field data from Graph API
      3. Parse fields
      4. Find or create GHL contact
      5. Add note
      6. Send ntfy URGENT
      7. Send SMS
    Returns True if successfully processed, False otherwise.
    """
    # Dedupe — skip if we've already processed this lead ID
    processed_ids = state.get("processed_lead_ids", [])
    if lead_id in processed_ids:
        logger.info(f"Duplicate lead ID {lead_id} — skipping")
        state["duplicate_skips"] = state.get("duplicate_skips", 0) + 1
        return False

    logger.info(f"Processing lead ID: {lead_id}")

    # ── Fetch lead fields from Graph API ──────────────────────────────────
    fields = fetch_lead_data(lead_id)

    # If token not set or fetch failed, we only have the lead_id
    # We still create a placeholder GHL contact so Wallace can follow up
    if not fields:
        logger.warning(f"No field data for lead {lead_id} — creating placeholder contact")
        fields = {}

    name, phone, email, company, industry_raw = parse_lead_fields(fields)

    # Fallback values
    name    = name    or "Facebook Lead"
    company = company or "Unknown Business"
    email   = email   or ""

    industry_tag, industry_display, job_word = normalize_industry(industry_raw)

    logger.info(f"Lead parsed — name={name!r} phone={phone!r} email={email!r} "
                f"company={company!r} industry={industry_display!r}")

    # ── GHL contact lookup / creation ─────────────────────────────────────
    existing_contact = None
    contact_id = None

    # Check for existing contact by phone first, then email
    if phone:
        existing_contact = find_contact_by_phone(phone)
    if not existing_contact and email:
        existing_contact = find_contact_by_email(email)

    if existing_contact:
        contact_id = existing_contact.get("id")
        logger.info(f"Found existing GHL contact {contact_id} — adding tags")
        tags_to_add = ["facebook-lead", "hot-lead", "pilot-candidate"]
        if industry_tag:
            tags_to_add.append(industry_tag)
        add_contact_tags(contact_id, tags_to_add)
        state["ghl_created"] = state.get("ghl_created", 0)  # not a new creation
    else:
        contact_id, created = create_ghl_contact(
            name, phone, email, company, industry_tag, industry_display
        )
        if created:
            logger.info(f"Created new GHL contact {contact_id}")
            state["ghl_created"] = state.get("ghl_created", 0) + 1
        else:
            logger.error(f"Failed to create GHL contact for lead {lead_id}")
            state["ghl_errors"] = state.get("ghl_errors", 0) + 1
            # Still record the lead so we don't retry forever
            _record_lead(state, lead_id, name, company, industry_display, phone, email, "ghl_error")
            return False

    # ── Add contact note ──────────────────────────────────────────────────
    note = (
        f"Source: Facebook Lead Ad - {industry_display}\n"
        f"Lead ID: {lead_id}\n"
        f"Received: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"Raw industry field: {industry_raw or '(not provided)'}"
    )
    add_contact_note(contact_id, note)

    # ── ntfy URGENT alert ─────────────────────────────────────────────────
    ntfy_facebook_lead(name, company, industry_display, phone, email)

    # ── SMS welcome ───────────────────────────────────────────────────────
    sms_sent = False
    if phone:
        sms_sent = send_sms(contact_id, phone, name, company, industry_display)
        if sms_sent:
            state["sms_sent"] = state.get("sms_sent", 0) + 1

    # ── Update state ──────────────────────────────────────────────────────
    _record_lead(state, lead_id, name, company, industry_display, phone, email, "ok")
    state["total_leads"]      = state.get("total_leads", 0) + 1
    state["leads_today"]      = state.get("leads_today", 0) + 1
    state["leads_this_month"] = state.get("leads_this_month", 0) + 1
    state["last_lead_at"]     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["last_lead_name"]   = name
    state["last_lead_company"]= company

    # Keep dedup list bounded to 200 entries
    processed_ids.append(lead_id)
    state["processed_lead_ids"] = processed_ids[-200:]

    logger.info(
        f"Lead processed OK — {name} @ {company} ({industry_display}) | "
        f"contact_id={contact_id} | sms={sms_sent}"
    )
    return True


def _record_lead(state, lead_id, name, company, industry, phone, email, status):
    """Append a lead summary to the state leads list (keep last 50)."""
    leads = state.get("leads", [])
    leads.append({
        "lead_id":   lead_id,
        "name":      name,
        "company":   company,
        "industry":  industry,
        "phone":     phone,
        "email":     email,
        "status":    status,
        "received":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    state["leads"] = leads[-50:]


# ─── HTTP REQUEST HANDLER ─────────────────────────────────────────────────────

class FacebookWebhookHandler(BaseHTTPRequestHandler):
    """
    HTTP handler for Facebook webhook events.

    GET  /webhook/facebook-leads  — Facebook verification challenge
    POST /webhook/facebook-leads  — Facebook lead event payload
    """

    # Silence the default request logging to stdout — we use our own logger
    def log_message(self, fmt, *args):
        logger.debug(f"HTTP {self.address_string()} — " + fmt % args)

    def send_json(self, status_code, body):
        response = json.dumps(body).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def send_text(self, status_code, text):
        body = text.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── Route dispatcher ──────────────────────────────────────────────────

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")

        if path in ("/webhook/facebook-leads", "/api/facebook-leads"):
            self._handle_verification(parsed)
        elif path == "/health":
            self.send_text(200, "ok")
        elif path == "/status":
            self._handle_status()
        else:
            self.send_text(404, "not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")

        if path in ("/webhook/facebook-leads", "/api/facebook-leads"):
            self._handle_webhook()
        else:
            self.send_text(404, "not found")

    # ── GET: Facebook verification challenge ─────────────────────────────

    def _handle_verification(self, parsed):
        """
        Facebook sends a GET with hub.mode=subscribe, hub.verify_token, and hub.challenge.
        We must respond with hub.challenge if the verify token matches.
        """
        params = parse_qs(parsed.query)

        mode      = params.get("hub.mode",         [""])[0]
        token     = params.get("hub.verify_token",  [""])[0]
        challenge = params.get("hub.challenge",     [""])[0]

        if mode == "subscribe" and token == FB_VERIFY_TOKEN:
            logger.info(f"Webhook verification challenge accepted")
            self.send_text(200, challenge)
        else:
            logger.warning(
                f"Webhook verification failed — "
                f"mode={mode!r} token_match={token == FB_VERIFY_TOKEN}"
            )
            if not FB_VERIFY_TOKEN:
                logger.error("FB_VERIFY_TOKEN env var is not set")
            self.send_text(403, "Verification failed")

    # ── POST: Facebook lead event ─────────────────────────────────────────

    def _handle_webhook(self):
        """
        Receive and process a Facebook lead event POST.
        Payload structure:
          {
            "object": "page",
            "entry": [{
              "id": "<page_id>",
              "time": 1234567890,
              "changes": [{
                "field": "leadgen",
                "value": {
                  "leadgen_id": "<lead_id>",
                  "page_id": "<page_id>",
                  "form_id": "<form_id>",
                  "adgroup_id": "<adgroup_id>",
                  "ad_id": "<ad_id>",
                  "created_time": 1234567890
                }
              }]
            }]
          }
        """
        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b""

        # Verify HMAC signature
        signature = self.headers.get("X-Hub-Signature-256", "")
        if not verify_facebook_signature(raw_body, signature):
            logger.error("Signature verification failed — rejecting webhook")
            self.send_text(403, "Signature verification failed")
            return

        # Parse JSON
        try:
            data = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as e:
            logger.error(f"Webhook JSON parse error: {e}")
            self.send_text(400, "Invalid JSON")
            return

        logger.debug(f"Webhook payload: {json.dumps(data)[:500]}")

        # Must respond 200 quickly — Facebook times out in 20 seconds
        # and retries up to 3 times if we don't respond
        self.send_text(200, "EVENT_RECEIVED")

        # Process leads in the payload
        if data.get("object") != "page":
            logger.info(f"Ignoring non-page webhook object: {data.get('object')}")
            return

        state = load_state()
        state = reset_daily_counts_if_needed(state)

        leads_processed = 0
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") != "leadgen":
                    continue
                value   = change.get("value", {})
                lead_id = str(value.get("leadgen_id", ""))
                if not lead_id:
                    logger.warning(f"No leadgen_id in change value: {value}")
                    continue
                try:
                    ok = process_lead(lead_id, state)
                    if ok:
                        leads_processed += 1
                except Exception as e:
                    logger.error(f"process_lead exception for {lead_id}: {e}\n{traceback.format_exc()}")
                    ntfy(NTFY_SYSTEM,
                         "[CRITICAL] FB Webhook Processing Error",
                         f"lead_id={lead_id}\nerror={e}",
                         priority="urgent")

        save_state(state)
        if leads_processed > 0:
            logger.info(f"Webhook batch complete — {leads_processed} lead(s) processed")

    # ── GET /status ───────────────────────────────────────────────────────

    def _handle_status(self):
        """Return a JSON status snapshot."""
        state = load_state()
        self.send_json(200, {
            "service":         "facebook-lead-webhook",
            "port":            PORT,
            "total_leads":     state.get("total_leads", 0),
            "leads_today":     state.get("leads_today", 0),
            "ghl_created":     state.get("ghl_created", 0),
            "ghl_errors":      state.get("ghl_errors", 0),
            "sms_sent":        state.get("sms_sent", 0),
            "duplicate_skips": state.get("duplicate_skips", 0),
            "last_lead_at":    state.get("last_lead_at"),
            "last_lead_name":  state.get("last_lead_name"),
            "last_lead_company": state.get("last_lead_company"),
            "config": {
                "fb_verify_token_set":      bool(FB_VERIFY_TOKEN),
                "fb_app_secret_set":        bool(FB_APP_SECRET),
                "fb_page_access_token_set": bool(FB_PAGE_ACCESS_TOKEN),
            },
        })


# ─── CLI COMMANDS ─────────────────────────────────────────────────────────────

def cmd_status():
    """Print a human-readable status summary."""
    state = load_state()
    print("\n=== Facebook Lead Webhook — Status ===")
    print(f"  Total leads received : {state.get('total_leads', 0)}")
    print(f"  Leads today          : {state.get('leads_today', 0)}")
    print(f"  Leads this month     : {state.get('leads_this_month', 0)}")
    print(f"  GHL contacts created : {state.get('ghl_created', 0)}")
    print(f"  GHL errors           : {state.get('ghl_errors', 0)}")
    print(f"  SMS sent             : {state.get('sms_sent', 0)}")
    print(f"  Duplicate skips      : {state.get('duplicate_skips', 0)}")
    print(f"  Last lead at         : {state.get('last_lead_at', 'never')}")
    print(f"  Last lead            : {state.get('last_lead_name', '-')} @ {state.get('last_lead_company', '-')}")
    print(f"\nConfig:")
    print(f"  FB_VERIFY_TOKEN      : {'SET' if FB_VERIFY_TOKEN else 'NOT SET (required)'}")
    print(f"  FB_APP_SECRET        : {'SET' if FB_APP_SECRET else 'NOT SET (webhook will skip sig check)'}")
    print(f"  FB_PAGE_ACCESS_TOKEN : {'SET' if FB_PAGE_ACCESS_TOKEN else 'NOT SET (lead fields will be empty)'}")
    print(f"  GHL API Key          : {GHL_API_KEY[:20]}...")
    print(f"  GHL Location         : {GHL_LOCATION_ID}")
    print(f"\nState file           : {STATE_FILE}")
    print(f"Log file             : {LOG_FILE}")
    print()


def cmd_leads():
    """Print the last 20 leads."""
    state = load_state()
    leads = state.get("leads", [])
    if not leads:
        print("No leads recorded yet.")
        return
    print(f"\n=== Last {min(len(leads), 20)} Facebook Leads ===\n")
    for lead in reversed(leads[-20:]):
        status_icon = "OK" if lead.get("status") == "ok" else "ERR"
        print(
            f"  [{status_icon}] {lead.get('received', '')}  "
            f"{lead.get('name', 'Unknown'):<25}  "
            f"{lead.get('company', ''):<30}  "
            f"{lead.get('industry', ''):<15}  "
            f"{lead.get('phone', '')}"
        )
    print()


def cmd_test():
    """Send a test ntfy URGENT alert to confirm the topic is working."""
    print("Sending test ntfy URGENT alert...")
    ntfy(
        NTFY_URGENT,
        "[TEST] Facebook Lead Webhook Online",
        f"facebook-lead-webhook.py is running on port {PORT}.\n"
        f"FB_VERIFY_TOKEN set: {bool(FB_VERIFY_TOKEN)}\n"
        f"FB_APP_SECRET set: {bool(FB_APP_SECRET)}\n"
        f"FB_PAGE_ACCESS_TOKEN set: {bool(FB_PAGE_ACCESS_TOKEN)}",
        priority="high",
        tags=["white_check_mark"],
    )
    print("Test alert sent to tct-urgent-Hk9UOEZR")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    """Parse CLI args and either run the server or a command."""
    command = sys.argv[1] if len(sys.argv) > 1 else "server"

    if command == "status":
        cmd_status()
        return

    if command == "leads":
        cmd_leads()
        return

    if command == "test":
        cmd_test()
        return

    if command not in ("server", "start"):
        print(f"Unknown command: {command!r}")
        print("Usage: python3 facebook-lead-webhook.py [server|status|leads|test]")
        sys.exit(1)

    # ── Startup warnings ──────────────────────────────────────────────────
    if not FB_VERIFY_TOKEN:
        logger.warning(
            "FB_VERIFY_TOKEN is not set — "
            "Facebook webhook verification challenges will be rejected"
        )
    if not FB_APP_SECRET:
        logger.warning(
            "FB_APP_SECRET is not set — "
            "incoming webhook signatures will NOT be verified (insecure)"
        )
    if not FB_PAGE_ACCESS_TOKEN:
        logger.warning(
            "FB_PAGE_ACCESS_TOKEN is not set — "
            "lead field data cannot be fetched from Graph API. "
            "Contacts will be created with placeholder data only."
        )

    # ── Start server ──────────────────────────────────────────────────────
    server = HTTPServer(("0.0.0.0", PORT), FacebookWebhookHandler)
    logger.info(f"Facebook Lead Webhook server listening on port {PORT}")
    logger.info(f"Webhook URL: POST /webhook/facebook-leads (or /api/facebook-leads)")
    logger.info(f"State file:  {STATE_FILE}")
    logger.info(f"Log file:    {LOG_FILE}")

    # Send startup ntfy so Wallace knows it's running
    ntfy(
        NTFY_SYSTEM,
        "Facebook Lead Webhook Started",
        f"Listening on port {PORT}\nWebhook: /api/facebook-leads",
        priority="default",
        tags=["white_check_mark"],
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Webhook server stopped by keyboard interrupt")
        server.server_close()


if __name__ == "__main__":
    main()
