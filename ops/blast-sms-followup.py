#!/usr/bin/env python3
"""
BLAST SMS FOLLOW-UP — The Call Taker
=====================================
Sends SMS follow-up 24h after cold email blast to contacts who haven't replied.

Logic:
  - Reads blast-engine-state.json for sent emails
  - For contacts emailed 24+ hours ago with no reply/conversion tags
  - Sends a short SMS nudge with demo line
  - One SMS per contact, tracks in own state

Commands:
  run     — Check all emailed leads, send due SMS follow-ups
  status  — Show stats

Schedule: Daily via launchd (11am — 24h after morning blast)
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
DEMO_LINE = "(615) 784-5747"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"

BLAST_STATE_FILE = os.path.expanduser("~/thecalltaker/ops/blast-engine-state.json")
STATE_FILE = os.path.expanduser("~/thecalltaker/ops/blast-sms-followup-state.json")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/blast-sms-followup.log")

MAX_SMS_PER_RUN = 25
FOLLOWUP_DELAY_HOURS = 24

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}", "Version": "2021-04-15",
    "Content-Type": "application/json", "Accept": "application/json",
    "User-Agent": "TheCallTaker-BlastSMSFollowup/1.0",
}
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}", "Version": "2021-07-28",
    "Content-Type": "application/json", "Accept": "application/json",
    "User-Agent": "TheCallTaker-BlastSMSFollowup/1.0",
}

CONVERTED_TAGS = {"customer", "active-client", "pilot-active", "pilot-converted",
                  "contacted", "hot-lead", "demo-booked", "do-not-contact", "unsubscribed"}

INDUSTRY_MAP = {
    "hvac": "AC repair", "plumbing": "plumbing job", "electrical": "electrical call",
    "roofing": "roof job", "locksmith": "lockout", "dental": "appointment",
    "legal": "consultation", "towing": "tow call", "veterinary": "vet visit",
    "medspa": "appointment", "pest-control": "service call", "garage-door": "repair",
    "property-management": "maintenance call", "water-damage": "emergency call",
    "cleaning": "booking", "landscaping": "estimate", "auto-repair": "repair",
    "general-contractor": "project", "funeral": "arrangement",
}


def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] blast-sms-followup: {msg}"
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
    return {"followed_up": {}, "stats": {"total_sms": 0, "total_runs": 0}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def load_blast_state():
    if os.path.exists(BLAST_STATE_FILE):
        try:
            with open(BLAST_STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


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


def followup_sms(first_name, company):
    return (
        f"Hey {first_name}, shot you an email about {company}'s after-hours calls. "
        f"Quick test — call {DEMO_LINE} and pretend you're a customer at 9pm tonight. "
        f"That's what your callers should hear instead of voicemail. 90 seconds. — Wallace"
    )


def cmd_run(state):
    log("=== Blast SMS Follow-Up Engine ===")
    state["stats"]["total_runs"] += 1

    blast_state = load_blast_state()
    sent_emails = blast_state.get("sent", {})

    if not sent_emails:
        log("No blast emails found in state. Nothing to follow up.")
        save_state(state)
        return

    now = datetime.now()
    sms_count = 0

    for email, info in sent_emails.items():
        if sms_count >= MAX_SMS_PER_RUN:
            break

        contact_id = info.get("contact_id")
        if not contact_id:
            continue

        # Skip if already followed up
        if contact_id in state["followed_up"]:
            continue

        # Check if 24+ hours since email
        sent_at = info.get("sent_at", "")
        if not sent_at:
            continue
        try:
            email_time = datetime.fromisoformat(sent_at)
        except ValueError:
            continue
        if (now - email_time).total_seconds() < FOLLOWUP_DELAY_HOURS * 3600:
            continue

        # Get fresh contact data to check tags
        data = ghl_request("GET", f"/contacts/{contact_id}")
        if not data or "contact" not in data:
            continue
        contact = data["contact"]
        tags = set(t.lower() for t in contact.get("tags", []))

        # Skip if replied or converted
        if tags & CONVERTED_TAGS:
            state["followed_up"][contact_id] = {"skipped": True, "reason": "converted"}
            continue

        # Skip if no phone
        if not contact.get("phone"):
            state["followed_up"][contact_id] = {"skipped": True, "reason": "no_phone"}
            continue

        first_name = contact.get("firstName", "there")
        company = info.get("company", contact.get("companyName", "your business"))

        msg = followup_sms(first_name, company)
        result = send_sms(contact_id, msg)
        if result:
            state["followed_up"][contact_id] = {
                "sent_at": now.isoformat(),
                "company": company,
            }
            state["stats"]["total_sms"] += 1
            sms_count += 1
            log(f"  SMS follow-up to {first_name} ({company})")

        time.sleep(5)

    log(f"Done. {sms_count} follow-up SMS sent.")
    save_state(state)


def cmd_status(state):
    stats = state["stats"]
    followed = state["followed_up"]
    sent = sum(1 for v in followed.values() if not v.get("skipped"))
    skipped = sum(1 for v in followed.values() if v.get("skipped"))

    print(f"\nBlast SMS Follow-Up: {stats.get('total_sms', 0)} sent | "
          f"Skipped: {skipped} | Runs: {stats.get('total_runs', 0)}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: blast-sms-followup.py <run|status>")
        sys.exit(1)

    state = load_state()
    cmd = sys.argv[1].lower()
    if cmd == "run":
        cmd_run(state)
    elif cmd == "status":
        cmd_status(state)
    else:
        print(f"Unknown: {cmd}")
