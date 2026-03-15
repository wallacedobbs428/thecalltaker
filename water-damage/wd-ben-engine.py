#!/usr/bin/env python3
"""
WD-BEN — Water Damage Lead Intelligence + Conversion Engine
Feb 22, 2026

Intelligence work for water damage leads: weather-aware briefings, lead scoring
tuned for restoration companies, re-engagement with water damage angles,
SMS when A2P approves, morning + evening summaries.

Usage:
  python3 wd-ben-engine.py morning     # Weather-aware briefing (7am)
  python3 wd-ben-engine.py sms         # SMS blasts when A2P approves (1pm)
  python3 wd-ben-engine.py reengage    # Re-engage warm leads who ghosted (2pm)
  python3 wd-ben-engine.py score       # Enhanced lead scoring (3pm)
  python3 wd-ben-engine.py evening     # Evening summary (9pm)
  python3 wd-ben-engine.py status      # Print status
  python3 wd-ben-engine.py all         # Run all tasks
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

NTFY_OPS_TOPIC = "tct-xK9mW4vR7pLd"
NTFY_WAR_TOPIC = "tct-warroom-Kx7mN9pQ"

DEMO_LINE = "(615) 784-5747"
FROM_EMAIL = "wallacemdobbs@icloud.com"
SMS_PHONE = "+16156539004"

WD_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(WD_DIR, "wd-ben-state.json")
LOG_FILE = os.path.join(WD_DIR, "wd-ben-log.txt")

# WD-Max's state file — Ben reads it for coordination
WD_MAX_STATE_FILE = os.path.join(WD_DIR, "wd-max-state.json")


# ===================================================
# SEASONAL ENGINE — Water Damage
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


def get_seasonal_context():
    season = get_season()
    context = {
        "spring": "Spring storms = flood season. Restoration companies are getting slammed with emergency calls. Every missed call is a $5,000+ job lost.",
        "summer": "Hurricane season + summer storms. Emergency water damage calls spike overnight. The company that answers first gets the insurance claim.",
        "fall": "Fall storms and early freezes bring pipe bursts. Emergency calls come when you least expect them. Restoration owners need 24/7 coverage.",
        "winter": "Frozen pipe season. Pipes burst at 3am, water pouring through ceilings. Every missed call is a $5,000-$10,000 job walking to the competitor.",
    }
    return context.get(season, context["winter"])


# ===================================================
# WEATHER ENGINE
# ===================================================

def get_weather(city):
    if not city:
        return None
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=%t+%C"
        req = Request(url, headers={"User-Agent": "WDBenEngine/1.0"})
        with urlopen(req, timeout=5) as resp:
            return resp.read().decode().strip()
    except:
        return None


def get_weather_temp(city):
    if not city:
        return None
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=%t"
        req = Request(url, headers={"User-Agent": "WDBenEngine/1.0"})
        with urlopen(req, timeout=5) as resp:
            temp_str = resp.read().decode().strip()
            temp_str = temp_str.replace("°F", "").replace("°C", "").replace("+", "")
            return int(temp_str)
    except:
        return None


def get_weather_conditions(city):
    if not city:
        return None
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=%C"
        req = Request(url, headers={"User-Agent": "WDBenEngine/1.0"})
        with urlopen(req, timeout=5) as resp:
            return resp.read().decode().strip().lower()
    except:
        return None


# ===================================================
# RE-ENGAGEMENT TEMPLATES — Water Damage Specific
# ===================================================

REENGAGE_EMAILS = {
    "winter": {
        "subject": "frozen pipes don't wait for voicemail",
        "body": """<p>Hey {{firstName}},</p>
<p>We connected a while back about The Call Taker for {{companyName}}. Wanted to circle back with something timely.</p>
<p>It's frozen pipe season. When a pipe bursts at 3am and water is pouring through the ceiling, the homeowner calls once. Voicemail? They call the next restoration company.</p>
<p>That's a $5,000-$10,000 job — extraction, dry-out, rebuild, insurance claim — all going to your competitor because nobody answered the phone.</p>
<p>The Call Taker answers in under 2 seconds. 24/7. Even Christmas morning. $497/mo, no contracts.</p>
<p>Still worth a listen: <strong>(615) 784-5747</strong></p>
<p>— Wallace</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>""",
    },
    "spring": {
        "subject": "storm season is about to hit {{companyName}} hard",
        "body": """<p>Hey {{firstName}},</p>
<p>We talked a while back about The Call Taker. Spring storm season is here — flash floods, basement flooding, roof leaks.</p>
<p>When every homeowner in {city} calls about water damage at the same time, how many calls go to voicemail? Each one is a $3,000-$8,000+ job walking to the restoration company that picked up first.</p>
<p>The Call Taker handles every call — answers in 2 seconds, gets the emergency details, dispatches to you. $497/mo.</p>
<p>Hear it: <strong>(615) 784-5747</strong></p>
<p>— Wallace</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>""",
    },
    "summer": {
        "subject": "hurricane season is here — are you catching every call?",
        "body": """<p>Hey {{firstName}},</p>
<p>Hurricane season is here. When storms hit, emergency water damage calls spike overnight. {{companyName}}'s phone is going to be ringing nonstop.</p>
<p>But what about the calls at 2am? The overflow? The ones that hit voicemail? Each missed call is a $5,000+ insurance job going to your competitor.</p>
<p>The Call Taker catches every emergency call. 24/7. No voicemail. No missed revenue.</p>
<p>$497/mo. Cancel anytime. Demo: <strong>(615) 784-5747</strong></p>
<p>— Wallace</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>""",
    },
    "fall": {
        "subject": "freeze warnings are coming — pipe burst season",
        "body": """<p>Hey {{firstName}},</p>
<p>We connected earlier this year about The Call Taker for {{companyName}}. Freeze warnings are starting — pipe burst season is weeks away.</p>
<p>When pipes freeze and burst at midnight, the homeowner calls the first restoration company they find. Voicemail? They call your competitor. That's a $5,000+ job gone.</p>
<p>The Call Taker makes sure {{companyName}} always answers. $497/mo, no contracts, 48-hour setup.</p>
<p>Hear it live: <strong>(615) 784-5747</strong></p>
<p>— Wallace</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>""",
    },
}

SMS_TEMPLATES = [
    "Hey {{firstName}}, quick Q — when a homeowner calls {{companyName}} at 2am with a flooded basement, what happens? The Call Taker answers 24/7 so you never lose a $5K+ job to voicemail. Hear it: (615) 784-5747. Reply STOP to opt out",
    "{{firstName}} — 85% of callers who hit voicemail never call back. For water damage, that's $3K-$8K per missed call. The Call Taker fixes that for {{companyName}}. Demo: (615) 784-5747. Reply STOP to opt out",
    "{{firstName}}, water damage gets worse every minute. If {{companyName}} misses the call, the homeowner calls your competitor — and they get the extraction, dry-out, AND insurance claim. Fix it: (615) 784-5747. Reply STOP to opt out",
]


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] WD-BEN: {msg}"
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
        "User-Agent": "WDBenEngine/1.0 TheCallTaker",
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
        "contacts_reengaged": [],
        "contacts_smsed": [],
        "lead_scores": {},
        "total_emails_sent": 0,
        "total_sms_sent": 0,
        "total_alerts": 0,
    }


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def load_wd_max_state():
    if os.path.exists(WD_MAX_STATE_FILE):
        try:
            with open(WD_MAX_STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {}


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
    """Filter to water-damage tagged leads ONLY."""
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


def send_sms(contact_id, message):
    body = {
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    }
    resp = ghl_request("POST", "/conversations/messages", body, version="2021-04-15")
    if resp:
        log(f"SMS sent to {contact_id}")
        return True
    return False


def personalize(template, contact):
    first = contact.get("firstName", contact.get("name", "there"))
    company = contact.get("companyName", "your company")
    text = template.replace("{{firstName}}", first or "there")
    text = text.replace("{{companyName}}", company or "your company")
    return text


def has_inbound_reply(contact_id):
    convos = get_conversations(contact_id)
    for convo in convos:
        messages = get_messages(convo.get("id", ""))
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            if msg.get("direction") == "inbound":
                body = msg.get("body", msg.get("message", ""))
                if body and body.strip().upper() not in ["STOP", "UNSUBSCRIBE"]:
                    return True
    return False


def is_business_hours():
    now = datetime.utcnow() - timedelta(hours=6)  # CST
    if now.hour < 9 or now.hour >= 17:
        return False
    if now.weekday() >= 5:
        return False
    return True


def days_since(date_str):
    if not date_str:
        return 999
    try:
        dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00").split("+")[0].split("T")[0])
        return (datetime.now() - dt).days
    except:
        return 999


def score_lead(contact, max_state):
    """Lead scoring tuned for water damage / restoration companies."""
    score = 3  # Base score

    # Has email = +1
    if contact.get("email"):
        score += 1

    # Has phone = +1
    if contact.get("phone"):
        score += 1

    # Has company name = +1
    if contact.get("companyName"):
        score += 1

    tags = [t.lower() for t in contact.get("tags", [])]

    # Water damage tagged = +1
    if "water-damage" in tags or "restoration" in tags:
        score += 1

    # Emergency services / 24-7 in name or tags = +1 (they understand the need)
    company_lower = contact.get("companyName", "").lower()
    if "emergency" in company_lower or "24/7" in company_lower or "24-7" in company_lower:
        score += 1

    # Voicemail confirmed = +2 (proven problem)
    if "voicemail-confirmed" in tags:
        score += 2

    # Demo booked or called = +2
    if "demo-booked" in tags or "demo-called" in tags:
        score += 2

    # Replied to outreach (from WD-Max warm followups)
    warm = max_state.get("warm_followups", {})
    cid = contact.get("id")
    if cid in warm:
        score += 2

    # Demo line caller = +2
    demo_callers = max_state.get("demo_callers", {})
    if cid in demo_callers:
        score += 2

    # Weather urgency — rain/storms/freeze in their city
    city = contact.get("city", "")
    if city:
        conditions = get_weather_conditions(city)
        if conditions:
            rain_keywords = ["rain", "storm", "thunder", "flood"]
            if any(kw in conditions for kw in rain_keywords):
                score += 1  # Active weather = more pain

        temp = get_weather_temp(city)
        if temp is not None and temp <= 32:
            score += 1  # Freeze = pipe burst risk

    return min(score, 10)


# ===================================================
# CORE TASKS
# ===================================================

def morning_briefing():
    """7am: Weather-aware briefing for water damage campaign."""
    log("=== WD-BEN: Morning Briefing ===")
    contacts = get_all_contacts()
    leads = get_water_damage_leads(contacts)
    state = load_state()
    max_state = load_wd_max_state()

    lead_count = len(leads)

    weather_info = get_weather("Nashville") or "unable to fetch"

    warm = max_state.get("warm_followups", {})
    active_warm = sum(1 for v in warm.values() if v.get("followup_count", 0) < 3)
    demo_callers = len(max_state.get("demo_callers", {}))
    secret_shoppers = max_state.get("total_secret_shopper", 0)

    now = datetime.utcnow() - timedelta(hours=6)
    day_name = now.strftime("%A")

    briefing = f"""WATER DAMAGE BRIEFING — {now.strftime('%b %d, %Y')} ({day_name})

WEATHER: Nashville — {weather_info}
SEASON: {get_season().upper()} — {get_seasonal_context()}

WATER DAMAGE PIPELINE:
  Active WD leads: {lead_count}
  Leads in warm follow-up: {active_warm}
  Demo line callers: {demo_callers}
  Secret shopper emails sent: {secret_shoppers}

TODAY'S WD GAME PLAN:
  WD-Max: Catching replies every 30min + warm follow-ups at 9am
  WD-Ben: SMS at 1pm, re-engagement at 2pm, lead scoring at 3pm

YOUR MOVES TODAY:
  1. Check ntfy for WD reply alerts — respond within 1 hour
  2. Secret shop 3-5 restoration companies after 6pm
     (call, say "my basement is flooding", confirm voicemail, tag in GHL)
  3. WD-Ben scores all WD leads at 3pm — check war room for hottest ones

KEY REMINDER: Water damage avg job = $3,000-$8,000+ (insurance claims)
Revenue per missed call is 10x higher than HVAC. These leads are gold."""

    ntfy(NTFY_OPS_TOPIC,
         f"WD Morning Briefing — {now.strftime('%b %d')}",
         briefing,
         priority="high",
         tags="droplet,sunrise,clipboard")

    log("WD morning briefing sent.")
    return briefing


def sms_outreach():
    """1pm: SMS to water damage leads with phone numbers."""
    log("=== WD-BEN: SMS Outreach ===")

    if not is_business_hours():
        log("Outside business hours. Skipping SMS.")
        return 0

    state = load_state()
    smsed = set(state.get("contacts_smsed", []))
    contacts = get_all_contacts()
    leads = get_water_damage_leads(contacts)
    sent = 0
    template_idx = 0

    for contact in leads:
        cid = contact.get("id")
        phone = contact.get("phone")

        if not phone or cid in smsed:
            continue

        if contact.get("dnd"):
            continue

        template = SMS_TEMPLATES[template_idx % len(SMS_TEMPLATES)]
        template_idx += 1
        message = personalize(template, contact)

        if send_sms(cid, message):
            sent += 1
            smsed.add(cid)
            state["total_sms_sent"] = state.get("total_sms_sent", 0) + 1
            log(f"  SMS #{sent} to {contact.get('firstName', 'Unknown')}")
        else:
            if sent == 0:
                log("SMS failed on first attempt — A2P likely not approved. Stopping.")
                break

        time.sleep(2)
        if sent >= 15:
            log("Hit daily SMS limit (15). Stopping.")
            break

    if sent > 0:
        ntfy(NTFY_WAR_TOPIC,
             f"WD-Ben sent {sent} SMS messages!",
             f"A2P working! {sent} texts sent to water damage leads.",
             priority="high",
             tags="droplet,iphone,zap")

    state["contacts_smsed"] = list(smsed)
    save_state(state)
    return sent


def reengage_warm_leads():
    """2pm: Re-engage water damage leads who replied then ghosted."""
    log("=== WD-BEN: Warm Re-engagement ===")

    if not is_business_hours():
        log("Outside business hours. Skipping.")
        return 0

    state = load_state()
    max_state = load_wd_max_state()
    reengaged = set(state.get("contacts_reengaged", []))

    warm = max_state.get("warm_followups", {})
    contacts = get_all_contacts()
    contact_map = {c["id"]: c for c in contacts}
    sent = 0
    season = get_season()

    for cid, data in warm.items():
        if cid in reengaged:
            continue

        if data.get("followup_count", 0) < 3:
            continue

        contact = contact_map.get(cid)
        if not contact:
            continue

        tags = [t.lower() for t in contact.get("tags", [])]
        # Only water-damage leads
        if "water-damage" not in tags:
            continue
        if "customer" in tags or "active-client" in tags:
            continue

        email = contact.get("email")
        if not email:
            continue

        template = REENGAGE_EMAILS.get(season, REENGAGE_EMAILS["winter"])
        subject = personalize(template["subject"], contact)
        body = personalize(template["body"], contact)

        if send_email(cid, subject, body):
            sent += 1
            reengaged.add(cid)
            state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
            log(f"  Re-engaged WD lead: {contact.get('firstName', 'Unknown')} ({season} angle)")

        time.sleep(3)
        if sent >= 10:
            log("Hit re-engagement limit (10). Stopping.")
            break

    if sent > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"WD-Ben re-engaged {sent} warm leads",
             f"Water damage {season} angle sent to {sent} leads who replied then ghosted.",
             tags="droplet,recycle,envelope")

    state["contacts_reengaged"] = list(reengaged)
    save_state(state)
    log(f"WD re-engaged {sent} warm leads.")
    return sent


def score_all_leads():
    """3pm: Lead scoring tuned for water damage / restoration."""
    log("=== WD-BEN: Lead Scoring ===")
    state = load_state()
    max_state = load_wd_max_state()
    contacts = get_all_contacts()
    leads = get_water_damage_leads(contacts)

    scores = {}
    hot_leads = []

    for contact in leads:
        cid = contact.get("id")
        score = score_lead(contact, max_state)
        scores[cid] = score

        if score >= 8:
            hot_leads.append({
                "name": contact.get("firstName", "Unknown"),
                "company": contact.get("companyName", "Unknown"),
                "email": contact.get("email", ""),
                "phone": contact.get("phone", ""),
                "city": contact.get("city", ""),
                "score": score,
                "tags": contact.get("tags", []),
            })

    log(f"Scored {len(leads)} WD leads. {len(hot_leads)} scored 8+.")

    if hot_leads:
        hot_list = "\n".join([
            f"  {h['score']}/10 — {h['name']} ({h['company']}) {h['phone'] or h['email']}"
            + (f" [VOICEMAIL]" if "voicemail-confirmed" in [t.lower() for t in h.get('tags', [])] else "")
            for h in sorted(hot_leads, key=lambda x: x['score'], reverse=True)[:10]
        ])
        ntfy(NTFY_WAR_TOPIC,
             f"{len(hot_leads)} HOT water damage leads scored 8+",
             f"Top WD leads to call TODAY:\n\n{hot_list}\n\nWater damage leads = $3K-$8K+ per job. Call voicemail-confirmed ones first!",
             priority="high",
             tags="droplet,fire,telephone_receiver")
        state["total_alerts"] = state.get("total_alerts", 0) + 1

    state["lead_scores"] = scores
    save_state(state)
    return len(hot_leads)


def evening_summary():
    """9pm: Evening summary for water damage campaign."""
    log("=== WD-BEN: Evening Summary ===")
    state = load_state()
    max_state = load_wd_max_state()
    contacts = get_all_contacts()
    leads = get_water_damage_leads(contacts)

    lead_count = len(leads)

    ben_emails = state.get("total_emails_sent", 0)
    ben_sms = state.get("total_sms_sent", 0)
    ben_reengaged = len(state.get("contacts_reengaged", []))
    hot_count = sum(1 for s in state.get("lead_scores", {}).values() if s >= 8)

    max_replies = max_state.get("total_replies_detected", 0)
    max_followups = max_state.get("total_followups_sent", 0)
    max_demo_calls = len(max_state.get("demo_callers", {}))
    max_secret_shopper = max_state.get("total_secret_shopper", 0)
    max_weather = max_state.get("total_weather_emails", 0)

    summary = f"""WD EVENING REPORT — {datetime.now().strftime('%b %d, %Y')}

WATER DAMAGE PIPELINE:
  Active WD leads: {lead_count}
  Hot leads (8+): {hot_count}

WD-MAX STATS:
  Replies caught: {max_replies}
  Warm follow-ups sent: {max_followups}
  Demo line callers: {max_demo_calls}
  Secret shopper emails: {max_secret_shopper}
  Weather-triggered emails: {max_weather}

WD-BEN STATS:
  Re-engagements sent: {ben_reengaged}
  SMS sent: {ben_sms}
  Total emails: {ben_emails}

SEASON: {get_season().upper()} — all water damage angles tuned for {get_season()}
INDUSTRY: Water Damage / Restoration (avg job $3,000-$8,000+)

TOMORROW:
  7:00 AM — WD-Ben: Morning briefing
  9:00 AM — WD-Max: Warm follow-ups
  1:00 PM — WD-Ben: SMS (if A2P)
  2:00 PM — WD-Ben: Re-engage warm leads
  3:00 PM — WD-Ben: Lead scoring
  + WD-Max catches WD replies every 30 min

The water damage team never stops. Good night."""

    ntfy(NTFY_OPS_TOPIC,
         f"WD Evening Report — {datetime.now().strftime('%b %d')}",
         summary,
         tags="droplet,moon,clipboard")

    log("WD evening summary sent.")
    return summary


def print_status():
    state = load_state()
    max_state = load_wd_max_state()
    contacts = get_all_contacts()
    leads = get_water_damage_leads(contacts)
    hot = sum(1 for s in state.get("lead_scores", {}).values() if s >= 8)

    print("\n" + "=" * 50)
    print("  WD-BEN — WATER DAMAGE STATUS REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print(f"  Water damage leads:    {len(leads)}")
    print(f"  WD-Ben emails sent:    {state.get('total_emails_sent', 0)}")
    print(f"  WD-Ben SMS sent:       {state.get('total_sms_sent', 0)}")
    print(f"  Re-engaged:            {len(state.get('contacts_reengaged', []))}")
    print(f"  Hot leads (8+):        {hot}")
    print(f"  Season:                {get_season()}")
    print(f"  WD-Max replies caught: {max_state.get('total_replies_detected', 0)}")
    print(f"  WD-Max demo callers:   {len(max_state.get('demo_callers', {}))}")
    print("=" * 50 + "\n")


# ===================================================
# MAIN
# ===================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "morning":
        morning_briefing()
    elif cmd == "sms":
        sms_outreach()
    elif cmd == "reengage":
        reengage_warm_leads()
    elif cmd == "score":
        score_all_leads()
    elif cmd == "evening":
        evening_summary()
    elif cmd == "status":
        print_status()
    elif cmd == "all":
        log("=== WD-BEN: Full cycle ===")
        morning_briefing()
        sms_outreach()
        reengage_warm_leads()
        score_all_leads()
        evening_summary()
        log("=== WD-BEN: Full cycle complete ===")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
