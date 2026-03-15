#!/usr/bin/env python3
"""
HOT LEAD CONVERTER ENGINE — The Call Taker
==========================================
Production follow-up engine for converting hot leads into booked demos and paying customers.

7-touch sequence over 7 days:
  Touch 1 (Day 0, Immediate): SMS — industry-aware pain hook + free pilot + demo line
  Touch 2 (Day 0, 2 hours):   Email — "Quick question about [Business Name]" — industry-aware
  Touch 3 (Day 1, 24 hours):  Bland.ai call attempt + voicemail if no answer
  Touch 4 (Day 2, 48 hours):  SMS — references the voicemail, soft nudge
  Touch 5 (Day 3, 72 hours):  Email — social proof, Robert Chen HVAC testimonial ($8,400 first week)
  Touch 6 (Day 5, 120 hours): SMS — urgency, pilot spots filling in their city
  Touch 7 (Day 7, 168 hours): Final email — last chance, direct ask, thecalltaker.com/book.html

Commands:
  scan     — Find hot-lead contacts not yet enrolled
  send     — Send due touches for enrolled contacts
  run      — scan + send (full cycle)
  enroll   — Force-enroll a specific contact by ID
  status   — Show enrollment stats
  notify   — Send Wallace a demo-booked alert (triggered by GHL webhook)

Schedule: Every 15 minutes via launchd
"""

import sys
import os
import json
import time
import requests
import traceback
from datetime import datetime, timedelta

# ─── Local Detection ────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from local_detect import is_local, get_lead_city
except ImportError:
    def is_local(c): return False
    def get_lead_city(c): return ""

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY        = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID    = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL       = "https://services.leadconnectorhq.com"
BLAND_API_KEY      = os.environ.get("TCT_BLAND_API_KEY", "org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969")
BLAND_BASE_URL     = "https://api.bland.ai/v1"
CALENDAR_ID        = "h4IlzccZ1m3JprEQqpMJ"
BOOKING_URL        = "https://thecalltaker.com/book.html"
DEMO_LINE          = "(615) 784-5747"
WALLACE_PHONE      = "+16156539004"
WALLACE_GHL_ID     = "DtKLG28VzgUb6q3brILD"
BUSINESS_EMAIL     = "thecalltakerai@gmail.com"
NTFY_URGENT        = "tct-urgent-Hk9UOEZR"
NTFY_ACTIVITY      = "tct-activity-cn1Aqa85"
NTFY_SYSTEM        = "tct-system-vRsfXQRQ"

STATE_FILE     = os.path.expanduser("~/thecalltaker/ops/hot-lead-converter-state.json")
LOG_FILE       = os.path.expanduser("~/thecalltaker/ops/hot-lead-converter.log")
HEARTBEAT_FILE = os.path.expanduser("~/thecalltaker/ops/hot-lead-converter.heartbeat")

# GHL API headers
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-HotLeadConverter/2.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-HotLeadConverter/2.0",
}

# Exclusion tags — never enroll these contacts
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "converter-enrolled",
    "donny-closing", "contacted",
}

# Tags that signal a positive reply — stop the sequence, flag for Wallace
POSITIVE_REPLY_TAGS = {
    "contacted", "pilot-active", "pilot-signup", "hot-reply",
    "demo-booked", "interested",
}

# ─── Touch Sequence Timing ────────────────────────────────────────────────────
#
# (touch_num, delay_minutes, touch_type)
# delay_minutes is measured from enrollment time (Touch 1 start)

TOUCH_SCHEDULE = [
    (1,   0,    "sms"),    # Day 0 — Immediate
    (2,   120,  "email"),  # Day 0 — 2 hours later
    (3,   1440, "call"),   # Day 1 — 24 hours (Bland.ai call + voicemail)
    (4,   2880, "sms"),    # Day 2 — 48 hours (references the voicemail)
    (5,   4320, "email"),  # Day 3 — 72 hours (Robert Chen social proof)
    (6,   7200, "sms"),    # Day 5 — 120 hours (city-based urgency)
    (7,   10080,"email"),  # Day 7 — 168 hours (final email, last chance)
]

# ─── Industry Mapping ────────────────────────────────────────────────────────

INDUSTRY_MAP = {
    "hvac":                ("service call", "$350+", "HVAC"),
    "plumbing":            ("service call", "$300+", "plumbing"),
    "electrical":          ("service call", "$275+", "electrical"),
    "roofing":             ("roof job", "$5,000+", "roofing"),
    "locksmith":           ("emergency call", "$250+", "locksmith"),
    "dental":              ("appointment", "$400+", "dental"),
    "medspa":              ("appointment", "$500+", "med spa"),
    "legal":               ("case consultation", "$500+", "legal"),
    "veterinary":          ("appointment", "$200+", "veterinary"),
    "towing":              ("tow call", "$150+", "towing"),
    "garage-door":         ("service call", "$300+", "garage door"),
    "pest-control":        ("service call", "$200+", "pest control"),
    "property-management": ("maintenance request", "$250+", "property management"),
    "water-damage":        ("emergency call", "$2,000+", "water damage restoration"),
    "cleaning":            ("booking", "$200+", "cleaning"),
    "landscaping":         ("estimate", "$300+", "landscaping"),
    "auto-repair":         ("repair job", "$400+", "auto repair"),
    "general-contractor":  ("estimate", "$1,000+", "contracting"),
    "funeral":             ("arrangement", "$3,000+", "funeral services"),
}

DEFAULT_INDUSTRY = ("service call", "$350+", "home services")


def get_industry_info(tags):
    """Extract (industry_word, job_value, industry_label) from contact tags."""
    if not tags:
        return DEFAULT_INDUSTRY
    for tag in tags:
        tag_lower = tag.lower().strip()
        if tag_lower in INDUSTRY_MAP:
            return INDUSTRY_MAP[tag_lower]
    return DEFAULT_INDUSTRY


# ─── Logging ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] hot-lead-converter: {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def write_heartbeat():
    try:
        os.makedirs(os.path.dirname(HEARTBEAT_FILE), exist_ok=True)
        with open(HEARTBEAT_FILE, "w") as f:
            f.write(datetime.now().isoformat())
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
        "enrolled": {},  # contact_id -> enrollment data
        "stats": {
            "total_enrolled": 0,
            "total_sms_sent": 0,
            "total_emails_sent": 0,
            "total_calls_made": 0,
            "total_demos_booked": 0,
            "total_conversions": 0,
            "total_positive_replies": 0,
        },
        "created": datetime.now().isoformat(),
    }


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


# ─── GHL API Helpers ─────────────────────────────────────────────────────────

def ghl_request(method, path, headers=None, params=None, json_body=None, retries=3):
    """Make a GHL API request with retry and rate-limit handling."""
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
                log(f"Bad request: {resp.text[:200]}", "ERROR")
                return None
            if resp.status_code == 401:
                log("Authentication failed — check API key", "ERROR")
                return None
            return resp.json() if resp.text else {}
        except requests.exceptions.RequestException as e:
            log(f"Request failed: {e}", "ERROR")
            if attempt < retries - 1:
                time.sleep(backoff[min(attempt, 2)])
    return None


def search_contacts_by_tag(tag, limit=100):
    """Search GHL contacts that have a specific tag."""
    all_contacts = []
    page = 1
    while True:
        data = ghl_request(
            "GET", "/contacts/",
            params={
                "locationId": GHL_LOCATION_ID,
                "query": "",
                "limit": limit,
                "page": page,
            },
        )
        if not data or "contacts" not in data:
            break
        contacts = data["contacts"]
        for c in contacts:
            contact_tags = c.get("tags", [])
            if isinstance(contact_tags, list) and tag in contact_tags:
                all_contacts.append(c)
        if len(contacts) < limit:
            break
        page += 1
        if page > 50:  # safety cap
            break
    return all_contacts


def get_contact(contact_id):
    """Get a single contact by ID."""
    data = ghl_request("GET", f"/contacts/{contact_id}")
    return data.get("contact") if data else None


def add_tag(contact_id, tags):
    """Add tags to a contact."""
    return ghl_request(
        "POST", f"/contacts/{contact_id}/tags",
        json_body={"tags": tags},
    )


def add_contact_note(contact_id, note_body):
    """Log an outcome note to the GHL contact record."""
    return ghl_request(
        "POST", f"/contacts/{contact_id}/notes",
        json_body={"body": note_body},
    )


def send_sms(contact_id, message):
    """Send SMS via GHL conversations API."""
    return ghl_request(
        "POST", "/conversations/messages",
        headers=CONVERSATIONS_HEADERS,
        json_body={
            "type": "SMS",
            "contactId": contact_id,
            "message": message,
        },
    )


def send_email(contact_id, subject, html_body):
    """Send email via GHL conversations API."""
    return ghl_request(
        "POST", "/conversations/messages",
        headers=CONVERSATIONS_HEADERS,
        json_body={
            "type": "Email",
            "contactId": contact_id,
            "subject": subject,
            "html": html_body,  # NOT "message" — html is the correct field for email body
            "emailFrom": f"Wallace Dobbs <{BUSINESS_EMAIL}>",
        },
    )


def send_wallace_sms(message):
    """Send SMS notification to Wallace."""
    return send_sms(WALLACE_GHL_ID, message)


def ntfy_alert(topic, title, message, priority="high"):
    """Send ntfy notification."""
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title": safe_title,
                "Priority": priority,
                "Tags": "fire" if priority == "urgent" else "chart_with_upwards_trend",
            },
            timeout=10,
        )
    except Exception as e:
        log(f"ntfy failed: {e}", "WARN")


# ─── Bland.ai Integration ────────────────────────────────────────────────────

def make_bland_call(contact_id, contact_data, industry_word, industry_label, job_value):
    """
    Place an outbound call via Bland.ai.
    If the prospect doesn't answer, Bland leaves a ~20-second voicemail.
    Returns (success: bool, call_id: str | None, outcome: str)
    """
    phone = contact_data.get("phone", "")
    if not phone:
        log(f"Touch 3 skipped for {contact_id} — no phone number", "WARN")
        return False, None, "no_phone"

    # Normalize phone format for Bland (+1XXXXXXXXXX)
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    if not digits.startswith("1") or len(digits) != 11:
        log(f"Touch 3 skipped — invalid phone format: {phone}", "WARN")
        return False, None, "invalid_phone"
    bland_phone = f"+{digits}"

    first_name = contact_data.get("firstName", "there")
    company_name = contact_data.get("companyName", "your business")

    # Live call task — the AI introduces itself and pitches the pilot
    task = (
        f"You are Wallace from The Call Taker, an AI receptionist service. "
        f"You are calling {first_name} at {company_name}. "
        f"Keep it friendly and direct. Say: "
        f"'Hey {first_name}, it's Wallace from The Call Taker. "
        f"I sent you a text earlier about the free pilot program for {industry_label} businesses. "
        f"We answer every call to your business 24/7 so you stop losing {industry_word}s to voicemail. "
        f"Takes 48 hours to set up, free for 14 days, no card required. "
        f"If you have 2 minutes I'd love to walk you through it — or just check your texts, I sent the details there.' "
        f"Then ask if they have 2 minutes. If they say yes, offer to walk them to thecalltaker.com/book.html to schedule a demo. "
        f"If no answer or voicemail, leave this exact message: "
        f"'Hey {first_name}, Wallace from The Call Taker. "
        f"I called because your {industry_word}s are going to voicemail — "
        f"and 85% of those callers hang up and call your competitor. "
        f"We fix that. Free 14-day pilot, no card, set up in 48 hours. "
        f"Check your texts from me — I sent the link. Talk soon.'"
    )

    payload = {
        "phone_number": bland_phone,
        "task": task,
        "voice": "mason",          # Neutral American male voice on Bland
        "wait_for_greeting": True,
        "record": True,
        "amd": True,               # Answering machine detection — triggers voicemail flow
        "answered_by_enabled": True,
        "max_duration": 3,         # Minutes — 20-second voicemail + brief live call window
        "temperature": 0.6,
        "language": "en-US",
        "metadata": {
            "contact_id": contact_id,
            "source": "hot-lead-converter-touch-3",
            "industry": industry_label,
        },
    }

    headers = {
        "Authorization": BLAND_API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "TheCallTaker-HotLeadConverter/2.0",
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                f"{BLAND_BASE_URL}/calls",
                headers=headers,
                json=payload,
                timeout=30,
            )
            if resp.status_code == 402:
                log("Bland.ai balance depleted (402) — Touch 3 call skipped", "ERROR")
                ntfy_alert(
                    NTFY_SYSTEM,
                    "[CRITICAL] Bland.ai Balance Depleted",
                    "hot-lead-converter Touch 3 calls stopped. Top up Bland.ai account immediately.",
                    priority="urgent",
                )
                return False, None, "bland_balance"
            if resp.status_code == 429:
                wait = [30, 60, 120][min(attempt, 2)]
                log(f"Bland rate limited, waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                wait = [5, 15, 30][min(attempt, 2)]
                log(f"Bland server error ({resp.status_code}), retry in {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code not in (200, 201):
                log(f"Bland API error {resp.status_code}: {resp.text[:200]}", "ERROR")
                return False, None, f"api_error_{resp.status_code}"

            data = resp.json()
            call_id = data.get("call_id") or data.get("id")
            log(f"Bland call placed: call_id={call_id}, phone={bland_phone}")
            return True, call_id, "placed"

        except requests.exceptions.RequestException as e:
            log(f"Bland request failed (attempt {attempt+1}): {e}", "ERROR")
            if attempt < 2:
                time.sleep([5, 15, 30][attempt])

    return False, None, "request_failed"


# ─── Touch Copy — National Sequence ──────────────────────────────────────────

def get_sms_touch_1(first_name, company_name, industry_word, industry_label):
    """Day 0 — Immediate SMS. Industry-aware pain hook + free pilot + demo line."""
    return (
        f"Hey {first_name}, it's Wallace from The Call Taker. "
        f"Quick question — who's answering {company_name}'s phones after 5pm? "
        f"If it's voicemail, you're losing {industry_word}s to competitors. "
        f"We built a free 14-day AI receptionist pilot for {industry_label} businesses — no card, set up in 48 hours. "
        f"Call {DEMO_LINE} right now to hear what your customers SHOULD hear."
    )


def get_email_touch_2(first_name, company_name, industry_word, industry_label, job_value):
    """Day 0, 2 hours — Email. Subject: 'Quick question about [Business Name]'"""
    subject = f"Quick question about {company_name}"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>What happens when a customer calls {company_name} at 7pm and nobody picks up?</p>

<p>For most {industry_label} businesses the answer is: voicemail. And <strong>85% of those callers hang up and call the next company on the list</strong> — usually a competitor who does answer.</p>

<p>At {job_value} per {industry_word}, every missed call is a job you never got credit for losing.</p>

<p>I built The Call Taker to fix exactly this. It's an AI receptionist that:</p>

<ul style="margin: 16px 0;">
<li>Answers every call 24/7 — sounds like a real person</li>
<li>Books appointments directly to your calendar</li>
<li>Texts you the caller's details instantly</li>
<li>Handles after-hours, weekends, and peak overflow</li>
</ul>

<p>We're running a free 14-day pilot for {industry_label} businesses right now. No card required. No contract. We set it up for you in 48 hours and you keep every dollar it earns.</p>

<p><strong>Call this number pretending to be a customer and hear it for yourself:</strong> {DEMO_LINE}<br>
Takes 90 seconds. No pressure.</p>

<p>Or just grab a time below — I'll walk you through it personally.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Book a 10-Minute Demo →</a>
</p>

<p>— Wallace Dobbs<br>
<span style="color: #666;">Founder, The Call Taker</span><br>
<span style="color: #666;">{DEMO_LINE}</span></p>

</div>"""
    return subject, html


def get_sms_touch_4(first_name, company_name, industry_word):
    """Day 2 — SMS. References the voicemail left on Day 1."""
    return (
        f"Hey {first_name} — I called {company_name} yesterday and left a voicemail. "
        f"Quick version: 85% of callers who get voicemail hang up and call a competitor. "
        f"At {job_value_from_word(industry_word)}, that's real money leaving every week. "
        f"Free 14-day pilot, no card — want me to set it up? Reply yes and I'll get started today."
    )


def get_email_touch_5(first_name, company_name, industry_word, industry_label, job_value):
    """Day 3 — Email. Social proof angle with Robert Chen HVAC testimonial."""
    subject = f"What happened to {company_name} after 14 days — a story"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>I want to share what happened to one of our {industry_label} clients — because it's the kind of thing that's hard to believe until you see the numbers.</p>

<blockquote style="border-left: 4px solid #f97316; padding: 16px 20px; margin: 20px 0; background: #fafafa; color: #222; border-radius: 4px;">
<p style="margin: 0 0 8px 0; font-style: italic;">"I signed up because Wallace told me to just try it for two weeks. First week, the AI booked $8,400 in jobs I never would have gotten — all after-hours calls I used to send to voicemail. By day 14 I was already paying for a year upfront."</p>
<p style="margin: 0; font-weight: 600; color: #f97316;">— Robert Chen, Chen's Climate Control (HVAC, Austin TX)</p>
</blockquote>

<p>Robert's situation is exactly what I see with {industry_label} businesses: the phone rings after 5pm, nobody answers, and the job goes to whoever picked up.</p>

<p>The math for {company_name}:</p>

<ul style="margin: 16px 0;">
<li>Miss 3 calls a week at {job_value} each → <strong>$4,500+/month in lost revenue</strong></li>
<li>Our AI answers them all, 24/7</li>
<li>Cost after the pilot: less than one missed {industry_word}</li>
</ul>

<p>The free 14-day pilot is still open for {company_name}. No card. No commitment. If it doesn't book you more jobs, you owe nothing and walk away.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Start the Free Pilot →</a>
</p>

<p>— Wallace<br>
<span style="color: #666;">Founder, The Call Taker | {DEMO_LINE}</span></p>

</div>"""
    return subject, html


def get_sms_touch_6(first_name, city):
    """Day 5 — SMS. City-based urgency — pilot spots filling up."""
    location = city if city else "your area"
    return (
        f"{first_name} — pilot spots are filling up fast in {location} this month. "
        f"We can only take 3 businesses per city to keep the quality right. "
        f"14 days free, no card, set up in 48 hours. "
        f"Grab the spot before it's gone: {BOOKING_URL}"
    )


def get_email_touch_7(first_name, company_name, industry_label):
    """Day 7 — Final email. Last chance, direct ask, book a 10-minute demo."""
    subject = f"Last message, {first_name}"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>This is my last message.</p>

<p>I've reached out a few times because I genuinely believe The Call Taker would help {company_name}. Every {industry_label} business I've worked with has the same story: calls going to voicemail, jobs going to competitors, and no idea how much revenue they're actually losing.</p>

<p>Here's the direct ask:</p>

<p><strong>Give me 10 minutes.</strong></p>

<p>Book a call, I'll show you the AI live — you'll hear it answer a call just like a customer would. If it's not for you, I'll shake your hand (virtually) and never contact you again. No pitch, no pressure, no hard sell.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Book 10 Minutes → thecalltaker.com/book.html</a>
</p>

<p>Or if the timing just isn't right, no worries at all. You can call our demo line anytime: <strong>{DEMO_LINE}</strong> — it's live 24/7.</p>

<p>Either way, I wish you and {company_name} the best. Hope the phones are ringing.</p>

<p>— Wallace Dobbs<br>
<span style="color: #666;">Founder, The Call Taker</span></p>

</div>"""
    return subject, html


# ─── LOCAL VARIANTS ───────────────────────────────────────────────────────────

def get_local_sms_touch_1(first_name, company_name, city, industry_label):
    """Day 0 Immediate SMS — in-person CTA for local leads."""
    city_part = f"right here in {city}" if city else "local to Nashville"
    return (
        f"Hey {first_name}, it's Wallace from The Call Taker — I'm {city_part}. "
        f"I built something new for {industry_label} businesses like {company_name} "
        f"and I'd love to show you in person or on a quick call — takes 10 minutes. "
        f"We answer every call you miss, 24/7. Free 14-day pilot, no card. "
        f"Call {DEMO_LINE} to hear it yourself. Worth it?"
    )


def get_local_email_touch_2(first_name, company_name, industry_word, industry_label, job_value, city):
    """Day 0, 2 hours — Email for local leads. In-person offer."""
    city_display = city if city else "the Nashville area"
    subject = f"Quick question about {company_name}"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>What happens when a customer calls {company_name} at 7pm and nobody picks up?</p>

<p>For most {industry_label} businesses the answer is: voicemail. And <strong>85% of those callers hang up and call the next company on Google</strong> — usually someone who does answer.</p>

<p>At {job_value} per {industry_word}, every missed call is a job you never knew you lost.</p>

<p>I built The Call Taker to fix this. It's an AI receptionist that answers every call 24/7, books appointments, and texts you the details instantly. Sounds like a real person. Works better than a part-time receptionist at a fraction of the cost.</p>

<p>Since we're both in {city_display}, I'd love to come by and show you in person. <strong>Takes 10 minutes.</strong> You'll hear the AI answer a live call to your business. If you're not impressed, I'll be out of your hair in 5.</p>

<p><strong>Or just call the demo line right now:</strong> {DEMO_LINE}<br>
Takes 90 seconds. Pretend you need a {industry_word}.</p>

<p><strong>What day works this week?</strong> Just reply and I'll be there.</p>

<p>— Wallace Dobbs<br>
<span style="color: #666;">Founder, The Call Taker | Brentwood, TN</span><br>
<span style="color: #666;">{DEMO_LINE}</span></p>

</div>"""
    return subject, html


def get_local_sms_touch_4(first_name, city):
    """Day 2 — SMS for local leads. References the voicemail."""
    city_part = city if city else "your area"
    return (
        f"Hey {first_name} — I called and left a voicemail yesterday. "
        f"I'm still in {city_part} this week if you want me to stop by and show you in person. "
        f"14 days free, no card, takes 10 minutes to see it live. "
        f"Just reply and I'll make it work around your schedule."
    )


def get_local_sms_touch_6(first_name, city):
    """Day 5 — SMS for local leads. City-based urgency."""
    location = city if city else "our area"
    return (
        f"{first_name} — I'm only running 3 free pilots in {location} this month. "
        f"Two spots are taken. Last chance before it's $97/mo to start. "
        f"10 minutes in person or on a call — reply and I'll set it up today."
    )


def get_local_email_touch_5(first_name, company_name, industry_label, city):
    """Day 3 email for local leads — social proof + in-person offer."""
    city_display = city if city else "the Nashville area"
    subject = f"What happened to {company_name} after 14 days — a story"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>One of our {industry_label} clients — Robert Chen in Austin — made $8,400 in his first week just from calls he used to send to voicemail.</p>

<blockquote style="border-left: 4px solid #f97316; padding: 16px 20px; margin: 20px 0; background: #fafafa; color: #222; border-radius: 4px;">
<p style="margin: 0 0 8px 0; font-style: italic;">"I signed up because Wallace told me to just try it for two weeks. First week, the AI booked $8,400 in jobs I never would have gotten — all after-hours calls I used to send to voicemail. By day 14 I was already paying for a year upfront."</p>
<p style="margin: 0; font-weight: 600; color: #f97316;">— Robert Chen, Chen's Climate Control (HVAC, Austin TX)</p>
</blockquote>

<p>Since we're both in {city_display}, I'd love to show you what that looks like for {company_name} in person. 10 minutes. Your location. This week.</p>

<p>Or jump right in with the free 14-day pilot — no card, set up in 48 hours.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Start the Free Pilot →</a>
</p>

<p>Just reply if you want me to come by instead. I'll make it happen.</p>

<p>— Wallace</p>

</div>"""
    return subject, html


def get_local_email_touch_7(first_name, company_name, industry_label, city):
    """Day 7 final email for local leads."""
    city_display = city if city else "the area"
    subject = f"Last message, {first_name}"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>This is my last message.</p>

<p>I've reached out a few times because I think The Call Taker would genuinely help {company_name}. Every {industry_label} business I've talked to in {city_display} has the same problem: calls going to voicemail, jobs going to competitors.</p>

<p>The direct ask: <strong>give me 10 minutes</strong>. In person at your location, or on a quick call — your choice. I'll show you the AI live, you'll hear it answer a call to your business, and you can decide if it's worth 14 free days to find out.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Book 10 Minutes → thecalltaker.com/book.html</a>
</p>

<p>No pitch, no pressure. If it's not for you, I'll shake your hand and leave. Promise.</p>

<p>— Wallace Dobbs<br>
<span style="color: #666;">Founder, The Call Taker | Brentwood, TN | {DEMO_LINE}</span></p>

</div>"""
    return subject, html


# ─── Helper ───────────────────────────────────────────────────────────────────

def value_from_job_value(job_value):
    """Strip '+' and return the string e.g. '$350+' -> '$350'."""
    return job_value.rstrip("+")


def job_value_from_word(industry_word):
    """Look up the job value for a given industry_word (reverse lookup)."""
    for _, (word, value, _) in INDUSTRY_MAP.items():
        if word == industry_word:
            return value
    return "$350+"


# ─── Sequence Logic ───────────────────────────────────────────────────────────

def should_send_touch(enrollment, touch_num):
    """Check if a touch is due based on enrollment time and schedule."""
    touches_sent = enrollment.get("touches_sent", [])
    if touch_num in touches_sent:
        return False  # Already sent

    # Must send touches in order
    if touch_num > 1 and (touch_num - 1) not in touches_sent:
        return False

    # Stop on positive reply
    if enrollment.get("replied", False):
        return False

    # Check timing against TOUCH_SCHEDULE
    enrolled_at = datetime.fromisoformat(enrollment["enrolled_at"])
    schedule_entry = next((s for s in TOUCH_SCHEDULE if s[0] == touch_num), None)
    if not schedule_entry:
        return False
    _, delay_minutes, _ = schedule_entry
    due_at = enrolled_at + timedelta(minutes=delay_minutes)

    return datetime.now() >= due_at


def flag_positive_reply(contact_id, enrollment, first_name, company_name, reason):
    """
    Pull a contact out of the sequence and alert Wallace for immediate personal response.
    Called whenever a positive signal tag is detected.
    """
    enrollment["replied"] = True
    enrollment["positive_reply_reason"] = reason
    enrollment["positive_reply_at"] = datetime.now().isoformat()

    add_tag(contact_id, ["hot-reply", "needs-personal-response"])
    add_contact_note(
        contact_id,
        f"[Hot Lead Converter] Positive signal detected — sequence stopped. "
        f"Reason: {reason}. Flagged for immediate personal response from Wallace. "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    )

    alert_msg = (
        f"HOT: {first_name} at {company_name} showed a positive signal ({reason}). "
        f"Sequence paused. Contact them personally NOW. Check GHL."
    )
    send_wallace_sms(alert_msg)
    ntfy_alert(
        NTFY_URGENT,
        f"[CRITICAL] Hot Lead Positive Signal — {first_name}",
        alert_msg,
        priority="urgent",
    )
    log(f"Positive signal flagged for {first_name} ({contact_id}): {reason}")


def execute_touch(contact_id, contact_data, enrollment, touch_num, state):
    """
    Execute a specific touch for a contact.
    Routes local vs national. Logs outcome to GHL.
    Tags contact with hot-seq-N after each successful touch.
    Returns True on success.
    """
    first_name    = contact_data.get("firstName", "there")
    company_name  = contact_data.get("companyName", "your business")
    tags          = contact_data.get("tags", [])
    industry_word, job_value, industry_label = get_industry_info(tags)
    local         = is_local(contact_data)
    city          = get_lead_city(contact_data) if local else ""

    if local:
        log(f"  LOCAL lead: {first_name} at {company_name} ({city})")

    success = False
    note_body = None

    # ── Touch 1: Day 0 Immediate SMS ──────────────────────────────────────────
    if touch_num == 1:
        if local:
            msg = get_local_sms_touch_1(first_name, company_name, city, industry_label)
        else:
            msg = get_sms_touch_1(first_name, company_name, industry_word, industry_label)
        result = send_sms(contact_id, msg)
        success = result is not None
        if success:
            state["stats"]["total_sms_sent"] += 1
            log(f"Touch 1 SMS sent to {first_name} ({contact_id}){' [LOCAL]' if local else ''}")
            note_body = (
                f"[HLC Touch 1] SMS sent — industry-aware pain hook + free pilot + demo line. "
                f"Industry: {industry_label}. Local: {local}. "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

    # ── Touch 2: Day 0 +2 hours Email ────────────────────────────────────────
    elif touch_num == 2:
        if local:
            subject, html = get_local_email_touch_2(
                first_name, company_name, industry_word, industry_label, job_value, city
            )
        else:
            subject, html = get_email_touch_2(
                first_name, company_name, industry_word, industry_label, job_value
            )
        result = send_email(contact_id, subject, html)
        success = result is not None
        if success:
            state["stats"]["total_emails_sent"] += 1
            log(f"Touch 2 Email sent to {first_name} ({contact_id}){' [LOCAL]' if local else ''}")
            note_body = (
                f"[HLC Touch 2] Email sent — subject: '{subject}'. "
                f"Industry-aware content for {industry_label}. Local: {local}. "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

    # ── Touch 3: Day 1 Bland.ai Call ─────────────────────────────────────────
    elif touch_num == 3:
        bland_success, call_id, outcome = make_bland_call(
            contact_id, contact_data, industry_word, industry_label, job_value
        )
        success = bland_success
        if success:
            state["stats"]["total_calls_made"] += 1
            enrollment["bland_call_id"] = call_id
            log(f"Touch 3 Bland call placed for {first_name} ({contact_id}) — call_id={call_id}")
            note_body = (
                f"[HLC Touch 3] Bland.ai call placed — call_id={call_id}. "
                f"AMD enabled; voicemail left if no answer (~20 seconds). "
                f"Industry: {industry_label}. Outcome: {outcome}. "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            # Log the skip so we don't leave the sequence stuck
            log(f"Touch 3 call not placed for {first_name} ({contact_id}): {outcome}", "WARN")
            note_body = (
                f"[HLC Touch 3] Bland.ai call skipped — reason: {outcome}. "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            # Still advance the sequence so Touch 4 can fire
            enrollment["touches_sent"].append(touch_num)
            enrollment["last_touch_at"] = datetime.now().isoformat()
            if note_body:
                add_contact_note(contact_id, note_body)
            return False  # Return False but sequence is unblocked via touches_sent above

    # ── Touch 4: Day 2 SMS — references the voicemail ────────────────────────
    elif touch_num == 4:
        if local:
            msg = get_local_sms_touch_4(first_name, city)
        else:
            msg = get_sms_touch_4(first_name, company_name, industry_word)
        result = send_sms(contact_id, msg)
        success = result is not None
        if success:
            state["stats"]["total_sms_sent"] += 1
            log(f"Touch 4 SMS (voicemail follow-up) sent to {first_name} ({contact_id}){' [LOCAL]' if local else ''}")
            note_body = (
                f"[HLC Touch 4] SMS sent — references Day 1 voicemail, soft pilot offer. "
                f"Local: {local}. {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

    # ── Touch 5: Day 3 Email — Robert Chen social proof ──────────────────────
    elif touch_num == 5:
        if local:
            subject, html = get_local_email_touch_5(first_name, company_name, industry_label, city)
        else:
            subject, html = get_email_touch_5(
                first_name, company_name, industry_word, industry_label, job_value
            )
        result = send_email(contact_id, subject, html)
        success = result is not None
        if success:
            state["stats"]["total_emails_sent"] += 1
            log(f"Touch 5 Email (social proof) sent to {first_name} ({contact_id}){' [LOCAL]' if local else ''}")
            note_body = (
                f"[HLC Touch 5] Email sent — Robert Chen HVAC testimonial ($8,400 first week). "
                f"Subject: '{subject}'. Local: {local}. "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

    # ── Touch 6: Day 5 SMS — city urgency ────────────────────────────────────
    elif touch_num == 6:
        if local:
            msg = get_local_sms_touch_6(first_name, city)
        else:
            msg = get_sms_touch_6(first_name, city)
        result = send_sms(contact_id, msg)
        success = result is not None
        if success:
            state["stats"]["total_sms_sent"] += 1
            log(f"Touch 6 SMS (city urgency) sent to {first_name} ({contact_id}){' [LOCAL]' if local else ''}")
            note_body = (
                f"[HLC Touch 6] SMS sent — pilot spots filling up in {city or 'their city'}. "
                f"Local: {local}. {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

    # ── Touch 7: Day 7 Final Email ────────────────────────────────────────────
    elif touch_num == 7:
        if local:
            subject, html = get_local_email_touch_7(first_name, company_name, industry_label, city)
        else:
            subject, html = get_email_touch_7(first_name, company_name, industry_label)
        result = send_email(contact_id, subject, html)
        success = result is not None
        if success:
            state["stats"]["total_emails_sent"] += 1
            log(f"Touch 7 Final Email sent to {first_name} ({contact_id}){' [LOCAL]' if local else ''}")
            note_body = (
                f"[HLC Touch 7] Final email sent — last chance, direct demo ask, "
                f"thecalltaker.com/book.html. Local: {local}. "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

    # ── Post-touch logging ────────────────────────────────────────────────────
    if success:
        enrollment["touches_sent"].append(touch_num)
        enrollment["last_touch_at"] = datetime.now().isoformat()

        # Tag contact in GHL: hot-seq-1 through hot-seq-7
        add_tag(contact_id, [f"hot-seq-{touch_num}"])

        # Log outcome to GHL contact record
        if note_body:
            add_contact_note(contact_id, note_body)

        # Activity notification
        touch_type_label = {
            1: "SMS", 2: "Email", 3: "Call", 4: "SMS", 5: "Email", 6: "SMS", 7: "Email"
        }.get(touch_num, "Touch")
        ntfy_alert(
            NTFY_ACTIVITY,
            f"Hot Lead Touch {touch_num}/7",
            f"{touch_type_label} sent to {first_name} ({company_name}) — Touch {touch_num}/7",
            priority="default",
        )

    return success


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_scan(state):
    """Find hot-lead contacts not yet enrolled in the converter sequence."""
    log("Scanning for new hot leads...")
    contacts = search_contacts_by_tag("hot-lead")
    new_enrollments = 0

    for contact in contacts:
        cid = contact.get("id")
        if not cid:
            continue

        # Skip if already enrolled
        if cid in state["enrolled"]:
            continue

        # Skip if contact has exclusion tags
        contact_tags = set(contact.get("tags", []))
        if contact_tags & EXCLUDE_TAGS:
            log(f"Skipping {contact.get('firstName', '?')} ({cid}) — excluded by tag")
            continue

        # Skip if no phone AND no email
        phone = contact.get("phone", "")
        email = contact.get("email", "")
        if not phone and not email:
            log(f"Skipping {contact.get('firstName', '?')} ({cid}) — no phone or email")
            continue

        # Enroll
        state["enrolled"][cid] = {
            "enrolled_at": datetime.now().isoformat(),
            "touches_sent": [],
            "last_touch_at": None,
            "replied": False,
            "positive_reply_reason": None,
            "positive_reply_at": None,
            "demo_booked": False,
            "converted": False,
            "bland_call_id": None,
            "first_name": contact.get("firstName", ""),
            "company_name": contact.get("companyName", ""),
            "phone": phone,
            "email": email,
        }
        state["stats"]["total_enrolled"] += 1
        new_enrollments += 1

        # Tag in GHL so we don't re-enroll on next scan
        add_tag(cid, ["converter-enrolled"])
        log(f"Enrolled: {contact.get('firstName', '?')} at {contact.get('companyName', '?')} ({cid})")

    log(f"Scan complete. {new_enrollments} new enrollments. {len(contacts)} total hot leads found.")
    return new_enrollments


def cmd_send(state):
    """Send due touches for all enrolled contacts."""
    log("Processing touches...")
    touches_sent = 0
    completed = 0

    for cid, enrollment in list(state["enrolled"].items()):
        if enrollment.get("replied") or enrollment.get("converted"):
            continue

        # Sequence complete when all 7 touches are sent
        if len(enrollment.get("touches_sent", [])) >= 7:
            completed += 1
            continue

        # Get fresh contact data for personalization and tag checking
        contact = get_contact(cid)
        if not contact:
            log(f"Contact {cid} not found in GHL, skipping", "WARN")
            continue

        # Check for positive reply tags — pull out of sequence immediately
        contact_tags = set(contact.get("tags", []))
        matching_positive = contact_tags & POSITIVE_REPLY_TAGS
        if matching_positive:
            reason = ", ".join(sorted(matching_positive))
            flag_positive_reply(
                cid, enrollment,
                enrollment.get("first_name", "?"),
                enrollment.get("company_name", "?"),
                reason,
            )
            state["stats"]["total_positive_replies"] += 1
            continue

        # Send next due touch (one per contact per run cycle)
        for touch_num in range(1, 8):
            if should_send_touch(enrollment, touch_num):
                if execute_touch(cid, contact, enrollment, touch_num, state):
                    touches_sent += 1
                break  # One touch per contact per cycle

        # Brief pause between contacts to respect rate limits
        time.sleep(2)

    log(f"Send complete. {touches_sent} touches sent. {completed} sequences fully completed.")
    return touches_sent


def cmd_run(state):
    """Full cycle: scan for new leads + send due touches."""
    new  = cmd_scan(state)
    sent = cmd_send(state)
    save_state(state)
    write_heartbeat()

    if new > 0 or sent > 0:
        ntfy_alert(
            NTFY_ACTIVITY,
            "Hot Lead Converter Cycle",
            f"Enrolled: {new} new | Touches sent: {sent} | "
            f"Total enrolled: {state['stats']['total_enrolled']}",
            priority="default",
        )


def cmd_enroll(state, contact_id):
    """Force-enroll a specific contact by ID."""
    if contact_id in state["enrolled"]:
        log(f"Contact {contact_id} already enrolled")
        return

    contact = get_contact(contact_id)
    if not contact:
        log(f"Contact {contact_id} not found", "ERROR")
        return

    state["enrolled"][contact_id] = {
        "enrolled_at": datetime.now().isoformat(),
        "touches_sent": [],
        "last_touch_at": None,
        "replied": False,
        "positive_reply_reason": None,
        "positive_reply_at": None,
        "demo_booked": False,
        "converted": False,
        "bland_call_id": None,
        "first_name": contact.get("firstName", ""),
        "company_name": contact.get("companyName", ""),
        "phone": contact.get("phone", ""),
        "email": contact.get("email", ""),
    }
    state["stats"]["total_enrolled"] += 1
    add_tag(contact_id, ["converter-enrolled", "hot-lead"])
    save_state(state)
    log(f"Force-enrolled: {contact.get('firstName', '?')} ({contact_id})")


def cmd_notify(state, contact_id=None, source="demo-booking"):
    """Notify Wallace when a demo is booked."""
    name    = "A hot lead"
    company = ""
    phone   = ""

    if contact_id:
        contact = get_contact(contact_id)
        if contact:
            name    = contact.get("firstName", "Someone")
            company = contact.get("companyName", "")
            phone   = contact.get("phone", "")

        if contact_id in state["enrolled"]:
            state["enrolled"][contact_id]["demo_booked"] = True
            state["stats"]["total_demos_booked"] += 1
            save_state(state)

    wallace_msg = (
        f"DEMO BOOKED: {name}"
        + (f" from {company}" if company else "")
        + (f" ({phone})" if phone else "")
        + f" just booked a demo. Source: {source}. Check GHL calendar NOW."
    )
    send_wallace_sms(wallace_msg)

    ntfy_alert(
        NTFY_URGENT,
        f"[CRITICAL] Demo Booked — {name}",
        wallace_msg,
        priority="urgent",
    )
    log(f"Demo-booked notification sent for {name} ({contact_id})")


def cmd_status(state):
    """Print enrollment stats and active sequence summary."""
    stats    = state["stats"]
    enrolled = state["enrolled"]

    active = sum(
        1 for e in enrolled.values()
        if not e.get("replied") and not e.get("converted")
        and len(e.get("touches_sent", [])) < 7
    )
    completed = sum(1 for e in enrolled.values() if len(e.get("touches_sent", [])) >= 7)
    replied   = sum(1 for e in enrolled.values() if e.get("replied"))
    booked    = sum(1 for e in enrolled.values() if e.get("demo_booked"))

    print("\n╔══════════════════════════════════════════╗")
    print("║    HOT LEAD CONVERTER — STATUS (7-TOUCH) ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  Total Enrolled:     {stats['total_enrolled']:>5}               ║")
    print(f"║  Active Sequences:   {active:>5}               ║")
    print(f"║  Completed (7/7):    {completed:>5}               ║")
    print(f"║  Positive Replies:   {stats.get('total_positive_replies', 0):>5}               ║")
    print(f"║  Replied/Stopped:    {replied:>5}               ║")
    print(f"║  Demos Booked:       {booked:>5}               ║")
    print(f"║  SMS Sent:           {stats['total_sms_sent']:>5}               ║")
    print(f"║  Emails Sent:        {stats['total_emails_sent']:>5}               ║")
    print(f"║  Calls Made:         {stats.get('total_calls_made', 0):>5}               ║")
    print("╚══════════════════════════════════════════╝\n")

    if active > 0:
        print("Active sequences:")
        for cid, e in enrolled.items():
            if not e.get("replied") and not e.get("converted") and len(e.get("touches_sent", [])) < 7:
                touches = len(e.get("touches_sent", []))
                print(
                    f"  {e.get('first_name', '?'):15} | "
                    f"{e.get('company_name', '?'):25} | "
                    f"Touch {touches}/7 | "
                    f"Enrolled: {e['enrolled_at'][:10]}"
                )
        print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: hot-lead-converter.py <command> [args]")
        print("Commands: scan, send, run, enroll <contact_id>, notify [contact_id] [source], status")
        sys.exit(1)

    command = sys.argv[1].lower()
    state   = load_state()

    try:
        if command == "scan":
            cmd_scan(state)
            save_state(state)
        elif command == "send":
            cmd_send(state)
            save_state(state)
        elif command == "run":
            cmd_run(state)
        elif command == "enroll":
            if len(sys.argv) < 3:
                print("Usage: hot-lead-converter.py enroll <contact_id>")
                sys.exit(1)
            cmd_enroll(state, sys.argv[2])
        elif command == "notify":
            contact_id = sys.argv[2] if len(sys.argv) > 2 else None
            source     = sys.argv[3] if len(sys.argv) > 3 else "demo-booking"
            cmd_notify(state, contact_id, source)
        elif command == "status":
            cmd_status(state)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        tb = traceback.format_exc()
        log(f"CRASH: {e}\n{tb}", "ERROR")
        ntfy_alert(
            NTFY_SYSTEM,
            "[CRITICAL] Hot Lead Converter Crashed",
            f"Command: {command}\nError: {str(e)[:400]}\n{tb[:300]}",
            priority="urgent",
        )
        raise


if __name__ == "__main__":
    main()
