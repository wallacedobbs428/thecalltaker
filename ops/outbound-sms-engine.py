#!/usr/bin/env python3
"""
OUTBOUND SMS ENGINE — The Call Taker
=====================================
Replaces the dead Bland.ai cold caller with an automated SMS outreach sequence.
Triggers when new leads are scraped/imported into GHL.

Sequence (3 touches over 5 days):
  Touch 1 (Immediate): SMS — pain hook + demo line
  Touch 2 (Day 2):     SMS — secret shopper angle
  Touch 3 (Day 5):     SMS — breakup + demo line

Commands:
  scan     — Find new leads tagged 'cold-outreach' not yet SMS'd
  send     — Send due SMS touches
  run      — scan + send (full cycle)
  status   — Show stats

Schedule: 2x daily via launchd (10am, 4pm — business hours only)
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta

# ─── Local Detection ────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from local_detect import is_local, get_lead_city
except ImportError:
    def is_local(c): return False
    def get_lead_city(c): return ""

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
DEMO_LINE = "(615) 784-5747"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"

STATE_FILE = os.path.expanduser("~/thecalltaker/ops/outbound-sms-state.json")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/outbound-sms.log")

MAX_SMS_PER_RUN = 30
DELAY_BETWEEN_SMS = 5  # seconds

# HVAC hero image — attach as MMS to all HVAC SMS outreach
HVAC_HERO_IMAGE_URL = "https://thecalltaker.com/images/hvac-hero.jpg"

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-OutboundSMS/1.0",
}

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-OutboundSMS/1.0",
}

EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "sms-enrolled",
    "hot-lead", "converter-enrolled",  # handled by hot-lead-converter
}

# ─── Industry Mapping ────────────────────────────────────────────────────────

INDUSTRY_MAP = {
    "hvac": ("AC repair", "$350"), "plumbing": ("plumbing job", "$300"),
    "electrical": ("electrical job", "$275"), "roofing": ("roof job", "$5,000"),
    "locksmith": ("lockout call", "$250"), "dental": ("appointment", "$400"),
    "legal": ("consultation", "$500"), "towing": ("tow", "$150"),
    "veterinary": ("vet visit", "$200"), "medspa": ("appointment", "$500"),
    "pest-control": ("service call", "$200"), "garage-door": ("repair", "$300"),
    "property-management": ("maintenance call", "$250"),
    "water-damage": ("emergency call", "$2,000"), "cleaning": ("booking", "$200"),
    "landscaping": ("estimate", "$300"), "auto-repair": ("repair", "$400"),
    "general-contractor": ("project", "$1,000"), "funeral": ("arrangement", "$3,000"),
}


def get_industry_info(tags):
    if not tags:
        return ("service call", "$350")
    for tag in tags:
        if tag.lower().strip() in INDUSTRY_MAP:
            return INDUSTRY_MAP[tag.lower().strip()]
    return ("service call", "$350")


# ─── SMS Copy ────────────────────────────────────────────────────────────────

def sms_touch_1(first_name, company, job_word, job_value):
    """Immediate — pain hook + demo line."""
    return (
        f"Hey {first_name}, it's Wallace. Quick question — "
        f"who's answering {company}'s phones after 5pm? "
        f"If it's voicemail, that's {job_value}+ per missed {job_word} going to your competitor. "
        f"Hear what your customers SHOULD hear: {DEMO_LINE}"
    )


def sms_touch_2(first_name, company):
    """Day 2 — secret shopper angle."""
    return (
        f"{first_name} — I called {company} last night at 8pm. Got voicemail. "
        f"85% of callers won't leave a message. They just call the next company. "
        f"I built an AI that answers every call 24/7 — sounds human, books jobs on your calendar. "
        f"Free 14-day pilot. No card. Interested?"
    )


def sms_touch_3(first_name):
    """Day 5 — breakup with final push."""
    return (
        f"Last text from me {first_name}. No pitch — just this: "
        f"call {DEMO_LINE} and pretend you're a customer. "
        f"Takes 90 seconds. If you're not impressed, I'll never text again. — Wallace"
    )


# ─── LOCAL IN-PERSON SMS VARIANTS ───────────────────────────────────────────

def local_sms_touch_1(first_name, company, city):
    """Immediate — in-person visit CTA for local leads."""
    city_part = f"right here in {city}" if city else "local to Nashville"
    return (
        f"Hey {first_name}, it's Wallace. I'm {city_part} and I built "
        f"some new technology for businesses like {company}. "
        f"Would it be worth 10 minutes for me to stop by and show you how it works?"
    )


def local_sms_touch_2(first_name, company, city):
    """Day 2 — in-person push with pain angle."""
    return (
        f"{first_name} — I called {company} last night at 8pm. Got voicemail. "
        f"85% of those callers won't leave a message — that's real money walking. "
        f"I'm in {city or 'the area'} and I'd love to show you what I built to fix that. "
        f"10 minutes, your location. Interested?"
    )


def local_sms_touch_3(first_name):
    """Day 5 — breakup for local leads."""
    return (
        f"Last text from me {first_name}. I tried to come show you in person "
        f"because I genuinely think it'd help. The offer stands — "
        f"whenever you're ready, I'm right here in Brentwood. — Wallace"
    )


# ─── Helpers ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] outbound-sms: {msg}"
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
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "enrolled": {},
        "stats": {"total_enrolled": 0, "total_sms_sent": 0, "total_runs": 0, "last_run": None},
    }


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
                time.sleep([30, 60, 120][min(attempt, 2)])
                continue
            if resp.status_code >= 500:
                time.sleep([5, 15, 30][min(attempt, 2)])
                continue
            return resp.json() if resp.text else {}
        except requests.exceptions.RequestException as e:
            log(f"Request error: {e}", "ERROR")
            time.sleep(5)
    return None


def send_sms(contact_id, message, attach_image=False):
    body = {"type": "SMS", "contactId": contact_id, "message": message}
    if attach_image:
        body["attachments"] = [HVAC_HERO_IMAGE_URL]
    return ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS, json_body=body)


def add_tag(contact_id, tags):
    return ghl_request("POST", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def ntfy_alert(topic, title, message, priority="default"):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        requests.post(f"https://ntfy.sh/{topic}", data=message.encode("utf-8"),
                      headers={"Title": safe_title, "Priority": priority}, timeout=10)
    except Exception:
        pass


# ─── Touch Schedule ──────────────────────────────────────────────────────────

TOUCH_SCHEDULE = [
    (1, 0),       # Immediate
    (2, 2880),    # Day 2 (48 hours)
    (3, 7200),    # Day 5 (120 hours)
]


def should_send(enrollment, touch_num):
    sent = enrollment.get("touches_sent", [])
    if touch_num in sent:
        return False
    if touch_num > 1 and (touch_num - 1) not in sent:
        return False
    if enrollment.get("replied"):
        return False
    enrolled_at = datetime.fromisoformat(enrollment["enrolled_at"])
    _, delay = TOUCH_SCHEDULE[touch_num - 1]
    return datetime.now() >= enrolled_at + timedelta(minutes=delay)


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_scan(state):
    log("Scanning for new cold-outreach leads...")
    all_contacts = []
    page = 1
    while True:
        data = ghl_request("GET", "/contacts/", params={
            "locationId": GHL_LOCATION_ID, "limit": 100, "page": page,
        })
        if not data or "contacts" not in data:
            break
        contacts = data["contacts"]
        all_contacts.extend(contacts)
        if len(contacts) < 100:
            break
        page += 1
        if page > 50:
            break

    new = 0
    for c in all_contacts:
        cid = c.get("id")
        if not cid or cid in state["enrolled"]:
            continue
        tags = set(t.lower() for t in c.get("tags", []))
        if not ({"cold-outreach"} & tags):
            continue
        if tags & EXCLUDE_TAGS:
            continue
        if not c.get("phone"):
            continue

        state["enrolled"][cid] = {
            "enrolled_at": datetime.now().isoformat(),
            "touches_sent": [],
            "replied": False,
            "first_name": c.get("firstName", "there"),
            "company_name": c.get("companyName", "your business"),
        }
        state["stats"]["total_enrolled"] += 1
        add_tag(cid, ["sms-enrolled"])
        new += 1

    log(f"Scan: {new} new leads enrolled, {len(all_contacts)} total contacts")
    return new


def cmd_send(state):
    log("Sending due SMS touches...")
    sent_count = 0

    for cid, enrollment in list(state["enrolled"].items()):
        if sent_count >= MAX_SMS_PER_RUN:
            break
        if enrollment.get("replied"):
            continue
        if len(enrollment.get("touches_sent", [])) >= 3:
            continue

        # Get fresh contact data
        data = ghl_request("GET", f"/contacts/{cid}")
        if not data or "contact" not in data:
            continue
        contact = data["contact"]
        tags = contact.get("tags", [])
        contact_tags_lower = set(t.lower() for t in tags)

        # Stop if replied or converted
        if {"contacted", "pilot-active", "customer"} & contact_tags_lower:
            enrollment["replied"] = True
            continue

        first_name = contact.get("firstName", "there")
        company = contact.get("companyName", "your business")
        job_word, job_value = get_industry_info(tags)
        local = is_local(contact)
        city = get_lead_city(contact) if local else ""

        for touch_num in range(1, 4):
            if not should_send(enrollment, touch_num):
                continue

            if local:
                # Local leads: in-person appointment CTA
                if touch_num == 1:
                    msg = local_sms_touch_1(first_name, company, city)
                elif touch_num == 2:
                    msg = local_sms_touch_2(first_name, company, city)
                elif touch_num == 3:
                    msg = local_sms_touch_3(first_name)
            else:
                # National leads: standard demo/pilot CTA
                if touch_num == 1:
                    msg = sms_touch_1(first_name, company, job_word, job_value)
                elif touch_num == 2:
                    msg = sms_touch_2(first_name, company)
                elif touch_num == 3:
                    msg = sms_touch_3(first_name)

            # Attach HVAC hero image as MMS for HVAC contacts
            is_hvac = "hvac" in contact_tags_lower
            result = send_sms(cid, msg, attach_image=is_hvac)
            if result:
                enrollment["touches_sent"].append(touch_num)
                state["stats"]["total_sms_sent"] += 1
                sent_count += 1
                log(f"  Touch {touch_num} {'MMS' if is_hvac else 'SMS'} to {first_name} ({company}){' [LOCAL]' if local else ''}")
            break  # One touch per contact per cycle

        time.sleep(DELAY_BETWEEN_SMS)

    log(f"Send complete. {sent_count} SMS sent.")
    return sent_count


def cmd_run(state):
    state["stats"]["total_runs"] += 1
    state["stats"]["last_run"] = datetime.now().isoformat()
    new = cmd_scan(state)
    sent = cmd_send(state)
    save_state(state)

    if new > 0 or sent > 0:
        ntfy_alert(NTFY_ACTIVITY, "Outbound SMS Engine",
                   f"New: {new} | SMS sent: {sent} | Total enrolled: {state['stats']['total_enrolled']}",
                   priority="default")


def cmd_status(state):
    stats = state["stats"]
    enrolled = state["enrolled"]
    active = sum(1 for e in enrolled.values() if not e.get("replied") and len(e.get("touches_sent", [])) < 3)
    completed = sum(1 for e in enrolled.values() if len(e.get("touches_sent", [])) >= 3)

    print("\n╔══════════════════════════════════════════╗")
    print("║     OUTBOUND SMS ENGINE — STATUS         ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  Total Enrolled:     {stats.get('total_enrolled', 0):>5}               ║")
    print(f"║  Active Sequences:   {active:>5}               ║")
    print(f"║  Completed (3/3):    {completed:>5}               ║")
    print(f"║  Total SMS Sent:     {stats.get('total_sms_sent', 0):>5}               ║")
    print(f"║  Total Runs:         {stats.get('total_runs', 0):>5}               ║")
    print("╚══════════════════════════════════════════╝\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: outbound-sms-engine.py <scan|send|run|status>")
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
        elif command == "status":
            cmd_status(state)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        log(f"CRASH: {e}", "ERROR")
        ntfy_alert("tct-system-vRsfXQRQ", "[CRITICAL] Outbound SMS Engine Crashed",
                   f"Error: {str(e)[:500]}", priority="urgent")
        raise


if __name__ == "__main__":
    main()
