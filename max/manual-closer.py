#!/usr/bin/env python3
"""
Manual Closer — The Call Taker
Pulls hot leads from GHL, ranks by close probability, generates personalized openers.

Usage:
  python3 manual-closer.py             # Full ranked list with openers
  python3 manual-closer.py top10       # Just top 10
  python3 manual-closer.py export      # Save to manual-closer-list.json

Wallace texts these openers manually to close deals.
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

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "manual-closer-list.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "manual-closer.log")

# Tags that indicate a hot lead
HOT_TAGS = ["hot-lead", "hot-demo", "engaged-demo", "demo-caller", "pilot-candidate"]

# Industries ranked by close probability and job value
INDUSTRY_RANK = {
    "hvac": 1, "plumbing": 2, "dental": 3, "roofing": 4, "locksmith": 5,
    "electrical": 6, "towing": 7, "water-damage": 8, "pest-control": 9,
    "med-spa": 10, "legal": 11, "veterinary": 12, "auto-repair": 13,
    "cleaning": 14, "property-mgmt": 15, "landscaping": 16,
    "general-contractor": 17, "garage-door": 18, "funeral": 19,
}

# Industry-specific pain points for openers
INDUSTRY_HOOKS = {
    "hvac": "after-hours emergency calls",
    "plumbing": "after-hours calls",
    "dental": "new patient calls",
    "roofing": "storm damage calls",
    "locksmith": "late-night lockout calls",
    "electrical": "emergency service calls",
    "towing": "after-hours tow requests",
    "water-damage": "emergency flood calls",
    "pest-control": "service inquiries",
    "med-spa": "appointment bookings",
    "legal": "client intake calls",
    "veterinary": "after-hours pet emergencies",
    "auto-repair": "service appointment calls",
    "cleaning": "booking calls",
    "property-mgmt": "tenant calls",
    "landscaping": "estimate requests",
    "general-contractor": "project inquiries",
    "garage-door": "emergency repair calls",
    "funeral": "family calls",
}

# Job value by industry (for urgency framing)
JOB_VALUES = {
    "hvac": "$300-800", "plumbing": "$200-600", "dental": "$400-2,000",
    "roofing": "$5,000-15,000", "locksmith": "$150-400", "electrical": "$200-500",
    "towing": "$150-300", "water-damage": "$2,000-10,000", "pest-control": "$200-500",
    "med-spa": "$300-1,500", "legal": "$2,000-10,000", "veterinary": "$200-800",
}

# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] CLOSER: {msg}"
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
        "User-Agent": "ManualCloser/1.0 TheCallTaker",
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


# ===================================================
# FETCH + CLASSIFY
# ===================================================

def get_hot_leads():
    """Fetch all hot-tagged contacts from GHL."""
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
    """Detect industry from GHL tags."""
    for tag in tags:
        tag_lower = tag.lower()
        for industry in INDUSTRY_RANK:
            if industry in tag_lower:
                return industry
    return "unknown"


def build_lead_profile(contact):
    """Build a full lead profile from a GHL contact."""
    tags = [t.lower() for t in contact.get("tags", [])]
    first = contact.get("firstName", "") or ""
    last = contact.get("lastName", "") or ""
    name = f"{first} {last}".strip() or "Unknown"
    company = contact.get("companyName", "") or ""
    phone = contact.get("phone", "") or ""
    email = contact.get("email", "") or ""
    city = contact.get("city", "") or ""
    state = contact.get("state", "") or ""
    location = f"{city}, {state}".strip(", ") if city or state else ""

    industry = detect_industry(tags)
    created = contact.get("dateAdded", contact.get("createdAt", ""))

    # Days since creation
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

    # Status flags
    has_replied = any(t in tags for t in ["replied", "positive-reply", "hot-reply"])
    has_booked = any(t in tags for t in ["demo-booked", "demo-scheduled", "booked"])
    has_been_contacted = any(t in tags for t in ["contacted", "email-sent", "sms-sent", "called"])
    is_pilot = "pilot-active" in tags or "pilot-signup" in tags

    return {
        "id": contact.get("id", ""),
        "name": name,
        "first_name": first,
        "company": company,
        "phone": phone,
        "email": email,
        "location": location,
        "industry": industry,
        "tags": tags,
        "days_since": days_since,
        "has_replied": has_replied,
        "has_booked": has_booked,
        "has_been_contacted": has_been_contacted,
        "is_pilot": is_pilot,
        "created": created,
    }


def close_score(lead):
    """Score 0-100 for how likely this lead is to close."""
    score = 50  # Base

    # Engagement signals
    if lead["has_booked"]:
        score += 40
    if lead["has_replied"]:
        score += 30
    if lead["is_pilot"]:
        score += 35

    # Contact info quality
    if lead["phone"]:
        score += 15
    if lead["email"]:
        score += 5

    # Industry value
    ind_rank = INDUSTRY_RANK.get(lead["industry"], 20)
    if ind_rank <= 3:
        score += 20
    elif ind_rank <= 6:
        score += 12
    elif ind_rank <= 10:
        score += 5

    # Recency
    if lead["days_since"] <= 1:
        score += 15
    elif lead["days_since"] <= 3:
        score += 10
    elif lead["days_since"] <= 7:
        score += 5
    elif lead["days_since"] > 14:
        score -= 20

    # Been contacted but no reply = less likely
    if lead["has_been_contacted"] and not lead["has_replied"]:
        score -= 10

    return max(0, min(100, score))


def generate_opener(lead):
    """Generate a personalized 1-sentence text opener for Wallace."""
    first = lead["first_name"] or lead["name"].split()[0] if lead["name"] != "Unknown" else ""
    company = lead["company"]
    industry = lead["industry"]
    location = lead["location"]
    hook = INDUSTRY_HOOKS.get(industry, "after-hours calls")
    value = JOB_VALUES.get(industry, "$200-500")

    # Build the opener based on what we know
    if first and company and location:
        return f"Hey {first}, saw you run {company} in {location} — had a quick question about your {hook}"
    elif first and company:
        return f"Hey {first}, saw you run {company} — had a quick question about your {hook}"
    elif first and industry != "unknown":
        return f"Hey {first}, quick question — how are you handling {hook} right now?"
    elif first:
        return f"Hey {first}, quick question about your business — are you missing any calls after hours?"
    elif company:
        return f"Hey, reaching out to {company} — quick question about your {hook}"
    else:
        return f"Hey, quick question — how are you handling after-hours calls for your business right now?"


# ===================================================
# DISPLAY
# ===================================================

def print_lead_list(leads, limit=None):
    """Print the ranked lead list with openers."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("=" * 80)
    print(f"  THE CALL TAKER — MANUAL CLOSER LIST")
    print(f"  {now}")
    print(f"  {len(leads)} hot leads ranked by close probability")
    print("=" * 80)

    display = leads[:limit] if limit else leads

    for i, lead in enumerate(display, 1):
        score = close_score(lead)

        # Status badge
        if lead["has_booked"]:
            badge = "BOOKED"
        elif lead["has_replied"]:
            badge = "REPLIED"
        elif lead["is_pilot"]:
            badge = "PILOT"
        elif lead["has_been_contacted"]:
            badge = "SENT"
        else:
            badge = "NEW"

        # Score bar
        filled = score // 5
        bar = "█" * filled + "░" * (20 - filled)

        ind = lead["industry"] if lead["industry"] != "unknown" else "---"

        print()
        print(f"  #{i:2d}  [{badge:8s}]  Score: {score}/100  {bar}")
        print(f"       {lead['name']}")
        if lead["company"]:
            print(f"       {lead['company']}", end="")
            if lead["location"]:
                print(f" — {lead['location']}", end="")
            print()
        print(f"       Industry: {ind}  |  Day {lead['days_since']}  |  Phone: {lead['phone'] or 'NONE'}")

        # The opener Wallace texts right now
        opener = generate_opener(lead)
        print(f"       ╰─▶ \"{opener}\"")

    # Summary
    with_phone = sum(1 for l in leads if l["phone"])
    replied = sum(1 for l in leads if l["has_replied"])
    booked = sum(1 for l in leads if l["has_booked"])

    print()
    print("-" * 80)
    print(f"  SUMMARY: {len(leads)} leads | {with_phone} have phone | {replied} replied | {booked} booked")
    print(f"  ACTION: Text the top 10 right now. Call anyone who replies within 5 min.")
    print("-" * 80)
    print()


def export_list(leads):
    """Save lead list to JSON for other scripts."""
    export = []
    for lead in leads:
        export.append({
            "id": lead["id"],
            "name": lead["name"],
            "company": lead["company"],
            "phone": lead["phone"],
            "email": lead["email"],
            "industry": lead["industry"],
            "location": lead["location"],
            "score": close_score(lead),
            "opener": generate_opener(lead),
            "days_since": lead["days_since"],
            "has_replied": lead["has_replied"],
            "has_booked": lead["has_booked"],
        })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(export, f, indent=2)
    print(f"Exported {len(export)} leads to {OUTPUT_FILE}")


# ===================================================
# MAIN
# ===================================================

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    print("Pulling hot leads from GHL...")
    raw_leads = get_hot_leads()
    leads = [build_lead_profile(c) for c in raw_leads]

    # Sort by close score descending
    leads.sort(key=close_score, reverse=True)

    log(f"Fetched {len(leads)} hot leads")

    if cmd == "top10":
        print_lead_list(leads, limit=10)
    elif cmd == "export":
        print_lead_list(leads)
        export_list(leads)
    elif cmd in ("all", "list", "run"):
        print_lead_list(leads)
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 manual-closer.py [all|top10|export]")
        sys.exit(1)
