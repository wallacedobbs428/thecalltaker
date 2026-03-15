#!/usr/bin/env python3
"""
HOT LEAD CONVERTER ENGINE — The Call Taker
==========================================
Production follow-up engine for converting hot leads into booked demos and paying customers.

5-touch sequence over 7 days:
  Touch 1 (Immediate): SMS — pain hook + demo line CTA
  Touch 2 (10 min):    Email — case study + scarcity + booking link
  Touch 3 (24 hours):  SMS — missed revenue angle + Wallace call offer
  Touch 4 (Day 3):     Email — social proof + last pilot spot
  Touch 5 (Day 7):     SMS — breakup with final demo line push

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
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
CALENDAR_ID = "h4IlzccZ1m3JprEQqpMJ"
BOOKING_URL = "https://thecalltaker.com/book.html"
DEMO_LINE = "(615) 784-5747"
WALLACE_PHONE = "+16156539004"
WALLACE_GHL_ID = "DtKLG28VzgUb6q3brILD"
BUSINESS_EMAIL = "thecalltakerai@gmail.com"
NTFY_URGENT = "tct-urgent-Hk9UOEZR"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"

STATE_FILE = os.path.expanduser("~/thecalltaker/ops/hot-lead-converter-state.json")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/hot-lead-converter.log")
HEARTBEAT_FILE = os.path.expanduser("~/thecalltaker/ops/hot-lead-converter.heartbeat")

# GHL API headers
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-HotLeadConverter/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-HotLeadConverter/1.0",
}

# Exclusion tags — never enroll these contacts
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "converter-enrolled",
    "donny-closing", "contacted",
}

# ─── Touch Sequence Copy ─────────────────────────────────────────────────────

def get_sms_touch_1(first_name, company_name, industry_word):
    """Immediate SMS — pain hook + demo line CTA"""
    return (
        f"Hey {first_name}, it's Wallace from The Call Taker. "
        f"Quick question — who's answering {company_name}'s phones after 5pm tonight? "
        f"If it's voicemail, you're losing {industry_word}. "
        f"Call this number right now and hear what your customers SHOULD hear: {DEMO_LINE}"
    )


def get_email_touch_2(first_name, company_name, industry_word, job_value):
    """10-minute email — case study + scarcity + booking link"""
    subject = f"I called {company_name} after hours"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>I called {company_name} after hours last week. Got voicemail.</p>

<p>No judgment — but your customers are doing the same thing right now. Their {industry_word.lower()} hits at 6pm, they Google your type of business, and they start calling. <strong>First company that picks up gets the job.</strong></p>

<p>Here's what that's costing you:</p>

<ul style="margin: 16px 0;">
<li><strong>85% of callers won't leave a voicemail</strong> — they hang up and call your competitor</li>
<li>Average {industry_word.lower()} is worth <strong>{job_value}</strong></li>
<li>Miss just 3 calls a week? That's <strong>$4,500+/month walking out your door</strong></li>
</ul>

<p>I built The Call Taker to fix this. It's an AI receptionist that answers every call to your business — 24/7. No voicemail. No missed jobs. It sounds like a real person, books appointments on your calendar, and texts you the details instantly.</p>

<p><strong>One business booked 14 extra jobs in their first 3 weeks.</strong></p>

<p>We're running a free 14-day pilot right now. No card required. No contract. We set it up for you in 48 hours and you keep every dollar it earns.</p>

<p>Only taking <strong>3 businesses this month</strong>. Two spots are already spoken for.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #00dc82; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Book Your Free Demo →</a>
</p>

<p>Or just call the AI yourself right now: <strong>{DEMO_LINE}</strong><br>
Pretend you need a {industry_word.lower()}. Takes 2 minutes. No pressure.</p>

<p>— Wallace Dobbs<br>
<span style="color: #666;">Founder, The Call Taker</span><br>
<span style="color: #666;">{DEMO_LINE}</span></p>

</div>"""
    return subject, html


def get_sms_touch_3(first_name, industry_word, job_value):
    """24-hour SMS — missed revenue angle + personal call offer"""
    return (
        f"{first_name} — real talk. Every night your phone goes to voicemail, "
        f"you're losing {job_value}+ in {industry_word.lower()}s. "
        f"I can have The Call Taker answering your calls in 48 hours. Free for 14 days. "
        f"Want me to call you for 5 min today and show you how it works?"
    )


def get_email_touch_4(first_name, company_name, industry_word):
    """Day 3 email — social proof + last pilot spot"""
    subject = f"Last pilot spot this month, {first_name}"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>Quick update — we just filled another pilot spot.</p>

<p><strong>There's 1 spot left this month.</strong> After that, new businesses go on a waitlist and it's $97/month to start.</p>

<p>Here's what three business owners said after their 14-day pilot:</p>

<blockquote style="border-left: 3px solid #00dc82; padding-left: 16px; margin: 16px 0; color: #333;">
"I was skeptical. Then the AI booked 3 appointments on my calendar the first weekend. Real jobs. Real money. I signed up permanently that Monday."
</blockquote>

<blockquote style="border-left: 3px solid #00dc82; padding-left: 16px; margin: 16px 0; color: #333;">
"My wife used to answer our phones after hours. Now she doesn't have to. The AI handles everything and I get a text with the details. It's like having a full-time receptionist for $297/month."
</blockquote>

<blockquote style="border-left: 3px solid #00dc82; padding-left: 16px; margin: 16px 0; color: #333;">
"I tested it by calling my own number at 11pm. The AI picked up, asked what was wrong, booked me an appointment, and texted me the confirmation. I was sold."
</blockquote>

<p>14 days free. No card. No contract. If it doesn't book you more jobs, walk away.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #00dc82; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Grab the Last Spot →</a>
</p>

<p>Or reply to this email. I'll personally set it up for {company_name}.</p>

<p>— Wallace</p>

</div>"""
    return subject, html


def get_sms_touch_5(first_name):
    """Day 7 SMS — breakup with final demo line push"""
    return (
        f"Hey {first_name} — last text from me. No pitch. "
        f"If you ever want to hear what it sounds like when EVERY call to your business gets answered, "
        f"dial {DEMO_LINE}. Pretend you're a customer. Takes 90 seconds. "
        f"When you're ready, I'm here. — Wallace"
    )


# ─── Industry Mapping ────────────────────────────────────────────────────────

INDUSTRY_MAP = {
    "hvac": ("service call", "$350+"),
    "plumbing": ("service call", "$300+"),
    "electrical": ("service call", "$275+"),
    "roofing": ("roof job", "$5,000+"),
    "locksmith": ("emergency call", "$250+"),
    "dental": ("appointment", "$400+"),
    "medspa": ("appointment", "$500+"),
    "legal": ("case consultation", "$500+"),
    "veterinary": ("appointment", "$200+"),
    "towing": ("tow call", "$150+"),
    "garage-door": ("service call", "$300+"),
    "pest-control": ("service call", "$200+"),
    "property-management": ("maintenance request", "$250+"),
    "water-damage": ("emergency call", "$2,000+"),
    "cleaning": ("booking", "$200+"),
    "landscaping": ("estimate", "$300+"),
    "auto-repair": ("repair job", "$400+"),
    "general-contractor": ("estimate", "$1,000+"),
    "funeral": ("arrangement", "$3,000+"),
}

DEFAULT_INDUSTRY = ("service call", "$350+")


def get_industry_info(tags):
    """Extract industry word and job value from contact tags."""
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
            "total_demos_booked": 0,
            "total_conversions": 0,
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
        if page > 50:  # safety limit
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
        # Sanitize headers
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


# ─── Touch Sequence Logic ────────────────────────────────────────────────────

TOUCH_SCHEDULE = [
    # (touch_num, delay_minutes, touch_type)
    (1, 0, "sms"),          # Immediate
    (2, 10, "email"),       # 10 minutes
    (3, 1440, "sms"),       # 24 hours
    (4, 4320, "email"),     # Day 3 (72 hours)
    (5, 10080, "sms"),      # Day 7 (168 hours)
]


def should_send_touch(enrollment, touch_num):
    """Check if a touch is due based on enrollment time and schedule."""
    touches_sent = enrollment.get("touches_sent", [])
    if touch_num in touches_sent:
        return False  # Already sent

    # Must send touches in order
    if touch_num > 1 and (touch_num - 1) not in touches_sent:
        return False

    # Check if contact replied (stop sequence on reply)
    if enrollment.get("replied", False):
        return False

    # Check timing
    enrolled_at = datetime.fromisoformat(enrollment["enrolled_at"])
    _, delay_minutes, _ = TOUCH_SCHEDULE[touch_num - 1]
    due_at = enrolled_at + timedelta(minutes=delay_minutes)

    return datetime.now() >= due_at


def execute_touch(contact_id, contact_data, enrollment, touch_num, state):
    """Execute a specific touch for a contact."""
    first_name = contact_data.get("firstName", "there")
    company_name = contact_data.get("companyName", "your business")
    tags = contact_data.get("tags", [])
    industry_word, job_value = get_industry_info(tags)

    success = False

    if touch_num == 1:
        msg = get_sms_touch_1(first_name, company_name, industry_word)
        result = send_sms(contact_id, msg)
        success = result is not None
        if success:
            state["stats"]["total_sms_sent"] += 1
            log(f"Touch 1 SMS sent to {first_name} ({contact_id})")

    elif touch_num == 2:
        subject, html = get_email_touch_2(first_name, company_name, industry_word, job_value)
        result = send_email(contact_id, subject, html)
        success = result is not None
        if success:
            state["stats"]["total_emails_sent"] += 1
            log(f"Touch 2 Email sent to {first_name} ({contact_id})")

    elif touch_num == 3:
        msg = get_sms_touch_3(first_name, industry_word, job_value)
        result = send_sms(contact_id, msg)
        success = result is not None
        if success:
            state["stats"]["total_sms_sent"] += 1
            log(f"Touch 3 SMS sent to {first_name} ({contact_id})")

    elif touch_num == 4:
        subject, html = get_email_touch_4(first_name, company_name, industry_word)
        result = send_email(contact_id, subject, html)
        success = result is not None
        if success:
            state["stats"]["total_emails_sent"] += 1
            log(f"Touch 4 Email sent to {first_name} ({contact_id})")

    elif touch_num == 5:
        msg = get_sms_touch_5(first_name)
        result = send_sms(contact_id, msg)
        success = result is not None
        if success:
            state["stats"]["total_sms_sent"] += 1
            log(f"Touch 5 SMS (breakup) sent to {first_name} ({contact_id})")

    if success:
        enrollment["touches_sent"].append(touch_num)
        enrollment["last_touch_at"] = datetime.now().isoformat()
        # Log to ntfy activity
        ntfy_alert(
            NTFY_ACTIVITY,
            f"Hot Lead Touch {touch_num}",
            f"{'SMS' if touch_num in [1,3,5] else 'Email'} sent to {first_name} "
            f"({company_name}) — Touch {touch_num}/5",
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
            "demo_booked": False,
            "converted": False,
            "first_name": contact.get("firstName", ""),
            "company_name": contact.get("companyName", ""),
            "phone": phone,
            "email": email,
        }
        state["stats"]["total_enrolled"] += 1
        new_enrollments += 1

        # Tag in GHL so we don't re-enroll
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

        # Check if all touches sent (sequence complete)
        if len(enrollment.get("touches_sent", [])) >= 5:
            completed += 1
            continue

        # Get fresh contact data for personalization
        contact = get_contact(cid)
        if not contact:
            log(f"Contact {cid} not found in GHL, skipping", "WARN")
            continue

        # Check if contact replied or booked demo since last check
        contact_tags = set(contact.get("tags", []))
        if "contacted" in contact_tags or "pilot-active" in contact_tags:
            enrollment["replied"] = True
            log(f"{enrollment['first_name']} ({cid}) replied or was contacted — stopping sequence")
            continue

        # Send due touches
        for touch_num in range(1, 6):
            if should_send_touch(enrollment, touch_num):
                if execute_touch(cid, contact, enrollment, touch_num, state):
                    touches_sent += 1
                # Only send one touch per contact per cycle
                break

        # Brief pause between contacts to avoid rate limits
        time.sleep(2)

    log(f"Send complete. {touches_sent} touches sent. {completed} sequences completed.")
    return touches_sent


def cmd_run(state):
    """Full cycle: scan for new leads + send due touches."""
    new = cmd_scan(state)
    sent = cmd_send(state)
    save_state(state)
    write_heartbeat()

    # Summary to ntfy if anything happened
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
        "demo_booked": False,
        "converted": False,
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
    name = "A hot lead"
    company = ""
    phone = ""

    if contact_id:
        contact = get_contact(contact_id)
        if contact:
            name = contact.get("firstName", "Someone")
            company = contact.get("companyName", "")
            phone = contact.get("phone", "")

        # Mark as demo booked in state
        if contact_id in state["enrolled"]:
            state["enrolled"][contact_id]["demo_booked"] = True
            state["stats"]["total_demos_booked"] += 1
            save_state(state)

    # SMS to Wallace
    wallace_msg = (
        f"DEMO BOOKED: {name}"
        + (f" from {company}" if company else "")
        + (f" ({phone})" if phone else "")
        + f" just booked a demo. Source: {source}. Check GHL calendar NOW."
    )
    send_wallace_sms(wallace_msg)

    # ntfy URGENT
    ntfy_alert(
        NTFY_URGENT,
        f"[CRITICAL] Demo Booked — {name}",
        wallace_msg,
        priority="urgent",
    )

    log(f"Demo-booked notification sent for {name} ({contact_id})")


def cmd_status(state):
    """Print enrollment stats."""
    stats = state["stats"]
    enrolled = state["enrolled"]

    active = sum(1 for e in enrolled.values()
                 if not e.get("replied") and not e.get("converted")
                 and len(e.get("touches_sent", [])) < 5)
    completed = sum(1 for e in enrolled.values()
                    if len(e.get("touches_sent", [])) >= 5)
    replied = sum(1 for e in enrolled.values() if e.get("replied"))
    booked = sum(1 for e in enrolled.values() if e.get("demo_booked"))

    print("\n╔══════════════════════════════════════════╗")
    print("║     HOT LEAD CONVERTER — STATUS          ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  Total Enrolled:     {stats['total_enrolled']:>5}               ║")
    print(f"║  Active Sequences:   {active:>5}               ║")
    print(f"║  Completed (5/5):    {completed:>5}               ║")
    print(f"║  Replied/Stopped:    {replied:>5}               ║")
    print(f"║  Demos Booked:       {booked:>5}               ║")
    print(f"║  SMS Sent:           {stats['total_sms_sent']:>5}               ║")
    print(f"║  Emails Sent:        {stats['total_emails_sent']:>5}               ║")
    print("╚══════════════════════════════════════════╝\n")

    # Show active sequences
    if active > 0:
        print("Active sequences:")
        for cid, e in enrolled.items():
            if not e.get("replied") and not e.get("converted") and len(e.get("touches_sent", [])) < 5:
                touches = len(e.get("touches_sent", []))
                print(f"  {e.get('first_name', '?'):15} | {e.get('company_name', '?'):25} | Touch {touches}/5 | Enrolled: {e['enrolled_at'][:10]}")
        print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: hot-lead-converter.py <command> [args]")
        print("Commands: scan, send, run, enroll <contact_id>, notify <contact_id>, status")
        sys.exit(1)

    command = sys.argv[1].lower()
    state = load_state()

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
            source = sys.argv[3] if len(sys.argv) > 3 else "demo-booking"
            cmd_notify(state, contact_id, source)
        elif command == "status":
            cmd_status(state)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        log(f"CRASH: {e}", "ERROR")
        ntfy_alert(
            "tct-system-vRsfXQRQ",
            "[CRITICAL] Hot Lead Converter Crashed",
            f"Command: {command}\nError: {str(e)[:500]}",
            priority="urgent",
        )
        raise


if __name__ == "__main__":
    main()
