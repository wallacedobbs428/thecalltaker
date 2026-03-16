#!/usr/bin/env python3
"""
FACEBOOK LEAD ADS FOLLOW-UP ENGINE — The Call Taker
=====================================================
Automated follow-up sequence for Facebook Lead Ad submissions.

Trigger: Contact tagged "facebook-lead" in GHL (via native integration or webhook)

Flow:
  1. IMMEDIATE: SMS → "Thanks for requesting The Call Taker..."
  2. +2 HOURS (no reply): Variant-specific follow-up email
  3. +24 HOURS (no reply): Tag "fb-lead-no-response", create task for Wallace
  4. REPLY "YES": Tag "fb-lead-interested", ntfy URGENT, create 1hr task

Tags applied by this engine:
  - fb-lead-enrolled     — enrolled in this follow-up sequence
  - fb-missed-revenue    — came from Missed Revenue ad variant
  - fb-after-hours       — came from After-Hours Lifeline ad variant
  - fb-hiring-headache   — came from Hiring Headache Relief ad variant
  - fb-lead-sms-sent     — initial SMS sent
  - fb-lead-email-sent   — 2hr follow-up email sent
  - fb-lead-no-response  — no reply after 24 hours
  - fb-lead-interested   — replied YES
  - fb-lead-replied      — replied with anything

Commands:
  scan      — Find new facebook-lead contacts not yet enrolled
  followup  — Send due follow-ups (2hr email, 24hr escalation)
  status    — Show stats
  run       — scan + followup (full cycle)
  preview   — Preview all message copy
  test      — Dry run scan (no sends)

Schedule:
  scan every 15 minutes (catch new leads fast)
  followup every 30 minutes (check reply status + send due emails)

launchd plists (install to ~/Library/LaunchAgents/):

--- com.thecalltaker.fb-leads.scan.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.thecalltaker.fb-leads.scan</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string>
    <string>/Users/wallacedobbs/thecalltaker/ops/fb-lead-ads-engine.py</string>
    <string>scan</string>
  </array>
  <key>StartInterval</key><integer>900</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key>
    <string>/Users/wallacedobbs/thecalltaker-ops/logs/fb-leads-stdout.log</string>
  <key>StandardErrorPath</key>
    <string>/Users/wallacedobbs/thecalltaker-ops/logs/fb-leads-stderr.log</string>
</dict></plist>

--- com.thecalltaker.fb-leads.followup.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.thecalltaker.fb-leads.followup</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string>
    <string>/Users/wallacedobbs/thecalltaker-ops/ops/fb-lead-ads-engine.py</string>
    <string>followup</string>
  </array>
  <key>StartInterval</key><integer>1800</integer>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key>
    <string>/Users/wallacedobbs/thecalltaker-ops/logs/fb-leads-stdout.log</string>
  <key>StandardErrorPath</key>
    <string>/Users/wallacedobbs/thecalltaker-ops/logs/fb-leads-stderr.log</string>
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
WALLACE_GHL_ID = "DtKLG28VzgUb6q3brILD"
FROM_EMAIL     = "thecalltakerai@gmail.com"

# ntfy topics — same channels as reactivation workflow
NTFY_URGENT   = "tct-urgent-Hk9UOEZR"
NTFY_SALES    = "tct-sales-63uYsIT9"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_SYSTEM   = "tct-system-vRsfXQRQ"

# State and log paths — write to thecalltaker-ops
OPS_DIR    = os.path.expanduser("~/thecalltaker-ops")
STATE_FILE = os.path.join(OPS_DIR, "fb-lead-ads-state.json")
LOG_FILE   = os.path.join(OPS_DIR, "logs", "fb-lead-ads-engine.log")

# Tags
SOURCE_TAG       = "facebook-lead"
ENROLLED_TAG     = "fb-lead-enrolled"
SMS_SENT_TAG     = "fb-lead-sms-sent"
EMAIL_SENT_TAG   = "fb-lead-email-sent"
NO_RESPONSE_TAG  = "fb-lead-no-response"
INTERESTED_TAG   = "fb-lead-interested"
REPLIED_TAG      = "fb-lead-replied"

# Ad variant tags (applied based on form data or ad UTM)
VARIANT_TAGS = {
    "missed-revenue":    "fb-missed-revenue",
    "after-hours":       "fb-after-hours",
    "hiring-headache":   "fb-hiring-headache",
}

# Vertical tags
VERTICAL_TAGS = {
    "hvac":     "hvac",
    "plumbing": "plumbing",
    "dental":   "dental",
}

# Timing
FOLLOWUP_EMAIL_DELAY_HOURS = 2
ESCALATION_DELAY_HOURS     = 24

# Rate limits
MAX_SMS_PER_RUN   = 20
MAX_EMAIL_PER_RUN = 15

# GHL API headers
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-FBLeadAds/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-FBLeadAds/1.0",
}

# Tags that mean contact is already handled — don't enroll
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", ENROLLED_TAG,
}


# ─── Logging ─────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] fb-lead-ads: {msg}"
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
        "stats": {
            "total_enrolled": 0,
            "sms_sent": 0,
            "emails_sent": 0,
            "replies_detected": 0,
            "interested": 0,
            "no_response": 0,
            "by_variant": {"missed-revenue": 0, "after-hours": 0, "hiring-headache": 0},
            "by_vertical": {"hvac": 0, "plumbing": 0, "dental": 0},
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


# ─── GHL API Helpers ─────────────────────────────────────────────────────────

def ghl_request(method, path, headers=None, params=None, json_body=None, retries=3):
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
    data = ghl_request("GET", f"/contacts/{contact_id}")
    return data.get("contact") if data else None


def add_tag(contact_id, tags):
    if isinstance(tags, str):
        tags = [tags]
    return ghl_request("POST", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def add_note(contact_id, body):
    return ghl_request("POST", f"/contacts/{contact_id}/notes", json_body={"body": body})


def add_task(contact_id, title, due_date):
    return ghl_request("POST", f"/contacts/{contact_id}/tasks", json_body={
        "title": title,
        "body": title,
        "dueDate": due_date,
        "completed": False,
    })


def send_sms(contact_id, phone, message):
    conv_data = ghl_request("POST", "/conversations/", headers=CONVERSATIONS_HEADERS,
                            json_body={"locationId": GHL_LOCATION_ID, "contactId": contact_id})
    if not conv_data:
        log(f"Failed to create conversation for {contact_id}", "ERROR")
        return False

    conv_id = conv_data.get("conversation", {}).get("id") or conv_data.get("conversationId")
    if not conv_id:
        log(f"No conversation ID for {contact_id}", "ERROR")
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
    log(f"Email sent to {contact_id} ({email})")
    return True


def check_for_inbound_reply(contact_id):
    """Check if contact has sent an inbound message."""
    data = ghl_request("GET", "/conversations/search", headers=CONVERSATIONS_HEADERS,
                       params={"locationId": GHL_LOCATION_ID, "contactId": contact_id})
    if not data:
        return False, None

    conversations = data.get("conversations", [])
    if not conversations:
        return False, None

    conv_id = conversations[0].get("id")
    if not conv_id:
        return False, None

    msgs = ghl_request("GET", f"/conversations/{conv_id}/messages", headers=CONVERSATIONS_HEADERS)
    if not msgs:
        return False, None

    messages = msgs.get("messages", {})
    if isinstance(messages, dict):
        messages = messages.get("messages", [])

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        if msg.get("direction") == "inbound":
            msg_body = msg.get("body") or msg.get("message") or ""
            return True, msg_body

    return False, None


# ─── ntfy ────────────────────────────────────────────────────────────────────

def ntfy(message, topic=NTFY_ACTIVITY, priority="default", title=None):
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


# ─── Variant Detection ──────────────────────────────────────────────────────

def detect_variant(contact):
    """Detect ad variant from contact tags or notes."""
    tags = contact.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    # Check if variant tag already present
    for variant_key, variant_tag in VARIANT_TAGS.items():
        if variant_tag in tags:
            return variant_key

    # Check UTM content in notes or source
    source = (contact.get("source") or "").lower()
    notes = ""
    # Try to read from attribution notes custom field
    custom_fields = contact.get("customFields", contact.get("customField", []))
    if isinstance(custom_fields, list):
        for cf in custom_fields:
            if isinstance(cf, dict):
                val = str(cf.get("value", "")).lower()
                if "missed-revenue" in val:
                    return "missed-revenue"
                if "after-hours" in val:
                    return "after-hours"
                if "hiring-headache" in val:
                    return "hiring-headache"

    # Check source field
    if "missed-revenue" in source:
        return "missed-revenue"
    if "after-hours" in source:
        return "after-hours"
    if "hiring-headache" in source or "hiring" in source:
        return "hiring-headache"

    return "missed-revenue"  # Default to most common variant


def detect_vertical(contact):
    """Detect vertical from contact tags."""
    tags = contact.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    for v in VERTICAL_TAGS:
        if v in tags:
            return v
    return "hvac"  # Default


# ─── Message Templates ──────────────────────────────────────────────────────

def initial_sms():
    """Universal initial SMS — same for all variants."""
    return (
        "Thanks for requesting The Call Taker. For 14 days, we'll show you how "
        "many jobs you can save when every call gets answered. Reply YES and "
        "we'll send setup details."
    )


def followup_email_missed_revenue(first_name, company):
    """2hr follow-up email for Missed Revenue variant."""
    subject = f"{first_name}, how many calls did {company or 'your business'} miss this week?"
    body = f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
    <p>Hey {first_name},</p>

    <p>Most service businesses miss 5-10 calls a week. At $300-$800 per job, that's
    <strong>$2,000-$10,000/month in lost revenue</strong> — just from unanswered phones.</p>

    <p>The Call Taker answers every call in 2 rings, 24/7. Sounds like a real person.
    Books appointments. Texts you the details.</p>

    <p>Your 14-day free trial is ready. No setup fee. No contracts. Cancel anytime.</p>

    <p><strong>Two ways to get started:</strong></p>
    <ol>
        <li>Reply YES to this email</li>
        <li><a href="{BOOKING_URL}">Book a 10-minute setup call</a></li>
    </ol>

    <p>Or call our demo line right now to hear Jessica in action: <strong>{DEMO_LINE}</strong></p>

    <p>— Wallace<br>The Call Taker</p>
</div>"""
    return subject, body


def followup_email_after_hours(first_name, company):
    """2hr follow-up email for After-Hours variant."""
    subject = f"{first_name}, who answered your phones last night?"
    body = f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
    <p>Hey {first_name},</p>

    <p>68% of service calls happen outside business hours. Evenings. Weekends. Holidays.
    If nobody's answering during those times, those customers are calling your competitor.</p>

    <p>The Call Taker gives {company or 'your business'} a professional receptionist that works 24/7.
    Answers in your business name. Books appointments. Handles FAQs. Texts you when it's urgent.</p>

    <p>Your customers think they're talking to your staff. You just see booked appointments
    in the morning.</p>

    <p><strong>Your free 14-day trial is ready:</strong></p>
    <ul>
        <li>Reply YES to this email</li>
        <li><a href="{BOOKING_URL}">Book a 10-minute setup call</a></li>
        <li>Call our demo line to hear it live: <strong>{DEMO_LINE}</strong></li>
    </ul>

    <p>No setup fee. No contracts. $97/month after trial — less than one missed job.</p>

    <p>— Wallace<br>The Call Taker</p>
</div>"""
    return subject, body


def followup_email_hiring_headache(first_name, company):
    """2hr follow-up email for Hiring Headache variant."""
    subject = f"{first_name}, what if you never had to hire another receptionist?"
    body = f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
    <p>Hey {first_name},</p>

    <p>Hiring a receptionist: $2,500/month + benefits + training + sick days + turnover.
    And they still can't answer calls at 2 AM.</p>

    <p>The Call Taker: $97/month. Answers every call, 24/7. Never takes a day off.
    Never puts anyone on hold. Books appointments automatically.</p>

    <p>Your customers at {company or 'your business'} can't tell the difference.
    Your bank account definitely can.</p>

    <p><strong>Your free 14-day trial is ready:</strong></p>
    <ul>
        <li>Reply YES to this email</li>
        <li><a href="{BOOKING_URL}">Book a 10-minute setup call</a></li>
        <li>Call our demo line: <strong>{DEMO_LINE}</strong></li>
    </ul>

    <p>14 days free. No setup fee. No contracts.</p>

    <p>— Wallace<br>The Call Taker</p>
</div>"""
    return subject, body


VARIANT_EMAIL_MAP = {
    "missed-revenue":  followup_email_missed_revenue,
    "after-hours":     followup_email_after_hours,
    "hiring-headache": followup_email_hiring_headache,
}


# ─── Reply Handler ───────────────────────────────────────────────────────────

def handle_reply(contact_id, contact, reply_body, state):
    """Handle any inbound reply from a Facebook lead."""
    first_name = contact.get("firstName") or contact.get("first_name") or "Lead"
    company = contact.get("companyName") or contact.get("company") or ""
    phone = contact.get("phone", "")

    log(f"REPLY from FB lead {first_name} ({contact_id}): {reply_body[:100]}")

    # Tag as replied
    add_tag(contact_id, REPLIED_TAG)

    # Check if they said YES
    reply_lower = (reply_body or "").strip().lower()
    is_yes = reply_lower in ("yes", "y", "yeah", "yep", "sure", "ok", "okay",
                              "yes please", "yes!", "let's do it", "sign me up",
                              "interested", "set it up", "ready")

    enrolled = state.get("enrolled", {})
    if contact_id in enrolled:
        enrolled[contact_id]["replied"] = True
        enrolled[contact_id]["replied_at"] = datetime.now().isoformat()
        enrolled[contact_id]["reply_body"] = reply_body[:500]
        enrolled[contact_id]["is_yes"] = is_yes

    if is_yes:
        # YES reply — hot lead!
        add_tag(contact_id, INTERESTED_TAG)

        # ntfy URGENT
        company_str = f" ({company})" if company else ""
        alert = (
            f"FB Lead {first_name}{company_str} replied YES to free trial!\n\n"
            f"Phone: {phone}\n"
            f"Reply: \"{reply_body[:200]}\"\n"
            f"Action: Follow up within 1 hour"
        )
        ntfy(alert, NTFY_URGENT, priority="urgent",
             title=f"[CRITICAL] FB Lead YES — {first_name}")

        # SMS alert to Wallace
        send_sms(WALLACE_GHL_ID, WALLACE_PHONE,
                 f"FB LEAD YES: {first_name}{company_str} replied YES!\n"
                 f"Call them NOW: {phone}")

        # Create 1-hour task
        due = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        add_task(contact_id,
                 f"Follow up with {first_name} within 1 hour — FB lead replied YES",
                 due)

        # Note
        add_note(contact_id,
                 f"FB Lead Ads: Replied YES at {datetime.now().strftime('%Y-%m-%d %H:%M')}. "
                 f"Message: \"{reply_body[:200]}\"")

        state["stats"]["interested"] = state["stats"].get("interested", 0) + 1

    else:
        # Non-YES reply — still important, alert Wallace
        company_str = f" ({company})" if company else ""
        alert = (
            f"FB Lead {first_name}{company_str} replied (not YES):\n"
            f"\"{reply_body[:200]}\"\n\n"
            f"Phone: {phone}\n"
            f"Action: Review and respond manually"
        )
        ntfy(alert, NTFY_URGENT, priority="high",
             title=f"[HIGH] FB Lead Reply — {first_name}")

        due = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        add_task(contact_id,
                 f"FB lead {first_name} replied — review and respond: \"{reply_body[:80]}\"",
                 due)

    state["stats"]["replies_detected"] = state["stats"].get("replies_detected", 0) + 1
    save_state(state)


# ─── Core Commands ───────────────────────────────────────────────────────────

def cmd_scan(state):
    """Find new facebook-lead contacts and send immediate SMS."""
    log("Scanning for new Facebook leads...")

    contacts = search_contacts_by_tag(SOURCE_TAG)
    enrolled = state.get("enrolled", {})
    new_count = 0
    sms_count = 0

    for c in contacts:
        cid = c.get("id")
        if not cid or cid in enrolled:
            continue

        tags = c.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        # Skip excluded
        if any(t in EXCLUDE_TAGS for t in tags):
            continue

        # Only process contacts that are actually from Facebook
        if SOURCE_TAG not in tags:
            continue

        first_name = c.get("firstName") or c.get("first_name") or "there"
        phone = c.get("phone", "")
        email = c.get("email", "")
        company = c.get("companyName") or c.get("company") or ""

        # Detect variant and vertical
        variant = detect_variant(c)
        vertical = detect_vertical(c)

        # Enroll
        enrolled[cid] = {
            "first_name": first_name,
            "phone": phone,
            "email": email,
            "company": company,
            "variant": variant,
            "vertical": vertical,
            "enrolled_at": datetime.now().isoformat(),
            "sms_sent": False,
            "email_sent": False,
            "escalated": False,
            "replied": False,
        }

        # Apply tags: variant + vertical + enrolled
        tags_to_add = [ENROLLED_TAG]
        if variant in VARIANT_TAGS:
            tags_to_add.append(VARIANT_TAGS[variant])
        if vertical in VERTICAL_TAGS:
            vt = VERTICAL_TAGS[vertical]
            if vt not in tags:
                tags_to_add.append(vt)
        add_tag(cid, tags_to_add)

        # IMMEDIATE: Send initial SMS
        if phone and sms_count < MAX_SMS_PER_RUN:
            msg = initial_sms()
            if send_sms(cid, phone, msg):
                enrolled[cid]["sms_sent"] = True
                enrolled[cid]["sms_sent_at"] = datetime.now().isoformat()
                add_tag(cid, SMS_SENT_TAG)
                sms_count += 1
                state["stats"]["sms_sent"] = state["stats"].get("sms_sent", 0) + 1

        # Update variant/vertical stats
        state["stats"]["by_variant"][variant] = \
            state["stats"]["by_variant"].get(variant, 0) + 1
        state["stats"]["by_vertical"][vertical] = \
            state["stats"]["by_vertical"].get(vertical, 0) + 1

        new_count += 1
        log(f"Enrolled FB lead: {first_name} ({cid}) — {variant}/{vertical}")

        # Notify on ACTIVITY channel
        ntfy(f"New FB lead enrolled: {first_name} ({company}) — {variant}/{vertical}",
             NTFY_ACTIVITY, title="FB Lead Enrolled")

        time.sleep(1)  # Pace API calls

    state["enrolled"] = enrolled
    state["stats"]["total_enrolled"] = len(enrolled)
    save_state(state)

    log(f"Scan complete: {new_count} new leads, {sms_count} SMS sent")
    return new_count


def cmd_followup(state):
    """Send due follow-ups: 2hr email, 24hr escalation, reply detection."""
    log("Running follow-up checks...")

    enrolled = state.get("enrolled", {})
    now = datetime.now()
    email_count = 0

    for cid, data in list(enrolled.items()):
        if data.get("replied") or data.get("escalated"):
            continue

        # Check for reply
        contact = get_contact(cid)
        if not contact:
            continue

        # Check current tags for positive signals
        current_tags = contact.get("tags", [])
        if isinstance(current_tags, list):
            positive = {"contacted", "pilot-active", "pilot-signup", "demo-booked",
                        "interested", "pilot-converted", "customer", INTERESTED_TAG}
            if any(t in positive for t in current_tags):
                data["replied"] = True
                save_state(state)
                continue

        # Check for inbound reply
        has_reply, reply_body = check_for_inbound_reply(cid)
        if has_reply and not data.get("replied"):
            handle_reply(cid, contact, reply_body or "", state)
            continue

        enrolled_at = datetime.fromisoformat(data["enrolled_at"])
        hours_since = (now - enrolled_at).total_seconds() / 3600

        # 2-hour follow-up email
        if hours_since >= FOLLOWUP_EMAIL_DELAY_HOURS and not data.get("email_sent"):
            email_addr = data.get("email", "")
            if email_addr and email_count < MAX_EMAIL_PER_RUN:
                variant = data.get("variant", "missed-revenue")
                first_name = data.get("first_name", "there")
                company = data.get("company", "")

                email_fn = VARIANT_EMAIL_MAP.get(variant, followup_email_missed_revenue)
                subject, body = email_fn(first_name, company)

                if send_email(cid, email_addr, subject, body):
                    data["email_sent"] = True
                    data["email_sent_at"] = now.isoformat()
                    add_tag(cid, EMAIL_SENT_TAG)
                    email_count += 1
                    state["stats"]["emails_sent"] = state["stats"].get("emails_sent", 0) + 1
                    log(f"2hr follow-up email sent to {first_name} ({cid}) — {variant}")

                time.sleep(1.5)

        # 24-hour escalation
        if hours_since >= ESCALATION_DELAY_HOURS and not data.get("escalated"):
            first_name = data.get("first_name", "Lead")
            company = data.get("company", "")

            # Tag as no response
            add_tag(cid, NO_RESPONSE_TAG)

            # Create task for Wallace
            due = (now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            add_task(cid,
                     f"FB lead {first_name} ({company}) — no response after 24hrs. Call or text manually.",
                     due)

            # Note
            add_note(cid,
                     f"FB Lead Ads: No response after 24 hours. "
                     f"Variant: {data.get('variant', '?')} | Vertical: {data.get('vertical', '?')} | "
                     f"Escalated at {now.strftime('%Y-%m-%d %H:%M')}")

            data["escalated"] = True
            data["escalated_at"] = now.isoformat()
            state["stats"]["no_response"] = state["stats"].get("no_response", 0) + 1

            log(f"24hr escalation for {first_name} ({cid}) — no response")

    save_state(state)
    log(f"Follow-up complete: {email_count} emails sent")


def cmd_status(state):
    """Show stats."""
    enrolled = state.get("enrolled", {})
    stats = state.get("stats", {})

    total = len(enrolled)
    replied = sum(1 for d in enrolled.values() if d.get("replied"))
    escalated = sum(1 for d in enrolled.values() if d.get("escalated") and not d.get("replied"))
    active = total - replied - escalated

    print("\n" + "=" * 60)
    print("  FACEBOOK LEAD ADS ENGINE — STATUS")
    print("=" * 60)
    print(f"  Total Enrolled:      {total}")
    print(f"  Active:              {active}")
    print(f"  Replied:             {replied}")
    print(f"  No Response (24hr):  {escalated}")
    print("-" * 60)
    print(f"  SMS Sent:            {stats.get('sms_sent', 0)}")
    print(f"  Emails Sent:         {stats.get('emails_sent', 0)}")
    print(f"  Replies Detected:    {stats.get('replies_detected', 0)}")
    print(f"  Interested (YES):    {stats.get('interested', 0)}")
    print("-" * 60)
    print("  By Variant:")
    for v, count in stats.get("by_variant", {}).items():
        print(f"    {v:20s} {count}")
    print("  By Vertical:")
    for v, count in stats.get("by_vertical", {}).items():
        print(f"    {v:20s} {count}")
    print("=" * 60)

    if replied:
        print("\n  REPLIES:")
        for cid, d in enrolled.items():
            if d.get("replied"):
                name = d.get("first_name", "?")
                yes = "YES" if d.get("is_yes") else "OTHER"
                reply = d.get("reply_body", "")[:60]
                print(f"    [{yes}] {name}: \"{reply}\"")
    print()


def cmd_preview(state):
    """Preview all message copy."""
    print("\n" + "=" * 60)
    print("  MESSAGE PREVIEW — FB Lead Ads Follow-Up")
    print("=" * 60)

    print("\n--- IMMEDIATE SMS (all variants) ---")
    print(initial_sms())

    for variant_key, fn in VARIANT_EMAIL_MAP.items():
        print(f"\n--- 2HR EMAIL: {variant_key} ---")
        subj, body = fn("Mike", "Mike's HVAC")
        print(f"Subject: {subj}")
        print(f"(HTML body with demo line + booking link)")

    print(f"\n--- 24HR ESCALATION ---")
    print("Action: Tag 'fb-lead-no-response' + create task for Wallace")

    print(f"\n--- REPLY 'YES' ---")
    print("Action: Tag 'fb-lead-interested' + ntfy URGENT + SMS to Wallace + 1hr task")

    print("\n" + "=" * 60 + "\n")


def cmd_run(state):
    """Full cycle: scan + followup."""
    cmd_scan(state)
    state = load_state()
    cmd_followup(state)


def cmd_test(state):
    """Dry run scan — show what would happen without sending."""
    log("TEST MODE — scanning without sending...")
    contacts = search_contacts_by_tag(SOURCE_TAG)
    enrolled = state.get("enrolled", {})

    print(f"\nFound {len(contacts)} contacts with '{SOURCE_TAG}' tag")
    new = 0
    for c in contacts:
        cid = c.get("id")
        if cid in enrolled:
            continue
        tags = c.get("tags", [])
        if any(t in EXCLUDE_TAGS for t in (tags if isinstance(tags, list) else [])):
            continue
        first_name = c.get("firstName") or "?"
        company = c.get("companyName") or ""
        phone = c.get("phone", "")
        variant = detect_variant(c)
        vertical = detect_vertical(c)
        print(f"  NEW: {first_name} ({company}) — {variant}/{vertical} — phone: {phone[:4]}***")
        new += 1

    print(f"\n{new} new leads would be enrolled (dry run — nothing sent)")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: fb-lead-ads-engine.py <scan|followup|status|run|preview|test>")
        sys.exit(1)

    command = sys.argv[1].lower()
    state = load_state()

    try:
        if command == "scan":
            cmd_scan(state)
        elif command == "followup":
            cmd_followup(state)
        elif command == "status":
            cmd_status(state)
        elif command == "run":
            cmd_run(state)
        elif command == "preview":
            cmd_preview(state)
        elif command == "test":
            cmd_test(state)
        else:
            print(f"Unknown command: {command}")
            print("Commands: scan, followup, status, run, preview, test")
            sys.exit(1)
    except Exception as e:
        log(f"CRASH: {e}\n{traceback.format_exc()}", "ERROR")
        ntfy(f"FB Lead Ads engine crashed: {e}",
             NTFY_SYSTEM, priority="high",
             title="[CRITICAL] FB Lead Ads Engine Crash")
        sys.exit(1)


if __name__ == "__main__":
    main()
