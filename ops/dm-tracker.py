#!/usr/bin/env python3
"""
DM TRACKER — The Call Taker
============================
Tracks LinkedIn and Instagram DM outreach as a fallback for leads
who don't respond to email or SMS.

Logic:
  - Reads contacts from GHL tagged 'dm-candidate' (auto-tagged by other engines
    after email+SMS sequence completes with no response)
  - Tracks which DMs have been sent on which platform
  - Generates daily DM lists for manual outreach
  - Logs responses and moves hot leads to GHL pipeline

Commands:
  generate    — Generate today's DM list (leads needing DM outreach)
  log <id> <platform> <status>  — Log a DM sent/replied (linkedin|instagram, sent|replied|booked)
  status      — Show DM outreach stats
  candidates  — Find new DM candidates from GHL

Schedule: Daily via launchd (8am — generate morning DM list)
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
NTFY_SALES = "tct-sales-63uYsIT9"

STATE_FILE = os.path.expanduser("~/thecalltaker/ops/dm-tracker-state.json")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/dm-tracker.log")
DM_LIST_FILE = os.path.expanduser("~/thecalltaker/ops/dm-list-today.json")

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}", "Version": "2021-07-28",
    "Content-Type": "application/json", "Accept": "application/json",
    "User-Agent": "TheCallTaker-DMTracker/1.0",
}

# Tags that indicate DM outreach is appropriate
DM_TRIGGER_TAGS = {"dm-candidate", "sms-no-reply", "email-no-reply", "cold-outreach"}
EXCLUDE_TAGS = {"customer", "active-client", "pilot-active", "pilot-converted",
                "do-not-contact", "unsubscribed", "contacted", "demo-booked"}


def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] dm-tracker: {msg}"
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
    return {
        "tracked": {},
        "stats": {
            "linkedin_sent": 0, "instagram_sent": 0,
            "linkedin_replied": 0, "instagram_replied": 0,
            "demos_booked": 0, "total_runs": 0,
        },
    }


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def ghl_request(method, path, params=None, json_body=None):
    url = f"{GHL_BASE_URL}{path}"
    for attempt in range(3):
        try:
            resp = requests.request(method, url, headers=CONTACTS_HEADERS, params=params, json=json_body, timeout=30)
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


def add_tag(contact_id, tags):
    return ghl_request("POST", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def ntfy_alert(topic, title, message, priority="default"):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        requests.post(f"https://ntfy.sh/{topic}", data=message.encode("utf-8"),
                      headers={"Title": safe_title, "Priority": priority}, timeout=10)
    except Exception:
        pass


def cmd_candidates(state):
    """Find new DM candidates from GHL."""
    log("Scanning for DM candidates...")
    all_contacts = []
    page = 1
    while True:
        data = ghl_request("GET", "/contacts/", params={
            "locationId": GHL_LOCATION_ID, "limit": 100, "page": page,
        })
        if not data or "contacts" not in data:
            break
        all_contacts.extend(data["contacts"])
        if len(data["contacts"]) < 100:
            break
        page += 1
        if page > 50:
            break

    new = 0
    for c in all_contacts:
        cid = c.get("id")
        if not cid or cid in state["tracked"]:
            continue
        tags = set(t.lower() for t in c.get("tags", []))
        if not (tags & DM_TRIGGER_TAGS):
            continue
        if tags & EXCLUDE_TAGS:
            continue

        company = c.get("companyName", "Unknown")
        first_name = c.get("firstName", "")

        state["tracked"][cid] = {
            "added": datetime.now().isoformat(),
            "first_name": first_name,
            "company": company,
            "email": c.get("email", ""),
            "linkedin_sent": False,
            "instagram_sent": False,
            "linkedin_replied": False,
            "instagram_replied": False,
            "booked": False,
        }
        add_tag(cid, ["dm-candidate"])
        new += 1

    log(f"Found {new} new DM candidates. Total tracked: {len(state['tracked'])}")
    save_state(state)
    return new


def cmd_generate(state):
    """Generate today's DM outreach list."""
    log("Generating today's DM list...")
    state["stats"]["total_runs"] += 1

    # First scan for new candidates
    cmd_candidates(state)

    dm_list = {"date": datetime.now().strftime("%Y-%m-%d"), "linkedin": [], "instagram": []}

    for cid, info in state["tracked"].items():
        if info.get("booked"):
            continue

        # LinkedIn DM needed
        if not info.get("linkedin_sent"):
            dm_list["linkedin"].append({
                "contact_id": cid,
                "name": info.get("first_name", "Unknown"),
                "company": info.get("company", "Unknown"),
                "email": info.get("email", ""),
                "script": (
                    f"Hey {info.get('first_name', 'there')}, I noticed {info.get('company', 'your business')} "
                    f"might be losing calls after hours. We built an AI receptionist that answers 24/7 — "
                    f"sounds human, books jobs on your calendar. Free 14-day pilot. Want to hear it? "
                    f"Call (615) 784-5747 and pretend you're a customer."
                ),
            })

        # Instagram DM needed (after LinkedIn)
        if info.get("linkedin_sent") and not info.get("instagram_sent"):
            dm_list["instagram"].append({
                "contact_id": cid,
                "name": info.get("first_name", "Unknown"),
                "company": info.get("company", "Unknown"),
                "script": (
                    f"Hey! Love what {info.get('company', 'you guys are')} doing. Quick Q — "
                    f"who handles your calls after 5pm? We have an AI that answers 24/7, "
                    f"books appointments, sounds totally human. Free pilot. DM me 'DEMO' if curious."
                ),
            })

    # Save DM list
    os.makedirs(os.path.dirname(DM_LIST_FILE), exist_ok=True)
    with open(DM_LIST_FILE, "w") as f:
        json.dump(dm_list, f, indent=2)

    linkedin_count = len(dm_list["linkedin"])
    instagram_count = len(dm_list["instagram"])
    log(f"DM list generated: {linkedin_count} LinkedIn, {instagram_count} Instagram")

    if linkedin_count + instagram_count > 0:
        ntfy_alert(NTFY_SALES, "DM Outreach List Ready",
                   f"LinkedIn: {linkedin_count} leads\n"
                   f"Instagram: {instagram_count} leads\n"
                   f"File: {DM_LIST_FILE}")

    save_state(state)


def cmd_log_dm(state, contact_id, platform, status):
    """Log a DM action."""
    if contact_id not in state["tracked"]:
        print(f"Contact {contact_id} not tracked. Run 'candidates' first.")
        return

    info = state["tracked"][contact_id]
    platform = platform.lower()
    status = status.lower()

    if platform not in ("linkedin", "instagram"):
        print("Platform must be 'linkedin' or 'instagram'")
        return

    if status == "sent":
        info[f"{platform}_sent"] = True
        info[f"{platform}_sent_at"] = datetime.now().isoformat()
        state["stats"][f"{platform}_sent"] += 1
        log(f"DM sent on {platform} to {info.get('first_name')} ({info.get('company')})")
    elif status == "replied":
        info[f"{platform}_replied"] = True
        state["stats"][f"{platform}_replied"] += 1
        add_tag(contact_id, ["contacted", "hot-lead"])
        log(f"DM reply on {platform} from {info.get('first_name')} ({info.get('company')})")
    elif status == "booked":
        info["booked"] = True
        state["stats"]["demos_booked"] += 1
        add_tag(contact_id, ["demo-booked", "contacted"])
        log(f"DEMO BOOKED via {platform} DM: {info.get('first_name')} ({info.get('company')})")
        ntfy_alert("tct-urgent-Hk9UOEZR", f"[CRITICAL] DM Demo Booked!",
                   f"{info.get('first_name')} from {info.get('company')} booked via {platform} DM!",
                   priority="urgent")
    else:
        print("Status must be 'sent', 'replied', or 'booked'")
        return

    save_state(state)


def cmd_status(state):
    stats = state["stats"]
    tracked = state["tracked"]
    active = sum(1 for v in tracked.values() if not v.get("booked"))

    print("\n╔══════════════════════════════════════════╗")
    print("║         DM TRACKER — STATUS              ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  LinkedIn Sent:      {stats.get('linkedin_sent', 0):>5}               ║")
    print(f"║  LinkedIn Replied:   {stats.get('linkedin_replied', 0):>5}               ║")
    print(f"║  Instagram Sent:     {stats.get('instagram_sent', 0):>5}               ║")
    print(f"║  Instagram Replied:  {stats.get('instagram_replied', 0):>5}               ║")
    print(f"║  Demos Booked:       {stats.get('demos_booked', 0):>5}               ║")
    print(f"║  Active Leads:       {active:>5}               ║")
    print(f"║  Total Tracked:      {len(tracked):>5}               ║")
    print("╚══════════════════════════════════════════╝\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: dm-tracker.py <generate|log|candidates|status>")
        print("  log <contact_id> <linkedin|instagram> <sent|replied|booked>")
        sys.exit(1)

    state = load_state()
    cmd = sys.argv[1].lower()

    if cmd == "generate":
        cmd_generate(state)
    elif cmd == "candidates":
        cmd_candidates(state)
    elif cmd == "log":
        if len(sys.argv) < 5:
            print("Usage: dm-tracker.py log <contact_id> <linkedin|instagram> <sent|replied|booked>")
            sys.exit(1)
        cmd_log_dm(state, sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "status":
        cmd_status(state)
    else:
        print(f"Unknown: {cmd}")
