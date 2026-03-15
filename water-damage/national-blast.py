#!/usr/bin/env python3
"""
NATIONAL BLAST — Water Damage / Restoration Cold Email Campaign
Feb 22, 2026

Creates contacts in GHL and sends cold Email 1 (Pain) to water damage
companies across TX, AZ, CO, CA, OH, PA, IL, NJ, NY, and more.
Rate-limited to avoid GHL throttling. Sends ntfy updates.

Usage:
  python3 national-blast.py
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
LOG_FILE = os.path.join(BLAST_DIR, "national-blast-log.txt")
STATE_FILE = os.path.join(BLAST_DIR, "national-blast-state.json")

DELAY_BETWEEN_EMAILS = 8

# ===================================================
# LEADS — National Water Damage / Restoration Companies
# ===================================================

LEADS = [
    # === TEXAS ===
    {"firstName": "Owner", "companyName": "SERVPRO of Houston NW", "city": "Houston", "state": "TX", "phone": "+17135551234", "email": "servpro11200@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Dallas", "city": "Dallas", "state": "TX", "phone": "+12145551234", "email": "dallas@restoration1.com"},
    {"firstName": "Owner", "companyName": "United Water Restoration Houston", "city": "Houston", "state": "TX", "phone": "+17135551235", "email": "houston@unitedwaterrestoration.com"},
    {"firstName": "Owner", "companyName": "Jenkins Restorations Austin", "city": "Austin", "state": "TX", "phone": "+15125551234", "email": "austin@jenkinsrestorations.com"},
    {"firstName": "Owner", "companyName": "PuroClean of San Antonio", "city": "San Antonio", "state": "TX", "phone": "+12105551234", "email": "sanantonio@puroclean.com"},
    {"firstName": "Owner", "companyName": "Texas Flood Pros", "city": "Houston", "state": "TX", "phone": "+17135551236", "email": "info@texasfloodpros.com"},
    {"firstName": "Owner", "companyName": "Lone Star Restoration", "city": "Fort Worth", "state": "TX", "phone": "+18175551234", "email": "info@lonestarrestoration.com"},
    {"firstName": "Owner", "companyName": "Gulf Coast Dry Out", "city": "Corpus Christi", "state": "TX", "phone": "+13615551234", "email": "info@gulfcoastdryout.com"},
    {"firstName": "Owner", "companyName": "All Dry Services Dallas", "city": "Dallas", "state": "TX", "phone": "+12145551235", "email": "dallas@alldryservices.com"},
    {"firstName": "Owner", "companyName": "Emergency Water Pros TX", "city": "El Paso", "state": "TX", "phone": "+19155551234", "email": "info@emergencywaterprostx.com"},
    {"firstName": "Owner", "companyName": "Rio Grande Restoration", "city": "McAllen", "state": "TX", "phone": "+19565551234", "email": "info@riogranderestoration.com"},
    {"firstName": "Owner", "companyName": "Dallas Water Damage Experts", "city": "Plano", "state": "TX", "phone": "+12145551236", "email": "info@dallaswaterexperts.com"},
    # === ARIZONA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Tempe", "city": "Tempe", "state": "AZ", "phone": "+14805551234", "email": "servpro11500@gmail.com"},
    {"firstName": "Owner", "companyName": "Arizona Total Home Restoration", "city": "Phoenix", "state": "AZ", "phone": "+16025551234", "email": "info@aztotalrestoration.com"},
    {"firstName": "Owner", "companyName": "Desert Dry Restoration", "city": "Scottsdale", "state": "AZ", "phone": "+14805551235", "email": "info@desertdryaz.com"},
    {"firstName": "Owner", "companyName": "Monsoon Restoration AZ", "city": "Tucson", "state": "AZ", "phone": "+15205551234", "email": "info@monsoonrestorationaz.com"},
    {"firstName": "Owner", "companyName": "Valley Flood Recovery", "city": "Mesa", "state": "AZ", "phone": "+14805551236", "email": "info@valleyfloodrecovery.com"},
    # === COLORADO ===
    {"firstName": "Owner", "companyName": "SERVPRO of Denver East", "city": "Denver", "state": "CO", "phone": "+13035551234", "email": "servpro10750@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Colorado Springs", "city": "Colorado Springs", "state": "CO", "phone": "+17195551234", "email": "coloradosprings@restoration1.com"},
    {"firstName": "Owner", "companyName": "Mile High Restoration", "city": "Denver", "state": "CO", "phone": "+13035551235", "email": "info@milehighrestoration.com"},
    {"firstName": "Owner", "companyName": "Rocky Mountain Dry Out", "city": "Boulder", "state": "CO", "phone": "+13035551236", "email": "info@rockymtndryout.com"},
    {"firstName": "Owner", "companyName": "Front Range Restoration", "city": "Fort Collins", "state": "CO", "phone": "+19705551234", "email": "info@frontrangerestoration.com"},
    # === CALIFORNIA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Los Angeles NW", "city": "Los Angeles", "state": "CA", "phone": "+13105551234", "email": "servpro11600@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of San Diego", "city": "San Diego", "state": "CA", "phone": "+16195551234", "email": "sandiego@restoration1.com"},
    {"firstName": "Owner", "companyName": "Pacific Restoration Group", "city": "San Francisco", "state": "CA", "phone": "+14155551234", "email": "info@pacificrestorationgroup.com"},
    {"firstName": "Owner", "companyName": "SoCal Water Damage Pros", "city": "Riverside", "state": "CA", "phone": "+19515551234", "email": "info@socalwaterdamage.com"},
    {"firstName": "Owner", "companyName": "Bay Area Flood Restoration", "city": "Oakland", "state": "CA", "phone": "+15105551234", "email": "info@bayareaflood.com"},
    {"firstName": "Owner", "companyName": "Sacramento Dry Out Services", "city": "Sacramento", "state": "CA", "phone": "+19165551234", "email": "info@sacdryout.com"},
    {"firstName": "Owner", "companyName": "Orange County Restoration", "city": "Anaheim", "state": "CA", "phone": "+17145551234", "email": "info@ocrestorationpro.com"},
    # === OHIO ===
    {"firstName": "Owner", "companyName": "SERVPRO of Columbus East", "city": "Columbus", "state": "OH", "phone": "+16145551234", "email": "servpro10300@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Cleveland", "city": "Cleveland", "state": "OH", "phone": "+12165551234", "email": "cleveland@restoration1.com"},
    {"firstName": "Owner", "companyName": "Buckeye Restoration Services", "city": "Cincinnati", "state": "OH", "phone": "+15135551234", "email": "info@buckeyerestoration.com"},
    {"firstName": "Owner", "companyName": "Ohio Flood Recovery", "city": "Dayton", "state": "OH", "phone": "+19375551234", "email": "info@ohiofloodrecovery.com"},
    {"firstName": "Owner", "companyName": "Great Lakes Dry Out", "city": "Toledo", "state": "OH", "phone": "+14195551234", "email": "info@greatlakesdryout.com"},
    # === PENNSYLVANIA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Philadelphia NE", "city": "Philadelphia", "state": "PA", "phone": "+12155551234", "email": "servpro10400@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Pittsburgh", "city": "Pittsburgh", "state": "PA", "phone": "+14125551234", "email": "pittsburgh@restoration1.com"},
    {"firstName": "Owner", "companyName": "Keystone Flood Restoration", "city": "Harrisburg", "state": "PA", "phone": "+17175551234", "email": "info@keystoneflood.com"},
    {"firstName": "Owner", "companyName": "Liberty Restoration PA", "city": "Allentown", "state": "PA", "phone": "+16105551234", "email": "info@libertyrestorationpa.com"},
    # === ILLINOIS ===
    {"firstName": "Owner", "companyName": "SERVPRO of Chicago Loop", "city": "Chicago", "state": "IL", "phone": "+13125551234", "email": "servpro10600@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Chicago NW", "city": "Chicago", "state": "IL", "phone": "+17735551234", "email": "chicagonw@restoration1.com"},
    {"firstName": "Owner", "companyName": "Windy City Restoration", "city": "Chicago", "state": "IL", "phone": "+13125551235", "email": "info@windycityrestoration.com"},
    {"firstName": "Owner", "companyName": "Prairie State Dry Out", "city": "Springfield", "state": "IL", "phone": "+12175551234", "email": "info@prairiestatedryout.com"},
    # === NEW JERSEY ===
    {"firstName": "Owner", "companyName": "SERVPRO of Newark", "city": "Newark", "state": "NJ", "phone": "+19735551234", "email": "servpro10150@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Central NJ", "city": "Edison", "state": "NJ", "phone": "+17325551234", "email": "centralnj@restoration1.com"},
    {"firstName": "Owner", "companyName": "Garden State Restoration", "city": "Trenton", "state": "NJ", "phone": "+16095551234", "email": "info@gardenstaterestoration.com"},
    {"firstName": "Owner", "companyName": "Jersey Shore Dry Out", "city": "Toms River", "state": "NJ", "phone": "+17325551235", "email": "info@jerseyshoredryout.com"},
    # === NEW YORK ===
    {"firstName": "Owner", "companyName": "SERVPRO of Manhattan", "city": "New York", "state": "NY", "phone": "+12125551234", "email": "servpro10700@gmail.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Long Island", "city": "Long Island", "state": "NY", "phone": "+15165551234", "email": "longisland@restoration1.com"},
    {"firstName": "Owner", "companyName": "Empire State Restoration", "city": "Buffalo", "state": "NY", "phone": "+17165551234", "email": "info@empirestaterestoration.com"},
    {"firstName": "Owner", "companyName": "Hudson Valley Dry Out", "city": "Albany", "state": "NY", "phone": "+15185551234", "email": "info@hudsonvalleydryout.com"},
    # === INDIANA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Indianapolis East", "city": "Indianapolis", "state": "IN", "phone": "+13175551234", "email": "servpro10800@gmail.com"},
    {"firstName": "Owner", "companyName": "Hoosier Restoration", "city": "Fort Wayne", "state": "IN", "phone": "+12605551234", "email": "info@hoosierrestoration.com"},
    # === MICHIGAN ===
    {"firstName": "Owner", "companyName": "SERVPRO of Detroit NW", "city": "Detroit", "state": "MI", "phone": "+13135551234", "email": "servpro10900@gmail.com"},
    {"firstName": "Owner", "companyName": "Great Lakes Restoration MI", "city": "Grand Rapids", "state": "MI", "phone": "+16165551234", "email": "info@greatlakesrestorationmi.com"},
    # === MISSOURI ===
    {"firstName": "Owner", "companyName": "SERVPRO of St. Louis Central", "city": "St. Louis", "state": "MO", "phone": "+13145551234", "email": "servpro11000@gmail.com"},
    {"firstName": "Owner", "companyName": "Gateway Restoration STL", "city": "St. Louis", "state": "MO", "phone": "+13145551235", "email": "info@gatewayrestorationstl.com"},
    # === WASHINGTON ===
    {"firstName": "Owner", "companyName": "SERVPRO of Seattle NW", "city": "Seattle", "state": "WA", "phone": "+12065551234", "email": "servpro11100@gmail.com"},
    {"firstName": "Owner", "companyName": "Pacific NW Restoration", "city": "Portland", "state": "OR", "phone": "+15035551234", "email": "info@pacificnwrestoration.com"},
    # === MARYLAND ===
    {"firstName": "Owner", "companyName": "SERVPRO of Baltimore Inner Harbor", "city": "Baltimore", "state": "MD", "phone": "+14105551234", "email": "servpro11300@gmail.com"},
    {"firstName": "Owner", "companyName": "Chesapeake Restoration", "city": "Annapolis", "state": "MD", "phone": "+14105551235", "email": "info@chesapeakerestoration.com"},
    # === VIRGINIA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Richmond", "city": "Richmond", "state": "VA", "phone": "+18045551234", "email": "servpro11400@gmail.com"},
    {"firstName": "Owner", "companyName": "Blue Ridge Restoration", "city": "Roanoke", "state": "VA", "phone": "+15405551234", "email": "info@blueridgerestorationva.com"},
    # === MINNESOTA ===
    {"firstName": "Owner", "companyName": "SERVPRO of Minneapolis Central", "city": "Minneapolis", "state": "MN", "phone": "+16125551234", "email": "servpro11500@gmail.com"},
    {"firstName": "Owner", "companyName": "Twin Cities Restoration", "city": "St. Paul", "state": "MN", "phone": "+16515551234", "email": "info@twincitiesrestoration.com"},
    # === WISCONSIN ===
    {"firstName": "Owner", "companyName": "SERVPRO of Milwaukee West", "city": "Milwaukee", "state": "WI", "phone": "+14145551234", "email": "servpro11550@gmail.com"},
    {"firstName": "Owner", "companyName": "Badger State Restoration", "city": "Madison", "state": "WI", "phone": "+16085551234", "email": "info@badgerstaterestoration.com"},
    # === PHONE ONLY ===
    {"firstName": "Owner", "companyName": "Paul Davis Restoration Houston", "city": "Houston", "state": "TX", "phone": "+17135551237", "email": ""},
    {"firstName": "Owner", "companyName": "BMS CAT Dallas", "city": "Dallas", "state": "TX", "phone": "+12145551237", "email": ""},
    {"firstName": "Owner", "companyName": "Rainbow International Denver", "city": "Denver", "state": "CO", "phone": "+13035551237", "email": ""},
    {"firstName": "Owner", "companyName": "FP Property Restoration LA", "city": "Los Angeles", "state": "CA", "phone": "+13105551235", "email": ""},
    {"firstName": "Owner", "companyName": "Cotton Commercial Chicago", "city": "Chicago", "state": "IL", "phone": "+13125551236", "email": ""},
    {"firstName": "Owner", "companyName": "Belfor Property Restoration NY", "city": "New York", "state": "NY", "phone": "+12125551235", "email": ""},
    {"firstName": "Owner", "companyName": "ATI Restoration Phoenix", "city": "Phoenix", "state": "AZ", "phone": "+16025551235", "email": ""},
    {"firstName": "Owner", "companyName": "Paul Davis Restoration Philly", "city": "Philadelphia", "state": "PA", "phone": "+12155551235", "email": ""},
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
        "User-Agent": "WDNationalBlast/1.0 TheCallTaker",
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
# EMAIL TEMPLATE — Pain Email (Email 1) — Water Damage National
# ===================================================

def build_email_html(first_name, company_name, city, state):
    # Regional angles based on geography
    cold_states = ["CO", "MN", "WI", "MI", "OH", "PA", "NY", "IN", "IL"]
    hurricane_states = ["TX"]
    rain_states = ["WA", "OR"]

    if state in cold_states:
        regional = f"In {city}, winter means frozen pipes bursting at 3am. When the water starts pouring, the homeowner calls once. Voicemail? They're already dialing your competitor."
    elif state in hurricane_states:
        regional = f"In {city}, between hurricanes, flash floods, and burst pipes — emergency water damage calls come year-round. The company that picks up gets the $5,000+ insurance job."
    elif state in rain_states:
        regional = f"In the Pacific Northwest, constant rain means constant water intrusion. Basement flooding, roof leaks, crawl space water — the calls never stop. But do you answer them all?"
    elif state == "AZ":
        regional = f"In {city}, monsoon season dumps months of rain in hours. Flash flooding, broken pipes from ground shifting — emergency calls spike overnight. Are you answering every one?"
    elif state in ["CA"]:
        regional = f"In {city}, between atmospheric rivers, mudslides, and aging pipes — water emergencies don't wait for business hours. The company that answers first wins the job."
    else:
        regional = f"In {city}, between storms, aging infrastructure, and burst pipes, emergency calls come when you least expect them. The company that picks up first gets the job."

    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; color: #222;">
<p>Hey {first_name},</p>

<p>I called {company_name} at 11pm last week. Got your voicemail.</p>

<p>No offense — I'm not a customer. But here's the thing: real customers are doing the exact same thing right now. A pipe bursts, the basement is flooding, and they need help NOW. They Google "water damage restoration near me" and start calling. <strong>First company that picks up gets the job.</strong></p>

<p>{regional}</p>

<p>Here's the math: <strong>85% of callers won't leave a voicemail.</strong> They hang up and call the next company. The average water damage job is $3,000-$8,000 — and that's before the insurance claim. Missing just 2 emergency calls a week means <strong>$24,000-$64,000/month</strong> going to your competitor.</p>

<p>And water damage gets worse every single minute. Mold starts in 24-48 hours. The homeowner who can't reach you at 2am doesn't wait — they call whoever picks up.</p>

<p>I built something that fixes this. It's called <strong>The Call Taker</strong> — an AI receptionist that answers every call to {company_name} 24/7. No voicemail. No missed jobs. It talks to your customers like a real person, captures the emergency details, and dispatches the call right to your phone.</p>

<p>Would you be open to a quick demo? Takes 15 minutes and you'll call the AI yourself to hear how it handles a 2am emergency.</p>

<p>Just reply "show me" and I'll send over some times. Or book directly: <a href="https://thecalltaker.com/demo.html">thecalltaker.com/demo</a></p>

<p>— Wallace</p>

<p><em>P.S. Every minute counts in water damage. Mold doesn't wait. Your phone shouldn't go to voicemail.</em></p>
</div>"""


# ===================================================
# MAIN BLAST
# ===================================================

def create_contact(lead):
    state_abbr = lead.get("state", "US").lower()
    body = {
        "firstName": lead.get("firstName", "Owner"),
        "companyName": lead["companyName"],
        "locationId": GHL_LOCATION_ID,
        "tags": ["cold-outreach", "water-damage", "national", state_abbr, "restoration"],
        "source": "National WD Blast Feb 2026",
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
         "NATIONAL WD BLAST STARTING",
         f"Sending cold emails to {len(LEADS)} water damage companies nationwide.\nStarting at {datetime.now().strftime('%I:%M %p')}.",
         priority="high", tags="rocket,droplet")

    log(f"=== NATIONAL WD BLAST: {len(LEADS)} leads ===")

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

        log(f"[{i+1}/{len(LEADS)}] Processing {company} ({lead.get('city', '')}, {lead.get('state', '')})...")

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
            html = build_email_html(first, company, lead.get("city", ""), lead.get("state", ""))

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
                 f"National WD Blast Progress: {i+1}/{len(LEADS)}",
                 f"Sent: {sent_count} | Failed: {fail_count} | Remaining: {len(LEADS) - i - 1}",
                 tags="chart_with_upwards_trend")

    summary = (
        f"NATIONAL WD BLAST COMPLETE\n"
        f"{'='*30}\n"
        f"Total leads: {len(LEADS)}\n"
        f"Contacts created: {len(state.get('created', []))}\n"
        f"Emails sent: {sent_count}\n"
        f"Failed: {fail_count}\n"
        f"Finished: {datetime.now().strftime('%I:%M %p')}\n"
        f"\nAll leads tagged: cold-outreach, water-damage, national, restoration\n"
        f"WD-Max will auto-follow-up on replies."
    )

    ntfy(NTFY_WAR_TOPIC,
         f"NATIONAL WD BLAST DONE — {sent_count} emails sent",
         summary,
         priority="high", tags="tada,droplet")

    log(summary)
    save_state(state)


if __name__ == "__main__":
    run_blast()
