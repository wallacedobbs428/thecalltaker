#!/usr/bin/env python3
"""
BEN — The Call Taker's 24/7 Senior Sales Closer
Built Feb 17, 2026 | v1.0

Ben is Max's sharper, smarter brother. Where Max handles the volume grind,
Ben focuses on CONVERSION. He uses different angles, smarter timing,
re-engages cold leads with fresh pitches, sends morning briefings,
handles SMS (when A2P approves), and scores every lead.

Ben never sends the same angle Max already sent. They work as a team.

Usage:
  python3 ben-engine.py morning     # 7am briefing to Wallace
  python3 ben-engine.py outreach    # Different-angle cold emails (11am)
  python3 ben-engine.py reengage    # Re-engage Max's cold leads with new angles (2pm)
  python3 ben-engine.py sms         # Send SMS blasts when A2P approves (1pm)
  python3 ben-engine.py score       # Score all leads and flag hot ones (3pm)
  python3 ben-engine.py evening     # Evening summary + next-day plan (9pm)
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

# ═══════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

PIPELINE_ID = "KhFDURSwBi2fn416BnGf"
CONTACTED_STAGE = "8285b2c9-9ca3-415f-a57b-ae458045aab4"

NTFY_OPS_TOPIC = "tct-xK9mW4vR7pLd"
NTFY_WAR_TOPIC = "tct-warroom-Kx7mN9pQ"

DEMO_LINE = "(615) 784-5747"
FROM_EMAIL = "wallacemdobbs@icloud.com"
SMS_PHONE = "+16156539004"

BEN_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BEN_DIR, "ben-state.json")
LOG_FILE = os.path.join(BEN_DIR, "ben-log.txt")

# Max's state file — Ben reads it to avoid duplicating work
MAX_STATE_FILE = os.path.join(os.path.dirname(BEN_DIR), "max", "max-state.json")

# ═══════════════════════════════════════════
# BEN'S EMAIL ANGLES (different from Max's)
# Max uses: missed calls, company-specific, HVAC switching, never miss
# Ben uses: ROI/money, competition, after-hours, seasonal urgency
# ═══════════════════════════════════════════

COLD_EMAILS_ROI = [
    {
        "subject": "$497 vs losing $9,000 a month",
        "body": """<p>Hey {{firstName}},</p>
<p>Quick math for {{companyName}}:</p>
<ul>
<li>Average HVAC service call: $350</li>
<li>Missed calls per month (industry avg): 40</li>
<li>67% never call back = 27 lost customers</li>
<li><strong>That's $9,450/month walking out the door.</strong></li>
</ul>
<p>The Call Taker answers every call for $497/mo. That's a 19x return.</p>
<p>Hear it live: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
    {
        "subject": "your competitor already uses AI",
        "body": """<p>Hey {{firstName}},</p>
<p>The HVAC companies winning right now aren't just better at installs — they're better at answering the phone.</p>
<p>While {{companyName}}'s calls go to voicemail after hours, competitors with AI receptionists are booking those same jobs at 10pm.</p>
<p>The Call Taker answers every call 24/7, books the job, texts you the details. $497/mo.</p>
<p>Call the demo line right now: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
    {
        "subject": "who answers at 10pm on saturday",
        "body": """<p>Hey {{firstName}},</p>
<p>Saturday night. 10pm. AC goes out in a customer's house with a newborn.</p>
<p>They Google "HVAC emergency." They call {{companyName}}. What happens?</p>
<p>If the answer is voicemail — that's a $500+ emergency call going to whoever picks up first.</p>
<p>The Call Taker answers in under 2 seconds. 24/7. Even Christmas morning.</p>
<p>Hear it: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
    {
        "subject": "summer is coming for {{companyName}}",
        "body": """<p>Hey {{firstName}},</p>
<p>Summer is about to hit and {{companyName}}'s phone will ring off the hook. Every AC breakdown, every thermostat emergency, every "it's too hot" call.</p>
<p>Your techs will be on jobs. Your office will be slammed. Calls will go to voicemail.</p>
<p>The Call Taker handles the overflow — answers every call, books the job, texts you. $497/mo, set up in 48 hours.</p>
<p>Call the demo: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
]

RE_ENGAGE_EMAILS = [
    {
        "subject": "one more thing about {{companyName}}",
        "body": """<p>Hey {{firstName}},</p>
<p>I know I've reached out before, so I'll keep this short.</p>
<p>I ran the numbers for a company like {{companyName}}. At just 40 missed calls/month, that's roughly <strong>$113,000/year</strong> in lost revenue.</p>
<p>The fix is $497/mo. No contracts. Cancel anytime.</p>
<p>If the math doesn't make sense for you, no worries — but if it does, call: <strong>(615) 784-5747</strong></p>
<p>— Wallace</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
    {
        "subject": "free missed call audit for {{companyName}}",
        "body": """<p>Hey {{firstName}},</p>
<p>I'd like to offer {{companyName}} a free Missed Call Audit — I'll call your business at different times and put together a report showing exactly what your customers experience.</p>
<p>No obligation. No pitch. Just data you can use.</p>
<p>Want me to run it? Just reply "yes" and I'll have it done in 48 hours.</p>
<p>— Wallace Dobbs<br>The Call Taker<br>thecalltaker.com/audit</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
]

SMS_TEMPLATES = [
    "Hey {{firstName}}, quick Q — when customers call {{companyName}} after hours, what happens? The Call Taker answers 24/7 so you never miss a job. Hear it: (615) 784-5747. Reply STOP to opt out",
    "{{firstName}} — 62% of HVAC calls that hit voicemail never call back. The Call Taker fixes that for {{companyName}}. Hear it live: (615) 784-5747. Reply STOP to opt out",
    "{{firstName}}, what if {{companyName}} never sent a caller to voicemail again? The Call Taker handles it 24/7. Quick listen: (615) 784-5747. Reply STOP to opt out",
]


# ═══════════════════════════════════════════
# HELPERS (same as Max but independent)
# ═══════════════════════════════════════════

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
        "User-Agent": "BenEngine/1.0 TheCallTaker",
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
        "contacts_emailed": [],
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
    """Read Max's state to coordinate — Ben won't email leads Max already emailed today."""
    if os.path.exists(MAX_STATE_FILE):
        with open(MAX_STATE_FILE) as f:
            return json.load(f)
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
    """Check if a contact has ever replied."""
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
    if now.weekday() >= 5:  # Weekend
        return False
    return True


def score_lead(contact):
    """Score a lead 1-10 based on available data."""
    score = 5  # Base score

    # Has email = +1
    if contact.get("email"):
        score += 1

    # Has phone = +1
    if contact.get("phone"):
        score += 1

    # Has company name = +1
    if contact.get("companyName"):
        score += 1

    # Has tags suggesting research was done = +1
    tags = contact.get("tags", [])
    if any("hvac" in t.lower() for t in tags):
        score += 1

    # Multiple tags = well-researched = +1
    if len(tags) >= 3:
        score += 1

    return min(score, 10)


# ═══════════════════════════════════════════
# CORE TASKS
# ═══════════════════════════════════════════

def morning_briefing():
    """Send Wallace a morning briefing with pipeline status and today's plan."""
    log("=== Morning Briefing ===")
    contacts = get_all_contacts()
    state = load_state()
    max_state = load_max_state()

    total = len(contacts)
    with_email = sum(1 for c in contacts if c.get("email"))
    with_phone = sum(1 for c in contacts if c.get("phone"))

    max_emailed = len(max_state.get("contacts_emailed", []))
    ben_emailed = len(state.get("contacts_emailed", []))
    ben_reengaged = len(state.get("contacts_reengaged", []))

    unemailed = with_email - max_emailed - ben_emailed
    if unemailed < 0:
        unemailed = 0

    now = datetime.utcnow() - timedelta(hours=6)
    day_name = now.strftime("%A")

    briefing = f"""GOOD MORNING WALLACE — {now.strftime('%b %d, %Y')} ({day_name})

PIPELINE:
  Total contacts: {total}
  With email: {with_email} | With phone: {with_phone}
  Emailed by Max: {max_emailed} | Emailed by Ben: {ben_emailed}
  Re-engaged by Ben: {ben_reengaged}
  Still unemailed: {unemailed}

TODAY'S PLAN:
  Max: Reply check every 30min, follow-ups at 9am, cold outreach at 10am
  Ben: Cold outreach at 11am (different angle), re-engagement at 2pm, lead scoring at 3pm

BLOCKERS:
  A2P SMS: Check GHL Trust Center — if approved, Ben will start SMS blasts
  Instantly.ai: Use the UI to add leads to campaigns manually

YOUR MOVE TODAY:
  1. Check ntfy for any reply alerts — respond within 1 hour
  2. Call the top 3 leads Ben scores highest today
  3. Post 1 thing on Instagram (@thecalltaker)

LET'S GET THIS CLIENT."""

    ntfy(NTFY_OPS_TOPIC,
         f"Morning Briefing — {now.strftime('%b %d')}",
         briefing,
         priority="high",
         tags="sunrise,clipboard")

    log("Morning briefing sent.")
    return briefing


def cold_outreach():
    """Send cold emails using Ben's angles (ROI, competition, after-hours, seasonal)."""
    log("=== Ben Cold Outreach ===")

    if not is_business_hours():
        log("Outside business hours. Skipping.")
        return 0

    state = load_state()
    max_state = load_max_state()

    ben_emailed = set(state.get("contacts_emailed", []))
    max_emailed = set(max_state.get("contacts_emailed", []))
    max_followed = set(max_state.get("contacts_followed_up", {}).keys())

    contacts = get_all_contacts()
    sent = 0
    template_idx = 0

    for contact in contacts:
        cid = contact.get("id")
        email = contact.get("email")

        if not email:
            continue

        # Skip if Ben already emailed
        if cid in ben_emailed:
            continue

        # Skip if Max already emailed — Ben waits for Max's cold email to land first
        # Ben only emails leads Max HASN'T touched
        if cid in max_emailed or cid in max_followed:
            continue

        template = COLD_EMAILS_ROI[template_idx % len(COLD_EMAILS_ROI)]
        template_idx += 1

        subject = personalize(template["subject"], contact)
        body = personalize(template["body"], contact)

        if send_email(cid, subject, body):
            sent += 1
            ben_emailed.add(cid)
            state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
            name = contact.get("firstName", "Unknown")
            log(f"  Cold email #{sent} to {name} ({email})")

        time.sleep(3)
        if sent >= 15:
            log("Hit Ben's daily cold limit (15). Stopping.")
            break

    if sent > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"Ben sent {sent} cold emails",
             f"Ben's ROI/competition angle emails sent to {sent} fresh leads.",
             tags="envelope,chart_with_upwards_trend")

    state["contacts_emailed"] = list(ben_emailed)
    save_state(state)
    log(f"Ben sent {sent} cold outreach emails.")
    return sent


def reengage_cold_leads():
    """Re-engage leads that Max followed up 3x with no response — use fresh angle."""
    log("=== Ben Re-engagement ===")

    if not is_business_hours():
        log("Outside business hours. Skipping.")
        return 0

    state = load_state()
    max_state = load_max_state()
    reengaged = set(state.get("contacts_reengaged", []))

    max_followed = max_state.get("contacts_followed_up", {})
    contacts = get_all_contacts()
    sent = 0
    template_idx = 0

    for contact in contacts:
        cid = contact.get("id")
        email = contact.get("email")

        if not email or cid in reengaged:
            continue

        # Only re-engage leads Max gave up on (3 follow-ups, no reply)
        fu = max_followed.get(cid, {})
        if fu.get("count", 0) < 3:
            continue

        # Make sure they haven't replied
        if has_inbound_reply(cid):
            continue

        template = RE_ENGAGE_EMAILS[template_idx % len(RE_ENGAGE_EMAILS)]
        template_idx += 1

        subject = personalize(template["subject"], contact)
        body = personalize(template["body"], contact)

        if send_email(cid, subject, body):
            sent += 1
            reengaged.add(cid)
            state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
            log(f"  Re-engaged: {contact.get('firstName', 'Unknown')}")

        time.sleep(3)
        if sent >= 10:
            log("Hit Ben's re-engagement limit (10). Stopping.")
            break

    if sent > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"Ben re-engaged {sent} cold leads",
             f"Fresh angles sent to {sent} leads who didn't respond to Max's 3 follow-ups.",
             tags="recycle,envelope")

    state["contacts_reengaged"] = list(reengaged)
    save_state(state)
    log(f"Ben re-engaged {sent} cold leads.")
    return sent


def sms_outreach():
    """Send SMS to leads with phone numbers. Only works when A2P is approved."""
    log("=== Ben SMS Outreach ===")

    if not is_business_hours():
        log("Outside business hours. Skipping SMS.")
        return 0

    state = load_state()
    smsed = set(state.get("contacts_smsed", []))
    contacts = get_all_contacts()
    sent = 0
    template_idx = 0

    for contact in contacts:
        cid = contact.get("id")
        phone = contact.get("phone")

        if not phone or cid in smsed:
            continue

        # Check DND
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
            # If SMS fails, A2P probably not approved yet
            if sent == 0:
                log("SMS failed on first attempt — A2P likely not approved. Stopping.")
                break

        time.sleep(2)
        if sent >= 15:
            log("Hit Ben's daily SMS limit (15). Stopping.")
            break

    if sent > 0:
        ntfy(NTFY_WAR_TOPIC,
             f"Ben sent {sent} SMS messages!",
             f"A2P is working! {sent} texts sent to HVAC leads.",
             priority="high",
             tags="iphone,zap")
    elif sent == 0:
        log("No SMS sent — A2P likely still pending.")

    state["contacts_smsed"] = list(smsed)
    save_state(state)
    return sent


def score_all_leads():
    """Score every lead and flag hot ones for Wallace to call."""
    log("=== Ben Lead Scoring ===")
    state = load_state()
    contacts = get_all_contacts()

    scores = {}
    hot_leads = []

    for contact in contacts:
        cid = contact.get("id")
        score = score_lead(contact)
        scores[cid] = score

        if score >= 8:
            hot_leads.append({
                "name": contact.get("firstName", "Unknown"),
                "company": contact.get("companyName", "Unknown"),
                "email": contact.get("email", ""),
                "phone": contact.get("phone", ""),
                "score": score,
            })

    log(f"Scored {len(contacts)} leads. {len(hot_leads)} scored 8+.")

    if hot_leads:
        hot_list = "\n".join([
            f"  {h['score']}/10 — {h['name']} ({h['company']}) {h['phone'] or h['email']}"
            for h in sorted(hot_leads, key=lambda x: x['score'], reverse=True)[:10]
        ])
        ntfy(NTFY_WAR_TOPIC,
             f"{len(hot_leads)} hot leads scored 8+",
             f"Top leads to call TODAY:\n\n{hot_list}\n\nCall these first!",
             priority="high",
             tags="fire,telephone_receiver")

    state["lead_scores"] = scores
    save_state(state)
    return len(hot_leads)


def evening_summary():
    """Evening summary + next-day plan."""
    log("=== Ben Evening Summary ===")
    state = load_state()
    max_state = load_max_state()
    contacts = get_all_contacts()

    total = len(contacts)
    max_emails = max_state.get("total_emails_sent", 0)
    ben_emails = state.get("total_emails_sent", 0)
    ben_sms = state.get("total_sms_sent", 0)
    ben_reengaged = len(state.get("contacts_reengaged", []))

    hot_count = sum(1 for s in state.get("lead_scores", {}).values() if s >= 8)

    summary = f"""EVENING REPORT — {datetime.now().strftime('%b %d, %Y')}

TEAM STATS TODAY:
  Max emails sent (all time): {max_emails}
  Ben emails sent (all time): {ben_emails}
  Ben SMS sent (all time): {ben_sms}
  Ben re-engagements: {ben_reengaged}
  Combined outreach: {max_emails + ben_emails + ben_sms} touches

PIPELINE:
  Total contacts: {total}
  Hot leads (8+): {hot_count}

TOMORROW'S GAME PLAN:
  7:00 AM — Ben sends morning briefing
  9:00 AM — Max sends follow-ups
  10:00 AM — Max sends cold outreach
  11:00 AM — Ben sends ROI-angle cold outreach
  1:00 PM — Ben tries SMS (if A2P approved)
  2:00 PM — Ben re-engages Max's cold leads
  3:00 PM — Ben scores all leads
  8:00 PM — Max daily report
  9:00 PM — Ben evening summary

The team never stops. Good night Wallace."""

    ntfy(NTFY_OPS_TOPIC,
         f"Evening Report — {datetime.now().strftime('%b %d')}",
         summary,
         tags="moon,clipboard")

    log("Evening summary sent.")
    return summary


def print_status():
    state = load_state()
    contacts = get_all_contacts()

    print("\n" + "=" * 50)
    print("  BEN — STATUS REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print(f"  Total contacts:        {len(contacts)}")
    print(f"  Ben emails sent:       {state.get('total_emails_sent', 0)}")
    print(f"  Ben SMS sent:          {state.get('total_sms_sent', 0)}")
    print(f"  Cold emailed:          {len(state.get('contacts_emailed', []))}")
    print(f"  Re-engaged:            {len(state.get('contacts_reengaged', []))}")
    print(f"  SMS'd:                 {len(state.get('contacts_smsed', []))}")
    hot = sum(1 for s in state.get("lead_scores", {}).values() if s >= 8)
    print(f"  Hot leads (8+):        {hot}")
    print("=" * 50 + "\n")


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "morning":
        morning_briefing()
    elif cmd == "outreach":
        cold_outreach()
    elif cmd == "reengage":
        reengage_cold_leads()
    elif cmd == "sms":
        sms_outreach()
    elif cmd == "score":
        score_all_leads()
    elif cmd == "evening":
        evening_summary()
    elif cmd == "status":
        print_status()
    elif cmd == "all":
        log("=== BEN: Full cycle ===")
        morning_briefing()
        cold_outreach()
        sms_outreach()
        reengage_cold_leads()
        score_all_leads()
        evening_summary()
        log("=== BEN: Full cycle complete ===")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
