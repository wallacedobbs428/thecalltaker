#!/usr/bin/env python3
"""
NTFY CALL LIST — Send updated call list to ntfy SALES topic.
Usage: python3 ops/ntfy-call-list.py
"""

import json
import os
import requests
from datetime import datetime

NTFY_SALES = "tct-sales-63uYsIT9"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "website", "closer-data.json")

def load_leads():
    with open(DATA_FILE) as f:
        return json.load(f)

def format_phone(phone):
    digits = phone.replace("+1", "").replace("+", "").replace("-", "").replace(" ", "")
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def build_message(data):
    leads = sorted(data.get("leads", []), key=lambda x: x.get("score", 0), reverse=True)
    stats = data.get("stats", {})
    today = datetime.now().strftime("%B %d, %Y")

    lines = [f"CALL LIST - {today}", f"{len(leads)} leads ranked by score. Call top to bottom.", ""]

    for i, lead in enumerate(leads, 1):
        lines.append(f"{i}. {lead['name']} - {lead['company']} ({lead.get('industry', 'general').title()})")
        lines.append(f"   Score: {lead.get('score', '?')}/10 | Touches: {lead.get('touches', '?')} | Last: {lead.get('lastTouch', 'N/A')}")
        lines.append(f"   Phone: {format_phone(lead['phone'])}")
        lines.append(f"   Why: {lead.get('reason', '')}")
        lines.append("")

    lines.append(f"Pipeline: {stats.get('inSequence', 0)} in sequence | {stats.get('textsSent', 0)} texts sent | ${stats.get('mrr', 0)} MRR")
    return "\n".join(lines)

def send():
    data = load_leads()
    leads = data.get("leads", [])
    body = build_message(data)

    resp = requests.post(
        f"https://ntfy.sh/{NTFY_SALES}",
        data=body.encode("utf-8"),
        headers={
            "Title": f"[CALL LIST] Updated Call List - {len(leads)} Leads",
            "Priority": "high",
            "Tags": "phone,clipboard",
        },
        timeout=10,
    )
    if resp.ok:
        print(f"Sent call list ({len(leads)} leads) to ntfy SALES")
    else:
        print(f"Failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    send()
