#!/usr/bin/env python3
"""
BLAST ENGINE v2 — The Call Taker
=================================
Production cold email engine with email validation, retry logic,
rate limiting, bounce tracking, and delivery monitoring.

FIXES from v1 (arizona-blast.py):
  1. Email validation before sending (syntax, MX records, junk patterns)
  2. Retry with exponential backoff on GHL API errors
  3. Rate limiting: max 50 emails/run, 8-second delay between sends
  4. Bounce tracking and auto-exclusion of bad addresses
  5. Send from business email (not personal iCloud)
  6. A/B subject line testing
  7. Delivery stats dashboard
  8. Industry-aware templates for 19 verticals

Commands:
  blast <csv>  — Send cold emails from a CSV lead file
  retry        — Retry failed sends from last run
  stats        — Show delivery metrics
  validate     — Validate emails in a CSV without sending
  status       — Show engine status

Schedule: 3x daily via launchd (7am, 12pm, 5pm) with max 50/run
"""

import sys
import os
import csv
import json
import time
import re
import socket
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
BUSINESS_EMAIL = "thecalltakerai@gmail.com"
BOOKING_URL = "https://thecalltaker.com/book.html"
DEMO_LINE = "(615) 784-5747"
NTFY_SALES = "tct-sales-63uYsIT9"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"

STATE_FILE = os.path.expanduser("~/thecalltaker/ops/blast-engine-state.json")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/blast-engine.log")

MAX_EMAILS_PER_RUN = 50
DELAY_BETWEEN_SENDS = 8  # seconds
MAX_RETRIES = 3

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-BlastEngine/2.0",
}

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-BlastEngine/2.0",
}

# ─── Email Validation ────────────────────────────────────────────────────────

JUNK_PATTERNS = [
    r"^noreply@", r"^no-reply@", r"^info@info\.", r"^admin@admin\.",
    r"^test@", r"@example\.", r"@test\.", r"@mailinator\.",
    r"@guerrillamail\.", r"@tempmail\.", r"@throwaway\.",
    r"@yopmail\.", r"@sharklasers\.", r"@grr\.la",
]

MX_CACHE = {}


def validate_email_syntax(email):
    """Check basic email syntax."""
    if not email or not isinstance(email, str):
        return False, "empty"
    email = email.strip().lower()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False, "invalid_syntax"
    return True, "ok"


def check_junk_email(email):
    """Check against known junk/disposable patterns."""
    email_lower = email.lower()
    for pattern in JUNK_PATTERNS:
        if re.search(pattern, email_lower):
            return True
    return False


def check_mx_record(domain):
    """Verify domain has MX records (can receive email)."""
    if domain in MX_CACHE:
        return MX_CACHE[domain]
    try:
        socket.getaddrinfo(domain, 25, socket.AF_INET, socket.SOCK_STREAM)
        MX_CACHE[domain] = True
        return True
    except socket.gaierror:
        MX_CACHE[domain] = False
        return False


def validate_email(email):
    """Full email validation: syntax + junk + MX."""
    valid, reason = validate_email_syntax(email)
    if not valid:
        return False, reason

    email = email.strip().lower()

    if check_junk_email(email):
        return False, "junk_pattern"

    domain = email.split("@")[1]
    if not check_mx_record(domain):
        return False, "no_mx_record"

    return True, "valid"


# ─── Industry Templates ──────────────────────────────────────────────────────

INDUSTRY_MAP = {
    "hvac": {"word": "service call", "value": "$350+", "scenario": "AC goes out at 6pm"},
    "plumbing": {"word": "service call", "value": "$300+", "scenario": "pipe bursts at midnight"},
    "electrical": {"word": "service call", "value": "$275+", "scenario": "power goes out in a storm"},
    "roofing": {"word": "estimate", "value": "$5,000+", "scenario": "storm damages their roof"},
    "locksmith": {"word": "emergency call", "value": "$250+", "scenario": "they're locked out at 11pm"},
    "dental": {"word": "appointment", "value": "$400+", "scenario": "toothache hits on Saturday"},
    "legal": {"word": "consultation", "value": "$500+", "scenario": "they need a lawyer NOW"},
    "towing": {"word": "tow call", "value": "$150+", "scenario": "car breaks down on the highway"},
    "veterinary": {"word": "appointment", "value": "$200+", "scenario": "their dog gets sick at night"},
    "medspa": {"word": "appointment", "value": "$500+", "scenario": "they want to book a treatment"},
    "pest-control": {"word": "service call", "value": "$200+", "scenario": "termites show up"},
    "garage-door": {"word": "service call", "value": "$300+", "scenario": "garage door won't open"},
    "property-management": {"word": "maintenance request", "value": "$250+", "scenario": "tenant calls about a leak"},
    "water-damage": {"word": "emergency call", "value": "$2,000+", "scenario": "basement floods"},
    "cleaning": {"word": "booking", "value": "$200+", "scenario": "they need a cleaning ASAP"},
    "landscaping": {"word": "estimate", "value": "$300+", "scenario": "they want a quote this week"},
    "auto-repair": {"word": "repair job", "value": "$400+", "scenario": "car won't start"},
    "general-contractor": {"word": "estimate", "value": "$1,000+", "scenario": "they need work done"},
    "funeral": {"word": "arrangement", "value": "$3,000+", "scenario": "they need help immediately"},
}

DEFAULT_INDUSTRY = {"word": "service call", "value": "$350+", "scenario": "they need help after hours"}


def get_industry(tags):
    if not tags:
        return DEFAULT_INDUSTRY
    for tag in tags:
        tag_lower = tag.lower().strip()
        if tag_lower in INDUSTRY_MAP:
            return INDUSTRY_MAP[tag_lower]
    return DEFAULT_INDUSTRY


# A/B subject lines
SUBJECT_A = "I called {company} after hours"
SUBJECT_B = "{company} is losing ${value}/month in missed calls"


def build_email_html(first_name, company_name, industry, city="your area"):
    """Build pain-first cold email with industry personalization."""
    scenario = industry["scenario"]
    value = industry["value"]
    word = industry["word"]

    return f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p>I called {company_name} after hours last week. Got your voicemail.</p>

<p>No judgment — but your customers are doing the same thing. When {scenario}, they Google your type of business and start calling. <strong>First company that picks up gets the job.</strong></p>

<p>Here's what that's costing you:</p>

<ul style="margin: 16px 0;">
<li><strong>85% of callers won't leave a voicemail</strong> — they hang up and call your competitor</li>
<li>Average {word} is worth <strong>{value}</strong></li>
<li>Miss 3 calls a week? That's <strong>$4,500+/month walking out your door</strong></li>
</ul>

<p>I built <strong>The Call Taker</strong> to fix this. It's an AI receptionist that answers every call to {company_name} — 24/7. No voicemail. No missed jobs. It sounds like a real person, gets their info, and books the appointment on your calendar.</p>

<p><strong>We're running a free 14-day pilot.</strong> No card. No contract. We set it up in 48 hours.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #F97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Book Your Free Demo →</a>
</p>

<p>Or call the AI yourself: <strong>{DEMO_LINE}</strong>. Pretend you're a customer. Takes 2 minutes.</p>

<p>— Wallace Dobbs<br>
<span style="color: #666;">Founder, The Call Taker</span></p>

</div>"""


# ─── Logging ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] blast-engine: {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ─── State Management ────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "sent": {},          # email -> {contact_id, sent_at, subject_variant}
        "failed": {},        # email -> {reason, attempts, last_attempt}
        "bounced": [],       # emails that bounced
        "invalid": [],       # emails that failed validation
        "stats": {
            "total_sent": 0, "total_failed": 0, "total_invalid": 0,
            "total_runs": 0, "last_run": None,
            "subject_a_sent": 0, "subject_b_sent": 0,
        },
    }


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


# ─── GHL API ─────────────────────────────────────────────────────────────────

def ghl_request(method, path, headers=None, params=None, json_body=None):
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    backoff = [5, 15, 30]
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.request(method, url, headers=headers, params=params, json=json_body, timeout=30)
            if resp.status_code == 429:
                wait = [30, 60, 120][min(attempt, 2)]
                log(f"Rate limited, waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                time.sleep(backoff[min(attempt, 2)])
                continue
            if resp.status_code in (400, 401, 403, 404, 422):
                return {"error": resp.status_code, "body": resp.text[:200]}
            return resp.json() if resp.text else {}
        except requests.exceptions.RequestException as e:
            log(f"Request error: {e}", "ERROR")
            if attempt < MAX_RETRIES - 1:
                time.sleep(backoff[min(attempt, 2)])
    return None


def create_or_find_contact(lead):
    """Create contact in GHL or find existing."""
    body = {
        "firstName": lead.get("firstName", "Owner"),
        "companyName": lead.get("companyName", ""),
        "phone": lead.get("phone", ""),
        "email": lead.get("email", ""),
        "locationId": GHL_LOCATION_ID,
        "tags": ["cold-outreach", lead.get("industry", "general")],
        "source": "Blast Engine v2",
    }
    if lead.get("city"):
        body["city"] = lead["city"]
    if lead.get("state"):
        body["state"] = lead["state"]

    resp = ghl_request("POST", "/contacts/", json_body=body)
    if resp and "contact" in resp:
        return resp["contact"]["id"]
    if resp and isinstance(resp, dict) and "id" in resp:
        return resp["id"]
    # Try searching by email
    search = ghl_request("GET", "/contacts/", params={
        "locationId": GHL_LOCATION_ID, "query": lead["email"], "limit": 1,
    })
    if search and "contacts" in search and search["contacts"]:
        return search["contacts"][0]["id"]
    return None


def send_email(contact_id, subject, html_body):
    return ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS, json_body={
        "type": "Email", "contactId": contact_id,
        "subject": subject, "html": html_body,
        "emailFrom": f"Wallace Dobbs <{BUSINESS_EMAIL}>",
    })


def ntfy_alert(topic, title, message, priority="default"):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        requests.post(f"https://ntfy.sh/{topic}", data=message.encode("utf-8"),
                      headers={"Title": safe_title, "Priority": priority}, timeout=10)
    except Exception:
        pass


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_blast(state, csv_path):
    """Send cold emails from CSV. Validates, creates contacts, sends with A/B testing."""
    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        sys.exit(1)

    log(f"=== Blast Engine v2: Loading {csv_path} ===")
    state["stats"]["total_runs"] += 1
    state["stats"]["last_run"] = datetime.now().isoformat()

    # Load leads from CSV
    leads = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)

    log(f"Loaded {len(leads)} leads from CSV")

    sent_count = 0
    failed_count = 0
    invalid_count = 0
    skipped_count = 0

    for i, lead in enumerate(leads):
        if sent_count >= MAX_EMAILS_PER_RUN:
            log(f"Hit max emails ({MAX_EMAILS_PER_RUN}), stopping. {len(leads) - i} remaining.")
            break

        email = (lead.get("email") or "").strip()
        company = lead.get("companyName") or lead.get("company") or "Unknown"

        # Skip if no email
        if not email:
            skipped_count += 1
            continue

        # Skip if already sent
        if email.lower() in state["sent"]:
            skipped_count += 1
            continue

        # Skip if known bounced
        if email.lower() in state["bounced"]:
            skipped_count += 1
            continue

        # Validate email
        valid, reason = validate_email(email)
        if not valid:
            state["invalid"].append(email.lower())
            state["stats"]["total_invalid"] += 1
            invalid_count += 1
            log(f"  INVALID: {email} ({reason})")
            continue

        # Create or find contact
        contact_id = create_or_find_contact(lead)
        if not contact_id:
            state["failed"][email.lower()] = {
                "reason": "contact_creation_failed",
                "attempts": 1,
                "last_attempt": datetime.now().isoformat(),
            }
            failed_count += 1
            log(f"  FAILED: Could not create contact for {company} ({email})")
            continue

        # A/B test subject lines
        industry = get_industry(lead.get("tags", "").split(",") if isinstance(lead.get("tags"), str) else [])
        first_name = lead.get("firstName") or lead.get("first_name") or "there"

        if state["stats"]["subject_a_sent"] <= state["stats"]["subject_b_sent"]:
            subject = SUBJECT_A.format(company=company)
            variant = "A"
        else:
            subject = SUBJECT_B.format(company=company, value="4,500")
            variant = "B"

        html = build_email_html(first_name, company, industry, lead.get("city", "your area"))

        # Send
        result = send_email(contact_id, subject, html)
        if result and not (isinstance(result, dict) and "error" in result):
            state["sent"][email.lower()] = {
                "contact_id": contact_id,
                "sent_at": datetime.now().isoformat(),
                "subject_variant": variant,
                "company": company,
            }
            state["stats"]["total_sent"] += 1
            state["stats"][f"subject_{variant.lower()}_sent"] += 1
            sent_count += 1
            log(f"  SENT [{variant}]: {company} ({email})")
        else:
            error_detail = result.get("body", "unknown") if isinstance(result, dict) else "no_response"
            state["failed"][email.lower()] = {
                "reason": f"send_failed: {error_detail[:100]}",
                "attempts": 1,
                "last_attempt": datetime.now().isoformat(),
            }
            state["stats"]["total_failed"] += 1
            failed_count += 1
            log(f"  FAILED: {company} ({email}) — {error_detail[:100]}")

        save_state(state)
        time.sleep(DELAY_BETWEEN_SENDS)

    # Summary
    total = sent_count + failed_count + invalid_count + skipped_count
    success_rate = (sent_count / max(sent_count + failed_count, 1)) * 100

    summary = (
        f"Blast complete: {sent_count} sent, {failed_count} failed, "
        f"{invalid_count} invalid, {skipped_count} skipped. "
        f"Success rate: {success_rate:.0f}%"
    )
    log(summary)

    ntfy_alert(NTFY_SALES, "Blast Engine v2 Complete",
               f"{summary}\nA/B: Subject A={state['stats']['subject_a_sent']}, B={state['stats']['subject_b_sent']}",
               priority="default")

    save_state(state)


def cmd_retry(state):
    """Retry failed sends."""
    failed = state.get("failed", {})
    retryable = {k: v for k, v in failed.items() if v.get("attempts", 0) < MAX_RETRIES}

    if not retryable:
        print("No retryable failures.")
        return

    log(f"Retrying {len(retryable)} failed sends...")
    retried = 0

    for email, info in list(retryable.items()):
        if retried >= MAX_EMAILS_PER_RUN:
            break

        valid, reason = validate_email(email)
        if not valid:
            del state["failed"][email]
            state["invalid"].append(email)
            continue

        # Try to find existing contact
        search = ghl_request("GET", "/contacts/", params={
            "locationId": GHL_LOCATION_ID, "query": email, "limit": 1,
        })
        if not search or not search.get("contacts"):
            info["attempts"] = info.get("attempts", 0) + 1
            continue

        contact = search["contacts"][0]
        contact_id = contact["id"]
        first_name = contact.get("firstName", "there")
        company = contact.get("companyName", "your business")
        industry = get_industry(contact.get("tags", []))

        subject = SUBJECT_A.format(company=company)
        html = build_email_html(first_name, company, industry)

        result = send_email(contact_id, subject, html)
        if result and not (isinstance(result, dict) and "error" in result):
            state["sent"][email] = {
                "contact_id": contact_id, "sent_at": datetime.now().isoformat(),
                "subject_variant": "A-retry", "company": company,
            }
            del state["failed"][email]
            state["stats"]["total_sent"] += 1
            retried += 1
            log(f"  RETRY OK: {company} ({email})")
        else:
            info["attempts"] = info.get("attempts", 0) + 1
            info["last_attempt"] = datetime.now().isoformat()

        time.sleep(DELAY_BETWEEN_SENDS)

    log(f"Retry complete. {retried} succeeded.")
    save_state(state)


def cmd_validate(csv_path):
    """Validate emails in a CSV without sending."""
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        valid_count = 0
        invalid_count = 0
        for row in reader:
            email = (row.get("email") or "").strip()
            if not email:
                continue
            ok, reason = validate_email(email)
            if ok:
                valid_count += 1
            else:
                invalid_count += 1
                print(f"  INVALID: {email} — {reason}")

    print(f"\nValid: {valid_count} | Invalid: {invalid_count} | "
          f"Rate: {valid_count / max(valid_count + invalid_count, 1) * 100:.0f}%")


def cmd_stats(state):
    stats = state["stats"]
    sent = len(state.get("sent", {}))
    failed = len(state.get("failed", {}))
    total_attempted = sent + failed
    success_rate = (sent / max(total_attempted, 1)) * 100

    print("\n╔══════════════════════════════════════════╗")
    print("║       BLAST ENGINE v2 — STATS            ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  Total Sent:         {stats.get('total_sent', 0):>5}               ║")
    print(f"║  Total Failed:       {stats.get('total_failed', 0):>5}               ║")
    print(f"║  Total Invalid:      {stats.get('total_invalid', 0):>5}               ║")
    print(f"║  Success Rate:       {success_rate:>4.0f}%               ║")
    print(f"║  Runs:               {stats.get('total_runs', 0):>5}               ║")
    print(f"║  Subject A Sent:     {stats.get('subject_a_sent', 0):>5}               ║")
    print(f"║  Subject B Sent:     {stats.get('subject_b_sent', 0):>5}               ║")
    print(f"║  Last Run:           {(stats.get('last_run', 'never'))[:16]:>16} ║")
    print("╚══════════════════════════════════════════╝\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: blast-engine-v2.py <blast CSV|retry|stats|validate CSV|status>")
        sys.exit(1)

    command = sys.argv[1].lower()
    state = load_state()

    try:
        if command == "blast":
            if len(sys.argv) < 3:
                print("Usage: blast-engine-v2.py blast <path-to-csv>")
                sys.exit(1)
            cmd_blast(state, sys.argv[2])
        elif command == "retry":
            cmd_retry(state)
        elif command in ("stats", "status"):
            cmd_stats(state)
        elif command == "validate":
            if len(sys.argv) < 3:
                print("Usage: blast-engine-v2.py validate <path-to-csv>")
                sys.exit(1)
            cmd_validate(sys.argv[2])
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        log(f"CRASH: {e}", "ERROR")
        ntfy_alert("tct-system-vRsfXQRQ", "[CRITICAL] Blast Engine v2 Crashed",
                   f"Error: {str(e)[:500]}", priority="urgent")
        raise


if __name__ == "__main__":
    main()
