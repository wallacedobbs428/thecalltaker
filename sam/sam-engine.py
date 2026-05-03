#!/usr/bin/env python3
"""
SAM — The Call Taker's 24/7 Customer Success Team Member
Built Feb 18, 2026 | v1.0

Sam takes care of the customers. He monitors for issues, auto-responds
with troubleshooting, alerts Wallace+Mills immediately on problems,
sends proactive check-ins at milestones, asks for referrals at the
right moments, and scores customer health.

"The best way to grow your business is taking care of your customers."

Usage:
  python3 sam-engine.py support    # Scan for issues, auto-respond (every 15 min)
  python3 sam-engine.py health     # Score customer health 1-10 (daily 6am)
  python3 sam-engine.py checkin    # Send milestone emails (daily 8am)
  python3 sam-engine.py referral   # Alert Wallace to call for referrals, email fallback after 48h (daily 11am)
  python3 sam-engine.py report     # Customer health summary (daily 7pm)
  python3 sam-engine.py status     # Print current stats
  python3 sam-engine.py all        # Run all tasks in sequence
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

PROVIDER_SYNC_DISABLED = "REMOVED_SECRET"
PROVIDER_SYNC_LOCATION_DISABLED = "tQb9YmrGDrdVUJYPKrsY"
LEGACY_CRM_BASE = "https://crm-disabled.invalid"

NTFY_OPS_TOPIC = "tct-sales-63uYsIT9"
NTFY_WAR_TOPIC = "tct-urgent-Hk9UOEZR"

FROM_EMAIL = "thecalltakerai@gmail.com"
FROM_NAME = "Wallace Dobbs"
DEMO_LINE = "(629) 269-9697"

SAM_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SAM_DIR, "sam-state.json")
LOG_FILE = os.path.join(SAM_DIR, "sam-log.txt")

# Read Max + Ben state files (read-only) for lead journey context
MAX_STATE_FILE = os.path.join(os.path.dirname(SAM_DIR), "max", "max-state.json")
BEN_STATE_FILE = os.path.join(os.path.dirname(SAM_DIR), "ben", "ben-state.json")

# ===================================================
# CRITICAL KEYWORDS — Immediate war room alert
# ===================================================

CRITICAL_KEYWORDS = [
    "cancel", "refund", "lawyer", "bbb", "stop service",
    "terrible", "worst", "attorney", "sue", "lawsuit",
    "better business bureau", "complaint",
]

# ===================================================
# ISSUE KEYWORDS — Trigger auto-response
# ===================================================

ISSUE_KEYWORDS = {
    "forwarding": ["forward", "forwarding", "transfer", "route", "routing", "not ringing", "calls aren't coming"],
    "ai_quality": ["greeting", "wrong name", "sounds weird", "robotic", "doesn't understand", "keeps asking", "repeating", "ai is", "agent sounds"],
    "scheduling": ["calendar", "schedule", "booking", "appointment", "sync", "not showing", "double booked", "wrong time"],
    "notifications": ["notification", "text me", "didn't get", "no alert", "sms", "not receiving", "missed notification"],
    "billing": ["bill", "billing", "charge", "payment", "invoice", "receipt", "charged", "subscription", "price"],
}

# ===================================================
# KNOWLEDGE BASE — Auto-response templates
# ===================================================

KNOWLEDGE_BASE = {
    "forwarding": {
        "subject": "Call Forwarding — Quick Fix",
        "body": """<p>Hey {{firstName}},</p>
<p>Thanks for reaching out! Call forwarding issues are usually a quick fix.</p>
<p><strong>Here's what to check:</strong></p>
<ol>
<li>Open your phone app and go to Settings > Call Forwarding</li>
<li>Make sure forwarding is set to your Call Taker number</li>
<li>If it's already set, toggle it off, wait 10 seconds, and toggle it back on</li>
<li>Try calling your business number from another phone to test</li>
</ol>
<p>If it's still not working after that, reply to this email and we'll get on a call to fix it together. Usually takes 5 minutes.</p>
<p>— The Call Taker Team</p>""",
    },
    "ai_quality": {
        "subject": "AI Agent — We're On It",
        "body": """<p>Hey {{firstName}},</p>
<p>Thanks for letting us know about the AI quality issue. We take this seriously — your callers should have a great experience.</p>
<p><strong>Common quick fixes:</strong></p>
<ul>
<li><strong>Wrong greeting/name:</strong> We can update this in under 5 minutes — just reply with what it should say</li>
<li><strong>Not understanding callers:</strong> We'll tune the AI's instructions to handle your specific call types better</li>
<li><strong>Sounds robotic:</strong> We can adjust the voice style and pacing</li>
</ul>
<p>Reply with the specific issue and we'll have it fixed within the hour.</p>
<p>— The Call Taker Team</p>""",
    },
    "scheduling": {
        "subject": "Scheduling/Calendar — Quick Fix",
        "body": """<p>Hey {{firstName}},</p>
<p>Thanks for flagging the scheduling issue. Let's get this sorted.</p>
<p><strong>Common fixes:</strong></p>
<ul>
<li><strong>Calendar not syncing:</strong> Check that your Google/Outlook calendar is connected in your dashboard</li>
<li><strong>Double bookings:</strong> Make sure buffer times are set between appointments</li>
<li><strong>Wrong time zone:</strong> Verify your time zone setting in your account</li>
</ul>
<p>If none of those apply, reply with the details and we'll fix it right away.</p>
<p>— The Call Taker Team</p>""",
    },
    "notifications": {
        "subject": "Notification Delivery — Quick Fix",
        "body": """<p>Hey {{firstName}},</p>
<p>Missing notifications is frustrating — let's fix it fast.</p>
<p><strong>Check these first:</strong></p>
<ul>
<li>Make sure your phone number is correct in your account settings</li>
<li>Check that notifications aren't going to spam/junk</li>
<li>Verify Do Not Disturb isn't blocking texts during business hours</li>
<li>Try replying "YES" to the last notification text to confirm the number is active</li>
</ul>
<p>Still not getting them? Reply here and we'll switch to email notifications or set up an alternative.</p>
<p>— The Call Taker Team</p>""",
    },
    "billing": {
        "subject": "Billing Question — We've Got You",
        "body": """<p>Hey {{firstName}},</p>
<p>Thanks for reaching out about billing. Here are the basics:</p>
<ul>
<li><strong>Monthly plan:</strong> $497/mo, billed on your signup date each month</li>
<li><strong>No contracts:</strong> Cancel anytime, no cancellation fees</li>
<li><strong>Receipts:</strong> Sent automatically to your email after each charge</li>
</ul>
<p>For specific questions about your account, reply to this email and Wallace will personally get back to you within a few hours.</p>
<p>— The Call Taker Team</p>""",
    },
    "general": {
        "subject": "We Got Your Message",
        "body": """<p>Hey {{firstName}},</p>
<p>Got your message — thanks for reaching out. I'm looking into this personally and will get back to you shortly.</p>
<p>If it's urgent, you can always call us directly at <strong>(629) 269-9697</strong>.</p>
<p>— Wallace Dobbs<br>The Call Taker</p>""",
    },
}

# ===================================================
# MILESTONE CHECK-IN EMAILS
# ===================================================

CHECKIN_EMAILS = {
    3: {
        "subject": "Day 3 — How's everything going?",
        "body": """<p>Hey {{firstName}},</p>
<p>You've been live with The Call Taker for 3 days now! Just wanted to check in.</p>
<p><strong>Quick questions:</strong></p>
<ul>
<li>Are calls coming through properly?</li>
<li>Is the AI greeting sounding right for your business?</li>
<li>Getting your text notifications after each call?</li>
</ul>
<p>If anything feels off, just reply to this email. We'll fix it same day.</p>
<p>You're in the early days — this is when we dial everything in to make it perfect for your customers.</p>
<p>— Wallace<br>The Call Taker</p>""",
    },
    7: {
        "subject": "One week in — your first week report",
        "body": """<p>Hey {{firstName}},</p>
<p>One full week with The Call Taker! Here's what matters:</p>
<ul>
<li>Every call answered — no voicemail, no missed revenue</li>
<li>Your customers are getting a professional experience 24/7</li>
<li>You're getting real-time notifications on every call</li>
</ul>
<p>The first week is about trust — knowing the AI handles your calls the way YOU would. If there's anything you'd tweak about how calls are handled, now's the time. Reply and we'll adjust.</p>
<p>— Wallace<br>The Call Taker</p>""",
    },
    14: {
        "subject": "Two weeks — you're in the groove",
        "body": """<p>Hey {{firstName}},</p>
<p>Two weeks live. By now you've probably noticed something: you're not stressing about missed calls anymore.</p>
<p>That's the whole point. Your phone rings, it gets answered, the job gets booked, you get the text. Every time.</p>
<p>Any feedback at all? Things you love, things you'd change? I genuinely want to hear it.</p>
<p>— Wallace<br>The Call Taker</p>""",
    },
    30: {
        "subject": "One month — thank you",
        "body": """<p>Hey {{firstName}},</p>
<p>One month with The Call Taker. Thank you for trusting us with your customers' first impression.</p>
<p>At this point, the AI knows your business. It's handling calls the way you want, booking jobs, and making sure nothing falls through the cracks.</p>
<p><strong>Quick ask:</strong> If The Call Taker has been good for your business, would you mind leaving us a quick review? It helps other HVAC companies find us.</p>
<p>And if you know any other HVAC owners who are losing jobs to voicemail — send them our way. We'll give you a free month for every referral that signs up.</p>
<p>— Wallace<br>The Call Taker</p>""",
    },
    "monthly": {
        "subject": "Monthly check-in from The Call Taker",
        "body": """<p>Hey {{firstName}},</p>
<p>Just your monthly check-in from The Call Taker team.</p>
<p>Everything running smoothly? Any changes to your business hours, services, or how you'd like calls handled?</p>
<p>We're always here to adjust. Just reply if you need anything.</p>
<p>— Wallace<br>The Call Taker</p>""",
    },
}

# ===================================================
# REFERRAL REQUEST TEMPLATES
# ===================================================

REFERRAL_EMAILS = {
    "30day": {
        "subject": "Know any HVAC owners losing calls?",
        "body": """<p>Hey {{firstName}},</p>
<p>You've been with The Call Taker for a month now and I hope it's been solid for your business.</p>
<p><strong>Quick favor:</strong> Do you know 2-3 other HVAC owners who are still sending callers to voicemail?</p>
<p>For every owner you refer who signs up, you get a <strong>free month</strong> of service. No limit.</p>
<p>Just reply with their name and number (or have them call our demo line: (629) 269-9697) and we'll take it from there.</p>
<p>Appreciate you, {{firstName}}.</p>
<p>— Wallace<br>The Call Taker</p>""",
    },
    "post_resolve": {
        "subject": "Glad we fixed that — quick favor?",
        "body": """<p>Hey {{firstName}},</p>
<p>Glad we got that sorted out quickly. That's what we're here for.</p>
<p>While I have you — do you know any other HVAC owners who'd benefit from never missing a call? We'll give you a <strong>free month</strong> for each one that signs up.</p>
<p>Just reply with their info or have them call <strong>(629) 269-9697</strong>.</p>
<p>Thanks for being a great customer.</p>
<p>— Wallace<br>The Call Taker</p>""",
    },
    "happy": {
        "subject": "You seem to love The Call Taker",
        "body": """<p>Hey {{firstName}},</p>
<p>I can tell The Call Taker has been working well for your business — and that makes my day.</p>
<p>I've got a simple ask: <strong>do you know 2-3 HVAC owners who still lose jobs to voicemail?</strong></p>
<p>For every one that signs up, you get a free month. Refer 3 and that's basically a quarter of free service.</p>
<p>Just reply with their name + phone and I'll personally reach out.</p>
<p>— Wallace<br>The Call Taker</p>""",
    },
}


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] SAM: {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass


def ghl_request(method, path, body=None, version="2021-07-28"):
    url = f"{LEGACY_CRM_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {PROVIDER_SYNC_DISABLED}",
        "Version": version,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "SamEngine/1.0 TheCallTaker",
    }
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        log(f"legacy CRM API Error {e.code}: {method} {path} — {error_body[:200]}")
        return None
    except URLError as e:
        log(f"legacy CRM Network Error: {method} {path} — {e.reason}")
        return None
    except Exception as e:
        log(f"legacy CRM Error: {method} {path} — {e}")
        return None


def ntfy(topic, title, msg, priority="default", tags=""):
    try:
        sys.path.insert(0, os.path.expanduser("~/thecalltaker-ops/ops"))
        from trusted_ntfy import post_trusted_ntfy
        post_trusted_ntfy(topic, title, msg, priority=priority, tags=tags, workflow_key="legacy-singleton:sam-engine")
        log(f"trusted ntfy queued: {title}")
    except Exception as e:
        log(f"trusted ntfy suppressed: {e}")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "customers": {},          # contact_id: {start_date, health_score, last_checkin, checkins_sent, issues_resolved, referral_asked}
        "known_message_ids": [],  # Messages Sam has already seen
        "issues_detected": 0,
        "issues_resolved": 0,
        "checkins_sent": 0,
        "referrals_asked": 0,
        "referrals_received": 0,
        "total_auto_responses": 0,
        "total_alerts": 0,
    }


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def load_team_state(filepath):
    """Read Max or Ben state (read-only) for context."""
    if os.path.exists(filepath):
        try:
            with open(filepath) as f:
                return json.load(f)
        except:
            pass
    return {}


def get_all_contacts():
    contacts = []
    page = 1
    while True:
        resp = ghl_request("GET", f"/contacts/?locationId={PROVIDER_SYNC_LOCATION_DISABLED}&limit=100&page={page}")
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


def get_customers(contacts):
    """Filter contacts to only those tagged 'customer' or 'active-client'."""
    customers = []
    for c in contacts:
        tags = [t.lower() for t in c.get("tags", [])]
        if "customer" in tags or "active-client" in tags:
            customers.append(c)
    return customers


def get_conversations(contact_id):
    resp = ghl_request("GET",
        f"/conversations/search?locationId={PROVIDER_SYNC_LOCATION_DISABLED}&contactId={contact_id}",
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


def personalize(template, contact):
    first = contact.get("firstName", contact.get("name", "there"))
    company = contact.get("companyName", "your company")
    text = template.replace("{{firstName}}", first or "there")
    text = text.replace("{{companyName}}", company or "your company")
    return text


def detect_issue_category(text):
    """Detect what category of issue a message is about."""
    text_lower = text.lower()
    for category, keywords in ISSUE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return None


def is_critical(text):
    """Check if message contains critical/escalation keywords."""
    text_lower = text.lower()
    for kw in CRITICAL_KEYWORDS:
        if kw in text_lower:
            return True
    return False


def days_since(date_str):
    """Calculate days since a date string."""
    if not date_str:
        return 999
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00").split("+")[0].split("T")[0])
        return (datetime.now() - dt).days
    except:
        return 999


# ===================================================
# CORE TASKS
# ===================================================

def support_monitor():
    """Every 15 min: Scan customer conversations for issues. Auto-respond + alert."""
    log("=== SAM: Support Monitor ===")
    state = load_state()
    known_ids = set(state.get("known_message_ids", []))
    all_contacts = get_all_contacts()
    customers = get_customers(all_contacts)

    log(f"Monitoring {len(customers)} customers for issues...")

    issues_found = 0
    critical_found = 0

    for customer in customers:
        cid = customer.get("id")
        name = customer.get("firstName", "Unknown")
        company = customer.get("companyName", "Unknown")

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

                # Only look at inbound messages we haven't processed
                if direction != "inbound" or msg_id in known_ids:
                    known_ids.add(msg_id)
                    continue

                body_text = msg.get("body", msg.get("message", ""))
                if not body_text:
                    known_ids.add(msg_id)
                    continue

                known_ids.add(msg_id)

                # Check for CRITICAL keywords first — immediate war room alert
                if is_critical(body_text):
                    critical_found += 1
                    alert_title = f"CRITICAL: {name} ({company})"
                    alert_body = (
                        f"Customer message contains critical keyword!\n\n"
                        f"Message: {body_text[:500]}\n\n"
                        f"ACTION REQUIRED: Call {name} immediately."
                    )
                    ntfy(NTFY_WAR_TOPIC, alert_title, alert_body,
                         priority="urgent", tags="rotating_light,warning,telephone_receiver")
                    state["total_alerts"] = state.get("total_alerts", 0) + 1

                # Check for issue keywords — auto-respond
                category = detect_issue_category(body_text)
                if category:
                    issues_found += 1
                    state["issues_detected"] = state.get("issues_detected", 0) + 1

                    # Send auto-response from knowledge base
                    kb = KNOWLEDGE_BASE[category]
                    subject = personalize(kb["subject"], customer)
                    html_body = personalize(kb["body"], customer)
                    if send_email(cid, subject, html_body):
                        state["total_auto_responses"] = state.get("total_auto_responses", 0) + 1
                        log(f"  Auto-responded to {name}: {category}")

                    # Alert war room about the issue
                    ntfy(NTFY_WAR_TOPIC,
                         f"Customer Issue: {name} — {category}",
                         f"Customer: {name} ({company})\nIssue: {category}\nMessage: {body_text[:300]}\n\nSam auto-responded with KB article. Follow up if needed.",
                         priority="high",
                         tags="wrench,speech_balloon")
                    state["total_alerts"] = state.get("total_alerts", 0) + 1

                elif body_text.strip().upper() not in ["STOP", "UNSUBSCRIBE", "YES", "NO", "OK", "THANKS", "THANK YOU"]:
                    # General inbound message from customer — send warm response + alert
                    kb = KNOWLEDGE_BASE["general"]
                    subject = personalize(kb["subject"], customer)
                    html_body = personalize(kb["body"], customer)
                    send_email(cid, subject, html_body)
                    state["total_auto_responses"] = state.get("total_auto_responses", 0) + 1

                    ntfy(NTFY_WAR_TOPIC,
                         f"Customer Message: {name}",
                         f"Customer: {name} ({company})\nMessage: {body_text[:300]}\n\nSam sent a warm acknowledgment. Review and respond personally.",
                         tags="speech_balloon")

        time.sleep(0.5)

    log(f"Support scan complete. {issues_found} issues, {critical_found} critical alerts.")

    state["known_message_ids"] = list(known_ids)[-1000:]  # Keep last 1000
    save_state(state)
    return {"issues": issues_found, "critical": critical_found, "customers": len(customers)}


def health_scoring():
    """Daily 6am: Score each customer 1-10 on health. Flag at-risk to war room."""
    log("=== SAM: Customer Health Scoring ===")
    state = load_state()
    all_contacts = get_all_contacts()
    customers = get_customers(all_contacts)

    log(f"Scoring {len(customers)} customers...")

    at_risk = []
    healthy = []
    customer_data = state.get("customers", {})

    for customer in customers:
        cid = customer.get("id")
        name = customer.get("firstName", "Unknown")
        company = customer.get("companyName", "Unknown")
        tags = [t.lower() for t in customer.get("tags", [])]

        score = 5  # Base score

        # Engagement: Have they replied to anything recently?
        recent_activity = False
        convos = get_conversations(cid)
        inbound_count = 0
        last_inbound_date = None
        negative_signals = 0

        for convo in convos:
            messages = get_messages(convo.get("id", ""))
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                if msg.get("direction") == "inbound":
                    inbound_count += 1
                    msg_date = msg.get("dateAdded", msg.get("createdAt", ""))
                    if msg_date:
                        last_inbound_date = msg_date
                    body = msg.get("body", msg.get("message", ""))
                    if body and is_critical(body):
                        negative_signals += 1

        # Engagement scoring
        if inbound_count > 0:
            score += 1  # They communicate
            if last_inbound_date and days_since(last_inbound_date) <= 7:
                score += 1  # Recent activity
                recent_activity = True

        # Negative signals
        score -= negative_signals * 2

        # Tenure bonus
        cust_data = customer_data.get(cid, {})
        start_date = cust_data.get("start_date", customer.get("dateAdded", ""))
        tenure_days = days_since(start_date)
        if tenure_days >= 30:
            score += 1  # Survived first month
        if tenure_days >= 90:
            score += 1  # Long-term customer

        # Issues resolved bonus
        issues_resolved = cust_data.get("issues_resolved", 0)
        if issues_resolved > 0:
            score += 1  # We've helped them before — stronger relationship

        # Clamp to 1-10
        score = max(1, min(10, score))

        # Update customer data
        if cid not in customer_data:
            customer_data[cid] = {
                "start_date": start_date or datetime.now().isoformat(),
                "last_checkin": None,
                "checkins_sent": [],
                "issues_resolved": 0,
                "referral_asked": False,
                "last_referral_ask": None,
            }
        customer_data[cid]["health_score"] = score
        customer_data[cid]["last_scored"] = datetime.now().isoformat()

        if score <= 4:
            at_risk.append({"name": name, "company": company, "score": score, "id": cid})
        else:
            healthy.append({"name": name, "company": company, "score": score, "id": cid})

        time.sleep(0.5)

    # Alert war room about at-risk customers
    if at_risk:
        risk_list = "\n".join([
            f"  {r['score']}/10 — {r['name']} ({r['company']})"
            for r in sorted(at_risk, key=lambda x: x['score'])
        ])
        ntfy(NTFY_WAR_TOPIC,
             f"AT-RISK: {len(at_risk)} customers need attention",
             f"These customers scored 4 or below:\n\n{risk_list}\n\nCall them TODAY.",
             priority="urgent",
             tags="warning,telephone_receiver")
        state["total_alerts"] = state.get("total_alerts", 0) + 1

    state["customers"] = customer_data
    save_state(state)

    avg_score = sum(c["score"] for c in at_risk + healthy) / max(len(at_risk) + len(healthy), 1)
    log(f"Health scoring complete. {len(customers)} customers, avg score: {avg_score:.1f}, {len(at_risk)} at-risk.")
    return {"total": len(customers), "at_risk": len(at_risk), "healthy": len(healthy), "avg": avg_score}


def milestone_checkins():
    """Daily 8am: Send milestone emails at day 3, 7, 14, 30, then monthly."""
    log("=== SAM: Milestone Check-ins ===")
    state = load_state()
    all_contacts = get_all_contacts()
    customers = get_customers(all_contacts)
    customer_data = state.get("customers", {})
    sent_count = 0

    for customer in customers:
        cid = customer.get("id")
        name = customer.get("firstName", "Unknown")

        cust = customer_data.get(cid, {})
        start_date = cust.get("start_date", customer.get("dateAdded", ""))
        checkins_sent = cust.get("checkins_sent", [])

        if not start_date:
            continue

        tenure = days_since(start_date)

        # Check each milestone
        milestones_to_check = [3, 7, 14, 30]
        for milestone in milestones_to_check:
            if tenure >= milestone and milestone not in checkins_sent:
                template = CHECKIN_EMAILS.get(milestone)
                if template:
                    subject = personalize(template["subject"], customer)
                    body = personalize(template["body"], customer)
                    if send_email(cid, subject, body):
                        sent_count += 1
                        checkins_sent.append(milestone)
                        log(f"  Day {milestone} check-in sent to {name}")
                    time.sleep(2)

        # Monthly check-ins after day 30 (every 30 days)
        if tenure > 30:
            last_checkin = cust.get("last_checkin")
            days_since_last = days_since(last_checkin) if last_checkin else 999

            if days_since_last >= 30:
                template = CHECKIN_EMAILS["monthly"]
                subject = personalize(template["subject"], customer)
                body = personalize(template["body"], customer)
                if send_email(cid, subject, body):
                    sent_count += 1
                    cust["last_checkin"] = datetime.now().isoformat()
                    log(f"  Monthly check-in sent to {name}")
                time.sleep(2)

        # Save updated checkin data
        if cid not in customer_data:
            customer_data[cid] = {
                "start_date": start_date,
                "health_score": 5,
                "last_checkin": None,
                "checkins_sent": [],
                "issues_resolved": 0,
                "referral_asked": False,
                "last_referral_ask": None,
            }
        customer_data[cid]["checkins_sent"] = checkins_sent

    state["customers"] = customer_data
    state["checkins_sent"] = state.get("checkins_sent", 0) + sent_count
    save_state(state)

    log(f"Check-ins complete. Sent {sent_count} milestone emails.")
    if sent_count > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"Sam sent {sent_count} check-ins",
             f"Milestone check-in emails sent to {sent_count} customers.",
             tags="wave,envelope")

    return sent_count


def referral_requests():
    """Daily 11am: Detect referral moments → alert Wallace to call → email fallback after 48h."""
    log("=== SAM: Referral Requests ===")
    state = load_state()
    all_contacts = get_all_contacts()
    customers = get_customers(all_contacts)
    customer_data = state.get("customers", {})
    alerts_sent = 0
    fallback_emails_sent = 0

    for customer in customers:
        cid = customer.get("id")
        name = customer.get("firstName", "Unknown")
        company = customer.get("companyName", "Unknown")
        phone = customer.get("phone", "No phone on file")

        cust = customer_data.get(cid, {})
        start_date = cust.get("start_date", customer.get("dateAdded", ""))
        health_score = cust.get("health_score", 5)
        last_referral_ask = cust.get("last_referral_ask")
        issues_resolved = cust.get("issues_resolved", 0)
        referral_alerted = cust.get("referral_alerted")        # When Wallace was alerted
        referral_email_sent = cust.get("referral_email_sent")  # When fallback email went out

        tenure = days_since(start_date)

        # Don't ask unhappy customers
        if health_score <= 5:
            continue

        # Don't ask too often (minimum 45 days between full cycles)
        if last_referral_ask and days_since(last_referral_ask) < 45:
            continue

        # ── Detect which trigger fired ──
        trigger = None
        trigger_label = None

        # Trigger 1: 30-day milestone
        if tenure >= 28 and tenure <= 40 and not last_referral_ask:
            trigger = "30day"
            trigger_label = f"30-day milestone — {name} has been a customer for {tenure} days"

        # Trigger 2: Just resolved an issue (gratitude moment)
        elif issues_resolved > 0 and not last_referral_ask:
            trigger = "post_resolve"
            trigger_label = f"Just resolved an issue for {name} — gratitude is high"

        # Trigger 3: Happy customer (score 8+, 30+ days)
        elif health_score >= 8 and tenure >= 30:
            trigger = "happy"
            trigger_label = f"Health score {health_score}/10 — {name} is thriving"

        if not trigger:
            continue

        # ── STEP 1: Alert Wallace to make the call (if not already alerted) ──
        if not referral_alerted:
            script = (
                f"REFERRAL OPPORTUNITY — Call {name} now!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Customer: {name} ({company})\n"
                f"Phone: {phone}\n"
                f"Trigger: {trigger_label}\n"
                f"Health Score: {health_score}/10\n"
                f"Tenure: {tenure} days\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"CALL SCRIPT:\n"
                f"\"Hey {name}, it's Wallace from The Call Taker. "
                f"Just calling to check in — how's everything going with the AI receptionist?\"\n\n"
                f"[Let them talk. Then:]\n\n"
                f"\"Glad to hear it. Quick question — do you know 2 or 3 other HVAC owners "
                f"who are still losing jobs to voicemail? For every one you send our way that "
                f"signs up, I'll give you a free month. No limit.\"\n\n"
                f"[If yes:] \"Perfect — just text me their name and number and I'll take it from there.\"\n"
                f"[If not sure:] \"No rush. If anyone comes to mind this week, just shoot me a text.\"\n\n"
                f"Sam will send a backup email in 48 hours if you don't get to this."
            )
            ntfy(NTFY_WAR_TOPIC,
                 f"CALL {name} — Referral Ask",
                 script,
                 priority="high",
                 tags="telephone_receiver,handshake,moneybag")
            alerts_sent += 1
            cust["referral_alerted"] = datetime.now().isoformat()
            log(f"  War room alert: Call {name} for referral ({trigger})")

        # ── STEP 2: Fallback email if Wallace hasn't called in 48+ hours ──
        elif referral_alerted and not referral_email_sent:
            hours_since_alert = (datetime.now() - datetime.fromisoformat(referral_alerted)).total_seconds() / 3600
            if hours_since_alert >= 48:
                template = REFERRAL_EMAILS.get(trigger, REFERRAL_EMAILS["30day"])
                subject = personalize(template["subject"], customer)
                body = personalize(template["body"], customer)
                if send_email(cid, subject, body):
                    fallback_emails_sent += 1
                    cust["referral_email_sent"] = datetime.now().isoformat()
                    cust["last_referral_ask"] = datetime.now().isoformat()
                    log(f"  48h fallback email sent to {name} ({trigger})")

                    # Let Wallace know the fallback fired
                    ntfy(NTFY_OPS_TOPIC,
                         f"Referral fallback email sent to {name}",
                         f"Wallace didn't call {name} within 48h, so Sam sent the referral email.\nNext time, the personal call converts 5-10x better!",
                         tags="envelope,reminder_ribbon")
                time.sleep(2)

        customer_data[cid] = cust

    state["customers"] = customer_data
    state["referrals_asked"] = state.get("referrals_asked", 0) + alerts_sent + fallback_emails_sent
    save_state(state)

    log(f"Referral check complete. {alerts_sent} call alerts, {fallback_emails_sent} fallback emails.")
    if alerts_sent > 0:
        ntfy(NTFY_OPS_TOPIC,
             f"Sam flagged {alerts_sent} referral calls for Wallace",
             f"{alerts_sent} customers ready for a referral ask.\nWallace: check war room for call scripts. You have 48 hours before Sam sends the email fallback.",
             tags="handshake,telephone_receiver")

    return {"alerts": alerts_sent, "fallback_emails": fallback_emails_sent}


def daily_report():
    """Daily 7pm: Customer health summary to ntfy ops."""
    log("=== SAM: Daily Report ===")
    state = load_state()
    all_contacts = get_all_contacts()
    customers = get_customers(all_contacts)
    customer_data = state.get("customers", {})

    total_customers = len(customers)
    scores = [customer_data.get(c.get("id"), {}).get("health_score", 5) for c in customers]
    avg_score = sum(scores) / max(len(scores), 1)
    at_risk = sum(1 for s in scores if s <= 4)
    healthy = sum(1 for s in scores if s >= 7)

    report = f"""SAM DAILY REPORT — {datetime.now().strftime('%b %d, %Y')}

CUSTOMER HEALTH:
  Total customers: {total_customers}
  Average health score: {avg_score:.1f}/10
  Healthy (7+): {healthy}
  At-risk (4 or below): {at_risk}

ACTIVITY (all time):
  Issues detected: {state.get('issues_detected', 0)}
  Auto-responses sent: {state.get('total_auto_responses', 0)}
  Check-in emails sent: {state.get('checkins_sent', 0)}
  Referral requests sent: {state.get('referrals_asked', 0)}
  War room alerts: {state.get('total_alerts', 0)}

TEAM CONTEXT:"""

    # Read Max/Ben stats for context
    max_state = load_team_state(MAX_STATE_FILE)
    ben_state = load_team_state(BEN_STATE_FILE)
    max_emails = max_state.get("total_emails_sent", 0)
    ben_emails = ben_state.get("total_emails_sent", 0)
    report += f"""
  Max emails sent: {max_emails}
  Ben emails sent: {ben_emails}
  Combined team touches: {max_emails + ben_emails}

STATUS: Sam is active — monitoring every 15 minutes.
Next: Support scan in 15 min, health scoring at 6am, check-ins at 8am."""

    ntfy(NTFY_OPS_TOPIC,
         f"Sam Daily Report — {datetime.now().strftime('%b %d')}",
         report,
         tags="stethoscope,chart_with_upwards_trend")

    log("Daily report sent.")
    return report


def print_status():
    """Print current Sam status."""
    state = load_state()
    all_contacts = get_all_contacts()
    customers = get_customers(all_contacts)
    customer_data = state.get("customers", {})

    scores = [customer_data.get(c.get("id"), {}).get("health_score", 5) for c in customers]
    avg_score = sum(scores) / max(len(scores), 1)
    at_risk = sum(1 for s in scores if s <= 4)

    print("\n" + "=" * 50)
    print("  SAM — STATUS REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print(f"  Total contacts:        {len(all_contacts)}")
    print(f"  Active customers:      {len(customers)}")
    print(f"  Avg health score:      {avg_score:.1f}/10")
    print(f"  At-risk (<=4):         {at_risk}")
    print(f"  Issues detected:       {state.get('issues_detected', 0)}")
    print(f"  Auto-responses sent:   {state.get('total_auto_responses', 0)}")
    print(f"  Check-ins sent:        {state.get('checkins_sent', 0)}")
    print(f"  Referrals asked:       {state.get('referrals_asked', 0)}")
    print(f"  War room alerts:       {state.get('total_alerts', 0)}")
    print("=" * 50 + "\n")


# ===================================================
# MAIN
# ===================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "support":
        result = support_monitor()
        print(f"\n{result['customers']} customers monitored, {result['issues']} issues, {result['critical']} critical.")
    elif cmd == "health":
        result = health_scoring()
        print(f"\n{result['total']} customers scored. Avg: {result['avg']:.1f}/10. {result['at_risk']} at-risk.")
    elif cmd == "checkin":
        count = milestone_checkins()
        print(f"\nSent {count} milestone check-in emails.")
    elif cmd == "referral":
        result = referral_requests()
        print(f"\n{result['alerts']} call alerts sent to Wallace, {result['fallback_emails']} fallback emails sent.")
    elif cmd == "report":
        report = daily_report()
        print(report)
    elif cmd == "status":
        print_status()
    elif cmd == "all":
        log("=== SAM: Full cycle ===")
        support_monitor()
        health_scoring()
        milestone_checkins()
        referral_requests()
        daily_report()
        log("=== SAM: Full cycle complete ===")
        ntfy(NTFY_OPS_TOPIC,
             "Sam completed full cycle",
             f"All tasks done: support + health + checkins + referrals + report.\nTime: {datetime.now().strftime('%I:%M %p')}",
             tags="white_check_mark,stethoscope")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
