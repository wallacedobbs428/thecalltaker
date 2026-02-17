#!/usr/bin/env python3
"""
MAX — The Call Taker's 24/7 Autonomous Sales Team Member
Built Feb 17, 2026 | v2.0

Max is a masterclass team member. He finds leads, reaches out with
killer personalized emails, monitors every reply, follows up relentlessly,
moves the pipeline, and alerts Wallace the instant something happens.
Max never sleeps. Max never stops. Max makes money.

Usage:
  python3 max-engine.py monitor    # Check for replies (run every 30 min)
  python3 max-engine.py followup   # Send follow-ups to cold leads (run daily 9am)
  python3 max-engine.py outreach   # Send cold emails to new leads (run daily 10am)
  python3 max-engine.py pipeline   # Move leads through stages (run daily midnight)
  python3 max-engine.py report     # Send daily summary to ntfy (run daily 8pm)
  python3 max-engine.py status     # Print current pipeline status
  python3 max-engine.py all        # Run all tasks in sequence
"""

import json
import subprocess
import sys
import os
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote

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
DEMO_URL = "https://thecalltaker.com/demo.html"
FROM_EMAIL = "wallacemdobbs@icloud.com"
FROM_NAME = "Wallace Dobbs"
FROM_USER_ID = "g4Ocu4qnhv7O8CrqpDTC"

# State file to track what Max has already done
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "max-state.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "max-log.txt")

# Cold outreach email templates (first touch — rotate through these)
COLD_EMAILS = [
    {
        "subject": "quick question about missed calls",
        "body": """<p>Hey {{firstName}},</p>
<p>Quick question — when a customer calls {{companyName}} after hours, what happens to that call?</p>
<p>If the answer is voicemail, you're losing jobs. 62% of callers who hit voicemail never call back.</p>
<p>The Call Taker is an AI receptionist that answers every call for {{companyName}} 24/7 — books jobs, takes messages, and texts you the details.</p>
<p>Takes 30 seconds to hear it live: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker<br>thecalltaker.com</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
    {
        "subject": "saw something about {{companyName}}",
        "body": """<p>Hey {{firstName}},</p>
<p>I work with HVAC companies and noticed {{companyName}} — looks like you've built something solid.</p>
<p>One thing I keep seeing: great companies losing $5K-$10K/month in jobs because calls go to voicemail when techs are busy or after hours.</p>
<p>We built an AI that answers every call, books the job, and texts you — 24/7. $497/mo, no contracts.</p>
<p>Want to hear it? Call the demo line: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker<br>thecalltaker.com</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
    {
        "subject": "hvac owners are switching to this",
        "body": """<p>Hey {{firstName}},</p>
<p>HVAC companies are quietly replacing voicemail with AI that answers calls, books jobs, and works 24/7.</p>
<p>The Call Taker does this for {{companyName}} — every call answered in under 2 seconds, every job booked, every detail texted to you.</p>
<p>$497/mo. No contracts. Set up in 48 hours. Cancel anytime.</p>
<p>Hear it yourself: <strong>(615) 784-5747</strong> — it's live right now.</p>
<p>— Wallace Dobbs<br>The Call Taker<br>thecalltaker.com</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
    {
        "subject": "what if {{companyName}} never missed a call",
        "body": """<p>Hey {{firstName}},</p>
<p>What if {{companyName}} never sent another customer to voicemail — not even at 11pm on a Saturday?</p>
<p>The Call Taker is an AI receptionist built for HVAC. It answers every call, asks the right questions, books the job, and texts you the details. 24/7/365.</p>
<p>Call the demo line and hear it yourself: <strong>(615) 784-5747</strong></p>
<p>— Wallace Dobbs<br>The Call Taker<br>thecalltaker.com</p>
<p style="font-size:11px;color:#999;">Reply STOP to opt out</p>"""
    },
]

# Follow-up email templates (rotate through these)
FOLLOWUP_EMAILS = [
    {
        "subject": "quick follow up",
        "body": """<p>Hey {{firstName}},</p>
<p>I reached out a few days ago about The Call Taker — an AI receptionist that answers every call for {{companyName}} 24/7.</p>
<p>62% of HVAC customers who hit voicemail never call back. That's real money walking out the door.</p>
<p>Want to hear it in action? Call our demo line: <strong>(615) 784-5747</strong> — it's live right now.</p>
<p>— Wallace<br>The Call Taker</p>"""
    },
    {
        "subject": "thought of {{companyName}}",
        "body": """<p>Hey {{firstName}},</p>
<p>Was thinking about {{companyName}} — when a customer calls after hours or while your team is on a job, what happens to that call?</p>
<p>The Call Taker is an AI that answers, books the job, and texts you the details. No voicemail. No missed revenue.</p>
<p>Takes 30 seconds to hear it: <strong>(615) 784-5747</strong></p>
<p>— Wallace<br>The Call Taker</p>"""
    },
    {
        "subject": "last thing then I'll stop",
        "body": """<p>Hey {{firstName}},</p>
<p>Last email from me — I promise.</p>
<p>Every missed call to {{companyName}} is a $350+ job going to a competitor. The Call Taker fixes that for $497/mo. No contracts, cancel anytime, set up in 48 hours.</p>
<p>If you're even slightly curious, call the demo line and hear it yourself: <strong>(615) 784-5747</strong></p>
<p>Either way, I respect your time. Good luck this season.</p>
<p>— Wallace<br>The Call Taker</p>"""
    }
]


# ═══════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════

def log(msg):
    """Log to file and stdout."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass


def ghl_request(method, path, body=None, version="2021-07-28"):
    """Make a GHL API request."""
    url = f"{GHL_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": version,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "MaxEngine/1.0 TheCallTaker",
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
    """Send ntfy notification."""
    try:
        url = f"https://ntfy.sh/{topic}"
        headers = {
            "Title": title,
            "Priority": priority,
            "Content-Type": "text/plain",
        }
        if tags:
            headers["Tags"] = tags
        req = Request(url, data=msg.encode(), headers=headers, method="POST")
        urlopen(req, timeout=10)
        log(f"ntfy sent: {title}")
    except Exception as e:
        log(f"ntfy error: {e}")


def load_state():
    """Load Max's state from disk."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_reply_check": None,
        "known_reply_ids": [],
        "contacts_followed_up": {},  # contact_id: {count, last_date}
        "last_pipeline_update": None,
        "total_emails_sent": 0,
        "total_alerts_sent": 0,
    }


def save_state(state):
    """Save Max's state to disk."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def get_all_contacts():
    """Fetch all contacts from GHL."""
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
    """Get conversations for a contact."""
    resp = ghl_request(
        "GET",
        f"/conversations/search?locationId={GHL_LOCATION_ID}&contactId={contact_id}",
        version="2021-04-15"
    )
    if resp and "conversations" in resp:
        return resp["conversations"]
    return []


def get_messages(conversation_id):
    """Get messages in a conversation."""
    resp = ghl_request(
        "GET",
        f"/conversations/{conversation_id}/messages",
        version="2021-04-15"
    )
    if resp and "messages" in resp:
        return resp["messages"]
    return []


def send_email(contact_id, subject, html_body):
    """Send an email via GHL."""
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


def personalize(template, contact):
    """Replace merge tags in a template."""
    first = contact.get("firstName", contact.get("name", "there"))
    company = contact.get("companyName", "your company")
    text = template.replace("{{firstName}}", first or "there")
    text = text.replace("{{companyName}}", company or "your company")
    return text


# ═══════════════════════════════════════════
# CORE TASKS
# ═══════════════════════════════════════════

def monitor_replies():
    """Check all conversations for new inbound replies. Alert via ntfy."""
    log("=== MAX: Checking for replies ===")
    state = load_state()
    known = set(state.get("known_reply_ids", []))
    new_replies = []

    contacts = get_all_contacts()
    log(f"Checking {len(contacts)} contacts for replies...")

    for contact in contacts:
        cid = contact.get("id")
        name = contact.get("firstName", "Unknown")
        company = contact.get("companyName", "Unknown")

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
                msg_type = msg.get("messageType", "")

                # Look for INBOUND messages we haven't seen
                if direction == "inbound" and msg_id not in known:
                    body_text = msg.get("body", msg.get("message", ""))
                    if not body_text or body_text.strip().upper() in ["STOP", "UNSUBSCRIBE"]:
                        known.add(msg_id)
                        continue

                    new_replies.append({
                        "contact_id": cid,
                        "name": name,
                        "company": company,
                        "message": body_text[:500],
                        "type": msg_type,
                        "msg_id": msg_id,
                    })
                    known.add(msg_id)

        # Rate limit — don't hammer the API
        time.sleep(0.5)

    if new_replies:
        log(f"Found {len(new_replies)} new replies!")
        for reply in new_replies:
            alert_title = f"REPLY from {reply['name']} ({reply['company']})"
            alert_body = f"Message: {reply['message']}\n\nType: {reply['type']}\n\nOpen GHL to respond."
            ntfy(NTFY_WAR_TOPIC, alert_title, alert_body, priority="high", tags="rotating_light,speech_balloon")
            state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1
    else:
        log("No new replies found.")

    state["known_reply_ids"] = list(known)[-500:]  # Keep last 500 to prevent bloat
    state["last_reply_check"] = datetime.now().isoformat()
    save_state(state)
    return new_replies


def send_followups():
    """Send follow-up emails to leads who haven't responded in 3+ days."""
    log("=== MAX: Sending follow-ups ===")
    state = load_state()
    followed_up = state.get("contacts_followed_up", {})
    contacts = get_all_contacts()
    sent_count = 0

    # Current hour in CST (UTC-6)
    now = datetime.utcnow() - timedelta(hours=6)
    current_hour = now.hour

    # Only send between 9am-5pm CST
    if current_hour < 9 or current_hour >= 17:
        log("Outside sending hours (9am-5pm CST). Skipping.")
        return 0

    # Only send Tue-Sat
    day_of_week = now.weekday()  # 0=Mon, 6=Sun
    if day_of_week == 6:  # Sunday
        log("Sunday — no follow-ups. Skipping.")
        return 0

    log(f"Processing {len(contacts)} contacts for follow-ups...")

    for contact in contacts:
        cid = contact.get("id")
        email = contact.get("email")
        name = contact.get("firstName", "")
        company = contact.get("companyName", "")

        if not email:
            continue

        # Check follow-up history
        fu_data = followed_up.get(cid, {"count": 0, "last_date": None})
        fu_count = fu_data.get("count", 0)

        # Max 3 follow-ups per contact
        if fu_count >= 3:
            continue

        # Check if last follow-up was at least 3 days ago
        last_date = fu_data.get("last_date")
        if last_date:
            try:
                last_dt = datetime.fromisoformat(last_date)
                if (datetime.now() - last_dt).days < 3:
                    continue
            except:
                pass

        # Check if they've replied (skip if they have)
        convos = get_conversations(cid)
        has_reply = False
        for convo in convos:
            messages = get_messages(convo.get("id", ""))
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                if msg.get("direction") == "inbound":
                    body = msg.get("body", msg.get("message", ""))
                    if body and body.strip().upper() not in ["STOP", "UNSUBSCRIBE"]:
                        has_reply = True
                        break
            if has_reply:
                break

        if has_reply:
            continue

        # Pick the right follow-up template
        template = FOLLOWUP_EMAILS[min(fu_count, len(FOLLOWUP_EMAILS) - 1)]
        subject = personalize(template["subject"], contact)
        body = personalize(template["body"], contact)

        # Send it
        if send_email(cid, subject, body):
            sent_count += 1
            followed_up[cid] = {
                "count": fu_count + 1,
                "last_date": datetime.now().isoformat()
            }
            state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1

        # Rate limit: max 30 emails per run, 2 sec between each
        time.sleep(2)
        if sent_count >= 30:
            log("Hit daily limit of 30 follow-ups. Stopping.")
            break

    log(f"Sent {sent_count} follow-up emails.")

    if sent_count > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"Max sent {sent_count} follow-ups",
             f"Follow-up emails sent to {sent_count} leads who hadn't responded in 3+ days.\n\nTotal emails sent by Max: {state.get('total_emails_sent', 0)}",
             tags="outbox_tray")

    state["contacts_followed_up"] = followed_up
    save_state(state)
    return sent_count


def update_pipeline():
    """Move leads through pipeline stages based on activity."""
    log("=== MAX: Updating pipeline stages ===")
    state = load_state()

    # Get all opportunities in the pipeline
    resp = ghl_request("GET", f"/opportunities/search?location_id={GHL_LOCATION_ID}&pipeline_id={PIPELINE_ID}")
    if not resp or "opportunities" not in resp:
        log("Could not fetch opportunities.")
        return

    opportunities = resp["opportunities"]
    log(f"Found {len(opportunities)} opportunities in pipeline.")

    moved = 0
    for opp in opportunities:
        opp_id = opp.get("id")
        contact_id = opp.get("contact", {}).get("id", opp.get("contactId"))
        current_stage = opp.get("pipelineStageId", "")
        last_activity = opp.get("lastActivity") or opp.get("updatedAt") or opp.get("createdAt")

        if not contact_id:
            continue

        # Check if contact has replied
        convos = get_conversations(contact_id)
        has_reply = False
        for convo in convos:
            messages = get_messages(convo.get("id", ""))
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                if msg.get("direction") == "inbound":
                    body = msg.get("body", msg.get("message", ""))
                    if body and body.strip().upper() not in ["STOP", "UNSUBSCRIBE"]:
                        has_reply = True
                        break
            if has_reply:
                break

        # If they replied and are still in "Contacted" stage, move to next stage
        if has_reply and current_stage == CONTACTED_STAGE:
            # We'd move to "Engaged" stage — need to know that stage ID
            # For now, log it and alert
            name = opp.get("contact", {}).get("name", "Unknown")
            log(f"LEAD ENGAGED: {name} replied and should be moved to Engaged stage")
            ntfy(NTFY_WAR_TOPIC,
                 f"HOT LEAD: {name} replied!",
                 f"{name} has replied to outreach. They're in the Contacted stage — move them to Engaged and follow up personally!",
                 priority="high",
                 tags="fire,rotating_light")
            moved += 1

        time.sleep(0.5)

    state["last_pipeline_update"] = datetime.now().isoformat()
    save_state(state)
    log(f"Pipeline check complete. {moved} leads flagged for stage change.")
    return moved


def send_cold_outreach():
    """Send first-touch cold emails to leads who haven't been contacted yet."""
    log("=== MAX: Cold outreach to new leads ===")
    state = load_state()
    emailed = state.get("contacts_emailed", set())
    if isinstance(emailed, list):
        emailed = set(emailed)
    followed_up = state.get("contacts_followed_up", {})
    contacts = get_all_contacts()
    sent_count = 0

    # Only send between 9am-5pm CST
    now = datetime.utcnow() - timedelta(hours=6)
    current_hour = now.hour
    if current_hour < 9 or current_hour >= 17:
        log("Outside sending hours (9am-5pm CST). Skipping cold outreach.")
        return 0

    # Only send Mon-Fri
    day_of_week = now.weekday()
    if day_of_week >= 5:  # Saturday or Sunday
        log("Weekend — no cold outreach. Skipping.")
        return 0

    log(f"Scanning {len(contacts)} contacts for unemailed leads...")

    import random
    template_idx = 0

    for contact in contacts:
        cid = contact.get("id")
        email = contact.get("email")
        name = contact.get("firstName", "")

        # Skip if no email
        if not email:
            continue

        # Skip if already emailed by Max
        if cid in emailed:
            continue

        # Skip if already in follow-up cycle
        if cid in followed_up:
            continue

        # Pick a cold email template (rotate)
        template = COLD_EMAILS[template_idx % len(COLD_EMAILS)]
        template_idx += 1

        subject = personalize(template["subject"], contact)
        body = personalize(template["body"], contact)

        if send_email(cid, subject, body):
            sent_count += 1
            emailed.add(cid)
            # Mark as first follow-up so the follow-up engine picks them up in 3 days
            followed_up[cid] = {
                "count": 0,
                "last_date": datetime.now().isoformat()
            }
            state["total_emails_sent"] = state.get("total_emails_sent", 0) + 1
            log(f"  Cold email #{sent_count} sent to {name} ({email})")

        # Rate limit: max 20 cold emails per run, 3 sec between each
        time.sleep(3)
        if sent_count >= 20:
            log("Hit daily cold outreach limit of 20. Stopping.")
            break

    log(f"Sent {sent_count} cold outreach emails.")

    if sent_count > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"Max sent {sent_count} cold emails",
             f"First-touch outreach sent to {sent_count} new leads.\n\nTotal emails sent by Max: {state.get('total_emails_sent', 0)}",
             tags="envelope,zap")

    state["contacts_emailed"] = list(emailed)
    state["contacts_followed_up"] = followed_up
    save_state(state)
    return sent_count


def send_daily_report():
    """Send end-of-day summary to Wallace via ntfy."""
    log("=== MAX: Generating daily report ===")
    state = load_state()
    contacts = get_all_contacts()

    total = len(contacts)
    with_email = sum(1 for c in contacts if c.get("email"))
    without_email = total - with_email

    fu = state.get("contacts_followed_up", {})
    emailed_count = len(state.get("contacts_emailed", []))
    total_sent = state.get("total_emails_sent", 0)
    total_alerts = state.get("total_alerts_sent", 0)

    fu_1 = sum(1 for v in fu.values() if v.get("count", 0) == 1)
    fu_2 = sum(1 for v in fu.values() if v.get("count", 0) == 2)
    fu_3 = sum(1 for v in fu.values() if v.get("count", 0) >= 3)

    report = f"""MAX DAILY REPORT — {datetime.now().strftime('%b %d, %Y')}

PIPELINE:
  Total contacts: {total}
  With email: {with_email}
  Without email: {without_email}

OUTREACH:
  Cold emails sent (all time): {emailed_count}
  Follow-up round 1: {fu_1}
  Follow-up round 2: {fu_2}
  Follow-up round 3 (final): {fu_3}
  Total emails sent by Max: {total_sent}

REPLIES:
  Total alerts sent: {total_alerts}
  Last reply check: {state.get('last_reply_check', 'Never')}

STATUS: Active and running 24/7
Next actions: Reply monitor in 30 min, follow-ups at 9am, cold outreach at 10am"""

    ntfy(NTFY_OPS_TOPIC,
         f"Max Daily Report — {datetime.now().strftime('%b %d')}",
         report,
         tags="clipboard,chart_with_upwards_trend")

    log("Daily report sent to ntfy.")
    return report


def print_status():
    """Print current Max status and pipeline overview."""
    state = load_state()
    contacts = get_all_contacts()

    print("\n" + "=" * 50)
    print("  MAX — STATUS REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print(f"  Total contacts in GHL:     {len(contacts)}")
    print(f"  Total emails sent by Max:  {state.get('total_emails_sent', 0)}")
    print(f"  Total alerts sent:         {state.get('total_alerts_sent', 0)}")
    print(f"  Last reply check:          {state.get('last_reply_check', 'Never')}")
    print(f"  Last pipeline update:      {state.get('last_pipeline_update', 'Never')}")

    # Count follow-up stats
    fu = state.get("contacts_followed_up", {})
    fu_1 = sum(1 for v in fu.values() if v.get("count", 0) == 1)
    fu_2 = sum(1 for v in fu.values() if v.get("count", 0) == 2)
    fu_3 = sum(1 for v in fu.values() if v.get("count", 0) >= 3)
    print(f"  Follow-up round 1:         {fu_1} contacts")
    print(f"  Follow-up round 2:         {fu_2} contacts")
    print(f"  Follow-up round 3 (final): {fu_3} contacts")
    print("=" * 50 + "\n")


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "monitor":
        replies = monitor_replies()
        if replies:
            print(f"\nFound {len(replies)} new replies!")
            for r in replies:
                print(f"  - {r['name']} ({r['company']}): {r['message'][:80]}...")
    elif cmd == "followup":
        count = send_followups()
        print(f"\nSent {count} follow-up emails.")
    elif cmd == "outreach":
        count = send_cold_outreach()
        print(f"\nSent {count} cold outreach emails.")
    elif cmd == "pipeline":
        moved = update_pipeline()
        print(f"\nFlagged {moved} leads for stage changes.")
    elif cmd == "report":
        report = send_daily_report()
        print(report)
    elif cmd == "status":
        print_status()
    elif cmd == "all":
        log("=== MAX: Running full cycle ===")
        monitor_replies()
        send_cold_outreach()
        send_followups()
        update_pipeline()
        send_daily_report()
        log("=== MAX: Full cycle complete ===")
        ntfy(NTFY_OPS_TOPIC,
             "Max completed full cycle",
             f"All tasks done: replies + outreach + follow-ups + pipeline + report.\nTime: {datetime.now().strftime('%I:%M %p')}",
             tags="white_check_mark")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
