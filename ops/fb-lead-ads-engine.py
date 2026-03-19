#!/usr/bin/env python3
"""
FACEBOOK LEAD ADS — SPEED-TO-LEAD + 5-DAY FOLLOW-UP ENGINE
=============================================================
The Call Taker — thecalltaker.com

30-second speed-to-lead with a 12-touch, 5-day follow-up sprint.
Contact rate drops 50%+ after 5 minutes — this is the #1 priority.

Trigger: Contact tagged "facebook-lead" in GHL

SEQUENCE (12 touches over 5 days):
  DAY 0:
    SMS #1  (0 min)   — demo line CTA + reply YES
    Email #1 (0 min)  — confirmation + booking link + one-line benefit
    SMS #2  (2-3 hrs) — variant-specific angle
    Email #2 (6-8 hrs)— social proof + single CTA
  DAY 1:
    SMS #3  (morning) — "still the best time to catch you?"
    Email #3 (afternoon) — "how many calls did [business] miss?"
  DAY 2:
    SMS #4  — pattern interrupt: "what's happening to your after-hours calls?"
    Email #4 — objection: "will my customers know it's not a real person?"
  DAY 3:
    SMS #5  — vertical-specific pain point
    Email #5 — case study: "how a [vertical] owner stopped missing jobs"
  DAY 4:
    SMS #6  — soft close: "last thing I'll send this week"
  DAY 5:
    Email #6 — breakup: "should I close your file?"

REPLY HANDLING:
  Any reply → pause → tag fb-lead-replied → ntfy URGENT → 1hr task
  YES/book/demo → tag fb-lead-interested → SMS to Wallace → 30min task
  stop/unsubscribe → tag fb-lead-opted-out → kill sequence → log

Commands:
  scan       — Find new leads, fire immediate SMS #1 + Email #1 + ntfy
  followup   — Send due touches (SMS #2-6, Email #2-6), check replies
  run        — scan + followup
  status     — Enrollment stats
  sequence   — Per-lead sequence progress
  benchmarks — Speed-to-lead + conversion metrics
  preview    — Preview all 12 messages
  test       — Dry run scan

Schedule (launchd):
  scan every 5 minutes (speed-to-lead critical path)
  followup every 30 minutes
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

BOOKING_URL    = "https://thecalltaker.com/demo.html"
DEMO_LINE      = "(615) 784-5747"
WALLACE_PHONE  = "+16156539004"
WALLACE_GHL_ID = "DtKLG28VzgUb6q3brILD"
FROM_EMAIL     = "thecalltakerai@gmail.com"

# ntfy topics
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
REPLIED_TAG      = "fb-lead-replied"
INTERESTED_TAG   = "fb-lead-interested"
OPTED_OUT_TAG    = "fb-lead-opted-out"
NO_RESPONSE_TAG  = "fb-lead-no-response"
EXHAUSTED_TAG    = "fb-lead-exhausted"

VARIANT_TAGS = {
    "missed-revenue":  "fb-missed-revenue",
    "after-hours":     "fb-after-hours",
    "hiring-headache": "fb-hiring-headache",
}

VERTICAL_TAGS = {
    "hvac":     "hvac",
    "plumbing": "plumbing",
    "dental":   "dental",
}

# Rate limits per run
MAX_SMS_PER_RUN   = 25
MAX_EMAIL_PER_RUN = 20

# ─── 5-Day Sequence Schedule ────────────────────────────────────────────────
# (step_key, delay_minutes_from_enrollment, channel, time_of_day_constraint)
# time_of_day_constraint: None=send anytime, "morning"=8-11am, "afternoon"=12-5pm

SEQUENCE_STEPS = [
    ("sms1",    0,      "sms",   None),         # Day 0 — immediate
    ("email1",  1,      "email", None),          # Day 0 — 1 min after (effectively immediate)
    ("sms2",    150,    "sms",   None),          # Day 0 — 2.5 hours
    ("email2",  420,    "email", None),          # Day 0 — 7 hours
    ("sms3",    1440,   "sms",   "morning"),     # Day 1 — morning (24hr)
    ("email3",  1620,   "email", "afternoon"),   # Day 1 — afternoon (27hr)
    ("sms4",    2880,   "sms",   None),          # Day 2 — 48 hours
    ("email4",  2970,   "email", None),          # Day 2 — 49.5 hours
    ("sms5",    4320,   "sms",   None),          # Day 3 — 72 hours
    ("email5",  4410,   "email", None),          # Day 3 — 73.5 hours
    ("sms6",    5760,   "sms",   None),          # Day 4 — 96 hours
    ("email6",  7200,   "email", None),          # Day 5 — 120 hours
]

# GHL API headers
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-FBLeadAds/2.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-FBLeadAds/2.0",
}

EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", ENROLLED_TAG, OPTED_OUT_TAG,
    EXHAUSTED_TAG,
}

# ─── Vertical Pain Points ───────────────────────────────────────────────────

VERTICAL_PAIN = {
    "hvac": {
        "label": "HVAC",
        "pain_sms": (
            "HVAC emergencies don't wait for business hours. When someone's AC dies "
            "at midnight in July, they call the first company that answers — not the "
            "best rated. How many of those calls is {company} missing?"
        ),
        "case_name": "HVAC company in Nashville",
        "case_stat": "23 after-hours calls answered in the first week — $8,400 in jobs saved",
    },
    "plumbing": {
        "label": "plumbing",
        "pain_sms": (
            "Burst pipe at 2 AM. Homeowner calls 3 plumbers. The first one that answers "
            "gets a $600 job. The other two get a voicemail nobody checks. Which one is "
            "{company} right now?"
        ),
        "case_name": "plumbing company in Atlanta",
        "case_stat": "17 emergency calls caught after hours in 10 days — $5,100 in new revenue",
    },
    "dental": {
        "label": "dental",
        "pain_sms": (
            "A new patient calls your office during lunch. Front desk is busy. Voicemail. "
            "They call the practice down the street. That's a $400 first visit and $2,000+ "
            "lifetime value — gone. How often is that happening at {company}?"
        ),
        "case_name": "dental practice in Charlotte",
        "case_stat": "31 new patient calls captured during lunch and after hours in 2 weeks",
    },
}

DEFAULT_VERTICAL = {
    "label": "service",
    "pain_sms": (
        "Every missed call is a customer calling your competitor instead. Most service "
        "businesses miss 5-10 calls a week — that's $2,000-$10,000/month in lost revenue. "
        "How many is {company} missing?"
    ),
    "case_name": "service business owner",
    "case_stat": "went from missing 40% of calls to answering 100% — revenue up 23% in 30 days",
}

# YES-intent keywords
YES_KEYWORDS = {
    "yes", "y", "yeah", "yep", "sure", "ok", "okay", "yes please", "yes!",
    "let's do it", "sign me up", "interested", "set it up", "ready",
    "book", "demo", "schedule", "show me", "i'm in", "let's go",
}

# Opt-out keywords
OPTOUT_KEYWORDS = {"stop", "unsubscribe", "opt out", "remove me", "cancel", "quit"}


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
        "benchmarks": {
            "response_times_sec": [],
            "demos_booked": 0,
            "total_cpl_cents": 0,
            "cpl_entries": 0,
        },
        "stats": {
            "total_enrolled": 0,
            "sms_sent": 0,
            "emails_sent": 0,
            "replies_detected": 0,
            "interested": 0,
            "opted_out": 0,
            "exhausted": 0,
            "by_variant": {"missed-revenue": 0, "after-hours": 0, "hiring-headache": 0},
            "by_vertical": {"hvac": 0, "plumbing": 0, "dental": 0, "other": 0},
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
                log("Auth failed — check GHL API key", "ERROR")
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
            "locationId": GHL_LOCATION_ID, "query": "", "limit": limit, "page": page,
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


def remove_tag(contact_id, tags):
    if isinstance(tags, str):
        tags = [tags]
    return ghl_request("DELETE", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def add_note(contact_id, body):
    return ghl_request("POST", f"/contacts/{contact_id}/notes", json_body={"body": body})


def add_task(contact_id, title, due_date):
    return ghl_request("POST", f"/contacts/{contact_id}/tasks", json_body={
        "title": title, "body": title, "dueDate": due_date, "completed": False,
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
                         json_body={"type": "SMS", "contactId": contact_id, "message": message})
    if result is None:
        log(f"SMS send failed for {contact_id}", "ERROR")
        return False
    log(f"SMS sent to {contact_id} ({phone})")
    return True


def send_email(contact_id, email, subject, html_body):
    result = ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS,
                         json_body={
                             "type": "Email", "contactId": contact_id,
                             "subject": subject, "html": html_body,
                             "emailFrom": f"Wallace from The Call Taker <{FROM_EMAIL}>",
                         })
    if result is None:
        log(f"Email send failed for {contact_id}", "ERROR")
        return False
    log(f"Email sent to {contact_id} ({email})")
    return True


def check_for_inbound_reply(contact_id):
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
            return True, msg.get("body") or msg.get("message") or ""
    return False, None


# ─── ntfy ────────────────────────────────────────────────────────────────────

def ntfy(message, topic=NTFY_ACTIVITY, priority="default", title=None):
    headers = {"Priority": priority}
    if title:
        safe_title = "".join(c for c in title if 32 <= ord(c) < 127)
        headers["Title"] = safe_title[:250]
    for attempt in range(3):
        try:
            resp = requests.post(f"https://ntfy.sh/{topic}",
                                 data=message.encode("utf-8"), headers=headers, timeout=10)
            if resp.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    return False


# ─── Variant / Vertical Detection ───────────────────────────────────────────

def detect_variant(contact):
    tags = contact.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    for vk, vt in VARIANT_TAGS.items():
        if vt in tags:
            return vk
    source = (contact.get("source") or "").lower()
    custom_fields = contact.get("customFields", contact.get("customField", []))
    if isinstance(custom_fields, list):
        for cf in custom_fields:
            if isinstance(cf, dict):
                val = str(cf.get("value", "")).lower()
                if "missed-revenue" in val: return "missed-revenue"
                if "after-hours" in val: return "after-hours"
                if "hiring-headache" in val or "hiring" in val: return "hiring-headache"
    if "missed-revenue" in source: return "missed-revenue"
    if "after-hours" in source: return "after-hours"
    if "hiring" in source: return "hiring-headache"
    return "missed-revenue"


def detect_vertical(contact):
    tags = contact.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    for v in VERTICAL_TAGS:
        if v in tags:
            return v
    return "hvac"


def get_vertical_data(vertical):
    return VERTICAL_PAIN.get(vertical, DEFAULT_VERTICAL)


# ─── Message Templates (12 touches) ─────────────────────────────────────────

def _e(html_content):
    """Wrap email body in styled container."""
    return f"""<div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333; line-height: 1.6;">
{html_content}
</div>"""


# ── DAY 0 ──

def sms1(first_name, **_):
    return (
        f"Hey {first_name}, this is The Call Taker. You asked about having a live "
        f"receptionist answer your calls 24/7. Want to hear Jessica answer a call "
        f"right now? Call {DEMO_LINE} — or reply YES and I'll send you a booking link."
    )


def email1(first_name, company, **_):
    return (
        f"You're in, {first_name} — here's your demo",
        _e(f"""<p>Hey {first_name},</p>
<p>Thanks for requesting info about The Call Taker. Here's what happens next:</p>
<p><strong>Hear Jessica answer a call live</strong> — she's our receptionist that answers
your phones 24/7, sounds completely human, and books appointments automatically.</p>
<p style="text-align:center; margin: 24px 0;">
  <a href="{BOOKING_URL}" style="background:#00dc82; color:#000; padding:14px 32px;
  border-radius:8px; text-decoration:none; font-weight:700; font-size:16px;">
  Book Your 10-Minute Demo</a>
</p>
<p>Or call the demo line right now: <strong>{DEMO_LINE}</strong></p>
<p style="color:#666; font-size:14px;">14-day free trial · No setup fee · Flat monthly rate · Cancel anytime</p>
<p>— Wallace<br>The Call Taker</p>""")
    )


def sms2_missed_revenue(first_name, company, **_):
    return (
        f"Quick math {first_name}: if {company or 'your business'} misses just 3 calls a week "
        f"at $300-$800 per job, that's $4,000-$10,000/month in lost revenue. "
        f"Jessica catches every one of those. Want to see? {BOOKING_URL}"
    )


def sms2_after_hours(first_name, company, **_):
    return (
        f"{first_name} — 68% of service calls happen after hours. If nobody's answering "
        f"{company or 'your'} phones at 9 PM, those customers are calling your competitor. "
        f"Jessica answers 24/7. Want to hear her? {BOOKING_URL}"
    )


def sms2_hiring_headache(first_name, company, **_):
    return (
        f"{first_name} — a receptionist costs $2,500/mo + benefits + sick days. "
        f"Jessica costs $97/mo, answers 24/7, never calls in sick, and books appointments "
        f"automatically. Want to hear the difference? {BOOKING_URL}"
    )


def email2(first_name, company, **_):
    return (
        f"One stat that might change how you think about your phones",
        _e(f"""<p>Hey {first_name},</p>
<p>Here's a number most business owners don't know:</p>
<p style="font-size:24px; font-weight:700; color:#000; margin:16px 0;">
The average service business misses 41% of incoming calls.</p>
<p>Lunch breaks. After hours. Busy times when everyone's on the job site.</p>
<p>A {company or 'business'} owner in Charleston started a free trial with us.
First week: <strong>23 calls answered that would've been missed. $8,400 in jobs saved.</strong></p>
<p>Three months later — zero missed calls.</p>
<p style="text-align:center; margin: 24px 0;">
  <a href="{BOOKING_URL}" style="background:#00dc82; color:#000; padding:14px 32px;
  border-radius:8px; text-decoration:none; font-weight:700;">
  See It Live in 10 Minutes</a>
</p>
<p>— Wallace<br>The Call Taker</p>""")
    )


# ── DAY 1 ──

def sms3(first_name, **_):
    return (
        f"Still the best time to catch you, {first_name}? Happy to show you "
        f"Jessica live in 10 minutes. {BOOKING_URL}"
    )


def email3(first_name, company, **_):
    return (
        f"How many calls did {company or 'your business'} miss last week?",
        _e(f"""<p>Hey {first_name},</p>
<p>Serious question: how many calls did {company or 'your business'} miss last week?</p>
<p>If the answer is "I don't know" — that's the problem. Most owners don't realize
how many calls go to voicemail because they never see the ones they miss.</p>
<p>Every missed call = $300-$800 walking to your competitor.</p>
<p>The Call Taker answers every call in 2 rings. 24/7. Sounds like a real person.
Books appointments. Texts you the details.</p>
<p><strong>14-day free trial. No setup fee. Cancel anytime.</strong></p>
<p style="text-align:center; margin: 24px 0;">
  <a href="{BOOKING_URL}" style="background:#00dc82; color:#000; padding:14px 32px;
  border-radius:8px; text-decoration:none; font-weight:700;">
  Book a 10-Minute Demo</a>
</p>
<p>— Wallace<br>The Call Taker</p>""")
    )


# ── DAY 2 ──

def sms4(first_name, **_):
    return (
        f"Honest question {first_name} — what's actually happening to your "
        f"after-hours calls right now?"
    )


def email4(first_name, company, **_):
    return (
        f"\"Will my customers know it's not a real person?\"",
        _e(f"""<p>Hey {first_name},</p>
<p>This is the #1 question I get, so let me address it head on:</p>
<p><strong>"Will my customers know it's not a real person?"</strong></p>
<p>Short answer: no. Here's why:</p>
<ul>
<li>Jessica answers in your business name — "{company or 'your company'}, how can I help you?"</li>
<li>She handles the full conversation — collects details, answers FAQs, books appointments</li>
<li>She sounds like a real person (no phone trees, no "press 1 for...")</li>
<li>She texts you the details so you can follow up personally</li>
</ul>
<p>Don't take my word for it — <strong>call the demo line and test her yourself:</strong></p>
<p style="font-size:20px; font-weight:700; text-align:center; margin:20px 0;">
<a href="tel:+16157845747" style="color:#00dc82;">{DEMO_LINE}</a></p>
<p>Tell her you're a {get_vertical_data(detect_vertical({"tags":[]}))["label"]} owner.
See if you can tell the difference.</p>
<p>— Wallace<br>The Call Taker</p>""")
    )


# ── DAY 3 ──

def sms5(first_name, company, vertical, **_):
    vdata = get_vertical_data(vertical)
    return vdata["pain_sms"].format(company=company or "your business")


def email5(first_name, company, vertical, **_):
    vdata = get_vertical_data(vertical)
    return (
        f"How a {vdata['case_name']} stopped missing jobs",
        _e(f"""<p>Hey {first_name},</p>
<p>Quick story about a {vdata['case_name']}:</p>
<p>They were missing 30-40% of incoming calls. After hours, lunch breaks, busy times.
Every missed call was a job going to the competition.</p>
<p>They started a free trial with The Call Taker. Results:</p>
<p style="font-size:18px; font-weight:700; color:#000; margin:16px 0; padding:16px;
background:#f0fdf4; border-left:4px solid #00dc82; border-radius:4px;">
{vdata['case_stat']}</p>
<p>Now they haven't missed a single call in months.</p>
<p>Your 14-day free trial is ready whenever you are. No setup fee. No contracts.</p>
<p style="text-align:center; margin: 24px 0;">
  <a href="{BOOKING_URL}" style="background:#00dc82; color:#000; padding:14px 32px;
  border-radius:8px; text-decoration:none; font-weight:700;">
  Start Your Free Trial</a>
</p>
<p>— Wallace<br>The Call Taker</p>""")
    )


# ── DAY 4 ──

def sms6(first_name, **_):
    return (
        f"Last thing I'll send this week {first_name}. If the timing's ever right, "
        f"the demo takes 10 minutes and costs nothing: {BOOKING_URL}"
    )


# ── DAY 5 ──

def email6(first_name, company, **_):
    return (
        f"Should I close your file?",
        _e(f"""<p>Hey {first_name},</p>
<p>I've reached out a few times about helping {company or 'your business'} stop missing calls,
and I haven't heard back. Totally fine — I know the timing isn't always right.</p>
<p>I'm going to close your file on my end so I'm not cluttering your inbox.</p>
<p>But if you ever want to:</p>
<ul>
<li>Hear Jessica answer a call live → <strong><a href="tel:+16157845747" style="color:#00dc82;">{DEMO_LINE}</a></strong></li>
<li>Book a 10-minute demo → <strong><a href="{BOOKING_URL}" style="color:#00dc82;">thecalltaker.com/demo</a></strong></li>
<li>Just ask a question → reply to this email</li>
</ul>
<p>14-day free trial is always available. No setup fee. Cancel anytime.</p>
<p>Wishing you the best,<br>Wallace<br>The Call Taker</p>""")
    )


# ─── Step → Message Dispatch ────────────────────────────────────────────────

def get_sms2_fn(variant):
    return {
        "missed-revenue":  sms2_missed_revenue,
        "after-hours":     sms2_after_hours,
        "hiring-headache": sms2_hiring_headache,
    }.get(variant, sms2_missed_revenue)


STEP_MESSAGE_MAP = {
    "sms1":   ("sms",   sms1),
    "email1": ("email", email1),
    "sms2":   ("sms",   None),  # resolved at runtime via variant
    "email2": ("email", email2),
    "sms3":   ("sms",   sms3),
    "email3": ("email", email3),
    "sms4":   ("sms",   sms4),
    "email4": ("email", email4),
    "sms5":   ("sms",   sms5),
    "email5": ("email", email5),
    "sms6":   ("sms",   sms6),
    "email6": ("email", email6),
}


def get_message_for_step(step_key, data):
    """Return (channel, content) for a given step."""
    first_name = data.get("first_name", "there")
    company = data.get("company", "")
    variant = data.get("variant", "missed-revenue")
    vertical = data.get("vertical", "hvac")
    ctx = dict(first_name=first_name, company=company, variant=variant, vertical=vertical)

    if step_key == "sms2":
        fn = get_sms2_fn(variant)
        return "sms", fn(**ctx)

    channel, fn = STEP_MESSAGE_MAP[step_key]
    result = fn(**ctx)
    if channel == "email":
        return "email", result  # (subject, body) tuple
    return "sms", result  # string


# ─── Reply Handler ───────────────────────────────────────────────────────────

def handle_reply(contact_id, contact, reply_body, state):
    first_name = contact.get("firstName") or contact.get("first_name") or "Lead"
    company = contact.get("companyName") or contact.get("company") or ""
    phone = contact.get("phone", "")
    reply_lower = (reply_body or "").strip().lower()

    log(f"REPLY from {first_name} ({contact_id}): {reply_body[:100]}")

    enrolled = state.get("enrolled", {})
    if contact_id in enrolled:
        enrolled[contact_id]["replied"] = True
        enrolled[contact_id]["replied_at"] = datetime.now().isoformat()
        enrolled[contact_id]["reply_body"] = reply_body[:500]

    # Check for opt-out
    if any(kw in reply_lower for kw in OPTOUT_KEYWORDS):
        add_tag(contact_id, OPTED_OUT_TAG)
        remove_tag(contact_id, SOURCE_TAG)
        add_note(contact_id, f"Opted out of FB lead sequence: \"{reply_body[:200]}\"")
        if contact_id in enrolled:
            enrolled[contact_id]["opted_out"] = True
        state["stats"]["opted_out"] = state["stats"].get("opted_out", 0) + 1
        log(f"OPT-OUT: {first_name} ({contact_id})")
        save_state(state)
        return

    # Pause sequence + tag
    add_tag(contact_id, REPLIED_TAG)

    # Check for YES intent
    is_yes = any(kw in reply_lower for kw in YES_KEYWORDS)

    if contact_id in enrolled:
        enrolled[contact_id]["is_yes"] = is_yes

    company_str = f" ({company})" if company else ""

    if is_yes:
        add_tag(contact_id, INTERESTED_TAG)

        # Record response time for benchmarks
        if contact_id in enrolled:
            enrolled_at = enrolled[contact_id].get("enrolled_at")
            if enrolled_at:
                delta = (datetime.now() - datetime.fromisoformat(enrolled_at)).total_seconds()
                state.setdefault("benchmarks", {}).setdefault("response_times_sec", []).append(int(delta))

        ntfy(f"FB Lead {first_name}{company_str} replied YES!\n\n"
             f"Phone: {phone}\nReply: \"{reply_body[:200]}\"\n"
             f"Action: Follow up within 30 minutes",
             NTFY_URGENT, priority="urgent",
             title=f"[CRITICAL] FB Lead YES — {first_name}")

        send_sms(WALLACE_GHL_ID, WALLACE_PHONE,
                 f"FB LEAD YES: {first_name}{company_str} replied YES!\n"
                 f"Call NOW: {phone}")

        due = (datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        add_task(contact_id,
                 f"FB lead {first_name} replied YES — call within 30 min: {phone}", due)

        add_note(contact_id, f"Replied YES at {datetime.now().strftime('%Y-%m-%d %H:%M')}: \"{reply_body[:200]}\"")
        state["stats"]["interested"] = state["stats"].get("interested", 0) + 1

    else:
        ntfy(f"FB Lead {first_name}{company_str} replied:\n\"{reply_body[:200]}\"\n\n"
             f"Phone: {phone}",
             NTFY_URGENT, priority="high",
             title=f"[HIGH] FB Lead Reply — {first_name}")

        due = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        add_task(contact_id,
                 f"FB lead {first_name} replied: \"{reply_body[:80]}\" — review & respond", due)

    state["stats"]["replies_detected"] = state["stats"].get("replies_detected", 0) + 1
    save_state(state)


# ─── Time-of-Day Check ──────────────────────────────────────────────────────

def check_time_constraint(constraint):
    """Return True if current time satisfies the constraint."""
    if constraint is None:
        return True
    hour = datetime.now().hour
    if constraint == "morning":
        return 8 <= hour < 11
    if constraint == "afternoon":
        return 12 <= hour < 17
    return True


# ─── Core Commands ───────────────────────────────────────────────────────────

def cmd_scan(state):
    """Find new leads — fire immediate SMS #1 + Email #1 + ntfy within 30 seconds."""
    log("SPEED SCAN — checking for new Facebook leads...")
    scan_start = time.time()

    contacts = search_contacts_by_tag(SOURCE_TAG)
    enrolled = state.get("enrolled", {})
    new_count = 0

    for c in contacts:
        cid = c.get("id")
        if not cid or cid in enrolled:
            continue
        tags = c.get("tags", [])
        if not isinstance(tags, list):
            tags = []
        if any(t in EXCLUDE_TAGS for t in tags):
            continue
        if SOURCE_TAG not in tags:
            continue

        lead_start = time.time()
        first_name = c.get("firstName") or c.get("first_name") or "there"
        phone = c.get("phone", "")
        email = c.get("email", "")
        company = c.get("companyName") or c.get("company") or ""
        variant = detect_variant(c)
        vertical = detect_vertical(c)

        # Enroll with full 5-day tracking
        enrolled[cid] = {
            "first_name": first_name,
            "phone": phone,
            "email": email,
            "company": company,
            "variant": variant,
            "vertical": vertical,
            "enrolled_at": datetime.now().isoformat(),
            "steps_sent": [],
            "replied": False,
            "opted_out": False,
        }

        # Apply tags
        tags_to_add = [ENROLLED_TAG]
        if variant in VARIANT_TAGS:
            tags_to_add.append(VARIANT_TAGS[variant])
        if vertical in VERTICAL_TAGS and VERTICAL_TAGS[vertical] not in tags:
            tags_to_add.append(VERTICAL_TAGS[vertical])
        add_tag(cid, tags_to_add)

        # SPEED: SMS #1 — must fire within 30 seconds
        sms_ok = False
        if phone:
            msg = sms1(first_name)
            sms_ok = send_sms(cid, phone, msg)
            if sms_ok:
                enrolled[cid]["steps_sent"].append({"step": "sms1", "at": datetime.now().isoformat()})
                state["stats"]["sms_sent"] = state["stats"].get("sms_sent", 0) + 1

        # SPEED: Email #1 — must fire within 60 seconds
        email_ok = False
        if email:
            subj, body = email1(first_name, company)
            email_ok = send_email(cid, email, subj, body)
            if email_ok:
                enrolled[cid]["steps_sent"].append({"step": "email1", "at": datetime.now().isoformat()})
                state["stats"]["emails_sent"] = state["stats"].get("emails_sent", 0) + 1

        # SPEED: ntfy URGENT to Wallace — within 30 seconds
        company_str = f" at {company}" if company else ""
        ntfy(f"NEW FB LEAD: {first_name}{company_str}\n"
             f"Phone: {phone}\nEmail: {email}\n"
             f"Variant: {variant} | Vertical: {vertical}\n"
             f"SMS sent: {'YES' if sms_ok else 'NO'} | Email sent: {'YES' if email_ok else 'NO'}\n"
             f"Action: Call within 5 minutes — contact rate drops 50% after that",
             NTFY_URGENT, priority="urgent",
             title=f"[CRITICAL] New FB Lead — {first_name}")

        elapsed = time.time() - lead_start
        log(f"ENROLLED {first_name} ({cid}) — {variant}/{vertical} — {elapsed:.1f}s")

        state["stats"]["by_variant"][variant] = state["stats"]["by_variant"].get(variant, 0) + 1
        vkey = vertical if vertical in state["stats"]["by_vertical"] else "other"
        state["stats"]["by_vertical"][vkey] = state["stats"]["by_vertical"].get(vkey, 0) + 1
        new_count += 1

    state["enrolled"] = enrolled
    state["stats"]["total_enrolled"] = len(enrolled)
    save_state(state)

    total_elapsed = time.time() - scan_start
    log(f"Scan complete: {new_count} new leads in {total_elapsed:.1f}s")
    return new_count


def cmd_followup(state):
    """Send due touches (SMS #2-6, Email #2-6) and check replies."""
    log("Running follow-up cycle...")

    enrolled = state.get("enrolled", {})
    now = datetime.now()
    sms_count = 0
    email_count = 0

    for cid, data in list(enrolled.items()):
        if data.get("replied") or data.get("opted_out"):
            continue

        # Check for reply
        contact = get_contact(cid)
        if not contact:
            continue

        current_tags = contact.get("tags", [])
        if isinstance(current_tags, list):
            positive = {"contacted", "pilot-active", "pilot-signup", "demo-booked",
                        "interested", "pilot-converted", "customer", INTERESTED_TAG}
            if any(t in positive for t in current_tags):
                data["replied"] = True
                save_state(state)
                continue

        has_reply, reply_body = check_for_inbound_reply(cid)
        if has_reply and not data.get("replied"):
            handle_reply(cid, contact, reply_body or "", state)
            continue

        # Determine which steps have been sent
        steps_sent = {s["step"] for s in data.get("steps_sent", [])}
        enrolled_at = datetime.fromisoformat(data["enrolled_at"])
        minutes_since = (now - enrolled_at).total_seconds() / 60

        for step_key, delay_min, channel, time_constraint in SEQUENCE_STEPS:
            if step_key in steps_sent:
                continue
            if minutes_since < delay_min:
                break  # Not due yet — remaining steps are even later

            # Check time-of-day constraint
            if not check_time_constraint(time_constraint):
                continue  # Skip for now, will catch next run

            # Rate limiting
            if channel == "sms" and sms_count >= MAX_SMS_PER_RUN:
                break
            if channel == "email" and email_count >= MAX_EMAIL_PER_RUN:
                break

            phone = data.get("phone", "")
            email_addr = data.get("email", "")

            ch, content = get_message_for_step(step_key, data)
            sent = False

            if ch == "sms" and phone:
                sent = send_sms(cid, phone, content)
                if sent:
                    sms_count += 1
                    state["stats"]["sms_sent"] = state["stats"].get("sms_sent", 0) + 1
            elif ch == "email" and email_addr:
                subj, body = content
                sent = send_email(cid, email_addr, subj, body)
                if sent:
                    email_count += 1
                    state["stats"]["emails_sent"] = state["stats"].get("emails_sent", 0) + 1

            if sent:
                data["steps_sent"].append({"step": step_key, "at": now.isoformat()})
                log(f"{step_key} sent to {data['first_name']} ({cid})")
                time.sleep(1.5)

            # Only send one step per contact per run for pacing
            if sent:
                break

        # Check for sequence exhaustion (all 12 steps sent, no reply)
        if len(steps_sent) >= len(SEQUENCE_STEPS) and not data.get("replied"):
            if not data.get("exhausted"):
                data["exhausted"] = True
                data["exhausted_at"] = now.isoformat()
                add_tag(cid, EXHAUSTED_TAG)
                add_note(cid, f"FB Lead Ads: Completed full 5-day sequence with no response — "
                              f"{now.strftime('%Y-%m-%d %H:%M')}")
                state["stats"]["exhausted"] = state["stats"].get("exhausted", 0) + 1
                log(f"Sequence exhausted for {data['first_name']} ({cid})")

        save_state(state)

    log(f"Follow-up complete: {sms_count} SMS, {email_count} emails")


def cmd_run(state):
    """Full cycle: scan + followup."""
    cmd_scan(state)
    state = load_state()
    cmd_followup(state)


def cmd_status(state):
    """Show enrollment stats."""
    enrolled = state.get("enrolled", {})
    stats = state.get("stats", {})

    total = len(enrolled)
    replied = sum(1 for d in enrolled.values() if d.get("replied"))
    opted_out = sum(1 for d in enrolled.values() if d.get("opted_out"))
    exhausted = sum(1 for d in enrolled.values() if d.get("exhausted") and not d.get("replied"))
    active = total - replied - opted_out - exhausted

    print("\n" + "=" * 65)
    print("  FB LEAD ADS ENGINE v2 — SPEED-TO-LEAD + 5-DAY SPRINT")
    print("=" * 65)
    print(f"  Total Enrolled:      {total}")
    print(f"  Active (in sequence):{active}")
    print(f"  Replied:             {replied}")
    print(f"  Interested (YES):    {stats.get('interested', 0)}")
    print(f"  Opted Out:           {opted_out}")
    print(f"  Exhausted (Day 5):   {exhausted}")
    print("-" * 65)
    print(f"  SMS Sent:            {stats.get('sms_sent', 0)}")
    print(f"  Emails Sent:         {stats.get('emails_sent', 0)}")
    print(f"  Total Touches:       {stats.get('sms_sent', 0) + stats.get('emails_sent', 0)}")
    print("-" * 65)
    print("  By Variant:")
    for v, count in stats.get("by_variant", {}).items():
        print(f"    {v:20s} {count}")
    print("  By Vertical:")
    for v, count in stats.get("by_vertical", {}).items():
        print(f"    {v:20s} {count}")
    print("=" * 65)

    if replied:
        print("\n  REPLIES:")
        for cid, d in enrolled.items():
            if d.get("replied") and not d.get("opted_out"):
                name = d.get("first_name", "?")
                yes = "YES" if d.get("is_yes") else "REPLY"
                reply = d.get("reply_body", "")[:60]
                print(f"    [{yes}] {name}: \"{reply}\"")
    print()


def cmd_sequence(state):
    """Show per-lead sequence progress."""
    enrolled = state.get("enrolled", {})
    if not enrolled:
        print("\nNo leads enrolled yet.\n")
        return

    all_step_keys = [s[0] for s in SEQUENCE_STEPS]

    print("\n" + "=" * 90)
    print("  SEQUENCE STATUS — Per Lead")
    print("=" * 90)
    print(f"  {'Name':<16} {'Variant':<16} {'Steps':<8} {'Status':<12} {'Last Step':<10} {'Enrolled'}")
    print("-" * 90)

    for cid, d in enrolled.items():
        name = d.get("first_name", "?")[:15]
        variant = d.get("variant", "?")[:15]
        steps_done = len(d.get("steps_sent", []))
        total_steps = len(all_step_keys)

        if d.get("opted_out"):
            status = "OPTED-OUT"
        elif d.get("is_yes"):
            status = "YES"
        elif d.get("replied"):
            status = "REPLIED"
        elif d.get("exhausted"):
            status = "EXHAUSTED"
        else:
            status = "ACTIVE"

        last_step = d["steps_sent"][-1]["step"] if d.get("steps_sent") else "—"
        enrolled_at = d.get("enrolled_at", "")[:10]

        print(f"  {name:<16} {variant:<16} {steps_done}/{total_steps:<5} {status:<12} {last_step:<10} {enrolled_at}")

    print("=" * 90)

    # Step completion grid
    print("\n  STEP GRID (X = sent, . = pending, - = skipped):")
    print(f"  {'Name':<16}", end="")
    for sk in all_step_keys:
        print(f" {sk[:5]:>5}", end="")
    print()

    for cid, d in enrolled.items():
        name = d.get("first_name", "?")[:15]
        steps_done = {s["step"] for s in d.get("steps_sent", [])}
        print(f"  {name:<16}", end="")
        for sk in all_step_keys:
            if sk in steps_done:
                print("     X", end="")
            elif d.get("replied") or d.get("opted_out"):
                print("     -", end="")
            else:
                print("     .", end="")
        print()
    print()


def cmd_benchmarks(state):
    """Show speed-to-lead + conversion metrics."""
    enrolled = state.get("enrolled", {})
    benchmarks = state.get("benchmarks", {})
    stats = state.get("stats", {})

    total = len(enrolled)
    replied = sum(1 for d in enrolled.values() if d.get("replied") and not d.get("opted_out"))
    interested = stats.get("interested", 0)
    demos = benchmarks.get("demos_booked", 0)

    # Median response time
    response_times = benchmarks.get("response_times_sec", [])
    if response_times:
        sorted_times = sorted(response_times)
        mid = len(sorted_times) // 2
        median_sec = sorted_times[mid]
        median_str = f"{median_sec}s" if median_sec < 60 else f"{median_sec // 60}m {median_sec % 60}s"
    else:
        median_str = "N/A (no replies yet)"

    # Contact rate
    contact_rate = (replied / total * 100) if total > 0 else 0
    demo_rate = (demos / total * 100) if total > 0 else 0

    # CPL
    cpl_entries = benchmarks.get("cpl_entries", 0)
    total_cpl = benchmarks.get("total_cpl_cents", 0)
    avg_cpl = (total_cpl / cpl_entries / 100) if cpl_entries > 0 else 0
    cost_per_demo = (avg_cpl * total / demos) if demos > 0 and avg_cpl > 0 else 0

    print("\n" + "=" * 65)
    print("  BENCHMARKS — Speed-to-Lead + Conversion")
    print("=" * 65)

    print(f"\n  SPEED-TO-LEAD:")
    print(f"    Median response time:    {median_str}")
    goal_met = "YES" if response_times and sorted(response_times)[len(response_times)//2] < 120 else "NO"
    print(f"    Goal (<2 min):           {goal_met}")

    print(f"\n  CONTACT RATE (within 48hrs):")
    print(f"    Replied (any):           {replied}/{total} ({contact_rate:.0f}%)")
    print(f"    Goal (50-70%):           {'ON TRACK' if 50 <= contact_rate <= 70 else 'NEEDS WORK' if total > 5 else 'TOO EARLY'}")

    print(f"\n  LEAD-TO-DEMO RATE:")
    print(f"    Interested (YES):        {interested}/{total} ({(interested/total*100) if total else 0:.0f}%)")
    print(f"    Demos Booked:            {demos}/{total} ({demo_rate:.0f}%)")
    print(f"    Goal (20-35%):           {'ON TRACK' if 20 <= demo_rate <= 35 else 'NEEDS WORK' if total > 5 else 'TOO EARLY'}")

    print(f"\n  COST METRICS:")
    print(f"    Avg CPL:                 ${avg_cpl:.2f}" if avg_cpl else "    Avg CPL:                 N/A (use: benchmarks set-cpl <cents>)")
    print(f"    Cost per Demo Booked:    ${cost_per_demo:.2f}" if cost_per_demo else "    Cost per Demo Booked:    N/A")

    print(f"\n  SEQUENCE EFFECTIVENESS:")
    sms_total = stats.get("sms_sent", 0)
    email_total = stats.get("emails_sent", 0)
    touch_total = sms_total + email_total
    print(f"    Total touches sent:      {touch_total}")
    print(f"    Touches per reply:       {touch_total / replied:.1f}" if replied else "    Touches per reply:       N/A")
    print(f"    SMS sent:                {sms_total}")
    print(f"    Emails sent:             {email_total}")
    print(f"    Opted out:               {stats.get('opted_out', 0)}")

    print("=" * 65)

    # Instructions for manual input
    if not cpl_entries:
        print("\n  To set CPL: edit state file or add to benchmarks.total_cpl_cents/cpl_entries")
    if not demos:
        print("  To record a demo: tag contact 'demo-booked' in GHL — engine will detect it")
    print()


def cmd_preview(state):
    """Preview all 12 messages."""
    print("\n" + "=" * 70)
    print("  MESSAGE PREVIEW — 5-Day Follow-Up Sprint (12 touches)")
    print("=" * 70)

    ctx = {"first_name": "Mike", "company": "Mike's HVAC", "variant": "missed-revenue", "vertical": "hvac"}

    for step_key, delay_min, channel, constraint in SEQUENCE_STEPS:
        day = delay_min // 1440
        hrs = (delay_min % 1440) // 60
        time_note = f" ({constraint})" if constraint else ""

        print(f"\n{'─' * 70}")
        print(f"  {step_key.upper()} — Day {day}, +{delay_min}min ({hrs}h){time_note} — {channel.upper()}")
        print(f"{'─' * 70}")

        ch, content = get_message_for_step(step_key, ctx)
        if ch == "sms":
            print(f"  {content}")
        else:
            subj, body = content
            print(f"  Subject: {subj}")
            print(f"  (HTML email body — see source for full content)")

    # Show variant-specific SMS #2 for other variants
    print(f"\n{'─' * 70}")
    print(f"  SMS2 VARIANTS:")
    print(f"{'─' * 70}")
    for v in ["after-hours", "hiring-headache"]:
        ctx2 = {**ctx, "variant": v}
        _, content = get_message_for_step("sms2", ctx2)
        print(f"\n  [{v}] {content}")

    # Show vertical-specific SMS #5 for other verticals
    print(f"\n{'─' * 70}")
    print(f"  SMS5 VERTICALS:")
    print(f"{'─' * 70}")
    for v in ["plumbing", "dental"]:
        ctx3 = {**ctx, "vertical": v}
        _, content = get_message_for_step("sms5", ctx3)
        print(f"\n  [{v}] {content}")

    print(f"\n{'=' * 70}\n")


def cmd_test(state):
    """Dry run scan."""
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
        print("Usage: fb-lead-ads-engine.py <scan|followup|run|status|sequence|benchmarks|preview|test>")
        sys.exit(1)

    command = sys.argv[1].lower()
    state = load_state()

    try:
        cmds = {
            "scan": cmd_scan, "followup": cmd_followup, "run": cmd_run,
            "status": cmd_status, "sequence": cmd_sequence,
            "benchmarks": cmd_benchmarks, "preview": cmd_preview, "test": cmd_test,
        }
        fn = cmds.get(command)
        if fn:
            fn(state)
        else:
            print(f"Unknown command: {command}")
            print("Commands: scan, followup, run, status, sequence, benchmarks, preview, test")
            sys.exit(1)
    except Exception as e:
        log(f"CRASH: {e}\n{traceback.format_exc()}", "ERROR")
        ntfy(f"FB Lead Ads engine crashed: {e}",
             NTFY_SYSTEM, priority="high",
             title="[CRITICAL] FB Lead Ads Engine Crash")
        sys.exit(1)


if __name__ == "__main__":
    main()
