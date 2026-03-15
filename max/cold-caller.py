#!/usr/bin/env python3
"""
COLD CALLER — Bland.ai Outbound Call Engine
March 2026

Makes outbound cold calls via Bland.ai to HVAC/service business leads.
20 calls per batch, scheduled 10am + 6pm via launchd.

Usage:
  python3 cold-caller.py call      # Make outbound calls (up to 20)
  python3 cold-caller.py status    # Print current stats
  python3 cold-caller.py check     # Check outcomes of previous calls
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

BLAND_API_KEY = "org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969"
BLAND_BASE = "https://api.bland.ai/v1"

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

NTFY_OPS_TOPIC = "tct-activity-cn1Aqa85"
NTFY_WAR_TOPIC = "tct-urgent-Hk9UOEZR"

# Voice AI agent for cold calls — universal demo prompt
VOICE_AGENT_ID = "695947c64b9ed67d8f1077ad"

CALLER_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(CALLER_DIR, "cold-caller-log.txt")
STATE_FILE = os.path.join(CALLER_DIR, "cold-caller-state.json")

MAX_CALLS_PER_BATCH = 20
DELAY_BETWEEN_CALLS = 5  # seconds between API calls

# Cold call script — kept short for AI voice
COLD_CALL_TASK = """You are calling on behalf of The Call Taker, an AI receptionist service.
Your goal: Find out if they miss calls after hours, then offer a free 14-day pilot.

Opening: "Hey, this is a quick call from The Call Taker. We help {industry} companies like {company}
catch every call 24/7 with AI — no voicemail, no missed jobs. Do you ever miss calls after hours or
when you're on a job?"

If YES or interested: "We're offering a free 14-day pilot — no card, no commitment.
Your callers talk to an AI that sounds like a real receptionist, books jobs on your calendar,
and texts you the details. Can I set that up for you?"

If they want more info: "You can call our demo line right now at 615-784-5747 to hear it live.
Or I can have Wallace, our founder, give you a call back. What works better?"

If NO or not interested: "No worries at all. If you ever want to hear it, our demo line is
615-784-5747. Have a great day!"

Keep it under 60 seconds. Be conversational, not salesy."""


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] CALLER: {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass


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
        log(f"Bland API Error {e.code}: {method} {path} — {error_body[:300]}")
        if e.code == 402:
            log("BLAND.AI BALANCE DEPLETED — stopping all calls")
            ntfy(NTFY_WAR_TOPIC,
                 "[CRITICAL] Bland.ai balance depleted",
                 "Cold caller stopped — Bland.ai returned 402. Top up balance to resume.",
                 priority="urgent", tags="warning,money_with_wings")
        return None
    except URLError as e:
        log(f"Bland Network Error: {method} {path} — {e.reason}")
        return None
    except Exception as e:
        log(f"Bland Error: {method} {path} — {e}")
        return None


def ghl_request(method, path, body=None, version="2021-07-28"):
    url = f"{GHL_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": version,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "ColdCaller/1.0 TheCallTaker",
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
    except Exception as e:
        log(f"ntfy error: {e}")


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {
        "calls_made": [],
        "call_ids": {},
        "total_calls": 0,
        "total_connected": 0,
        "total_interested": 0,
        "last_run": None,
        "daily_count": 0,
        "daily_date": None,
    }


def save_state(state):
    import tempfile
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, default=str)
    os.replace(tmp, STATE_FILE)


# ===================================================
# GHL LEAD FETCHING
# ===================================================

def get_callable_leads():
    """Fetch leads from GHL that have phone numbers and haven't been cold-called."""
    leads = []
    page = 1
    while page <= 5:
        resp = ghl_request("GET", f"/contacts/?locationId={GHL_LOCATION_ID}&limit=100&page={page}")
        if not resp or "contacts" not in resp:
            break
        contacts = resp["contacts"]
        if not contacts:
            break
        for c in contacts:
            phone = c.get("phone", "")
            tags = [t.lower() for t in c.get("tags", [])]
            # Skip: no phone, already called, customers, do-not-contact
            if not phone or len(phone) < 10:
                continue
            if "cold-called" in tags or "customer" in tags or "active-client" in tags:
                continue
            if "do-not-contact" in tags or "unsubscribed" in tags or "pilot-active" in tags:
                continue
            leads.append({
                "id": c.get("id"),
                "phone": phone,
                "firstName": c.get("firstName", "Owner"),
                "companyName": c.get("companyName", "your company"),
                "tags": tags,
                "industry": next((t for t in tags if t in [
                    "hvac", "plumbing", "roofing", "electrical", "locksmith",
                    "dental", "medspa", "legal", "towing", "veterinary",
                    "pest-control", "auto-repair", "cleaning", "water-damage",
                    "property-management", "landscaping", "general-contractor",
                    "garage-door", "funeral"
                ]), "service"),
            })
        page += 1
        time.sleep(1)
    return leads


# ===================================================
# CALL ENGINE
# ===================================================

def make_call(lead):
    """Place a single outbound call via Bland.ai."""
    phone = lead["phone"]
    company = lead.get("companyName", "your company")
    industry = lead.get("industry", "service")

    task = COLD_CALL_TASK.format(
        company=company,
        industry=industry,
    )

    body = {
        "phone_number": phone,
        "task": task,
        "voice_id": "w9rPM8AIZle60Nbpw7nl",
        "reduce_latency": True,
        "wait_for_greeting": True,
        "max_duration": 120,
        "record": True,
        "metadata": {
            "contact_id": lead.get("id", ""),
            "company": company,
            "industry": industry,
            "source": "cold-caller",
        },
    }

    resp = bland_request("POST", "/calls", body)
    if resp and resp.get("call_id"):
        return resp["call_id"]
    return None


def tag_contact(contact_id, tag):
    """Add a tag to a GHL contact."""
    resp = ghl_request("GET", f"/contacts/{contact_id}")
    if not resp or "contact" not in resp:
        return
    existing_tags = resp["contact"].get("tags", [])
    if tag not in existing_tags:
        existing_tags.append(tag)
        ghl_request("PUT", f"/contacts/{contact_id}", {"tags": existing_tags})


def run_calls():
    """Make up to MAX_CALLS_PER_BATCH outbound calls."""
    state = load_state()

    # Reset daily counter if new day
    today = datetime.now().strftime("%Y-%m-%d")
    if state.get("daily_date") != today:
        state["daily_count"] = 0
        state["daily_date"] = today

    if state["daily_count"] >= 40:
        log("Daily limit reached (40 calls). Stopping.")
        return

    log(f"=== COLD CALLER: Starting batch (daily count: {state['daily_count']}) ===")

    leads = get_callable_leads()
    if not leads:
        log("No callable leads found.")
        return

    already_called = set(state.get("calls_made", []))
    available = [l for l in leads if l["phone"] not in already_called]

    if not available:
        log("All leads have been called. Need new leads.")
        return

    batch = available[:MAX_CALLS_PER_BATCH]
    called = 0
    failed = 0

    ntfy(NTFY_OPS_TOPIC,
         f"Cold Caller starting — {len(batch)} calls",
         f"Batch of {len(batch)} calls starting.\nDaily count: {state['daily_count']}",
         tags="telephone_receiver")

    for lead in batch:
        call_id = make_call(lead)
        if call_id:
            called += 1
            state["calls_made"].append(lead["phone"])
            state["call_ids"][call_id] = {
                "phone": lead["phone"],
                "contact_id": lead.get("id", ""),
                "company": lead.get("companyName", ""),
                "time": datetime.now().isoformat(),
            }
            state["total_calls"] += 1
            state["daily_count"] += 1

            # Tag in GHL
            if lead.get("id"):
                tag_contact(lead["id"], "cold-called")

            log(f"  CALL #{called}: {lead.get('companyName', 'Unknown')} ({lead['phone']}) — call_id: {call_id}")
        else:
            failed += 1
            log(f"  FAILED: {lead.get('companyName', 'Unknown')} ({lead['phone']})")

        save_state(state)
        time.sleep(DELAY_BETWEEN_CALLS)

    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    summary = f"Cold Caller batch complete: {called} called, {failed} failed\nDaily total: {state['daily_count']}"
    log(summary)

    if called > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"Cold Caller: {called} calls made",
             summary,
             tags="white_check_mark,telephone_receiver")


def check_outcomes():
    """Check call outcomes from Bland.ai and update state."""
    state = load_state()
    call_ids = state.get("call_ids", {})
    unchecked = {cid: data for cid, data in call_ids.items() if not data.get("checked")}

    if not unchecked:
        log("No unchecked calls.")
        return

    log(f"=== COLD CALLER: Checking {len(unchecked)} call outcomes ===")
    connected = 0
    interested = 0

    for call_id, data in unchecked.items():
        resp = bland_request("GET", f"/calls/{call_id}")
        if not resp:
            continue

        status = resp.get("status", "unknown")
        duration = resp.get("call_length", 0)
        answered = resp.get("answered_by", "unknown")
        transcript = resp.get("concatenated_transcript", "")

        data["checked"] = True
        data["status"] = status
        data["duration"] = duration
        data["answered_by"] = answered

        if status == "completed" and duration and duration > 10:
            connected += 1
            state["total_connected"] += 1
            log(f"  CONNECTED: {data.get('company', 'Unknown')} — {duration}s")

            # Check for interest signals in transcript
            interest_words = ["interested", "tell me more", "sounds good", "set that up",
                              "how much", "pricing", "free", "pilot", "demo", "yes"]
            if any(w in transcript.lower() for w in interest_words):
                interested += 1
                state["total_interested"] += 1
                data["interested"] = True

                # Hot lead alert
                ntfy(NTFY_WAR_TOPIC,
                     f"HOT COLD CALL: {data.get('company', 'Unknown')}",
                     f"Cold call showed interest!\nCompany: {data.get('company')}\nPhone: {data.get('phone')}\nDuration: {duration}s\n\nCall back NOW!",
                     priority="urgent",
                     tags="fire,telephone_receiver")

                # Tag in GHL
                if data.get("contact_id"):
                    tag_contact(data["contact_id"], "hot-lead")
        elif status == "completed":
            log(f"  SHORT: {data.get('company', 'Unknown')} — {duration}s (voicemail/hangup)")
        else:
            log(f"  {status.upper()}: {data.get('company', 'Unknown')}")

        time.sleep(1)

    save_state(state)
    log(f"Check complete: {connected} connected, {interested} interested out of {len(unchecked)} calls")


def print_status():
    state = load_state()
    print("\n" + "=" * 50)
    print("  COLD CALLER — STATUS")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print(f"  Total calls made:     {state.get('total_calls', 0)}")
    print(f"  Total connected:      {state.get('total_connected', 0)}")
    print(f"  Total interested:     {state.get('total_interested', 0)}")
    print(f"  Today's calls:        {state.get('daily_count', 0)}")
    print(f"  Leads called:         {len(state.get('calls_made', []))}")
    print(f"  Unchecked calls:      {sum(1 for d in state.get('call_ids', {}).values() if not d.get('checked'))}")
    print(f"  Last run:             {state.get('last_run', 'Never')}")
    print("=" * 50 + "\n")


# ===================================================
# MAIN
# ===================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "call":
        run_calls()
    elif cmd == "check":
        check_outcomes()
    elif cmd == "status":
        print_status()
    elif cmd == "all":
        run_calls()
        time.sleep(2)
        check_outcomes()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
