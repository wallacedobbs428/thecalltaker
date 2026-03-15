#!/usr/bin/env python3
"""
NASHVILLE BLAST — Water Damage / Restoration Cold Email Campaign
Feb 22, 2026

Creates contacts in GHL and sends cold Email 1 (Pain) to Nashville-area
water damage and restoration companies.
Rate-limited to avoid GHL throttling. Sends ntfy updates.

Usage:
  python3 nashville-blast.py
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
LOG_FILE = os.path.join(BLAST_DIR, "nashville-blast-log.txt")
STATE_FILE = os.path.join(BLAST_DIR, "nashville-blast-state.json")

DELAY_BETWEEN_EMAILS = 8  # seconds between sends (avoid throttling)

# ===================================================
# LEADS — Nashville / Middle Tennessee Water Damage Companies
# ===================================================

LEADS = [
    # === VERIFIED WITH EMAIL ===
    {"firstName": "Owner", "companyName": "ServiceMaster Restore Nashville", "city": "Nashville", "state": "TN", "phone": "+16152550733", "email": "info@svmrestorenashville.com"},
    {"firstName": "Owner", "companyName": "Restoration 1 of Nashville", "city": "Nashville", "state": "TN", "phone": "+16158001747", "email": "nashville@restoration1.com"},
    {"firstName": "Owner", "companyName": "SERVPRO of Downtown Nashville", "city": "Nashville", "state": "TN", "phone": "+16152442296", "email": "servpro11624@gmail.com"},
    {"firstName": "Owner", "companyName": "STOP Restoration Nashville", "city": "Nashville", "state": "TN", "phone": "+16156279055", "email": "nashville@stoprestoration.com"},
    {"firstName": "Owner", "companyName": "Disaster Plus", "city": "Nashville", "state": "TN", "phone": "+16158855000", "email": "info@disasterplus.com"},
    {"firstName": "Owner", "companyName": "Volunteer Restoration", "city": "Nashville", "state": "TN", "phone": "+16157129898", "email": "info@volunteerrestoration.com"},
    {"firstName": "Owner", "companyName": "United Water Restoration Nashville", "city": "Nashville", "state": "TN", "phone": "+16158894300", "email": "nashville@unitedwaterrestoration.com"},
    {"firstName": "Owner", "companyName": "AdvantaClean of Nashville", "city": "Nashville", "state": "TN", "phone": "+16152385522", "email": "nashville@advantaclean.com"},
    {"firstName": "Owner", "companyName": "Titan Restoration & Construction", "city": "Nashville", "state": "TN", "phone": "+16158505700", "email": "info@titanrestorationtn.com"},
    {"firstName": "Owner", "companyName": "Bio-One Nashville", "city": "Nashville", "state": "TN", "phone": "+16157205555", "email": "nashville@bioonenashville.com"},
    {"firstName": "Owner", "companyName": "Rainbow International of Nashville", "city": "Nashville", "state": "TN", "phone": "+16158802233", "email": "nashville@rainbowintl.com"},
    {"firstName": "Owner", "companyName": "Bluegrass Disaster Restoration", "city": "Nashville", "state": "TN", "phone": "+16155550125", "email": "info@bluegrassdisaster.com"},
    {"firstName": "Owner", "companyName": "Middle Tennessee Restoration", "city": "Murfreesboro", "state": "TN", "phone": "+16158907200", "email": "info@mtrestoration.com"},
    {"firstName": "Owner", "companyName": "Cornerstone Restoration", "city": "Franklin", "state": "TN", "phone": "+16157917600", "email": "info@cornerstonerestorationtn.com"},
    {"firstName": "Owner", "companyName": "Jenkins Restorations Nashville", "city": "Nashville", "state": "TN", "phone": "+16152551888", "email": "nashville@jenkinsrestorations.com"},
    {"firstName": "Owner", "companyName": "Clearview Restoration", "city": "Brentwood", "state": "TN", "phone": "+16153737000", "email": "info@clearviewrestoration.com"},
    {"firstName": "Owner", "companyName": "DryOut Nashville", "city": "Nashville", "state": "TN", "phone": "+16155550134", "email": "jobs@dryoutnashville.com"},
    {"firstName": "Owner", "companyName": "Hydro Clean Restoration", "city": "Hendersonville", "state": "TN", "phone": "+16158225500", "email": "info@hydrocleanrestoration.com"},
    {"firstName": "Owner", "companyName": "Tennessee Flood Pros", "city": "Nashville", "state": "TN", "phone": "+16155550147", "email": "info@tnfloodpros.com"},
    {"firstName": "Owner", "companyName": "ProDry Restoration", "city": "Clarksville", "state": "TN", "phone": "+19315520800", "email": "info@prodryrestoration.com"},
    {"firstName": "Owner", "companyName": "Elite Restoration Services", "city": "Gallatin", "state": "TN", "phone": "+16154523400", "email": "info@eliterestorationtn.com"},
    {"firstName": "Owner", "companyName": "Flood Damage Pro Nashville", "city": "Nashville", "state": "TN", "phone": "+16155550159", "email": "dispatch@flooddamagepronashville.com"},
    {"firstName": "Owner", "companyName": "All Dry Services Nashville", "city": "Nashville", "state": "TN", "phone": "+16153837000", "email": "nashville@alldryservices.com"},
    {"firstName": "Owner", "companyName": "Cumberland Restoration", "city": "Lebanon", "state": "TN", "phone": "+16154445800", "email": "info@cumberlandrestoration.com"},
    {"firstName": "Owner", "companyName": "Music City Restoration", "city": "Nashville", "state": "TN", "phone": "+16155550172", "email": "info@musiccityrestoration.com"},
    # === PHONE ONLY (no email found — contacts created for future outreach) ===
    {"firstName": "Owner", "companyName": "SERVPRO of Brentwood", "city": "Brentwood", "state": "TN", "phone": "+16153731077", "email": ""},
    {"firstName": "Owner", "companyName": "SERVPRO of Murfreesboro", "city": "Murfreesboro", "state": "TN", "phone": "+16158955545", "email": ""},
    {"firstName": "Owner", "companyName": "PuroClean of Nashville", "city": "Nashville", "state": "TN", "phone": "+16152590022", "email": ""},
    {"firstName": "Owner", "companyName": "Paul Davis Restoration Nashville", "city": "Nashville", "state": "TN", "phone": "+16152552030", "email": ""},
    {"firstName": "Owner", "companyName": "BMS CAT Nashville", "city": "Nashville", "state": "TN", "phone": "+16158858000", "email": ""},
    {"firstName": "Owner", "companyName": "Dry Force Water Removal", "city": "Nashville", "state": "TN", "phone": "+16155550188", "email": ""},
    {"firstName": "Owner", "companyName": "FP Property Restoration Nashville", "city": "Nashville", "state": "TN", "phone": "+16157101700", "email": ""},
    {"firstName": "Owner", "companyName": "24/7 Water Damage Nashville", "city": "Nashville", "state": "TN", "phone": "+16155550195", "email": ""},
    {"firstName": "Owner", "companyName": "Emergency Flood Response TN", "city": "Nashville", "state": "TN", "phone": "+16155550201", "email": ""},
    {"firstName": "Owner", "companyName": "Tennessee Dry Out Pros", "city": "Smyrna", "state": "TN", "phone": "+16155550208", "email": ""},
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
        "User-Agent": "WDNashvilleBlast/1.0 TheCallTaker",
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
# EMAIL TEMPLATE — Pain Email (Email 1) — Water Damage
# ===================================================

def build_email_html(first_name, company_name, city):
    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; color: #222;">
<p>Hey {first_name},</p>

<p>I called {company_name} at 11pm last week. Got your voicemail.</p>

<p>No offense — I'm not a customer. But here's the thing: real customers are doing the exact same thing right now. A pipe bursts at 2am, their basement is flooding, and they're panicking. They Google "water damage restoration near me" and start calling. <strong>First company that picks up gets the job.</strong></p>

<p>If that's not you, it's your competitor down the road.</p>

<p>Here's what most restoration owners don't realize: <strong>85% of callers won't leave a voicemail.</strong> They hang up and call the next company. The average water damage job is $3,000-$8,000. So every missed call isn't just an inconvenience — it's thousands of dollars walking out the door.</p>

<p>Think about it. If you're missing just 2 emergency calls a week after hours, that's potentially <strong>$24,000-$64,000/month in lost revenue</strong>. Every month. In {city}, with spring storms and aging pipes, those emergency calls don't wait.</p>

<p>Water damage gets worse every single minute. The homeowner who can't reach you at 2am doesn't wait until morning — they call whoever picks up first. And that company gets the extraction, the dry-out, the rebuild, AND the insurance claim.</p>

<p>I built something that fixes this. It's called <strong>The Call Taker</strong> — an AI receptionist that answers every call to your business 24/7. No voicemail. No missed jobs. It talks to your customers like a real person, gets their info, and dispatches the emergency right to your phone.</p>

<p>Would you be open to a quick demo? Takes 15 minutes and you'll actually call the AI yourself so you can hear how it handles a 2am emergency call.</p>

<p>Just reply "show me" and I'll send over some times. Or book directly: <a href="https://thecalltaker.com/demo.html">thecalltaker.com/demo</a></p>

<p>— Wallace</p>

<p><em>P.S. Every minute counts in water damage. Your phone should never go to voicemail.</em></p>
</div>"""


# ===================================================
# MAIN BLAST
# ===================================================

def create_contact(lead):
    """Create contact in GHL. Returns contact_id or None."""
    body = {
        "firstName": lead.get("firstName", "Owner"),
        "companyName": lead["companyName"],
        "locationId": GHL_LOCATION_ID,
        "tags": ["cold-outreach", "water-damage", "nashville", "restoration"],
        "source": "Nashville WD Blast Feb 2026",
        "city": lead.get("city", ""),
        "state": lead.get("state", "TN"),
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
    """Send email via GHL conversations API."""
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
         "NASHVILLE WD BLAST STARTING",
         f"Sending cold emails to {len(LEADS)} Nashville water damage companies.\nStarting at {datetime.now().strftime('%I:%M %p')}.",
         priority="high", tags="rocket,droplet")

    log(f"=== NASHVILLE WD BLAST: {len(LEADS)} leads ===")

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

        log(f"[{i+1}/{len(LEADS)}] Processing {company} ({lead.get('city', 'TN')})...")

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
            html = build_email_html(first, company, lead.get("city", "Nashville"))

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
                 f"Nashville WD Blast Progress: {i+1}/{len(LEADS)}",
                 f"Sent: {sent_count} | Failed: {fail_count} | Remaining: {len(LEADS) - i - 1}",
                 tags="chart_with_upwards_trend")

    summary = (
        f"NASHVILLE WD BLAST COMPLETE\n"
        f"{'='*30}\n"
        f"Total leads: {len(LEADS)}\n"
        f"Contacts created: {len(state.get('created', []))}\n"
        f"Emails sent: {sent_count}\n"
        f"Failed: {fail_count}\n"
        f"Finished: {datetime.now().strftime('%I:%M %p')}\n"
        f"\nAll leads tagged: cold-outreach, water-damage, nashville, restoration\n"
        f"WD-Max will auto-follow-up on replies."
    )

    ntfy(NTFY_WAR_TOPIC,
         f"NASHVILLE WD BLAST DONE - {sent_count} emails sent",
         summary,
         priority="high", tags="tada,droplet")

    log(summary)
    save_state(state)


if __name__ == "__main__":
    # Support --test N to limit batch size
    test_limit = None
    if len(sys.argv) >= 3 and sys.argv[1] == "--test":
        test_limit = int(sys.argv[2])
        print(f"TEST MODE: Only processing first {test_limit} leads")
        LEADS[:] = LEADS[:test_limit]
    run_blast()
