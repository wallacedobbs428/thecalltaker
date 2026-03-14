#!/usr/bin/env python3
"""
POST-PAYMENT ONBOARDING ENGINE — The Call Taker
================================================
Triggered after Stripe payment. Sends the complete onboarding sequence:
  1. Immediate: Welcome SMS from Jessica + onboarding email
  2. 1 hour: Setup instructions email with forwarding guide
  3. 24 hours: Check-in SMS from Wallace
  4. 48 hours: "You're live!" confirmation + kickoff call invite
  5. Day 7: First week check-in + review request

Commands:
  scan    — Find newly-paid contacts (stripe-paid tag, no onboarding-started tag)
  send    — Send due onboarding touches
  run     — scan + send (full cycle)
  status  — Show onboarding stats

Schedule: Every 30 minutes via launchd
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
CALENDAR_ID = "h4IlzccZ1m3JprEQqpMJ"
BOOKING_URL = "https://thecalltaker.com/book.html"
DEMO_LINE = "(615) 784-5747"
BUSINESS_EMAIL = "thecalltakerai@gmail.com"
NTFY_URGENT = "tct-urgent-Hk9UOEZR"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
WALLACE_GHL_ID = "DtKLG28VzgUb6q3brILD"

STATE_FILE = os.path.expanduser("~/thecalltaker/ops/post-payment-onboarding-state.json")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/post-payment-onboarding.log")
HEARTBEAT_FILE = os.path.expanduser("~/thecalltaker/ops/post-payment-onboarding.heartbeat")

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-Onboarding/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-Onboarding/1.0",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] onboarding: {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"enrollments": {}, "stats": {"total_enrolled": 0, "total_completed": 0}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def write_heartbeat():
    try:
        with open(HEARTBEAT_FILE, "w") as f:
            f.write(datetime.now().isoformat())
    except Exception:
        pass


def ghl_request(method, path, headers=None, params=None, json_body=None):
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    for attempt in range(3):
        try:
            resp = requests.request(method, url, headers=headers, params=params, json=json_body, timeout=30)
            if resp.status_code == 429:
                time.sleep(30)
                continue
            if resp.status_code >= 500:
                time.sleep(5)
                continue
            return resp.json() if resp.text else {}
        except Exception as e:
            log(f"GHL error: {e}", "ERROR")
            time.sleep(5)
    return None


def send_email(contact_id, subject, html_body):
    return ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS, json_body={
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": html_body,
        "emailFrom": f"The Call Taker <{BUSINESS_EMAIL}>",
    })


def send_sms(contact_id, message):
    return ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS, json_body={
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    })


def add_tags(contact_id, tags):
    return ghl_request("POST", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def ntfy(topic, title, body, priority="default"):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        requests.post(f"https://ntfy.sh/{topic}", data=body.encode("utf-8"),
                      headers={"Title": safe_title, "Priority": priority}, timeout=10)
    except Exception:
        pass


# ─── Onboarding Touches ──────────────────────────────────────────────────────

def get_touch_1_sms(first_name, plan_name):
    """Immediate: Welcome SMS from Wallace"""
    return (
        f"{first_name}, welcome to The Call Taker! Your AI receptionist is being set up right now. "
        f"You'll be live within 48 hours. I'm personally handling your setup. "
        f"Questions? Just text me here. — Wallace"
    )


def get_touch_1_email(first_name, company_name, plan_name):
    """Immediate: Welcome + what's next email"""
    return (
        f"Welcome to The Call Taker, {first_name}!",
        f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>You just made the best decision {company_name} has made all year. Your AI receptionist is being built right now.</p>

<p><strong>Here's what happens next:</strong></p>
<ol>
<li><strong>Right now:</strong> I'm configuring your AI receptionist with your business name, hours, and services.</li>
<li><strong>Within 24 hours:</strong> You'll get setup instructions to forward your calls to your AI line.</li>
<li><strong>Within 48 hours:</strong> Your AI receptionist goes live. Every call answered. Zero missed.</li>
</ol>

<p><strong>Your plan:</strong> {plan_name}</p>

<p><strong>What your customers will experience:</strong></p>
<ul>
<li>Instant pickup — no rings, no hold music</li>
<li>Professional greeting customized for {company_name}</li>
<li>Appointment booking and lead capture</li>
<li>Emergency dispatch for urgent calls</li>
<li>Text summary sent to you after every call</li>
</ul>

<p>Questions? Reply to this email or text me at {DEMO_LINE}. I read every message.</p>

<p>Let's make {company_name} the business that never misses a call.</p>

<p>— Wallace Dobbs<br>Founder, The Call Taker</p>

</div>"""
    )


def get_touch_2_email(first_name, company_name):
    """1 hour: Setup instructions"""
    return (
        f"Setup instructions for {company_name}'s AI receptionist",
        f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>Your AI receptionist for {company_name} is almost ready. Here's how to go live:</p>

<p><strong>Step 1: Set Up Call Forwarding</strong></p>
<p>Forward your business line to your new AI number (I'll send this in a follow-up once configuration is done). Most phone systems let you set conditional forwarding — so calls only go to AI when you don't pick up, or after hours.</p>

<p><strong>Step 2: Tell Me Your Business Details</strong></p>
<p>Reply to this email with:</p>
<ul>
<li>Your business hours</li>
<li>Services you offer</li>
<li>How you want emergency calls handled</li>
<li>Any specific instructions (pricing, service areas, etc.)</li>
</ul>

<p><strong>Step 3: Test It</strong></p>
<p>Once live, call your own number. You'll hear your AI receptionist answer as {company_name}. If anything sounds off, I'll adjust it same-day.</p>

<p>Most businesses are fully live within 48 hours of sending me this info.</p>

<p>— Wallace</p>

</div>"""
    )


def get_touch_3_sms(first_name):
    """24h: Check-in SMS"""
    return (
        f"Hey {first_name}, just checking in — did you get the setup instructions I sent? "
        f"Reply with your business hours and services and I'll have your AI receptionist "
        f"configured today. Want to hop on a quick call to walk through it? — Wallace"
    )


def get_touch_4_email(first_name, company_name):
    """48h: You're live + kickoff call invite"""
    return (
        f"{company_name}'s AI receptionist is ready to go live",
        f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p><strong>{company_name}'s AI receptionist is configured and ready to go live.</strong></p>

<p>Let's schedule a 15-minute kickoff call to:</p>
<ul>
<li>Walk through your AI receptionist's settings</li>
<li>Set up call forwarding together</li>
<li>Run a test call so you can hear it live</li>
<li>Answer any questions</li>
</ul>

<p><a href="{BOOKING_URL}" style="display: inline-block; background: #00dc82; color: #000; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 16px;">Book Your Kickoff Call</a></p>

<p>Or just reply "ready" and I'll call you in the next hour.</p>

<p>— Wallace</p>

</div>"""
    )


def get_touch_5_sms(first_name, company_name):
    """Day 7: First week check-in"""
    return (
        f"Hey {first_name}, it's been a week since {company_name} went live with The Call Taker. "
        f"How's everything working? Any calls you want me to review? "
        f"If you're happy with the service, I'd love a quick Google review — it would mean the world. — Wallace"
    )


TOUCH_SEQUENCE = [
    {"id": 1, "delay_minutes": 0, "type": "sms+email", "name": "Welcome"},
    {"id": 2, "delay_minutes": 60, "type": "email", "name": "Setup instructions"},
    {"id": 3, "delay_minutes": 1440, "type": "sms", "name": "24h check-in"},
    {"id": 4, "delay_minutes": 2880, "type": "email", "name": "Go-live + kickoff"},
    {"id": 5, "delay_minutes": 10080, "type": "sms", "name": "Week 1 check-in"},
]


# ─── Core Logic ──────────────────────────────────────────────────────────────

def scan_new_customers():
    """Find contacts with stripe-paid tag but no onboarding-started tag."""
    data = ghl_request("POST", "/contacts/search", json_body={
        "locationId": GHL_LOCATION_ID,
        "filters": [
            {"field": "tags", "operator": "contains", "value": "stripe-paid"},
        ],
        "page": 1,
        "pageLimit": 50,
    })

    if not data or "contacts" not in data:
        log("No contacts found or API error")
        return []

    new_customers = []
    for contact in data.get("contacts", []):
        tags = contact.get("tags", [])
        if "onboarding-started" not in tags and "onboarding-complete" not in tags:
            new_customers.append(contact)

    return new_customers


def enroll_contact(contact, state):
    """Enroll a new paying customer in the onboarding sequence."""
    cid = contact["id"]
    first_name = contact.get("firstName", "there")
    company = contact.get("companyName", "your company")
    email = contact.get("email", "")

    # Determine plan from tags
    tags = contact.get("tags", [])
    if "plan-497" in tags:
        plan_name = "Premium Enterprise ($497/mo)"
    elif "plan-297" in tags:
        plan_name = "Full 24/7 Pro ($297/mo)"
    else:
        plan_name = "After-Hours Starter ($97/mo)"

    state["enrollments"][cid] = {
        "contact_id": cid,
        "first_name": first_name,
        "company": company,
        "email": email,
        "plan": plan_name,
        "enrolled_at": datetime.now().isoformat(),
        "touches_sent": [],
        "completed": False,
    }
    state["stats"]["total_enrolled"] += 1

    # Tag in GHL
    add_tags(cid, ["onboarding-started"])

    log(f"Enrolled {first_name} ({company}) — {plan_name}")
    return True


def send_due_touches(state):
    """Send any touches that are due based on enrollment time."""
    now = datetime.now()
    sent_count = 0

    for cid, enrollment in state["enrollments"].items():
        if enrollment.get("completed"):
            continue

        enrolled_at = datetime.fromisoformat(enrollment["enrolled_at"])
        first_name = enrollment["first_name"]
        company = enrollment["company"]
        plan = enrollment["plan"]
        sent_ids = enrollment.get("touches_sent", [])

        for touch in TOUCH_SEQUENCE:
            if touch["id"] in sent_ids:
                continue

            due_at = enrolled_at + timedelta(minutes=touch["delay_minutes"])
            if now < due_at:
                break  # Not yet due, and sequence is ordered

            # Send this touch
            log(f"Sending touch {touch['id']} ({touch['name']}) to {first_name}")

            if touch["id"] == 1:
                sms_text = get_touch_1_sms(first_name, plan)
                send_sms(cid, sms_text)
                subject, html = get_touch_1_email(first_name, company, plan)
                send_email(cid, subject, html)
            elif touch["id"] == 2:
                subject, html = get_touch_2_email(first_name, company)
                send_email(cid, subject, html)
            elif touch["id"] == 3:
                send_sms(cid, get_touch_3_sms(first_name))
            elif touch["id"] == 4:
                subject, html = get_touch_4_email(first_name, company)
                send_email(cid, subject, html)
            elif touch["id"] == 5:
                send_sms(cid, get_touch_5_sms(first_name, company))

            sent_ids.append(touch["id"])
            enrollment["touches_sent"] = sent_ids
            sent_count += 1

            ntfy(NTFY_ACTIVITY, f"Onboarding touch {touch['id']}",
                 f"{first_name} ({company}) — {touch['name']}")

            time.sleep(3)

        # Check if all touches sent
        if len(sent_ids) >= len(TOUCH_SEQUENCE):
            enrollment["completed"] = True
            state["stats"]["total_completed"] += 1
            add_tags(cid, ["onboarding-complete"])
            log(f"Onboarding complete for {first_name} ({company})")

    return sent_count


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_scan():
    state = load_state()
    customers = scan_new_customers()
    enrolled = 0
    for c in customers:
        if c["id"] not in state["enrollments"]:
            enroll_contact(c, state)
            enrolled += 1
    save_state(state)
    log(f"Scan complete: {enrolled} new customers enrolled")


def cmd_send():
    state = load_state()
    sent = send_due_touches(state)
    save_state(state)
    log(f"Send complete: {sent} touches sent")


def cmd_run():
    cmd_scan()
    cmd_send()
    write_heartbeat()


def cmd_status():
    state = load_state()
    stats = state.get("stats", {})
    enrollments = state.get("enrollments", {})
    active = sum(1 for e in enrollments.values() if not e.get("completed"))
    print(f"\n=== Post-Payment Onboarding Status ===")
    print(f"Total enrolled: {stats.get('total_enrolled', 0)}")
    print(f"Active: {active}")
    print(f"Completed: {stats.get('total_completed', 0)}")
    for cid, e in enrollments.items():
        status = "COMPLETE" if e.get("completed") else f"Touch {len(e.get('touches_sent', []))}/5"
        print(f"  {e['first_name']} ({e['company']}) — {status}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: post-payment-onboarding.py <scan|send|run|status>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "scan":
        cmd_scan()
    elif cmd == "send":
        cmd_send()
    elif cmd == "run":
        cmd_run()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
