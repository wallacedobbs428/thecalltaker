#!/usr/bin/env python3
"""
MAX v3 — The Call Taker's Reply Catcher + Follow-Up Machine
Rebuilt Feb 18, 2026

Max no longer sends cold emails. Instantly handles that on burner domains.
Max now does the HIGH-CONVERSION work: catching replies, following up with
engaged leads, detecting demo line calls, triggering secret shopper emails,
and using seasonal/weather urgency to close.

Usage:
  python3 max-engine.py monitor    # Catch replies + demo calls + secret shopper (every 30 min)
  python3 max-engine.py followup   # Warm follow-ups for engaged leads (daily 9am)
  python3 max-engine.py pipeline   # Move leads through stages (daily midnight)
  python3 max-engine.py report     # Daily summary to ntfy (daily 8pm)
  python3 max-engine.py status     # Print current stats
  python3 max-engine.py all        # Run all tasks
"""

import json
import sys
import os
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ===================================================
# CONFIG
# ===================================================

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

PIPELINE_ID = "KhFDURSwBi2fn416BnGf"
CONTACTED_STAGE = "8285b2c9-9ca3-415f-a57b-ae458045aab4"

NTFY_OPS_TOPIC = "tct-sales-63uYsIT9"
NTFY_WAR_TOPIC = "tct-urgent-Hk9UOEZR"
NTFY_CALLS_TOPIC = "tct-finishtask"

DEMO_LINE = "(615) 784-5747"
DEMO_LINE_NUMBER = "+16157845747"
DEMO_URL = "https://thecalltaker.com/demo.html"
CALENDAR_URL = "https://thecalltaker.com/demo.html"
FROM_EMAIL = "wallacemdobbs@icloud.com"
FROM_NAME = "Wallace Dobbs"

MAX_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(MAX_DIR, "max-state.json")
LOG_FILE = os.path.join(MAX_DIR, "max-log.txt")

# ===================================================
# SEASONAL ENGINE
# ===================================================

def get_season():
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"


def get_seasonal_urgency():
    season = get_season()
    urgency = {
        "spring": "Spring AC season is about to hit — every missed call is a lost install job.",
        "summer": "Peak AC season is HERE. Your phone is ringing off the hook — who's answering overflow?",
        "fall": "Heating season is coming fast. Emergency calls at midnight won't wait for voicemail.",
        "winter": "Furnace emergencies don't wait. When it's 15 degrees and the heat goes out, your customer calls once. If voicemail answers, they call your competitor.",
    }
    return urgency.get(season, urgency["winter"])


# ===================================================
# WEATHER ENGINE (free, no API key)
# ===================================================

def get_weather(city):
    """Get current temp for a city via wttr.in (free, no key)."""
    if not city:
        return None
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=%t"
        req = Request(url, headers={"User-Agent": "MaxEngine/3.0"})
        with urlopen(req, timeout=5) as resp:
            temp_str = resp.read().decode().strip()
            # Parse "+45°F" or "+7°C"
            temp_str = temp_str.replace("°F", "").replace("°C", "").replace("+", "")
            return int(temp_str)
    except:
        return None


def get_weather_angle(city):
    """Return a weather-triggered email angle if extreme temps detected."""
    temp = get_weather(city)
    if temp is None:
        return None
    if temp >= 90:
        return f"Temperatures hitting {temp}°F in {city} — your phone is about to ring off the hook. Every missed call is a lost AC job."
    elif temp <= 32:
        return f"It's {temp}°F in {city} right now. When a furnace dies tonight, your customer calls once. Voicemail means they call someone else."
    return None


# ===================================================
# WARM FOLLOW-UP TEMPLATES (for leads who REPLIED)
# ===================================================

WARM_FOLLOWUP_DAY2 = {
    "subject": "great hearing from you",
    "body": """<p>Hey {{firstName}},</p>
<p>Thanks for getting back to me — I appreciate it.</p>
<p>Just to recap what The Call Taker does for {{companyName}}:</p>
<ul>
<li>Answers every call 24/7 — no voicemail, no missed jobs</li>
<li>Books the appointment and texts you the details</li>
<li>Set up in 48 hours, $497/mo, cancel anytime</li>
</ul>
<p>{{seasonal}}</p>
<p>Want to hear it live? Call the demo line right now: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}

WARM_FOLLOWUP_DAY5 = {
    "subject": "the demo line is live right now",
    "body": """<p>Hey {{firstName}},</p>
<p>Quick reminder — you can hear exactly what your customers would experience by calling our demo line:</p>
<p style="font-size:18px;font-weight:bold;text-align:center;">(615) 784-5747</p>
<p>It picks up in under 2 seconds. Ask it anything — it handles scheduling, emergency calls, after-hours, you name it.</p>
<p>Or if you'd rather, grab a 15-minute slot and I'll walk you through it personally: <a href="https://thecalltaker.com/demo.html">Book a Demo</a></p>
<p>— Wallace</p>""",
}

WARM_FOLLOWUP_DAY8 = {
    "subject": "last note from me",
    "body": """<p>Hey {{firstName}},</p>
<p>Last follow-up from me — I respect your time.</p>
<p>{{seasonal}}</p>
<p>The Call Taker is $497/mo for {{companyName}} to never miss another call. No contracts. Cancel anytime. Set up in 48 hours.</p>
<p>If the timing isn't right, no worries at all. But if you ever want to hear it: <strong>(615) 784-5747</strong></p>
<p>Good luck this season, {{firstName}}.</p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}

# ===================================================
# SECRET SHOPPER EMAIL (for voicemail-confirmed leads)
# ===================================================

SECRET_SHOPPER_EMAIL = {
    "subject": "I called {{companyName}} last night",
    "body": """<p>Hey {{firstName}},</p>
<p>I called {{companyName}} after hours yesterday — and I got your voicemail.</p>
<p>I'm not a customer, so no harm done. But real customers are doing the same thing right now. And 62% of them will never call back.</p>
<p>The Call Taker is an AI receptionist that would have answered that call, gotten the customer's info, booked the job, and texted you the details. 24/7.</p>
<p>Hear exactly what your callers would experience: <strong>(615) 784-5747</strong></p>
<p>$497/mo. No contracts. Set up in 48 hours.</p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}

# ===================================================
# DEMO LINE FOLLOW-UP (for leads who called the demo)
# ===================================================

DEMO_FOLLOWUP_EMAIL = {
    "subject": "you just tried the demo line",
    "body": """<p>Hey {{firstName}},</p>
<p>I saw you just called our demo line — thanks for checking it out!</p>
<p>What you heard is exactly what your customers would experience when they call {{companyName}} after hours, on weekends, or when your team is busy.</p>
<p>Every call answered. Every job booked. Every detail texted to you. 24/7.</p>
<p>Want to set it up for {{companyName}}? Takes 48 hours and $497/mo — no contracts, cancel anytime.</p>
<p>Grab a quick slot and I'll walk you through it: <a href="https://thecalltaker.com/demo.html">Book a Demo</a></p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}

# ===================================================
# WEATHER-TRIGGERED EMAIL
# ===================================================

WEATHER_EMAIL = {
    "subject": "{{companyName}} — this week is going to be busy",
    "body": """<p>Hey {{firstName}},</p>
<p>{{weather_angle}}</p>
<p>The Call Taker answers every call for {{companyName}} 24/7 — books the job, texts you the details. No voicemail. No missed revenue.</p>
<p>$497/mo. No contracts. Hear it live: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] MAX: {msg}"
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
        "User-Agent": "MaxEngine/3.0 TheCallTaker",
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


def ntfy(topic, title, msg, priority="default", tags=""):
    try:
        url = f"https://ntfy.sh/{topic}"
        headers = {"Title": title, "Priority": priority, "Content-Type": "text/plain"}
        if tags:
            headers["Tags"] = tags
        req = Request(url, data=msg.encode(), headers=headers, method="POST")
        urlopen(req, timeout=10)
        log(f"ntfy sent: {title}")
    except Exception as e:
        log(f"ntfy error: {e}")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "known_reply_ids": [],
        "warm_followups": {},       # contact_id: {replied_date, followup_count, last_followup}
        "demo_callers": {},         # contact_id: {detected_date, followed_up}
        "secret_shopper_sent": [],  # contact_ids that got the secret shopper email
        "weather_sent": {},         # contact_id: last_weather_email_date
        "last_reply_check": None,
        "total_replies_detected": 0,
        "total_followups_sent": 0,
        "total_demo_followups": 0,
        "total_secret_shopper": 0,
        "total_weather_emails": 0,
        "total_emails_sent": 0,
        "total_alerts_sent": 0,
    }


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


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


def get_non_customer_contacts(contacts):
    """Filter to leads only — NOT customers (Sam handles those)."""
    leads = []
    for c in contacts:
        tags = [t.lower() for t in c.get("tags", [])]
        if "customer" not in tags and "active-client" not in tags:
            leads.append(c)
    return leads


def get_conversations(contact_id):
    resp = ghl_request("GET",
        f"/conversations/search?locationId={GHL_LOCATION_ID}&contactId={contact_id}",
        version="2021-04-15")
    if resp and "conversations" in resp:
        return resp["conversations"]
    return []


def get_messages(conversation_id):
    resp = ghl_request("GET", f"/conversations/{conversation_id}/messages", version="2021-04-15")
    if resp and "messages" in resp:
        return resp["messages"]
    return []


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
        log(f"Email sent to {contact_id}: {subject}")
        return True
    return False


def personalize(template, contact, extras=None):
    first = contact.get("firstName", contact.get("name", "there"))
    company = contact.get("companyName", "your company")
    text = template.replace("{{firstName}}", first or "there")
    text = text.replace("{{companyName}}", company or "your company")
    text = text.replace("{{seasonal}}", get_seasonal_urgency())
    if extras:
        for key, val in extras.items():
            text = text.replace("{{" + key + "}}", str(val))
    return text


def days_since(date_str):
    if not date_str:
        return 999
    try:
        dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00").split("+")[0].split("T")[0])
        return (datetime.now() - dt).days
    except:
        return 999


# ===================================================
# CORE TASKS
# ===================================================

def monitor_replies():
    """Every 30 min: Catch replies, demo line calls, secret shopper triggers."""
    log("=== MAX v3: Monitor ===")
    state = load_state()
    known = set(state.get("known_reply_ids", []))
    all_contacts = get_all_contacts()
    leads = get_non_customer_contacts(all_contacts)
    new_replies = []

    log(f"Scanning {len(leads)} leads for replies, demo calls, secret shopper tags...")

    for contact in leads:
        cid = contact.get("id")
        name = contact.get("firstName", "Unknown")
        company = contact.get("companyName", "Unknown")
        phone = contact.get("phone", "")
        tags = [t.lower() for t in contact.get("tags", [])]

        # ── SECRET SHOPPER: Check for "voicemail-confirmed" tag ──
        if "voicemail-confirmed" in tags and cid not in state.get("secret_shopper_sent", []):
            subject = personalize(SECRET_SHOPPER_EMAIL["subject"], contact)
            body = personalize(SECRET_SHOPPER_EMAIL["body"], contact)
            if send_email(cid, subject, body):
                state.setdefault("secret_shopper_sent", []).append(cid)
                state["total_secret_shopper"] = state.get("total_secret_shopper", 0) + 1
                state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
                log(f"  SECRET SHOPPER email sent to {name} ({company})")

                ntfy(NTFY_WAR_TOPIC,
                     f"Secret Shopper email sent to {name}",
                     f"Voicemail confirmed for {company}. Max sent the devastating 'I called your business' email.\n\nThis converts 3x better than cold email.",
                     priority="high",
                     tags="telephone_receiver,fire")
                state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1

        # ── SCAN CONVERSATIONS ──
        convos = get_conversations(cid)
        for convo in convos:
            conv_id = convo.get("id")
            if not conv_id:
                continue

            messages = get_messages(conv_id)
            for msg in messages:
                if not isinstance(msg, dict):
                    continue

                msg_id = msg.get("id", "")
                direction = msg.get("direction", "")
                msg_type = msg.get("messageType", msg.get("type", ""))

                if msg_id in known:
                    continue

                # ── DEMO LINE CALL: Inbound call detected ──
                if direction == "inbound" and msg_type in ["CALL", "call", "Call"]:
                    known.add(msg_id)
                    if cid not in state.get("demo_callers", {}):
                        state.setdefault("demo_callers", {})[cid] = {
                            "detected_date": datetime.now().isoformat(),
                            "followed_up": False,
                        }
                        # Immediate follow-up email
                        subject = personalize(DEMO_FOLLOWUP_EMAIL["subject"], contact)
                        body = personalize(DEMO_FOLLOWUP_EMAIL["body"], contact)
                        if send_email(cid, subject, body):
                            state["demo_callers"][cid]["followed_up"] = True
                            state["total_demo_followups"] = state.get("total_demo_followups", 0) + 1
                            state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
                            log(f"  DEMO CALL follow-up sent to {name}")

                        ntfy(NTFY_WAR_TOPIC,
                             f"DEMO CALL: {name} ({company}) called the demo line!",
                             f"{name} from {company} just called the demo line!\nPhone: {phone}\n\nMax sent an immediate follow-up. Call them back NOW while it's fresh!",
                             priority="urgent",
                             tags="telephone_receiver,fire,rotating_light")
                        state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1
                    continue

                # ── INBOUND REPLY: Text/email reply from lead ──
                if direction == "inbound" and msg_id not in known:
                    body_text = msg.get("body", msg.get("message", ""))
                    if not body_text or body_text.strip().upper() in ["STOP", "UNSUBSCRIBE"]:
                        known.add(msg_id)
                        continue

                    known.add(msg_id)
                    new_replies.append({
                        "contact_id": cid,
                        "name": name,
                        "company": company,
                        "phone": phone,
                        "message": body_text[:500],
                        "type": msg_type,
                    })

                    # Track for warm follow-up sequence
                    if cid not in state.get("warm_followups", {}):
                        state.setdefault("warm_followups", {})[cid] = {
                            "replied_date": datetime.now().isoformat(),
                            "followup_count": 0,
                            "last_followup": None,
                        }

        time.sleep(0.5)

    # ── Alert war room for new replies ──
    if new_replies:
        log(f"Found {len(new_replies)} new replies!")
        state["total_replies_detected"] = state.get("total_replies_detected", 0) + len(new_replies)

        for reply in new_replies:
            ntfy(NTFY_WAR_TOPIC,
                 f"REPLY: {reply['name']} ({reply['company']})",
                 f"Message: {reply['message']}\n\nPhone: {reply['phone']}\nType: {reply['type']}\n\nRespond personally ASAP — this lead is warm!",
                 priority="high",
                 tags="rotating_light,speech_balloon")
            state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1
    else:
        log("No new replies.")

    # ── WEATHER CHECK: Send weather-triggered emails to leads in extreme weather ──
    weather_sent_today = 0
    weather_state = state.get("weather_sent", {})
    for contact in leads[:50]:  # Check first 50 to avoid API hammering
        cid = contact.get("id")
        city = contact.get("city", "")
        if not city or weather_sent_today >= 5:
            continue
        # Only send one weather email per contact per 14 days
        if cid in weather_state and days_since(weather_state[cid]) < 14:
            continue

        angle = get_weather_angle(city)
        if angle:
            subject = personalize(WEATHER_EMAIL["subject"], contact)
            body = personalize(WEATHER_EMAIL["body"], contact, {"weather_angle": angle})
            if send_email(cid, subject, body):
                weather_sent_today += 1
                weather_state[cid] = datetime.now().isoformat()
                state["total_weather_emails"] = state.get("total_weather_emails", 0) + 1
                state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
                name = contact.get("firstName", "Unknown")
                log(f"  WEATHER email sent to {name} in {city}")
        time.sleep(1)

    state["weather_sent"] = weather_state
    state["known_reply_ids"] = list(known)[-500:]
    state["last_reply_check"] = datetime.now().isoformat()
    save_state(state)
    return new_replies


def send_warm_followups():
    """Daily 9am: Send warm follow-ups to leads who replied but haven't booked."""
    log("=== MAX v3: Warm Follow-ups ===")
    state = load_state()
    warm = state.get("warm_followups", {})
    all_contacts = get_all_contacts()
    contact_map = {c["id"]: c for c in all_contacts}
    sent_count = 0

    for cid, data in warm.items():
        contact = contact_map.get(cid)
        if not contact:
            continue

        # Skip customers (Sam handles them)
        tags = [t.lower() for t in contact.get("tags", [])]
        if "customer" in tags or "active-client" in tags:
            continue

        replied_date = data.get("replied_date")
        followup_count = data.get("followup_count", 0)
        last_followup = data.get("last_followup")

        days_since_reply = days_since(replied_date)

        # Already done max follow-ups
        if followup_count >= 3:
            continue

        # Day 2 follow-up
        if followup_count == 0 and days_since_reply >= 2:
            template = WARM_FOLLOWUP_DAY2
        # Day 5 follow-up
        elif followup_count == 1 and days_since_reply >= 5:
            template = WARM_FOLLOWUP_DAY5
        # Day 8 follow-up
        elif followup_count == 2 and days_since_reply >= 8:
            template = WARM_FOLLOWUP_DAY8
        else:
            continue

        subject = personalize(template["subject"], contact)
        body = personalize(template["body"], contact)

        if send_email(cid, subject, body):
            sent_count += 1
            data["followup_count"] = followup_count + 1
            data["last_followup"] = datetime.now().isoformat()
            state["total_followups_sent"] = state.get("total_followups_sent", 0) + 1
            state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
            name = contact.get("firstName", "Unknown")
            log(f"  Warm follow-up #{followup_count + 1} sent to {name}")

        time.sleep(2)

    state["warm_followups"] = warm
    save_state(state)

    log(f"Warm follow-ups complete. Sent {sent_count}.")
    if sent_count > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"Max sent {sent_count} warm follow-ups",
             f"Personalized follow-ups sent to {sent_count} leads who replied.\nThese convert 10x better than cold emails.",
             tags="fire,envelope")
    return sent_count


def update_pipeline():
    """Daily midnight: Move leads through pipeline based on activity."""
    log("=== MAX v3: Pipeline Update ===")
    state = load_state()

    resp = ghl_request("GET", f"/opportunities/search?location_id={GHL_LOCATION_ID}&pipeline_id={PIPELINE_ID}")
    if not resp or "opportunities" not in resp:
        log("Could not fetch opportunities.")
        return 0

    opportunities = resp["opportunities"]
    log(f"Checking {len(opportunities)} opportunities...")

    moved = 0
    warm = state.get("warm_followups", {})
    demo_callers = state.get("demo_callers", {})

    for opp in opportunities:
        opp_id = opp.get("id")
        contact_id = opp.get("contact", {}).get("id", opp.get("contactId"))
        current_stage = opp.get("pipelineStageId", "")

        if not contact_id:
            continue

        name = opp.get("contact", {}).get("name", "Unknown")

        # Flag leads who replied or called demo but are still in Contacted stage
        is_engaged = contact_id in warm or contact_id in demo_callers
        if is_engaged and current_stage == CONTACTED_STAGE:
            log(f"  ENGAGED: {name} replied/called demo — needs stage change")
            ntfy(NTFY_WAR_TOPIC,
                 f"MOVE: {name} is engaged!",
                 f"{name} has replied or called the demo line but is still in Contacted stage.\nMove them to Engaged and follow up personally!",
                 priority="high",
                 tags="fire,rotating_light")
            moved += 1
            state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1

        time.sleep(0.5)

    save_state(state)
    log(f"Pipeline check complete. {moved} leads flagged for stage change.")
    return moved


def send_daily_report():
    """Daily 8pm: Summary to ntfy."""
    log("=== MAX v3: Daily Report ===")
    state = load_state()
    all_contacts = get_all_contacts()
    leads = get_non_customer_contacts(all_contacts)

    warm = state.get("warm_followups", {})
    active_warm = sum(1 for v in warm.values() if v.get("followup_count", 0) < 3)

    report = f"""MAX v3 DAILY REPORT — {datetime.now().strftime('%b %d, %Y')}

PIPELINE:
  Total contacts: {len(all_contacts)}
  Active leads (non-customer): {len(leads)}

ENGAGEMENT:
  Replies detected (all time): {state.get('total_replies_detected', 0)}
  Leads in warm follow-up: {active_warm}
  Demo line callers: {len(state.get('demo_callers', {}))}
  Secret shopper emails sent: {state.get('total_secret_shopper', 0)}
  Weather-triggered emails: {state.get('total_weather_emails', 0)}

ACTIVITY:
  Warm follow-ups sent: {state.get('total_followups_sent', 0)}
  Demo call follow-ups: {state.get('total_demo_followups', 0)}
  Total emails sent by Max: {state.get('total_emails_sent', 0)}
  War room alerts: {state.get('total_alerts_sent', 0)}
  Last reply check: {state.get('last_reply_check', 'Never')}

SEASON: {get_season().upper()} — angles tuned for {get_season()} urgency

STATUS: Max v3 is active. Catching replies every 30 min.
Cold outreach: Handled by Instantly (120/day on burner domains)."""

    ntfy(NTFY_OPS_TOPIC,
         f"Max Daily Report — {datetime.now().strftime('%b %d')}",
         report,
         tags="clipboard,chart_with_upwards_trend")

    log("Daily report sent.")
    return report


def print_status():
    state = load_state()
    all_contacts = get_all_contacts()
    leads = get_non_customer_contacts(all_contacts)
    warm = state.get("warm_followups", {})
    active_warm = sum(1 for v in warm.values() if v.get("followup_count", 0) < 3)

    print("\n" + "=" * 50)
    print("  MAX v3 — STATUS REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print(f"  Total contacts:          {len(all_contacts)}")
    print(f"  Active leads:            {len(leads)}")
    print(f"  Replies detected:        {state.get('total_replies_detected', 0)}")
    print(f"  Leads in warm follow-up: {active_warm}")
    print(f"  Demo line callers:       {len(state.get('demo_callers', {}))}")
    print(f"  Secret shopper emails:   {state.get('total_secret_shopper', 0)}")
    print(f"  Weather emails:          {state.get('total_weather_emails', 0)}")
    print(f"  Total emails sent:       {state.get('total_emails_sent', 0)}")
    print(f"  War room alerts:         {state.get('total_alerts_sent', 0)}")
    print(f"  Season:                  {get_season()}")
    print(f"  Last reply check:        {state.get('last_reply_check', 'Never')}")
    print("=" * 50 + "\n")


# ===================================================
# MAIN
# ===================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "monitor":
        replies = monitor_replies()
        print(f"\n{len(replies)} new replies detected.")
    elif cmd == "followup":
        count = send_warm_followups()
        print(f"\nSent {count} warm follow-ups.")
    elif cmd == "pipeline":
        moved = update_pipeline()
        print(f"\nFlagged {moved} leads for stage changes.")
    elif cmd == "report":
        report = send_daily_report()
        print(report)
    elif cmd == "status":
        print_status()
    elif cmd == "all":
        log("=== MAX v3: Full cycle ===")
        monitor_replies()
        send_warm_followups()
        update_pipeline()
        send_daily_report()
        log("=== MAX v3: Full cycle complete ===")
        ntfy(NTFY_OPS_TOPIC,
             "Max v3 completed full cycle",
             f"All tasks done: monitor + follow-ups + pipeline + report.\nTime: {datetime.now().strftime('%I:%M %p')}",
             tags="white_check_mark")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    _cmd = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    try:
        main()
        ntfy(NTFY_CALLS_TOPIC,
             f"Max finished: {_cmd}",
             f"Max engine completed '{_cmd}' at {datetime.now().strftime('%I:%M %p')}",
             tags="white_check_mark")
    except Exception as _exc:
        import traceback
        _tb = traceback.format_exc()
        log(f"CRASH in max-engine {_cmd}: {_exc}")
        ntfy(NTFY_CALLS_TOPIC,
             f"Max CRASHED: {_cmd}",
             f"Command: {_cmd}\nError: {_exc}\n\n{_tb[-500:]}",
             priority="high", tags="rotating_light")
        raise
