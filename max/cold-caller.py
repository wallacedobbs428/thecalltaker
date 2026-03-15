#!/usr/bin/env python3
"""
COLD CALLER — AI Outbound Calls via Bland.ai
Mar 12, 2026

Pulls hot leads from GHL, makes AI cold calls via Bland.ai (20 per batch),
tags contacts with outcomes, and fires ntfy alerts on interested prospects.

Zero external dependencies — stdlib only.
Uses curl for Bland.ai (system Python 3.9 SSL too old for their servers).

Usage:
  python3 cold-caller.py call     # Make a batch of 20 calls
  python3 cold-caller.py status   # Print dashboard
  python3 cold-caller.py check    # Check outcomes of last batch
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ===================================================
# CONFIG
# ===================================================

BLAND_API_KEY = "org_4830e9ebd85112b13b754d3fac8166c7473fa822df612c757b034479c1e0ed734323dd3f80be81139ead69"
BLAND_BASE = "https://api.bland.ai/v1"

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

NTFY_OPS_TOPIC = "tct-sales-63uYsIT9"
NTFY_WAR_TOPIC = "tct-urgent-Hk9UOEZR"
NTFY_CALLS_TOPIC = "tct-finishtask"

DEMO_LINE = "(615) 784-5747"
DEMO_URL = "https://thecalltaker.com/demo.html"

CALLER_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(CALLER_DIR, "cold-caller-state.json")
LOG_FILE = os.path.join(CALLER_DIR, "cold-caller-log.txt")

MAX_CALLS_PER_BATCH = 20
CALL_DELAY_SECONDS = 8  # seconds between dispatching calls

# Tags that disqualify a contact from being called
SKIP_TAGS = {"customer", "demo-booked", "pilot-active", "cold-called", "dnc",
             "do-not-call", "active-client", "bad-number"}

# Keywords that suggest interest in call transcript
INTEREST_KEYWORDS = [
    "yes", "interested", "tell me more", "demo", "sure",
    "sounds good", "let's do it", "sign me up", "set it up",
    "how does it work", "what's the cost", "send me info",
    "i'd like to", "absolutely", "that's interesting",
    "we could use that", "we need that", "perfect",
    "schedule", "book", "appointment", "show me",
]

# ===================================================
# AI CALL SCRIPT
# ===================================================

CALL_TASK = """You are calling on behalf of The Call Taker, an AI answering service for service businesses.

Your goal: Get the business owner interested in a free demo of The Call Taker.

Opening: "Hi, this is Sarah from The Call Taker. I'm reaching out because we help HVAC and service companies make sure they never miss a customer call — even after hours, on weekends, or when the team is busy. Do you have 30 seconds?"

If they say yes or seem open:
"Great — so what we do is really simple. When a customer calls your business and no one picks up, instead of getting voicemail, our AI receptionist answers the call. It sounds like a real person, gets the customer's info, books the appointment, and texts you the details. All for $497 a month, no contracts."

"Most companies we work with are losing 3 to 5 calls a week to voicemail. At $350 per job, that's over $4,000 a month walking out the door."

"Would you be open to hearing a quick demo? You'd actually call the AI yourself so you can hear exactly what your customers would experience."

If they say yes to the demo:
"Awesome! You can call our demo line right now or anytime — it's always live. The number is 615-784-5747. That's 615-784-5747. Or I can text you the link to book a walkthrough with our founder."

If they're busy:
"No problem at all — when would be a better time to call back? Or I can just text you our demo line number so you can try it whenever you have a minute."

If they say no or not interested:
"Totally understand. If you ever want to check it out, the demo line is 615-784-5747 — it's live 24/7. Have a great day!"

Important rules:
- Be friendly, conversational, not pushy
- Keep it under 2 minutes
- Always mention the demo line number: 615-784-5747
- If they ask about price: $497/month, no contracts, cancel anytime, set up in 48 hours
- If they ask who you are: "I work with The Call Taker — we're an AI answering service built specifically for service businesses"
"""

CALL_FIRST_SENTENCE = "Hi, this is Sarah from The Call Taker — I'm reaching out because we help service companies make sure they never miss a customer call. Do you have 30 seconds?"


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


def bland_request(method, path, body=None):
    """Call Bland.ai API via curl (system Python SSL too old for their servers)."""
    url = f"{BLAND_BASE}{path}"
    cmd = [
        "curl", "-s", "-X", method, url,
        "-H", f"Authorization: {BLAND_API_KEY}",
        "-H", "Content-Type: application/json",
    ]
    if body:
        cmd.extend(["-d", json.dumps(body)])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        if result.returncode != 0:
            log(f"Bland curl error: {method} {path} — exit {result.returncode}: {result.stderr[:300]}")
            return None
        if not result.stdout.strip():
            log(f"Bland empty response: {method} {path}")
            return None
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        log(f"Bland timeout: {method} {path}")
        return None
    except json.JSONDecodeError:
        log(f"Bland bad JSON: {method} {path} — {result.stdout[:300]}")
        return None
    except Exception as e:
        log(f"Bland error: {method} {path} — {e}")
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
        "calls_today": [],         # [{contact_id, company, phone, call_id, dispatched_at}]
        "call_history": [],        # all-time call records
        "last_call_date": None,
        "total_calls": 0,
        "total_answered": 0,
        "total_voicemail": 0,
        "total_no_answer": 0,
        "total_interested": 0,
        "total_batches": 0,
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


def is_callable(contact):
    """Check if contact is eligible for a cold call."""
    tags = {t.lower() for t in contact.get("tags", [])}
    # Skip anyone with exclusion tags
    if tags & SKIP_TAGS:
        return False
    # Must have a phone number
    phone = contact.get("phone", "")
    if not phone or len(phone) < 10:
        return False
    return True


def add_tag(contact_id, tag):
    """Add a tag to a GHL contact."""
    resp = ghl_request("PUT", f"/contacts/{contact_id}", {"tags": [tag]})
    if resp:
        log(f"Tagged {contact_id}: {tag}")
    return resp


def score_interest(transcript):
    """Score how interested the prospect sounded based on transcript."""
    if not transcript:
        return 0, []
    text = transcript.lower()
    matches = [kw for kw in INTEREST_KEYWORDS if kw in text]
    score = len(matches)
    # Negative signals
    for neg in ["not interested", "don't call", "stop calling", "no thanks", "remove me"]:
        if neg in text:
            score -= 3
    return max(score, 0), matches


# ===================================================
# COMMANDS
# ===================================================

def cmd_call():
    """Make a batch of cold calls via Bland.ai."""
    log("=== COLD CALLER: Starting batch ===")

    # Check Bland balance
    balance_resp = bland_request("GET", "/me")
    if balance_resp and "billing" in balance_resp:
        balance = balance_resp["billing"].get("current_balance", 0)
        log(f"Bland.ai balance: ${balance:.2f}")
        if balance < 2:
            log("LOW BALANCE — aborting")
            ntfy(NTFY_WAR_TOPIC, "COLD CALLER: LOW BALANCE",
                 f"Bland.ai balance: ${balance:.2f} — need to refill!",
                 priority="urgent", tags="warning")
            return
    else:
        log("Could not check Bland balance — proceeding anyway")

    # Load state
    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")

    # Reset daily counter if new day
    if state.get("last_call_date") != today:
        state["calls_today"] = []
        state["last_call_date"] = today

    already_called_ids = {c["contact_id"] for c in state.get("call_history", []) if c.get("contact_id")}
    today_count = len(state["calls_today"])

    if today_count >= MAX_CALLS_PER_BATCH:
        log(f"Already made {today_count} calls today — batch limit reached")
        return

    remaining = MAX_CALLS_PER_BATCH - today_count

    # Pull contacts from GHL
    log("Pulling contacts from GHL...")
    all_contacts = get_all_contacts()
    log(f"Total contacts in GHL: {len(all_contacts)}")

    # Filter to callable leads
    callable_leads = []
    for c in all_contacts:
        if not is_callable(c):
            continue
        if c["id"] in already_called_ids:
            continue
        callable_leads.append(c)

    log(f"Callable leads (not yet called, no skip tags, has phone): {len(callable_leads)}")

    if not callable_leads:
        log("No callable leads found")
        ntfy(NTFY_OPS_TOPIC, "Cold Caller: No leads to call",
             "All callable leads have been exhausted. Need more leads.",
             tags="warning")
        return

    # Take the batch
    batch = callable_leads[:remaining]
    log(f"Dispatching {len(batch)} calls...")

    ntfy(NTFY_OPS_TOPIC,
         f"COLD CALLER: {len(batch)} calls starting",
         f"Dispatching {len(batch)} AI calls via Bland.ai\nBalance: ${balance_resp['billing']['current_balance']:.2f}" if balance_resp and "billing" in balance_resp else f"Dispatching {len(batch)} AI calls",
         priority="high", tags="phone")

    dispatched = 0
    failed = 0

    for i, contact in enumerate(batch):
        phone = contact.get("phone", "")
        company = contact.get("companyName", "Unknown")
        first = contact.get("firstName", "there")
        contact_id = contact["id"]

        log(f"[{i+1}/{len(batch)}] Calling {company} at {phone}...")

        # Dispatch call via Bland.ai
        call_body = {
            "phone_number": phone,
            "task": CALL_TASK,
            "first_sentence": CALL_FIRST_SENTENCE,
            "wait_for_greeting": True,
            "record": True,
            "max_duration": 120,
            "model": "enhanced",
            "voice": "maya",
            "metadata": {
                "contact_id": contact_id,
                "company": company,
                "source": "max-cold-caller",
            },
        }

        resp = bland_request("POST", "/calls", call_body)

        if resp and resp.get("call_id"):
            call_id = resp["call_id"]
            log(f"Call dispatched: {company} -> {call_id}")
            dispatched += 1

            # Record in state
            call_record = {
                "contact_id": contact_id,
                "company": company,
                "phone": phone,
                "call_id": call_id,
                "dispatched_at": datetime.now().isoformat(),
                "status": "dispatched",
                "outcome": None,
            }
            state["calls_today"].append(call_record)
            state["call_history"].append(call_record)
            state["total_calls"] = state.get("total_calls", 0) + 1

            # Tag the contact as cold-called
            add_tag(contact_id, "cold-called")

        else:
            log(f"FAILED to dispatch call to {company}")
            failed += 1

        save_state(state)

        # Rate limit between calls
        if i < len(batch) - 1:
            time.sleep(CALL_DELAY_SECONDS)

    # Batch complete
    state["total_batches"] = state.get("total_batches", 0) + 1
    save_state(state)

    summary = (
        f"COLD CALLER BATCH COMPLETE\n"
        f"{'='*30}\n"
        f"Dispatched: {dispatched}\n"
        f"Failed: {failed}\n"
        f"Total calls today: {len(state['calls_today'])}\n"
        f"All-time calls: {state['total_calls']}\n"
        f"\nRun 'python3 cold-caller.py check' in 5-10 min to see outcomes."
    )
    log(summary)
    ntfy(NTFY_WAR_TOPIC,
         f"COLD CALLER: {dispatched} calls dispatched",
         summary, priority="high", tags="phone,rocket")


def cmd_check():
    """Check outcomes of recent calls."""
    log("=== COLD CALLER: Checking outcomes ===")
    state = load_state()

    # Find calls that need outcome checking (dispatched but no outcome yet)
    unchecked = [c for c in state.get("call_history", []) if c.get("status") == "dispatched"]
    if not unchecked:
        log("No unchecked calls found")
        print("All calls have been checked. Run 'call' to make more.")
        return

    log(f"Checking {len(unchecked)} call outcomes...")

    answered = 0
    voicemail = 0
    no_answer = 0
    interested = 0
    errors = 0

    for call in unchecked:
        call_id = call.get("call_id")
        company = call.get("company", "Unknown")
        contact_id = call.get("contact_id")

        if not call_id:
            call["status"] = "error"
            errors += 1
            continue

        # Get call details from Bland
        resp = bland_request("GET", f"/calls/{call_id}")
        if not resp:
            log(f"Could not fetch call {call_id} for {company}")
            errors += 1
            continue

        status = resp.get("status", "unknown")
        answered_by = resp.get("answered_by", "unknown")
        transcript = resp.get("concatenated_transcript", "") or resp.get("transcript", "")
        duration = resp.get("call_length", 0) or 0

        log(f"{company}: status={status}, answered_by={answered_by}, duration={duration:.1f}s")

        # Determine outcome
        if status in ("completed", "ended"):
            if answered_by == "voicemail" or duration < 15:
                outcome = "voicemail"
                voicemail += 1
                tag = "voicemail"
            elif answered_by == "human" or duration >= 15:
                outcome = "answered"
                answered += 1
                tag = "answered"

                # Score interest
                score, matches = score_interest(transcript)
                if score >= 2:
                    outcome = "interested"
                    interested += 1
                    tag = "hot-lead-call"
                    log(f"HOT LEAD: {company} — score {score}, matches: {matches}")

                    # Fire immediate ntfy alert
                    ntfy(NTFY_WAR_TOPIC,
                         f"HOT LEAD: {company}",
                         f"Interested on AI call!\n"
                         f"Score: {score}/10\n"
                         f"Keywords: {', '.join(matches)}\n"
                         f"Duration: {duration:.0f}s\n"
                         f"Phone: {call.get('phone', 'N/A')}\n\n"
                         f"Transcript snippet: {transcript[:300]}",
                         priority="urgent", tags="fire,phone")
            else:
                outcome = "no-answer"
                no_answer += 1
                tag = "no-answer"
        elif status in ("no-answer", "failed", "busy"):
            outcome = "no-answer"
            no_answer += 1
            tag = "no-answer"
        elif status == "in-progress":
            log(f"{company}: still in progress — will check later")
            continue  # Don't mark as checked yet
        else:
            outcome = "no-answer"
            no_answer += 1
            tag = "no-answer"

        # Update call record
        call["status"] = "checked"
        call["outcome"] = outcome
        call["duration"] = duration
        call["transcript_snippet"] = (transcript[:200] if transcript else "")

        # Tag contact in GHL
        if contact_id:
            add_tag(contact_id, tag)

        save_state(state)
        time.sleep(1)  # Rate limit Bland API checks

    # Update totals
    state["total_answered"] = state.get("total_answered", 0) + answered
    state["total_voicemail"] = state.get("total_voicemail", 0) + voicemail
    state["total_no_answer"] = state.get("total_no_answer", 0) + no_answer
    state["total_interested"] = state.get("total_interested", 0) + interested
    save_state(state)

    # Report
    still_pending = len([c for c in state.get("call_history", []) if c.get("status") == "dispatched"])
    summary = (
        f"OUTCOME CHECK COMPLETE\n"
        f"{'='*30}\n"
        f"Checked: {len(unchecked) - still_pending - errors}\n"
        f"Answered: {answered}\n"
        f"Voicemail: {voicemail}\n"
        f"No answer: {no_answer}\n"
        f"INTERESTED: {interested}\n"
        f"Still pending: {still_pending}\n"
        f"Errors: {errors}\n"
    )
    log(summary)

    if interested > 0:
        ntfy(NTFY_WAR_TOPIC,
             f"COLD CALLER: {interested} HOT LEADS from batch",
             summary, priority="urgent", tags="fire,tada")
    else:
        ntfy(NTFY_OPS_TOPIC,
             "Cold Caller: Outcome check done",
             summary, tags="phone")


def cmd_status():
    """Print dashboard."""
    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")
    today_calls = len([c for c in state.get("calls_today", []) if True])

    # Check Bland balance
    balance_resp = bland_request("GET", "/me")
    balance = "?"
    if balance_resp and "billing" in balance_resp:
        balance = f"${balance_resp['billing'].get('current_balance', 0):.2f}"

    # Count unchecked
    unchecked = len([c for c in state.get("call_history", []) if c.get("status") == "dispatched"])

    # Recent outcomes
    recent = [c for c in state.get("call_history", []) if c.get("status") == "checked"]
    recent = recent[-10:]  # Last 10

    print("=" * 50)
    print("  COLD CALLER — STATUS DASHBOARD")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print(f"  Bland.ai balance:      {balance}")
    print(f"  Calls today:           {today_calls}")
    print(f"  Total calls (all time):{state.get('total_calls', 0)}")
    print(f"  Total batches:         {state.get('total_batches', 0)}")
    print(f"  Unchecked calls:       {unchecked}")
    print(f"  ---")
    print(f"  Answered:              {state.get('total_answered', 0)}")
    print(f"  Voicemail:             {state.get('total_voicemail', 0)}")
    print(f"  No answer:             {state.get('total_no_answer', 0)}")
    print(f"  INTERESTED:            {state.get('total_interested', 0)}")
    print(f"  Last call date:        {state.get('last_call_date', 'never')}")

    if recent:
        print(f"\n  --- LAST {len(recent)} CALLS ---")
        for c in recent:
            icon = {"interested": "***", "answered": "+", "voicemail": "vm", "no-answer": "-"}.get(c.get("outcome", ""), "?")
            print(f"  [{icon}] {c.get('company', 'N/A'):<30} {c.get('outcome', 'N/A'):<12} {c.get('duration', 0):.0f}s")

    print("=" * 50)


# ===================================================
# MAIN
# ===================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 cold-caller.py [call|status|check]")
        print("  call   — Dispatch a batch of 20 AI calls")
        print("  status — Print dashboard")
        print("  check  — Check outcomes of last batch")
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "call":
            cmd_call()
        elif command == "status":
            cmd_status()
        elif command == "check":
            cmd_check()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 cold-caller.py [call|status|check]")
            sys.exit(1)
        ntfy(NTFY_CALLS_TOPIC,
             f"Cold Caller finished: {command}",
             f"Cold Caller completed '{command}' at {datetime.now().strftime('%I:%M %p')}",
             tags="white_check_mark")
    except Exception as _exc:
        import traceback
        _tb = traceback.format_exc()
        log(f"CRASH in cold-caller {command}: {_exc}")
        ntfy(NTFY_CALLS_TOPIC,
             f"Cold Caller CRASHED: {command}",
             f"Command: {command}\nError: {_exc}\n\n{_tb[-500:]}",
             priority="high", tags="rotating_light")
        raise
