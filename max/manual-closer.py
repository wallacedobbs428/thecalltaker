#!/usr/bin/env python3
"""
MANUAL CLOSER — Top 30 Hottest Leads to Text Right Now
Mar 12, 2026

Pulls all contacts from GHL, scores them by engagement signals,
and outputs the 30 hottest leads with phone numbers and personalized
text messages ready to copy-paste.

Usage:
  python3 manual-closer.py
"""

import json
import os
import sys
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ===================================================
# CONFIG
# ===================================================

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

DEMO_LINE = "(615) 784-5747"

# Tags that disqualify
SKIP_TAGS = {"customer", "pilot-active", "active-client", "dnc",
             "opted-out", "do-not-contact", "suppressed", "test-lead"}

# Scoring weights — higher = hotter
TAG_SCORES = {
    "hot-lead": 25,
    "bland-interested": 25,
    "warm-demo-prospect": 20,
    "demo-called": 20,
    "replied": 18,
    "revenue-signal": 15,
    "funnel-active": 12,
    "demo-followup-queue": 12,
    "score-70": 10,
    "score-65": 8,
    "score-59": 6,
    "score-50": 4,
    "closer-stage-1": 10,
    "pilot-candidate": 10,
    "agency-hot": 15,
    "apollo-hot": 12,
    "sms-followup-sent": 5,
    "cold-call-priority": 8,
    "has-email": 2,
    "bland-called": 3,
    "bland-campaign-called": 2,
}

# ===================================================
# HELPERS
# ===================================================

def ghl_request(method, path):
    url = f"{GHL_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "ManualCloser/1.0 TheCallTaker",
    }
    req = Request(url, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  API Error: {e}")
        return None


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


def score_contact(contact):
    tags = {t.lower() for t in contact.get("tags", [])}
    if tags & SKIP_TAGS:
        return -1
    phone = contact.get("phone", "")
    if not phone or len(phone) < 10:
        return -1
    score = 0
    matched = []
    for tag, points in TAG_SCORES.items():
        if tag in tags:
            score += points
            matched.append(tag)
    return score


def get_industry(contact):
    tags = {t.lower() for t in contact.get("tags", [])}
    industries = ["hvac", "plumbing", "roofing", "electrical", "dental",
                  "medspa", "legal", "locksmith", "towing", "veterinary",
                  "garage-door", "funeral", "property-management",
                  "restoration", "water-damage"]
    for ind in industries:
        if ind in tags:
            return ind
    return ""


def build_text(contact):
    first = contact.get("firstName", contact.get("contactName", ""))
    if not first or first.startswith("(") or first == "Owner":
        first = "there"
    company = contact.get("companyName", "")

    if company:
        return (f"Hey {first}, this is Wallace from The Call Taker. "
                f"I noticed {company} could be losing calls after hours — "
                f"we built an AI that answers every call 24/7, books the job, "
                f"and texts you the details. Want to hear it? Call {DEMO_LINE} right now.")
    else:
        return (f"Hey {first}, this is Wallace from The Call Taker. "
                f"We built an AI receptionist that answers every call 24/7 "
                f"for service businesses — books jobs, texts you details. "
                f"Hear it live: {DEMO_LINE}")


# ===================================================
# MAIN
# ===================================================

if __name__ == "__main__":
    print("Pulling contacts from GHL...", flush=True)
    all_contacts = get_all_contacts()
    print(f"Total contacts: {len(all_contacts)}")

    # Score everyone
    scored = []
    for c in all_contacts:
        s = score_contact(c)
        if s > 0:
            scored.append((s, c))

    # Sort by score descending
    scored.sort(key=lambda x: -x[0])

    # Take top 30
    top30 = scored[:30]

    print()
    print("=" * 70)
    print(f"  TOP 30 LEADS TO TEXT RIGHT NOW — {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
    print("=" * 70)
    print()

    for i, (score, contact) in enumerate(top30):
        name = contact.get("contactName", contact.get("firstName", "?"))
        company = contact.get("companyName", "") or ""
        phone = contact.get("phone", "")
        industry = get_industry(contact)
        tags = contact.get("tags", [])
        hot_tags = [t for t in tags if t.lower() in TAG_SCORES]

        print(f"  #{i+1}  SCORE: {score}")
        print(f"  Name:     {name}")
        if company:
            print(f"  Company:  {company}")
        if industry:
            print(f"  Industry: {industry}")
        print(f"  Phone:    {phone}")
        print(f"  Signals:  {', '.join(hot_tags)}")
        print(f"  ---")
        print(f"  TEXT:")
        print(f"  {build_text(contact)}")
        print()
        print("-" * 70)
        print()

    print(f"  Total scored leads: {len(scored)}")
    print(f"  Showing top 30 of {len(scored)}")
    print()
