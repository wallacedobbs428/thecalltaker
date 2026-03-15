#!/usr/bin/env python3
"""
Lead Scorer — The Call Taker
Scores hot-lead contacts 1-10 and tags top 10 as priority-close.
Commands: score, status
"""

import sys
import os
import json
import tempfile
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ── Config ──────────────────────────────────────────────────────────────────

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

NTFY_SALES = "tct-sales-63uYsIT9"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "lead-scorer-state.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "lead-scorer.log")

SKIP_TAGS = {"customer", "active-client", "pilot-active", "do-not-contact", "unsubscribed"}
ENGAGEMENT_TAGS = {"replied", "demo-caller", "engaged-demo", "hot-demo", "email-opened", "positive-reply"}
HIGH_VALUE_INDUSTRIES = {"hvac", "plumbing", "dental"}
SOLO_KEYWORDS = ["solo", "one man", "owner", "mobile", "independent", "family", "brothers", "sons", "and", "&"]

# ── Logging ─────────────────────────────────────────────────────────────────

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ── GHL API ─────────────────────────────────────────────────────────────────

def ghl_request(method, path, body=None, version="2021-07-28"):
    url = f"{GHL_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": version,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "LeadScorer/1.0 TheCallTaker",
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

# ── ntfy ────────────────────────────────────────────────────────────────────

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

# ── State ───────────────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            log(f"State load error: {e}")
    return {"last_scored": None, "scores": {}}


def save_state(state):
    try:
        fd, tmp_path = tempfile.mkstemp(dir=SCRIPT_DIR, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, STATE_FILE)
    except Exception as e:
        log(f"State save error: {e}")
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

# ── Scoring ─────────────────────────────────────────────────────────────────

def score_contact(contact):
    """Score a contact 1-10 based on defined criteria."""
    score = 0
    tags = [t.lower() for t in (contact.get("tags") or [])]

    # +3: has phone number
    phone = contact.get("phone") or ""
    if phone.strip():
        score += 3

    # +2: high-value industry
    industry = ""
    custom_fields = contact.get("customFields") or contact.get("customField") or []
    # Industry might be in tags or custom fields
    for tag in tags:
        if tag in HIGH_VALUE_INDUSTRIES:
            industry = tag
            score += 2
            break
    if not industry:
        # Check company name or tags for industry hints
        company = (contact.get("companyName") or "").lower()
        for ind in HIGH_VALUE_INDUSTRIES:
            if ind in company:
                industry = ind
                score += 2
                break

    # +2: Nashville or Tennessee
    city = (contact.get("city") or "").lower().strip()
    state = (contact.get("state") or "").lower().strip()
    if city == "nashville" or state in ("tennessee", "tn"):
        score += 2

    # +2: has been contacted AND has engagement tags
    engagement_found = any(t in ENGAGEMENT_TAGS for t in tags)
    contacted = any(t in tags for t in ["contacted", "emailed", "sms-sent", "called", "blast-sent", "funnel-enrolled"])
    if contacted and engagement_found:
        score += 2

    # +1: solo/small operator keywords in business name
    company = (contact.get("companyName") or "").lower()
    if company:
        for kw in SOLO_KEYWORDS:
            if kw in company:
                score += 1
                break

    # Clamp to 1-10
    score = max(1, min(10, score))
    return score


def get_industry_from_tags(tags):
    """Extract industry name from tags."""
    for tag in tags:
        t = tag.lower()
        if t in HIGH_VALUE_INDUSTRIES:
            return t.upper()
        # Check for other industry tags
        industry_tags = [
            "locksmith", "hvac", "plumbing", "electrical", "roofing",
            "pest-control", "towing", "dental", "med-spa", "legal",
            "veterinary", "auto-repair", "cleaning", "property-mgmt",
            "water-damage", "landscaping", "general-contractor",
        ]
        for ind in industry_tags:
            if t == ind or t == ind.replace("-", " "):
                return ind.replace("-", " ").title()
    return "Unknown"


def cmd_score():
    """Score all hot-lead contacts and tag top 10 as priority-close."""
    log("═══ Lead Scorer — score run starting ═══")

    # Fetch all contacts
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

    log(f"Fetched {len(contacts)} total contacts")

    # Filter to hot-lead only, skip excluded tags
    hot_leads = []
    for c in contacts:
        tags = set(t.lower() for t in (c.get("tags") or []))
        if "hot-lead" not in tags:
            continue
        if tags & SKIP_TAGS:
            log(f"Skipping {c.get('contactName', 'Unknown')} — has skip tag")
            continue
        hot_leads.append(c)

    log(f"Found {len(hot_leads)} hot-lead contacts after filtering")

    if not hot_leads:
        log("No hot-lead contacts to score")
        return

    # Score each contact
    scored = []
    for c in hot_leads:
        s = score_contact(c)
        tags = [t.lower() for t in (c.get("tags") or [])]
        industry = get_industry_from_tags(tags)
        scored.append({
            "id": c.get("id"),
            "name": c.get("contactName") or c.get("firstName", "Unknown"),
            "company": c.get("companyName") or "—",
            "industry": industry,
            "phone": c.get("phone") or "—",
            "city": c.get("city") or "—",
            "state": c.get("state") or "—",
            "score": s,
            "existing_tags": c.get("tags") or [],
        })

    # Sort highest to lowest
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Print ranked list
    log("")
    log("═══ RANKED HOT LEADS ═══")
    for i, lead in enumerate(scored, 1):
        location = f"{lead['city']}, {lead['state']}"
        line = f"[{lead['score']}] {lead['name']} — {lead['company']} — {lead['industry']} — {lead['phone']} — {location}"
        log(f"  {i}. {line}")

    # Tag top 10 as priority-close
    tagged_count = 0
    for lead in scored[:10]:
        existing = list(lead["existing_tags"])
        if "priority-close" in [t.lower() for t in existing]:
            log(f"  Already tagged priority-close: {lead['name']}")
            tagged_count += 1
            continue
        new_tags = existing + ["priority-close"]
        resp = ghl_request("PUT", f"/contacts/{lead['id']}", body={"tags": new_tags})
        if resp:
            log(f"  Tagged priority-close: {lead['name']} (score {lead['score']})")
            tagged_count += 1
        else:
            log(f"  Failed to tag: {lead['name']}")
        time.sleep(0.5)  # rate limit courtesy

    log(f"Tagged {tagged_count} contacts as priority-close")

    # Save state
    state = load_state()
    state["last_scored"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for lead in scored:
        state["scores"][lead["id"]] = {
            "name": lead["name"],
            "score": lead["score"],
            "scored_at": state["last_scored"],
        }
    save_state(state)

    # Send ntfy summary with top 5
    top5_lines = []
    for i, lead in enumerate(scored[:5], 1):
        top5_lines.append(f"{i}. [{lead['score']}] {lead['name']} — {lead['company']} ({lead['industry']})")
    summary = f"Scored {len(scored)} hot leads. Top 10 tagged priority-close.\n\n"
    summary += "Top 5:\n" + "\n".join(top5_lines)
    ntfy(NTFY_SALES, "Lead Scorer — Top Leads", summary, priority="default", tags="chart_with_upwards_trend")

    log(f"═══ Lead Scorer complete — {len(scored)} scored, {tagged_count} tagged ═══")


def cmd_status():
    """Show last scoring run info."""
    state = load_state()
    last = state.get("last_scored", "Never")
    count = len(state.get("scores", {}))
    log(f"Lead Scorer Status")
    log(f"  Last scored: {last}")
    log(f"  Contacts in state: {count}")

    if count > 0:
        # Show top 5 from state
        scores = state["scores"]
        ranked = sorted(scores.items(), key=lambda x: x[1].get("score", 0), reverse=True)
        log(f"  Top 5 from last run:")
        for i, (cid, info) in enumerate(ranked[:5], 1):
            log(f"    {i}. [{info.get('score', '?')}] {info.get('name', 'Unknown')}")


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 lead-scorer.py <command>")
        print("Commands: score, status")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "score":
        cmd_score()
    elif command == "status":
        cmd_status()
    else:
        print(f"Unknown command: {command}")
        print("Commands: score, status")
        sys.exit(1)
