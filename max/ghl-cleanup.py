#!/usr/bin/env python3
"""
GHL Contact Cleanup — The Call Taker
Pulls all contacts from GHL, identifies duplicates, dead leads, and untagged contacts.
Report only — does NOT delete anything.

Usage:
  python3 ghl-cleanup.py scan     # Full scan + report
  python3 ghl-cleanup.py status   # Show last scan results
"""

import json
import sys
import os
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from collections import defaultdict

# ===================================================
# CONFIG
# ===================================================

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "ghl-cleanup-state.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "ghl-cleanup.log")

# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] CLEANUP: {msg}"
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
        "User-Agent": "GHLCleanup/1.0 TheCallTaker",
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
# FETCH ALL CONTACTS
# ===================================================

def get_all_contacts():
    """Fetch all contacts from GHL with pagination."""
    contacts = []
    page = 1
    while True:
        log(f"Fetching page {page}...")
        resp = ghl_request("GET", f"/contacts/?locationId={GHL_LOCATION_ID}&limit=100&page={page}")
        if not resp or "contacts" not in resp:
            log(f"No response on page {page}, stopping.")
            break
        batch = resp["contacts"]
        if not batch:
            break
        contacts.extend(batch)
        log(f"  Got {len(batch)} contacts (total: {len(contacts)})")
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.5)  # Rate limiting
    return contacts


# ===================================================
# ANALYSIS
# ===================================================

def analyze_contacts(contacts):
    """Analyze contacts for duplicates, dead leads, and untagged."""

    # --- Duplicates by phone ---
    phone_map = defaultdict(list)
    for c in contacts:
        phone = (c.get("phone") or "").strip()
        if phone and len(phone) >= 7:
            # Normalize: strip spaces, dashes, parens
            normalized = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
            # Take last 10 digits
            if len(normalized) >= 10:
                normalized = normalized[-10:]
            phone_map[normalized].append({
                "id": c.get("id"),
                "name": f"{c.get('firstName', '')} {c.get('lastName', '')}".strip(),
                "company": c.get("companyName", ""),
                "phone": phone,
                "email": c.get("email", ""),
                "tags": c.get("tags", []),
            })

    phone_dupes = {k: v for k, v in phone_map.items() if len(v) > 1}

    # --- Duplicates by business name ---
    biz_map = defaultdict(list)
    for c in contacts:
        biz = (c.get("companyName") or "").strip().lower()
        if biz and len(biz) > 2:
            biz_map[biz].append({
                "id": c.get("id"),
                "name": f"{c.get('firstName', '')} {c.get('lastName', '')}".strip(),
                "company": c.get("companyName", ""),
                "phone": c.get("phone", ""),
                "email": c.get("email", ""),
                "tags": c.get("tags", []),
            })

    biz_dupes = {k: v for k, v in biz_map.items() if len(v) > 1}

    # --- Dead contacts (no phone AND no email) ---
    dead = []
    for c in contacts:
        phone = (c.get("phone") or "").strip()
        email = (c.get("email") or "").strip()
        if not phone and not email:
            dead.append({
                "id": c.get("id"),
                "name": f"{c.get('firstName', '')} {c.get('lastName', '')}".strip(),
                "company": c.get("companyName", ""),
                "tags": c.get("tags", []),
                "created": c.get("dateAdded", c.get("createdAt", "")),
            })

    # --- Untagged contacts (zero tags) ---
    untagged = []
    for c in contacts:
        tags = c.get("tags", [])
        if not tags or len(tags) == 0:
            phone = (c.get("phone") or "").strip()
            email = (c.get("email") or "").strip()
            untagged.append({
                "id": c.get("id"),
                "name": f"{c.get('firstName', '')} {c.get('lastName', '')}".strip(),
                "company": c.get("companyName", ""),
                "phone": phone,
                "email": email,
                "created": c.get("dateAdded", c.get("createdAt", "")),
            })

    # --- Collect all duplicate contact IDs (for total unique dupe count) ---
    dupe_ids = set()
    for group in phone_dupes.values():
        for c in group:
            dupe_ids.add(c["id"])
    for group in biz_dupes.values():
        for c in group:
            dupe_ids.add(c["id"])

    return {
        "phone_dupes": phone_dupes,
        "biz_dupes": biz_dupes,
        "dead": dead,
        "untagged": untagged,
        "dupe_ids": list(dupe_ids),
    }


# ===================================================
# REPORT
# ===================================================

def print_report(total, results):
    phone_dupes = results["phone_dupes"]
    biz_dupes = results["biz_dupes"]
    dead = results["dead"]
    untagged = results["untagged"]

    print("\n" + "=" * 60)
    print("  GHL CONTACT CLEANUP REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    print(f"\n  Total contacts pulled: {total}")
    print(f"  Phone duplicates:      {len(phone_dupes)} groups ({sum(len(v) for v in phone_dupes.values())} contacts)")
    print(f"  Business name dupes:   {len(biz_dupes)} groups ({sum(len(v) for v in biz_dupes.values())} contacts)")
    print(f"  Dead contacts:         {len(dead)} (no phone, no email)")
    print(f"  Untagged contacts:     {len(untagged)} (zero tags)")
    print(f"  Total flagged IDs:     {len(results['dupe_ids'])} unique duplicates")

    # Show top phone dupes
    if phone_dupes:
        print(f"\n--- TOP PHONE DUPLICATES (showing up to 10) ---")
        for i, (phone, group) in enumerate(sorted(phone_dupes.items(), key=lambda x: -len(x[1]))):
            if i >= 10:
                break
            print(f"\n  Phone: ...{phone[-4:]}")
            for c in group:
                tags_str = ", ".join(c["tags"][:3]) if c["tags"] else "NO TAGS"
                print(f"    - {c['name'] or '(no name)'} | {c['company'] or '(no company)'} | {tags_str}")

    # Show top biz dupes
    if biz_dupes:
        print(f"\n--- TOP BUSINESS NAME DUPLICATES (showing up to 10) ---")
        for i, (biz, group) in enumerate(sorted(biz_dupes.items(), key=lambda x: -len(x[1]))):
            if i >= 10:
                break
            print(f"\n  Business: {biz}")
            for c in group:
                print(f"    - {c['name'] or '(no name)'} | {c['phone'] or 'no phone'} | {c['email'] or 'no email'}")

    # Show dead contacts sample
    if dead:
        print(f"\n--- DEAD CONTACTS (no phone, no email — showing up to 10) ---")
        for c in dead[:10]:
            print(f"  - {c['name'] or '(no name)'} | {c['company'] or '(no company)'} | tags: {len(c['tags'])}")

    # Show untagged sample
    if untagged:
        print(f"\n--- UNTAGGED CONTACTS (showing up to 10) ---")
        for c in untagged[:10]:
            print(f"  - {c['name'] or '(no name)'} | {c['company'] or '(no company)'} | {c['phone'] or 'no phone'}")

    print("\n" + "=" * 60)
    print("  ACTION: Report only — nothing was deleted or modified.")
    print("=" * 60 + "\n")


# ===================================================
# COMMANDS
# ===================================================

def cmd_scan():
    """Full scan: pull all contacts, analyze, report, save state."""
    log("Starting full GHL contact scan...")
    contacts = get_all_contacts()
    total = len(contacts)
    log(f"Pulled {total} contacts total.")

    if total == 0:
        log("No contacts found. Check API key / location ID.")
        return

    results = analyze_contacts(contacts)

    # Print report
    print_report(total, results)

    # Save state (without full contact data — just counts + flagged IDs)
    state = {
        "last_scan": datetime.now().isoformat(),
        "total_contacts": total,
        "phone_dupe_groups": len(results["phone_dupes"]),
        "phone_dupe_contacts": sum(len(v) for v in results["phone_dupes"].values()),
        "biz_dupe_groups": len(results["biz_dupes"]),
        "biz_dupe_contacts": sum(len(v) for v in results["biz_dupes"].values()),
        "dead_contacts": len(results["dead"]),
        "untagged_contacts": len(results["untagged"]),
        "total_flagged_dupe_ids": len(results["dupe_ids"]),
        "dead_ids": [c["id"] for c in results["dead"]],
        "untagged_ids": [c["id"] for c in results["untagged"]],
        "dupe_ids": results["dupe_ids"],
    }
    save_state(state)
    log("State saved. Report complete.")


def cmd_status():
    """Show last scan results."""
    state = load_state()
    if not state:
        print("No scan data. Run: python3 ghl-cleanup.py scan")
        return

    print(f"\nLast scan: {state.get('last_scan', 'unknown')}")
    print(f"Total contacts:        {state.get('total_contacts', 0)}")
    print(f"Phone dupe groups:     {state.get('phone_dupe_groups', 0)} ({state.get('phone_dupe_contacts', 0)} contacts)")
    print(f"Business dupe groups:  {state.get('biz_dupe_groups', 0)} ({state.get('biz_dupe_contacts', 0)} contacts)")
    print(f"Dead contacts:         {state.get('dead_contacts', 0)}")
    print(f"Untagged contacts:     {state.get('untagged_contacts', 0)}")
    print(f"Total flagged dupes:   {state.get('total_flagged_dupe_ids', 0)}")


# ===================================================
# MAIN
# ===================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ghl-cleanup.py [scan|status]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "scan":
        cmd_scan()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 ghl-cleanup.py [scan|status]")
        sys.exit(1)
