#!/usr/bin/env python3
"""
cold-caller-v2.py — Bland.ai Cold Calling Engine
The Call Taker | Replaced dead cold-caller.py (died Feb 24, 2026)

LAUNCHD SCHEDULE (add these plists to ~/Library/LaunchAgents/):

--- com.thecalltaker.coldcaller.call.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.thecalltaker.coldcaller.call</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/moneymaker99/Desktop/thecalltaker/ops/cold-caller-v2.py</string>
        <string>call</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
    </array>
    <key>StandardOutPath</key><string>/Users/moneymaker99/thecalltaker-ops/logs/coldcaller-stdout.log</string>
    <key>StandardErrorPath</key><string>/Users/moneymaker99/thecalltaker-ops/logs/coldcaller-stderr.log</string>
    <key>RunAtLoad</key><false/>
</dict>
</plist>

--- com.thecalltaker.coldcaller.check.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.thecalltaker.coldcaller.check</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/moneymaker99/Desktop/thecalltaker/ops/cold-caller-v2.py</string>
        <string>check</string>
    </array>
    <key>StartInterval</key><integer>600</integer>
    <key>StandardOutPath</key><string>/Users/moneymaker99/thecalltaker-ops/logs/coldcaller-stdout.log</string>
    <key>StandardErrorPath</key><string>/Users/moneymaker99/thecalltaker-ops/logs/coldcaller-stderr.log</string>
    <key>RunAtLoad</key><false/>
</dict>
</plist>

--- com.thecalltaker.coldcaller.summary.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.thecalltaker.coldcaller.summary</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/moneymaker99/Desktop/thecalltaker/ops/cold-caller-v2.py</string>
        <string>summary</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    </array>
    <key>StandardOutPath</key><string>/Users/moneymaker99/thecalltaker-ops/logs/coldcaller-stdout.log</string>
    <key>StandardErrorPath</key><string>/Users/moneymaker99/thecalltaker-ops/logs/coldcaller-stderr.log</string>
    <key>RunAtLoad</key><false/>
</dict>
</plist>

INSTALL:
    cp com.thecalltaker.coldcaller.*.plist ~/Library/LaunchAgents/
    launchctl load ~/Library/LaunchAgents/com.thecalltaker.coldcaller.call.plist
    launchctl load ~/Library/LaunchAgents/com.thecalltaker.coldcaller.check.plist
    launchctl load ~/Library/LaunchAgents/com.thecalltaker.coldcaller.summary.plist

USAGE:
    python3 cold-caller-v2.py call       # Make calls (hot leads first, max 20/run)
    python3 cold-caller-v2.py check      # Poll Bland.ai for pending call outcomes
    python3 cold-caller-v2.py retry      # Retry failed calls (2x max, 4hr gap)
    python3 cold-caller-v2.py summary    # Send 8pm daily summary to ntfy SALES
    python3 cold-caller-v2.py status     # Print engine stats to console
    python3 cold-caller-v2.py test       # Dry run — no actual calls placed
"""

import json
import os
import sys
import csv
import time
import logging
import tempfile
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

BLAND_API_KEY = "org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969"
BLAND_BASE    = "https://api.bland.ai/v1"
BLAND_HEADERS = {
    "Authorization": BLAND_API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "TheCallTaker/2.0",
}

GHL_API_KEY     = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE        = "https://services.leadconnectorhq.com"
GHL_HEADERS     = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Content-Type": "application/json",
    "Version": "2021-07-28",
    "User-Agent": "TheCallTaker/2.0",
}

# Wallace's GHL contact ID for SMS alerts
WALLACE_CONTACT_ID = "DtKLG28VzgUb6q3brILD"
WALLACE_PHONE      = "+16156539004"

# ntfy topics
NTFY_URGENT   = "tct-urgent-Hk9UOEZR"
NTFY_SALES    = "tct-sales-63uYsIT9"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_SYSTEM   = "tct-system-vRsfXQRQ"

# File paths — use absolute paths, never relative
BASE_DIR   = Path(os.path.expanduser("~/Desktop/thecalltaker"))
OPS_DIR    = BASE_DIR / "ops"
LEADS_DIR  = BASE_DIR / "leads"
STATE_FILE = OPS_DIR / "cold-caller-state.json"
CALL_LOG   = OPS_DIR / "call-log.json"
LOG_FILE   = OPS_DIR / "cold-caller.log"

MAX_CALLS_PER_RUN = 20
MAX_RETRIES       = 2
RETRY_GAP_HOURS   = 4

# Industry-specific job values for the call script
INDUSTRY_VALUES = {
    "hvac":                "$300-500",
    "locksmith":           "$150-300",
    "plumbing":            "$250-500",
    "electrical":          "$300-600",
    "roofing":             "$5,000-15,000",
    "pest control":        "$150-300",
    "towing":              "$100-300",
    "dental":              "$200-800",
    "med spa":             "$300-1,500",
    "legal":               "$2,000-10,000",
    "veterinary":          "$150-500",
    "auto repair":         "$200-800",
    "cleaning":            "$150-400",
    "property management": "$1,000-3,000",
    "water damage":        "$2,000-10,000",
    "landscaping":         "$300-2,000",
    "general contractor":  "$5,000-50,000",
}

CALL_SCRIPT = """You are Wallace, calling from The Call Taker. You're friendly, direct, and casual — like a neighbor who has good news. Your goal: get them to try the free 14-day pilot.

HOOK (first 4 seconds): 'Hey [First Name], quick question — who answers [Company]'s phones after 5pm?'

If they say nobody/voicemail/they do: 'Yeah, that's what I figured. So here's the thing — every call that goes to voicemail, that customer calls your competitor instead. For [industry], that's [value] per missed call.'

PROOF: 'I built an AI that answers your phone 24/7. Sounds like a real person. Gets their name, what they need, books the appointment on your calendar, texts you the details. One of our [industry] clients booked 14 extra jobs in 3 weeks.'

CTA: 'We do a free 14-day pilot — no card, no contract. We set it up in 48 hours and you keep every dollar it earns. Want me to get you set up?'

If interested: 'Awesome. I'll send you a text right now with the details. What's the best email to send the setup info to?'
If not interested: 'No worries at all. If you ever want to hear what it sounds like, call (615) 784-5747 — that's our live demo line. It'll answer like it works for your business. Take care.'

NEVER be pushy. If they say no twice, thank them and end the call."""

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
    ],
)
log = logging.getLogger("cold-caller-v2")

# ---------------------------------------------------------------------------
# STATE MANAGEMENT (atomic writes)
# ---------------------------------------------------------------------------

DEFAULT_STATE = {
    "version": 2,
    "created_at": None,
    "last_run": None,
    "pending_calls": {},      # call_id -> {contact_id, name, company, phone, industry, dispatched_at}
    "called_contacts": {},    # contact_id -> {call_count, last_call, outcomes, retry_count}
    "daily_stats": {
        "date": None,
        "calls_made": 0,
        "answered": 0,
        "voicemail": 0,
        "no_answer": 0,
        "interested": 0,
        "not_interested": 0,
        "failed": 0,
    },
    "total_stats": {
        "calls_made": 0,
        "interested": 0,
        "pilots_started": 0,
    },
}


def load_state() -> dict:
    if not STATE_FILE.exists():
        state = DEFAULT_STATE.copy()
        state["created_at"] = datetime.now().isoformat()
        save_state(state)
        return state
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        # Ensure all keys exist (forward-compat)
        for k, v in DEFAULT_STATE.items():
            if k not in data:
                data[k] = v
        return data
    except (json.JSONDecodeError, OSError) as e:
        log.error(f"State file corrupt: {e} — loading defaults")
        return DEFAULT_STATE.copy()


def save_state(state: dict):
    """Atomic write: tempfile + os.replace prevents corruption."""
    OPS_DIR.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        fd, tmp_path = tempfile.mkstemp(dir=OPS_DIR, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2, default=str)
        os.replace(tmp_path, STATE_FILE)
    except OSError as e:
        log.error(f"Failed to save state: {e}")
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def reset_daily_stats_if_new_day(state: dict) -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    if state["daily_stats"].get("date") != today:
        state["daily_stats"] = {
            "date": today,
            "calls_made": 0,
            "answered": 0,
            "voicemail": 0,
            "no_answer": 0,
            "interested": 0,
            "not_interested": 0,
            "failed": 0,
        }
    return state

# ---------------------------------------------------------------------------
# CALL LOG (append-only JSON log)
# ---------------------------------------------------------------------------

def append_call_log(entry: dict):
    """Append one call record to call-log.json (array of objects)."""
    OPS_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    if CALL_LOG.exists():
        try:
            with open(CALL_LOG, "r") as f:
                records = json.load(f)
        except (json.JSONDecodeError, OSError):
            records = []
    records.append(entry)
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(dir=OPS_DIR, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(records, f, indent=2, default=str)
        os.replace(tmp_path, CALL_LOG)
    except OSError as e:
        log.error(f"Failed to write call log: {e}")
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

# ---------------------------------------------------------------------------
# NTFY
# ---------------------------------------------------------------------------

def ntfy(topic: str, title: str, body: str, priority: str = "default", tags: str = ""):
    """Send ntfy notification. Sanitizes headers."""
    def _clean(s: str) -> str:
        return s.encode("ascii", errors="replace").decode("ascii").replace("\n", " ")[:250]

    headers = {
        "Title": _clean(title),
        "Priority": priority,
        "Content-Type": "text/plain",
    }
    if tags:
        headers["Tags"] = tags

    for attempt in range(3):
        try:
            resp = requests.post(
                f"https://ntfy.sh/{topic}",
                data=body.encode("utf-8"),
                headers=headers,
                timeout=10,
            )
            if resp.status_code < 300:
                return True
            log.warning(f"ntfy HTTP {resp.status_code}")
        except requests.RequestException as e:
            log.warning(f"ntfy attempt {attempt + 1} failed: {e}")
        if attempt < 2:
            time.sleep(2)
    return False

# ---------------------------------------------------------------------------
# GHL API
# ---------------------------------------------------------------------------

def ghl_get(path: str, params: dict = None, version: str = "2021-07-28") -> dict | None:
    headers = {**GHL_HEADERS, "Version": version}
    url = f"{GHL_BASE}{path}"
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                log.warning(f"GHL rate limit — waiting {wait}s")
                time.sleep(wait)
                continue
            if resp.status_code == 200:
                return resp.json()
            log.error(f"GHL GET {path} returned {resp.status_code}: {resp.text[:200]}")
            return None
        except requests.RequestException as e:
            log.warning(f"GHL GET {path} attempt {attempt + 1} failed: {e}")
            time.sleep(5 * (attempt + 1))
    return None


def ghl_post(path: str, payload: dict, version: str = "2021-07-28") -> dict | None:
    headers = {**GHL_HEADERS, "Version": version}
    url = f"{GHL_BASE}{path}"
    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                log.warning(f"GHL rate limit — waiting {wait}s")
                time.sleep(wait)
                continue
            if resp.status_code in (200, 201):
                return resp.json()
            log.error(f"GHL POST {path} returned {resp.status_code}: {resp.text[:200]}")
            return None
        except requests.RequestException as e:
            log.warning(f"GHL POST {path} attempt {attempt + 1} failed: {e}")
            time.sleep(5 * (attempt + 1))
    return None


def ghl_fetch_contacts_by_tag(tag: str, limit: int = 100) -> list[dict]:
    """Fetch GHL contacts with a specific tag."""
    contacts = []
    page = 1
    while True:
        data = ghl_get(
            f"/contacts/",
            params={
                "locationId": GHL_LOCATION_ID,
                "tags": tag,
                "limit": min(limit, 100),
                "page": page,
            },
        )
        if not data:
            break
        batch = data.get("contacts", [])
        contacts.extend(batch)
        if len(batch) < 100 or len(contacts) >= limit:
            break
        page += 1
    return contacts


def ghl_send_sms(contact_id: str, message: str) -> bool:
    """Send SMS via GHL conversations API."""
    # First get or create conversation
    conv_data = ghl_get(
        "/conversations/search",
        params={"locationId": GHL_LOCATION_ID, "contactId": contact_id},
        version="2021-04-15",
    )
    conversation_id = None
    if conv_data and conv_data.get("conversations"):
        conversation_id = conv_data["conversations"][0].get("id")

    if not conversation_id:
        # Create conversation
        result = ghl_post(
            "/conversations/",
            {"locationId": GHL_LOCATION_ID, "contactId": contact_id},
            version="2021-04-15",
        )
        if result:
            conversation_id = result.get("conversation", {}).get("id")

    if not conversation_id:
        log.error(f"Could not get/create conversation for contact {contact_id}")
        return False

    result = ghl_post(
        f"/conversations/{conversation_id}/messages",
        {"type": "SMS", "message": message},
        version="2021-04-15",
    )
    return result is not None


def ghl_tag_contact(contact_id: str, tags: list[str]) -> bool:
    result = ghl_post(
        f"/contacts/{contact_id}/tags",
        {"tags": tags},
    )
    return result is not None

# ---------------------------------------------------------------------------
# BLAND.AI API
# ---------------------------------------------------------------------------

def bland_place_call(
    phone: str,
    first_name: str,
    company: str,
    industry: str,
    contact_id: str,
    dry_run: bool = False,
) -> dict | None:
    """
    Place a Bland.ai outbound call.
    Returns the Bland.ai response dict, or None on failure.
    402 (payment required) triggers immediate SYSTEM alert + stops all calls.
    """
    job_value = INDUSTRY_VALUES.get(industry.lower(), "$200-500")
    task = (
        CALL_SCRIPT
        .replace("[First Name]", first_name)
        .replace("[Company]", company)
        .replace("[industry]", industry)
        .replace("[value]", job_value)
    )

    payload = {
        "phone_number": phone,
        "task": task,
        "voice": "maya",
        "first_sentence": f"Hey, is this {first_name}? This is Wallace from The Call Taker.",
        "wait_for_greeting": True,
        "max_duration": 120,
        "record": True,
        "webhook": None,
        "transfer_phone_number": WALLACE_PHONE,
        "metadata": {
            "contact_id": contact_id,
            "company": company,
            "industry": industry,
        },
    }

    if dry_run:
        log.info(f"[DRY RUN] Would call {phone} ({first_name} @ {company}, {industry})")
        return {"call_id": f"dry_run_{contact_id}", "status": "queued", "dry_run": True}

    log.info(f"Calling {phone} — {first_name} @ {company} ({industry})")

    try:
        resp = requests.post(
            f"{BLAND_BASE}/calls",
            headers=BLAND_HEADERS,
            json=payload,
            timeout=20,
        )

        if resp.status_code == 402:
            log.critical("Bland.ai balance depleted (402). Stopping all calls.")
            ntfy(
                NTFY_SYSTEM,
                "[CRITICAL] Bland.ai Balance Depleted",
                "Cold caller stopped. 402 Payment Required from Bland.ai. Top up at app.bland.ai before calls resume.",
                priority="urgent",
                tags="warning,phone",
            )
            raise BlandBalanceError("Bland.ai returned 402 — balance depleted")

        if resp.status_code in (200, 201):
            data = resp.json()
            log.info(f"Call dispatched: call_id={data.get('call_id')}")
            return data

        log.error(f"Bland.ai call failed {resp.status_code}: {resp.text[:300]}")
        return None

    except BlandBalanceError:
        raise
    except requests.RequestException as e:
        log.error(f"Bland.ai request error: {e}")
        return None


def bland_get_call(call_id: str) -> dict | None:
    """Fetch call status from Bland.ai."""
    try:
        resp = requests.get(
            f"{BLAND_BASE}/calls/{call_id}",
            headers=BLAND_HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
        log.warning(f"bland_get_call {call_id}: HTTP {resp.status_code}")
        return None
    except requests.RequestException as e:
        log.warning(f"bland_get_call {call_id} error: {e}")
        return None


class BlandBalanceError(Exception):
    pass

# ---------------------------------------------------------------------------
# LEAD SOURCES
# ---------------------------------------------------------------------------

def fetch_hot_leads(state: dict) -> list[dict]:
    """Pull contacts tagged `hot-lead` from GHL."""
    log.info("Fetching hot leads from GHL (tag: hot-lead)...")
    contacts = ghl_fetch_contacts_by_tag("hot-lead", limit=50)
    leads = []
    for c in contacts:
        cid = c.get("id")
        if not cid:
            continue
        phone = c.get("phone") or ""
        if not phone or not phone.startswith("+"):
            # Try to normalize
            phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if len(phone) == 10:
                phone = "+1" + phone
            elif len(phone) == 11 and phone.startswith("1"):
                phone = "+" + phone
        if not phone or len(phone) < 12:
            continue
        tags = [t.lower() for t in (c.get("tags") or [])]
        industry = _detect_industry_from_tags(tags)
        leads.append({
            "contact_id": cid,
            "first_name": c.get("firstName") or c.get("name", "there").split()[0],
            "company": c.get("companyName") or c.get("name") or "your company",
            "phone": phone,
            "industry": industry,
            "source": "ghl_hot_lead",
            "tags": tags,
        })
    log.info(f"Found {len(leads)} hot leads")
    return leads


def fetch_cold_leads(state: dict) -> list[dict]:
    """Pull contacts tagged `cold-outreach` from GHL, then check CSV."""
    log.info("Fetching cold leads from GHL (tag: cold-outreach)...")
    leads = []

    # GHL cold-outreach contacts
    contacts = ghl_fetch_contacts_by_tag("cold-outreach", limit=100)
    for c in contacts:
        cid = c.get("id")
        if not cid:
            continue
        phone = _normalize_phone(c.get("phone") or "")
        if not phone:
            continue
        tags = [t.lower() for t in (c.get("tags") or [])]
        industry = _detect_industry_from_tags(tags)
        leads.append({
            "contact_id": cid,
            "first_name": c.get("firstName") or "there",
            "company": c.get("companyName") or c.get("name") or "your company",
            "phone": phone,
            "industry": industry,
            "source": "ghl_cold_outreach",
            "tags": tags,
        })

    # CSV fallback from leads dir
    if LEADS_DIR.exists():
        csv_files = list(LEADS_DIR.glob("*.csv"))
        for csv_path in csv_files:
            csv_leads = _load_csv_leads(csv_path)
            leads.extend(csv_leads)
            log.info(f"Loaded {len(csv_leads)} leads from {csv_path.name}")

    log.info(f"Found {len(leads)} cold leads total")
    return leads


def _load_csv_leads(path: Path) -> list[dict]:
    """Load leads from CSV. Expected columns: phone, first_name, company, industry (flexible)."""
    results = []
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize field names (case-insensitive)
                row_lower = {k.lower().strip(): v for k, v in row.items()}
                phone = _normalize_phone(
                    row_lower.get("phone") or row_lower.get("phone_number") or ""
                )
                if not phone:
                    continue
                contact_id = row_lower.get("contact_id") or row_lower.get("id") or f"csv_{phone}"
                results.append({
                    "contact_id": contact_id,
                    "first_name": row_lower.get("first_name") or row_lower.get("firstname") or "there",
                    "company": row_lower.get("company") or row_lower.get("business_name") or "your company",
                    "phone": phone,
                    "industry": row_lower.get("industry") or "general",
                    "source": f"csv:{path.name}",
                    "tags": [],
                })
    except (OSError, csv.Error) as e:
        log.warning(f"Could not read CSV {path}: {e}")
    return results


def _normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    if len(digits) > 11:
        return ""
    return ""


def _detect_industry_from_tags(tags: list[str]) -> str:
    industry_map = {
        "hvac": "HVAC",
        "locksmith": "Locksmith",
        "plumbing": "Plumbing",
        "electrical": "Electrical",
        "roofing": "Roofing",
        "pest-control": "Pest Control",
        "pest_control": "Pest Control",
        "towing": "Towing",
        "dental": "Dental",
        "med-spa": "Med Spa",
        "medspa": "Med Spa",
        "legal": "Legal",
        "veterinary": "Veterinary",
        "auto-repair": "Auto Repair",
        "cleaning": "Cleaning",
        "property-management": "Property Management",
        "water-damage": "Water Damage",
        "landscaping": "Landscaping",
        "general-contractor": "General Contractor",
    }
    for tag in tags:
        for key, value in industry_map.items():
            if key in tag.lower():
                return value
    return "general service"

# ---------------------------------------------------------------------------
# CALL FILTERING
# ---------------------------------------------------------------------------

def _is_eligible(contact_id: str, state: dict, dry_run: bool = False) -> tuple[bool, str]:
    """
    Return (eligible, reason). A contact is skipped if:
    - Already called successfully (outcome=answered/voicemail) within today
    - Retry count >= MAX_RETRIES
    - Has do-not-call / unsubscribed / customer / pilot-active tag
    """
    history = state["called_contacts"].get(contact_id, {})
    if not history:
        return True, "new"

    retry_count = history.get("retry_count", 0)
    if retry_count >= MAX_RETRIES:
        return False, f"max_retries_reached ({retry_count})"

    last_call_str = history.get("last_call")
    if last_call_str:
        try:
            last_call = datetime.fromisoformat(last_call_str)
            hours_since = (datetime.now() - last_call).total_seconds() / 3600
            if hours_since < RETRY_GAP_HOURS:
                return False, f"retry_gap ({hours_since:.1f}h < {RETRY_GAP_HOURS}h)"
        except ValueError:
            pass

    return True, "retry"


def _filter_leads(leads: list[dict], state: dict, skip_tags: set[str] = None, dry_run: bool = False) -> list[dict]:
    if skip_tags is None:
        skip_tags = {
            "do-not-contact", "unsubscribed", "customer", "active-client",
            "pilot-active", "pilot-converted", "cold-caller-done",
        }
    eligible = []
    for lead in leads:
        cid = lead["contact_id"]
        # Tag exclusion
        lead_tags = set(t.lower() for t in lead.get("tags", []))
        if lead_tags & skip_tags:
            log.debug(f"Skipping {cid} — excluded tag: {lead_tags & skip_tags}")
            continue
        ok, reason = _is_eligible(cid, state, dry_run)
        if ok:
            eligible.append(lead)
        else:
            log.debug(f"Skipping {cid} — {reason}")
    return eligible

# ---------------------------------------------------------------------------
# OUTCOME PARSING
# ---------------------------------------------------------------------------

def _parse_bland_outcome(call_data: dict) -> str:
    """
    Map Bland.ai call data to our outcome categories:
    answered / voicemail / no_answer / interested / not_interested / failed
    """
    status = (call_data.get("status") or "").lower()
    completed = call_data.get("completed", False)
    duration = call_data.get("call_length") or call_data.get("duration") or 0
    transcript = (call_data.get("transcript") or "").lower()

    if status in ("failed", "error"):
        return "failed"

    if not completed:
        if status in ("no-answer", "no_answer", "busy", "timeout"):
            return "no_answer"
        return "no_answer"

    # If completed, look at transcript for interest signals
    interest_signals = [
        "yes", "sure", "sounds good", "interested", "tell me more",
        "set it up", "free trial", "pilot", "how does it work",
        "email", "sign me up", "let's do it",
    ]
    disinterest_signals = [
        "not interested", "no thank you", "no thanks", "don't call",
        "take me off", "remove me", "stop calling",
    ]

    if any(sig in transcript for sig in interest_signals):
        return "interested"
    if any(sig in transcript for sig in disinterest_signals):
        return "not_interested"

    if duration and float(duration) < 15:
        return "voicemail"

    return "answered"

# ---------------------------------------------------------------------------
# COMMANDS
# ---------------------------------------------------------------------------

def cmd_call(dry_run: bool = False):
    """Make calls to hot leads first, then cold leads. Max 20 per run."""
    state = load_state()
    state = reset_daily_stats_if_new_day(state)
    state["last_run"] = datetime.now().isoformat()

    hot_leads  = fetch_hot_leads(state)
    cold_leads = fetch_cold_leads(state)

    # Hot leads first
    all_leads = hot_leads + cold_leads

    eligible = _filter_leads(all_leads, state, dry_run=dry_run)
    to_call  = eligible[:MAX_CALLS_PER_RUN]

    if not to_call:
        log.info("No eligible leads to call right now.")
        save_state(state)
        return

    log.info(f"Calling {len(to_call)} leads (dry_run={dry_run})")
    calls_this_run = 0

    try:
        for lead in to_call:
            cid     = lead["contact_id"]
            phone   = lead["phone"]
            name    = lead["first_name"]
            company = lead["company"]
            industry = lead["industry"]

            result = bland_place_call(phone, name, company, industry, cid, dry_run=dry_run)

            now = datetime.now().isoformat()

            if result:
                call_id = result.get("call_id", "unknown")
                state["pending_calls"][call_id] = {
                    "contact_id": cid,
                    "name": name,
                    "company": company,
                    "phone": phone,
                    "industry": industry,
                    "dispatched_at": now,
                    "source": lead.get("source", "unknown"),
                    "dry_run": dry_run,
                }
                history = state["called_contacts"].setdefault(cid, {
                    "call_count": 0,
                    "retry_count": 0,
                    "outcomes": [],
                    "last_call": None,
                })
                history["call_count"] += 1
                history["last_call"] = now

                state["daily_stats"]["calls_made"] += 1
                state["total_stats"]["calls_made"]  += 1
                calls_this_run += 1

                # Activity log
                ntfy(
                    NTFY_ACTIVITY,
                    f"Call dispatched: {company}",
                    f"{name} @ {company} ({industry})\n{phone}\nCall ID: {call_id}",
                    priority="low",
                    tags="phone",
                )

                append_call_log({
                    "timestamp": now,
                    "contact_id": cid,
                    "call_id": call_id,
                    "business_name": company,
                    "phone": phone,
                    "industry": industry,
                    "outcome": "dispatched",
                    "duration": None,
                    "source": lead.get("source"),
                    "dry_run": dry_run,
                })

            else:
                log.warning(f"Failed to dispatch call to {phone} ({company})")
                history = state["called_contacts"].setdefault(cid, {
                    "call_count": 0, "retry_count": 0, "outcomes": [], "last_call": None
                })
                history["retry_count"] = history.get("retry_count", 0) + 1
                history["last_call"] = now
                state["daily_stats"]["failed"] += 1

            # Small gap between calls to avoid hammering Bland.ai
            if not dry_run:
                time.sleep(2)

    except BlandBalanceError:
        log.critical("Stopping call run — Bland.ai balance depleted.")
    finally:
        save_state(state)

    log.info(f"Run complete. Dispatched {calls_this_run} calls.")


def cmd_check():
    """Poll Bland.ai for outcomes of pending calls. Update state + log."""
    state = load_state()
    state = reset_daily_stats_if_new_day(state)

    pending = state.get("pending_calls", {})
    if not pending:
        log.info("No pending calls to check.")
        save_state(state)
        return

    log.info(f"Checking {len(pending)} pending calls...")
    resolved = []

    for call_id, info in list(pending.items()):
        if info.get("dry_run"):
            log.info(f"Skipping dry-run call {call_id}")
            resolved.append(call_id)
            continue

        call_data = bland_get_call(call_id)
        if not call_data:
            log.warning(f"Could not fetch status for {call_id}")
            continue

        bland_status = (call_data.get("status") or "").lower()
        completed    = call_data.get("completed", False)

        # Skip if still in progress
        if bland_status in ("in-progress", "queued", "ringing") or not completed:
            dispatched = info.get("dispatched_at", "")
            if dispatched:
                try:
                    age_hours = (datetime.now() - datetime.fromisoformat(dispatched)).total_seconds() / 3600
                    if age_hours > 2:
                        log.warning(f"Call {call_id} stuck for {age_hours:.1f}h — marking failed")
                        _record_outcome(state, call_id, info, "failed", call_data)
                        resolved.append(call_id)
                except ValueError:
                    pass
            continue

        outcome = _parse_bland_outcome(call_data)
        _record_outcome(state, call_id, info, outcome, call_data)
        resolved.append(call_id)

    for call_id in resolved:
        pending.pop(call_id, None)

    state["pending_calls"] = pending
    save_state(state)
    log.info(f"Resolved {len(resolved)} calls.")


def _record_outcome(state: dict, call_id: str, info: dict, outcome: str, call_data: dict):
    """Update state + call log + send alerts for a resolved call."""
    cid      = info.get("contact_id", "")
    name     = info.get("name", "Unknown")
    company  = info.get("company", "Unknown")
    phone    = info.get("phone", "")
    industry = info.get("industry", "")
    duration = call_data.get("call_length") or call_data.get("duration") or 0

    now = datetime.now().isoformat()

    # Update called_contacts history
    history = state["called_contacts"].setdefault(cid, {
        "call_count": 0, "retry_count": 0, "outcomes": [], "last_call": None
    })
    history["outcomes"].append({"outcome": outcome, "call_id": call_id, "at": now})
    history["last_call"] = now

    # Update daily stats
    if outcome in state["daily_stats"]:
        state["daily_stats"][outcome] += 1
    if outcome == "answered":
        state["daily_stats"]["answered"] += 1

    # If not interested or voicemail, increment retry counter
    if outcome in ("no_answer", "failed"):
        history["retry_count"] = history.get("retry_count", 0) + 1

    log.info(f"Outcome: {outcome} | {name} @ {company} | call_id={call_id} | duration={duration}s")

    # Append to call log
    append_call_log({
        "timestamp": now,
        "call_id": call_id,
        "contact_id": cid,
        "business_name": company,
        "phone": phone,
        "industry": industry,
        "outcome": outcome,
        "duration": duration,
        "transcript_snippet": (call_data.get("transcript") or "")[:300],
        "recording_url": call_data.get("recording_url") or "",
    })

    # INTERESTED — fire URGENT alert + SMS to Wallace
    if outcome == "interested":
        state["daily_stats"]["interested"] = state["daily_stats"].get("interested", 0) + 1
        state["total_stats"]["interested"]  = state["total_stats"].get("interested", 0) + 1

        ntfy(
            NTFY_URGENT,
            f"[CRITICAL] HOT LEAD: {company}",
            (
                f"INTERESTED on cold call!\n"
                f"Name: {name}\n"
                f"Company: {company}\n"
                f"Industry: {industry}\n"
                f"Phone: {phone}\n"
                f"Call duration: {duration}s\n"
                f"Call ID: {call_id}\n\n"
                f"Text them now — they're warm."
            ),
            priority="urgent",
            tags="fire,phone",
        )

        # SMS alert to Wallace via GHL
        sms_body = (
            f"HOT LEAD on cold call: {name} @ {company} ({industry}) "
            f"— {phone} — said interested. Call ID: {call_id}. Text them now."
        )
        sent = ghl_send_sms(WALLACE_CONTACT_ID, sms_body)
        if sent:
            log.info("SMS alert sent to Wallace.")
        else:
            log.warning("SMS to Wallace failed — ntfy backup sent.")

        # Tag the GHL contact
        if cid and not cid.startswith("csv_") and not cid.startswith("dry_run_"):
            ghl_tag_contact(cid, ["cold-caller-interested", "hot-lead"])


def cmd_retry():
    """Retry failed/no-answer calls that are past the gap threshold."""
    state = load_state()
    state = reset_daily_stats_if_new_day(state)

    retry_candidates = []
    for cid, history in state["called_contacts"].items():
        retry_count = history.get("retry_count", 0)
        if retry_count == 0 or retry_count >= MAX_RETRIES:
            continue
        last_call_str = history.get("last_call")
        if not last_call_str:
            continue
        try:
            last_call = datetime.fromisoformat(last_call_str)
            hours_since = (datetime.now() - last_call).total_seconds() / 3600
            if hours_since >= RETRY_GAP_HOURS:
                retry_candidates.append(cid)
        except ValueError:
            continue

    if not retry_candidates:
        log.info("No calls eligible for retry right now.")
        return

    log.info(f"Found {len(retry_candidates)} calls to retry.")

    # We need lead info — pull from pending or call log
    call_log_index = _build_call_log_index()

    try:
        for cid in retry_candidates[:MAX_CALLS_PER_RUN]:
            entry = call_log_index.get(cid)
            if not entry:
                log.warning(f"No call log entry for {cid} — skipping retry")
                continue

            phone    = entry.get("phone", "")
            name     = entry.get("business_name", "there").split()[0]
            company  = entry.get("business_name", "your company")
            industry = entry.get("industry", "general service")

            if not phone:
                continue

            result = bland_place_call(phone, name, company, industry, cid)
            now = datetime.now().isoformat()

            history = state["called_contacts"][cid]
            if result:
                call_id = result.get("call_id", "unknown")
                state["pending_calls"][call_id] = {
                    "contact_id": cid,
                    "name": name,
                    "company": company,
                    "phone": phone,
                    "industry": industry,
                    "dispatched_at": now,
                    "source": "retry",
                }
                history["call_count"] += 1
                history["last_call"]   = now
                state["daily_stats"]["calls_made"] += 1
                state["total_stats"]["calls_made"]  += 1
                log.info(f"Retry dispatched for {company}: {call_id}")
            else:
                history["retry_count"] += 1
                if history["retry_count"] >= MAX_RETRIES:
                    log.info(f"Max retries reached for {cid} — marking dead")
                    if cid and not cid.startswith("csv_"):
                        ghl_tag_contact(cid, ["cold-caller-done"])

            time.sleep(2)

    except BlandBalanceError:
        log.critical("Stopping retries — Bland.ai balance depleted.")
    finally:
        save_state(state)


def _build_call_log_index() -> dict[str, dict]:
    """Build a contact_id → most recent call log entry dict."""
    if not CALL_LOG.exists():
        return {}
    try:
        with open(CALL_LOG, "r") as f:
            records = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    index = {}
    for r in records:
        cid = r.get("contact_id")
        if cid:
            index[cid] = r  # Later records overwrite — keeps most recent
    return index


def cmd_summary():
    """Send daily summary to ntfy SALES at 8pm."""
    state = load_state()
    stats = state.get("daily_stats", {})
    total = state.get("total_stats", {})
    date  = stats.get("date", datetime.now().strftime("%Y-%m-%d"))

    calls_made     = stats.get("calls_made", 0)
    answered       = stats.get("answered", 0)
    voicemail      = stats.get("voicemail", 0)
    no_answer      = stats.get("no_answer", 0)
    interested     = stats.get("interested", 0)
    not_interested = stats.get("not_interested", 0)
    failed         = stats.get("failed", 0)

    pickup_rate = round((answered / calls_made * 100), 1) if calls_made else 0
    interest_rate = round((interested / calls_made * 100), 1) if calls_made else 0

    body = (
        f"COLD CALLER DAILY SUMMARY — {date}\n\n"
        f"Calls made:     {calls_made}\n"
        f"Answered:       {answered} ({pickup_rate}%)\n"
        f"Voicemail:      {voicemail}\n"
        f"No answer:      {no_answer}\n"
        f"Interested:     {interested} ({interest_rate}%)\n"
        f"Not interested: {not_interested}\n"
        f"Failed:         {failed}\n\n"
        f"TOTAL STATS\n"
        f"All-time calls:      {total.get('calls_made', 0)}\n"
        f"All-time interested: {total.get('interested', 0)}\n"
        f"Pilots started:      {total.get('pilots_started', 0)}\n\n"
        f"Pending calls in queue: {len(state.get('pending_calls', {}))}"
    )

    ntfy(
        NTFY_SALES,
        f"Cold Caller Summary — {date}",
        body,
        priority="default",
        tags="phone,bar_chart",
    )
    log.info("Daily summary sent to ntfy SALES.")
    print(body)


def cmd_status():
    """Print engine stats to console."""
    state = load_state()
    stats = state.get("daily_stats", {})
    total = state.get("total_stats", {})
    pending = state.get("pending_calls", {})
    called  = state.get("called_contacts", {})

    print("\n=== COLD CALLER v2 STATUS ===")
    print(f"State file:       {STATE_FILE}")
    print(f"Call log:         {CALL_LOG}")
    print(f"Last run:         {state.get('last_run', 'never')}")
    print()
    print(f"--- TODAY ({stats.get('date', 'N/A')}) ---")
    print(f"Calls made:       {stats.get('calls_made', 0)}")
    print(f"Answered:         {stats.get('answered', 0)}")
    print(f"Voicemail:        {stats.get('voicemail', 0)}")
    print(f"No answer:        {stats.get('no_answer', 0)}")
    print(f"Interested:       {stats.get('interested', 0)}")
    print(f"Not interested:   {stats.get('not_interested', 0)}")
    print(f"Failed dispatches:{stats.get('failed', 0)}")
    print()
    print(f"--- ALL TIME ---")
    print(f"Calls made:       {total.get('calls_made', 0)}")
    print(f"Interested:       {total.get('interested', 0)}")
    print(f"Pilots started:   {total.get('pilots_started', 0)}")
    print()
    print(f"Pending calls:    {len(pending)}")
    print(f"Contacts called:  {len(called)}")

    # Show pending calls
    if pending:
        print("\n--- PENDING CALLS ---")
        for call_id, info in list(pending.items())[:10]:
            age = ""
            dispatched = info.get("dispatched_at", "")
            if dispatched:
                try:
                    delta = datetime.now() - datetime.fromisoformat(dispatched)
                    age = f" ({int(delta.total_seconds() / 60)}m ago)"
                except ValueError:
                    pass
            print(f"  {call_id[:20]}... | {info.get('company')} | {info.get('phone')}{age}")

    print()


def cmd_test():
    """Dry run — logs what would be called without placing any calls."""
    log.info("=== TEST MODE (dry run) ===")
    state = load_state()

    hot_leads  = fetch_hot_leads(state)
    cold_leads = fetch_cold_leads(state)
    all_leads  = hot_leads + cold_leads
    eligible   = _filter_leads(all_leads, state, dry_run=True)
    to_call    = eligible[:MAX_CALLS_PER_RUN]

    print(f"\nDRY RUN RESULTS")
    print(f"Hot leads found:   {len(hot_leads)}")
    print(f"Cold leads found:  {len(cold_leads)}")
    print(f"Eligible to call:  {len(eligible)}")
    print(f"Would call (cap):  {len(to_call)}")
    print()

    for i, lead in enumerate(to_call, 1):
        print(f"  [{i:02}] {lead['company']:35} {lead['phone']}  ({lead['industry']}) [{lead['source']}]")

    cmd_call(dry_run=True)
    print("\nDry run complete. No actual calls placed.")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

COMMANDS = {
    "call":    cmd_call,
    "check":   cmd_check,
    "retry":   cmd_retry,
    "summary": cmd_summary,
    "status":  cmd_status,
    "test":    cmd_test,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python3 cold-caller-v2.py [{' | '.join(COMMANDS)}]")
        print()
        print("  call    — Make calls (hot leads first, max 20/run)")
        print("  check   — Poll Bland.ai for pending call outcomes")
        print("  retry   — Retry failed/no-answer calls (2x max, 4hr gap)")
        print("  summary — Send daily summary to ntfy SALES")
        print("  status  — Show engine stats")
        print("  test    — Dry run (no actual calls)")
        sys.exit(1)

    command = sys.argv[1]
    log.info(f"cold-caller-v2.py starting — command: {command}")

    try:
        COMMANDS[command]()
    except BlandBalanceError:
        log.critical("Engine halted — Bland.ai balance depleted. Top up at app.bland.ai")
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log.critical(f"Unhandled crash in {command}: {e}\n{tb}")
        ntfy(
            NTFY_SYSTEM,
            f"[CRITICAL] Cold Caller Crashed",
            f"Command: {command}\nError: {e}\n\n{tb[:500]}",
            priority="urgent",
            tags="warning",
        )
        sys.exit(1)
