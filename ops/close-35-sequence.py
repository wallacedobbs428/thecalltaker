#!/usr/bin/env python3
"""
CLOSE-35 SEQUENCE — The Call Taker
===================================
3-touch close sequence for the 35 hot leads already in GHL.
This is NOT a nurture. This is a CLOSE.

Touches:
  Touch 1 (Day 0): Personalized email — industry-specific, demo line CTA + book call
  Touch 2 (Day 2): SMS — direct, urgency-based, reply Y for callback
  Touch 3 (Day 5): Final email — "closing your file" framing, last CTA

Commands:
  scan     — Find hot-lead contacts not yet enrolled in close-35
  send     — Send due touches for enrolled contacts
  run      — scan + send (full cycle)
  status   — Show enrollment stats
  preview  — Preview all 3 touches for a sample contact (dry run)

Deploy: python3 ops/close-35-sequence.py run
Schedule: Run 2x daily (9am, 2pm) via launchd or manually
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────
GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
DEMO_LINE = "(615) 784-5747"
BOOKING_URL = "https://thecalltaker.com/book.html"
CHECKOUT_URL = "https://thecalltaker.com/checkout.html"
PILOT_URL = "https://thecalltaker.com/pilot/"
BUSINESS_EMAIL = "thecalltakerai@gmail.com"
WALLACE_PHONE = "+16156539004"
NTFY_URGENT = "tct-urgent-Hk9UOEZR"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "close-35-state.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "close-35.log")

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-Close35/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-Close35/1.0",
}

# Tags that mean the contact is already handled — don't enroll
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "close-35-enrolled",
    "paid", "donny-closing",
}

# Industry → pain-specific copy
INDUSTRY_MAP = {
    "hvac": {"word": "service call", "value": "$350-$1,200", "pain": "AC breaks at 2am, customer calls — voicemail. They call your competitor. $800 job gone."},
    "plumbing": {"word": "service call", "value": "$400-$1,500", "pain": "Pipe bursts Friday night, homeowner calls — voicemail. They find someone else. $600 job gone."},
    "electrical": {"word": "service call", "value": "$300-$900", "pain": "Power out in a storm, homeowner calls — voicemail. Next electrician on Google gets the job."},
    "roofing": {"word": "estimate", "value": "$5,000-$15,000", "pain": "Hail damage, homeowner calls 3 roofers. You go to voicemail. The one who picks up gets a $12,000 job."},
    "dental": {"word": "appointment", "value": "$200-$800", "pain": "Patient calls at lunch to book a cleaning. Voicemail. They book with the dentist down the street."},
    "legal": {"word": "consultation", "value": "$500-$5,000", "pain": "Someone gets in a car accident, calls your firm at 6pm. Voicemail. They call the next attorney on Google."},
    "medspa": {"word": "appointment", "value": "$300-$2,000", "pain": "Client wants to book Botox before a wedding. Calls after 5pm. Voicemail. They book elsewhere."},
    "locksmith": {"word": "service call", "value": "$150-$400", "pain": "Locked out at midnight. Calls you — voicemail. Calls your competitor. $250 job, gone in 10 seconds."},
    "property-mgmt": {"word": "maintenance call", "value": "$200-$600", "pain": "Tenant has a burst pipe at 11pm. Calls the office — voicemail. Now it's a $5,000 water damage claim."},
    "towing": {"word": "tow call", "value": "$150-$500", "pain": "Stranded on the highway at midnight. Calls you — voicemail. Next tow company gets $200."},
    "veterinary": {"word": "appointment", "value": "$200-$1,000", "pain": "Dog ate something toxic at 9pm. Owner calls your clinic — voicemail. They drive to the emergency vet."},
    "garage-door": {"word": "service call", "value": "$200-$600", "pain": "Garage door won't close at 10pm. They feel unsafe. Call you — voicemail. Call your competitor."},
    "pest-control": {"word": "service call", "value": "$200-$500", "pain": "Termites found during a home inspection. Buyer calls for emergency treatment. Voicemail. Job gone."},
    "auto-repair": {"word": "appointment", "value": "$300-$1,200", "pain": "Car breaks down, customer calls your shop. Voicemail. They find another mechanic on Google."},
    "cleaning": {"word": "booking", "value": "$150-$400", "pain": "Homeowner needs move-out cleaning this weekend. Calls — voicemail. Books someone else."},
    "landscaping": {"word": "estimate", "value": "$500-$3,000", "pain": "New homeowner wants full yard design. Calls 3 companies. You go to voicemail. Job gone."},
    "funeral": {"word": "arrangement", "value": "$5,000-$12,000", "pain": "Family loses a loved one at 3am. Calls your funeral home. Voicemail. They call the one that answers."},
}

DEFAULT_INDUSTRY = {"word": "service call", "value": "$300-$1,000", "pain": "Customer calls after hours — voicemail. They call the next business on Google. Job gone."}


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"enrolled": {}, "stats": {"enrolled": 0, "touch1_sent": 0, "touch2_sent": 0, "touch3_sent": 0}}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def ntfy(topic, title, body, priority="default", tags=""):
    try:
        headers = {"Title": title[:255], "Priority": priority}
        if tags:
            headers["Tags"] = tags
        requests.post(f"https://ntfy.sh/{topic}", data=body.encode("utf-8"), headers=headers, timeout=10)
    except Exception as e:
        log(f"ntfy error: {e}")


def get_industry_data(contact):
    """Extract industry from contact tags and return industry copy data."""
    tags = contact.get("tags", [])
    if not tags:
        return DEFAULT_INDUSTRY
    for tag in tags:
        if tag.startswith("industry-"):
            key = tag.replace("industry-", "")
            return INDUSTRY_MAP.get(key, DEFAULT_INDUSTRY)
    return DEFAULT_INDUSTRY


def get_name(contact):
    first = (contact.get("firstName") or "").strip()
    return first if first else "there"


def get_company(contact):
    return (contact.get("companyName") or "your business").strip()


# ─── GHL API ──────────────────────────────────────────────────────────────

def ghl_get(endpoint, headers=None, params=None):
    """GET request with retry."""
    h = headers or CONTACTS_HEADERS
    for attempt in range(3):
        try:
            r = requests.get(f"{GHL_BASE_URL}{endpoint}", headers=h, params=params, timeout=30)
            if r.status_code == 429:
                time.sleep(30)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                log(f"GHL GET failed: {endpoint} — {e}")
                return None
    return None


def ghl_post(endpoint, data, headers=None):
    """POST request with retry."""
    h = headers or CONTACTS_HEADERS
    for attempt in range(3):
        try:
            r = requests.post(f"{GHL_BASE_URL}{endpoint}", headers=h, json=data, timeout=30)
            if r.status_code == 429:
                time.sleep(30)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                log(f"GHL POST failed: {endpoint} — {e}")
                return None
    return None


def ghl_put(endpoint, data, headers=None):
    """PUT request with retry."""
    h = headers or CONTACTS_HEADERS
    for attempt in range(3):
        try:
            r = requests.put(f"{GHL_BASE_URL}{endpoint}", headers=h, json=data, timeout=30)
            if r.status_code == 429:
                time.sleep(30)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                log(f"GHL PUT failed: {endpoint} — {e}")
                return None
    return None


def send_email(contact_id, subject, html_body):
    """Send email via GHL conversations API."""
    data = {
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": html_body,
        "emailFrom": f"Wallace Dobbs <{BUSINESS_EMAIL}>",
    }
    return ghl_post("/conversations/messages", data, CONVERSATIONS_HEADERS)


def send_sms(contact_id, message):
    """Send SMS via GHL conversations API."""
    data = {
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    }
    return ghl_post("/conversations/messages", data, CONVERSATIONS_HEADERS)


def add_tags(contact_id, tags):
    """Add tags to a GHL contact."""
    return ghl_put(f"/contacts/{contact_id}", {"tags": tags})


# ─── Touch Copy ───────────────────────────────────────────────────────────

def touch_1_email(contact):
    """Day 0: Personalized email — industry-specific, demo line CTA + book call."""
    first = get_name(contact)
    company = get_company(contact)
    ind = get_industry_data(contact)

    subject = f"{company} — the call you missed last night"

    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #1a1a1a; max-width: 580px; line-height: 1.7; font-size: 15px;">

<p>{first},</p>

<p>{ind['pain']}</p>

<p>That's happening to {company} right now. Every night. Every weekend. Every holiday.</p>

<p>I built an AI receptionist that answers your calls 24/7. It sounds like a real person, books appointments on your calendar, handles emergencies, and texts you every detail. <strong>Your customers never hit voicemail again.</strong></p>

<p style="margin: 20px 0; padding: 16px; background: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 4px;">
<strong>Call it yourself right now: <a href="tel:+16157845747" style="color: #16a34a;">{DEMO_LINE}</a></strong><br>
Pretend you need a {ind['word']}. It picks up instantly. Takes 60 seconds.
</p>

<p>Here's what I'm offering {company}:</p>

<ul style="margin: 12px 0; padding-left: 20px;">
<li><strong>14-day free pilot</strong> — no card, no contract, no risk</li>
<li><strong>Custom AI trained on your business</strong> — your services, your hours, your pricing</li>
<li><strong>Live in 48 hours</strong> — just forward your calls and start catching leads</li>
<li><strong>Starts at $97/month</strong> — less than one missed {ind['word']}</li>
</ul>

<p>I'm only taking <strong>3 businesses this month</strong>. Want one of the spots?</p>

<p style="margin: 24px 0;">
<a href="{PILOT_URL}" style="background: #22c55e; color: #fff; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 16px; display: inline-block;">Start your free pilot</a>
&nbsp;&nbsp;or&nbsp;&nbsp;
<a href="{BOOKING_URL}" style="color: #22c55e; font-weight: 600; text-decoration: underline;">book a 15-min call with me</a>
</p>

<p>— Wallace Dobbs<br>
<span style="color: #666;">Founder, The Call Taker | {DEMO_LINE}</span></p>

</div>"""

    return subject, html


def touch_2_sms(contact):
    """Day 2: SMS — short, direct, urgency-based, reply Y for callback."""
    first = get_name(contact)
    company = get_company(contact)
    ind = get_industry_data(contact)

    return (
        f"Hey {first} — Wallace from The Call Taker. "
        f"Quick question: how many calls did {company} miss this week after hours? "
        f"I can have an AI answering your phone in 48 hours. Free for 14 days. "
        f"Reply Y and I'll call you today to set it up."
    )


def touch_3_email(contact):
    """Day 5: Final email — closing your file, last CTA."""
    first = get_name(contact)
    company = get_company(contact)
    ind = get_industry_data(contact)

    subject = f"Closing your file, {first}"

    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #1a1a1a; max-width: 580px; line-height: 1.7; font-size: 15px;">

<p>{first},</p>

<p>I've reached out a couple times about setting up an AI receptionist for {company}. Haven't heard back, so I'm going to close your file.</p>

<p>No hard feelings — I know you're busy running a business.</p>

<p>But before I do, I want to leave you with one number:</p>

<p style="font-size: 28px; font-weight: 800; color: #22c55e; margin: 20px 0; text-align: center;">
{ind['value']}
</p>

<p style="text-align: center; color: #666; margin-top: -12px; margin-bottom: 20px;">
That's what one missed {ind['word']} costs {company}.
</p>

<p>If you ever want to stop losing those calls to voicemail, two ways to reach me:</p>

<ol style="margin: 12px 0; padding-left: 20px;">
<li><strong>Call the AI yourself:</strong> <a href="tel:+16157845747" style="color: #22c55e;">{DEMO_LINE}</a> — it picks up instantly, 24/7</li>
<li><strong>Start your free pilot:</strong> <a href="{PILOT_URL}" style="color: #22c55e;">{PILOT_URL}</a> — takes 60 seconds</li>
</ol>

<p>The offer stands: 14 days free, no card, no contract. $97/month after if you want to keep it.</p>

<p>Good luck with everything, {first}. I hope {company} catches every call.</p>

<p>— Wallace<br>
<span style="color: #666;">{DEMO_LINE}</span></p>

</div>"""

    return subject, html


# ─── Core Commands ────────────────────────────────────────────────────────

def cmd_scan():
    """Find hot-lead contacts not yet enrolled in close-35."""
    state = load_state()
    enrolled_ids = set(state["enrolled"].keys())

    log("Scanning for hot-lead contacts...")

    # Search for contacts with hot-lead tag
    contacts = []
    page = 1
    while True:
        params = {"locationId": GHL_LOCATION_ID, "query": "hot-lead", "limit": 100, "page": page}
        data = ghl_get("/contacts/", params=params)
        if not data or "contacts" not in data:
            break
        batch = data["contacts"]
        if not batch:
            break
        contacts.extend(batch)
        page += 1
        if len(batch) < 100:
            break

    log(f"Found {len(contacts)} contacts with hot-lead related matches")

    new_enrolled = 0
    for contact in contacts:
        cid = contact.get("id", "")
        tags = set(contact.get("tags", []))

        # Must have hot-lead tag
        if "hot-lead" not in tags:
            continue

        # Skip already enrolled
        if cid in enrolled_ids:
            continue

        # Skip excluded contacts
        if tags & EXCLUDE_TAGS:
            log(f"  Skipping {contact.get('firstName', '?')} — excluded tag: {tags & EXCLUDE_TAGS}")
            continue

        # Skip contacts without email (needed for touch 1 and 3)
        email = contact.get("email", "")
        if not email:
            log(f"  Skipping {contact.get('firstName', '?')} — no email")
            continue

        # Enroll
        first = get_name(contact)
        company = get_company(contact)
        state["enrolled"][cid] = {
            "enrolled_at": datetime.now().isoformat(),
            "first": first,
            "company": company,
            "email": email,
            "phone": contact.get("phone", ""),
            "tags": list(tags),
            "touches_sent": [],
            "next_touch": 1,
        }
        state["stats"]["enrolled"] += 1
        new_enrolled += 1

        # Tag in GHL
        add_tags(cid, list(tags | {"close-35-enrolled"}))

        log(f"  Enrolled: {first} @ {company} ({email})")

    save_state(state)
    log(f"Scan complete. {new_enrolled} new contacts enrolled. Total: {len(state['enrolled'])}")

    if new_enrolled > 0:
        ntfy(NTFY_ACTIVITY, f"Close-35: {new_enrolled} new leads enrolled",
             f"Total enrolled: {len(state['enrolled'])}. Run 'send' to fire Touch 1.",
             tags="target")

    return new_enrolled


def cmd_send():
    """Send due touches for enrolled contacts."""
    state = load_state()
    now = datetime.now()
    sent_count = 0

    for cid, enrollment in list(state["enrolled"].items()):
        next_touch = enrollment.get("next_touch", 1)
        enrolled_at = datetime.fromisoformat(enrollment["enrolled_at"])

        if next_touch > 3:
            continue  # Sequence complete

        # Calculate when each touch is due
        if next_touch == 1:
            due_at = enrolled_at  # Immediate
        elif next_touch == 2:
            due_at = enrolled_at + timedelta(days=2)
        elif next_touch == 3:
            due_at = enrolled_at + timedelta(days=5)
        else:
            continue

        if now < due_at:
            continue  # Not due yet

        # Fetch fresh contact data for personalization
        contact_data = ghl_get(f"/contacts/{cid}")
        if not contact_data or "contact" not in contact_data:
            log(f"  Could not fetch contact {cid}, skipping")
            continue
        contact = contact_data["contact"]

        # Check if contact has been converted since enrollment
        current_tags = set(contact.get("tags", []))
        if current_tags & {"customer", "paid", "pilot-active", "pilot-converted", "do-not-contact", "unsubscribed"}:
            log(f"  {enrollment['first']} converted or opted out — removing from sequence")
            enrollment["next_touch"] = 99
            save_state(state)
            continue

        first = get_name(contact)
        company = get_company(contact)

        # Send the touch
        if next_touch == 1:
            subject, html = touch_1_email(contact)
            result = send_email(cid, subject, html)
            if result:
                log(f"  Touch 1 (email) sent to {first} @ {company}")
                enrollment["touches_sent"].append({"touch": 1, "type": "email", "sent_at": now.isoformat()})
                enrollment["next_touch"] = 2
                state["stats"]["touch1_sent"] += 1
                sent_count += 1
            else:
                log(f"  Touch 1 FAILED for {first} @ {company}")

        elif next_touch == 2:
            phone = contact.get("phone", "")
            if not phone:
                log(f"  {first} has no phone — skipping Touch 2 (SMS), advancing to Touch 3")
                enrollment["next_touch"] = 3
                save_state(state)
                continue

            sms_text = touch_2_sms(contact)
            result = send_sms(cid, sms_text)
            if result:
                log(f"  Touch 2 (SMS) sent to {first} @ {company}")
                enrollment["touches_sent"].append({"touch": 2, "type": "sms", "sent_at": now.isoformat()})
                enrollment["next_touch"] = 3
                state["stats"]["touch2_sent"] += 1
                sent_count += 1
            else:
                log(f"  Touch 2 FAILED for {first} @ {company}")

        elif next_touch == 3:
            subject, html = touch_3_email(contact)
            result = send_email(cid, subject, html)
            if result:
                log(f"  Touch 3 (email) sent to {first} @ {company}")
                enrollment["touches_sent"].append({"touch": 3, "type": "email", "sent_at": now.isoformat()})
                enrollment["next_touch"] = 4  # Sequence complete
                state["stats"]["touch3_sent"] += 1
                sent_count += 1

                # Tag as sequence complete
                add_tags(cid, list(current_tags | {"close-35-complete"}))
            else:
                log(f"  Touch 3 FAILED for {first} @ {company}")

        save_state(state)
        time.sleep(2)  # Rate limiting between sends

    log(f"Send complete. {sent_count} touches sent this run.")

    if sent_count > 0:
        ntfy(NTFY_ACTIVITY, f"Close-35: {sent_count} touches sent",
             f"T1: {state['stats']['touch1_sent']} | T2: {state['stats']['touch2_sent']} | T3: {state['stats']['touch3_sent']}",
             tags="outbox_tray")

    return sent_count


def cmd_run():
    """Full cycle: scan + send."""
    log("═══ Close-35 Sequence — Full Run ═══")
    new = cmd_scan()
    sent = cmd_send()
    log(f"═══ Done. {new} enrolled, {sent} sent ═══")


def cmd_status():
    """Show enrollment stats."""
    state = load_state()
    total = len(state["enrolled"])
    pending = sum(1 for e in state["enrolled"].values() if e.get("next_touch", 1) <= 3)
    complete = sum(1 for e in state["enrolled"].values() if e.get("next_touch", 1) > 3)

    print(f"\n  Close-35 Sequence Status")
    print(f"  ========================")
    print(f"  Total enrolled:  {total}")
    print(f"  Pending:         {pending}")
    print(f"  Complete:        {complete}")
    print(f"  Touch 1 sent:    {state['stats']['touch1_sent']}")
    print(f"  Touch 2 sent:    {state['stats']['touch2_sent']}")
    print(f"  Touch 3 sent:    {state['stats']['touch3_sent']}")
    print()

    if pending > 0:
        print("  Pending contacts:")
        for cid, e in state["enrolled"].items():
            if e.get("next_touch", 1) <= 3:
                print(f"    - {e['first']} @ {e['company']} — next: Touch {e['next_touch']}")
        print()


def cmd_preview():
    """Preview all 3 touches with sample data."""
    sample = {
        "firstName": "Mike",
        "companyName": "Nashville Plumbing Co",
        "email": "mike@example.com",
        "phone": "+16155551234",
        "tags": ["hot-lead", "industry-plumbing"],
    }

    print("\n═══ TOUCH 1: Email (Day 0) ═══")
    subject, html = touch_1_email(sample)
    print(f"Subject: {subject}")
    print(f"Body preview (first 500 chars):\n{html[:500]}...")

    print("\n═══ TOUCH 2: SMS (Day 2) ═══")
    sms = touch_2_sms(sample)
    print(f"Message ({len(sms)} chars): {sms}")

    print("\n═══ TOUCH 3: Email (Day 5) ═══")
    subject, html = touch_3_email(sample)
    print(f"Subject: {subject}")
    print(f"Body preview (first 500 chars):\n{html[:500]}...")
    print()


# ─── Main ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 close-35-sequence.py [scan|send|run|status|preview]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    try:
        if cmd == "scan":
            cmd_scan()
        elif cmd == "send":
            cmd_send()
        elif cmd == "run":
            cmd_run()
        elif cmd == "status":
            cmd_status()
        elif cmd == "preview":
            cmd_preview()
        else:
            print(f"Unknown command: {cmd}")
            print("Commands: scan, send, run, status, preview")
            sys.exit(1)
    except Exception as e:
        log(f"CRASH: {e}")
        ntfy(NTFY_URGENT, "[CRITICAL] Close-35 CRASHED", f"Error: {e}", priority="urgent", tags="rotating_light")
        raise
