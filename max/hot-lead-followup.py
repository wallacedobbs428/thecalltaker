#!/usr/bin/env python3
"""
HOT LEAD FOLLOW-UP ENGINE — SMS Drip for Warm Prospects
Mar 12, 2026

Enrolls hot leads from GHL into a multi-day SMS follow-up sequence.
Fires Day 0 SMS immediately on enrollment, then follows up on schedule.

Targets contacts tagged: hot-lead, warm-demo-prospect, bland-interested
Skips contacts tagged: customer, pilot-active, dnc, opted-out, do-not-contact

Zero external dependencies — stdlib only.

Usage:
  python3 hot-lead-followup.py enroll   # Enroll hot leads + fire Day 0 SMS
  python3 hot-lead-followup.py run      # Process due follow-ups (run every 4 hours)
  python3 hot-lead-followup.py status   # Print dashboard
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ===================================================
# CONFIG
# ===================================================

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

NTFY_OPS_TOPIC = "tct-sales-63uYsIT9"
NTFY_WAR_TOPIC = "tct-urgent-Hk9UOEZR"
NTFY_CALLS_TOPIC = "tct-finishtask"

DEMO_LINE = "(615) 784-5747"
DEMO_URL = "https://thecalltaker.com/demo.html"
FROM_NUMBER = "+16157845747"

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(ENGINE_DIR, "hot-lead-followup-state.json")
LOG_FILE = os.path.join(ENGINE_DIR, "hot-lead-followup-log.txt")

# Tags that qualify a contact for enrollment
HOT_TAGS = {"hot-lead", "warm-demo-prospect", "bland-interested"}

# Tags that disqualify a contact
SKIP_TAGS = {"customer", "pilot-active", "dnc", "opted-out", "do-not-contact",
             "active-client", "sms-failed-a2p", "suppressed"}

SMS_DELAY_SECONDS = 5  # between sends to avoid throttling

# ===================================================
# SMS SEQUENCE — 7-touch drip over 14 days
# ===================================================

SMS_SEQUENCE = [
    {
        "day": 0,
        "name": "Day 0 — Instant Intro",
        "message": "Hey {{firstName}}, this is Wallace from The Call Taker. You showed interest in our AI receptionist for {{companyName}} — it answers every call 24/7, books jobs, and texts you the details. Want to hear it live? Call our demo line right now: (615) 784-5747. It picks up in 2 seconds.",
    },
    {
        "day": 1,
        "name": "Day 1 — Social Proof",
        "message": "{{firstName}} — quick update. We just set up an HVAC company in Nashville last week. They missed 11 calls their first month with us — every one of those got answered and booked. That's $3,850 in jobs they would've lost. Your demo line is live anytime: (615) 784-5747",
    },
    {
        "day": 3,
        "name": "Day 3 — Pain Point",
        "message": "Hey {{firstName}}, real talk — 85% of callers who hit voicemail never call back. They just call your competitor. The Call Taker makes sure that never happens for {{companyName}}. $497/mo, no contracts. Try the demo: (615) 784-5747",
    },
    {
        "day": 5,
        "name": "Day 5 — Easy CTA",
        "message": "{{firstName}} — just reply YES and I'll set up a 15-min walkthrough this week. Or call the AI yourself right now: (615) 784-5747. Either way, happy to show you what it does for {{companyName}}.",
    },
    {
        "day": 7,
        "name": "Day 7 — Urgency",
        "message": "{{firstName}}, spring season is ramping up. Every missed call is a lost job for {{companyName}}. We can have The Call Taker answering your phones in 48 hours. Reply DEMO and I'll send you the link.",
    },
    {
        "day": 10,
        "name": "Day 10 — ROI Math",
        "message": "{{firstName}} — quick math: if {{companyName}} misses just 3 calls/week at $350 avg, that's $4,500/mo walking out the door. The Call Taker is $497/mo. That's a 9x return. Demo line: (615) 784-5747",
    },
    {
        "day": 14,
        "name": "Day 14 — Last Touch",
        "message": "Last text from me {{firstName}} — I respect your time. If you ever want to hear what your customers would experience, the demo line is always live: (615) 784-5747. Good luck this season. — Wallace, The Call Taker",
    },
]


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] FOLLOWUP: {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass


def ghl_request(method, path, body=None, version="2021-07-28"):
    url = f"{GHL_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": version,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "HotLeadFollowup/1.0 TheCallTaker",
    }
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        log(f"GHL API Error {e.code}: {method} {path} — {error_body[:200]}")
        return None
    except URLError as e:
        log(f"GHL Network Error: {method} {path} — {e.reason}")
        return None
    except Exception as e:
        log(f"GHL Error: {method} {path} — {e}")
        return None


def ntfy(topic, title, msg, priority="default", tags=""):
    try:
        url = f"https://ntfy.sh/{topic}"
        headers = {"Title": title, "Priority": priority, "Content-Type": "text/plain"}
        if tags:
            headers["Tags"] = tags
        req = Request(url, data=msg.encode(), headers=headers, method="POST")
        urlopen(req, timeout=10)
        log(f"ntfy sent: {title}")
    except Exception as e:
        log(f"ntfy error: {e}")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "enrolled": {},           # contact_id: {name, company, phone, enrolled_at, last_step, last_sent_at, completed}
        "total_enrolled": 0,
        "total_sms_sent": 0,
        "total_sms_failed": 0,
        "total_completed": 0,
        "last_run": None,
    }


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def get_all_contacts():
    contacts = []
    page = 1
    while True:
        resp = ghl_request("GET", f"/contacts/?locationId={GHL_LOCATION_ID}&limit=100&page={page}")
        if not resp or "contacts" not in resp:
            break
        batch = resp["contacts"]
        if not batch:
            break
        contacts.extend(batch)
        page += 1
        if len(batch) < 100:
            break
    return contacts


def send_sms(contact_id, message):
    """Send SMS via GHL conversations API."""
    body = {
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    }
    resp = ghl_request("POST", "/conversations/messages", body, version="2021-04-15")
    if resp:
        return True
    return False


def personalize(template, contact_data):
    """Replace {{firstName}} and {{companyName}} placeholders."""
    first = contact_data.get("name", "there")
    if not first or first == "?" or first.startswith("("):
        first = "there"
    company = contact_data.get("company", "your company")
    if not company:
        company = "your company"
    text = template.replace("{{firstName}}", first)
    text = text.replace("{{companyName}}", company)
    return text


def add_tag(contact_id, tag):
    resp = ghl_request("PUT", f"/contacts/{contact_id}", {"tags": [tag]})
    return resp


# ===================================================
# COMMANDS
# ===================================================

def cmd_enroll():
    """Find hot leads in GHL and enroll them into the follow-up sequence."""
    log("=== HOT LEAD FOLLOWUP: Enrolling leads ===")

    state = load_state()
    already_enrolled = set(state.get("enrolled", {}).keys())

    # Pull all contacts
    log("Pulling contacts from GHL...")
    all_contacts = get_all_contacts()
    log(f"Total contacts in GHL: {len(all_contacts)}")

    # Filter to hot leads
    hot_leads = []
    for c in all_contacts:
        tags = {t.lower() for t in c.get("tags", [])}
        # Must have at least one hot tag
        if not (tags & HOT_TAGS):
            continue
        # Must not have skip tags
        if tags & SKIP_TAGS:
            continue
        # Must have a phone number
        phone = c.get("phone", "")
        if not phone or len(phone) < 10:
            continue
        # Not already enrolled
        if c["id"] in already_enrolled:
            continue
        hot_leads.append(c)

    log(f"New hot leads to enroll: {len(hot_leads)}")

    if not hot_leads:
        log("No new hot leads found to enroll")
        ntfy(NTFY_OPS_TOPIC, "Hot Lead Followup: No new leads",
             "All hot leads already enrolled or none found.",
             tags="information_source")
        return

    # Enroll each lead and fire Day 0 SMS
    enrolled_count = 0
    sms_sent = 0
    sms_failed = 0

    ntfy(NTFY_WAR_TOPIC,
         f"HOT LEAD FOLLOWUP: Enrolling {len(hot_leads)} leads",
         f"Firing Day 0 SMS to {len(hot_leads)} hot leads now.",
         priority="high", tags="rocket,sms")

    for i, contact in enumerate(hot_leads):
        contact_id = contact["id"]
        name = contact.get("contactName", contact.get("firstName", "there"))
        company = contact.get("companyName", "")
        phone = contact.get("phone", "")

        log(f"[{i+1}/{len(hot_leads)}] Enrolling {name} / {company} ({phone})...")

        # Build contact data for personalization
        contact_data = {
            "name": name,
            "company": company,
            "phone": phone,
        }

        # Fire Day 0 SMS
        day0 = SMS_SEQUENCE[0]
        message = personalize(day0["message"], contact_data)

        if send_sms(contact_id, message):
            sms_sent += 1
            log(f"Day 0 SMS sent to {name} / {company}")
        else:
            sms_failed += 1
            log(f"FAILED Day 0 SMS to {name} / {company}")

        # Record enrollment
        state["enrolled"][contact_id] = {
            "name": name,
            "company": company,
            "phone": phone,
            "enrolled_at": datetime.now().isoformat(),
            "last_step": 0,
            "last_sent_at": datetime.now().isoformat(),
            "completed": False,
        }
        enrolled_count += 1

        # Tag contact
        add_tag(contact_id, "followup-active")

        save_state(state)
        time.sleep(SMS_DELAY_SECONDS)

    # Update totals
    state["total_enrolled"] = state.get("total_enrolled", 0) + enrolled_count
    state["total_sms_sent"] = state.get("total_sms_sent", 0) + sms_sent
    state["total_sms_failed"] = state.get("total_sms_failed", 0) + sms_failed
    save_state(state)

    # Report
    summary = (
        f"HOT LEAD ENROLLMENT COMPLETE\n"
        f"{'='*30}\n"
        f"New leads enrolled: {enrolled_count}\n"
        f"Day 0 SMS sent: {sms_sent}\n"
        f"Day 0 SMS failed: {sms_failed}\n"
        f"Total enrolled (all time): {state['total_enrolled']}\n"
    )
    log(summary)
    ntfy(NTFY_WAR_TOPIC,
         f"ENROLLED {enrolled_count} — Day 0 SMS: {sms_sent} sent, {sms_failed} failed",
         summary, priority="high", tags="white_check_mark,sms")


def cmd_run():
    """Process due follow-ups for enrolled leads."""
    log("=== HOT LEAD FOLLOWUP: Processing due follow-ups ===")

    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    enrolled = state.get("enrolled", {})

    if not enrolled:
        log("No enrolled leads")
        return

    now = datetime.now()
    due_count = 0
    sent_count = 0
    failed_count = 0
    completed_count = 0

    for contact_id, data in enrolled.items():
        if data.get("completed"):
            continue

        enrolled_at = datetime.fromisoformat(data["enrolled_at"])
        days_since_enroll = (now - enrolled_at).days
        last_step = data.get("last_step", 0)

        # Find the next step that's due
        next_step = None
        for step in SMS_SEQUENCE:
            if step["day"] > last_step and step["day"] <= days_since_enroll:
                next_step = step
                break

        if not next_step:
            # Check if sequence is complete
            if last_step >= SMS_SEQUENCE[-1]["day"]:
                data["completed"] = True
                completed_count += 1
                add_tag(contact_id, "followup-complete")
                log(f"Sequence complete for {data['name']} / {data['company']}")
            continue

        due_count += 1
        contact_data = {"name": data["name"], "company": data["company"], "phone": data["phone"]}
        message = personalize(next_step["message"], contact_data)

        log(f"Sending {next_step['name']} to {data['name']} / {data['company']}...")

        if send_sms(contact_id, message):
            sent_count += 1
            data["last_step"] = next_step["day"]
            data["last_sent_at"] = now.isoformat()
            log(f"{next_step['name']} sent to {data['name']}")
        else:
            failed_count += 1
            log(f"FAILED {next_step['name']} to {data['name']}")

        save_state(state)
        time.sleep(SMS_DELAY_SECONDS)

    state["total_sms_sent"] = state.get("total_sms_sent", 0) + sent_count
    state["total_sms_failed"] = state.get("total_sms_failed", 0) + failed_count
    state["total_completed"] = state.get("total_completed", 0) + completed_count
    save_state(state)

    if due_count > 0 or completed_count > 0:
        summary = (
            f"FOLLOWUP RUN COMPLETE\n"
            f"{'='*30}\n"
            f"Due follow-ups: {due_count}\n"
            f"SMS sent: {sent_count}\n"
            f"SMS failed: {failed_count}\n"
            f"Sequences completed: {completed_count}\n"
        )
        log(summary)
        ntfy(NTFY_OPS_TOPIC,
             f"Followup Run: {sent_count} SMS sent",
             summary, tags="sms")
    else:
        log("No follow-ups due right now")


def cmd_status():
    """Print dashboard."""
    state = load_state()
    enrolled = state.get("enrolled", {})

    active = sum(1 for d in enrolled.values() if not d.get("completed"))
    completed = sum(1 for d in enrolled.values() if d.get("completed"))

    # Count by step
    step_counts = {}
    for d in enrolled.values():
        if not d.get("completed"):
            step = d.get("last_step", 0)
            step_counts[step] = step_counts.get(step, 0) + 1

    print("=" * 55)
    print("  HOT LEAD FOLLOW-UP ENGINE — STATUS DASHBOARD")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    print(f"  Total enrolled (all time): {state.get('total_enrolled', 0)}")
    print(f"  Currently active:          {active}")
    print(f"  Completed sequences:       {completed}")
    print(f"  Total SMS sent:            {state.get('total_sms_sent', 0)}")
    print(f"  Total SMS failed:          {state.get('total_sms_failed', 0)}")
    print(f"  Last run:                  {state.get('last_run', 'never')}")
    print(f"  ---")

    if step_counts:
        print(f"  ACTIVE LEADS BY STEP:")
        for step_day in sorted(step_counts.keys()):
            step_name = next((s["name"] for s in SMS_SEQUENCE if s["day"] == step_day), f"Day {step_day}")
            print(f"    {step_name}: {step_counts[step_day]} leads")

    print(f"\n  --- ENROLLED LEADS ({len(enrolled)}) ---")
    for cid, d in list(enrolled.items())[:40]:
        status_icon = "done" if d.get("completed") else f"step {d.get('last_step', 0)}"
        name = d.get("name", "?")
        company = d.get("company", "")
        phone = d.get("phone", "")
        print(f"  [{status_icon:<8}] {(name or '?'):<25} {(company or ''):<30} {phone}")

    print("=" * 55)


# ===================================================
# MAIN
# ===================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 hot-lead-followup.py [enroll|run|status]")
        print("  enroll — Find hot leads + fire Day 0 SMS")
        print("  run    — Process due follow-ups (run every 4 hours)")
        print("  status — Print dashboard")
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "enroll":
            cmd_enroll()
        elif command == "run":
            cmd_run()
        elif command == "status":
            cmd_status()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 hot-lead-followup.py [enroll|run|status]")
            sys.exit(1)
        ntfy(NTFY_CALLS_TOPIC,
             f"Hot Lead Followup finished: {command}",
             f"Hot Lead Followup completed '{command}' at {datetime.now().strftime('%I:%M %p')}",
             tags="white_check_mark")
    except Exception as _exc:
        import traceback
        _tb = traceback.format_exc()
        log(f"CRASH in hot-lead-followup {command}: {_exc}")
        ntfy(NTFY_CALLS_TOPIC,
             f"Hot Lead Followup CRASHED: {command}",
             f"Command: {command}\nError: {_exc}\n\n{_tb[-500:]}",
             priority="high", tags="rotating_light")
        raise
