#!/usr/bin/env python3
"""
WD-MAX — Water Damage Reply Catcher + Follow-Up Machine
Feb 22, 2026

Monitors GHL for replies from water-damage tagged contacts ONLY.
Sends follow-ups with water damage angles (pipe bursts, flooding, storm damage).
Detects demo line calls, triggers secret shopper emails, weather-triggered outreach.

Usage:
  python3 wd-max-engine.py monitor    # Catch replies + demo calls + secret shopper (every 30 min)
  python3 wd-max-engine.py followup   # Warm follow-ups for engaged leads (daily 9am)
  python3 wd-max-engine.py pipeline   # Move leads through stages (daily midnight)
  python3 wd-max-engine.py report     # Daily summary to ntfy (daily 8pm)
  python3 wd-max-engine.py status     # Print current stats
  python3 wd-max-engine.py all        # Run all tasks
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

NTFY_OPS_TOPIC = "tct-xK9mW4vR7pLd"
NTFY_WAR_TOPIC = "tct-warroom-Kx7mN9pQ"

DEMO_LINE = "(615) 784-5747"
DEMO_LINE_NUMBER = "+16157845747"
DEMO_URL = "https://thecalltaker.com/demo.html"
CALENDAR_URL = "https://thecalltaker.com/demo.html"
FROM_EMAIL = "wallacemdobbs@icloud.com"
FROM_NAME = "Wallace Dobbs"

WD_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(WD_DIR, "wd-max-state.json")
LOG_FILE = os.path.join(WD_DIR, "wd-max-log.txt")

# ===================================================
# SEASONAL ENGINE — Water Damage Specific
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
        "spring": "Spring storms are here — flash flooding, burst pipes from thawing ground, and basement floods. Every missed call is a $5,000+ job walking out the door.",
        "summer": "Hurricane season and summer storms mean emergency calls spike overnight. When a homeowner's house is flooding at 2am, voicemail isn't an option.",
        "fall": "Fall storms and early freezes bring pipe bursts and water damage. The calls come when you least expect them — and the company that answers first wins.",
        "winter": "Frozen pipes burst at 3am. Water is pouring through the ceiling. The homeowner calls once — voicemail means they call your competitor and you lose a $5,000+ job.",
    }
    return urgency.get(season, urgency["winter"])


# ===================================================
# WEATHER ENGINE — Water Damage Triggers
# ===================================================

def get_weather(city):
    if not city:
        return None
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=%t"
        req = Request(url, headers={"User-Agent": "WDMaxEngine/1.0"})
        with urlopen(req, timeout=5) as resp:
            temp_str = resp.read().decode().strip()
            temp_str = temp_str.replace("°F", "").replace("°C", "").replace("+", "")
            return int(temp_str)
    except:
        return None


def get_weather_conditions(city):
    """Get weather conditions (rain, storms, etc.) for water damage triggers."""
    if not city:
        return None
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=%C"
        req = Request(url, headers={"User-Agent": "WDMaxEngine/1.0"})
        with urlopen(req, timeout=5) as resp:
            return resp.read().decode().strip().lower()
    except:
        return None


def get_weather_angle(city):
    """Return a weather-triggered email angle for water damage."""
    temp = get_weather(city)
    conditions = get_weather_conditions(city)

    # Rain/storm triggers — most relevant for water damage
    if conditions:
        rain_keywords = ["rain", "shower", "storm", "thunder", "drizzle", "overcast"]
        if any(kw in conditions for kw in rain_keywords):
            return f"It's raining in {city} right now. When storms hit, emergency water damage calls spike. The restoration company that answers first gets the $5,000+ job."

    # Freeze triggers — pipe bursts
    if temp is not None and temp <= 32:
        return f"It's {temp}°F in {city} right now. Frozen pipes are bursting across the city. When water starts pouring at 3am, your customer calls once. Voicemail means they call your competitor."

    # Heat + humidity — mold risk
    if temp is not None and temp >= 85:
        return f"Temps hitting {temp}°F in {city} — high humidity means mold starts in 24-48 hours after any water intrusion. Speed is everything. Are you catching every call?"

    return None


# ===================================================
# WARM FOLLOW-UP TEMPLATES — Water Damage Specific
# ===================================================

WARM_FOLLOWUP_DAY2 = {
    "subject": "great hearing from you",
    "body": """<p>Hey {{firstName}},</p>
<p>Thanks for getting back to me — I appreciate it.</p>
<p>Just to recap what The Call Taker does for {{companyName}}:</p>
<ul>
<li>Answers every call 24/7 — no voicemail, no missed emergency jobs</li>
<li>Captures the emergency details (flooding, pipe burst, storm damage) and dispatches to you immediately</li>
<li>Every minute counts in water damage — your phone should never go unanswered</li>
<li>Set up in 48 hours, $497/mo, cancel anytime</li>
</ul>
<p>{{seasonal}}</p>
<p>Want to hear it live? Call the demo line right now: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}

WARM_FOLLOWUP_DAY5 = {
    "subject": "the demo line is live — hear how we handle a 2am flood call",
    "body": """<p>Hey {{firstName}},</p>
<p>Quick reminder — you can hear exactly what your customers would experience by calling our demo line:</p>
<p style="font-size:18px;font-weight:bold;text-align:center;">(615) 784-5747</p>
<p>Tell it you have a flooded basement at 2am. Watch how it handles the emergency — gets the address, the situation details, and dispatches immediately. No voicemail. No hold music. No missed jobs.</p>
<p>Or grab a 15-minute slot: <a href="https://thecalltaker.com/demo.html">Book a Demo</a></p>
<p>— Wallace</p>""",
}

WARM_FOLLOWUP_DAY8 = {
    "subject": "last note from me",
    "body": """<p>Hey {{firstName}},</p>
<p>Last follow-up — I respect your time.</p>
<p>{{seasonal}}</p>
<p>The average water damage job is $3,000-$8,000. Missing just 2 calls a week means $24,000-$64,000/month going to your competitor.</p>
<p>The Call Taker is $497/mo for {{companyName}} to never miss another emergency call. No contracts. Cancel anytime. Set up in 48 hours.</p>
<p>If the timing isn't right, no worries. But if you ever want to hear it: <strong>(615) 784-5747</strong></p>
<p>Good luck out there, {{firstName}}.</p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}

# ===================================================
# SECRET SHOPPER EMAIL — Water Damage Version
# ===================================================

SECRET_SHOPPER_EMAIL = {
    "subject": "I called {{companyName}} at 11pm pretending my basement was flooding",
    "body": """<p>Hey {{firstName}},</p>
<p>I called {{companyName}} at 11pm last night pretending I had a flooded basement. I got your voicemail.</p>
<p>I'm not a customer, so no harm done. But here's what would happen if I were:</p>
<ul>
<li>I'd panic and call the next restoration company</li>
<li>That company gets the extraction, dry-out, rebuild, AND insurance claim — easily $5,000-$10,000+</li>
<li>And water damage gets worse every minute I wait. Mold starts in 24-48 hours.</li>
</ul>
<p>62% of callers who hit voicemail never call back. They call your competitor instead.</p>
<p>The Call Taker would have answered that call in under 2 seconds, gotten my address, asked what's happening, and dispatched the emergency to your phone immediately. 24/7.</p>
<p>Hear exactly what your callers would experience: <strong>(615) 784-5747</strong></p>
<p>$497/mo. No contracts. Set up in 48 hours.</p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}

# ===================================================
# DEMO LINE FOLLOW-UP — Water Damage Version
# ===================================================

DEMO_FOLLOWUP_EMAIL = {
    "subject": "you just tried the demo line",
    "body": """<p>Hey {{firstName}},</p>
<p>I saw you just called our demo line — thanks for checking it out!</p>
<p>What you heard is exactly what your customers would experience when they call {{companyName}} at 2am with a flooded basement, a burst pipe, or storm damage.</p>
<p>Every emergency call answered. Every job captured. Every detail dispatched to you. 24/7. No voicemail. No missed revenue.</p>
<p>The average water damage job is $3,000-$8,000. How many are you losing to voicemail each month?</p>
<p>Want to set it up for {{companyName}}? Takes 48 hours and $497/mo — no contracts, cancel anytime.</p>
<p>Grab a quick slot: <a href="https://thecalltaker.com/demo.html">Book a Demo</a></p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}

# ===================================================
# WEATHER-TRIGGERED EMAIL — Water Damage Version
# ===================================================

WEATHER_EMAIL = {
    "subject": "{{companyName}} — emergency calls are about to spike",
    "body": """<p>Hey {{firstName}},</p>
<p>{{weather_angle}}</p>
<p>The Call Taker answers every call for {{companyName}} 24/7 — captures the emergency, dispatches to you immediately. No voicemail. No missed jobs. No revenue lost.</p>
<p>Water damage gets worse every minute. Your phone should never go unanswered.</p>
<p>$497/mo. No contracts. Hear it live: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
}


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] WD-MAX: {msg}"
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
        "User-Agent": "WDMaxEngine/1.0 TheCallTaker",
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
        safe_title = title.encode("ascii", "replace").decode("ascii")
        headers = {"Title": safe_title, "Priority": priority, "Content-Type": "text/plain; charset=utf-8"}
        if tags:
            headers["Tags"] = tags
        req = Request(url, data=msg.encode("utf-8"), headers=headers, method="POST")
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
        "warm_followups": {},
        "demo_callers": {},
        "secret_shopper_sent": [],
        "weather_sent": {},
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


def get_water_damage_leads(contacts):
    """Filter to water-damage tagged leads ONLY — not HVAC, not customers."""
    leads = []
    for c in contacts:
        tags = [t.lower() for t in c.get("tags", [])]
        if "water-damage" in tags and "customer" not in tags and "active-client" not in tags:
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
    log("=== WD-MAX: Monitor ===")
    state = load_state()
    known = set(state.get("known_reply_ids", []))
    all_contacts = get_all_contacts()
    leads = get_water_damage_leads(all_contacts)
    new_replies = []

    log(f"Scanning {len(leads)} water damage leads for replies, demo calls, secret shopper tags...")

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
                     f"WD Secret Shopper: {name} ({company})",
                     f"Voicemail confirmed for {company} (WATER DAMAGE). WD-Max sent the devastating 'I called pretending my basement was flooding' email.\n\nThis converts 3x better than cold email.",
                     priority="high",
                     tags="droplet,fire")
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

                # ── DEMO LINE CALL ──
                if direction == "inbound" and msg_type in ["CALL", "call", "Call"]:
                    known.add(msg_id)
                    if cid not in state.get("demo_callers", {}):
                        state.setdefault("demo_callers", {})[cid] = {
                            "detected_date": datetime.now().isoformat(),
                            "followed_up": False,
                        }
                        subject = personalize(DEMO_FOLLOWUP_EMAIL["subject"], contact)
                        body = personalize(DEMO_FOLLOWUP_EMAIL["body"], contact)
                        if send_email(cid, subject, body):
                            state["demo_callers"][cid]["followed_up"] = True
                            state["total_demo_followups"] = state.get("total_demo_followups", 0) + 1
                            state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
                            log(f"  DEMO CALL follow-up sent to {name}")

                        ntfy(NTFY_WAR_TOPIC,
                             f"WD DEMO CALL: {name} ({company}) called the demo line!",
                             f"WATER DAMAGE lead {name} from {company} just called the demo line!\nPhone: {phone}\n\nWD-Max sent an immediate follow-up. Call them back NOW!",
                             priority="urgent",
                             tags="droplet,fire,rotating_light")
                        state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1
                    continue

                # ── INBOUND REPLY ──
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

                    if cid not in state.get("warm_followups", {}):
                        state.setdefault("warm_followups", {})[cid] = {
                            "replied_date": datetime.now().isoformat(),
                            "followup_count": 0,
                            "last_followup": None,
                        }

        time.sleep(0.5)

    # ── Alert war room for new replies ──
    if new_replies:
        log(f"Found {len(new_replies)} new water damage replies!")
        state["total_replies_detected"] = state.get("total_replies_detected", 0) + len(new_replies)

        for reply in new_replies:
            ntfy(NTFY_WAR_TOPIC,
                 f"WD REPLY: {reply['name']} ({reply['company']})",
                 f"WATER DAMAGE lead replied!\nMessage: {reply['message']}\n\nPhone: {reply['phone']}\nType: {reply['type']}\n\nRespond personally ASAP — restoration leads are time-sensitive!",
                 priority="high",
                 tags="droplet,rotating_light,speech_balloon")
            state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1
    else:
        log("No new water damage replies.")

    # ── WEATHER CHECK: Rain/storms/freeze triggers ──
    weather_sent_today = 0
    weather_state = state.get("weather_sent", {})
    for contact in leads[:50]:
        cid = contact.get("id")
        city = contact.get("city", "")
        if not city or weather_sent_today >= 5:
            continue
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
    """Daily 9am: Send warm follow-ups to water damage leads who replied."""
    log("=== WD-MAX: Warm Follow-ups ===")
    state = load_state()
    warm = state.get("warm_followups", {})
    all_contacts = get_all_contacts()
    contact_map = {c["id"]: c for c in all_contacts}
    sent_count = 0

    for cid, data in warm.items():
        contact = contact_map.get(cid)
        if not contact:
            continue

        tags = [t.lower() for t in contact.get("tags", [])]
        # Only process water-damage tagged contacts
        if "water-damage" not in tags:
            continue
        if "customer" in tags or "active-client" in tags:
            continue

        replied_date = data.get("replied_date")
        followup_count = data.get("followup_count", 0)

        days_since_reply = days_since(replied_date)

        if followup_count >= 3:
            continue

        if followup_count == 0 and days_since_reply >= 2:
            template = WARM_FOLLOWUP_DAY2
        elif followup_count == 1 and days_since_reply >= 5:
            template = WARM_FOLLOWUP_DAY5
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

    log(f"WD warm follow-ups complete. Sent {sent_count}.")
    if sent_count > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"WD-Max sent {sent_count} warm follow-ups",
             f"Water damage follow-ups sent to {sent_count} leads who replied.\nRestoration leads convert fast when you stay on them.",
             tags="droplet,envelope")
    return sent_count


def update_pipeline():
    """Daily midnight: Move water damage leads through pipeline."""
    log("=== WD-MAX: Pipeline Update ===")
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
        contact_id = opp.get("contact", {}).get("id", opp.get("contactId"))
        current_stage = opp.get("pipelineStageId", "")

        if not contact_id:
            continue

        name = opp.get("contact", {}).get("name", "Unknown")
        is_engaged = contact_id in warm or contact_id in demo_callers
        if is_engaged and current_stage == CONTACTED_STAGE:
            log(f"  ENGAGED WD LEAD: {name} replied/called demo")
            ntfy(NTFY_WAR_TOPIC,
                 f"WD MOVE: {name} is engaged!",
                 f"Water damage lead {name} has replied or called the demo line.\nMove them to Engaged and follow up personally — restoration leads are time-sensitive!",
                 priority="high",
                 tags="droplet,fire,rotating_light")
            moved += 1
            state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1

        time.sleep(0.5)

    save_state(state)
    log(f"WD pipeline check complete. {moved} leads flagged.")
    return moved


def send_daily_report():
    """Daily 8pm: Water damage summary to ntfy."""
    log("=== WD-MAX: Daily Report ===")
    state = load_state()
    all_contacts = get_all_contacts()
    leads = get_water_damage_leads(all_contacts)

    warm = state.get("warm_followups", {})
    active_warm = sum(1 for v in warm.values() if v.get("followup_count", 0) < 3)

    report = f"""WD-MAX DAILY REPORT — {datetime.now().strftime('%b %d, %Y')}

WATER DAMAGE PIPELINE:
  Water damage leads: {len(leads)}

ENGAGEMENT:
  Replies detected (all time): {state.get('total_replies_detected', 0)}
  Leads in warm follow-up: {active_warm}
  Demo line callers: {len(state.get('demo_callers', {}))}
  Secret shopper emails sent: {state.get('total_secret_shopper', 0)}
  Weather-triggered emails: {state.get('total_weather_emails', 0)}

ACTIVITY:
  Warm follow-ups sent: {state.get('total_followups_sent', 0)}
  Demo call follow-ups: {state.get('total_demo_followups', 0)}
  Total emails sent by WD-Max: {state.get('total_emails_sent', 0)}
  War room alerts: {state.get('total_alerts_sent', 0)}
  Last reply check: {state.get('last_reply_check', 'Never')}

SEASON: {get_season().upper()} — water damage angles tuned for {get_season()}
INDUSTRY: Water Damage / Restoration (avg job $3,000-$8,000)

STATUS: WD-Max is active. Catching water damage replies every 30 min."""

    ntfy(NTFY_OPS_TOPIC,
         f"WD-Max Report — {datetime.now().strftime('%b %d')}",
         report,
         tags="droplet,clipboard")

    log("WD daily report sent.")
    return report


def print_status():
    state = load_state()
    all_contacts = get_all_contacts()
    leads = get_water_damage_leads(all_contacts)
    warm = state.get("warm_followups", {})
    active_warm = sum(1 for v in warm.values() if v.get("followup_count", 0) < 3)

    print("\n" + "=" * 50)
    print("  WD-MAX — WATER DAMAGE STATUS REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print(f"  Water damage leads:      {len(leads)}")
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
        print(f"\n{len(replies)} new water damage replies detected.")
    elif cmd == "followup":
        count = send_warm_followups()
        print(f"\nSent {count} warm follow-ups to water damage leads.")
    elif cmd == "pipeline":
        moved = update_pipeline()
        print(f"\nFlagged {moved} water damage leads for stage changes.")
    elif cmd == "report":
        report = send_daily_report()
        print(report)
    elif cmd == "status":
        print_status()
    elif cmd == "all":
        log("=== WD-MAX: Full cycle ===")
        monitor_replies()
        send_warm_followups()
        update_pipeline()
        send_daily_report()
        log("=== WD-MAX: Full cycle complete ===")
        ntfy(NTFY_OPS_TOPIC,
             "WD-Max completed full cycle",
             f"Water damage tasks done: monitor + follow-ups + pipeline + report.\nTime: {datetime.now().strftime('%I:%M %p')}",
             tags="droplet,white_check_mark")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
