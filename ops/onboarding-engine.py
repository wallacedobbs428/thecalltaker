#!/usr/bin/env python3
"""
CUSTOMER ONBOARDING ENGINE
===========================
The Call Taker — thecalltaker.com

Automated 30-day onboarding sequence for new customers.
Trigger: Contact tagged "new-customer" in GHL.

SEQUENCE:
  DAY 0:  Welcome SMS + Welcome Email + ntfy URGENT + GHL task
  DAY 3:  Check-in SMS + ntfy reminder
  DAY 7:  Tuning SMS + First Wins email template + ntfy reminder
  DAY 10: Pre-trial-end SMS + ntfy reminder
  DAY 14: Trial complete SMS + tag swap (new-customer → paying-customer)
  DAY 30: Value review ntfy + Month 1 email template

TAGS:
  new-customer      → triggers enrollment
  in-trial          → active during 14-day trial
  trial-complete    → after day 14
  paying-customer   → ongoing
  day3-checked      → prevents dup
  day7-checked      → prevents dup
  day10-checked     → prevents dup
  day14-checked     → prevents dup
  day30-checked     → prevents dup

Commands:
  scan     — Find new customers, send day-0 messages
  run      — scan + all scheduled touches
  status   — Show all active customers + their day
  preview  — Preview all message copy
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

DEMO_LINE       = "(615) 784-5747"
WALLACE_PHONE   = "+16156539004"
WALLACE_GHL_ID  = "DtKLG28VzgUb6q3brILD"
FROM_EMAIL      = "thecalltakerai@gmail.com"
BOOKING_URL     = "https://thecalltaker.com/demo.html"

# ntfy topics
NTFY_URGENT   = "tct-urgent-Hk9UOEZR"
NTFY_SALES    = "tct-sales-63uYsIT9"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_SYSTEM   = "tct-system-vRsfXQRQ"

# State and log paths
OPS_DIR    = os.path.expanduser("~/thecalltaker-ops")
STATE_FILE = os.path.join(OPS_DIR, "onboarding-engine-state.json")
LOG_FILE   = os.path.join(OPS_DIR, "logs", "onboarding-engine.log")

# Tags
TRIGGER_TAG       = "new-customer"
IN_TRIAL_TAG      = "in-trial"
TRIAL_COMPLETE_TAG = "trial-complete"
PAYING_TAG        = "paying-customer"

TOUCHPOINT_TAGS = {
    3:  "day3-checked",
    7:  "day7-checked",
    10: "day10-checked",
    14: "day14-checked",
    30: "day30-checked",
}

EXCLUDE_TAGS = {
    "do-not-contact", "unsubscribed",
}

# GHL API headers
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

# ─── Logging ─────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
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
        except Exception as e:
            log(f"State load error: {e}", "ERROR")
    return {"customers": {}, "stats": {"enrolled": 0, "trial_complete": 0, "paying": 0}}

def save_state(state):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(STATE_FILE), suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, STATE_FILE)
    except Exception as e:
        log(f"State save error: {e}", "ERROR")

# ─── GHL API Helpers ─────────────────────────────────────────────────────────

def ghl_get(endpoint, headers=None, params=None):
    headers = headers or CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{endpoint}"
    for attempt in range(3):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                log(f"Rate limited, waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                log(f"GHL GET {endpoint} failed: {e}", "ERROR")
    return None

def ghl_post(endpoint, data, headers=None):
    headers = headers or CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{endpoint}"
    for attempt in range(3):
        try:
            r = requests.post(url, headers=headers, json=data, timeout=30)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                log(f"Rate limited, waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                log(f"GHL POST {endpoint} failed: {e}", "ERROR")
    return None

def ghl_put(endpoint, data, headers=None):
    headers = headers or CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{endpoint}"
    for attempt in range(3):
        try:
            r = requests.put(url, headers=headers, json=data, timeout=30)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                log(f"Rate limited, waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                log(f"GHL PUT {endpoint} failed: {e}", "ERROR")
    return None

# ─── GHL Actions ─────────────────────────────────────────────────────────────

def get_contacts_by_tag(tag):
    """Fetch all contacts with a specific tag."""
    contacts = []
    page = 1
    while True:
        data = ghl_get(
            "/contacts/",
            params={"locationId": GHL_LOCATION_ID, "query": tag, "page": page, "limit": 100}
        )
        if not data or "contacts" not in data:
            break
        batch = data["contacts"]
        for c in batch:
            tags = c.get("tags", [])
            if tag in tags:
                contacts.append(c)
        if len(batch) < 100:
            break
        page += 1
        time.sleep(1)
    return contacts

def add_tag(contact_id, tag):
    tags_data = ghl_get(f"/contacts/{contact_id}")
    if not tags_data or "contact" not in tags_data:
        return False
    current = tags_data["contact"].get("tags", [])
    if tag in current:
        return True
    current.append(tag)
    result = ghl_put(f"/contacts/{contact_id}", {"tags": current})
    return result is not None

def remove_tag(contact_id, tag):
    tags_data = ghl_get(f"/contacts/{contact_id}")
    if not tags_data or "contact" not in tags_data:
        return False
    current = tags_data["contact"].get("tags", [])
    if tag not in current:
        return True
    current.remove(tag)
    result = ghl_put(f"/contacts/{contact_id}", {"tags": current})
    return result is not None

def send_sms(contact_id, phone, message):
    if not phone:
        log(f"No phone for {contact_id}, skip SMS", "WARN")
        return False
    data = {
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    }
    result = ghl_post("/conversations/messages", data, headers=CONVERSATIONS_HEADERS)
    if result:
        log(f"SMS sent to {contact_id}: {message[:60]}...")
        return True
    return False

def send_email(contact_id, email, subject, html_body):
    if not email:
        log(f"No email for {contact_id}, skip email", "WARN")
        return False
    data = {
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": html_body,
    }
    result = ghl_post("/conversations/messages", data, headers=CONVERSATIONS_HEADERS)
    if result:
        log(f"Email sent to {contact_id}: {subject}")
        return True
    return False

def create_task(contact_id, title, due_date=None):
    if due_date is None:
        due_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    data = {
        "contactId": contact_id,
        "title": title,
        "dueDate": due_date,
        "completed": False,
    }
    # GHL tasks endpoint
    result = ghl_post(f"/contacts/{contact_id}/tasks", data)
    if result:
        log(f"Task created: {title}")
        return True
    return False

def ntfy(topic, title, message, priority="default"):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        safe_msg = "".join(c for c in message if ord(c) < 128).strip()
        r = requests.post(
            f"https://ntfy.sh/{topic}",
            data=safe_msg.encode("utf-8"),
            headers={
                "Title": safe_title[:256],
                "Priority": priority,
                "Tags": "phone,white_check_mark",
            },
            timeout=10,
        )
        return r.status_code == 200
    except Exception as e:
        log(f"ntfy failed: {e}", "ERROR")
        return False

# ─── Message Templates ───────────────────────────────────────────────────────

def get_name(contact):
    first = contact.get("firstName", contact.get("first_name", ""))
    return first or "there"

def get_company(contact):
    return contact.get("companyName", contact.get("company_name", "your business"))

def get_plan_info(state_entry):
    plan = state_entry.get("plan", "Starter")
    amount = "$997" if plan.lower() == "pro" else "$497"
    return plan, amount

def get_billing_date(enrolled_at):
    """Billing starts Day 15 after enrollment."""
    try:
        dt = datetime.fromisoformat(enrolled_at.replace("Z", "+00:00"))
    except Exception:
        dt = datetime.now()
    billing = dt + timedelta(days=15)
    return billing.strftime("%B %d")

# ─── Day 0 Messages ─────────────────────────────────────────────────────────

def day0_sms(contact, state_entry):
    name = get_name(contact)
    return (
        f"Hey {name}, you're all set. Jessica is going live on your phones today. "
        f"I'll text you once she's ready to test — usually within a few hours. "
        f"Text me anytime: (615) 653-9004"
    )

def day0_email_subject(contact):
    return f"Jessica is live — here's what happens next"

def day0_email_body(contact, state_entry):
    name = get_name(contact)
    company = get_company(contact)
    plan, amount = get_plan_info(state_entry)
    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<p>Hey {name},</p>

<p>Jessica is officially answering your phones. Here's what you need to know:</p>

<p><strong>1. Test her yourself</strong><br>
Call your business number from a different phone. Try "I need an appointment" and hear her handle it.</p>

<p><strong>2. Check your bookings</strong><br>
Every call she books shows up in your calendar. You'll also get a text notification for each one.</p>

<p><strong>3. Need anything?</strong><br>
Text me directly at (615) 653-9004. I respond in minutes, not days.</p>

<p><strong>Your plan:</strong> {plan} ({amount}/mo)<br>
<strong>Trial:</strong> 14 days free — billing starts on day 15<br>
<strong>Setup fee:</strong> Waived</p>

<p>I'll check in with you in a few days to make sure everything's dialed in.</p>

<p>— Wallace<br>
The Call Taker<br>
(615) 653-9004</p>
</div>"""

# ─── Day 3 Messages ─────────────────────────────────────────────────────────

def day3_sms(contact, state_entry):
    name = get_name(contact)
    return (
        f"Hey {name}, how are the calls going? Anything Jessica should handle differently? "
        f"I can tweak her script in 5 minutes."
    )

# ─── Day 7 Messages ─────────────────────────────────────────────────────────

def day7_sms(contact, state_entry):
    name = get_name(contact)
    company = get_company(contact)
    return (
        f"Hey {name}, this week Jessica handled calls for {company}. "
        f"Quick 15-min tuning call this week — when works?"
    )

def day7_email_subject(contact):
    company = get_company(contact)
    return f"Your first week with Jessica — the numbers"

def day7_email_body(contact, state_entry):
    name = get_name(contact)
    company = get_company(contact)
    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<p>Hey {name},</p>

<p>Here's what Jessica did for {company} this week:</p>

<ul>
<li><strong>[X] calls answered</strong> (including [Y] after hours)</li>
<li><strong>[Z] appointments booked</strong></li>
<li><strong>Estimated revenue captured: $[amount]</strong></li>
</ul>

<p><em>[One specific win — e.g., "Tuesday at 9:47 PM, Jessica booked a $600 emergency repair that would have gone to voicemail."]</em></p>

<p>We tweaked [specific thing] on our tuning call. She'll be even sharper this week.</p>

<p>— Wallace<br>
The Call Taker<br>
(615) 653-9004</p>
</div>"""

# ─── Day 10 Messages ────────────────────────────────────────────────────────

def day10_sms(contact, state_entry):
    name = get_name(contact)
    _, amount = get_plan_info(state_entry)
    billing_date = get_billing_date(state_entry.get("enrolled_at", ""))
    return (
        f"Hey {name}, your 14-day trial ends in 4 days. Billing starts {billing_date} "
        f"at {amount}/mo. Want to do a quick call before then?"
    )

# ─── Day 14 Messages ────────────────────────────────────────────────────────

def day14_sms(contact, state_entry):
    name = get_name(contact)
    billing_date = get_billing_date(state_entry.get("enrolled_at", ""))
    return (
        f"Hey {name}, your trial is done and Jessica is officially part of your team. "
        f"First invoice goes out {billing_date}. Any questions, I'm a text away."
    )

# ─── Day 30 Messages ────────────────────────────────────────────────────────

def day30_email_subject(contact):
    return f"One month with Jessica — here's your report"

def day30_email_body(contact, state_entry):
    name = get_name(contact)
    company = get_company(contact)
    plan, amount = get_plan_info(state_entry)
    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<p>Hey {name},</p>

<p>One month in. Here's what Jessica did for {company}:</p>

<ul>
<li><strong>[X] total calls answered</strong></li>
<li><strong>[Y] after-hours calls caught</strong></li>
<li><strong>[Z] appointments booked</strong></li>
<li><strong>Estimated revenue captured: $[amount]</strong></li>
<li><strong>Biggest single job: $[amount]</strong> — [brief description]</li>
</ul>

<p>That's a [ROI]x return on your {amount}/mo investment.</p>

<p>Based on our call, I've [updated X / added Y / tweaked Z].</p>

<p>Here's to month 2.</p>

<p>— Wallace<br>
The Call Taker<br>
(615) 653-9004</p>
</div>"""

# ─── Core Commands ───────────────────────────────────────────────────────────

def cmd_scan():
    """Find new customers tagged new-customer, send Day 0 messages."""
    log("=== SCAN: Looking for new customers ===")
    state = load_state()
    contacts = get_contacts_by_tag(TRIGGER_TAG)

    if not contacts:
        log("No new customers found")
        return

    enrolled = 0
    for contact in contacts:
        cid = contact.get("id")
        tags = contact.get("tags", [])

        # Skip if already enrolled or excluded
        if cid in state["customers"]:
            continue
        if any(t in EXCLUDE_TAGS for t in tags):
            log(f"Skipping {cid} — excluded tag")
            continue

        name = get_name(contact)
        company = get_company(contact)
        phone = contact.get("phone", "")
        email = contact.get("email", "")

        # Detect plan from tags
        plan = "Starter"
        if "pro-plan" in tags or "997-plan" in tags:
            plan = "Pro"

        # Detect vertical from tags
        vertical = "service"
        for v in ["hvac", "plumbing", "dental", "roofing", "electrical", "locksmith",
                   "towing", "pest-control", "legal", "medspa", "veterinary"]:
            if v in tags:
                vertical = v
                break

        now = datetime.now().isoformat()
        state_entry = {
            "enrolled_at": now,
            "name": name,
            "company": company,
            "phone": phone,
            "email": email,
            "plan": plan,
            "vertical": vertical,
            "touches_sent": [],
        }

        # ── Day 0: Welcome SMS ──
        sms_msg = day0_sms(contact, state_entry)
        if send_sms(cid, phone, sms_msg):
            state_entry["touches_sent"].append({"touch": "day0-sms", "at": now})

        time.sleep(2)

        # ── Day 0: Welcome Email ──
        subject = day0_email_subject(contact)
        body = day0_email_body(contact, state_entry)
        if send_email(cid, email, subject, body):
            state_entry["touches_sent"].append({"touch": "day0-email", "at": now})

        # ── Day 0: ntfy URGENT ──
        plan_label, amount = get_plan_info(state_entry)
        ntfy(
            NTFY_URGENT,
            f"NEW CUSTOMER: {name}",
            f"{company} | {plan_label} {amount}/mo | {vertical}\nStart config NOW\nPhone: {phone}",
            priority="urgent"
        )

        # ── Day 0: GHL task ──
        create_task(cid, f"Configure Jessica for {company}")

        # ── Tag: in-trial ──
        add_tag(cid, IN_TRIAL_TAG)

        state["customers"][cid] = state_entry
        state["stats"]["enrolled"] = state["stats"].get("enrolled", 0) + 1
        enrolled += 1
        log(f"ENROLLED: {name} ({company}) — {plan_label} {amount}/mo")
        time.sleep(2)

    save_state(state)
    log(f"Scan complete. Enrolled {enrolled} new customers.")

def cmd_touchpoints():
    """Run scheduled touchpoints for all active customers."""
    log("=== TOUCHPOINTS: Running scheduled touches ===")
    state = load_state()
    now = datetime.now()
    touches_sent = 0

    for cid, entry in list(state["customers"].items()):
        try:
            enrolled_dt = datetime.fromisoformat(entry["enrolled_at"].replace("Z", "+00:00"))
        except Exception:
            continue

        days_since = (now - enrolled_dt).total_seconds() / 86400
        name = entry.get("name", "Customer")
        company = entry.get("company", "Business")
        phone = entry.get("phone", "")
        email = entry.get("email", "")
        sent_touches = [t["touch"] for t in entry.get("touches_sent", [])]

        # Build a fake contact dict for message functions
        contact = {
            "firstName": name,
            "companyName": company,
            "phone": phone,
            "email": email,
        }

        # ── Day 3 ──
        if days_since >= 3 and "day3-sms" not in sent_touches:
            msg = day3_sms(contact, entry)
            if send_sms(cid, phone, msg):
                entry["touches_sent"].append({"touch": "day3-sms", "at": now.isoformat()})
                touches_sent += 1
            add_tag(cid, TOUCHPOINT_TAGS[3])
            ntfy(NTFY_SALES, f"Day 3 check-in: {name}",
                 f"{company} — reply if they texted back", priority="default")
            time.sleep(2)

        # ── Day 7 ──
        if days_since >= 7 and "day7-sms" not in sent_touches:
            msg = day7_sms(contact, entry)
            if send_sms(cid, phone, msg):
                entry["touches_sent"].append({"touch": "day7-sms", "at": now.isoformat()})
                touches_sent += 1
            time.sleep(2)

            subject = day7_email_subject(contact)
            body = day7_email_body(contact, entry)
            if send_email(cid, email, subject, body):
                entry["touches_sent"].append({"touch": "day7-email", "at": now.isoformat()})
                touches_sent += 1

            add_tag(cid, TOUCHPOINT_TAGS[7])
            ntfy(NTFY_URGENT, f"Day 7 tuning due: {name}",
                 f"{company} — book tuning call\nPhone: {phone}", priority="high")
            time.sleep(2)

        # ── Day 10 ──
        if days_since >= 10 and "day10-sms" not in sent_touches:
            msg = day10_sms(contact, entry)
            if send_sms(cid, phone, msg):
                entry["touches_sent"].append({"touch": "day10-sms", "at": now.isoformat()})
                touches_sent += 1
            add_tag(cid, TOUCHPOINT_TAGS[10])
            plan_label, amount = get_plan_info(entry)
            ntfy(NTFY_URGENT, f"Trial ending in 4 days: {name}",
                 f"{company} | {plan_label} {amount}/mo\nConfirm payment method is set up",
                 priority="high")
            time.sleep(2)

        # ── Day 14 ──
        if days_since >= 14 and "day14-sms" not in sent_touches:
            msg = day14_sms(contact, entry)
            if send_sms(cid, phone, msg):
                entry["touches_sent"].append({"touch": "day14-sms", "at": now.isoformat()})
                touches_sent += 1

            # Tag swap
            add_tag(cid, TRIAL_COMPLETE_TAG)
            add_tag(cid, PAYING_TAG)
            remove_tag(cid, TRIGGER_TAG)
            remove_tag(cid, IN_TRIAL_TAG)
            add_tag(cid, TOUCHPOINT_TAGS[14])

            state["stats"]["trial_complete"] = state["stats"].get("trial_complete", 0) + 1
            state["stats"]["paying"] = state["stats"].get("paying", 0) + 1

            ntfy(NTFY_URGENT, f"TRIAL COMPLETE: {name}",
                 f"{company} — now a paying customer!", priority="high")
            log(f"TRIAL COMPLETE: {name} ({company})")
            time.sleep(2)

        # ── Day 30 ──
        if days_since >= 30 and "day30-email" not in sent_touches:
            subject = day30_email_subject(contact)
            body = day30_email_body(contact, entry)
            if send_email(cid, email, subject, body):
                entry["touches_sent"].append({"touch": "day30-email", "at": now.isoformat()})
                touches_sent += 1

            add_tag(cid, TOUCHPOINT_TAGS[30])
            ntfy(NTFY_URGENT, f"30-day review due: {name}",
                 f"{company} — run value review call\nPhone: {phone}", priority="high")
            log(f"DAY 30: {name} ({company}) — value review due")
            time.sleep(2)

    save_state(state)
    log(f"Touchpoints complete. Sent {touches_sent} touches.")

def cmd_status():
    """Show all active customers and their onboarding day."""
    state = load_state()
    now = datetime.now()

    print("=" * 70)
    print("  ONBOARDING STATUS")
    print("=" * 70)
    print()

    stats = state.get("stats", {})
    print(f"  Enrolled: {stats.get('enrolled', 0)}")
    print(f"  Trial Complete: {stats.get('trial_complete', 0)}")
    print(f"  Paying: {stats.get('paying', 0)}")
    print()

    customers = state.get("customers", {})
    if not customers:
        print("  No customers enrolled yet.")
        return

    print(f"  {'Name':<20} {'Company':<25} {'Plan':<10} {'Day':<6} {'Touches':<8}")
    print(f"  {'─'*20} {'─'*25} {'─'*10} {'─'*6} {'─'*8}")

    for cid, entry in sorted(customers.items(), key=lambda x: x[1].get("enrolled_at", "")):
        try:
            enrolled_dt = datetime.fromisoformat(entry["enrolled_at"].replace("Z", "+00:00"))
            days = int((now - enrolled_dt).total_seconds() / 86400)
        except Exception:
            days = 0

        name = entry.get("name", "Unknown")[:20]
        company = entry.get("company", "Unknown")[:25]
        plan = entry.get("plan", "?")
        touch_count = len(entry.get("touches_sent", []))

        print(f"  {name:<20} {company:<25} {plan:<10} {days:<6} {touch_count:<8}")

    print()

def cmd_preview():
    """Preview all message copy for each touchpoint."""
    fake_contact = {"firstName": "Mike", "companyName": "Mike's HVAC"}
    fake_entry = {"plan": "Starter", "enrolled_at": datetime.now().isoformat()}

    print("=" * 70)
    print("  MESSAGE PREVIEW — 30-Day Onboarding Sequence")
    print("=" * 70)

    touches = [
        ("DAY 0 — Welcome SMS", day0_sms(fake_contact, fake_entry)),
        ("DAY 0 — Welcome Email", f"Subject: {day0_email_subject(fake_contact)}\n  (HTML email body — see source for full content)"),
        ("DAY 3 — Check-in SMS", day3_sms(fake_contact, fake_entry)),
        ("DAY 7 — Tuning SMS", day7_sms(fake_contact, fake_entry)),
        ("DAY 7 — First Wins Email", f"Subject: {day7_email_subject(fake_contact)}\n  (HTML email body — Wallace fills in numbers)"),
        ("DAY 10 — Pre-trial-end SMS", day10_sms(fake_contact, fake_entry)),
        ("DAY 14 — Trial complete SMS", day14_sms(fake_contact, fake_entry)),
        ("DAY 30 — Month 1 Report Email", f"Subject: {day30_email_subject(fake_contact)}\n  (HTML email body — Wallace fills in numbers)"),
    ]

    for label, content in touches:
        print()
        print(f"{'─' * 70}")
        print(f"  {label}")
        print(f"{'─' * 70}")
        print(f"  {content}")

    print()
    print("=" * 70)

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: onboarding-engine.py <command>")
        print("Commands: scan, run, status, preview")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    try:
        if cmd == "scan":
            cmd_scan()
        elif cmd == "run":
            cmd_scan()
            cmd_touchpoints()
        elif cmd == "status":
            cmd_status()
        elif cmd == "preview":
            cmd_preview()
        else:
            print(f"Unknown command: {cmd}")
            print("Commands: scan, run, status, preview")
            sys.exit(1)
    except Exception as e:
        log(f"CRASH: {e}\n{traceback.format_exc()}", "CRITICAL")
        ntfy(NTFY_SYSTEM, "CRASH: onboarding-engine",
             f"Command: {cmd}\nError: {str(e)[:200]}", priority="urgent")
        sys.exit(1)

if __name__ == "__main__":
    main()
