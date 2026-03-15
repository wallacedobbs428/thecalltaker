#!/usr/bin/env python3
"""
DEMO FOLLOW-UP SMS ENGINE — The Call Taker
==========================================
Fires a follow-up SMS to contacts who requested a live demo
(tagged 'live-demo-request') but did NOT convert to pilot or paid.

Trigger: 2 hours after the contact is created / tagged.
One SMS per contact, never duplicated. Tracks sent contacts in state file.

Commands:
  scan    — Find eligible contacts and queue them
  send    — Send queued SMS messages that are ready (2h elapsed)
  run     — scan + send (full cycle, use this in launchd)
  status  — Print stats without sending

Schedule recommendation: every 15-30 min via launchd (or cron).
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

# ─── Import path for tct_common (if available) ───────────────────────────────
# Graceful — script still works standalone if tct_common is absent.
sys.path.insert(0, os.path.expanduser("~/thecalltaker-ops/ops"))
try:
    from tct_common import ntfy_standard
    HAS_TCT_COMMON = True
except ImportError:
    HAS_TCT_COMMON = False

# ─── Configuration ────────────────────────────────────────────────────────────

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"

DEMO_LINE = "(615) 784-5747"

# Tag that triggers this engine — set by try-live.html form submission
TRIGGER_TAG = "live-demo-request"

# If contact has ANY of these tags, skip — they already converted or are managed elsewhere
EXCLUDE_TAGS = {
    "pilot-active",
    "pilot-signup",
    "paid-client",
    "pilot-converted",
    "active-client",
    "customer",
    "do-not-contact",
    "unsubscribed",
    "demo-followup-sms-sent",   # our own dedup tag
}

# How long to wait after contact creation before firing the SMS (minutes)
DELAY_MINUTES = 120  # 2 hours

# Safety cap per run to avoid API bursts
MAX_SMS_PER_RUN = 50
DELAY_BETWEEN_SMS = 3  # seconds between GHL API calls

# Paths — self-contained inside website repo ops/ folder
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo-followup-sms-state.json")
LOG_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo-followup-sms.log")

# ntfy topics
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_SYSTEM   = "tct-system-vRsfXQRQ"

# ─── GHL Headers ──────────────────────────────────────────────────────────────

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-DemoFollowupSMS/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-DemoFollowupSMS/1.0",
}

# ─── SMS Message ──────────────────────────────────────────────────────────────

def build_sms(first_name: str, company: str) -> str:
    """
    Post-demo follow-up SMS. Personalized with first name and company.
    Falls back gracefully when either field is missing.
    Stays under 160 chars to avoid multi-part SMS charges where possible.
    """
    name = (first_name or "").strip() or "Hey"
    company_clean = (company or "").strip()

    if company_clean:
        line = (
            f"{name}! That was just a taste — imagine Jessica answering every call "
            f"at {company_clean} 24/7. Zero missed jobs. Zero voicemail. "
            f"We have 3 pilot spots left this month — free 14-day trial, no card needed. "
            f"Want in? Reply YES or call {DEMO_LINE}"
        )
    else:
        line = (
            f"{name}! That was just a taste — imagine an AI answering every call "
            f"24/7. Zero missed jobs. Zero voicemail. "
            f"We have 3 pilot spots left this month — free 14-day trial, no card needed. "
            f"Want in? Reply YES or call {DEMO_LINE}"
        )
    return line


def build_local_sms(first_name: str, company: str, city: str) -> str:
    """Post-demo follow-up SMS for LOCAL leads — pushes in-person visit, not signup."""
    name = (first_name or "").strip() or "Hey"
    company_clean = (company or "").strip()
    city_clean = (city or "").strip() or "the Nashville area"

    if company_clean:
        return (
            f"{name}! That AI you just talked to? That's what your customers at "
            f"{company_clean} would hear 24/7. I'm right here in {city_clean} — "
            f"would it be worth 10 minutes for me to stop by and show you the full setup in person?"
        )
    else:
        return (
            f"{name}! That AI you just talked to? That's what your customers would hear 24/7. "
            f"I'm right here in {city_clean} — would it be worth 10 minutes "
            f"for me to stop by and show you the full setup?"
        )


# ─── Logging ──────────────────────────────────────────────────────────────────

def log(msg: str, level: str = "INFO") -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] demo-followup-sms: {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ─── State File ───────────────────────────────────────────────────────────────

def load_state() -> dict:
    """Load state from JSON, return empty default if missing or corrupt."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            log(f"State file corrupt, resetting: {e}", "WARN")
    return {
        "queued": {},      # contact_id -> {queued_at, first_name, company, phone}
        "sent": {},        # contact_id -> {sent_at, first_name, company}
        "stats": {
            "total_queued": 0,
            "total_sent": 0,
            "total_skipped": 0,
            "total_runs": 0,
            "last_run": None,
        },
    }


def save_state(state: dict) -> None:
    """Atomic write — tempfile + os.replace to prevent corruption."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, default=str)
        os.replace(tmp, STATE_FILE)
    except Exception as e:
        log(f"Failed to save state: {e}", "ERROR")

# ─── GHL API Helpers ──────────────────────────────────────────────────────────

def ghl_request(method: str, path: str, headers: dict = None,
                params: dict = None, json_body: dict = None) -> dict | None:
    """Retry wrapper with exponential backoff for 5xx and 429 rate limits."""
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    backoff = [5, 15, 30]
    rate_backoff = [30, 60, 120]

    for attempt in range(3):
        try:
            resp = requests.request(
                method, url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=30,
            )
            if resp.status_code == 429:
                wait = rate_backoff[min(attempt, 2)]
                log(f"Rate limited, waiting {wait}s (attempt {attempt+1}/3)", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                wait = backoff[min(attempt, 2)]
                log(f"GHL 5xx ({resp.status_code}), retrying in {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.text:
                return resp.json()
            return {}
        except requests.exceptions.RequestException as e:
            log(f"Request error (attempt {attempt+1}/3): {e}", "ERROR")
            time.sleep(backoff[min(attempt, 2)])

    log(f"All retries failed for {method} {path}", "ERROR")
    return None


def fetch_contacts_by_tag(tag: str) -> list:
    """
    Paginate through all GHL contacts that have a specific tag.
    Returns list of contact dicts.
    """
    all_contacts = []
    page = 1

    while True:
        data = ghl_request("GET", "/contacts/", params={
            "locationId": GHL_LOCATION_ID,
            "limit": 100,
            "page": page,
            "query": tag,          # GHL supports tag query via search
        })

        if not data:
            log(f"Empty response from /contacts/ page {page}", "WARN")
            break

        # GHL returns contacts inside "contacts" key
        contacts = data.get("contacts", [])
        if not contacts:
            break

        # Filter client-side by tag presence (GHL query is fuzzy)
        for c in contacts:
            tags = [t.lower().strip() for t in c.get("tags", [])]
            if tag in tags:
                all_contacts.append(c)

        # Pagination — stop when page returns fewer than limit
        if len(contacts) < 100:
            break

        page += 1
        if page > 100:
            log("Pagination safety limit hit at page 100", "WARN")
            break

    return all_contacts


def fetch_contact(contact_id: str) -> dict | None:
    """Fetch a single contact by ID for freshness check before sending."""
    data = ghl_request("GET", f"/contacts/{contact_id}")
    if not data:
        return None
    return data.get("contact") or data.get("contacts", [None])[0]


def send_sms(contact_id: str, phone: str, message: str) -> bool:
    """
    Send an SMS via GHL Conversations API.
    Returns True on success (HTTP 2xx), False otherwise.
    """
    payload = {
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    }
    data = ghl_request("POST", "/conversations/messages",
                       headers=CONVERSATIONS_HEADERS, json_body=payload)
    if data is None:
        return False
    # GHL returns {"id": ..., "msg": "message queued successfully"} on success
    return bool(data.get("id") or data.get("message") or data.get("msg"))


def add_tag(contact_id: str, tags: list) -> bool:
    """Add one or more tags to a GHL contact."""
    data = ghl_request("POST", f"/contacts/{contact_id}/tags",
                       json_body={"tags": tags})
    return data is not None


def format_phone(raw: str) -> str:
    """Normalize phone to E.164 (+1XXXXXXXXXX). Returns None if invalid."""
    if not raw:
        return None
    digits = "".join(c for c in raw if c.isdigit())
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    if len(digits) > 11:
        # Could be a raw E.164 with leading 1 and country code already
        if digits.startswith("1") and len(digits) == 11:
            return f"+{digits}"
    return None

# ─── ntfy Notification ────────────────────────────────────────────────────────

def ntfy(topic: str, title: str, body: str, priority: str = "default") -> None:
    """Fire-and-forget ntfy notification. Never raises."""
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers={
                "Title": safe_title,
                "Priority": priority,
                "Tags": "phone",
            },
            timeout=10,
        )
    except Exception:
        pass

# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_scan(state: dict) -> int:
    """
    Fetch all contacts tagged 'live-demo-request'.
    Queue those not already sent or excluded.
    Returns count of newly queued contacts.
    """
    log(f"Scanning GHL for contacts tagged '{TRIGGER_TAG}'...")
    contacts = fetch_contacts_by_tag(TRIGGER_TAG)
    log(f"Found {len(contacts)} contact(s) with tag '{TRIGGER_TAG}'")

    newly_queued = 0

    for c in contacts:
        cid = c.get("id")
        if not cid:
            continue

        # Already processed
        if cid in state["sent"]:
            continue

        # Already queued
        if cid in state["queued"]:
            continue

        # Check exclusion tags
        tags = {t.lower().strip() for t in c.get("tags", [])}
        if tags & EXCLUDE_TAGS:
            log(f"Skipping {cid} — excluded tag(s): {tags & EXCLUDE_TAGS}")
            state["stats"]["total_skipped"] += 1
            continue

        # Require a valid phone number
        raw_phone = c.get("phone", "")
        phone = format_phone(raw_phone)
        if not phone:
            log(f"Skipping {cid} — no valid phone: '{raw_phone}'")
            state["stats"]["total_skipped"] += 1
            continue

        # Record queue time as now (will check 2h delay at send time)
        # Use contact dateAdded if available so the clock starts from when they tagged
        date_added = c.get("dateAdded") or c.get("createdAt") or datetime.now().isoformat()
        # Normalize to ISO string
        if not isinstance(date_added, str):
            date_added = datetime.now().isoformat()

        state["queued"][cid] = {
            "queued_at": date_added,
            "first_name": (c.get("firstName") or "").strip() or "there",
            "company":    (c.get("companyName") or c.get("company") or "").strip(),
            "phone":      phone,
        }
        state["stats"]["total_queued"] += 1
        newly_queued += 1
        log(f"Queued: {cid} — {state['queued'][cid]['first_name']} @ {state['queued'][cid]['company'] or 'unknown company'} ({phone})")

    log(f"Scan complete. {newly_queued} newly queued. Total in queue: {len(state['queued'])}")
    return newly_queued


def cmd_send(state: dict) -> int:
    """
    For each queued contact where 2h has elapsed, do a fresh GHL check,
    confirm they still haven't converted, then fire the SMS.
    Returns count sent this run.
    """
    now = datetime.now()
    log(f"Checking send queue ({len(state['queued'])} contacts)...")

    sent_this_run = 0
    ready = []

    for cid, entry in state["queued"].items():
        # Parse queue time — handle both ISO 8601 and GHL's epoch ms
        raw_time = entry.get("queued_at", "")
        try:
            # Try ISO parse first
            queued_dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00").replace("+00:00", ""))
        except (ValueError, AttributeError):
            try:
                # GHL sometimes returns ms epoch as string
                queued_dt = datetime.fromtimestamp(int(raw_time) / 1000)
            except (ValueError, TypeError):
                log(f"Cannot parse queued_at for {cid}: '{raw_time}' — using now minus delay", "WARN")
                queued_dt = now - timedelta(minutes=DELAY_MINUTES + 1)

        fire_at = queued_dt + timedelta(minutes=DELAY_MINUTES)
        if now >= fire_at:
            ready.append((cid, entry, queued_dt))

    log(f"{len(ready)} contact(s) ready to send (2h elapsed)")

    for cid, entry, queued_dt in ready:
        if sent_this_run >= MAX_SMS_PER_RUN:
            log(f"Reached max SMS per run ({MAX_SMS_PER_RUN}). Will continue next run.")
            break

        first_name = entry.get("first_name", "there")
        company    = entry.get("company", "")
        phone      = entry.get("phone", "")

        if not phone:
            log(f"No phone for {cid}, removing from queue", "WARN")
            del state["queued"][cid]
            continue

        # Fresh GHL check — make sure they haven't converted since we queued them
        fresh = fetch_contact(cid)
        if fresh:
            fresh_tags = {t.lower().strip() for t in fresh.get("tags", [])}
            if fresh_tags & EXCLUDE_TAGS:
                log(f"Skipping {cid} ({first_name}) — converted since queue: {fresh_tags & EXCLUDE_TAGS}")
                state["stats"]["total_skipped"] += 1
                # Move out of queue silently
                del state["queued"][cid]
                state["sent"][cid] = {
                    "sent_at": now.isoformat(),
                    "skipped": True,
                    "reason": "converted",
                    "first_name": first_name,
                    "company": company,
                }
                continue
            # Refresh name and company from live data in case GHL updated them
            first_name = (fresh.get("firstName") or first_name or "").strip() or "there"
            company    = (fresh.get("companyName") or fresh.get("company") or company or "").strip()

        # Build and send SMS — route local leads to in-person CTA
        contact_for_check = fresh if fresh else {"phone": phone}
        if is_local(contact_for_check):
            city = get_lead_city(contact_for_check)
            message = build_local_sms(first_name, company, city)
            log(f"LOCAL lead detected: {first_name} @ {company} ({city})")
        else:
            message = build_sms(first_name, company)
        log(f"Sending SMS to {cid} ({first_name} @ {company or 'unknown'}) {phone}")
        log(f"  Message ({len(message)} chars): {message[:80]}...")

        success = send_sms(cid, phone, message)

        if success:
            log(f"SMS sent: {cid} — {first_name}")

            # Tag contact so we never double-send
            add_tag(cid, ["demo-followup-sms-sent"])

            # Move from queued to sent
            del state["queued"][cid]
            state["sent"][cid] = {
                "sent_at": now.isoformat(),
                "first_name": first_name,
                "company": company,
                "phone": phone,
                "message_length": len(message),
            }
            state["stats"]["total_sent"] += 1
            sent_this_run += 1

            # Activity ping to ntfy
            ntfy(
                NTFY_ACTIVITY,
                "Demo Follow-Up SMS Sent",
                f"{first_name} @ {company or 'unknown'} | {phone} | queued {queued_dt.strftime('%H:%M')}",
                priority="default",
            )

            time.sleep(DELAY_BETWEEN_SMS)

        else:
            log(f"SMS FAILED for {cid} — will retry next run", "ERROR")
            # Leave in queue for next run — don't remove

    log(f"Send run complete. Sent {sent_this_run} this run. Total all-time: {state['stats']['total_sent']}")
    return sent_this_run


def cmd_run(state: dict) -> None:
    """Full cycle: scan then send."""
    state["stats"]["total_runs"] += 1
    state["stats"]["last_run"] = datetime.now().isoformat()
    queued = cmd_scan(state)
    sent   = cmd_send(state)
    log(f"Run complete. Newly queued: {queued}. Sent this run: {sent}.")


def cmd_status(state: dict) -> None:
    """Print human-readable status without mutating state."""
    stats = state.get("stats", {})
    queue = state.get("queued", {})
    sent  = state.get("sent", {})

    print("\n" + "=" * 50)
    print("DEMO FOLLOW-UP SMS — STATUS")
    print("=" * 50)
    print(f"  Total runs:          {stats.get('total_runs', 0)}")
    print(f"  Last run:            {stats.get('last_run', 'never')}")
    print(f"  Trigger tag:         {TRIGGER_TAG}")
    print(f"  Send delay:          {DELAY_MINUTES} minutes (2 hours)")
    print(f"  Max per run:         {MAX_SMS_PER_RUN}")
    print()
    print(f"  Currently queued:    {len(queue)}")
    print(f"  Total queued:        {stats.get('total_queued', 0)}")
    print(f"  Total sent:          {stats.get('total_sent', 0)}")
    print(f"  Total skipped:       {stats.get('total_skipped', 0)}")
    print()

    if queue:
        now = datetime.now()
        print("  QUEUE:")
        for cid, entry in list(queue.items())[:10]:
            raw_time = entry.get("queued_at", "")
            try:
                queued_dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00").replace("+00:00", ""))
                fire_at   = queued_dt + timedelta(minutes=DELAY_MINUTES)
                remaining = max(0, (fire_at - now).seconds // 60)
                readiness = "READY" if now >= fire_at else f"in {remaining}m"
            except Exception:
                readiness = "unknown"
            name = entry.get("first_name", "?")
            company = entry.get("company") or "?"
            print(f"    {cid[:16]}... | {name} @ {company} | {readiness}")
        if len(queue) > 10:
            print(f"    ... and {len(queue) - 10} more")

    if sent:
        print()
        print("  RECENTLY SENT:")
        recent = sorted(sent.items(), key=lambda x: x[1].get("sent_at", ""), reverse=True)[:5]
        for cid, entry in recent:
            name    = entry.get("first_name", "?")
            company = entry.get("company") or "?"
            ts      = entry.get("sent_at", "?")[:16]
            print(f"    {cid[:16]}... | {name} @ {company} | sent {ts}")

    print("=" * 50 + "\n")

# ─── Entry Point ──────────────────────────────────────────────────────────────

COMMANDS = ("scan", "send", "run", "status")

def main():
    command = sys.argv[1].lower().strip() if len(sys.argv) > 1 else "run"

    if command not in COMMANDS:
        print(f"Unknown command: {command}")
        print(f"Usage: python3 demo-followup-sms.py [{' | '.join(COMMANDS)}]")
        sys.exit(1)

    state = load_state()

    try:
        if command == "scan":
            cmd_scan(state)
        elif command == "send":
            state["stats"]["total_runs"] += 1
            state["stats"]["last_run"] = datetime.now().isoformat()
            cmd_send(state)
        elif command == "run":
            cmd_run(state)
        elif command == "status":
            cmd_status(state)
            return  # Don't save state on status (read-only)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log(f"CRASH in command '{command}': {e}\n{tb}", "CRITICAL")
        ntfy(NTFY_SYSTEM, "[CRITICAL] demo-followup-sms crashed",
             f"Command: {command}\nError: {e}\n\n{tb[:500]}", priority="urgent")
        sys.exit(1)
    finally:
        if command != "status":
            save_state(state)


if __name__ == "__main__":
    main()
