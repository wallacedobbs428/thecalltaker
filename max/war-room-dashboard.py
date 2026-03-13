#!/usr/bin/env python3
"""
War Room Dashboard — The Call Taker
Live terminal dashboard for closing hot leads.

Usage:
  python3 war-room-dashboard.py          # Full dashboard
  python3 war-room-dashboard.py refresh   # Same as above
  python3 war-room-dashboard.py status    # Quick summary line

Tracks:
  - 35 hot leads and their follow-up step (Day 0/1/3/5/7)
  - Email opens and replies
  - Demo-booked leads
  - Bland.ai credit balance
  - Today's email send count + success rate
  - Cold leads (no response after Day 7)
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
BLAND_API_KEY = os.environ.get("TCT_BLAND_API_KEY", "org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "war-room-state.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "war-room-dashboard.log")

# Hot lead tags — any contact with one of these is in the war room
HOT_TAGS = ["hot-lead", "hot-demo", "engaged-demo", "demo-caller", "pilot-candidate"]
BOOKED_TAGS = ["demo-booked", "demo-scheduled", "booked"]
REPLIED_TAGS = ["replied", "positive-reply", "hot-reply"]
CONTACTED_TAGS = ["contacted", "email-sent", "sms-sent", "called"]
COLD_TAGS = ["cold", "breakup-sent", "no-response"]

# Follow-up day buckets
FOLLOWUP_DAYS = [0, 1, 3, 5, 7]

# High-value industries (ranked by close probability)
HIGH_VALUE_INDUSTRIES = ["hvac", "plumbing", "dental", "roofing", "locksmith", "electrical", "towing", "water-damage"]

# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] WARROOM: {msg}"
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
        "User-Agent": "WarRoomDashboard/1.0 TheCallTaker",
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
        except URLError as e:
            log(f"GHL Network Error: {method} {path} — {e.reason}")
            if attempt < 2:
                time.sleep(5)
                continue
            return None
        except Exception as e:
            log(f"GHL Error: {method} {path} — {e}")
            return None
    return None


def bland_request(method, path):
    url = f"https://api.bland.ai/v1{path}"
    headers = {
        "Authorization": BLAND_API_KEY,
        "Content-Type": "application/json",
    }
    req = Request(url, headers=headers, method=method)
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        log(f"Bland.ai Error: {e}")
        return None


def save_state(data):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, STATE_FILE)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


# ===================================================
# FETCH HOT LEADS
# ===================================================

def get_hot_leads():
    """Fetch all contacts tagged as hot leads."""
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
                tags = [t.lower() for t in c.get("tags", [])]
                if cid not in seen_ids and any(t in tags for t in [tag]):
                    seen_ids.add(cid)
                    hot_leads.append(c)
            if len(batch) < 100:
                break
            page += 1
            time.sleep(0.5)

    return hot_leads


def get_conversations_for_contact(contact_id):
    """Get recent messages for a contact."""
    resp = ghl_request("GET",
        f"/conversations/search?contactId={contact_id}&locationId={GHL_LOCATION_ID}",
        version="2021-04-15")
    if not resp or "conversations" not in resp:
        return []
    convos = resp.get("conversations", [])
    if not convos:
        return []
    # Get messages from first conversation
    convo_id = convos[0].get("id", "")
    if not convo_id:
        return []
    msg_resp = ghl_request("GET",
        f"/conversations/{convo_id}/messages?limit=20",
        version="2021-04-15")
    if not msg_resp:
        return []
    return msg_resp.get("messages", [])


# ===================================================
# ANALYSIS
# ===================================================

def classify_lead(contact):
    """Classify a lead's current status and follow-up day."""
    tags = [t.lower() for t in contact.get("tags", [])]
    name = f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip() or "Unknown"
    company = contact.get("companyName", "") or ""
    phone = contact.get("phone", "") or ""
    email = contact.get("email", "") or ""
    created = contact.get("dateAdded", contact.get("createdAt", ""))

    # Determine industry from tags
    industry = "unknown"
    for tag in tags:
        for ind in HIGH_VALUE_INDUSTRIES + ["pest-control", "med-spa", "legal", "veterinary",
            "auto-repair", "cleaning", "property-mgmt", "landscaping", "general-contractor"]:
            if ind in tag:
                industry = ind
                break

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

    # Determine follow-up step
    followup_step = "Day 0"
    for d in FOLLOWUP_DAYS:
        if days_since >= d:
            followup_step = f"Day {d}"
    if days_since > 7:
        followup_step = f"Day {days_since}"

    # Status flags
    has_replied = any(t in tags for t in REPLIED_TAGS)
    has_booked = any(t in tags for t in BOOKED_TAGS)
    has_been_contacted = any(t in tags for t in CONTACTED_TAGS)
    is_cold = days_since > 7 and not has_replied and not has_booked
    is_pilot = "pilot-active" in tags or "pilot-signup" in tags

    return {
        "id": contact.get("id", ""),
        "name": name,
        "company": company,
        "phone": phone,
        "email": email,
        "industry": industry,
        "tags": tags,
        "days_since": days_since,
        "followup_step": followup_step,
        "has_replied": has_replied,
        "has_booked": has_booked,
        "has_been_contacted": has_been_contacted,
        "is_cold": is_cold,
        "is_pilot": is_pilot,
        "created": created,
    }


def get_bland_balance():
    """Check Bland.ai credit balance."""
    resp = bland_request("GET", "/me")
    if resp:
        return resp.get("billing", {}).get("credits", resp.get("credits", "??"))
    return "API Error"


def get_todays_email_stats(leads):
    """Count today's email sends from tags/conversations."""
    today = datetime.now().strftime("%Y-%m-%d")
    sent = 0
    success = 0
    for lead in leads:
        tags = lead.get("tags", [])
        if any("email-sent" in t.lower() for t in tags):
            sent += 1
            if any(t.lower() in ["opened", "email-opened", "clicked"] for t in tags):
                success += 1
    return sent, success


# ===================================================
# DISPLAY
# ===================================================

def print_header():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print()
    print("=" * 72)
    print(f"  THE CALL TAKER — WAR ROOM DASHBOARD")
    print(f"  {now}")
    print("=" * 72)


def print_section(title):
    print()
    print(f"  --- {title} ---")
    print()


def render_dashboard():
    """Main dashboard render."""
    print_header()

    # Fetch leads
    print("  Pulling hot leads from GHL...")
    raw_leads = get_hot_leads()
    leads = [classify_lead(c) for c in raw_leads]
    total = len(leads)

    print(f"  Found {total} hot leads")

    # ---- FOLLOW-UP PIPELINE ----
    print_section(f"FOLLOW-UP PIPELINE ({total} leads)")

    # Group by follow-up step
    buckets = {}
    for lead in leads:
        step = lead["followup_step"]
        if step not in buckets:
            buckets[step] = []
        buckets[step].append(lead)

    for day in ["Day 0", "Day 1", "Day 3", "Day 5", "Day 7"]:
        group = buckets.get(day, [])
        bar = "#" * len(group)
        print(f"  {day:8s} [{len(group):2d}] {bar}")

    # Overflow (Day 8+)
    overflow = [l for l in leads if l["days_since"] > 7]
    if overflow:
        bar = "#" * len(overflow)
        print(f"  {'Day 8+':8s} [{len(overflow):2d}] {bar}")

    # ---- ENGAGEMENT ----
    replied = [l for l in leads if l["has_replied"]]
    booked = [l for l in leads if l["has_booked"]]
    pilots = [l for l in leads if l["is_pilot"]]
    cold = [l for l in leads if l["is_cold"]]

    print_section("ENGAGEMENT")
    print(f"  Replied / Opened     {len(replied):3d}  ", end="")
    if replied:
        names = ", ".join(l["name"] for l in replied[:5])
        print(f"({names})")
    else:
        print("(none yet)")

    print(f"  Demo Booked          {len(booked):3d}  ", end="")
    if booked:
        names = ", ".join(l["name"] for l in booked[:5])
        print(f"({names})")
    else:
        print("(none yet)")

    print(f"  Pilot Active         {len(pilots):3d}  ", end="")
    if pilots:
        names = ", ".join(l["name"] for l in pilots[:5])
        print(f"({names})")
    else:
        print("(none yet)")

    print(f"  Gone Cold (Day 7+)   {len(cold):3d}  ", end="")
    if cold:
        names = ", ".join(l["name"] for l in cold[:5])
        print(f"({names})")
    else:
        print("(none yet)")

    # ---- BLAND.AI BALANCE ----
    print_section("BLAND.AI CREDITS")
    balance = get_bland_balance()
    print(f"  Balance: {balance}")

    # ---- EMAIL STATS ----
    print_section("TODAY'S EMAIL STATS")
    sent, success = get_todays_email_stats(raw_leads)
    rate = f"{(success/sent*100):.0f}%" if sent > 0 else "N/A"
    print(f"  Sent:    {sent}")
    print(f"  Opened:  {success}")
    print(f"  Rate:    {rate}")

    # ---- TOP PRIORITY LEADS ----
    print_section("TOP 10 PRIORITY LEADS (closest to closing)")

    # Score leads: replied > booked > pilot > high-value industry > has phone > recent
    def close_score(lead):
        score = 0
        if lead["has_booked"]:
            score += 100
        if lead["has_replied"]:
            score += 80
        if lead["is_pilot"]:
            score += 70
        if lead["industry"] in HIGH_VALUE_INDUSTRIES[:4]:
            score += 30
        elif lead["industry"] in HIGH_VALUE_INDUSTRIES:
            score += 15
        if lead["phone"]:
            score += 20
        if lead["has_been_contacted"]:
            score += 10
        # Prefer recent leads
        if lead["days_since"] <= 3:
            score += 15
        elif lead["days_since"] <= 7:
            score += 5
        # Penalize cold
        if lead["is_cold"]:
            score -= 40
        return score

    sorted_leads = sorted(leads, key=close_score, reverse=True)

    for i, lead in enumerate(sorted_leads[:10], 1):
        status = ""
        if lead["has_booked"]:
            status = "BOOKED"
        elif lead["has_replied"]:
            status = "REPLIED"
        elif lead["is_pilot"]:
            status = "PILOT"
        elif lead["is_cold"]:
            status = "COLD"
        else:
            status = lead["followup_step"]

        ind = lead["industry"][:8] if lead["industry"] != "unknown" else "---"
        phone_flag = "P" if lead["phone"] else " "
        print(f"  {i:2d}. [{status:8s}] {lead['name']:25s} {lead['company'][:22]:22s} {ind:8s} {phone_flag}")

    # ---- COLD LEADS DETAIL ----
    if cold:
        print_section(f"COLD LEADS — NEED RESCUE ({len(cold)})")
        for lead in cold:
            days = lead["days_since"]
            print(f"  - {lead['name']:25s} {lead['company'][:22]:22s} Day {days} — no response")

    # ---- SAVE STATE ----
    state = {
        "last_run": datetime.now().isoformat(),
        "total_hot": total,
        "replied": len(replied),
        "booked": len(booked),
        "pilots": len(pilots),
        "cold": len(cold),
        "bland_balance": str(balance),
        "emails_sent_today": sent,
        "leads": [{"id": l["id"], "name": l["name"], "status": "booked" if l["has_booked"]
                   else "replied" if l["has_replied"] else "pilot" if l["is_pilot"]
                   else "cold" if l["is_cold"] else "active"} for l in sorted_leads],
    }
    save_state(state)

    # ---- BOTTOM LINE ----
    print()
    print("=" * 72)
    pipeline_pct = f"{len(replied)+len(booked)+len(pilots)}/{total}"
    print(f"  PIPELINE: {pipeline_pct} engaged | {len(cold)} cold | Bland: {balance}")
    print(f"  GOAL: 1 paying client from {total} hot leads")
    print("=" * 72)
    print()


def quick_status():
    """One-line status from saved state."""
    state = load_state()
    if not state:
        print("No dashboard data yet. Run: python3 war-room-dashboard.py")
        return
    last = state.get("last_run", "never")
    total = state.get("total_hot", 0)
    replied = state.get("replied", 0)
    booked = state.get("booked", 0)
    cold = state.get("cold", 0)
    balance = state.get("bland_balance", "??")
    print(f"[{last}] {total} hot | {replied} replied | {booked} booked | {cold} cold | Bland: {balance}")


# ===================================================
# MAIN
# ===================================================

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "refresh"

    if cmd == "status":
        quick_status()
    elif cmd in ("refresh", "run", "dashboard"):
        render_dashboard()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 war-room-dashboard.py [refresh|status]")
        sys.exit(1)
