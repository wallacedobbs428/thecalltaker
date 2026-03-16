#!/usr/bin/env python3
"""
GHL REACTIVATION WORKFLOW — Hot Lead Reactivation: Founding 10
================================================================
5-message reactivation sequence targeting 35 hot leads.

Goal: Get a demo booked. Move contacts to "demo-booked" when they reply
and confirm a time.

Sequence:
  Message 1 (Day 0):  SMS — missed calls question (industry-personalized)
                       Email fallback if no cell phone
  Message 2 (Day 3):  SMS — follow-up, "didn't want this buried"
  Message 3 (Day 5):  SMS — value pitch, AI receptionist Jessica, demo offer
  Message 4 (REPLY-TRIGGERED ONLY): SMS — price hesitation handler
                       Only fires when contact is tagged "price-hesitation"
  Message 5 (Day 10): SMS — breakup, final CTA, then exhaustion tagging

Branch Logic:
  - Reply detected after any message → Reply Handler (pause, alert Wallace, 2hr task)
  - No reply → continue to next scheduled message
  - After Message 5 → add "reactivation-exhausted", remove "hot-lead-reactivation"
  - Message 4 is NOT in the normal flow — only triggered by "price-hesitation" tag

Commands:
  scan     — Find contacts tagged "hot-lead-reactivation" not yet enrolled
  send     — Execute due messages for enrolled contacts
  enroll   — Tag all "hot-lead" contacts with "hot-lead-reactivation" to trigger
  status   — Show enrollment stats and message counts
  run      — scan + send (full cycle)
  preview  — Preview all messages for a sample contact (dry run)

Schedule: Run 2x daily (9am, 2pm) via launchd

launchd plists (install to ~/Library/LaunchAgents/):

--- com.thecalltaker.reactivation.scan.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.thecalltaker.reactivation.scan</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string>
    <string>/Users/wallacedobbs/thecalltaker/ops/ghl-reactivation-workflow.py</string>
    <string>scan</string>
  </array>
  <key>StartInterval</key><integer>7200</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key>
    <string>/Users/wallacedobbs/thecalltaker/ops/reactivation-stdout.log</string>
  <key>StandardErrorPath</key>
    <string>/Users/wallacedobbs/thecalltaker/ops/reactivation-stderr.log</string>
</dict></plist>

--- com.thecalltaker.reactivation.send.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.thecalltaker.reactivation.send</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string>
    <string>/Users/wallacedobbs/thecalltaker/ops/ghl-reactivation-workflow.py</string>
    <string>send</string>
  </array>
  <key>StartCalendarInterval</key><array>
    <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>StandardOutPath</key>
    <string>/Users/wallacedobbs/thecalltaker/ops/reactivation-stdout.log</string>
  <key>StandardErrorPath</key>
    <string>/Users/wallacedobbs/thecalltaker/ops/reactivation-stderr.log</string>
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

BOOKING_URL    = "https://thecalltaker.com/book"
DEMO_LINE      = "(615) 784-5747"
WALLACE_PHONE  = "+16156539004"
WALLACE_EMAIL  = "thecalltakerai@gmail.com"
WALLACE_GHL_ID = "DtKLG28VzgUb6q3brILD"
FROM_EMAIL     = "thecalltakerai@gmail.com"

# ntfy topics
NTFY_URGENT   = "tct-urgent-Hk9UOEZR"
NTFY_SALES    = "tct-sales-63uYsIT9"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_SYSTEM   = "tct-system-vRsfXQRQ"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "ghl-reactivation-state.json")
LOG_FILE   = os.path.join(SCRIPT_DIR, "ghl-reactivation.log")

# Workflow tags
TRIGGER_TAG       = "hot-lead-reactivation"
SOURCE_TAG        = "hot-lead"
REPLIED_TAG       = "replied-reactivation"
EXHAUSTED_TAG     = "reactivation-exhausted"
DEMO_BOOKED_TAG   = "demo-booked"
PRICE_HESIT_TAG   = "price-hesitation"
ENROLLED_TAG      = "reactivation-enrolled"

# Rate limits per run
MAX_SMS_PER_RUN   = 15
MAX_EMAIL_PER_RUN = 10

# Message schedule — (message_num, delay_hours_from_enrollment, channel)
# Message 4 is NOT scheduled — it's reply-triggered via price-hesitation tag
MESSAGE_SCHEDULE = [
    (1, 0,    "sms"),     # Day 0 — immediate (email fallback if no phone)
    (2, 72,   "sms"),     # Day 3 — 72 hours
    (3, 120,  "sms"),     # Day 5 — 120 hours
    # Message 4 omitted — triggered by price-hesitation tag only
    (5, 240,  "sms"),     # Day 10 — 240 hours (breakup)
]

# GHL API headers
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-Reactivation/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-Reactivation/1.0",
}

# Tags that mean contact is already handled — don't enroll
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "donny-closing", "paid",
    EXHAUSTED_TAG, ENROLLED_TAG,
}

# Tags that signal positive outcome — pause sequence
POSITIVE_TAGS = {
    "contacted", "pilot-active", "pilot-signup", "hot-reply",
    DEMO_BOOKED_TAG, "interested", "pilot-converted", "customer",
}

# ─── Industry Personalization ────────────────────────────────────────────────
# tag -> (industry_label, missed_call_hook)
# Used to personalize Message 1: "are you still losing [INDUSTRY] calls..."

INDUSTRY_HOOKS = {
    "hvac": ("HVAC", "losing HVAC calls on nights and weekends"),
    "plumbing": ("plumbing", "missing plumbing emergency calls after hours"),
    "electrical": ("electrical", "losing electrical service calls after 5pm"),
    "roofing": ("roofing", "missing roofing estimate calls during storm season"),
    "locksmith": ("locksmith", "losing lockout calls at night"),
    "dental": ("dental", "missing new patient calls during lunch and after hours"),
    "medspa": ("med spa", "losing appointment calls from clients trying to book"),
    "legal": ("legal", "missing potential client calls after hours"),
    "veterinary": ("veterinary", "missing emergency pet calls at night"),
    "towing": ("towing", "losing tow calls to the next company in Google"),
    "garage-door": ("garage door", "missing garage door emergency calls"),
    "pest-control": ("pest control", "losing pest control calls to competitors"),
    "property-management": ("property management", "missing tenant emergency calls at night"),
    "water-damage": ("water damage", "losing water damage emergency calls after hours"),
    "cleaning": ("cleaning", "missing new client booking calls"),
    "landscaping": ("landscaping", "losing estimate calls during busy season"),
    "auto-repair": ("auto repair", "missing repair calls while your hands are under the hood"),
    "general-contractor": ("contracting", "losing estimate calls from homeowners"),
    "funeral": ("funeral services", "missing arrangement calls when families need you most"),
}

DEFAULT_HOOK = ("home services", "getting missed calls after hours")


def get_industry_hook(tags):
    """Return (industry_label, missed_call_hook) from contact tags."""
    if not tags:
        return DEFAULT_HOOK
    for tag in tags:
        key = tag.lower().strip()
        if key in INDUSTRY_HOOKS:
            return INDUSTRY_HOOKS[key]
    return DEFAULT_HOOK


# ─── Logging ─────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] reactivation: {msg}"
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
            "replies_detected": 0,
            "sequences_completed": 0,
            "demos_booked": 0,
            "price_hesitation_sent": 0,
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


def get_run_counts(state):
    """Return this run's send counts."""
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
    """Fetch a single GHL contact by ID."""
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


def add_note(contact_id, body):
    """Add an internal note to a GHL contact."""
    return ghl_request("POST", f"/contacts/{contact_id}/notes",
                        json_body={"body": body})


def add_task(contact_id, title, due_date, assigned_to=None):
    """Add a task to a GHL contact."""
    payload = {
        "title": title,
        "body": title,
        "dueDate": due_date,
        "completed": False,
    }
    if assigned_to:
        payload["assignedTo"] = assigned_to
    return ghl_request("POST", f"/contacts/{contact_id}/tasks", json_body=payload)


def send_sms(contact_id, phone, message):
    """Send an SMS via GHL conversations API."""
    conv_data = ghl_request("POST", "/conversations/", headers=CONVERSATIONS_HEADERS,
                            json_body={"locationId": GHL_LOCATION_ID, "contactId": contact_id})
    if not conv_data:
        log(f"Failed to create conversation for {contact_id}", "ERROR")
        return False

    conv_id = conv_data.get("conversation", {}).get("id") or conv_data.get("conversationId")
    if not conv_id:
        log(f"No conversation ID for {contact_id}: {str(conv_data)[:200]}", "ERROR")
        return False

    result = ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS,
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
    result = ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS,
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


def check_for_reply(contact_id):
    """Check if contact has sent an inbound message since enrollment."""
    data = ghl_request("GET", "/conversations/search", headers=CONVERSATIONS_HEADERS,
                       params={
                           "locationId": GHL_LOCATION_ID,
                           "contactId": contact_id,
                       })
    if not data:
        return False, None

    conversations = data.get("conversations", [])
    if not conversations:
        return False, None

    conv_id = conversations[0].get("id")
    if not conv_id:
        return False, None

    msgs = ghl_request("GET", f"/conversations/{conv_id}/messages",
                       headers=CONVERSATIONS_HEADERS)
    if not msgs:
        return False, None

    messages = msgs.get("messages", {})
    if isinstance(messages, dict):
        messages = messages.get("messages", [])

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        direction = msg.get("direction", "")
        if direction == "inbound":
            msg_body = msg.get("body") or msg.get("message") or ""
            return True, msg_body

    return False, None


# ─── ntfy ────────────────────────────────────────────────────────────────────

def ntfy(message, topic=NTFY_ACTIVITY, priority="default", title=None):
    """Send an ntfy notification."""
    headers = {"Priority": priority}
    if title:
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


# ─── Contact Registry ────────────────────────────────────────────────────────

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
            if gap < 72:
                return False, f"same touch type '{touch_type}' sent {gap:.0f}h ago"
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
        "engine": "ghl-reactivation",
        "type": touch_type,
        "time": datetime.now().isoformat(),
    })

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

def msg1_sms(first_name, industry_label, missed_call_hook):
    """Message 1 — Day 0: SMS missed calls question (industry-personalized)."""
    if industry_label != "home services":
        return (
            f"Hey {first_name}, quick question — are you still {missed_call_hook}?"
        )
    return (
        f"Hey {first_name}, quick question — are you still getting missed calls after hours?"
    )


def msg1_email_subject(first_name):
    """Message 1 — Email fallback subject."""
    return f"{first_name}, quick question about your missed calls"


def msg1_email_body(first_name, industry_label, missed_call_hook):
    """Message 1 — Email fallback body (used when no cell phone on file)."""
    question = (
        f"are you still {missed_call_hook}"
        if industry_label != "home services"
        else "are you still getting missed calls after hours"
    )
    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
    <p>Hey {first_name},</p>

    <p>Quick question — {question}?</p>

    <p>I built something that might help. Happy to show you in 10 minutes if you're open to it.</p>

    <p>Just reply to this email and I'll get you set up.</p>

    <p>— Wallace<br>
    The Call Taker<br>
    <a href="{BOOKING_URL}">Book a quick demo</a></p>
</div>"""


def msg2_sms(first_name):
    """Message 2 — Day 3: Follow-up, didn't want this buried."""
    return (
        f"Hey {first_name} — just wanted to make sure this didn't get buried. "
        f"Are missed calls still an issue for you?"
    )


def msg3_sms(first_name):
    """Message 3 — Day 5: Value pitch, AI receptionist Jessica."""
    return (
        f"Got it. I built something that might actually fix that — an AI receptionist "
        f"named Jessica that answers your phones 24/7, sounds completely human, and "
        f"books appointments automatically.\n\n"
        f"Takes 10 minutes to show you. I'll call your actual business number so you "
        f"can hear exactly what your customers would hear.\n\n"
        f"Want me to set that up this week? No cost, no commitment."
    )


def msg4_price_hesitation_sms(first_name):
    """Message 4 — REPLY-TRIGGERED ONLY: Founding 10 offer for price hesitation."""
    return (
        f"We're onboarding our first 10 founding customers right now — no setup fee "
        f"(normally $500), and it's $197/month for the first 3 months, then standard "
        f"pricing after that.\n\n"
        f"One booked job a month more than covers it. And if Jessica doesn't deliver "
        f"in the first 14 days, you pay nothing.\n\n"
        f"Want to be one of the 10?"
    )


def msg5_breakup_sms(first_name):
    """Message 5 — Day 10: Breakup, final CTA."""
    return (
        f"Hey {first_name} — I'll stop reaching out after this. If missed calls ever "
        f"become a problem worth solving, you can always reach me at {WALLACE_PHONE} "
        f"or book a quick demo at {BOOKING_URL}.\n\n"
        f"Wish you the best either way."
    )


# ─── Reply Handler ───────────────────────────────────────────────────────────

def handle_reply(contact_id, contact, reply_body, state):
    """
    Reply Handler Branch:
    1. Pause all scheduled messages (mark as replied in state)
    2. Add tag: replied-reactivation
    3. Send notification to Wallace (ntfy + SMS)
    4. Add task: "Follow up within 2 hours" assigned to Wallace
    5. Log and update state
    """
    first_name = contact.get("firstName", contact.get("first_name", "Lead"))
    company = contact.get("companyName", contact.get("company", ""))
    phone = contact.get("phone", "")

    log(f"REPLY detected from {first_name} ({contact_id}): {reply_body[:100]}")

    # 1. Mark as replied in state (pauses all future messages)
    enrolled = state.get("enrolled", {})
    if contact_id in enrolled:
        enrolled[contact_id]["replied"] = True
        enrolled[contact_id]["replied_at"] = datetime.now().isoformat()
        enrolled[contact_id]["reply_body"] = reply_body[:500]

    # 2. Add tag
    add_tag(contact_id, REPLIED_TAG)
    # Remove the trigger tag since sequence is paused
    remove_tag(contact_id, TRIGGER_TAG)

    # 3. Send notification to Wallace
    company_str = f" ({company})" if company else ""
    alert_msg = (
        f"🔥 {first_name}{company_str} replied to reactivation sequence!\n\n"
        f"Message: {reply_body[:300]}\n\n"
        f"Phone: {phone}\n"
        f"Contact: https://app.gohighlevel.com/contacts/{contact_id}"
    )
    ntfy(alert_msg, NTFY_URGENT, priority="urgent",
         title=f"[CRITICAL] Reactivation Reply — {first_name}")

    # SMS alert to Wallace
    wallace_sms = (
        f"REACTIVATION REPLY: {first_name}{company_str} replied: "
        f"\"{reply_body[:150]}\"\n\n"
        f"Call them NOW: {phone}"
    )
    send_sms(WALLACE_GHL_ID, WALLACE_PHONE, wallace_sms)

    # 4. Add task — follow up within 2 hours
    due = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    add_task(contact_id,
             f"Follow up with {first_name} within 2 hours — reactivation reply",
             due)

    # 5. Add internal note
    add_note(contact_id,
             f"Reactivation reply detected at {datetime.now().strftime('%Y-%m-%d %H:%M')}: "
             f"\"{reply_body[:300]}\"")

    state["stats"]["replies_detected"] = state["stats"].get("replies_detected", 0) + 1
    save_state(state)

    log(f"Reply handler complete for {first_name} ({contact_id})")


# ─── Sequence Exhaustion Handler ─────────────────────────────────────────────

def handle_exhaustion(contact_id, contact, state):
    """After Message 5 with no reply — tag and close out."""
    first_name = contact.get("firstName", contact.get("first_name", "Lead"))

    log(f"Sequence exhausted for {first_name} ({contact_id}) — no reply after 5 messages")

    # Add exhaustion tag
    add_tag(contact_id, EXHAUSTED_TAG)

    # Remove trigger tag
    remove_tag(contact_id, TRIGGER_TAG)

    # Add internal note
    add_note(contact_id,
             f"Completed full reactivation sequence with no response — "
             f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Update state
    enrolled = state.get("enrolled", {})
    if contact_id in enrolled:
        enrolled[contact_id]["exhausted"] = True
        enrolled[contact_id]["exhausted_at"] = datetime.now().isoformat()

    state["stats"]["sequences_completed"] = state["stats"].get("sequences_completed", 0) + 1
    save_state(state)


# ─── Core Commands ───────────────────────────────────────────────────────────

def cmd_scan(state):
    """Find contacts tagged 'hot-lead-reactivation' not yet enrolled."""
    log("Scanning for new contacts to enroll...")

    contacts = search_contacts_by_tag(TRIGGER_TAG)
    enrolled = state.get("enrolled", {})
    new_count = 0

    for c in contacts:
        cid = c.get("id")
        if not cid or cid in enrolled:
            continue

        tags = c.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        # Skip excluded contacts
        if any(t in EXCLUDE_TAGS for t in tags):
            log(f"Skipping {c.get('firstName', '?')} ({cid}) — excluded tag")
            continue

        # Skip contacts that already replied or are demo-booked
        if any(t in POSITIVE_TAGS for t in tags):
            log(f"Skipping {c.get('firstName', '?')} ({cid}) — positive tag already present")
            continue

        first_name = c.get("firstName") or c.get("first_name") or "there"
        phone = c.get("phone", "")
        email = c.get("email", "")
        company = c.get("companyName") or c.get("company") or ""
        industry_label, missed_call_hook = get_industry_hook(tags)

        enrolled[cid] = {
            "first_name": first_name,
            "phone": phone,
            "email": email,
            "company": company,
            "tags": tags,
            "industry_label": industry_label,
            "missed_call_hook": missed_call_hook,
            "enrolled_at": datetime.now().isoformat(),
            "last_message": 0,
            "replied": False,
            "exhausted": False,
        }

        # Add enrolled tag
        add_tag(cid, ENROLLED_TAG)

        new_count += 1
        log(f"Enrolled: {first_name} ({cid}) — {industry_label}")

    state["enrolled"] = enrolled
    state["stats"]["total_enrolled"] = len(enrolled)
    save_state(state)

    log(f"Scan complete: {new_count} new contacts enrolled, {len(enrolled)} total")
    return new_count


def cmd_send(state):
    """Execute due messages for enrolled contacts."""
    log("Sending due messages...")

    enrolled = state.get("enrolled", {})
    counts = get_run_counts(state)
    sms_sent = 0
    email_sent = 0
    now = datetime.now()

    for cid, data in list(enrolled.items()):
        # Skip if already replied or exhausted
        if data.get("replied") or data.get("exhausted"):
            continue

        # Check for fresh reply from GHL
        contact = get_contact(cid)
        if not contact:
            log(f"Contact {cid} not found in GHL — skipping", "WARN")
            continue

        # Check if contact gained a positive tag since last check
        current_tags = contact.get("tags", [])
        if isinstance(current_tags, list):
            if any(t in POSITIVE_TAGS for t in current_tags):
                log(f"{data['first_name']} ({cid}) has positive tag — pausing sequence")
                data["replied"] = True
                data["replied_at"] = now.isoformat()
                save_state(state)
                continue

        # Check for inbound reply
        has_reply, reply_body = check_for_reply(cid)
        if has_reply and not data.get("replied"):
            handle_reply(cid, contact, reply_body or "", state)
            continue

        # ─── Check for price-hesitation tag (triggers Message 4) ───
        if isinstance(current_tags, list) and PRICE_HESIT_TAG in current_tags:
            if not data.get("msg4_sent"):
                if sms_sent >= MAX_SMS_PER_RUN:
                    log(f"SMS limit reached — deferring msg4 for {data['first_name']}")
                    continue
                phone = data.get("phone", "")
                if phone:
                    ok, reason = check_registry(cid, "sms")
                    if ok:
                        msg = msg4_price_hesitation_sms(data["first_name"])
                        if send_sms(cid, phone, msg):
                            data["msg4_sent"] = True
                            data["msg4_sent_at"] = now.isoformat()
                            update_registry(cid, "sms")
                            sms_sent += 1
                            counts["sms"] = counts.get("sms", 0) + 1
                            state["stats"]["price_hesitation_sent"] = \
                                state["stats"].get("price_hesitation_sent", 0) + 1
                            log(f"Message 4 (price hesitation) sent to {data['first_name']} ({cid})")
                            # Remove the price-hesitation tag so it doesn't fire again
                            remove_tag(cid, PRICE_HESIT_TAG)
                    else:
                        log(f"Registry blocked msg4 for {data['first_name']}: {reason}")
                save_state(state)
                continue

        # ─── Normal message schedule ───
        enrolled_at = datetime.fromisoformat(data["enrolled_at"])
        hours_since = (now - enrolled_at).total_seconds() / 3600
        last_msg = data.get("last_message", 0)

        for msg_num, delay_hours, channel in MESSAGE_SCHEDULE:
            if msg_num <= last_msg:
                continue
            if hours_since < delay_hours:
                break  # Not due yet

            # Rate limiting
            if channel == "sms" and sms_sent >= MAX_SMS_PER_RUN:
                log(f"SMS limit reached — deferring msg{msg_num} for {data['first_name']}")
                break
            if channel == "email" and email_sent >= MAX_EMAIL_PER_RUN:
                log(f"Email limit reached — deferring msg{msg_num} for {data['first_name']}")
                break

            phone = data.get("phone", "")
            email_addr = data.get("email", "")
            first_name = data["first_name"]
            industry_label = data.get("industry_label", "home services")
            missed_call_hook = data.get("missed_call_hook", "getting missed calls after hours")

            sent = False

            if msg_num == 1:
                # SMS primary, email fallback
                if phone:
                    ok, reason = check_registry(cid, "sms")
                    if ok:
                        msg = msg1_sms(first_name, industry_label, missed_call_hook)
                        sent = send_sms(cid, phone, msg)
                        if sent:
                            update_registry(cid, "sms")
                            sms_sent += 1
                            counts["sms"] = counts.get("sms", 0) + 1
                            state["stats"]["sms_sent"] += 1
                    else:
                        log(f"Registry blocked msg1 SMS for {first_name}: {reason}")
                elif email_addr:
                    ok, reason = check_registry(cid, "email")
                    if ok:
                        subj = msg1_email_subject(first_name)
                        body = msg1_email_body(first_name, industry_label, missed_call_hook)
                        sent = send_email(cid, email_addr, subj, body)
                        if sent:
                            update_registry(cid, "email")
                            email_sent += 1
                            counts["email"] = counts.get("email", 0) + 1
                            state["stats"]["emails_sent"] += 1
                    else:
                        log(f"Registry blocked msg1 email for {first_name}: {reason}")
                else:
                    log(f"No phone or email for {first_name} ({cid}) — skipping msg1", "WARN")
                    sent = True  # Mark as sent to avoid retrying

            elif msg_num == 2:
                if phone:
                    ok, reason = check_registry(cid, "sms")
                    if ok:
                        msg = msg2_sms(first_name)
                        sent = send_sms(cid, phone, msg)
                        if sent:
                            update_registry(cid, "sms")
                            sms_sent += 1
                            counts["sms"] = counts.get("sms", 0) + 1
                            state["stats"]["sms_sent"] += 1
                    else:
                        log(f"Registry blocked msg2 for {first_name}: {reason}")

            elif msg_num == 3:
                if phone:
                    ok, reason = check_registry(cid, "sms")
                    if ok:
                        msg = msg3_sms(first_name)
                        sent = send_sms(cid, phone, msg)
                        if sent:
                            update_registry(cid, "sms")
                            sms_sent += 1
                            counts["sms"] = counts.get("sms", 0) + 1
                            state["stats"]["sms_sent"] += 1
                    else:
                        log(f"Registry blocked msg3 for {first_name}: {reason}")

            elif msg_num == 5:
                if phone:
                    ok, reason = check_registry(cid, "sms")
                    if ok:
                        msg = msg5_breakup_sms(first_name)
                        sent = send_sms(cid, phone, msg)
                        if sent:
                            update_registry(cid, "sms")
                            sms_sent += 1
                            counts["sms"] = counts.get("sms", 0) + 1
                            state["stats"]["sms_sent"] += 1
                    else:
                        log(f"Registry blocked msg5 for {first_name}: {reason}")

            if sent:
                data["last_message"] = msg_num
                data[f"msg{msg_num}_sent_at"] = now.isoformat()
                log(f"Message {msg_num} sent to {first_name} ({cid})")

                # After Message 5 — handle exhaustion
                if msg_num == 5:
                    handle_exhaustion(cid, contact, state)

                save_state(state)
                time.sleep(1.5)  # Pace between sends
                break  # Only send one message per contact per run

    save_state(state)
    log(f"Send complete: {sms_sent} SMS, {email_sent} emails sent this run")
    return sms_sent + email_sent


def cmd_enroll(state):
    """Tag all 'hot-lead' contacts with 'hot-lead-reactivation' to trigger the workflow."""
    log("Enrolling all hot-lead contacts into reactivation workflow...")

    contacts = search_contacts_by_tag(SOURCE_TAG)
    enrolled_count = 0
    skipped = 0

    for c in contacts:
        cid = c.get("id")
        if not cid:
            continue

        tags = c.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        # Skip if already has trigger tag or exhaustion tag
        if TRIGGER_TAG in tags or EXHAUSTED_TAG in tags or ENROLLED_TAG in tags:
            skipped += 1
            continue

        # Skip excluded
        if any(t in EXCLUDE_TAGS for t in tags):
            skipped += 1
            continue

        # Add the trigger tag
        result = add_tag(cid, TRIGGER_TAG)
        if result is not None:
            first_name = c.get("firstName") or c.get("first_name") or "?"
            log(f"Tagged {first_name} ({cid}) with {TRIGGER_TAG}")
            enrolled_count += 1
            time.sleep(0.5)  # Pace API calls

    log(f"Enrollment complete: {enrolled_count} contacts tagged, {skipped} skipped")
    ntfy(f"Reactivation workflow: {enrolled_count} hot leads enrolled for Founding 10 sequence",
         NTFY_SALES, priority="high",
         title="Reactivation — Founding 10 Enrollment")
    return enrolled_count


def cmd_status(state):
    """Show enrollment stats and message counts."""
    enrolled = state.get("enrolled", {})
    stats = state.get("stats", {})

    total = len(enrolled)
    replied = sum(1 for d in enrolled.values() if d.get("replied"))
    exhausted = sum(1 for d in enrolled.values() if d.get("exhausted"))
    active = total - replied - exhausted

    # Count by last message sent
    msg_counts = {}
    for d in enrolled.values():
        last = d.get("last_message", 0)
        msg_counts[last] = msg_counts.get(last, 0) + 1

    print("\n" + "=" * 60)
    print("  HOT LEAD REACTIVATION — FOUNDING 10")
    print("=" * 60)
    print(f"  Total Enrolled:        {total}")
    print(f"  Active (in sequence):  {active}")
    print(f"  Replied:               {replied}")
    print(f"  Exhausted (no reply):  {exhausted}")
    print("-" * 60)
    print(f"  SMS Sent:              {stats.get('sms_sent', 0)}")
    print(f"  Emails Sent:           {stats.get('emails_sent', 0)}")
    print(f"  Replies Detected:      {stats.get('replies_detected', 0)}")
    print(f"  Price Hesitation Sent: {stats.get('price_hesitation_sent', 0)}")
    print(f"  Demos Booked:          {stats.get('demos_booked', 0)}")
    print("-" * 60)
    print("  Progress by Message:")
    for msg_num in range(0, 6):
        count = msg_counts.get(msg_num, 0)
        label = {0: "Not started", 1: "Msg 1 sent", 2: "Msg 2 sent",
                 3: "Msg 3 sent", 4: "Msg 4 (price)", 5: "Msg 5 (breakup)"}
        print(f"    {label.get(msg_num, f'Msg {msg_num}'):20s} {count}")
    print("=" * 60)

    # Show replied contacts
    if replied:
        print("\n  REPLIES:")
        for cid, d in enrolled.items():
            if d.get("replied"):
                name = d.get("first_name", "?")
                reply = d.get("reply_body", "")[:80]
                print(f"    {name}: \"{reply}\"")

    print()


def cmd_preview(state):
    """Preview all messages for a sample contact."""
    print("\n" + "=" * 60)
    print("  MESSAGE PREVIEW — Reactivation Sequence")
    print("=" * 60)

    name = "Mike"

    print(f"\n--- Message 1 (Day 0) — SMS ---")
    print(f"[Generic] {msg1_sms(name, 'home services', 'getting missed calls after hours')}")
    print(f"\n[HVAC]    {msg1_sms(name, 'HVAC', 'losing HVAC calls on nights and weekends')}")
    print(f"\n[Plumbing]{msg1_sms(name, 'plumbing', 'missing plumbing emergency calls after hours')}")
    print(f"\n[Dental]  {msg1_sms(name, 'dental', 'missing new patient calls during lunch and after hours')}")
    print(f"\n[Roofing] {msg1_sms(name, 'roofing', 'missing roofing estimate calls during storm season')}")

    print(f"\n--- Message 1 (Day 0) — Email fallback ---")
    print(f"Subject: {msg1_email_subject(name)}")
    print(f"(HTML body with booking link)")

    print(f"\n--- Message 2 (Day 3) — SMS ---")
    print(msg2_sms(name))

    print(f"\n--- Message 3 (Day 5) — SMS ---")
    print(msg3_sms(name))

    print(f"\n--- Message 4 (REPLY-TRIGGERED — price hesitation) ---")
    print(msg4_price_hesitation_sms(name))

    print(f"\n--- Message 5 (Day 10) — SMS breakup ---")
    print(msg5_breakup_sms(name))

    print("\n" + "=" * 60)
    print("  Post-msg5 actions: +reactivation-exhausted, -hot-lead-reactivation, +internal note")
    print("  Reply handler: pause → +replied-reactivation → ntfy URGENT → SMS to Wallace → 2hr task")
    print("=" * 60 + "\n")


def cmd_run(state):
    """Full cycle: scan + send."""
    cmd_scan(state)
    state = load_state()  # Reload after scan
    cmd_send(state)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: ghl-reactivation-workflow.py <scan|send|enroll|status|run|preview>")
        sys.exit(1)

    command = sys.argv[1].lower()
    state = load_state()

    try:
        if command == "scan":
            cmd_scan(state)
        elif command == "send":
            cmd_send(state)
        elif command == "enroll":
            cmd_enroll(state)
        elif command == "status":
            cmd_status(state)
        elif command == "run":
            cmd_run(state)
        elif command == "preview":
            cmd_preview(state)
        else:
            print(f"Unknown command: {command}")
            print("Commands: scan, send, enroll, status, run, preview")
            sys.exit(1)
    except Exception as e:
        log(f"CRASH: {e}\n{traceback.format_exc()}", "ERROR")
        ntfy(f"Reactivation workflow crashed: {e}",
             NTFY_SYSTEM, priority="high",
             title="[CRITICAL] Reactivation Workflow Crash")
        sys.exit(1)


if __name__ == "__main__":
    main()
