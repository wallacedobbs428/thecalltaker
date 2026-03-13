#!/usr/bin/env python3
"""
Hot Lead Follow-Up Engine — The Call Taker
Automated follow-up sequence for hot leads. Runs every 4 hours via launchd.

Sequence:
  Day 0 (immediate): SMS — pain hook + demo line CTA
  Day 1: Email — missed call cost + ROI + scarcity
  Day 3: SMS — "still losing calls" + direct question
  Day 5: Email — case study + social proof
  Day 7: SMS — final breakup message + urgency

Usage:
  python3 hot-lead-followup.py run       # Process all hot leads
  python3 hot-lead-followup.py status    # Show current state
  python3 hot-lead-followup.py preview   # Preview next sends (dry run)
"""

import json
import sys
import os
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ===================================================
# CONFIG
# ===================================================

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "hot-lead-followup-state.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "hot-lead-followup.log")

HOT_TAGS = ["hot-lead", "hot-demo", "engaged-demo", "demo-caller", "pilot-candidate"]
SKIP_TAGS = ["customer", "active-client", "pilot-active", "pilot-converted",
             "do-not-contact", "unsubscribed", "demo-booked"]

DEMO_LINE = "(615) 784-5747"

# Industry job words
JOB_WORDS = {
    "hvac": "HVAC job", "plumbing": "plumbing job", "dental": "new patient",
    "roofing": "roofing lead", "locksmith": "lockout call", "electrical": "service call",
    "towing": "tow call", "water-damage": "water damage job", "pest-control": "service call",
    "med-spa": "appointment", "legal": "client inquiry", "veterinary": "emergency call",
}

# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] HOTLEAD: {msg}"
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
    for attempt in range(3):
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            if e.code == 429:
                wait = 30 * (attempt + 1)
                log(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            error_body = e.read().decode() if e.fp else ""
            log(f"GHL API Error {e.code}: {method} {path} — {error_body[:200]}")
            return None
        except (URLError, Exception) as e:
            log(f"GHL Error: {method} {path} — {e}")
            if attempt < 2:
                time.sleep(5)
                continue
            return None
    return None


def send_sms(contact_id, message):
    """Send SMS via GHL conversations API."""
    resp = ghl_request("POST", "/conversations/messages", {
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    }, version="2021-04-15")
    return resp is not None


def send_email(contact_id, subject, html_body):
    """Send email via GHL conversations API."""
    resp = ghl_request("POST", "/conversations/messages", {
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": html_body,
    }, version="2021-04-15")
    return resp is not None


def add_tag(contact_id, tag):
    """Add a tag to a GHL contact."""
    # First get existing tags
    contact = ghl_request("GET", f"/contacts/{contact_id}")
    if not contact or "contact" not in contact:
        return False
    existing = contact["contact"].get("tags", [])
    if tag in existing:
        return True
    existing.append(tag)
    resp = ghl_request("PUT", f"/contacts/{contact_id}", {"tags": existing})
    return resp is not None


def save_state(data):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, STATE_FILE)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"leads": {}, "last_run": None, "sends_today": 0, "last_send_date": None}


# ===================================================
# SEQUENCE MESSAGES
# ===================================================

def get_sequence_messages(lead):
    """Return the 5-touch sequence for a lead."""
    first = lead.get("first_name", "")
    company = lead.get("company", "")
    industry = lead.get("industry", "unknown")
    job_word = JOB_WORDS.get(industry, "service call")

    return {
        0: {
            "type": "sms",
            "message": f"Hey{' ' + first if first else ''}, imagine it's 9pm and a customer calls your business needing help — but nobody picks up. That's a {job_word} gone to your competitor.\n\nCall our demo line and hear how AI handles it: {DEMO_LINE}\n\nFree 14-day pilot, no card needed. — Wallace, The Call Taker"
        },
        1: {
            "type": "email",
            "subject": f"{'[' + company + '] ' if company else ''}You're losing $2K-$10K/mo in missed calls",
            "html": f"""<p>Hey{' ' + first if first else ''},</p>
<p>Quick math: if you miss just <b>3 calls a week</b> and each {job_word} is worth $300-800... that's <b>$3,600-$9,600/month</b> walking straight to your competitor.</p>
<p>Our AI receptionist answers every call in 2 rings, 24/7. Books appointments. Texts the customer details. Sounds human.</p>
<p><b>Hear it yourself:</b> Call <a href="tel:+16157845747">{DEMO_LINE}</a></p>
<p>We're running free 14-day pilots for <b>3 businesses this month</b>. No card, no contracts, cancel anytime.</p>
<p>Want one of the spots?</p>
<p>— Wallace Dobbs<br>The Call Taker<br>thecalltaker.com</p>"""
        },
        3: {
            "type": "sms",
            "message": f"Hey{' ' + first if first else ''} — quick question: how many calls did {'you' if not company else company} miss this past weekend?\n\nMost {industry if industry != 'unknown' else 'service'} businesses lose 5-10 calls/week after hours. Each one is $300+ gone.\n\nWe can fix that in 24 hours. Free pilot — {DEMO_LINE}"
        },
        5: {
            "type": "email",
            "subject": f"How a {industry if industry != 'unknown' else 'small'} business stopped losing $8K/mo",
            "html": f"""<p>Hey{' ' + first if first else ''},</p>
<p>Quick story: a {industry if industry != 'unknown' else 'service'} business owner was missing 40% of incoming calls. After-hours, weekends, lunch breaks — calls going to voicemail and never coming back.</p>
<p>They started a free pilot with us. <b>First week: 23 calls answered that would've been missed.</b> That's over $6,000 in jobs they would've lost.</p>
<p>After the pilot they signed up at $97/mo. Their words: <i>"Best money I've ever spent."</i></p>
<p><b>We have 1 pilot spot left this month.</b></p>
<p>Want it? Just reply "YES" and I'll set it up today.</p>
<p>— Wallace<br>The Call Taker</p>"""
        },
        7: {
            "type": "sms",
            "message": f"Last message from me{', ' + first if first else ''} — we had a free pilot spot reserved but I need to give it to someone else by end of day.\n\nIf you ever want to stop missing calls: {DEMO_LINE}\n\nNo hard feelings either way. — Wallace"
        },
    }


# ===================================================
# CORE ENGINE
# ===================================================

def get_hot_leads():
    """Fetch all hot-tagged contacts."""
    hot_leads = []
    seen_ids = set()

    for tag in HOT_TAGS:
        page = 1
        while True:
            resp = ghl_request("GET",
                f"/contacts/?locationId={GHL_LOCATION_ID}&limit=100&page={page}&query={tag}")
            if not resp or "contacts" not in resp:
                break
            batch = resp["contacts"]
            if not batch:
                break
            for c in batch:
                cid = c.get("id", "")
                if cid not in seen_ids:
                    seen_ids.add(cid)
                    hot_leads.append(c)
            if len(batch) < 100:
                break
            page += 1
            time.sleep(0.5)

    return hot_leads


def detect_industry(tags):
    for tag in tags:
        for ind in JOB_WORDS:
            if ind in tag.lower():
                return ind
    return "unknown"


def process_leads(dry_run=False):
    """Process all hot leads through the follow-up sequence."""
    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")

    # Reset daily counter
    if state.get("last_send_date") != today:
        state["sends_today"] = 0
        state["last_send_date"] = today

    raw_leads = get_hot_leads()
    log(f"Found {len(raw_leads)} hot leads")

    sent_count = 0
    skipped_count = 0

    for contact in raw_leads:
        cid = contact.get("id", "")
        tags = [t.lower() for t in contact.get("tags", [])]
        first = contact.get("firstName", "") or ""
        company = contact.get("companyName", "") or ""
        phone = contact.get("phone", "") or ""
        email = contact.get("email", "") or ""

        # Skip if tagged with exclusion
        if any(t in tags for t in SKIP_TAGS):
            continue

        # Skip if no way to contact
        if not phone and not email:
            continue

        industry = detect_industry(tags)
        created = contact.get("dateAdded", contact.get("createdAt", ""))

        # Calculate days since creation
        days_since = 0
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                days_since = (datetime.now(created_dt.tzinfo) - created_dt).days
            except:
                try:
                    created_dt = datetime.strptime(created[:10], "%Y-%m-%d")
                    days_since = (datetime.now() - created_dt).days
                except:
                    pass

        # Get lead state
        lead_state = state.get("leads", {}).get(cid, {
            "touches_sent": [],
            "last_touch_date": None,
            "enrolled": today,
        })

        # Build sequence
        lead_info = {"first_name": first, "company": company, "industry": industry}
        sequence = get_sequence_messages(lead_info)

        # Find next touch to send
        sent_days = set(lead_state.get("touches_sent", []))

        for day in sorted(sequence.keys()):
            if day in sent_days:
                continue
            if days_since < day:
                break  # Not time yet

            msg = sequence[day]

            # Check we can send this type
            if msg["type"] == "sms" and not phone:
                continue
            if msg["type"] == "email" and not email:
                continue

            # Daily send cap (100/day)
            if state["sends_today"] >= 100:
                log("Daily send cap reached (100)")
                break

            if dry_run:
                log(f"[DRY RUN] Would send Day {day} {msg['type']} to {first} {company} ({cid})")
                sent_count += 1
            else:
                success = False
                if msg["type"] == "sms":
                    success = send_sms(cid, msg["message"])
                elif msg["type"] == "email":
                    success = send_email(cid, msg["subject"], msg["html"])

                if success:
                    log(f"Sent Day {day} {msg['type']} to {first} {company}")
                    lead_state.setdefault("touches_sent", []).append(day)
                    lead_state["last_touch_date"] = today
                    state["sends_today"] = state.get("sends_today", 0) + 1
                    sent_count += 1

                    # Tag the contact
                    add_tag(cid, f"followup-day-{day}")
                    if day == 0:
                        add_tag(cid, "contacted")
                    if day == 7:
                        add_tag(cid, "breakup-sent")
                else:
                    log(f"FAILED Day {day} {msg['type']} to {first} {company}")

                time.sleep(1)  # Rate limit between sends

            break  # Only send one touch per lead per run

        # Save lead state
        state.setdefault("leads", {})[cid] = lead_state

    state["last_run"] = datetime.now().isoformat()
    if not dry_run:
        save_state(state)

    log(f"Done. Sent: {sent_count}, Skipped: {skipped_count}")
    return sent_count


def show_status():
    """Show current follow-up state."""
    state = load_state()
    leads = state.get("leads", {})
    last_run = state.get("last_run", "never")
    sends = state.get("sends_today", 0)

    print()
    print(f"  Hot Lead Follow-Up Status")
    print(f"  Last run: {last_run}")
    print(f"  Sends today: {sends}")
    print(f"  Leads tracked: {len(leads)}")
    print()

    # Count by step
    step_counts = {0: 0, 1: 0, 3: 0, 5: 0, 7: 0}
    for lid, lstate in leads.items():
        touches = lstate.get("touches_sent", [])
        if touches:
            last_day = max(touches)
            if last_day in step_counts:
                step_counts[last_day] += 1

    for day, count in sorted(step_counts.items()):
        bar = "#" * count
        print(f"  Day {day}: {count:3d} {bar}")
    print()


# ===================================================
# MAIN
# ===================================================

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"

    if cmd == "run":
        process_leads(dry_run=False)
    elif cmd == "preview":
        process_leads(dry_run=True)
    elif cmd == "status":
        show_status()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 hot-lead-followup.py [run|preview|status]")
        sys.exit(1)
