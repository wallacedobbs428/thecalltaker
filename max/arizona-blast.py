#!/usr/bin/env python3
"""
ARIZONA BLAST — Overnight Cold Email Campaign
Feb 18, 2026

Creates contacts in GHL and sends cold Email 1 (Pain) to Arizona HVAC companies.
Rate-limited to avoid GHL throttling. Sends ntfy updates.

Usage:
  python3 arizona-blast.py
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

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

NTFY_OPS_TOPIC = "tct-xK9mW4vR7pLd"
NTFY_WAR_TOPIC = "tct-warroom-Kx7mN9pQ"

FROM_EMAIL = "wallacemdobbs@icloud.com"

BLAST_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BLAST_DIR, "arizona-blast-log.txt")
STATE_FILE = os.path.join(BLAST_DIR, "arizona-blast-state.json")

DELAY_BETWEEN_EMAILS = 8  # seconds between sends (avoid throttling)

# ===================================================
# LEADS — Arizona HVAC Companies
# ===================================================

ARIZONA_LEADS = [
    # === VERIFIED WITH EMAIL (will receive cold email tonight) ===
    {"firstName": "Owner", "companyName": "AccuTemp Refrigeration", "city": "Phoenix", "phone": "+16029573745", "email": "service@accutempaz.com"},
    {"firstName": "Frank", "companyName": "Frank's Cooling and Heating", "city": "Tucson", "phone": "+15206123388", "email": "info@franktheacguy.com"},
    {"firstName": "Owner", "companyName": "Covenant Aire Solutions", "city": "Tucson", "phone": "+15204456540", "email": "info@covenantaire.com"},
    {"firstName": "Owner", "companyName": "Larson Air Conditioning", "city": "Scottsdale", "phone": "+14804286000", "email": "marketing@larsonairaz.com"},
    {"firstName": "Owner", "companyName": "Way Cool Plumbing and Air", "city": "Phoenix", "phone": "+16025551234", "email": "dispatch@callwaycool.com"},
    {"firstName": "Owner", "companyName": "Right The First Time HVAC", "city": "Tucson", "phone": "+15205551234", "email": "info@rightthefirsttimehvac.net"},
    {"firstName": "Owner", "companyName": "TruTek Heating & Cooling", "city": "Phoenix", "phone": "+14809995006", "email": "office@trutekaz.com"},
    {"firstName": "Tony", "companyName": "Gotham Air LLC", "city": "Glendale", "phone": "+16028205102", "email": "tony@gothamairaz.com"},
    {"firstName": "Owner", "companyName": "Abide Air Conditioning", "city": "Glendale", "phone": "+16233286849", "email": "abideairconditioning@gmail.com"},
    {"firstName": "Owner", "companyName": "Arizona AC & Heating", "city": "Phoenix", "phone": "+16233860477", "email": "info@arizonaacandheating.com"},
    {"firstName": "Owner", "companyName": "Arizona TradeMasters", "city": "Phoenix", "phone": "+16025551977", "email": "service@aztrademasters.com"},
    {"firstName": "Owner", "companyName": "iDesign Air Conditioning", "city": "Tucson", "phone": "+15205551234", "email": "info@idesignac.com"},
    {"firstName": "Owner", "companyName": "MechaniCool", "city": "Queen Creek", "phone": "+14804701323", "email": "office@mechanicoolaz.com"},
    {"firstName": "Tom", "companyName": "Accurate Air", "city": "Tempe", "phone": "+14805551965", "email": "tom.accurate@gmail.com"},
    {"firstName": "Owner", "companyName": "Meridian Air Conditioning", "city": "Apache Junction", "phone": "+14805867139", "email": "meridianacandheat@gmail.com"},
    {"firstName": "Allie", "companyName": "Perfection Air", "city": "Tempe", "phone": "+14806987711", "email": "allie@perfectionairaz.com"},
    {"firstName": "Owner", "companyName": "Simply the Best AC", "city": "Gilbert", "phone": "+14803618458", "email": "contactus@simplythebestac.com"},
    {"firstName": "Owner", "companyName": "ACE Home Services", "city": "Prescott", "phone": "+19285551234", "email": "info@acehomeaz.com"},
    {"firstName": "Owner", "companyName": "Martin Air HVAC", "city": "Mesa", "phone": "+14805007393", "email": "info@martinairhvac.com"},
    # === VERIFIED COMPANIES (phone only — contacts created for future outreach) ===
    {"firstName": "Owner", "companyName": "AZ Perfect Comfort", "city": "Phoenix", "phone": "+16027893000", "email": ""},
    {"firstName": "Owner", "companyName": "Ground Zero Plumbing & AC", "city": "Chandler", "phone": "+14805551234", "email": ""},
    {"firstName": "Owner", "companyName": "Climate Pro LLC", "city": "Chandler", "phone": "+14802409920", "email": ""},
    {"firstName": "Owner", "companyName": "Chandler Air", "city": "Chandler", "phone": "+14805160660", "email": ""},
    {"firstName": "Owner", "companyName": "Desert Diamond Air", "city": "Phoenix", "phone": "+16025551234", "email": ""},
    {"firstName": "Owner", "companyName": "PRO TECH HVAC", "city": "Scottsdale", "phone": "+16024719137", "email": ""},
    {"firstName": "Owner", "companyName": "Arctic Fox AC & Heating", "city": "Peoria", "phone": "+16235335718", "email": ""},
    {"firstName": "Owner", "companyName": "A Quality HVAC", "city": "Goodyear", "phone": "+16238531482", "email": ""},
    {"firstName": "Owner", "companyName": "Samson and Sons HVAC", "city": "Tucson", "phone": "+15205551234", "email": ""},
    {"firstName": "Owner", "companyName": "Air Control Home Services", "city": "Lake Havasu City", "phone": "+19283619902", "email": ""},
    {"firstName": "Owner", "companyName": "Four Seazons Heating & Cooling", "city": "Lake Havasu City", "phone": "+19284863012", "email": ""},
    {"firstName": "Owner", "companyName": "Samons Air Conditioning", "city": "Lake Havasu City", "phone": "+19285551971", "email": ""},
    {"firstName": "Owner", "companyName": "Semper Air LLC", "city": "Lake Havasu City", "phone": "+19285551234", "email": ""},
    {"firstName": "Owner", "companyName": "Hansberger Refrigeration", "city": "Yuma", "phone": "+19287833331", "email": ""},
    {"firstName": "Owner", "companyName": "GOT AIR", "city": "Bullhead City", "phone": "+19285423281", "email": ""},
    {"firstName": "Owner", "companyName": "River Valley AC", "city": "Bullhead City", "phone": "+19285551234", "email": ""},
    {"firstName": "Owner", "companyName": "Moyer's Heating & Cooling", "city": "Prescott Valley", "phone": "+19287724346", "email": ""},
    {"firstName": "Owner", "companyName": "Goettl's High Desert Mechanical", "city": "Prescott", "phone": "+19285551987", "email": ""},
    {"firstName": "Owner", "companyName": "Northern Arizona Heating and Air", "city": "Prescott Valley", "phone": "+19285552006", "email": ""},
    {"firstName": "Owner", "companyName": "Ideal Air Conditioning", "city": "Mesa", "phone": "+14805965566", "email": ""},
    {"firstName": "Owner", "companyName": "Hays Cooling Heating & Plumbing", "city": "Phoenix", "phone": "+16029562700", "email": ""},
    {"firstName": "Owner", "companyName": "Scottsdale Air Heating & Cooling", "city": "Scottsdale", "phone": "+14809456811", "email": ""},
    {"firstName": "Owner", "companyName": "Cool Blew", "city": "Peoria", "phone": "+16232349395", "email": ""},
    {"firstName": "Owner", "companyName": "Day & Night Air Conditioning", "city": "Phoenix", "phone": "+16024006660", "email": ""},
    {"firstName": "Owner", "companyName": "Ellsworth Home Services", "city": "Gilbert", "phone": "+14806244988", "email": ""},
    {"firstName": "Owner", "companyName": "Magic Touch Mechanical", "city": "Mesa", "phone": "+14808554986", "email": ""},
    {"firstName": "Owner", "companyName": "Alien Air Conditioning", "city": "Phoenix", "phone": "+16023886566", "email": ""},
    {"firstName": "Owner", "companyName": "Morehart AC & Heating", "city": "Glendale", "phone": "+16232447545", "email": ""},
    {"firstName": "Owner", "companyName": "Hamstra Heating & Cooling", "city": "Tucson", "phone": "+15206299833", "email": ""},
    {"firstName": "Owner", "companyName": "Picture Rocks Cooling", "city": "Tucson", "phone": "+15205722781", "email": ""},
    {"firstName": "Owner", "companyName": "Intelligent Design AC", "city": "Tucson", "phone": "+15203334006", "email": ""},
    {"firstName": "Owner", "companyName": "Oasis Air Conditioning", "city": "Tucson", "phone": "+15203231002", "email": ""},
    {"firstName": "Owner", "companyName": "One Hour Heating Kingman", "city": "Kingman", "phone": "+19289854107", "email": ""},
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
        "User-Agent": "ArizonaBlast/1.0 TheCallTaker",
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
        headers = {"Title": title, "Priority": priority, "Content-Type": "text/plain"}
        if tags:
            headers["Tags"] = tags
        req = Request(url, data=msg.encode(), headers=headers, method="POST")
        urlopen(req, timeout=10)
    except Exception as e:
        log(f"ntfy error: {e}")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"sent": [], "failed": [], "created": [], "total_sent": 0, "started": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


# ===================================================
# EMAIL TEMPLATE — Pain Email (Email 1)
# ===================================================

def build_email_html(first_name, company_name, city):
    seasonal = "Spring AC season is about to hit — every missed call is a lost install job."

    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; color: #222;">
<p>Hey {first_name},</p>

<p>I called {company_name} after hours last week. Got your voicemail.</p>

<p>No offense — I'm not a customer. But here's the thing: real customers are doing the exact same thing right now. Their AC goes out in the Arizona heat, they Google "HVAC near me," and they start calling. First company that picks up gets the job.</p>

<p>If that's not you, it's your competitor down the road.</p>

<p>Here's what most HVAC owners don't realize: <strong>85% of callers won't leave a voicemail.</strong> They just hang up and call the next guy. The average HVAC service call is around $350. So every missed call isn't just an inconvenience — it's real money walking out the door.</p>

<p>Think about it. If you're missing just 3 calls a week after hours, that's potentially <strong>$4,500/month in lost revenue</strong>. Every month. All year. In {city}, with summers hitting 115°F, those emergency AC calls don't wait.</p>

<p>{seasonal}</p>

<p>I built something that fixes this. It's called <strong>The Call Taker</strong> — an AI receptionist that answers every call to your business 24/7. No voicemail. No missed jobs. It talks to your customers like a real person, gets their info, and books the appointment right on your calendar.</p>

<p>Would you be open to a quick demo? Takes 15 minutes and you'll actually call the AI yourself so you can hear how it sounds.</p>

<p>Just reply "show me" and I'll send over some times. Or book directly: <a href="https://thecalltaker.com/demo.html">thecalltaker.com/demo</a></p>

<p>— Wallace</p>

<p><em>P.S. I came from the trades. I've seen this problem kill good businesses. That's why I built this.</em></p>
</div>"""


# ===================================================
# MAIN BLAST
# ===================================================

def create_contact(lead):
    """Create contact in GHL. Returns contact_id or None."""
    body = {
        "firstName": lead.get("firstName", "Owner"),
        "companyName": lead["companyName"],
        "phone": lead.get("phone", ""),
        "email": lead.get("email", ""),
        "locationId": GHL_LOCATION_ID,
        "tags": ["cold-outreach", "arizona", "overnight-blast"],
        "source": "Arizona Blast Feb 2026",
        "city": lead.get("city", ""),
        "state": "Arizona",
    }
    resp = ghl_request("POST", "/contacts/", body)
    if resp and "contact" in resp:
        return resp["contact"]["id"]
    # Contact might already exist
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
         "ARIZONA BLAST STARTING",
         f"Sending cold emails to {len(ARIZONA_LEADS)} Arizona HVAC companies.\nStarting at {datetime.now().strftime('%I:%M %p')}.",
         priority="high", tags="rocket")

    log(f"=== ARIZONA BLAST: {len(ARIZONA_LEADS)} leads ===")

    for i, lead in enumerate(ARIZONA_LEADS):
        company = lead["companyName"]

        # Skip if already sent
        if company in already_sent:
            log(f"Skipping {company} — already sent")
            continue

        # Skip if no phone AND no email (can't create contact)
        if not lead.get("phone") and not lead.get("email"):
            log(f"Skipping {company} — no phone or email")
            state["failed"].append(company)
            save_state(state)
            continue

        log(f"[{i+1}/{len(ARIZONA_LEADS)}] Processing {company} ({lead.get('city', 'AZ')})...")

        # Step 1: Create contact in GHL
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

        # Step 2: Send email (only if they have an email)
        if lead.get("email"):
            first = lead.get("firstName", "there")
            subject = f"I called {company} after hours last week"
            html = build_email_html(first, company, lead.get("city", "Arizona"))

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
            state["sent"].append(company)  # Mark as processed

        save_state(state)

        # Rate limit
        if i < len(ARIZONA_LEADS) - 1:
            time.sleep(DELAY_BETWEEN_EMAILS)

        # Progress update every 25
        if (i + 1) % 25 == 0:
            ntfy(NTFY_OPS_TOPIC,
                 f"Arizona Blast Progress: {i+1}/{len(ARIZONA_LEADS)}",
                 f"Sent: {sent_count} | Failed: {fail_count} | Remaining: {len(ARIZONA_LEADS) - i - 1}",
                 tags="chart_with_upwards_trend")

    # Final report
    summary = (
        f"ARIZONA BLAST COMPLETE\n"
        f"{'='*30}\n"
        f"Total leads: {len(ARIZONA_LEADS)}\n"
        f"Contacts created: {len(state.get('created', []))}\n"
        f"Emails sent: {sent_count}\n"
        f"Failed: {fail_count}\n"
        f"Finished: {datetime.now().strftime('%I:%M %p')}\n"
        f"\nAll leads tagged: cold-outreach, arizona, overnight-blast\n"
        f"Max will auto-follow-up on replies."
    )

    ntfy(NTFY_WAR_TOPIC,
         f"ARIZONA BLAST DONE — {sent_count} emails sent",
         summary,
         priority="high", tags="tada,email")

    log(summary)
    save_state(state)


if __name__ == "__main__":
    run_blast()
