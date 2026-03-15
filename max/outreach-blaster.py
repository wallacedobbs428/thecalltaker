#!/usr/bin/env python3
"""
outreach-blaster.py — Cold SMS Outreach Engine for The Call Taker
Sends industry-personalized Day 0 pain hook SMS to hot leads via GHL.

Commands:
    send    — Pull hot-lead contacts, filter, send cold SMS, tag, notify
    status  — Show send stats from state file

Usage:
    python3 max/outreach-blaster.py send
    python3 max/outreach-blaster.py status
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ─── Config ────────────────────────────────────────────────────────────────────

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

NTFY_SALES = "tct-sales-63uYsIT9"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "outreach-blaster-state.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "outreach-blaster.log")

EXCLUDE_TAGS = {"customer", "active-client", "pilot-active", "do-not-contact", "unsubscribed"}
COOLDOWN_DAYS = 7
SMS_DELAY = 2  # seconds between sends

# ─── Industry SMS Templates (Day 0 Pain Hook) ─────────────────────────────────

INDUSTRY_SMS = {
    "hvac": "hey {name}, quick question — how many calls does your hvac shop miss after 5pm? most guys i talk to say 5-10/week. that's easily $2k/mo walking out the door",
    "plumbing": "hey {name}, random question — when someone calls your shop at 8pm with a burst pipe and nobody picks up, where do they go? usually straight to the next plumber on google",
    "dental": "hey {name}, how does your office handle calls when you're with a patient? most dental practices i talk to send like 30% of calls to voicemail. patients just book somewhere else",
    "roofing": "hey {name}, after a big storm hits and 50 people call your roofing company at once — how many of those actually get answered? most roofers i talk to say they lose half their storm leads",
    "locksmith": "hey {name}, when someone's locked out at 2am and calls you, does anyone pick up? every missed lockout call is a $150-300 job gone to whoever answers first",
    "electrical": "hey {name}, quick question — when someone's breaker trips at 10pm and they call your shop, who answers? most electricians i talk to say those calls go straight to voicemail. that's $200-400 gone",
    "restaurant": "hey {name}, when the dinner rush hits and no one can answer the phone, how many reservations do you think walk? most restaurants i talk to say it's 5-10 per week",
    "real-estate": "hey {name}, when a buyer calls about a listing at 8pm and gets your voicemail, what happens? they call the next agent on zillow. that's a $12k commission gone",
    "insurance": "hey {name}, when someone's shopping quotes and calls your agency at lunch, who picks up? most agencies i talk to say they miss 30% of quote calls. that's policies going to the next agent",
    "auto-repair": "hey {name}, when you're under the hood and the phone rings, who answers? most shops i talk to say they miss 3-5 calls a day. at $400/ticket that's serious money walking out",
    "pest-control": "hey {name}, when someone finds termites at 9pm and calls you, does anyone pick up? most pest control companies miss those after-hours calls. that's a $250+ job gone to whoever answers",
}

DEFAULT_SMS = "hey {name}, quick question — how many calls does your business miss after hours? most companies i talk to say 5-10/week. at $200-500/job, that's $2k-5k/mo walking out the door"

KNOWN_INDUSTRIES = {
    "hvac", "plumbing", "dental", "roofing", "locksmith", "electrical",
    "medspa", "legal", "property-management", "veterinary", "garage-door",
    "towing", "funeral", "restaurant", "real-estate", "insurance",
    "auto-repair", "pest-control",
}

# ─── Logging ───────────────────────────────────────────────────────────────────

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ─── ntfy ──────────────────────────────────────────────────────────────────────

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

# ─── GHL API ──────────────────────────────────────────────────────────────────

def ghl_request(method, path, body=None, version="2021-07-28"):
    url = f"{GHL_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": version,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "OutreachBlaster/1.0 TheCallTaker",
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

# ─── GHL Helpers ───────────────────────────────────────────────────────────────

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
    log(f"Fetched {len(contacts)} total contacts from GHL")
    return contacts


def send_sms(contact_id, message):
    body = {
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    }
    return ghl_request("POST", "/conversations/messages", body=body, version="2021-04-15")


def tag_contact(contact_id, existing_tags, new_tag):
    tags = list(set(existing_tags + [new_tag]))
    return ghl_request("PUT", f"/contacts/{contact_id}", body={"tags": tags})

# ─── State Management ─────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            log(f"State load error: {e}")
    return {"sent": {}, "total_sent": 0, "runs": []}


def save_state(state):
    try:
        fd, tmp = tempfile.mkstemp(dir=SCRIPT_DIR, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, STATE_FILE)
    except Exception as e:
        log(f"State save error: {e}")

# ─── Core Logic ────────────────────────────────────────────────────────────────

def detect_industry(tags):
    """Return the industry tag if found, else None."""
    for tag in tags:
        tag_lower = tag.lower().strip()
        if tag_lower in KNOWN_INDUSTRIES:
            return tag_lower
    return None


def get_sms_text(name, industry):
    """Return personalized SMS for the given industry."""
    template = INDUSTRY_SMS.get(industry, DEFAULT_SMS) if industry else DEFAULT_SMS
    display_name = name if name else "there"
    return template.format(name=display_name)


def is_on_cooldown(contact_id, state):
    """Check if contact was sent outreach within the cooldown window."""
    sent_info = state.get("sent", {}).get(contact_id)
    if not sent_info:
        return False
    last_sent = sent_info.get("date")
    if not last_sent:
        return False
    try:
        last_dt = datetime.strptime(last_sent, "%Y-%m-%d")
        return datetime.now() - last_dt < timedelta(days=COOLDOWN_DAYS)
    except Exception:
        return False


def cmd_send():
    """Main send command — pull contacts, filter, send SMS, tag, notify."""
    log("=" * 60)
    log("OUTREACH BLASTER — send started")

    state = load_state()
    contacts = get_all_contacts()
    if not contacts:
        log("No contacts fetched. Aborting.")
        return

    # Filter to hot-lead only
    hot_leads = []
    for c in contacts:
        tags = [t.lower().strip() for t in (c.get("tags") or [])]
        if "hot-lead" not in tags:
            continue
        # Exclude by tags
        if EXCLUDE_TAGS & set(tags):
            continue
        # Exclude if on cooldown
        cid = c.get("id")
        if is_on_cooldown(cid, state):
            continue
        hot_leads.append(c)

    log(f"Qualifying hot-leads after filtering: {len(hot_leads)}")

    if not hot_leads:
        log("No qualifying contacts to send. Done.")
        return

    sent_count = 0
    failed_count = 0
    industries_hit = {}
    today = datetime.now().strftime("%Y-%m-%d")

    for i, contact in enumerate(hot_leads):
        cid = contact.get("id")
        first_name = (contact.get("firstName") or "").strip()
        phone = contact.get("phone", "")
        tags_raw = contact.get("tags") or []
        tags_lower = [t.lower().strip() for t in tags_raw]

        if not phone:
            log(f"SKIP {cid} — no phone number")
            continue

        industry = detect_industry(tags_lower)
        sms_text = get_sms_text(first_name or "there", industry)

        log(f"Sending SMS to {first_name or 'Unknown'} ({phone}) — industry: {industry or 'default'}")

        result = send_sms(cid, sms_text)
        if result:
            sent_count += 1
            ind_key = industry or "default"
            industries_hit[ind_key] = industries_hit.get(ind_key, 0) + 1

            # Tag contact
            tag_contact(cid, tags_raw, "outreach-sent")

            # Record in state
            state.setdefault("sent", {})[cid] = {
                "date": today,
                "name": first_name,
                "phone": phone,
                "industry": industry or "default",
            }

            log(f"  SMS sent + tagged outreach-sent")
        else:
            failed_count += 1
            log(f"  SMS FAILED for {cid}")

        # Rate limit delay (skip after last contact)
        if i < len(hot_leads) - 1:
            time.sleep(SMS_DELAY)

    # Update state totals
    state["total_sent"] = state.get("total_sent", 0) + sent_count
    state.setdefault("runs", []).append({
        "date": today,
        "time": datetime.now().strftime("%H:%M:%S"),
        "sent": sent_count,
        "failed": failed_count,
        "industries": industries_hit,
    })
    save_state(state)

    # Summary
    log(f"DONE — Sent: {sent_count}, Failed: {failed_count}")
    log(f"Industries: {industries_hit}")

    # ntfy alert
    industry_lines = "\n".join(f"  {k}: {v}" for k, v in sorted(industries_hit.items()))
    ntfy(
        NTFY_SALES,
        f"Outreach Blaster — {sent_count} SMS sent",
        f"Cold SMS batch complete\n"
        f"Sent: {sent_count}\n"
        f"Failed: {failed_count}\n"
        f"Industries:\n{industry_lines}\n"
        f"Total all-time: {state['total_sent']}",
        priority="default",
        tags="outbox,speech_balloon",
    )


def cmd_status():
    """Show stats from state file."""
    state = load_state()
    sent = state.get("sent", {})
    runs = state.get("runs", [])
    total = state.get("total_sent", 0)

    print(f"\n{'=' * 50}")
    print(f"  OUTREACH BLASTER STATUS")
    print(f"{'=' * 50}")
    print(f"  Total SMS sent (all-time): {total}")
    print(f"  Unique contacts reached:   {len(sent)}")
    print(f"  Total runs:                {len(runs)}")

    if runs:
        last = runs[-1]
        print(f"\n  Last run:")
        print(f"    Date:       {last.get('date')} {last.get('time', '')}")
        print(f"    Sent:       {last.get('sent', 0)}")
        print(f"    Failed:     {last.get('failed', 0)}")
        print(f"    Industries: {last.get('industries', {})}")

    # Cooldown contacts
    now = datetime.now()
    on_cooldown = 0
    for cid, info in sent.items():
        try:
            last_dt = datetime.strptime(info.get("date", ""), "%Y-%m-%d")
            if now - last_dt < timedelta(days=COOLDOWN_DAYS):
                on_cooldown += 1
        except Exception:
            pass
    print(f"\n  On 7-day cooldown:         {on_cooldown}")
    print(f"{'=' * 50}\n")

# ─── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 outreach-blaster.py [send|status]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "send":
        cmd_send()
    elif command == "status":
        cmd_status()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python3 outreach-blaster.py [send|status]")
        sys.exit(1)
