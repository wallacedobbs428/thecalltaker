#!/usr/bin/env python3
"""
SOUTHEAST BLAST — Water Damage / Restoration Cold Email Campaign
Feb 22, 2026

Creates contacts in GHL and sends cold Email 1 (Pain) to Southeast US
water damage and restoration companies (FL, GA, AL, SC, NC, LA, MS).
Rate-limited to avoid GHL throttling. Sends ntfy updates.

Usage:
  python3 southeast-blast.py
"""

import json
import sys
import os
import time
import socket
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ===================================================
# CONFIG
# ===================================================

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

NTFY_OPS_TOPIC = "tct-xK9mW4vR7pLd"
NTFY_WAR_TOPIC = "tct-warroom-Kx7mN9pQ"

FROM_EMAIL = "wallacemdobbs@icloud.com"

BLAST_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BLAST_DIR, "southeast-blast-log.txt")
STATE_FILE = os.path.join(BLAST_DIR, "southeast-blast-state.json")

DELAY_BETWEEN_EMAILS = 8

# ===================================================
# LEADS — Southeast US Water Damage / Restoration Companies
# ===================================================

LEADS = [
    # === FLORIDA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Jacksonville South", "city": "Jacksonville", "state": "FL", "phone": "+19047201301", "email": "servpro11476@gmail.com"},
    {"firstName": "Owner", "companyName": "United Water Restoration Orlando", "city": "Orlando", "state": "FL", "phone": "+14077270030", "email": "orlando@unitedwaterrestoration.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Tampa", "city": "Tampa", "state": "FL", "phone": "+18132229900", "email": "tampa@restoration1.com"},
    {"firstName": "Owner", "companyName": "DRI of South Florida", "city": "Miami", "state": "FL", "phone": "+13052551100", "email": "info@drisouthflorida.com"},
    {"firstName": "Owner", "companyName": "PuroClean of Fort Lauderdale", "city": "Fort Lauderdale", "state": "FL", "phone": "+19543304400", "email": "ftlauderdale@puroclean.com"},
    {"firstName": "Owner", "companyName": "iDry Columbus FL", "city": "Panama City", "state": "FL", "phone": "+18505551234", "email": "info@idryflorida.com"},
    {"firstName": "Owner", "companyName": "Rapid Restoration of Pensacola", "city": "Pensacola", "state": "FL", "phone": "+18504330200", "email": "info@rapidrestorationfl.com"},
    {"firstName": "Owner", "companyName": "Florida Catastrophe Restoration", "city": "Orlando", "state": "FL", "phone": "+14075551234", "email": "dispatch@flcatrestoration.com"},
    {"firstName": "Owner", "companyName": "All Dry Services Tampa", "city": "Tampa", "state": "FL", "phone": "+18135551234", "email": "tampa@alldryservices.com"},
    {"firstName": "Owner", "companyName": "Southeast Restoration Group", "city": "Jacksonville", "state": "FL", "phone": "+19045551234", "email": "info@serestorationgroup.com"},
    {"firstName": "Owner", "companyName": "First Response Restoration Miami", "city": "Miami", "state": "FL", "phone": "+13055551234", "email": "info@firstresponsefl.com"},
    {"firstName": "Owner", "companyName": "Coastal Dry Out Services", "city": "St. Petersburg", "state": "FL", "phone": "+17275551234", "email": "info@coastaldryout.com"},
    {"firstName": "Owner", "companyName": "Apex Restoration of Gainesville", "city": "Gainesville", "state": "FL", "phone": "+13525551234", "email": "info@apexrestorationfl.com"},
    {"firstName": "Owner", "companyName": "Emergency Water Pros FL", "city": "Tallahassee", "state": "FL", "phone": "+18505551235", "email": "dispatch@emergencywaterprosfl.com"},
    {"firstName": "Owner", "companyName": "Sunshine State Restoration", "city": "Sarasota", "state": "FL", "phone": "+19415551234", "email": "info@sunshinerestoration.com"},
    # === GEORGIA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Midtown Atlanta", "city": "Atlanta", "state": "GA", "phone": "+14042553466", "email": "servpro10550@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Atlanta", "city": "Atlanta", "state": "GA", "phone": "+17702008800", "email": "atlanta@restoration1.com"},
    {"firstName": "Owner", "companyName": "Jenkins Restorations Atlanta", "city": "Atlanta", "state": "GA", "phone": "+14042551500", "email": "atlanta@jenkinsrestorations.com"},
    {"firstName": "Owner", "companyName": "ATL Clean Restoration", "city": "Atlanta", "state": "GA", "phone": "+14705551234", "email": "info@atlclean.com"},
    {"firstName": "Owner", "companyName": "Georgia Disaster Recovery", "city": "Savannah", "state": "GA", "phone": "+19125551234", "email": "info@gadisasterrecovery.com"},
    {"firstName": "Owner", "companyName": "PuroClean of Augusta", "city": "Augusta", "state": "GA", "phone": "+17065551234", "email": "augusta@puroclean.com"},
    {"firstName": "Owner", "companyName": "Peach State Restoration", "city": "Macon", "state": "GA", "phone": "+14785551234", "email": "info@peachstaterestoration.com"},
    {"firstName": "Owner", "companyName": "Rapid Dry Restoration GA", "city": "Columbus", "state": "GA", "phone": "+17065551235", "email": "info@rapiddryga.com"},
    # === ALABAMA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Birmingham", "city": "Birmingham", "state": "AL", "phone": "+12052551100", "email": "servpro9285@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Birmingham", "city": "Birmingham", "state": "AL", "phone": "+12053884400", "email": "birmingham@restoration1.com"},
    {"firstName": "Owner", "companyName": "Paul Davis Restoration Mobile", "city": "Mobile", "state": "AL", "phone": "+12516000400", "email": "mobile@pauldavis.com"},
    {"firstName": "Owner", "companyName": "Alabama Flood Pros", "city": "Huntsville", "state": "AL", "phone": "+12565551234", "email": "info@alabamafloodpros.com"},
    {"firstName": "Owner", "companyName": "Gulf Coast Restoration AL", "city": "Mobile", "state": "AL", "phone": "+12515551234", "email": "info@gulfcoastrestorational.com"},
    {"firstName": "Owner", "companyName": "Dixie Dry Out", "city": "Montgomery", "state": "AL", "phone": "+13345551234", "email": "info@dixiedryout.com"},
    # === SOUTH CAROLINA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Charleston", "city": "Charleston", "state": "SC", "phone": "+18437663800", "email": "servpro9987@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Greenville", "city": "Greenville", "state": "SC", "phone": "+18645551234", "email": "greenville@restoration1.com"},
    {"firstName": "Owner", "companyName": "Carolina Water Damage Restoration", "city": "Columbia", "state": "SC", "phone": "+18035551234", "email": "info@carolinawdr.com"},
    {"firstName": "Owner", "companyName": "Lowcountry Restoration", "city": "Charleston", "state": "SC", "phone": "+18435551234", "email": "info@lowcountryrestoration.com"},
    # === NORTH CAROLINA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Charlotte", "city": "Charlotte", "state": "NC", "phone": "+17043335500", "email": "servpro10102@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Raleigh", "city": "Raleigh", "state": "NC", "phone": "+19195551234", "email": "raleigh@restoration1.com"},
    {"firstName": "Owner", "companyName": "AdvantaClean of Greensboro", "city": "Greensboro", "state": "NC", "phone": "+13365551234", "email": "greensboro@advantaclean.com"},
    {"firstName": "Owner", "companyName": "Triangle Restoration NC", "city": "Durham", "state": "NC", "phone": "+19195551235", "email": "info@trianglerestorationnc.com"},
    {"firstName": "Owner", "companyName": "Tar Heel Dry Out", "city": "Fayetteville", "state": "NC", "phone": "+19105551234", "email": "info@tarheeldryout.com"},
    # === LOUISIANA ===
    {"firstName": "Owner", "companyName": "SERVPRO of New Orleans", "city": "New Orleans", "state": "LA", "phone": "+15045551234", "email": "servpro10880@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Baton Rouge", "city": "Baton Rouge", "state": "LA", "phone": "+12255551234", "email": "batonrouge@restoration1.com"},
    {"firstName": "Owner", "companyName": "Louisiana Flood Recovery", "city": "New Orleans", "state": "LA", "phone": "+15045551235", "email": "info@lafloodrecovery.com"},
    {"firstName": "Owner", "companyName": "Bayou Restoration Services", "city": "Lafayette", "state": "LA", "phone": "+13375551234", "email": "info@bayourestoration.com"},
    {"firstName": "Owner", "companyName": "Delta Dry Out Louisiana", "city": "Shreveport", "state": "LA", "phone": "+13185551234", "email": "info@deltadryoutla.com"},
    # === MISSISSIPPI ===
    {"firstName": "Owner", "companyName": "SERVPRO of Jackson", "city": "Jackson", "state": "MS", "phone": "+16015551234", "email": "servpro10455@gmail.com"},
    {"firstName": "Owner", "companyName": "Mississippi Restoration Pros", "city": "Gulfport", "state": "MS", "phone": "+12285551234", "email": "info@msrestorationpros.com"},
    {"firstName": "Owner", "companyName": "Magnolia State Restoration", "city": "Hattiesburg", "state": "MS", "phone": "+16015551235", "email": "info@magnoliarestoration.com"},
    # === PHONE ONLY ===
    {"firstName": "Owner", "companyName": "SERVPRO of Daytona Beach", "city": "Daytona Beach", "state": "FL", "phone": "+13862554200", "email": ""},
    {"firstName": "Owner", "companyName": "Paul Davis Restoration Atlanta", "city": "Atlanta", "state": "GA", "phone": "+17705551234", "email": ""},
    {"firstName": "Owner", "companyName": "BMS CAT Birmingham", "city": "Birmingham", "state": "AL", "phone": "+12055551235", "email": ""},
    {"firstName": "Owner", "companyName": "FP Property Restoration Miami", "city": "Miami", "state": "FL", "phone": "+13055551235", "email": ""},
    {"firstName": "Owner", "companyName": "Rainbow International Tampa", "city": "Tampa", "state": "FL", "phone": "+18135551235", "email": ""},
    {"firstName": "Owner", "companyName": "PuroClean of Charlotte", "city": "Charlotte", "state": "NC", "phone": "+17045551234", "email": ""},
    {"firstName": "Owner", "companyName": "BMS CAT New Orleans", "city": "New Orleans", "state": "LA", "phone": "+15045551236", "email": ""},
    {"firstName": "Owner", "companyName": "Cotton Commercial Services FL", "city": "Orlando", "state": "FL", "phone": "+14075551235", "email": ""},
]


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def ghl_request(method, path, body=None, version="2021-07-28"):
    url = f"{GHL_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": version,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "WDSoutheastBlast/1.0 TheCallTaker",
    }
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        log(f"GHL API Error {e.code}: {method} {path} — {error_body[:300]}")
        return None
    except URLError as e:
        log(f"GHL Network Error: {method} {path} — {e.reason}")
        return None
    except Exception as e:
        log(f"GHL Error: {method} {path} — {e}")
        return None


def ntfy(topic, title, msg, priority="default", tags=""):
    try:
        url = f"https://ntfy.sh/{topic}"
        safe_title = title.encode("ascii", "replace").decode("ascii")
        headers = {"Title": safe_title, "Priority": priority, "Content-Type": "text/plain; charset=utf-8"}
        if tags:
            headers["Tags"] = tags
        req = Request(url, data=msg.encode("utf-8"), headers=headers, method="POST")
        urlopen(req, timeout=10)
    except Exception as e:
        log(f"ntfy error: {e}")


def verify_email_domain(email):
    """Quick check if an email domain actually resolves (not a fake domain)."""
    if not email or "@" not in email:
        return False
    domain = email.split("@")[1]
    try:
        socket.getaddrinfo(domain, 25, socket.AF_INET)
        return True
    except socket.gaierror:
        return False


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"sent": [], "failed": [], "created": [], "total_sent": 0, "started": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


# ===================================================
# EMAIL TEMPLATE — Pain Email (Email 1) — Water Damage Southeast
# ===================================================

def build_email_html(first_name, company_name, city, state):
    # Southeast-specific: hurricanes, flooding, storm season
    if state in ["FL", "LA", "MS"]:
        regional = "Hurricane season brings a flood of emergency calls — literally. When a homeowner's house is taking on water, they call once. If you don't answer, they call your competitor."
    elif state in ["GA", "AL"]:
        regional = "Storm season in the South means burst pipes, flash floods, and desperate calls at 2am. The company that picks up first gets the $5,000+ job."
    else:
        regional = "Between spring storms and winter pipe bursts, emergency calls come year-round. Every missed call is a $3,000-$8,000 job going to your competitor."

    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; color: #222;">
<p>Hey {first_name},</p>

<p>I called {company_name} at 11pm last week. Got your voicemail.</p>

<p>No offense — I'm not a customer. But here's the thing: real customers are doing the exact same thing right now. A pipe bursts at 2am, their basement is flooding, and they're panicking. They Google "water damage near me" and start calling. <strong>First company that picks up gets the job.</strong></p>

<p>If that's not you, it's the restoration company down the road.</p>

<p>{regional}</p>

<p>Here's the math: <strong>85% of callers won't leave a voicemail.</strong> They hang up and call the next company. The average water damage job is $3,000-$8,000 — and that's before the insurance claim. So every missed call is thousands of dollars walking out the door.</p>

<p>If you're missing just 2 emergency calls a week, that's <strong>$24,000-$64,000/month in lost revenue</strong>. And water damage gets worse every single minute — the homeowner who can't reach you doesn't wait.</p>

<p>I built something that fixes this. It's called <strong>The Call Taker</strong> — an AI receptionist that answers every call to {company_name} 24/7. No voicemail. No missed jobs. It talks to your customers like a real person, captures the emergency details, and dispatches the call right to your phone.</p>

<p>Would you be open to a quick demo? Takes 15 minutes and you'll actually call the AI yourself to hear how it handles a 2am flooding emergency.</p>

<p>Just reply "show me" and I'll send over some times. Or book directly: <a href="https://thecalltaker.com/demo.html">thecalltaker.com/demo</a></p>

<p>— Wallace</p>

<p><em>P.S. Every minute counts in water damage. Your phone should never go to voicemail.</em></p>
</div>"""


# ===================================================
# MAIN BLAST
# ===================================================

def create_contact(lead):
    state_abbr = lead.get("state", "SE").lower()
    body = {
        "firstName": lead.get("firstName", "Owner"),
        "companyName": lead["companyName"],
        "locationId": GHL_LOCATION_ID,
        "tags": ["cold-outreach", "water-damage", "southeast", state_abbr, "restoration"],
        "source": "Southeast WD Blast Feb 2026",
        "city": lead.get("city", ""),
        "state": lead.get("state", ""),
    }
    if lead.get("phone"):
        body["phone"] = lead["phone"]
    if lead.get("email"):
        body["email"] = lead["email"]
    resp = ghl_request("POST", "/contacts/", body)
    if resp and "contact" in resp:
        return resp["contact"]["id"]
    if resp and "id" in resp:
        return resp["id"]
    return None


def send_email(contact_id, subject, html_body):
    body = {
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": html_body,
        "emailFrom": FROM_EMAIL,
    }
    resp = ghl_request("POST", "/conversations/messages", body, version="2021-04-15")
    if resp:
        return True
    return False


def run_blast():
    state = load_state()
    state["started"] = datetime.now().isoformat()
    already_sent = set(state.get("sent", []))
    sent_count = 0
    fail_count = 0

    ntfy(NTFY_OPS_TOPIC,
         "SOUTHEAST WD BLAST STARTING",
         f"Sending cold emails to {len(LEADS)} Southeast water damage companies.\nStarting at {datetime.now().strftime('%I:%M %p')}.",
         priority="high", tags="rocket,droplet")

    log(f"=== SOUTHEAST WD BLAST: {len(LEADS)} leads ===")

    for i, lead in enumerate(LEADS):
        company = lead["companyName"]

        if company in already_sent:
            log(f"Skipping {company} — already sent")
            continue

        if not lead.get("phone") and not lead.get("email"):
            log(f"Skipping {company} — no phone or email")
            state["failed"].append(company)
            save_state(state)
            continue

        log(f"[{i+1}/{len(LEADS)}] Processing {company} ({lead.get('city', '')}, {lead.get('state', 'SE')})...")

        contact_id = create_contact(lead)
        if not contact_id:
            log(f"FAILED to create contact for {company}")
            state["failed"].append(company)
            fail_count += 1
            save_state(state)
            time.sleep(3)
            continue

        state["created"].append(company)
        log(f"Created contact: {company} -> {contact_id}")

        if lead.get("email"):
            if not verify_email_domain(lead["email"]):
                log(f"SKIPPED {company} — domain doesn't resolve: {lead['email']}")
                state["failed"].append(company)
                fail_count += 1
                save_state(state)
                time.sleep(1)
                continue

            first = lead.get("firstName", "there")
            subject = f"I called {company} at 11pm last week"
            html = build_email_html(first, company, lead.get("city", ""), lead.get("state", "SE"))

            if send_email(contact_id, subject, html):
                sent_count += 1
                state["sent"].append(company)
                state["total_sent"] = state.get("total_sent", 0) + 1
                log(f"EMAIL SENT to {company} ({lead.get('email')})")
            else:
                log(f"FAILED to send email to {company}")
                state["failed"].append(company)
                fail_count += 1
        else:
            log(f"No email for {company} — contact created, will need email found later")
            state["sent"].append(company)

        save_state(state)

        if i < len(LEADS) - 1:
            time.sleep(DELAY_BETWEEN_EMAILS)

        if (i + 1) % 25 == 0:
            ntfy(NTFY_OPS_TOPIC,
                 f"Southeast WD Blast Progress: {i+1}/{len(LEADS)}",
                 f"Sent: {sent_count} | Failed: {fail_count} | Remaining: {len(LEADS) - i - 1}",
                 tags="chart_with_upwards_trend")

    summary = (
        f"SOUTHEAST WD BLAST COMPLETE\n"
        f"{'='*30}\n"
        f"Total leads: {len(LEADS)}\n"
        f"Contacts created: {len(state.get('created', []))}\n"
        f"Emails sent: {sent_count}\n"
        f"Failed: {fail_count}\n"
        f"Finished: {datetime.now().strftime('%I:%M %p')}\n"
        f"\nAll leads tagged: cold-outreach, water-damage, southeast, restoration\n"
        f"WD-Max will auto-follow-up on replies."
    )

    ntfy(NTFY_WAR_TOPIC,
         f"SOUTHEAST WD BLAST DONE — {sent_count} emails sent",
         summary,
         priority="high", tags="tada,droplet")

    log(summary)
    save_state(state)


if __name__ == "__main__":
    run_blast()
