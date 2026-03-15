#!/usr/bin/env python3
"""
HOT LEAD FOLLOW-UP SEQUENCE — The Call Taker
=============================================
5-step automated follow-up sequence for contacts tagged "hot-lead" in GHL.

Sequence:
  Step 1 (Day 0, Immediate):  SMS — pain hook + pilot offer + scarcity
  Step 2 (Day 1, 24 hours):   Email — missed call costs, competitor angle, case studies
  Step 3 (Day 2, 48 hours):   Voicemail drop via Bland.ai
  Step 4 (Day 4, 96 hours):   SMS — social proof + scarcity countdown
  Step 5 (Day 7, 168 hours):  Breakup email — last chance, then silence

Commands:
  scan    — Find hot-lead contacts not yet enrolled
  send    — Execute due steps for enrolled contacts
  status  — Show enrollment stats and step counts
  run     — scan + send (full cycle)
  test    — Dry run: scan + simulate sends without actually sending

Schedule: scan every 2 hours, send 3x daily (9am, 1pm, 5pm) via launchd

launchd plists (install to ~/Library/LaunchAgents/):

--- com.thecalltaker.hot-lead-sequence.scan.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.thecalltaker.hot-lead-sequence.scan</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string>
    <string>/Users/wallacedobbs/thecalltaker/ops/hot-lead-sequence.py</string>
    <string>scan</string>
  </array>
  <key>StartInterval</key><integer>7200</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key>
    <string>/Users/wallacedobbs/thecalltaker/ops/hot-lead-sequence-stdout.log</string>
  <key>StandardErrorPath</key>
    <string>/Users/wallacedobbs/thecalltaker/ops/hot-lead-sequence-stderr.log</string>
</dict></plist>

--- com.thecalltaker.hot-lead-sequence.send.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.thecalltaker.hot-lead-sequence.send</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string>
    <string>/Users/wallacedobbs/thecalltaker/ops/hot-lead-sequence.py</string>
    <string>send</string>
  </array>
  <key>StartCalendarInterval</key><array>
    <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>StandardOutPath</key>
    <string>/Users/wallacedobbs/thecalltaker/ops/hot-lead-sequence-stdout.log</string>
  <key>StandardErrorPath</key>
    <string>/Users/wallacedobbs/thecalltaker/ops/hot-lead-sequence-stderr.log</string>
</dict></plist>
"""

import sys
import os
import json
import time
import tempfile
import traceback
import requests
from datetime import datetime, timedelta

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY     = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL    = "https://services.leadconnectorhq.com"
BLAND_API_KEY   = os.environ.get("TCT_BLAND_API_KEY",
    "org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969")
BLAND_BASE_URL  = "https://api.bland.ai/v1"

BOOKING_URL    = "https://thecalltaker.com/book"
TRY_LIVE_URL   = "https://thecalltaker.com/try-live.html"
DEMO_LINE      = "(615) 784-5747"
WALLACE_PHONE  = "+16156539004"
WALLACE_GHL_ID = "DtKLG28VzgUb6q3brILD"
FROM_EMAIL     = "thecalltakerai@gmail.com"

# ntfy topics
NTFY_URGENT   = "tct-urgent-Hk9UOEZR"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_SYSTEM   = "tct-system-vRsfXQRQ"

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
STATE_FILE  = os.path.join(SCRIPT_DIR, "hot-lead-sequence-state.json")
LOG_FILE    = os.path.join(SCRIPT_DIR, "hot-lead-sequence.log")

# Rate limits per run
MAX_SMS_PER_DAY   = 20
MAX_EMAIL_PER_DAY = 30

# GHL API headers
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-HotLeadSequence/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-HotLeadSequence/1.0",
}

# ─── Exclusion Tags ─────────────────────────────────────────────────────────

EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "donny-closing",
}

# Tags that signal a positive outcome — pause sequence, alert Wallace
POSITIVE_REPLY_TAGS = {
    "contacted", "pilot-active", "pilot-signup", "hot-reply",
    "demo-booked", "interested", "pilot-converted", "customer",
}

# ─── Step Timing ─────────────────────────────────────────────────────────────
# (step_num, delay_minutes_from_enrollment, channel)

STEP_SCHEDULE = [
    (1, 0,     "sms"),       # Day 0 — immediate
    (2, 1440,  "email"),     # Day 1 — 24 hours
    (3, 2880,  "voicemail"), # Day 2 — 48 hours (Bland.ai)
    (4, 5760,  "sms"),       # Day 4 — 96 hours
    (5, 10080, "email"),     # Day 7 — 168 hours (breakup)
]

# ─── Industry Hooks ──────────────────────────────────────────────────────────
# tag -> (job_word, avg_job_value, display_name, pain_hook)

INDUSTRY_HOOKS = {
    "hvac": (
        "service call", "$350+", "HVAC",
        "One missed AC emergency call in July is $500 you'll never get back"
    ),
    "plumbing": (
        "service call", "$300+", "plumbing",
        "A burst pipe call at 2am goes to voicemail — that's a $400 job walking to your competitor"
    ),
    "electrical": (
        "service call", "$275+", "electrical",
        "Homeowners with no power don't leave voicemails — they call the next electrician"
    ),
    "roofing": (
        "roof job", "$5,000+", "roofing",
        "One missed storm damage call could be a $10K roof replacement that goes to the other guy"
    ),
    "locksmith": (
        "emergency call", "$250+", "locksmith",
        "Someone locked out at midnight won't wait for a callback — they'll call the next locksmith in 10 seconds"
    ),
    "dental": (
        "appointment", "$400+", "dental",
        "A new patient calling for a cleaning is worth $3K+ over their lifetime — if you answer"
    ),
    "medspa": (
        "appointment", "$500+", "med spa",
        "Botox clients calling to book won't leave a voicemail — they'll book with whoever picks up"
    ),
    "legal": (
        "case consultation", "$500+", "legal",
        "A potential client with a fresh injury case calls 3 firms — the one that answers first wins"
    ),
    "veterinary": (
        "appointment", "$200+", "veterinary",
        "A panicking pet owner isn't going to wait for your voicemail to call back"
    ),
    "towing": (
        "tow call", "$150+", "towing",
        "Stranded drivers call the first tow company that answers — not the best rated"
    ),
    "garage-door": (
        "service call", "$300+", "garage door",
        "A broken garage door at 6am means they need someone NOW — not after business hours"
    ),
    "pest-control": (
        "service call", "$200+", "pest control",
        "A homeowner who just found termites is calling everyone until someone picks up"
    ),
    "property-management": (
        "maintenance request", "$250+", "property management",
        "Tenants with emergencies don't wait — they escalate, leave bad reviews, or call a lawyer"
    ),
    "water-damage": (
        "emergency call", "$2,000+", "water damage restoration",
        "Water damage gets worse every minute — a missed call at midnight means 10x the repair cost"
    ),
    "cleaning": (
        "booking", "$200+", "cleaning",
        "A new client looking for weekly cleaning is worth $10K/year — if you answer the phone"
    ),
    "landscaping": (
        "estimate", "$300+", "landscaping",
        "Spring is when everyone calls for quotes — miss those calls and you miss the whole season"
    ),
    "auto-repair": (
        "repair job", "$400+", "auto repair",
        "A car that won't start means they need a shop TODAY — the first one that answers gets the job"
    ),
    "general-contractor": (
        "estimate", "$1,000+", "contracting",
        "A homeowner ready to remodel calls 3 contractors — only the one who picks up gets the meeting"
    ),
    "funeral": (
        "arrangement", "$3,000+", "funeral services",
        "Families making arrangements need compassionate, immediate response — voicemail won't cut it"
    ),
}

DEFAULT_INDUSTRY = ("service call", "$350+", "home services",
                    "Every missed call is a customer calling your competitor instead")


def get_industry_info(tags):
    """Return (job_word, job_value, display_name, pain_hook) from contact tags."""
    if not tags:
        return DEFAULT_INDUSTRY
    for tag in tags:
        key = tag.lower().strip()
        if key in INDUSTRY_HOOKS:
            return INDUSTRY_HOOKS[key]
    return DEFAULT_INDUSTRY


# ─── Logging ─────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] hot-lead-sequence: {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ─── State Management ────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            log("State file corrupted, starting fresh", "WARN")
    return {
        "enrolled": {},
        "daily_counts": {},
        "stats": {
            "total_enrolled": 0,
            "sms_sent": 0,
            "emails_sent": 0,
            "voicemails_sent": 0,
            "sequences_completed": 0,
            "positive_replies": 0,
        },
        "created": datetime.now().isoformat(),
    }


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(STATE_FILE), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, STATE_FILE)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def get_daily_counts(state):
    """Return today's send counts, resetting if it's a new day."""
    today = datetime.now().strftime("%Y-%m-%d")
    dc = state.get("daily_counts", {})
    if dc.get("date") != today:
        state["daily_counts"] = {"date": today, "sms": 0, "email": 0}
    return state["daily_counts"]


# ─── GHL API Helpers ─────────────────────────────────────────────────────────

def ghl_request(method, path, headers=None, params=None, json_body=None, retries=3):
    """GHL API request with retry + rate-limit handling."""
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    backoff = [5, 15, 30]

    for attempt in range(retries):
        try:
            resp = requests.request(
                method, url, headers=headers, params=params, json=json_body, timeout=30
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
            if resp.status_code == 400:
                log(f"Bad request: {resp.text[:300]}", "ERROR")
                return None
            if resp.status_code == 401:
                log("Authentication failed — check GHL API key", "ERROR")
                return None
            return resp.json() if resp.text else {}
        except requests.exceptions.RequestException as e:
            log(f"Request error: {e}", "ERROR")
            if attempt < retries - 1:
                time.sleep(backoff[min(attempt, 2)])
    return None


def search_contacts_by_tag(tag, limit=100):
    """Fetch all GHL contacts with a specific tag (paginated)."""
    results = []
    page = 1
    while True:
        data = ghl_request("GET", "/contacts/", params={
            "locationId": GHL_LOCATION_ID,
            "query": "",
            "limit": limit,
            "page": page,
        })
        if not data or "contacts" not in data:
            break
        contacts = data["contacts"]
        for c in contacts:
            ctags = c.get("tags", [])
            if isinstance(ctags, list) and tag in ctags:
                results.append(c)
        if len(contacts) < limit:
            break
        page += 1
        if page > 50:
            break
    return results


def get_contact(contact_id):
    """Fetch a single GHL contact."""
    data = ghl_request("GET", f"/contacts/{contact_id}")
    return data.get("contact") if data else None


def add_tag(contact_id, tags):
    """Add tags to a GHL contact."""
    if isinstance(tags, str):
        tags = [tags]
    return ghl_request("POST", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def remove_tag(contact_id, tags):
    """Remove tags from a GHL contact."""
    if isinstance(tags, str):
        tags = [tags]
    return ghl_request("DELETE", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def send_sms(contact_id, phone, message):
    """Send an SMS via GHL conversations API."""
    # Create or get conversation
    conv_data = ghl_request("POST", "/conversations/", headers=CONVERSATIONS_HEADERS,
                            json_body={"locationId": GHL_LOCATION_ID, "contactId": contact_id})
    if not conv_data:
        log(f"Failed to create conversation for {contact_id}", "ERROR")
        return False

    conv_id = conv_data.get("conversation", {}).get("id") or conv_data.get("conversationId")
    if not conv_id:
        log(f"No conversation ID returned for {contact_id}: {str(conv_data)[:200]}", "ERROR")
        return False

    result = ghl_request("POST", f"/conversations/messages", headers=CONVERSATIONS_HEADERS,
                         json_body={
                             "type": "SMS",
                             "contactId": contact_id,
                             "message": message,
                         })
    if result is None:
        log(f"SMS send failed for {contact_id}", "ERROR")
        return False
    log(f"SMS sent to {contact_id} ({phone})")
    return True


def send_email(contact_id, email, subject, html_body):
    """Send an email via GHL conversations API."""
    result = ghl_request("POST", f"/conversations/messages", headers=CONVERSATIONS_HEADERS,
                         json_body={
                             "type": "Email",
                             "contactId": contact_id,
                             "subject": subject,
                             "html": html_body,
                             "emailFrom": f"Wallace from The Call Taker <{FROM_EMAIL}>",
                         })
    if result is None:
        log(f"Email send failed for {contact_id}", "ERROR")
        return False
    log(f"Email sent to {contact_id} ({email}): {subject}")
    return True


def bland_voicemail_drop(phone, first_name, industry_label):
    """Place a Bland.ai call to drop a voicemail."""
    task = (
        f"Hey {first_name}, Wallace here from The Call Taker. Quick question — "
        f"how many calls did your business miss last night? Our AI answered 47 calls "
        f"for clients yesterday alone. I've got a free 14-day pilot with your name on it. "
        f"Text me back at this number or grab your spot at thecalltaker.com. Talk soon."
    )
    headers = {
        "Authorization": BLAND_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "phone_number": phone,
        "task": task,
        "voice": "mason",
        "wait_for_greeting": True,
        "max_duration": 60,
        "amd": True,
        "voicemail_message": task,
        "record": True,
        "from": None,
    }
    try:
        resp = requests.post(f"{BLAND_BASE_URL}/calls", headers=headers, json=payload, timeout=30)
        if resp.status_code == 402:
            log("Bland.ai balance depleted (402) — voicemail skipped", "ERROR")
            ntfy("Bland.ai 402 — balance empty, voicemail drops paused", NTFY_SYSTEM, priority="high")
            return False
        if resp.status_code == 200:
            data = resp.json()
            call_id = data.get("call_id", "unknown")
            log(f"Bland.ai voicemail queued for {phone}, call_id={call_id}")
            return True
        log(f"Bland.ai error {resp.status_code}: {resp.text[:200]}", "ERROR")
        return False
    except requests.exceptions.RequestException as e:
        log(f"Bland.ai request failed: {e}", "ERROR")
        return False


# ─── ntfy ────────────────────────────────────────────────────────────────────

def ntfy(message, topic=NTFY_ACTIVITY, priority="default", title=None):
    """Send an ntfy notification."""
    headers = {"Priority": priority}
    if title:
        # Sanitize title for ntfy header (ASCII only, no newlines)
        safe_title = "".join(c for c in title if 32 <= ord(c) < 127)
        headers["Title"] = safe_title[:250]
    for attempt in range(3):
        try:
            resp = requests.post(
                f"https://ntfy.sh/{topic}",
                data=message.encode("utf-8"),
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    return False


# ─── Contact Registry Check ─────────────────────────────────────────────────
# Lightweight check — reads the shared contact registry to avoid over-contacting

REGISTRY_FILE = os.path.join(SCRIPT_DIR, "contact-registry.json")


def check_registry(contact_id, touch_type):
    """Check if we can contact this lead (3-day gap for same touch type)."""
    if not os.path.exists(REGISTRY_FILE):
        return True, "no registry"
    try:
        with open(REGISTRY_FILE, "r") as f:
            registry = json.load(f)
    except (json.JSONDecodeError, IOError):
        return True, "registry unreadable"

    contact_data = registry.get(contact_id, {})
    touches = contact_data.get("touches", [])
    now = datetime.now()
    for touch in touches:
        if touch.get("type") == touch_type:
            touch_time = datetime.fromisoformat(touch["time"])
            gap = (now - touch_time).total_seconds() / 3600
            if gap < 72:  # 3-day minimum gap
                return False, f"same touch type '{touch_type}' sent {gap:.0f}h ago"
    # Check max 2 emails/week
    if touch_type == "email":
        week_ago = now - timedelta(days=7)
        email_count = sum(1 for t in touches
                         if t.get("type") == "email"
                         and datetime.fromisoformat(t["time"]) > week_ago)
        if email_count >= 2:
            return False, f"already sent {email_count} emails this week"
    return True, "ok"


def update_registry(contact_id, touch_type):
    """Record a touch in the contact registry."""
    registry = {}
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f:
                registry = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    if contact_id not in registry:
        registry[contact_id] = {"touches": []}

    registry[contact_id]["touches"].append({
        "engine": "hot-lead-sequence",
        "type": touch_type,
        "time": datetime.now().isoformat(),
    })

    # Prune touches older than 30 days
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    for cid in registry:
        registry[cid]["touches"] = [
            t for t in registry[cid].get("touches", [])
            if t.get("time", "") > cutoff
        ]

    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(REGISTRY_FILE), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(registry, f, indent=2)
        os.replace(tmp, REGISTRY_FILE)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# ─── Message Templates ──────────────────────────────────────────────────────

def step1_sms(first_name, industry_label):
    """Day 0 — Immediate SMS: pain hook + pilot offer."""
    return (
        f"Hey {first_name}, this is Wallace from The Call Taker. I saw you checked out "
        f"our demo — pretty wild, right? That AI handles calls exactly like that for "
        f"{industry_label} businesses 24/7. We have 3 pilot spots open this month. "
        f"Want me to set yours up? Takes 10 minutes."
    )


def step2_email_subject(first_name):
    """Day 1 — Email subject."""
    return f"{first_name}, your competitors are answering calls you're missing"


def step2_email_body(first_name, industry_label, job_word, job_value, pain_hook):
    """Day 1 — Email: missed call costs, competitor angle, case studies."""
    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
    <p>Hey {first_name},</p>

    <p>Here's the math that keeps {industry_label} owners up at night:</p>

    <p><strong>{pain_hook}.</strong></p>

    <p>The average {industry_label} business misses <strong>12-15 calls per week</strong>.
    At {job_value} per {job_word}, that's <strong>$2,000-$10,000/month</strong> in revenue
    walking straight to your competitor — the one who actually picks up.</p>

    <p>Your competitors aren't better than you. They just answer the phone.</p>

    <p>That's exactly why we built The Call Taker — an AI receptionist trained specifically
    for {industry_label} businesses. It answers every call in under 2 rings, 24/7/365.
    Books appointments. Captures caller info. Sends you a summary. No missed calls, ever.</p>

    <p><strong>What our clients are seeing:</strong></p>
    <ul>
        <li>HVAC company in Charleston: 41% missed call rate → 0%. Added $8,400/mo in revenue.</li>
        <li>Solo plumber in Tampa: +72% revenue in 60 days.</li>
        <li>Locksmith in Nashville: +65% emergency call revenue.</li>
    </ul>

    <p><strong>I'm offering you a free 14-day pilot.</strong> No card. No contract. No risk.
    Takes 10 minutes to set up — you just forward your overflow calls to our AI.</p>

    <p>After the pilot, plans start at <strong>$97/mo</strong> (most businesses choose the
    $297/mo full 24/7 plan). But honestly, if the AI doesn't pay for itself 10x over
    during the free trial, I don't want your money.</p>

    <p><strong>→ <a href="{TRY_LIVE_URL}" style="color: #F97316;">Try it live right now</a></strong>
    — call our demo line and hear the AI in action.</p>

    <p><strong>→ <a href="{BOOKING_URL}" style="color: #F97316;">Grab your pilot spot</a></strong>
    — only 3 left this month.</p>

    <p>Talk soon,<br>
    <strong>Wallace Dobbs</strong><br>
    The Call Taker<br>
    {DEMO_LINE}</p>
</div>"""


def step4_sms(first_name, industry_label):
    """Day 4 — SMS: social proof + scarcity countdown."""
    return (
        f"{first_name} — just had a {industry_label} company sign up yesterday. "
        f"They missed 12 calls last week before switching to us. Down to 2 pilot spots. "
        f"If you want in before they're gone: thecalltaker.com/book"
    )


def step5_email_subject():
    """Day 7 — Breakup email subject."""
    return "Last note from me"


def step5_email_body(first_name):
    """Day 7 — Breakup email: direct, respectful, final offer."""
    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
    <p>Hey {first_name},</p>

    <p>I've reached out a few times and I know you're busy — so this is my last note.</p>

    <p>If now isn't the right time, no worries at all. I'll back off.</p>

    <p>But if you're still losing calls to voicemail, I want you to know:
    the <strong>free 14-day pilot</strong> is still on the table. No card required.
    Takes 10 minutes to set up. You just forward your overflow calls and our AI
    handles the rest.</p>

    <p>After this week, the 3 spots we're holding go to our waitlist.</p>

    <p><strong>→ <a href="{TRY_LIVE_URL}" style="color: #F97316;">Hear the AI live</a></strong></p>

    <p><strong>→ <a href="{BOOKING_URL}" style="color: #F97316;">Claim your pilot spot</a></strong></p>

    <p>Either way, I wish you the best. Your business clearly does great work — I hope
    you're capturing every call that comes in.</p>

    <p>— Wallace</p>
</div>"""


# ─── Core Logic ──────────────────────────────────────────────────────────────

def should_exclude(contact):
    """Check if contact has any exclusion tags."""
    tags = contact.get("tags", [])
    if not isinstance(tags, list):
        return True
    for tag in tags:
        if tag.lower().strip() in EXCLUDE_TAGS:
            return True
    return False


def has_positive_reply(contact):
    """Check if contact has replied positively (has positive tags)."""
    tags = contact.get("tags", [])
    if not isinstance(tags, list):
        return False
    for tag in tags:
        if tag.lower().strip() in {t.lower() for t in POSITIVE_REPLY_TAGS}:
            return True
    return False


def cmd_scan(state, dry_run=False):
    """Find hot-lead contacts not yet enrolled in the sequence."""
    log("Scanning for hot-lead contacts...")
    contacts = search_contacts_by_tag("hot-lead")
    log(f"Found {len(contacts)} contacts with hot-lead tag")

    enrolled = state.get("enrolled", {})
    new_count = 0

    for contact in contacts:
        cid = contact.get("id")
        if not cid or cid in enrolled:
            continue
        if should_exclude(contact):
            log(f"Skipping {cid} — has exclusion tag")
            continue

        first_name = contact.get("firstName") or contact.get("first_name") or "there"
        email = contact.get("email", "")
        phone = contact.get("phone", "")
        tags = contact.get("tags", [])

        if not phone and not email:
            log(f"Skipping {cid} — no phone or email")
            continue

        industry_info = get_industry_info(tags)
        now = datetime.now().isoformat()

        enrolled[cid] = {
            "enrolled_at": now,
            "first_name": first_name,
            "email": email,
            "phone": phone,
            "tags": tags,
            "industry": industry_info[2],  # display_name
            "steps_completed": [],
            "last_step": 0,
            "status": "active",
        }
        new_count += 1

        if not dry_run:
            add_tag(cid, ["hot-lead-sequence"])

        log(f"Enrolled: {first_name} ({cid}) — {industry_info[2]}")

    state["enrolled"] = enrolled
    state["stats"]["total_enrolled"] = state["stats"].get("total_enrolled", 0) + new_count
    log(f"Scan complete: {new_count} new enrollments, {len(enrolled)} total in sequence")
    return new_count


def cmd_send(state, dry_run=False):
    """Execute due steps for all enrolled contacts."""
    log("Checking for due sends...")
    enrolled = state.get("enrolled", {})
    daily = get_daily_counts(state)
    now = datetime.now()
    sent_count = 0

    for cid, enrollment in list(enrolled.items()):
        if enrollment.get("status") != "active":
            continue

        # Re-check contact for exclusion/positive tags
        contact = get_contact(cid)
        if contact:
            if should_exclude(contact):
                log(f"Pausing {cid} — acquired exclusion tag")
                enrollment["status"] = "paused_excluded"
                continue
            if has_positive_reply(contact):
                log(f"Pausing {cid} — positive reply detected!")
                enrollment["status"] = "paused_replied"
                state["stats"]["positive_replies"] = state["stats"].get("positive_replies", 0) + 1
                ntfy(
                    f"Hot lead {enrollment['first_name']} ({enrollment['industry']}) "
                    f"replied positively during sequence step {enrollment['last_step']}!\n"
                    f"Phone: {enrollment.get('phone', 'N/A')}\n"
                    f"Email: {enrollment.get('email', 'N/A')}",
                    topic=NTFY_URGENT,
                    priority="high",
                    title="[HIGH] Hot Lead Engaged — Sequence Paused",
                )
                continue

        enrolled_at = datetime.fromisoformat(enrollment["enrolled_at"])
        completed = set(enrollment.get("steps_completed", []))
        first_name = enrollment.get("first_name", "there")
        phone = enrollment.get("phone", "")
        email = enrollment.get("email", "")
        tags = enrollment.get("tags", [])
        industry_info = get_industry_info(tags)
        job_word, job_value, industry_label, pain_hook = industry_info

        for step_num, delay_min, channel in STEP_SCHEDULE:
            if step_num in completed:
                continue

            due_at = enrolled_at + timedelta(minutes=delay_min)
            if now < due_at:
                break  # Not yet due; steps are ordered, so skip rest

            # Rate limit checks
            if channel == "sms" and daily.get("sms", 0) >= MAX_SMS_PER_DAY:
                log(f"SMS daily limit ({MAX_SMS_PER_DAY}) reached, skipping step {step_num} for {cid}")
                break
            if channel == "email" and daily.get("email", 0) >= MAX_EMAIL_PER_DAY:
                log(f"Email daily limit ({MAX_EMAIL_PER_DAY}) reached, skipping step {step_num} for {cid}")
                break

            # Registry check
            ok, reason = check_registry(cid, channel)
            if not ok:
                log(f"Registry block for {cid} step {step_num}: {reason}")
                break

            success = False

            if dry_run:
                log(f"[DRY RUN] Would send step {step_num} ({channel}) to {first_name} ({cid})")
                success = True
            elif channel == "sms" and phone:
                if step_num == 1:
                    msg = step1_sms(first_name, industry_label)
                elif step_num == 4:
                    msg = step4_sms(first_name, industry_label)
                else:
                    continue
                success = send_sms(cid, phone, msg)
                if success:
                    daily["sms"] = daily.get("sms", 0) + 1
                    state["stats"]["sms_sent"] = state["stats"].get("sms_sent", 0) + 1
                    update_registry(cid, "sms")
            elif channel == "email" and email:
                if step_num == 2:
                    subj = step2_email_subject(first_name)
                    body = step2_email_body(first_name, industry_label, job_word, job_value, pain_hook)
                elif step_num == 5:
                    subj = step5_email_subject()
                    body = step5_email_body(first_name)
                else:
                    continue
                success = send_email(cid, email, subj, body)
                if success:
                    daily["email"] = daily.get("email", 0) + 1
                    state["stats"]["emails_sent"] = state["stats"].get("emails_sent", 0) + 1
                    update_registry(cid, "email")
            elif channel == "voicemail" and phone:
                success = bland_voicemail_drop(phone, first_name, industry_label)
                if success:
                    state["stats"]["voicemails_sent"] = state["stats"].get("voicemails_sent", 0) + 1
                    update_registry(cid, "voicemail")
            else:
                log(f"No {channel} contact info for {cid}, skipping step {step_num}")
                # Mark as completed so we don't block on it
                success = True

            if success:
                enrollment["steps_completed"].append(step_num)
                enrollment["last_step"] = step_num
                sent_count += 1

                if not dry_run:
                    add_tag(cid, [f"hls-step-{step_num}"])
                    ntfy(
                        f"Step {step_num}/5 ({channel}) sent to {first_name} "
                        f"({industry_label}) — {cid}",
                        topic=NTFY_ACTIVITY,
                    )

                # Check if sequence complete
                if len(enrollment["steps_completed"]) >= len(STEP_SCHEDULE):
                    enrollment["status"] = "completed"
                    enrollment["completed_at"] = now.isoformat()
                    state["stats"]["sequences_completed"] = (
                        state["stats"].get("sequences_completed", 0) + 1
                    )
                    log(f"Sequence completed for {first_name} ({cid})")
                    if not dry_run:
                        add_tag(cid, ["hot-lead-sequence-done"])
                        remove_tag(cid, ["hot-lead-sequence"])

                # Small delay between sends to avoid hammering APIs
                if not dry_run:
                    time.sleep(2)

            break  # Only send one step per contact per run

    log(f"Send pass complete: {sent_count} messages sent")
    return sent_count


def cmd_status(state):
    """Print enrollment and step stats."""
    enrolled = state.get("enrolled", {})
    stats = state.get("stats", {})
    daily = get_daily_counts(state)

    active = sum(1 for e in enrolled.values() if e.get("status") == "active")
    completed = sum(1 for e in enrolled.values() if e.get("status") == "completed")
    paused_reply = sum(1 for e in enrolled.values() if e.get("status") == "paused_replied")
    paused_excl = sum(1 for e in enrolled.values() if e.get("status") == "paused_excluded")

    # Step distribution
    step_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for e in enrolled.values():
        if e.get("status") == "active":
            last = e.get("last_step", 0)
            if last in step_counts:
                step_counts[last] += 1

    print("\n" + "=" * 55)
    print("  HOT LEAD SEQUENCE — STATUS")
    print("=" * 55)
    print(f"  Total enrolled:      {stats.get('total_enrolled', 0)}")
    print(f"  Active:              {active}")
    print(f"  Completed:           {completed}")
    print(f"  Paused (replied):    {paused_reply}")
    print(f"  Paused (excluded):   {paused_excl}")
    print("-" * 55)
    print(f"  SMS sent (all time): {stats.get('sms_sent', 0)}")
    print(f"  Emails sent:         {stats.get('emails_sent', 0)}")
    print(f"  Voicemails sent:     {stats.get('voicemails_sent', 0)}")
    print(f"  Positive replies:    {stats.get('positive_replies', 0)}")
    print(f"  Sequences completed: {stats.get('sequences_completed', 0)}")
    print("-" * 55)
    print(f"  Today SMS:           {daily.get('sms', 0)} / {MAX_SMS_PER_DAY}")
    print(f"  Today Email:         {daily.get('email', 0)} / {MAX_EMAIL_PER_DAY}")
    print("-" * 55)
    print("  Active leads by step:")
    for s in range(1, 6):
        label = {1: "SMS intro", 2: "Pain email", 3: "Voicemail",
                 4: "Scarcity SMS", 5: "Breakup email"}[s]
        print(f"    Step {s} ({label}): {step_counts.get(s, 0)}")
    # Step 0 = just enrolled, not yet sent step 1
    awaiting = sum(1 for e in enrolled.values()
                   if e.get("status") == "active" and e.get("last_step", 0) == 0)
    if awaiting:
        print(f"    Awaiting step 1:   {awaiting}")
    print("=" * 55 + "\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: hot-lead-sequence.py <scan|send|status|run|test>")
        sys.exit(1)

    command = sys.argv[1].lower().strip()
    valid = {"scan", "send", "status", "run", "test"}
    if command not in valid:
        print(f"Unknown command: {command}")
        print(f"Valid commands: {', '.join(sorted(valid))}")
        sys.exit(1)

    state = load_state()

    try:
        if command == "scan":
            cmd_scan(state)
            save_state(state)

        elif command == "send":
            cmd_send(state)
            save_state(state)

        elif command == "run":
            cmd_scan(state)
            cmd_send(state)
            save_state(state)

        elif command == "test":
            log("=== DRY RUN MODE ===")
            cmd_scan(state, dry_run=True)
            cmd_send(state, dry_run=True)
            # Don't save state in test mode
            cmd_status(state)
            log("=== DRY RUN COMPLETE — nothing was sent ===")

        elif command == "status":
            cmd_status(state)

    except Exception as e:
        tb = traceback.format_exc()
        log(f"CRASH: {e}\n{tb}", "ERROR")
        ntfy(
            f"hot-lead-sequence crashed on '{command}': {e}\n{tb[:500]}",
            topic=NTFY_SYSTEM,
            priority="high",
            title="[CRITICAL] hot-lead-sequence crash",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
