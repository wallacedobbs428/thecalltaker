#!/usr/bin/env python3
"""
PAYMENT REMINDER ENGINE — The Call Taker
=========================================
Sends follow-up to demo-booked leads who don't convert within 48 hours.

Logic:
  - Monitors contacts tagged 'demo-booked' or 'demo-completed'
  - If no 'customer' or 'pilot-active' tag after 48 hours → send reminder
  - Touch 1 (48 hours): SMS — pilot offer reminder
  - Touch 2 (96 hours): Email — scarcity + ROI breakdown
  - Touch 3 (168 hours / Day 7): SMS — final breakup

Commands:
  run     — Check all demo'd leads, send due reminders
  status  — Show stats

Schedule: 2x daily via launchd (9am, 5pm)
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
BUSINESS_EMAIL = "thecalltakerai@gmail.com"
BOOKING_URL = "https://thecalltaker.com/book.html"
DEMO_LINE = "(615) 784-5747"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"

STATE_FILE = os.path.expanduser("~/thecalltaker/ops/payment-reminder-state.json")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/payment-reminder.log")

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}", "Version": "2021-07-28",
    "Content-Type": "application/json", "Accept": "application/json",
    "User-Agent": "TheCallTaker-PaymentReminder/1.0",
}
CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}", "Version": "2021-04-15",
    "Content-Type": "application/json", "Accept": "application/json",
    "User-Agent": "TheCallTaker-PaymentReminder/1.0",
}

CONVERTED_TAGS = {"customer", "active-client", "pilot-active", "pilot-converted", "stripe-paid"}
DEMO_TAGS = {"demo-booked", "demo-completed", "engaged-demo", "hot-demo"}


def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] payment-reminder: {msg}"
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
    return {"tracked": {}, "stats": {"total_reminders": 0, "total_runs": 0}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


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
        except Exception:
            time.sleep(5)
    return None


def send_sms(contact_id, message):
    return ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS, json_body={
        "type": "SMS", "contactId": contact_id, "message": message,
    })


def send_email(contact_id, subject, html):
    return ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS, json_body={
        "type": "Email", "contactId": contact_id, "subject": subject, "html": html,
        "emailFrom": f"Wallace Dobbs <{BUSINESS_EMAIL}>",
    })


# ─── Reminder Copy ───────────────────────────────────────────────────────────

def reminder_sms_48h(first_name):
    return (
        f"Hey {first_name}, it's Wallace. Great demo the other day. "
        f"Quick reminder — we've got 1 pilot spot left this month. "
        f"14 days free, no card, no contract. "
        f"Want me to set it up for you today? Just reply YES."
    )


def reminder_email_96h(first_name, company):
    subject = f"{first_name}, your pilot spot is still open"
    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>Just checking in after your demo. I held a pilot spot for {company}.</p>

<p>Here's the math that keeps me up at night:</p>

<table style="border-collapse: collapse; margin: 16px 0; width: 100%;">
<tr style="background: #f5f5f5;"><td style="padding: 12px; border: 1px solid #ddd;"><strong>Missed calls/week</strong></td><td style="padding: 12px; border: 1px solid #ddd; text-align: center;">3-5</td></tr>
<tr><td style="padding: 12px; border: 1px solid #ddd;"><strong>Avg job value</strong></td><td style="padding: 12px; border: 1px solid #ddd; text-align: center;">$350+</td></tr>
<tr style="background: #f5f5f5;"><td style="padding: 12px; border: 1px solid #ddd;"><strong>Monthly cost of missed calls</strong></td><td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #dc2626;"><strong>$4,200 - $7,000</strong></td></tr>
<tr><td style="padding: 12px; border: 1px solid #ddd;"><strong>The Call Taker</strong></td><td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #16a34a;"><strong>$97/month</strong></td></tr>
</table>

<p>That's a <strong>43x-72x return</strong> on a $97 investment. And the pilot is free.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #F97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Claim Your Free Pilot →</a>
</p>

<p>I'm holding this spot until end of day tomorrow. After that, I'll give it to the next business in line.</p>

<p>— Wallace</p>

</div>"""
    return subject, html


def reminder_sms_7d(first_name):
    return (
        f"Last message from me {first_name}. Your pilot spot expired. "
        f"If you change your mind, The Call Taker starts at $97/mo — less than one missed job. "
        f"Hear it yourself anytime: {DEMO_LINE}. — Wallace"
    )


# ─── Main Logic ──────────────────────────────────────────────────────────────

def cmd_run(state):
    log("=== Payment Reminder Engine ===")
    state["stats"]["total_runs"] += 1

    # Find demo'd contacts
    all_contacts = []
    page = 1
    while True:
        data = ghl_request("GET", "/contacts/", params={
            "locationId": GHL_LOCATION_ID, "limit": 100, "page": page,
        })
        if not data or "contacts" not in data:
            break
        all_contacts.extend(data["contacts"])
        if len(data["contacts"]) < 100:
            break
        page += 1
        if page > 50:
            break

    reminders_sent = 0

    for contact in all_contacts:
        cid = contact.get("id")
        if not cid:
            continue
        tags = set(t.lower() for t in contact.get("tags", []))

        # Skip if not a demo lead
        if not (tags & DEMO_TAGS):
            continue

        # Skip if already converted
        if tags & CONVERTED_TAGS:
            if cid in state["tracked"]:
                state["tracked"][cid]["converted"] = True
            continue

        # Skip if no phone
        if not contact.get("phone"):
            continue

        # Track this contact
        if cid not in state["tracked"]:
            state["tracked"][cid] = {
                "first_seen": datetime.now().isoformat(),
                "touches_sent": [],
                "converted": False,
            }

        tracked = state["tracked"][cid]
        if tracked.get("converted"):
            continue

        first_seen = datetime.fromisoformat(tracked["first_seen"])
        hours_since = (datetime.now() - first_seen).total_seconds() / 3600
        touches = tracked.get("touches_sent", [])
        first_name = contact.get("firstName", "there")
        company = contact.get("companyName", "your business")

        # Touch 1: 48 hours
        if hours_since >= 48 and 1 not in touches:
            msg = reminder_sms_48h(first_name)
            if send_sms(cid, msg):
                touches.append(1)
                reminders_sent += 1
                log(f"  48h reminder SMS to {first_name} ({company})")

        # Touch 2: 96 hours
        elif hours_since >= 96 and 2 not in touches and 1 in touches:
            subject, html = reminder_email_96h(first_name, company)
            if send_email(cid, subject, html):
                touches.append(2)
                reminders_sent += 1
                log(f"  96h reminder email to {first_name} ({company})")

        # Touch 3: 168 hours (Day 7)
        elif hours_since >= 168 and 3 not in touches and 2 in touches:
            msg = reminder_sms_7d(first_name)
            if send_sms(cid, msg):
                touches.append(3)
                reminders_sent += 1
                log(f"  7d breakup SMS to {first_name} ({company})")

        tracked["touches_sent"] = touches
        time.sleep(3)

    state["stats"]["total_reminders"] += reminders_sent
    log(f"Done. {reminders_sent} reminders sent.")
    save_state(state)


def cmd_status(state):
    stats = state["stats"]
    tracked = state["tracked"]
    active = sum(1 for t in tracked.values() if not t.get("converted") and len(t.get("touches_sent", [])) < 3)
    converted = sum(1 for t in tracked.values() if t.get("converted"))

    print(f"\nPayment Reminder: {stats.get('total_reminders', 0)} sent | "
          f"Active: {active} | Converted: {converted} | Runs: {stats.get('total_runs', 0)}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: payment-reminder-engine.py <run|status>")
        sys.exit(1)

    state = load_state()
    cmd = sys.argv[1].lower()
    if cmd == "run":
        cmd_run(state)
    elif cmd == "status":
        cmd_status(state)
    else:
        print(f"Unknown: {cmd}")
