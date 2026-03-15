#!/usr/bin/env python3
"""
SPEED-TO-LEAD v2 ENGINE — The Call Taker
=========================================
15-second hot-tier monitoring with Bland.ai call queue, dead lead resurrection,
and full action logging. Replaces the original speed-alert.py 60-second checker.

HOT SIGNAL DETECTION (every 15 seconds):
  - Email opened 2+ times (GHL message events)
  - CTA link clicked
  - Pilot form filled (tagged pilot-signup or calculator-lead)
  - Demo line caller (tagged demo-caller)
  - Inbound reply with hot keywords

HOT LEAD RESPONSE SEQUENCE:
  T+0s  : Tag HOT in GHL, move to hot pipeline stage
  T+60s : Personalized SMS referencing what they were looking at
  T+5m  : Bland.ai call attempt
  T+10m : Follow-up email

DEAD LEAD RESURRECTION (resurrect command):
  Conditions: hot-lead tag + no activity 14+ days + not excluded
  Sequence: 3 emails over 5 days
    Email 1 (Day 0):  Social proof angle
    Email 2 (Day 2):  ROI calculator angle
    Email 3 (Day 5):  Competitor angle

Commands:
  watch      — Continuous 15-second monitoring (main mode)
  check      — Single pass hot signal check
  resurrect  — Run dead lead resurrection scan + send
  status     — Show engine stats
  test       — Dry-run detection without sending

State: ~/thecalltaker/ops/speed-to-lead-state.json
Log  : ~/thecalltaker/ops/speed-to-lead.log
Speed: ~/thecalltaker/ops/speed-log.json
"""

import sys
import os
import json
import time
import re
import requests
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────

GHL_API_KEY      = os.environ.get("TCT_GHL_API_KEY",   "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID  = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
BLAND_API_KEY    = os.environ.get("TCT_BLAND_API_KEY",
    "org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969")
GHL_BASE_URL     = "https://services.leadconnectorhq.com"
BLAND_CALLS_URL  = "https://api.bland.ai/v1/calls"
BOOKING_URL      = "https://thecalltaker.com/book.html"
DEMO_LINE        = "(615) 784-5747"
DEMO_LINE_DIGITS = "+16157845747"
BUSINESS_EMAIL   = "thecalltakerai@gmail.com"
WALLACE_PHONE    = "+16156539004"
WALLACE_GHL_ID   = "DtKLG28VzgUb6q3brILD"

NTFY_URGENT      = "tct-urgent-Hk9UOEZR"
NTFY_ACTIVITY    = "tct-activity-cn1Aqa85"
NTFY_SYSTEM      = "tct-system-vRsfXQRQ"

STATE_FILE       = os.path.expanduser("~/thecalltaker/ops/speed-to-lead-state.json")
SPEED_LOG_FILE   = os.path.expanduser("~/thecalltaker/ops/speed-log.json")
LOG_FILE         = os.path.expanduser("~/thecalltaker/ops/speed-to-lead.log")

# Timing windows (seconds)
SMS_WINDOW_SEC   = 60    # fire SMS within 60s of detection
CALL_WINDOW_SEC  = 300   # fire Bland.ai call within 5 min
EMAIL_WINDOW_SEC = 600   # fire email within 10 min

# Resurrection intervals
RESURRECT_DAYS_COLD  = 14   # days since last activity to qualify
RESURRECT_EMAIL_2_DAYS = 2  # Email 2 fires 2 days after Email 1
RESURRECT_EMAIL_3_DAYS = 5  # Email 3 fires 5 days after Email 1

# Hot keywords for reply detection
HOT_KEYWORDS = {
    "interested", "pricing", "price", "demo", "sign me up", "ready",
    "how much", "schedule", "book", "sign up", "let's do it", "let's go",
    "i'm in", "im in", "tell me more", "send info", "sounds good",
    "what's included", "whats included", "trial", "pilot", "free",
    "can you call", "call me", "set it up", "when can", "available",
}

# Tags that exclude a contact from hot treatment
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "donny-closing",
}

# Tags that mean the resurrection should be skipped
RESURRECT_EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "resurrection-seq",
}

# ─── GHL Headers ──────────────────────────────────────────────────────────────

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-SpeedToLeadV2/2.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-SpeedToLeadV2/2.0",
}

# ─── Industry Map ─────────────────────────────────────────────────────────────

INDUSTRY_MAP = {
    "hvac": ("service call", "$350"),
    "plumbing": ("service call", "$300"),
    "electrical": ("service call", "$275"),
    "roofing": ("roof job", "$5,000"),
    "locksmith": ("emergency call", "$250"),
    "dental": ("appointment", "$400"),
    "medspa": ("appointment", "$500"),
    "legal": ("case consultation", "$500"),
    "veterinary": ("appointment", "$200"),
    "towing": ("tow call", "$150"),
    "garage-door": ("service call", "$300"),
    "pest-control": ("service call", "$200"),
    "property-management": ("maintenance call", "$250"),
    "water-damage": ("emergency call", "$2,000"),
    "cleaning": ("booking", "$200"),
    "landscaping": ("estimate", "$300"),
    "auto-repair": ("repair job", "$400"),
    "general-contractor": ("estimate", "$1,000"),
    "funeral": ("arrangement", "$3,000"),
}
DEFAULT_INDUSTRY = ("service call", "$350")


def get_industry(tags):
    if not tags:
        return DEFAULT_INDUSTRY
    for tag in tags:
        key = tag.lower().strip()
        if key in INDUSTRY_MAP:
            return INDUSTRY_MAP[key]
    return DEFAULT_INDUSTRY


# ─── Logging ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] speed-to-lead-v2: {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def speed_log(event_type, contact_id, contact_name, company, action, outcome, signal=None, latency_sec=None):
    """Append a structured entry to speed-log.json for every speed-to-lead action."""
    entry = {
        "ts": datetime.now().isoformat(),
        "event_type": event_type,
        "contact_id": contact_id,
        "contact_name": contact_name,
        "company": company,
        "action": action,
        "outcome": outcome,
        "signal": signal,
        "latency_sec": latency_sec,
    }
    try:
        os.makedirs(os.path.dirname(SPEED_LOG_FILE), exist_ok=True)
        existing = []
        if os.path.exists(SPEED_LOG_FILE):
            try:
                with open(SPEED_LOG_FILE, "r") as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, IOError):
                existing = []
        existing.append(entry)
        # Keep last 5000 entries to cap file size
        if len(existing) > 5000:
            existing = existing[-5000:]
        tmp = SPEED_LOG_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(existing, f, indent=2)
        os.replace(tmp, SPEED_LOG_FILE)
    except Exception as e:
        log(f"speed_log write failed: {e}", "WARN")


# ─── State Management ─────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            log("State file corrupted, starting fresh", "WARN")
    return {
        "hot_leads": {},           # contact_id -> hot lead tracking object
        "resurrection": {},        # contact_id -> resurrection enrollment object
        "seen_conversations": {},  # conv_id -> last_seen_message_id (for reply detection)
        "stats": {
            "total_hot_detected": 0,
            "total_sms_sent": 0,
            "total_calls_queued": 0,
            "total_emails_sent": 0,
            "total_resurrected": 0,
            "resurrection_emails_sent": 0,
        },
        "created": datetime.now().isoformat(),
        "last_check": None,
    }


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


# ─── GHL API ──────────────────────────────────────────────────────────────────

def ghl_request(method, path, headers=None, params=None, json_body=None, retries=3):
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    backoff = [5, 15, 30]
    for attempt in range(retries):
        try:
            resp = requests.request(
                method, url, headers=headers,
                params=params, json=json_body, timeout=30
            )
            if resp.status_code == 429:
                wait = [30, 60, 120][min(attempt, 2)]
                log(f"Rate limited (429), waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                wait = backoff[min(attempt, 2)]
                log(f"Server error ({resp.status_code}), retry in {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code in (400, 401, 404):
                log(f"GHL error {resp.status_code}: {resp.text[:200]}", "ERROR")
                return None
            return resp.json() if resp.text else {}
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(backoff[min(attempt, 2)])
            else:
                log(f"Request failed after {retries} attempts: {e}", "ERROR")
    return None


def get_contact(contact_id):
    data = ghl_request("GET", f"/contacts/{contact_id}")
    return data.get("contact") if data else None


def search_contacts_by_tag(tag, limit=100):
    """Paginate through all contacts that have a given tag."""
    all_contacts = []
    page = 1
    while True:
        data = ghl_request(
            "GET", "/contacts/",
            params={"locationId": GHL_LOCATION_ID, "query": "", "limit": limit, "page": page},
        )
        if not data or "contacts" not in data:
            break
        batch = data["contacts"]
        for c in batch:
            ctags = c.get("tags", [])
            if isinstance(ctags, list) and tag in ctags:
                all_contacts.append(c)
        if len(batch) < limit:
            break
        page += 1
        if page > 50:
            break
    return all_contacts


def get_recent_contacts(limit=200):
    """Fetch the most recently updated contacts for signal scanning."""
    data = ghl_request(
        "GET", "/contacts/",
        params={"locationId": GHL_LOCATION_ID, "limit": limit, "page": 1},
    )
    if not data:
        return []
    return data.get("contacts", [])


def get_conversations_for_contact(contact_id):
    data = ghl_request(
        "GET", "/conversations/search",
        headers=CONVERSATIONS_HEADERS,
        params={"contactId": contact_id, "locationId": GHL_LOCATION_ID, "limit": 5},
    )
    if not data:
        return []
    return data.get("conversations", [])


def get_messages_for_conversation(conv_id, limit=20):
    data = ghl_request(
        "GET", f"/conversations/{conv_id}/messages",
        headers=CONVERSATIONS_HEADERS,
        params={"limit": limit},
    )
    if not data:
        return []
    msgs = data.get("messages", {})
    # GHL wraps messages in a messages object with a list
    if isinstance(msgs, dict):
        return msgs.get("messages", [])
    return msgs if isinstance(msgs, list) else []


def add_tags(contact_id, tags):
    return ghl_request("POST", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def update_contact(contact_id, fields):
    return ghl_request("PUT", f"/contacts/{contact_id}", json_body=fields)


def send_sms(contact_id, message):
    return ghl_request(
        "POST", "/conversations/messages",
        headers=CONVERSATIONS_HEADERS,
        json_body={"type": "SMS", "contactId": contact_id, "message": message},
    )


def send_email(contact_id, subject, html_body, from_name="Wallace Dobbs"):
    return ghl_request(
        "POST", "/conversations/messages",
        headers=CONVERSATIONS_HEADERS,
        json_body={
            "type": "Email",
            "contactId": contact_id,
            "subject": subject,
            "html": html_body,
            "emailFrom": f"{from_name} <{BUSINESS_EMAIL}>",
        },
    )


def send_wallace_sms(message):
    return send_sms(WALLACE_GHL_ID, message)


def move_to_pipeline_stage(contact_id, pipeline_id, stage_id):
    """Move a contact's opportunity to a specific pipeline stage."""
    # First, find existing opportunity for this contact
    data = ghl_request(
        "GET", "/opportunities/search",
        params={"location_id": GHL_LOCATION_ID, "contact_id": contact_id},
    )
    opps = (data or {}).get("opportunities", [])
    if opps:
        opp_id = opps[0].get("id")
        if opp_id:
            ghl_request(
                "PUT", f"/opportunities/{opp_id}",
                json_body={"pipelineId": pipeline_id, "pipelineStageId": stage_id},
            )
            return True
    # No opportunity found — create one
    ghl_request(
        "POST", "/opportunities/",
        json_body={
            "pipelineId": pipeline_id,
            "pipelineStageId": stage_id,
            "locationId": GHL_LOCATION_ID,
            "contactId": contact_id,
            "name": "Speed-to-Lead Hot",
            "status": "open",
        },
    )
    return True


# ─── ntfy ─────────────────────────────────────────────────────────────────────

def ntfy(topic, title, message, priority="high"):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()[:60]
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title": safe_title,
                "Priority": priority,
                "Tags": "zap" if priority == "urgent" else "chart_with_upwards_trend",
            },
            timeout=10,
        )
    except Exception as e:
        log(f"ntfy failed: {e}", "WARN")


# ─── Bland.ai Call ────────────────────────────────────────────────────────────

BLAND_CALL_SCRIPT = """You are calling from The Call Taker, an AI receptionist service for service businesses.

Your name is Wallace. Keep it brief and human.

Opening: "Hey, is this {first_name}? This is Wallace from The Call Taker — you showed some interest in our AI answering service for {company_name}. Did I catch you at an okay time?"

If yes: "Perfect. Real quick — are you still losing calls to voicemail when you're on a job? I can show you what it sounds like when every call to {company_name} gets answered 24/7. Takes two minutes — want me to walk you through it?"

Goal: Book a 15-minute demo or get them to call {demo_line} themselves.

CTA: "Would this week work for a quick 15-minute Zoom? Or you can call {demo_line} right now and hear the AI live."

If not a good time: "Totally understand. What's a better time for me to reach you?" Then wrap up politely.

Keep the entire call under 90 seconds. Never pitch pricing on this call."""


def queue_bland_call(contact_id, contact, dry_run=False):
    """Fire a Bland.ai outbound call to a hot lead within 5 minutes."""
    phone = contact.get("phone", "")
    if not phone:
        log(f"No phone for {contact_id}, skipping call", "WARN")
        return False, "no_phone"

    # Normalize phone to E.164
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        digits = "1" + digits
    if not digits.startswith("1") or len(digits) != 11:
        log(f"Bad phone format for {contact_id}: {phone}", "WARN")
        return False, "bad_phone"
    e164_phone = f"+{digits}"

    first_name = contact.get("firstName", "there")
    company    = contact.get("companyName", "your business")
    tags       = contact.get("tags", [])
    job_word, job_value = get_industry(tags)

    script = BLAND_CALL_SCRIPT.format(
        first_name=first_name,
        company_name=company,
        demo_line=DEMO_LINE,
    )

    payload = {
        "phone_number": e164_phone,
        "task": script,
        "model": "enhanced",
        "language": "en",
        "voice": "nat",
        "max_duration": 2,         # 2 minutes max
        "answered_by_enabled": True,
        "voicemail_message": (
            f"Hey {first_name}, this is Wallace from The Call Taker. "
            f"You checked out our AI receptionist earlier — call me back or dial "
            f"{DEMO_LINE} to hear it live. Talk soon."
        ),
        "wait_for_greeting": True,
        "record": True,
        "metadata": {
            "contact_id": contact_id,
            "source": "speed-to-lead-v2",
        },
    }

    if dry_run:
        log(f"[DRY RUN] Would call {e164_phone} for {first_name} ({company})")
        return True, "dry_run"

    try:
        resp = requests.post(
            BLAND_CALLS_URL,
            json=payload,
            headers={
                "Authorization": BLAND_API_KEY,
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        if resp.status_code == 402:
            log("Bland.ai balance depleted (402) — auto-stopping calls", "ERROR")
            ntfy(NTFY_SYSTEM, "[CRITICAL] Bland.ai Balance Depleted",
                 "Speed-to-lead call queue paused. Top up Bland.ai immediately.", "urgent")
            return False, "balance_depleted"
        if resp.status_code != 200:
            log(f"Bland.ai error {resp.status_code}: {resp.text[:200]}", "ERROR")
            return False, f"bland_error_{resp.status_code}"
        call_data = resp.json()
        call_id = call_data.get("call_id", "unknown")
        log(f"Bland.ai call queued for {first_name} ({company}) — call_id={call_id}")
        return True, call_id
    except requests.exceptions.RequestException as e:
        log(f"Bland.ai request failed: {e}", "ERROR")
        return False, str(e)


# ─── Signal Detection ──────────────────────────────────────────────────────────

def detect_hot_signals(contacts, state, dry_run=False):
    """
    Scan contacts for hot signals. Returns list of (contact, signal_type, signal_detail) tuples.
    Skips contacts already in the hot_leads tracking dict (already being handled).
    """
    hot_found = []
    already_hot = set(state["hot_leads"].keys())

    for contact in contacts:
        cid = contact.get("id")
        if not cid or cid in already_hot:
            continue

        ctags = set(contact.get("tags", []))

        # Exclusion check
        if ctags & EXCLUDE_TAGS:
            continue

        # Must have phone or email
        if not contact.get("phone") and not contact.get("email"):
            continue

        signal = _check_tag_signals(contact, ctags)
        if signal:
            hot_found.append((contact, signal[0], signal[1]))
            continue

        # Check conversation for opens, clicks, keyword replies
        conv_signal = _check_conversation_signals(contact, state, dry_run)
        if conv_signal:
            hot_found.append((contact, conv_signal[0], conv_signal[1]))

    return hot_found


def _check_tag_signals(contact, ctags):
    """Check GHL tags for instant hot signals."""
    cid = contact.get("id")
    name = contact.get("firstName", "?")

    if "pilot-signup" in ctags:
        log(f"Signal: pilot-signup tag on {name} ({cid})")
        return ("pilot_form", "tagged:pilot-signup")
    if "calculator-lead" in ctags:
        log(f"Signal: calculator-lead tag on {name} ({cid})")
        return ("calculator_lead", "tagged:calculator-lead")
    if "demo-caller" in ctags:
        log(f"Signal: demo-caller tag on {name} ({cid})")
        return ("demo_caller", "tagged:demo-caller")
    return None


def _check_conversation_signals(contact, state, dry_run=False):
    """
    Check GHL conversations for:
    - Inbound reply with hot keyword
    - Email opened 2+ times
    - CTA link clicked
    """
    cid = contact.get("id")
    convs = get_conversations_for_contact(cid)
    if not convs:
        return None

    for conv in convs:
        conv_id = conv.get("id")
        if not conv_id:
            continue

        messages = get_messages_for_conversation(conv_id)
        if not messages:
            continue

        # Track seen messages to avoid duplicate processing
        seen_key = f"{cid}:{conv_id}"
        last_seen = state["seen_conversations"].get(seen_key, "")

        open_count = 0
        for msg in messages:
            if not isinstance(msg, dict):
                continue

            msg_id  = msg.get("id", "")
            msg_dir = msg.get("direction", "")  # "inbound" or "outbound"
            msg_type = msg.get("messageType", msg.get("type", ""))
            body    = msg.get("body", msg.get("message", "")) or ""

            # --- Hot keyword reply (inbound) ---
            if msg_dir == "inbound" and msg_id != last_seen:
                body_lower = body.lower()
                for kw in HOT_KEYWORDS:
                    if kw in body_lower:
                        state["seen_conversations"][seen_key] = msg_id
                        log(f"Signal: hot keyword '{kw}' reply from {contact.get('firstName', '?')} ({cid})")
                        return ("hot_reply", f"keyword:{kw}|msg:{msg_id[:8]}")

            # --- Email open tracking ---
            meta = msg.get("meta", {}) or {}
            opens = meta.get("openCount", 0) or 0
            try:
                opens = int(opens)
            except (ValueError, TypeError):
                opens = 0
            if opens >= 2 and msg_dir == "outbound":
                open_count = max(open_count, opens)

            # --- CTA click tracking ---
            clicks = meta.get("clickCount", 0) or 0
            try:
                clicks = int(clicks)
            except (ValueError, TypeError):
                clicks = 0
            if clicks >= 1 and msg_dir == "outbound":
                state["seen_conversations"][seen_key] = msg_id
                log(f"Signal: CTA clicked {clicks}x by {contact.get('firstName', '?')} ({cid})")
                return ("cta_click", f"clicks:{clicks}|msg:{msg_id[:8]}")

        if open_count >= 2:
            log(f"Signal: email opened {open_count}x by {contact.get('firstName', '?')} ({cid})")
            return ("email_opens", f"opens:{open_count}")

    return None


# ─── Hot Lead Response Copy ────────────────────────────────────────────────────

def _signal_context(signal_type, signal_detail, contact):
    """Return a human-readable 'what they were looking at' line for copy personalization."""
    if signal_type == "pilot_form":
        return "our free pilot program"
    if signal_type == "calculator_lead":
        return "our missed-call revenue calculator"
    if signal_type == "demo_caller":
        return "our live demo line"
    if signal_type == "hot_reply":
        kw = signal_detail.split("|")[0].replace("keyword:", "")
        return f"your message about {kw}"
    if signal_type == "email_opens":
        opens = signal_detail.replace("opens:", "")
        return f"our email (opened {opens} times)"
    if signal_type == "cta_click":
        return "our booking page"
    return "The Call Taker"


def build_hot_sms(contact, signal_type, signal_detail):
    first  = contact.get("firstName", "there")
    company = contact.get("companyName", "your business")
    tags   = contact.get("tags", [])
    job_word, job_value = get_industry(tags)
    context = _signal_context(signal_type, signal_detail, contact)

    return (
        f"Hey {first}, it's Wallace from The Call Taker. "
        f"I saw you were checking out {context} for {company}. "
        f"Quick question — how many calls go to voicemail after 5pm? "
        f"We can have an AI answering every one of them in 48 hours, free for 14 days. "
        f"Worth a 5-minute call? Or dial {DEMO_LINE} and hear it live right now."
    )


def build_hot_email(contact, signal_type, signal_detail):
    first   = contact.get("firstName", "there")
    company = contact.get("companyName", "your business")
    tags    = contact.get("tags", [])
    job_word, job_value = get_industry(tags)
    context = _signal_context(signal_type, signal_detail, contact)

    subject = f"I saw you checking out The Call Taker, {first}"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.7;">

<p>Hey {first},</p>

<p>I noticed you were looking at {context} for {company} — wanted to reach out personally.</p>

<p>Here's the short version of what we do:</p>

<p><strong>Every call to {company} gets answered, 24/7, by an AI that sounds like a real receptionist.</strong> It books appointments, collects information, and texts you the details instantly. No voicemail. No missed {job_word}s.</p>

<p>The average {job_word} is worth {job_value}. If you're missing 3-4 a week to voicemail, that's <strong>${int(job_value.replace('$','').replace(',','').replace('+','')) * 3 * 4:,}/month</strong> walking out the door.</p>

<p>We're running a free 14-day pilot right now. No card, no contract. We set everything up for you in 48 hours.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Book a Free 15-Min Demo &rarr;</a>
</p>

<p>Or call the AI yourself right now: <strong>{DEMO_LINE}</strong><br>
Pretend you're a customer. Takes 90 seconds and you'll see exactly what your customers will hear.</p>

<p>— Wallace Dobbs<br>
<span style="color: #666;">Founder, The Call Taker</span></p>

</div>"""
    return subject, html


# ─── Hot Lead Response Sequencer ──────────────────────────────────────────────

def handle_hot_lead(contact, signal_type, signal_detail, state, dry_run=False):
    """
    Execute the full hot lead response:
      T+0s  : Tag + pipeline move
      T+60s : SMS
      T+5m  : Bland.ai call
      T+10m : Email
    Actions are queued by recording detection_at. The send loop fires them when due.
    """
    cid   = contact.get("id")
    first = contact.get("firstName", "?")
    comp  = contact.get("companyName", "?")
    now_iso = datetime.now().isoformat()

    log(f"HOT LEAD DETECTED: {first} ({comp}) | signal={signal_type} | id={cid}")

    if cid in state["hot_leads"]:
        log(f"Already tracking {cid}, skipping duplicate detection")
        return

    # --- Step 0: Tag + pipeline (immediate) ---
    if not dry_run:
        add_tags(cid, ["hot-lead", "speed-to-lead-v2"])
        # GHL pipeline IDs — using contact custom field update as fallback
        # (Pipeline stage move requires knowing specific pipeline/stage IDs)
        update_contact(cid, {"customFields": [
            {"key": "hot_signal_type", "value": signal_type},
            {"key": "hot_signal_ts", "value": now_iso},
        ]})

    state["hot_leads"][cid] = {
        "detection_at": now_iso,
        "signal_type": signal_type,
        "signal_detail": signal_detail,
        "first_name": first,
        "company": comp,
        "phone": contact.get("phone", ""),
        "email": contact.get("email", ""),
        "sms_sent": False,
        "sms_at": None,
        "sms_outcome": None,
        "call_queued": False,
        "call_at": None,
        "call_outcome": None,
        "call_id": None,
        "email_sent": False,
        "email_at": None,
        "email_outcome": None,
        "replied": False,
    }

    state["stats"]["total_hot_detected"] += 1

    speed_log(
        event_type="detection",
        contact_id=cid,
        contact_name=first,
        company=comp,
        action="detected_hot_signal",
        outcome="queued",
        signal=f"{signal_type}:{signal_detail}",
        latency_sec=0,
    )

    # Alert Wallace immediately
    if not dry_run:
        alert_msg = (
            f"HOT LEAD: {first} ({comp})\n"
            f"Signal: {signal_type.replace('_', ' ').title()}\n"
            f"Detail: {signal_detail}\n"
            f"Phone: {contact.get('phone', 'none')}\n"
            f"SMS firing in 60s, call in 5min, email in 10min."
        )
        ntfy(NTFY_URGENT, f"[CRITICAL] Hot Lead — {first}", alert_msg, "urgent")
        send_wallace_sms(
            f"HOT LEAD: {first} at {comp} just triggered ({signal_type.replace('_',' ')}). "
            f"SMS queued. Check GHL: {contact.get('phone','no phone')}"
        )
    else:
        log(f"[DRY RUN] Would alert Wallace about {first} ({comp})")


def process_hot_lead_queue(state, dry_run=False):
    """
    Fire queued SMS / call / email actions when their time windows arrive.
    Called on every 15-second loop tick.
    """
    now = datetime.now()
    for cid, rec in list(state["hot_leads"].items()):
        if rec.get("replied"):
            continue

        detected_at = datetime.fromisoformat(rec["detection_at"])
        elapsed_sec = (now - detected_at).total_seconds()
        first = rec.get("first_name", "?")
        comp  = rec.get("company", "?")

        # ── SMS: fire within 60 seconds ──────────────────────────────────────
        if not rec["sms_sent"] and elapsed_sec >= SMS_WINDOW_SEC:
            contact = get_contact(cid) if not dry_run else {"firstName": first, "companyName": comp,
                                                              "tags": [], "phone": rec.get("phone",""),
                                                              "email": rec.get("email","")}
            if contact:
                msg = build_hot_sms(contact, rec["signal_type"], rec["signal_detail"])
                if dry_run:
                    log(f"[DRY RUN] SMS to {first}: {msg[:80]}...")
                    ok = True
                else:
                    result = send_sms(cid, msg)
                    ok = result is not None

                rec["sms_sent"] = True
                rec["sms_at"] = now.isoformat()
                rec["sms_outcome"] = "sent" if ok else "failed"
                if ok:
                    state["stats"]["total_sms_sent"] += 1
                    log(f"SMS sent to {first} ({comp}) — {elapsed_sec:.0f}s after detection")
                    speed_log("sms", cid, first, comp, "sms_sent", "sent",
                              signal=rec["signal_type"], latency_sec=int(elapsed_sec))
                    ntfy(NTFY_ACTIVITY, f"Speed-to-Lead SMS", f"{first} ({comp}) — {int(elapsed_sec)}s after hot signal", "default")
                else:
                    log(f"SMS FAILED for {first} ({cid})", "ERROR")
                    speed_log("sms", cid, first, comp, "sms_sent", "failed", signal=rec["signal_type"])

        # ── Bland.ai call: fire within 5 minutes ─────────────────────────────
        if not rec["call_queued"] and elapsed_sec >= CALL_WINDOW_SEC:
            contact = get_contact(cid) if not dry_run else {"firstName": first, "companyName": comp,
                                                              "tags": [], "phone": rec.get("phone","")}
            if contact:
                ok, call_id = queue_bland_call(cid, contact, dry_run=dry_run)
                rec["call_queued"] = True
                rec["call_at"] = now.isoformat()
                rec["call_outcome"] = "queued" if ok else "failed"
                rec["call_id"] = str(call_id)
                if ok:
                    state["stats"]["total_calls_queued"] += 1
                    log(f"Bland.ai call queued for {first} ({comp}) — {elapsed_sec:.0f}s after detection")
                    speed_log("call", cid, first, comp, "call_queued", "queued",
                              signal=rec["signal_type"], latency_sec=int(elapsed_sec))
                    ntfy(NTFY_ACTIVITY, "Speed-to-Lead Call",
                         f"Bland.ai calling {first} ({comp}) — {int(elapsed_sec)}s after hot signal", "default")
                else:
                    log(f"Bland.ai call FAILED for {first} ({cid}): {call_id}", "ERROR")
                    speed_log("call", cid, first, comp, "call_queued", str(call_id), signal=rec["signal_type"])

        # ── Email: fire within 10 minutes ────────────────────────────────────
        if not rec["email_sent"] and elapsed_sec >= EMAIL_WINDOW_SEC:
            contact = get_contact(cid) if not dry_run else {"firstName": first, "companyName": comp,
                                                              "tags": [], "phone": rec.get("phone",""),
                                                              "email": rec.get("email","")}
            if contact:
                subj, html = build_hot_email(contact, rec["signal_type"], rec["signal_detail"])
                if dry_run:
                    log(f"[DRY RUN] Email to {first}: subject='{subj}'")
                    ok = True
                else:
                    result = send_email(cid, subj, html)
                    ok = result is not None

                rec["email_sent"] = True
                rec["email_at"] = now.isoformat()
                rec["email_outcome"] = "sent" if ok else "failed"
                if ok:
                    state["stats"]["total_emails_sent"] += 1
                    log(f"Email sent to {first} ({comp}) — {elapsed_sec:.0f}s after detection")
                    speed_log("email", cid, first, comp, "email_sent", "sent",
                              signal=rec["signal_type"], latency_sec=int(elapsed_sec))
                    ntfy(NTFY_ACTIVITY, "Speed-to-Lead Email",
                         f"Email to {first} ({comp}) — {int(elapsed_sec)}s after hot signal", "default")
                else:
                    log(f"Email FAILED for {first} ({cid})", "ERROR")
                    speed_log("email", cid, first, comp, "email_sent", "failed", signal=rec["signal_type"])


# ─── Dead Lead Resurrection ───────────────────────────────────────────────────

def _build_resurrection_email_1(first, company, job_word, job_value):
    """Social proof angle — Day 0."""
    subject = f"businesses like {company} are booking more jobs with this"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.7;">

<p>Hey {first},</p>

<p>I know it's been a while since we talked, so I'll keep this short.</p>

<p>Since we last connected, a handful of {job_word} businesses have started using The Call Taker — and the results are consistent:</p>

<ul style="margin: 16px 0;">
  <li>Calls answered 24/7, even at 2am and on weekends</li>
  <li>Appointments booked directly into their calendar without lifting a finger</li>
  <li>Competitors who called them after hours — gone to voicemail — moved on</li>
</ul>

<p>One business told me: <em>"I came in Monday morning and had 3 new jobs on the calendar from the weekend. I didn't even know we got called."</em></p>

<p>Not every business is ready for this. But the ones that are — they're glad they didn't wait another season.</p>

<p>14 days free. No card. No contract. Just results.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">See How It Works &rarr;</a>
</p>

<p>Or reply and I'll send you a 2-minute video showing it live.</p>

<p>— Wallace<br>
<span style="color: #666;">Founder, The Call Taker</span></p>

</div>"""
    return subject, html


def _build_resurrection_email_2(first, company, job_word, job_value):
    """ROI calculator angle — Day 2."""
    try:
        val_int = int(job_value.replace("$", "").replace(",", "").replace("+", ""))
    except ValueError:
        val_int = 350
    weekly_lost = val_int * 3
    monthly_lost = weekly_lost * 4

    subject = f"we estimated what {company} is losing to voicemail"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.7;">

<p>Hey {first},</p>

<p>Quick math on {company}:</p>

<table style="border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 15px;">
  <tr style="background: #f9fafb;">
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb;">Average {job_word} value</td>
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb; font-weight: 600;">{job_value}</td>
  </tr>
  <tr>
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb;">Calls going to voicemail per week <em>(industry avg: 3-5)</em></td>
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb; font-weight: 600;">~3</td>
  </tr>
  <tr style="background: #f9fafb;">
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb;">Lost per week</td>
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb; font-weight: 600; color: #dc2626;">${weekly_lost:,}</td>
  </tr>
  <tr>
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb;">Lost per month</td>
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb; font-weight: 600; color: #dc2626;">${monthly_lost:,}</td>
  </tr>
  <tr style="background: #fefce8;">
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb;">Cost of The Call Taker</td>
    <td style="padding: 10px 12px; border: 1px solid #e5e7eb; font-weight: 600; color: #16a34a;">$297/mo (or free for 14 days)</td>
  </tr>
</table>

<p>That's not a pitch. That's just math.</p>

<p>If those numbers are even half right for {company}, the 14-day pilot pays for itself the first week.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Start the Free Pilot &rarr;</a>
</p>

<p>Run your own numbers at <a href="https://thecalltaker.com/calculator.html" style="color: #f97316;">thecalltaker.com/calculator</a></p>

<p>— Wallace</p>

</div>"""
    return subject, html


def _build_resurrection_email_3(first, company, city, job_word):
    """Competitor angle — Day 5."""
    city_display = city if city else "your area"
    subject = f"your competition in {city_display} just signed up"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.7;">

<p>Hey {first},</p>

<p>I don't usually send emails like this, but I think you should know.</p>

<p>Another {job_word} business in {city_display} just started their pilot with The Call Taker this week.</p>

<p>Starting today, every call they get after hours — including the ones that used to go to voicemail — is getting answered. They're booking jobs that would have otherwise gone to whoever picked up first.</p>

<p>I don't know if that business competes with {company} directly. But I figured if the situation were reversed, you'd want to know.</p>

<p>The 14-day pilot is still free. No card, no contract. We can have {company} live in 48 hours.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Claim Your Pilot Spot &rarr;</a>
</p>

<p>Or just call {DEMO_LINE} right now and hear what your calls will sound like. Takes 90 seconds.</p>

<p>— Wallace<br>
<span style="color: #999; font-size: 13px;">If you'd rather I stop reaching out, just reply "stop" and I won't contact you again.</span></p>

</div>"""
    return subject, html


def _get_contact_city(contact):
    """Extract city from contact data."""
    city = contact.get("city", "") or ""
    if not city:
        addr = contact.get("address1", "") or ""
        # Best effort: last segment before state abbreviation
        parts = addr.split(",")
        if len(parts) >= 2:
            city = parts[-2].strip()
    return city.strip()


def cmd_resurrect(state, dry_run=False):
    """
    Find contacts tagged hot-lead that have gone cold for 14+ days.
    Enroll them in 3-email resurrection sequence over 5 days.
    Sends any emails that are due based on enrollment date.
    """
    log("Running dead lead resurrection scan...")

    now = datetime.now()
    cold_cutoff = now - timedelta(days=RESURRECT_DAYS_COLD)
    new_enrollments = 0
    emails_sent = 0

    # Pull all hot-lead contacts
    hot_contacts = search_contacts_by_tag("hot-lead")
    log(f"Found {len(hot_contacts)} contacts with hot-lead tag")

    for contact in hot_contacts:
        cid = contact.get("id")
        if not cid:
            continue

        ctags = set(contact.get("tags", []))

        # Skip excluded
        if ctags & RESURRECT_EXCLUDE_TAGS:
            continue

        # Skip if already enrolled in resurrection
        if cid in state["resurrection"]:
            pass  # still check for due emails below
        else:
            # Check last activity — use GHL dateUpdated field
            last_updated_str = contact.get("dateUpdated") or contact.get("dateAdded", "")
            if not last_updated_str:
                continue
            try:
                last_updated = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00").replace("+00:00", ""))
            except ValueError:
                continue

            if last_updated >= cold_cutoff:
                # Still active — skip
                continue

            # Enroll in resurrection sequence
            first = contact.get("firstName", "?")
            comp  = contact.get("companyName", "?")
            tags  = contact.get("tags", [])
            job_word, job_value = get_industry(tags)
            city  = _get_contact_city(contact)

            log(f"Enrolling resurrection: {first} ({comp}) — last active {last_updated.date()}")

            if not dry_run:
                add_tags(cid, ["resurrection-seq"])

            state["resurrection"][cid] = {
                "enrolled_at": now.isoformat(),
                "first_name": first,
                "company": comp,
                "job_word": job_word,
                "job_value": job_value,
                "city": city,
                "emails_sent": [],   # list of email numbers sent: [1], [1,2], [1,2,3]
                "completed": False,
                "replied": False,
            }
            state["stats"]["total_resurrected"] += 1
            new_enrollments += 1

            speed_log("resurrection", cid, first, comp, "enrolled", "enrolled",
                      signal="dead_14d", latency_sec=None)

    # Send due emails for all enrolled (new + existing)
    email_schedule = {
        1: 0,                           # Email 1: immediately on enrollment
        2: RESURRECT_EMAIL_2_DAYS * 86400,   # Email 2: 2 days later in seconds
        3: RESURRECT_EMAIL_3_DAYS * 86400,   # Email 3: 5 days later in seconds
    }

    for cid, rec in list(state["resurrection"].items()):
        if rec.get("completed") or rec.get("replied"):
            continue

        enrolled_at = datetime.fromisoformat(rec["enrolled_at"])
        elapsed_sec = (now - enrolled_at).total_seconds()
        first    = rec.get("first_name", "?")
        comp     = rec.get("company", "?")
        job_word = rec.get("job_word", "service call")
        job_value= rec.get("job_value", "$350")
        city     = rec.get("city", "")
        sent_nums = rec.get("emails_sent", [])

        for email_num, delay_sec in email_schedule.items():
            if email_num in sent_nums:
                continue
            if elapsed_sec < delay_sec:
                continue
            # Must send in order
            if email_num > 1 and (email_num - 1) not in sent_nums:
                continue

            # Build email
            if email_num == 1:
                subj, html = _build_resurrection_email_1(first, comp, job_word, job_value)
                tag = "resurrection-1"
            elif email_num == 2:
                subj, html = _build_resurrection_email_2(first, comp, job_word, job_value)
                tag = "resurrection-2"
            else:
                subj, html = _build_resurrection_email_3(first, comp, city, job_word)
                tag = "resurrection-3"

            if dry_run:
                log(f"[DRY RUN] Resurrection email {email_num} to {first} ({comp}): '{subj}'")
                ok = True
            else:
                result = send_email(cid, subj, html)
                ok = result is not None
                if ok:
                    add_tags(cid, [tag])

            if ok:
                sent_nums.append(email_num)
                rec["emails_sent"] = sent_nums
                state["stats"]["resurrection_emails_sent"] += 1
                emails_sent += 1
                log(f"Resurrection email {email_num}/3 sent to {first} ({comp})")
                speed_log("resurrection_email", cid, first, comp,
                          f"email_{email_num}_sent", "sent",
                          signal=f"resurrection_day{email_num}", latency_sec=None)
                ntfy(NTFY_ACTIVITY, f"Resurrection Email {email_num}",
                     f"{first} ({comp}) — {email_num}/3", "default")
            else:
                log(f"Resurrection email {email_num} FAILED for {first} ({cid})", "ERROR")

            # Only send one email per contact per cycle
            break

        # Mark completed after all 3 sent
        if len(rec.get("emails_sent", [])) >= 3:
            rec["completed"] = True
            log(f"Resurrection sequence complete for {first} ({comp})")

    log(f"Resurrection done. New enrollments: {new_enrollments} | Emails sent: {emails_sent}")
    return new_enrollments, emails_sent


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_check(state, dry_run=False):
    """Single-pass hot signal scan + queue processing."""
    log("Running single-pass hot signal check...")
    contacts = get_recent_contacts(limit=200)
    log(f"Scanning {len(contacts)} recent contacts for hot signals...")

    signals = detect_hot_signals(contacts, state, dry_run=dry_run)
    for contact, signal_type, signal_detail in signals:
        handle_hot_lead(contact, signal_type, signal_detail, state, dry_run=dry_run)

    process_hot_lead_queue(state, dry_run=dry_run)
    state["last_check"] = datetime.now().isoformat()
    save_state(state)

    if signals:
        log(f"Check complete. {len(signals)} new hot signals detected.")
    else:
        log("Check complete. No new hot signals.")

    return len(signals)


def cmd_watch(state):
    """
    Continuous 15-second monitoring loop.
    This is the main production mode — runs indefinitely.
    """
    log("Starting continuous watch mode (15-second intervals)...")
    ntfy(NTFY_SYSTEM, "Speed-to-Lead v2 Started",
         "15-second hot tier monitoring is live.", "default")

    consecutive_errors = 0
    max_consecutive_errors = 10

    while True:
        cycle_start = time.time()
        try:
            contacts = get_recent_contacts(limit=200)
            signals = detect_hot_signals(contacts, state, dry_run=False)
            for contact, signal_type, signal_detail in signals:
                handle_hot_lead(contact, signal_type, signal_detail, state, dry_run=False)
            process_hot_lead_queue(state, dry_run=False)
            state["last_check"] = datetime.now().isoformat()
            save_state(state)
            consecutive_errors = 0
        except KeyboardInterrupt:
            log("Watch mode stopped by user.")
            break
        except Exception as e:
            consecutive_errors += 1
            log(f"Error in watch cycle ({consecutive_errors}/{max_consecutive_errors}): {e}", "ERROR")
            log(traceback.format_exc(), "ERROR")
            if consecutive_errors >= max_consecutive_errors:
                ntfy(NTFY_SYSTEM, "[CRITICAL] Speed-to-Lead v2 Crashed",
                     f"10 consecutive errors. Last: {str(e)[:300]}", "urgent")
                raise

        # Sleep for remainder of 15-second window
        elapsed = time.time() - cycle_start
        sleep_for = max(0, 15.0 - elapsed)
        if sleep_for > 0:
            time.sleep(sleep_for)


def cmd_status(state):
    """Print engine stats and active hot lead queue."""
    stats = state["stats"]
    hot   = state["hot_leads"]
    res   = state["resurrection"]

    active_hot = [cid for cid, r in hot.items()
                  if not r.get("replied") and not (r["sms_sent"] and r["call_queued"] and r["email_sent"])]
    completed_hot = [cid for cid, r in hot.items()
                     if r["sms_sent"] and r["call_queued"] and r["email_sent"]]
    active_res = [cid for cid, r in res.items() if not r.get("completed") and not r.get("replied")]

    last_check = state.get("last_check", "never")

    print("\n╔══════════════════════════════════════════════════╗")
    print("║        SPEED-TO-LEAD v2 — STATUS                ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║  Last check:              {str(last_check)[:19]:<24} ║")
    print(f"║  Hot leads detected:      {stats['total_hot_detected']:<5}                    ║")
    print(f"║  Active hot queue:        {len(active_hot):<5}                    ║")
    print(f"║  Completed sequences:     {len(completed_hot):<5}                    ║")
    print(f"║  SMS sent:                {stats['total_sms_sent']:<5}                    ║")
    print(f"║  Calls queued:            {stats['total_calls_queued']:<5}                    ║")
    print(f"║  Emails sent:             {stats['total_emails_sent']:<5}                    ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║  Resurrection enrolled:   {stats['total_resurrected']:<5}                    ║")
    print(f"║  Resurrection active:     {len(active_res):<5}                    ║")
    print(f"║  Resurrection emails:     {stats['resurrection_emails_sent']:<5}                    ║")
    print("╚══════════════════════════════════════════════════╝\n")

    if active_hot:
        print("Active Hot Lead Queue:")
        for cid in active_hot:
            r = hot[cid]
            det = datetime.fromisoformat(r["detection_at"])
            age_min = int((datetime.now() - det).total_seconds() / 60)
            sms  = "Y" if r["sms_sent"] else "N"
            call = "Y" if r["call_queued"] else "N"
            eml  = "Y" if r["email_sent"] else "N"
            print(f"  {r['first_name']:12} | {r['company']:25} | {r['signal_type']:15} | "
                  f"{age_min}min ago | SMS:{sms} Call:{call} Email:{eml}")
        print()

    if active_res:
        print("Active Resurrection Sequences:")
        for cid in active_res:
            r = res[cid]
            sent_count = len(r.get("emails_sent", []))
            print(f"  {r['first_name']:12} | {r['company']:25} | Email {sent_count}/3 sent")
        print()


def cmd_test(state):
    """Dry-run: detect signals and show what would be sent without firing anything."""
    log("TEST MODE — no messages will be sent")
    contacts = get_recent_contacts(limit=200)
    log(f"Scanning {len(contacts)} contacts in dry-run mode...")
    signals = detect_hot_signals(contacts, state, dry_run=True)
    if signals:
        for contact, sig_type, sig_detail in signals:
            first = contact.get("firstName", "?")
            comp  = contact.get("companyName", "?")
            log(f"[DRY RUN] Would trigger hot sequence for {first} ({comp}) — {sig_type}: {sig_detail}")
            sms_msg = build_hot_sms(contact, sig_type, sig_detail)
            log(f"[DRY RUN] SMS: {sms_msg[:100]}...")
            subj, _ = build_hot_email(contact, sig_type, sig_detail)
            log(f"[DRY RUN] Email subject: {subj}")
        print(f"\nTest found {len(signals)} hot signals. No messages sent.")
    else:
        print("No hot signals detected in current contact set.")

    # Also dry-run resurrection
    log("[DRY RUN] Running resurrection scan...")
    cmd_resurrect(state, dry_run=True)


# ─── Main ─────────────────────────────────────────────────────────────────────

USAGE = """
Speed-to-Lead v2 Engine — The Call Taker

Usage:
  speed-to-lead-v2.py watch       Continuous 15-second monitoring (main mode)
  speed-to-lead-v2.py check       Single pass check
  speed-to-lead-v2.py resurrect   Run dead lead resurrection scan + send
  speed-to-lead-v2.py status      Show engine stats and queue
  speed-to-lead-v2.py test        Dry-run detection without sending
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    command = sys.argv[1].lower()
    state = load_state()

    try:
        if command == "watch":
            cmd_watch(state)

        elif command == "check":
            cmd_check(state, dry_run=False)

        elif command == "resurrect":
            new, sent = cmd_resurrect(state, dry_run=False)
            save_state(state)
            print(f"\nResurrection: {new} new enrollments, {sent} emails sent.")
            if new > 0 or sent > 0:
                ntfy(NTFY_ACTIVITY, "Dead Lead Resurrection",
                     f"Enrolled: {new} | Emails sent: {sent}", "default")

        elif command == "status":
            cmd_status(state)

        elif command == "test":
            cmd_test(state)

        else:
            print(f"Unknown command: {command}")
            print(USAGE)
            sys.exit(1)

    except KeyboardInterrupt:
        log("Interrupted by user.")
    except Exception as e:
        log(f"CRASH: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        ntfy(
            NTFY_SYSTEM,
            "[CRITICAL] Speed-to-Lead v2 Crashed",
            f"Command: {command}\nError: {str(e)[:400]}",
            "urgent",
        )
        raise


if __name__ == "__main__":
    main()
