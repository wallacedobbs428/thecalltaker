#!/usr/bin/env python3
"""
BEN v2 — The Call Taker's Lead Intelligence + Conversion Engine
Rebuilt Feb 18, 2026

Ben no longer sends cold emails. Instantly handles that on burner domains.
Ben now does INTELLIGENCE work: weather-aware briefings, enhanced lead scoring
with Google review signals, warm re-engagement for leads who ghosted after
replying, SMS when A2P approves, and evening summaries.

Usage:
  python3 ben-engine.py morning     # Weather-aware briefing (7am)
  python3 ben-engine.py sms         # SMS blasts when A2P approves (1pm)
  python3 ben-engine.py reengage    # Re-engage warm leads who ghosted (2pm)
  python3 ben-engine.py score       # Enhanced lead scoring + flag hot leads (3pm)
  python3 ben-engine.py evening     # Evening summary + tomorrow's plan (9pm)
  python3 ben-engine.py status      # Print Ben's status
  python3 ben-engine.py all         # Run all tasks
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

NTFY_OPS_TOPIC = "tct-sales-63uYsIT9"
NTFY_WAR_TOPIC = "tct-urgent-Hk9UOEZR"

DEMO_LINE = "(615) 784-5747"
FROM_EMAIL = "wallacemdobbs@icloud.com"
SMS_PHONE = "+16156539004"

BEN_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BEN_DIR, "ben-state.json")
LOG_FILE = os.path.join(BEN_DIR, "ben-log.txt")

# Max's state file — Ben reads it for coordination
MAX_STATE_FILE = os.path.join(os.path.dirname(BEN_DIR), "max", "max-state.json")


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


def get_seasonal_context():
    season = get_season()
    context = {
        "spring": "Spring AC season is ramping up — HVAC owners are getting slammed with install calls. Perfect time to pitch.",
        "summer": "Peak AC season. Phones ringing off the hook. Overflow calls going to voicemail. Our best selling season.",
        "fall": "Heating season prep. Smart owners are getting ready for furnace emergencies. Urgency is building.",
        "winter": "Furnace emergency season. After-hours calls are spiking. Every missed call is a $500+ emergency job lost.",
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
        req = Request(url, headers={"User-Agent": "BenEngine/2.0"})
        with urlopen(req, timeout=5) as resp:
            return resp.read().decode().strip()
    except:
        return None


def get_weather_temp(city):
    if not city:
        return None
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=%t"
        req = Request(url, headers={"User-Agent": "BenEngine/2.0"})
        with urlopen(req, timeout=5) as resp:
            temp_str = resp.read().decode().strip()
            temp_str = temp_str.replace("°F", "").replace("°C", "").replace("+", "")
            return int(temp_str)
    except:
        return None


# ===================================================
# RE-ENGAGEMENT TEMPLATES (for warm leads who ghosted)
# ===================================================

REENGAGE_EMAILS = {
    "winter": {
        "subject": "furnace emergencies don't wait for voicemail",
        "body": """<p>Hey {{firstName}},</p>
<p>We connected a little while back about The Call Taker for {{companyName}}. Just wanted to circle back with something timely.</p>
<p>It's peak heating season. When a furnace dies at midnight, your customer calls once. If voicemail answers, they call whoever picks up first.</p>
<p>The Call Taker answers in under 2 seconds. 24/7. Even Christmas morning. $497/mo, no contracts.</p>
<p>Still worth a listen: <strong>(615) 784-5747</strong></p>
<p>— Wallace</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>""",
    },
    "spring": {
        "subject": "AC season is about to hit {{companyName}}",
        "body": """<p>Hey {{firstName}},</p>
<p>We talked a while back about The Call Taker. Spring is here and AC season is coming fast.</p>
<p>When every homeowner calls about their AC at the same time, your team will be on jobs and the phone will go to voicemail. That's $350+ per missed call walking out the door.</p>
<p>The Call Taker handles the overflow — answers every call, books the job, texts you. $497/mo.</p>
<p>Hear it: <strong>(615) 784-5747</strong></p>
<p>— Wallace</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>""",
    },
    "summer": {
        "subject": "your phone is ringing off the hook right now",
        "body": """<p>Hey {{firstName}},</p>
<p>It's peak AC season and I know {{companyName}}'s phone is busy. Quick question — how many calls are going to voicemail this week?</p>
<p>The Call Taker catches every overflow call, gets the customer's info, and books the job. No voicemail. No lost revenue.</p>
<p>$497/mo. Set up in 48 hours. Cancel anytime.</p>
<p>Call the demo: <strong>(615) 784-5747</strong></p>
<p>— Wallace</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>""",
    },
    "fall": {
        "subject": "heating season is 30 days away",
        "body": """<p>Hey {{firstName}},</p>
<p>We connected earlier this year about The Call Taker for {{companyName}}. Wanted to circle back before heating season hits.</p>
<p>When furnaces start failing and customers call at 10pm, voicemail won't cut it. The company that answers first gets the job.</p>
<p>The Call Taker makes sure that's always {{companyName}}. $497/mo, no contracts, 48-hour setup.</p>
<p>Hear it live: <strong>(615) 784-5747</strong></p>
<p>— Wallace</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>""",
    },
}

SMS_TEMPLATES = [
    "Hey {{firstName}}, quick Q — when customers call {{companyName}} after hours, what happens? The Call Taker answers 24/7 so you never miss a job. Hear it: (615) 784-5747. Reply STOP to opt out",
    "{{firstName}} — 62% of HVAC calls that hit voicemail never call back. The Call Taker fixes that for {{companyName}}. Hear it live: (615) 784-5747. Reply STOP to opt out",
    "{{firstName}}, what if {{companyName}} never sent a caller to voicemail again? The Call Taker handles it 24/7. Quick listen: (615) 784-5747. Reply STOP to opt out",
]


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] BEN: {msg}"
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
        "User-Agent": "BenEngine/2.0 TheCallTaker",
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


def load_max_state():
    if os.path.exists(MAX_STATE_FILE):
        try:
            with open(MAX_STATE_FILE) as f:
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


def get_non_customer_contacts(contacts):
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
    """Enhanced lead scoring 1-10 with engagement + review + weather signals."""
    score = 3  # Base score (lower than before — earn your points)

    # Has email = +1
    if contact.get("email"):
        score += 1

    # Has phone = +1
    if contact.get("phone"):
        score += 1

    # Has company name = +1
    if contact.get("companyName"):
        score += 1

    # Tags analysis
    tags = [t.lower() for t in contact.get("tags", [])]

    # HVAC tagged = +1
    if any("hvac" in t for t in tags):
        score += 1

    # Voicemail confirmed (secret shopped) = +2 (proven problem)
    if "voicemail-confirmed" in tags:
        score += 2

    # Bad reviews mentioned = +1
    if "bad-reviews" in tags or "voicemail-in-reviews" in tags:
        score += 1

    # Demo booked or called = +2
    if "demo-booked" in tags or "demo-called" in tags:
        score += 2

    # Replied to outreach (check Max's warm followups)
    warm = max_state.get("warm_followups", {})
    cid = contact.get("id")
    if cid in warm:
        score += 2  # They replied — high intent

    # Demo line caller = +2
    demo_callers = max_state.get("demo_callers", {})
    if cid in demo_callers:
        score += 2

    # Weather urgency (extreme temps in their city = more pain)
    city = contact.get("city", "")
    if city:
        temp = get_weather_temp(city)
        if temp is not None and (temp >= 90 or temp <= 32):
            score += 1

    return min(score, 10)


# ===================================================
# CORE TASKS
# ===================================================

def morning_briefing():
    """7am: Weather-aware briefing with today's priorities."""
    log("=== BEN v2: Morning Briefing ===")
    contacts = get_all_contacts()
    leads = get_non_customer_contacts(contacts)
    state = load_state()
    max_state = load_max_state()

    total = len(contacts)
    lead_count = len(leads)
    customer_count = total - lead_count

    # Get weather for Nashville (HQ area)
    weather_info = get_weather("Nashville") or "unable to fetch"

    # Count key metrics from Max
    warm = max_state.get("warm_followups", {})
    active_warm = sum(1 for v in warm.values() if v.get("followup_count", 0) < 3)
    demo_callers = len(max_state.get("demo_callers", {}))
    secret_shoppers = max_state.get("total_secret_shopper", 0)

    now = datetime.utcnow() - timedelta(hours=6)
    day_name = now.strftime("%A")

    briefing = f"""GOOD MORNING WALLACE — {now.strftime('%b %d, %Y')} ({day_name})

WEATHER: Nashville — {weather_info}
SEASON: {get_season().upper()} — {get_seasonal_context()}

PIPELINE:
  Total contacts: {total}
  Active leads: {lead_count}
  Customers: {customer_count}
  Leads in warm follow-up: {active_warm}
  Demo line callers: {demo_callers}
  Secret shopper emails sent: {secret_shoppers}

TODAY'S GAME PLAN:
  Instantly: Sending 120 cold emails on burner domains (automatic)
  Max: Catching replies every 30min + warm follow-ups at 9am
  Ben: SMS at 1pm, re-engagement at 2pm, lead scoring at 3pm
  Sam: Support monitor every 15min, check-ins at 8am

YOUR MOVES TODAY:
  1. Check ntfy for any reply alerts — respond within 1 hour
  2. Secret shop 3-5 HVAC companies after 6pm (call, confirm voicemail, tag "voicemail-confirmed" in GHL)
  3. Check Instantly dashboard — make sure emails are actually sending
  4. Ben will score all leads at 3pm — check war room for hottest ones

LET'S GET THIS CLIENT."""

    ntfy(NTFY_OPS_TOPIC,
         f"Morning Briefing — {now.strftime('%b %d')}",
         briefing,
         priority="high",
         tags="sunrise,clipboard")

    log("Morning briefing sent.")
    return briefing


def sms_outreach():
    """1pm: SMS to leads with phone numbers. Only when A2P approved."""
    log("=== BEN v2: SMS Outreach ===")

    if not is_business_hours():
        log("Outside business hours. Skipping SMS.")
        return 0

    state = load_state()
    smsed = set(state.get("contacts_smsed", []))
    contacts = get_all_contacts()
    leads = get_non_customer_contacts(contacts)
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
             f"Ben sent {sent} SMS messages!",
             f"A2P is working! {sent} texts sent to HVAC leads.",
             priority="high",
             tags="iphone,zap")

    state["contacts_smsed"] = list(smsed)
    save_state(state)
    return sent


def reengage_warm_leads():
    """2pm: Re-engage leads who replied then ghosted. Uses seasonal angles."""
    log("=== BEN v2: Warm Re-engagement ===")

    if not is_business_hours():
        log("Outside business hours. Skipping.")
        return 0

    state = load_state()
    max_state = load_max_state()
    reengaged = set(state.get("contacts_reengaged", []))

    # Find leads who replied (in Max's warm_followups) but Max finished 3 follow-ups with no conversion
    warm = max_state.get("warm_followups", {})
    contacts = get_all_contacts()
    contact_map = {c["id"]: c for c in contacts}
    sent = 0
    season = get_season()

    for cid, data in warm.items():
        if cid in reengaged:
            continue

        # Only re-engage leads Max already followed up 3x
        if data.get("followup_count", 0) < 3:
            continue

        contact = contact_map.get(cid)
        if not contact:
            continue

        # Skip customers
        tags = [t.lower() for t in contact.get("tags", [])]
        if "customer" in tags or "active-client" in tags:
            continue

        email = contact.get("email")
        if not email:
            continue

        # Use seasonal re-engagement template
        template = REENGAGE_EMAILS.get(season, REENGAGE_EMAILS["winter"])
        subject = personalize(template["subject"], contact)
        body = personalize(template["body"], contact)

        if send_email(cid, subject, body):
            sent += 1
            reengaged.add(cid)
            state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
            log(f"  Re-engaged: {contact.get('firstName', 'Unknown')} ({season} angle)")

        time.sleep(3)
        if sent >= 10:
            log("Hit re-engagement limit (10). Stopping.")
            break

    if sent > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"Ben re-engaged {sent} warm leads",
             f"Seasonal {season} angle sent to {sent} leads who replied then ghosted.",
             tags="recycle,envelope")

    state["contacts_reengaged"] = list(reengaged)
    save_state(state)
    log(f"Re-engaged {sent} warm leads.")
    return sent


def score_all_leads():
    """3pm: Enhanced lead scoring with engagement + review + weather signals."""
    log("=== BEN v2: Lead Scoring ===")
    state = load_state()
    max_state = load_max_state()
    contacts = get_all_contacts()
    leads = get_non_customer_contacts(contacts)

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

    log(f"Scored {len(leads)} leads. {len(hot_leads)} scored 8+.")

    if hot_leads:
        hot_list = "\n".join([
            f"  {h['score']}/10 — {h['name']} ({h['company']}) {h['phone'] or h['email']}"
            + (f" [VOICEMAIL CONFIRMED]" if "voicemail-confirmed" in [t.lower() for t in h.get('tags', [])] else "")
            + (f" [DEMO CALLER]" if h.get('phone') and contact.get("id") in max_state.get("demo_callers", {}) else "")
            for h in sorted(hot_leads, key=lambda x: x['score'], reverse=True)[:10]
        ])
        ntfy(NTFY_WAR_TOPIC,
             f"{len(hot_leads)} HOT leads scored 8+",
             f"Top leads for Wallace to call TODAY:\n\n{hot_list}\n\nVoicemail-confirmed leads convert 3x better. Call those first!",
             priority="high",
             tags="fire,telephone_receiver")
        state["total_alerts"] = state.get("total_alerts", 0) + 1

    state["lead_scores"] = scores
    save_state(state)
    return len(hot_leads)


def evening_summary():
    """9pm: Evening summary with full team stats."""
    log("=== BEN v2: Evening Summary ===")
    state = load_state()
    max_state = load_max_state()
    contacts = get_all_contacts()
    leads = get_non_customer_contacts(contacts)

    total = len(contacts)
    lead_count = len(leads)
    customer_count = total - lead_count

    ben_emails = state.get("total_emails_sent", 0)
    ben_sms = state.get("total_sms_sent", 0)
    ben_reengaged = len(state.get("contacts_reengaged", []))
    hot_count = sum(1 for s in state.get("lead_scores", {}).values() if s >= 8)

    max_replies = max_state.get("total_replies_detected", 0)
    max_followups = max_state.get("total_followups_sent", 0)
    max_demo_calls = len(max_state.get("demo_callers", {}))
    max_secret_shopper = max_state.get("total_secret_shopper", 0)
    max_weather = max_state.get("total_weather_emails", 0)

    summary = f"""EVENING REPORT — {datetime.now().strftime('%b %d, %Y')}

PIPELINE:
  Total contacts: {total}
  Active leads: {lead_count}
  Customers: {customer_count}
  Hot leads (8+): {hot_count}

MAX v3 STATS:
  Replies caught: {max_replies}
  Warm follow-ups sent: {max_followups}
  Demo line callers: {max_demo_calls}
  Secret shopper emails: {max_secret_shopper}
  Weather-triggered emails: {max_weather}

BEN v2 STATS:
  Re-engagements sent: {ben_reengaged}
  SMS sent: {ben_sms}
  Total emails: {ben_emails}

COLD OUTREACH:
  Instantly.ai: 120/day on skylfinder.com (check dashboard for actual stats)

SEASON: {get_season().upper()} — all angles tuned for {get_season()} urgency

TOMORROW:
  7:00 AM — Ben: Morning briefing
  9:00 AM — Max: Warm follow-ups
  11:00 AM — Sam: Referral check
  1:00 PM — Ben: SMS (if A2P)
  2:00 PM — Ben: Re-engage warm leads
  3:00 PM — Ben: Lead scoring
  + Max catches replies every 30 min
  + Sam monitors customers every 15 min
  + Instantly sends 120 cold emails automatically

The team never stops. Good night Wallace."""

    ntfy(NTFY_OPS_TOPIC,
         f"Evening Report — {datetime.now().strftime('%b %d')}",
         summary,
         tags="moon,clipboard")

    log("Evening summary sent.")
    return summary


def print_status():
    state = load_state()
    max_state = load_max_state()
    contacts = get_all_contacts()
    leads = get_non_customer_contacts(contacts)
    hot = sum(1 for s in state.get("lead_scores", {}).values() if s >= 8)

    print("\n" + "=" * 50)
    print("  BEN v2 — STATUS REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print(f"  Total contacts:        {len(contacts)}")
    print(f"  Active leads:          {len(leads)}")
    print(f"  Ben emails sent:       {state.get('total_emails_sent', 0)}")
    print(f"  Ben SMS sent:          {state.get('total_sms_sent', 0)}")
    print(f"  Re-engaged:            {len(state.get('contacts_reengaged', []))}")
    print(f"  Hot leads (8+):        {hot}")
    print(f"  Season:                {get_season()}")
    print(f"  Max replies caught:    {max_state.get('total_replies_detected', 0)}")
    print(f"  Max demo callers:      {len(max_state.get('demo_callers', {}))}")
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
        log("=== BEN v2: Full cycle ===")
        morning_briefing()
        sms_outreach()
        reengage_warm_leads()
        score_all_leads()
        evening_summary()
        log("=== BEN v2: Full cycle complete ===")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
