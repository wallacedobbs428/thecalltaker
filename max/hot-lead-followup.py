#!/usr/bin/env python3
"""
HOT LEAD FOLLOW-UP — 5-Step Automated Sequence
March 2026

Pulls all contacts tagged "hot-lead" who haven't booked a demo,
then runs a 5-step follow-up sequence:

  Day 0: SMS — casual check-in
  Day 1: Email — demo link + pain angle
  Day 3: Bland.ai call trigger
  Day 5: Email — case study + scarcity
  Day 7: Final SMS — last chance

Usage:
  python3 hot-lead-followup.py scan      # Find hot leads, enroll new ones
  python3 hot-lead-followup.py send      # Process sequence steps for enrolled leads
  python3 hot-lead-followup.py run       # scan + send (for launchd)
  python3 hot-lead-followup.py enroll    # Force-enroll all current hot leads NOW
  python3 hot-lead-followup.py status    # Print current stats
"""

import json
import sys
import os
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# ===================================================
# CONFIG
# ===================================================

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

BLAND_API_KEY = "org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969"
BLAND_BASE = "https://api.bland.ai/v1"

VOICE_AGENT_ID = "695947c64b9ed67d8f1077ad"

FROM_EMAIL = "thecalltakerai@gmail.com"

NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_URGENT = "tct-urgent-Hk9UOEZR"
NTFY_SALES = "tct-sales-63uYsIT9"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "hot-lead-followup.log")
STATE_FILE = os.path.join(SCRIPT_DIR, "hot-lead-followup-state.json")

BOOK_URL = "https://thecalltaker.com/book.html"

# Skip tags — never enroll these contacts
SKIP_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "demo-booked",
}

INDUSTRY_LIST = [
    "hvac", "plumbing", "roofing", "electrical", "locksmith",
    "dental", "medspa", "legal", "towing", "veterinary",
    "pest-control", "auto-repair", "cleaning", "water-damage",
    "property-management", "landscaping", "general-contractor",
    "garage-door", "funeral",
]

# Industry → job word mapping for personalized copy
INDUSTRY_JOBS = {
    "hvac": "service call",
    "plumbing": "service call",
    "roofing": "roofing job",
    "electrical": "service call",
    "locksmith": "lockout call",
    "dental": "appointment",
    "medspa": "appointment",
    "legal": "case",
    "towing": "tow call",
    "veterinary": "appointment",
    "pest-control": "service call",
    "auto-repair": "repair job",
    "cleaning": "cleaning job",
    "water-damage": "emergency call",
    "property-management": "maintenance call",
    "landscaping": "estimate call",
    "general-contractor": "project call",
    "garage-door": "service call",
    "funeral": "arrangement call",
}


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] HOT-FOLLOWUP: {msg}"
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
        log(f"GHL Error {e.code}: {method} {path} — {error_body[:200]}")
        return None
    except URLError as e:
        log(f"GHL Network Error: {method} {path} — {e.reason}")
        return None
    except Exception as e:
        log(f"GHL Error: {method} {path} — {e}")
        return None


def bland_request(method, path, body=None):
    url = f"{BLAND_BASE}{path}"
    headers = {
        "Authorization": BLAND_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        log(f"Bland Error {e.code}: {method} {path} — {error_body[:300]}")
        if e.code == 402:
            log("BLAND.AI BALANCE DEPLETED — skipping call step")
            ntfy(NTFY_URGENT,
                 "[CRITICAL] Bland.ai balance depleted",
                 "Hot lead followup call step skipped — Bland.ai 402. Top up balance.",
                 priority="urgent")
        return None
    except Exception as e:
        log(f"Bland Error: {method} {path} — {e}")
        return None


def ntfy(topic, title, msg, priority="default", tags=""):
    try:
        url = f"https://ntfy.sh/{topic}"
        headers = {"Title": title, "Priority": priority, "Content-Type": "text/plain"}
        if tags:
            headers["Tags"] = tags
        req = Request(url, data=msg.encode(), headers=headers, method="POST")
        urlopen(req, timeout=10)
    except Exception as e:
        log(f"ntfy error: {e}")


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            log("State file corrupted, starting fresh")
    return {
        "enrolled": {},       # contact_id → {name, company, phone, email, industry, enrolled_date, step, tags_applied}
        "completed": {},      # contact_id → {name, company, outcome, completed_date}
        "total_enrolled": 0,
        "total_sms_sent": 0,
        "total_emails_sent": 0,
        "total_calls_made": 0,
        "total_completed": 0,
        "total_booked": 0,
        "last_scan": None,
        "last_send": None,
    }


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, default=str)
    os.replace(tmp, STATE_FILE)


def days_since(date_str):
    if not date_str:
        return 999
    try:
        dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00").split("+")[0].split("T")[0])
        return (datetime.now() - dt).days
    except:
        return 999


def get_industry(tags):
    return next((t for t in tags if t in INDUSTRY_LIST), "service")


def get_job_word(industry):
    return INDUSTRY_JOBS.get(industry, "call")


def tag_contact(contact_id, new_tag):
    """Add a tag to a GHL contact."""
    resp = ghl_request("GET", f"/contacts/{contact_id}")
    if not resp or "contact" not in resp:
        return False
    existing = resp["contact"].get("tags", [])
    if new_tag not in existing:
        existing.append(new_tag)
        result = ghl_request("PUT", f"/contacts/{contact_id}", {"tags": existing})
        return result is not None
    return True


def remove_tag(contact_id, tag_to_remove):
    """Remove a tag from a GHL contact."""
    resp = ghl_request("GET", f"/contacts/{contact_id}")
    if not resp or "contact" not in resp:
        return False
    existing = resp["contact"].get("tags", [])
    if tag_to_remove in existing:
        existing.remove(tag_to_remove)
        result = ghl_request("PUT", f"/contacts/{contact_id}", {"tags": existing})
        return result is not None
    return True


# ===================================================
# SEQUENCE COPY
# ===================================================

# Step 0 — Day 0: SMS (casual, direct)
def sms_day0(name, company, industry):
    job = get_job_word(industry)
    return (
        f"Hey {name}, this is Wallace from The Call Taker — "
        f"did you still want to see how the AI receptionist works for {company}? "
        f"It picks up every {job} 24/7 so you never miss one. "
        f"I can set up a free demo whenever you're ready"
    )


# Step 1 — Day 1: Email (pain angle + demo link)
def email_day1(name, company, industry):
    job = get_job_word(industry)
    subject = f"{company} — quick question about missed calls"
    body = f"""<p>Hey {name},</p>

<p>I wanted to follow up — we flagged {company} as a business that could
benefit from an AI receptionist, and I wanted to make sure you had the chance
to see it in action before we fill our pilot spots.</p>

<p>Here's the thing most {industry} businesses don't realize: every missed call
is a {job} that goes to your competitor. That's $300-$2,000 walking out the door
every time nobody picks up.</p>

<p>Our AI answers in 2 rings, sounds like a real person, books the {job},
and texts you the details — 24/7, even at 2am on a Saturday.</p>

<p><strong><a href="{BOOK_URL}?utm_source=hot-followup&utm_medium=email&utm_campaign=day1">Book a quick 10-minute demo</a></strong>
and I'll show you exactly how it works for {industry} businesses like yours.</p>

<p>Or just call our demo line at <strong>(615) 784-5747</strong> right now to hear it live.</p>

<p>— Wallace<br>
The Call Taker<br>
<em>AI receptionist that never misses a call</em></p>"""
    return subject, body


# Step 2 — Day 3: Bland.ai call trigger
def call_day3_task(name, company, industry):
    job = get_job_word(industry)
    return f"""You are calling {name} at {company} on behalf of Wallace from The Call Taker.

Opening: "Hey {name}, this is a quick follow-up from Wallace at The Call Taker. I reached out
a few days ago about our AI receptionist for {industry} businesses. Did you get a chance to
check it out?"

If YES or curious: "Awesome — the easiest way to see it is to call our demo line at
615-784-5747. You'll talk to the AI live. It handles {job}s, books appointments, texts you
the details. Takes 60 seconds. Want me to text you that number?"

If NO or busy: "Totally understand. Quick version — it picks up every {job} 24/7 so you
never miss revenue. We're doing free 14-day pilots for {industry} businesses right now,
no card needed. Can I set one up for {company}?"

If not interested: "No problem at all. If you ever want to hear it, demo line is
615-784-5747. Have a good one."

Keep it under 45 seconds. Be friendly, not pushy."""


# Step 3 — Day 5: Email (case study + scarcity)
def email_day5(name, company, industry):
    job = get_job_word(industry)
    subject = f"How a {industry} company added $8K/mo (doing what {company} does)"
    body = f"""<p>Hey {name},</p>

<p>Wanted to share a quick story —</p>

<p>One of our {industry} clients was missing 40% of their after-hours calls.
Within the first month of using our AI receptionist, they recovered
<strong>$8,400/month</strong> in jobs that would've gone to voicemail.</p>

<p>Same {job}s you handle. Same hours you probably miss.</p>

<p>We have <strong>2 pilot spots left this month</strong> for {industry} businesses.
14 days free, no credit card, cancel anytime.</p>

<p><strong><a href="{BOOK_URL}?utm_source=hot-followup&utm_medium=email&utm_campaign=day5">Grab your pilot spot now →</a></strong></p>

<p>Or reply to this email and I'll set it up personally.</p>

<p>— Wallace<br>
The Call Taker</p>"""
    return subject, body


# Step 4 — Day 7: Final SMS (last chance)
def sms_day7(name, company, industry):
    return (
        f"Last follow-up {name} — we have 1 pilot spot left this month for {industry} businesses. "
        f"14 days free, no card. "
        f"Book here: {BOOK_URL}?utm_source=hot-followup&utm_medium=sms&utm_campaign=day7 "
        f"or call our demo line at (615) 784-5747 to hear the AI live. "
        f"After this I won't bug you again"
    )


# ===================================================
# SEQUENCE STEPS
# ===================================================

SEQUENCE_STEPS = [
    {"step": 0, "day": 0, "type": "sms",   "label": "Day 0 SMS"},
    {"step": 1, "day": 1, "type": "email", "label": "Day 1 Email"},
    {"step": 2, "day": 3, "type": "call",  "label": "Day 3 Call"},
    {"step": 3, "day": 5, "type": "email", "label": "Day 5 Email"},
    {"step": 4, "day": 7, "type": "sms",   "label": "Day 7 SMS"},
]


def send_sms(contact_id, phone, message):
    """Send SMS via GHL conversations API."""
    body = {
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    }
    resp = ghl_request("POST", "/conversations/messages", body, version="2021-04-15")
    if resp:
        msg_id = resp.get("messageId", resp.get("id", "ok"))
        log(f"  SMS sent to {phone} — msgId: {msg_id}")
        return True
    log(f"  SMS FAILED to {phone}")
    return False


def send_email(contact_id, subject, html_body):
    """Send email via GHL conversations API."""
    body = {
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": html_body,
        "emailFrom": FROM_EMAIL,
    }
    resp = ghl_request("POST", "/conversations/messages", body, version="2021-04-15")
    if resp:
        msg_id = resp.get("messageId", resp.get("id", "ok"))
        log(f"  Email sent — msgId: {msg_id}")
        return True
    log(f"  Email FAILED for contact {contact_id}")
    return False


def trigger_call(contact_id, phone, company, industry, name):
    """Trigger a Bland.ai outbound call."""
    task = call_day3_task(name, company, industry)
    call_body = {
        "phone_number": phone,
        "task": task,
        "voice_id": "w9rPM8AIZle60Nbpw7nl",
        "reduce_latency": True,
        "wait_for_greeting": True,
        "max_duration": 90,
        "record": True,
        "metadata": {
            "contact_id": contact_id,
            "company": company,
            "industry": industry,
            "source": "hot-lead-followup-day3",
        },
    }
    resp = bland_request("POST", "/calls", call_body)
    if resp and resp.get("call_id"):
        log(f"  Call triggered to {phone} — call_id: {resp['call_id']}")
        return True
    log(f"  Call FAILED to {phone}")
    return False


# ===================================================
# CORE ENGINE
# ===================================================

def get_all_contacts():
    """Fetch all contacts from GHL with pagination."""
    contacts = []
    page = 1
    while page <= 10:
        resp = ghl_request("GET", f"/contacts/?locationId={GHL_LOCATION_ID}&limit=100&page={page}")
        if not resp or "contacts" not in resp:
            break
        batch = resp["contacts"]
        if not batch:
            break
        contacts.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        time.sleep(1)
    return contacts


def scan_and_enroll(state, force=False):
    """Find hot leads not yet enrolled and add them to the sequence."""
    log("=== SCANNING for hot leads ===")
    contacts = get_all_contacts()
    log(f"Fetched {len(contacts)} total contacts from GHL")

    enrolled_count = 0
    skipped = 0

    for c in contacts:
        cid = c.get("id", "")
        tags = [t.lower() for t in c.get("tags", [])]

        # Must have "hot-lead" tag
        if "hot-lead" not in tags:
            continue

        # Skip if already enrolled or completed
        if cid in state["enrolled"] or cid in state["completed"]:
            continue

        # Skip if they have any blocking tags
        if SKIP_TAGS & set(tags):
            skipped += 1
            continue

        # Need either phone or email to run the sequence
        phone = c.get("phone", "")
        email = c.get("email", "")
        if not phone and not email:
            skipped += 1
            continue

        name = c.get("firstName") or c.get("name") or "there"
        company = c.get("companyName") or "your company"
        industry = get_industry(tags)

        # Enroll
        state["enrolled"][cid] = {
            "name": name,
            "company": company,
            "phone": phone,
            "email": email,
            "industry": industry,
            "enrolled_date": datetime.now().isoformat(),
            "step": -1,  # hasn't received step 0 yet
            "tags_applied": [],
        }
        state["total_enrolled"] += 1
        enrolled_count += 1

        # Tag in GHL
        tag_contact(cid, "follow-up-sequence-active")
        state["enrolled"][cid]["tags_applied"].append("follow-up-sequence-active")

        log(f"  ENROLLED: {name} ({company}) [{industry}] — {phone or email}")
        time.sleep(0.5)

    state["last_scan"] = datetime.now().isoformat()
    save_state(state)
    log(f"Scan complete: {enrolled_count} new enrollments, {skipped} skipped, {len(state['enrolled'])} active")

    if enrolled_count > 0:
        ntfy(NTFY_SALES,
             f"Hot Lead Followup: {enrolled_count} enrolled",
             f"{enrolled_count} new hot leads entered follow-up sequence.\n"
             f"Total active: {len(state['enrolled'])}\n"
             f"Total ever enrolled: {state['total_enrolled']}",
             tags="fire,envelope")

    return enrolled_count


def process_sends(state):
    """Walk through enrolled contacts and send the next step if due."""
    log("=== PROCESSING sequence sends ===")

    if not state["enrolled"]:
        log("No enrolled contacts. Run 'scan' first.")
        return

    sent_count = 0
    completed_count = 0
    to_remove = []

    for cid, data in list(state["enrolled"].items()):
        name = data.get("name", "there")
        company = data.get("company", "your company")
        phone = data.get("phone", "")
        email = data.get("email", "")
        industry = data.get("industry", "service")
        enrolled_date = data.get("enrolled_date")
        current_step = data.get("step", -1)
        days_enrolled = days_since(enrolled_date)

        # Check if they booked a demo (tag check)
        contact_resp = ghl_request("GET", f"/contacts/{cid}")
        if contact_resp and "contact" in contact_resp:
            live_tags = [t.lower() for t in contact_resp["contact"].get("tags", [])]
            if "demo-booked" in live_tags or "pilot-active" in live_tags or "customer" in live_tags:
                log(f"  {name} ({company}) — already converted (demo-booked/pilot/customer). Completing.")
                state["completed"][cid] = {
                    "name": name,
                    "company": company,
                    "outcome": "converted",
                    "completed_date": datetime.now().isoformat(),
                }
                state["total_completed"] += 1
                state["total_booked"] += 1
                to_remove.append(cid)
                continue
            if "do-not-contact" in live_tags or "unsubscribed" in live_tags:
                log(f"  {name} ({company}) — opted out. Removing.")
                to_remove.append(cid)
                continue
        time.sleep(0.5)

        # Find the next step that's due
        next_step = current_step + 1
        if next_step >= len(SEQUENCE_STEPS):
            # Sequence complete
            log(f"  {name} ({company}) — sequence complete (all 5 steps sent)")
            remove_tag(cid, "follow-up-sequence-active")
            state["completed"][cid] = {
                "name": name,
                "company": company,
                "outcome": "sequence-complete",
                "completed_date": datetime.now().isoformat(),
            }
            state["total_completed"] += 1
            to_remove.append(cid)
            continue

        step_info = SEQUENCE_STEPS[next_step]
        required_day = step_info["day"]

        if days_enrolled < required_day:
            continue  # Not time yet

        step_type = step_info["type"]
        step_label = step_info["label"]
        success = False

        if step_type == "sms" and phone:
            if next_step == 0:
                msg = sms_day0(name, company, industry)
            else:
                msg = sms_day7(name, company, industry)
            success = send_sms(cid, phone, msg)
            if success:
                state["total_sms_sent"] += 1

        elif step_type == "email" and email:
            if next_step == 1:
                subject, body = email_day1(name, company, industry)
            else:
                subject, body = email_day5(name, company, industry)
            success = send_email(cid, subject, body)
            if success:
                state["total_emails_sent"] += 1

        elif step_type == "call" and phone:
            success = trigger_call(cid, phone, company, industry, name)
            if success:
                state["total_calls_made"] += 1

        elif step_type == "sms" and not phone:
            # No phone — skip SMS steps, mark as sent
            log(f"  {name} — no phone, skipping {step_label}")
            success = True

        elif step_type == "call" and not phone:
            log(f"  {name} — no phone, skipping {step_label}")
            success = True

        elif step_type == "email" and not email:
            log(f"  {name} — no email, skipping {step_label}")
            success = True

        if success:
            data["step"] = next_step
            sent_count += 1
            log(f"  [{step_label}] {name} ({company}) — sent")

        time.sleep(2)  # Rate limiting between sends

    # Remove completed contacts from active list
    for cid in to_remove:
        state["enrolled"].pop(cid, None)

    state["last_send"] = datetime.now().isoformat()
    save_state(state)

    log(f"Send complete: {sent_count} messages sent, {completed_count + len(to_remove)} completed/removed")
    log(f"Active: {len(state['enrolled'])} | Completed: {len(state['completed'])}")


def force_enroll_all(state):
    """Force-enroll all hot leads right now, even if scan already ran today."""
    log("=== FORCE ENROLLING all hot leads ===")
    count = scan_and_enroll(state, force=True)
    if count == 0:
        log("No new hot leads to enroll (all may already be in sequence)")
    return count


def print_status():
    state = load_state()
    enrolled = state.get("enrolled", {})
    completed = state.get("completed", {})

    print("\n" + "=" * 60)
    print("  HOT LEAD FOLLOW-UP — STATUS")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"  Total ever enrolled:  {state.get('total_enrolled', 0)}")
    print(f"  Currently active:     {len(enrolled)}")
    print(f"  Completed:            {len(completed)}")
    print(f"  Demos booked:         {state.get('total_booked', 0)}")
    print(f"  SMS sent:             {state.get('total_sms_sent', 0)}")
    print(f"  Emails sent:          {state.get('total_emails_sent', 0)}")
    print(f"  Calls made:           {state.get('total_calls_made', 0)}")
    print(f"  Last scan:            {state.get('last_scan', 'Never')}")
    print(f"  Last send:            {state.get('last_send', 'Never')}")
    print("=" * 60)

    if enrolled:
        print("\n  ACTIVE CONTACTS:")
        for cid, data in enrolled.items():
            step = data.get("step", -1)
            step_label = SEQUENCE_STEPS[step]["label"] if 0 <= step < len(SEQUENCE_STEPS) else "Not started"
            days = days_since(data.get("enrolled_date"))
            print(f"    {data['name']:15s} ({data['company']:20s}) — Step {step + 1}/5 [{step_label}] — Day {days}")

    if completed:
        booked = [d for d in completed.values() if d.get("outcome") == "converted"]
        seq_done = [d for d in completed.values() if d.get("outcome") == "sequence-complete"]
        print(f"\n  OUTCOMES: {len(booked)} booked demos, {len(seq_done)} completed sequence")

    print()


# ===================================================
# MAIN
# ===================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    state = load_state()

    if cmd == "scan":
        scan_and_enroll(state)
    elif cmd == "send":
        process_sends(state)
    elif cmd == "run":
        scan_and_enroll(state)
        process_sends(state)
    elif cmd == "enroll":
        force_enroll_all(state)
        # Immediately send Day 0 SMS to all newly enrolled
        state = load_state()
        process_sends(state)
    elif cmd == "status":
        print_status()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
