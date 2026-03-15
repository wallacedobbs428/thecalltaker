#!/usr/bin/env python3
"""
DM OUTREACH v2 — The Call Taker
================================
3-DM automated sequence system for HVAC, Plumbing, Roofing, and Dental
businesses found via scraper that have Instagram or Facebook.

Replaces the old dm-tracker.py (which only generated manual lists with no
sequence logic, no industry copy, and no state per step).

Sequence:
  DM 1: Compliment + one-sentence pitch (no link)
  DM 2: Pain point question (3 days later, no response)
  DM 3: Proof + demo line (5 days after DM 2, no response)

Commands:
  generate    — Scan GHL for candidates, write today's DM list
  log <id> <platform> <step> <status>
              — Log a DM action manually
              — platform: instagram|facebook
              — step: 1|2|3
              — status: sent|replied|booked
  advance     — Advance contacts to next DM step if enough time has passed
  candidates  — Scan GHL for new DM candidates only (no list generation)
  status      — Print stats and active pipeline
  export      — Print formatted copy-paste DM list for today

State file:  ~/thecalltaker/ops/dm-outreach-state.json
DM log:      ~/thecalltaker/ops/dm-log.json
Daily list:  ~/thecalltaker/ops/dm-list-today.json
Log file:    ~/thecalltaker/ops/dm-outreach.log
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GHL_API_KEY     = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL    = "https://services.leadconnectorhq.com"

NTFY_URGENT   = "tct-urgent-Hk9UOEZR"
NTFY_SALES    = "tct-sales-63uYsIT9"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"

BASE_DIR   = os.path.expanduser("~/thecalltaker/ops")
STATE_FILE = os.path.join(BASE_DIR, "dm-outreach-state.json")
DM_LOG     = os.path.join(BASE_DIR, "dm-log.json")
LIST_FILE  = os.path.join(BASE_DIR, "dm-list-today.json")
LOG_FILE   = os.path.join(BASE_DIR, "dm-outreach.log")

# Days to wait before sending each follow-up
DM2_DELAY_DAYS = 3   # DM 2 fires 3 days after DM 1 (if no response)
DM3_DELAY_DAYS = 5   # DM 3 fires 5 days after DM 2 (if no response)

# Max DMs to include in today's list (so Wallace isn't overwhelmed)
MAX_DAILY_DMS = 30

# Tags that qualify a contact for DM outreach
DM_TRIGGER_TAGS = {
    "dm-candidate", "pilot-candidate", "hot-lead",
    "sms-no-reply", "email-no-reply", "cold-outreach",
}

# Tags that permanently exclude a contact
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed", "dm-complete", "dm-replied",
}

# Map GHL industry tags → internal industry key
INDUSTRY_TAG_MAP = {
    "hvac": "hvac",
    "air-conditioning": "hvac",
    "heating-cooling": "hvac",
    "plumbing": "plumbing",
    "plumber": "plumbing",
    "roofing": "roofing",
    "roofer": "roofing",
    "dental": "dental",
    "dentist": "dental",
    "dental-office": "dental",
}

GHL_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-DMOutreach/2.0",
}

# ---------------------------------------------------------------------------
# Industry-specific DM copy
# Each entry is a dict: {1: str, 2: str, 3: str}
# Placeholders: {company}, {city}, {stars}
# ---------------------------------------------------------------------------

DM_COPY = {
    "hvac": {
        1: (
            "Hey! Saw {company} has {stars} stars on Google — that's awesome for HVAC in {city}. "
            "Quick Q: who handles your calls when your techs are out on jobs?"
        ),
        2: (
            "Do you have someone answering {company}'s phones after 5pm? "
            "Most HVAC companies we talk to say calls go to voicemail during their busiest season."
        ),
        3: (
            "We helped a Nashville HVAC company catch 4 missed calls their first week — "
            "2 turned into emergency repairs worth $900. "
            "If you want to hear what it sounds like, call (615) 784-5747."
        ),
    },
    "plumbing": {
        1: (
            "Hey! {company} looks solid — {stars} stars on Google. "
            "Quick question: what happens when someone calls about a burst pipe at midnight?"
        ),
        2: (
            "Most plumbers we talk to miss 3-5 emergency calls a week after hours. "
            "Those are $300-500 jobs going to whoever answers first."
        ),
        3: (
            "We built an AI that answers plumbing calls 24/7 — sounds human, books the job, "
            "texts you the details. One plumber went from 11 missed calls/week to zero. "
            "Call (615) 784-5747 to hear it."
        ),
    },
    "roofing": {
        1: (
            "Hey! {company} looks like you guys do great work in {city}. "
            "With storm season coming up, who handles your overflow calls?"
        ),
        2: (
            "After a hail event, most roofers get 10x normal call volume for 48 hours. "
            "First company to answer gets the inspection. What happens to your overflow?"
        ),
        3: (
            "We helped a roofing company capture an extra $15,000 in storm-season inspections "
            "by answering every call 24/7. "
            "Call (615) 784-5747 — that's our live AI demo."
        ),
    },
    "dental": {
        1: (
            "Hey! {company} has great reviews. "
            "Quick Q: does your front desk ever miss calls during lunch or when checking patients in?"
        ),
        2: (
            "The #1 complaint in 1-star dental reviews isn't the dentist — "
            "it's 'no one answered when I called.' That's a $385+ new patient gone."
        ),
        3: (
            "We built an AI receptionist for dental offices. "
            "It answers overflow calls, books appointments, sounds completely natural. "
            "Free 14-day pilot. Call (615) 784-5747 to hear it."
        ),
    },
    "generic": {
        1: (
            "Hey! {company} looks great — {stars} stars. "
            "Quick Q: who answers your phones after hours or when you're slammed?"
        ),
        2: (
            "Do you have someone answering calls after 5pm? "
            "Most service businesses lose $2K-10K/month to unanswered calls."
        ),
        3: (
            "We built an AI that answers your phone 24/7 — sounds like a real person, "
            "books the job, texts you the details. Free to try for 14 days. "
            "Call (615) 784-5747."
        ),
    },
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] dm-outreach-v2: {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# State management (atomic write)
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            log(f"State load error (starting fresh): {e}", "WARN")
    return {
        "contacts": {},          # contact_id -> contact record
        "stats": {
            "dm1_sent": 0,
            "dm2_sent": 0,
            "dm3_sent": 0,
            "instagram_sent": 0,
            "facebook_sent": 0,
            "replies": 0,
            "demos_booked": 0,
            "total_candidates": 0,
        },
        "last_run": None,
    }


def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


# ---------------------------------------------------------------------------
# DM log (append-only JSON lines)
# ---------------------------------------------------------------------------

def write_dm_log(entry: dict):
    os.makedirs(os.path.dirname(DM_LOG), exist_ok=True)
    entry["logged_at"] = datetime.now().isoformat()
    with open(DM_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# GHL API helpers
# ---------------------------------------------------------------------------

def ghl_get(path, params=None) -> dict:
    url = f"{GHL_BASE_URL}{path}"
    for attempt in range(3):
        try:
            r = requests.get(url, headers=GHL_HEADERS, params=params, timeout=30)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                log(f"GHL 429 rate limit — waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            if r.status_code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            return r.json() if r.text else {}
        except Exception as e:
            log(f"GHL GET error ({attempt+1}/3): {e}", "WARN")
            time.sleep(5)
    return {}


def ghl_post(path, body: dict) -> dict:
    url = f"{GHL_BASE_URL}{path}"
    for attempt in range(3):
        try:
            r = requests.post(url, headers=GHL_HEADERS, json=body, timeout=30)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                time.sleep(wait)
                continue
            if r.status_code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            return r.json() if r.text else {}
        except Exception as e:
            log(f"GHL POST error ({attempt+1}/3): {e}", "WARN")
            time.sleep(5)
    return {}


def add_tags(contact_id: str, tags: list):
    ghl_post(f"/contacts/{contact_id}/tags", {"tags": tags})


def remove_tags(contact_id: str, tags: list):
    url = f"{GHL_BASE_URL}/contacts/{contact_id}/tags"
    try:
        requests.delete(url, headers=GHL_HEADERS, json={"tags": tags}, timeout=30)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# ntfy
# ---------------------------------------------------------------------------

def ntfy(topic: str, title: str, message: str, priority: str = "default"):
    try:
        safe_title = title.encode("ascii", errors="ignore").decode().strip()[:128]
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={"Title": safe_title, "Priority": priority},
            timeout=10,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Copy builder
# ---------------------------------------------------------------------------

def get_industry(tags: list) -> str:
    lower_tags = [t.lower() for t in tags]
    for tag in lower_tags:
        if tag in INDUSTRY_TAG_MAP:
            return INDUSTRY_TAG_MAP[tag]
    return "generic"


def build_dm(contact: dict, step: int) -> str:
    industry = contact.get("industry", "generic")
    template = DM_COPY.get(industry, DM_COPY["generic"]).get(step, "")
    company = contact.get("company", "your business")
    city    = contact.get("city", "your area")
    stars   = contact.get("stars", "4.8")
    return template.format(company=company, city=city, stars=stars)


# ---------------------------------------------------------------------------
# GHL candidate scan
# ---------------------------------------------------------------------------

def scan_ghl_candidates(state: dict) -> int:
    log("Scanning GHL for DM candidates...")
    all_contacts = []
    page = 1
    while True:
        data = ghl_get("/contacts/", params={
            "locationId": GHL_LOCATION_ID,
            "limit": 100,
            "page": page,
        })
        if not data or "contacts" not in data:
            break
        batch = data.get("contacts", [])
        all_contacts.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > 50:
            break
        time.sleep(0.3)  # be gentle on the API

    new = 0
    for c in all_contacts:
        cid = c.get("id")
        if not cid:
            continue
        if cid in state["contacts"]:
            continue  # already tracking

        raw_tags = c.get("tags", [])
        tag_set  = {t.lower() for t in raw_tags}

        # Must have at least one trigger tag
        if not (tag_set & DM_TRIGGER_TAGS):
            continue
        # Must not be excluded
        if tag_set & EXCLUDE_TAGS:
            continue

        industry = get_industry(raw_tags)
        company  = (c.get("companyName") or c.get("name") or "").strip() or "Unknown"
        city     = (c.get("city") or "").strip() or "your area"
        # Pull star rating from a custom field if present; default to 4.8
        stars    = "4.8"
        for cf in c.get("customFields", []):
            if isinstance(cf, dict) and "review" in cf.get("id", "").lower():
                val = str(cf.get("value", "")).strip()
                if val:
                    stars = val

        # Try to find social handles from website or custom fields
        instagram_handle = ""
        facebook_handle  = ""
        website = (c.get("website") or "").strip()
        for cf in c.get("customFields", []):
            if not isinstance(cf, dict):
                continue
            cid_key = cf.get("id", "").lower()
            val     = str(cf.get("value", "")).strip()
            if "instagram" in cid_key:
                instagram_handle = val.lstrip("@")
            if "facebook" in cid_key:
                facebook_handle = val

        # Determine which platform(s) to DM on
        platforms = []
        if instagram_handle:
            platforms.append("instagram")
        if facebook_handle:
            platforms.append("facebook")
        # If no explicit handle but website contains instagram.com / facebook.com
        if not platforms:
            if "instagram.com" in website:
                platforms.append("instagram")
            if "facebook.com" in website:
                platforms.append("facebook")

        # Even if we can't find a handle we still track them — Wallace can look it up
        if not platforms:
            platforms = ["instagram"]  # default to Instagram for outreach

        record = {
            "added":            datetime.now().isoformat(),
            "company":          company,
            "city":             city,
            "stars":            stars,
            "industry":         industry,
            "email":            c.get("email", ""),
            "phone":            c.get("phone", ""),
            "website":          website,
            "instagram_handle": instagram_handle,
            "facebook_handle":  facebook_handle,
            "platforms":        platforms,
            # Per-platform sequence tracking
            "sequences": {
                p: {
                    "step":           0,       # 0 = not started, 1 = DM1 sent, 2 = DM2 sent, 3 = DM3 sent
                    "step1_sent_at":  None,
                    "step2_sent_at":  None,
                    "step3_sent_at":  None,
                    "replied":        False,
                    "replied_at":     None,
                    "booked":         False,
                } for p in platforms
            },
            "complete": False,  # True when all platforms exhausted or booked
        }
        state["contacts"][cid] = record
        state["stats"]["total_candidates"] += 1
        new += 1

    log(f"Found {new} new DM candidates. Total tracked: {len(state['contacts'])}")
    return new


# ---------------------------------------------------------------------------
# Advance: promote contacts ready for next step
# ---------------------------------------------------------------------------

def cmd_advance(state: dict):
    """Advance contacts whose wait period has expired to the next step."""
    now = datetime.now()
    advanced = 0
    for cid, rec in state["contacts"].items():
        if rec.get("complete"):
            continue
        for platform, seq in rec.get("sequences", {}).items():
            if seq.get("replied") or seq.get("booked"):
                continue
            step = seq.get("step", 0)
            if step == 0:
                continue  # not started yet — generate will pick it up

            if step == 1:
                # Ready for DM 2?
                sent_at = seq.get("step1_sent_at")
                if not sent_at:
                    continue
                elapsed = (now - datetime.fromisoformat(sent_at)).days
                if elapsed >= DM2_DELAY_DAYS:
                    seq["step"] = 2
                    advanced += 1
                    log(f"Advanced {rec['company']} ({platform}) to step 2 "
                        f"({elapsed}d since DM 1)")

            elif step == 2:
                # Ready for DM 3?
                sent_at = seq.get("step2_sent_at")
                if not sent_at:
                    continue
                elapsed = (now - datetime.fromisoformat(sent_at)).days
                if elapsed >= DM3_DELAY_DAYS:
                    seq["step"] = 3
                    advanced += 1
                    log(f"Advanced {rec['company']} ({platform}) to step 3 "
                        f"({elapsed}d since DM 2)")

            elif step == 3:
                # DM 3 already queued or sent — check if sequence is done
                sent_at = seq.get("step3_sent_at")
                if sent_at:
                    # Sequence complete for this platform
                    pass  # nothing to advance

    if advanced:
        log(f"Advanced {advanced} contact-platform pairs to next step.")
        save_state(state)
    else:
        log("No contacts ready for advancement.")
    return advanced


# ---------------------------------------------------------------------------
# Generate today's DM list
# ---------------------------------------------------------------------------

def cmd_generate(state: dict):
    """Scan GHL, advance eligible contacts, then write today's DM list."""
    log("=== GENERATE: building today's DM list ===")
    state["last_run"] = datetime.now().isoformat()

    # 1. Pull fresh candidates
    new = scan_ghl_candidates(state)

    # 2. Advance anyone ready for next step
    cmd_advance(state)

    # 3. Build the list
    dm_list = {
        "date":      datetime.now().strftime("%Y-%m-%d"),
        "instagram": [],
        "facebook":  [],
    }

    for cid, rec in state["contacts"].items():
        if rec.get("complete"):
            continue
        for platform, seq in rec.get("sequences", {}).items():
            if seq.get("replied") or seq.get("booked"):
                continue

            step = seq.get("step", 0)
            # step 0 = not yet started (needs DM 1)
            # step 1 = DM 1 sent, waiting (not ready for DM 2 yet unless advanced)
            # step 2 = ready for DM 2 (was advanced)
            # step 3 = ready for DM 3 (was advanced)
            # If step is 1 or 3-already-sent, skip (nothing to send right now)

            needs_send = step in (0, 2, 3) and not (
                (step == 0 and seq.get("step1_sent_at")) or
                (step == 2 and seq.get("step2_sent_at")) or
                (step == 3 and seq.get("step3_sent_at"))
            )

            if not needs_send:
                continue

            # Which DM number to write
            dm_num = 1 if step == 0 else step
            message = build_dm(rec, dm_num)

            handle = (
                rec.get("instagram_handle") if platform == "instagram"
                else rec.get("facebook_handle")
            ) or rec.get("company", "Unknown")

            entry = {
                "contact_id":  cid,
                "company":     rec.get("company", "Unknown"),
                "city":        rec.get("city", ""),
                "industry":    rec.get("industry", "generic"),
                "platform":    platform,
                "handle":      handle,
                "dm_step":     dm_num,
                "message":     message,
                "website":     rec.get("website", ""),
            }
            dm_list[platform].append(entry)

    # Sort: DM 1 first (discovery), then follow-ups, then last-chance
    for platform in ("instagram", "facebook"):
        dm_list[platform].sort(key=lambda x: x["dm_step"])
        # Cap per platform
        dm_list[platform] = dm_list[platform][:MAX_DAILY_DMS]

    # 4. Write the list file
    os.makedirs(os.path.dirname(LIST_FILE), exist_ok=True)
    with open(LIST_FILE, "w") as f:
        json.dump(dm_list, f, indent=2)

    ig_count = len(dm_list["instagram"])
    fb_count = len(dm_list["facebook"])
    total    = ig_count + fb_count

    log(f"DM list written: {ig_count} Instagram, {fb_count} Facebook ({total} total)")
    log(f"File: {LIST_FILE}")

    if total > 0:
        ntfy(
            NTFY_SALES,
            "DM List Ready",
            f"Today's DM list is ready.\n"
            f"Instagram: {ig_count} | Facebook: {fb_count}\n"
            f"Run: python3 dm-outreach-v2.py export",
        )

    save_state(state)
    return dm_list


# ---------------------------------------------------------------------------
# Log a DM action
# ---------------------------------------------------------------------------

def cmd_log(state: dict, contact_id: str, platform: str, step: str, status: str):
    """Record that Wallace sent or received a response to a DM."""
    platform = platform.lower()
    status   = status.lower()

    try:
        step_int = int(step)
    except ValueError:
        print("ERROR: step must be 1, 2, or 3")
        sys.exit(1)

    if platform not in ("instagram", "facebook"):
        print("ERROR: platform must be 'instagram' or 'facebook'")
        sys.exit(1)

    if status not in ("sent", "replied", "booked"):
        print("ERROR: status must be 'sent', 'replied', or 'booked'")
        sys.exit(1)

    if contact_id not in state["contacts"]:
        print(f"ERROR: Contact {contact_id} not tracked. Run 'candidates' first.")
        sys.exit(1)

    rec = state["contacts"][contact_id]
    if platform not in rec.get("sequences", {}):
        # Auto-add platform if missing
        rec.setdefault("sequences", {})[platform] = {
            "step": 0,
            "step1_sent_at": None,
            "step2_sent_at": None,
            "step3_sent_at": None,
            "replied": False,
            "replied_at": None,
            "booked": False,
        }
        if platform not in rec.get("platforms", []):
            rec.setdefault("platforms", []).append(platform)

    seq = rec["sequences"][platform]
    now_iso = datetime.now().isoformat()

    if status == "sent":
        seq[f"step{step_int}_sent_at"] = now_iso
        # Update current step if this is a new high-water mark
        if seq.get("step", 0) < step_int:
            seq["step"] = step_int
        # For step 1 only: advance internal state so we start the wait clock
        # (step 2 and 3 are set by advance command)
        state["stats"][f"dm{step_int}_sent"] += 1
        state["stats"][f"{platform}_sent"] += 1
        log(f"DM {step_int} sent on {platform} to {rec.get('company')} (step recorded)")

        write_dm_log({
            "event":      "sent",
            "contact_id": contact_id,
            "company":    rec.get("company"),
            "platform":   platform,
            "step":       step_int,
        })
        # Tag in GHL
        add_tags(contact_id, [f"dm{step_int}-sent", f"dm-{platform}"])

    elif status == "replied":
        seq["replied"]    = True
        seq["replied_at"] = now_iso
        state["stats"]["replies"] += 1
        log(f"REPLY from {rec.get('company')} on {platform} DM {step_int} — tagging hot-lead")

        write_dm_log({
            "event":      "replied",
            "contact_id": contact_id,
            "company":    rec.get("company"),
            "platform":   platform,
            "step":       step_int,
        })
        add_tags(contact_id, ["hot-lead", "dm-replied", "contacted"])
        ntfy(
            NTFY_URGENT,
            "[CRITICAL] DM Reply — Hot Lead",
            f"{rec.get('company')} replied to DM {step_int} on {platform}.\n"
            f"Industry: {rec.get('industry', 'unknown')}\n"
            f"Contact: {contact_id}",
            priority="urgent",
        )

    elif status == "booked":
        seq["replied"] = True
        seq["booked"]  = True
        rec["complete"] = True
        state["stats"]["demos_booked"] += 1
        log(f"DEMO BOOKED via {platform} DM: {rec.get('company')}")

        write_dm_log({
            "event":      "booked",
            "contact_id": contact_id,
            "company":    rec.get("company"),
            "platform":   platform,
            "step":       step_int,
        })
        add_tags(contact_id, ["demo-booked", "contacted", "dm-replied"])
        ntfy(
            NTFY_URGENT,
            "[CRITICAL] Demo Booked via DM!",
            f"{rec.get('company')} booked a demo via {platform} DM {step_int}!\n"
            f"Industry: {rec.get('industry', 'unknown')}",
            priority="urgent",
        )

    save_state(state)
    print(f"Logged: {status} | {rec.get('company')} | {platform} | DM {step_int}")


# ---------------------------------------------------------------------------
# Candidates only
# ---------------------------------------------------------------------------

def cmd_candidates(state: dict):
    new = scan_ghl_candidates(state)
    save_state(state)
    print(f"Found {new} new candidates. Total in pipeline: {len(state['contacts'])}")


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def cmd_status(state: dict):
    stats    = state["stats"]
    contacts = state["contacts"]

    active    = sum(1 for r in contacts.values() if not r.get("complete"))
    complete  = sum(1 for r in contacts.values() if r.get("complete"))
    replied   = sum(
        1 for r in contacts.values()
        for seq in r.get("sequences", {}).values()
        if seq.get("replied")
    )

    # Step breakdown
    step_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for rec in contacts.values():
        if rec.get("complete"):
            continue
        for seq in rec.get("sequences", {}).values():
            s = seq.get("step", 0)
            step_counts[s] = step_counts.get(s, 0) + 1

    print()
    print("=" * 50)
    print("  DM OUTREACH v2 — STATUS")
    print("=" * 50)
    print(f"  Total candidates tracked: {len(contacts)}")
    print(f"  Active in pipeline:       {active}")
    print(f"  Sequence complete:        {complete}")
    print(f"  Replies received:         {replied}")
    print(f"  Demos booked:             {stats.get('demos_booked', 0)}")
    print()
    print("  DMs sent")
    print(f"    DM 1:        {stats.get('dm1_sent', 0)}")
    print(f"    DM 2:        {stats.get('dm2_sent', 0)}")
    print(f"    DM 3:        {stats.get('dm3_sent', 0)}")
    print(f"    Instagram:   {stats.get('instagram_sent', 0)}")
    print(f"    Facebook:    {stats.get('facebook_sent', 0)}")
    print()
    print("  Pipeline by step (active only)")
    print(f"    Not started (step 0): {step_counts.get(0, 0)}")
    print(f"    DM 1 sent, waiting:   {step_counts.get(1, 0)}")
    print(f"    Ready for DM 2:       {step_counts.get(2, 0)}")
    print(f"    Ready for DM 3:       {step_counts.get(3, 0)}")
    print()
    last_run = state.get("last_run", "never")
    print(f"  Last generate run: {last_run}")
    print("=" * 50)
    print()


# ---------------------------------------------------------------------------
# Export — formatted copy-paste output for Wallace
# ---------------------------------------------------------------------------

def cmd_export(state: dict):
    today = datetime.now().strftime("%B %-d")  # e.g. "March 15"

    # Load today's list if it exists; otherwise generate it on the fly
    if os.path.exists(LIST_FILE):
        try:
            with open(LIST_FILE, "r") as f:
                dm_list = json.load(f)
        except Exception:
            dm_list = cmd_generate(state)
    else:
        dm_list = cmd_generate(state)

    output_lines = []

    for platform in ("instagram", "facebook"):
        items = dm_list.get(platform, [])
        if not items:
            continue

        label = "Instagram" if platform == "instagram" else "Facebook"
        output_lines.append(f"\n=== {label} DMs for {today} ===\n")

        for idx, item in enumerate(items, 1):
            handle  = item.get("handle") or item.get("company", "Unknown")
            step    = item.get("dm_step", 1)
            message = item.get("message", "")
            company = item.get("company", "")
            city    = item.get("city", "")
            industry= item.get("industry", "generic").upper()

            # Step label
            step_label = {
                1: "DM 1 — first touch",
                2: "DM 2 — follow-up (3d no response)",
                3: "DM 3 — final proof + demo line",
            }.get(step, f"DM {step}")

            handle_display = f"@{handle}" if platform == "instagram" else handle

            output_lines.append(f"{idx}. {handle_display} [{industry} | {city}]")
            output_lines.append(f"   {step_label}")
            output_lines.append(f'   "{message}"')
            output_lines.append("")

    if not output_lines:
        print("No DMs to send today. Run 'generate' first.")
        return

    # Print to stdout so Wallace can read it in terminal
    for line in output_lines:
        print(line)

    # Also log to activity
    total = sum(len(dm_list.get(p, [])) for p in ("instagram", "facebook"))
    ntfy(
        NTFY_ACTIVITY,
        "DM Export Printed",
        f"{total} DMs ready for today. Check terminal for copy-paste messages.",
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

USAGE = """
Usage: dm-outreach-v2.py <command> [args]

Commands:
  generate                          Scan GHL, advance sequences, write today's DM list
  log <id> <platform> <step> <status>
                                    Log a DM action
                                    platform: instagram|facebook
                                    step:     1|2|3
                                    status:   sent|replied|booked
  advance                           Advance contacts whose wait period has expired
  candidates                        Scan GHL for new DM candidates only
  status                            Show pipeline stats
  export                            Print formatted copy-paste DM list for today
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    state = load_state()
    cmd   = sys.argv[1].lower()

    if cmd == "generate":
        cmd_generate(state)

    elif cmd == "log":
        if len(sys.argv) < 6:
            print("Usage: dm-outreach-v2.py log <contact_id> <platform> <step> <status>")
            sys.exit(1)
        _, _, contact_id, platform, step, status = sys.argv[:6]
        cmd_log(state, contact_id, platform, step, status)

    elif cmd == "advance":
        cmd_advance(state)

    elif cmd == "candidates":
        cmd_candidates(state)

    elif cmd == "status":
        cmd_status(state)

    elif cmd == "export":
        cmd_export(state)

    else:
        print(f"Unknown command: {cmd}")
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
