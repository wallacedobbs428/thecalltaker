#!/usr/bin/env python3
"""
BLAST ENGINE v3 — The Call Taker
=================================
Upgraded cold email engine with deliverability monitoring, address rotation,
A/B auto-promotion, bounce categorization, and plain-text/HTML dual-format emails.

FIXES from v2 (63% failure rate):
  1. Max 40 emails per sending address per day (not 50 total)
  2. Minimum 90-second gap between sends from same address (not 8 seconds)
  3. Rotate across 5 sending address aliases (wallace@, hello@, support@, info@, team@)
  4. Unsubscribe link in every email footer (legally required)
  5. Plain-text AND HTML versions for every email
  6. Personalization: every email includes business name and city; owner name when available
  7. Deliverability health check command with per-address bounce rate monitoring
  8. A/B auto-promotion: winner locked after 100 sends per variant per industry
  9. Bounce categorization: hard, soft, spam_block, domain_reject, rate_limit
  10. DNS MX record checks via dns.resolver (falls back to socket)

Commands:
  blast <csv>     — Send cold emails from a CSV lead file
  retry           — Retry failed sends from last run
  stats           — Show delivery metrics and A/B results
  validate <csv>  — Validate emails in a CSV without sending
  status          — Show engine status
  health          — Run deliverability health check, write deliverability-health.json

Schedule: 3x daily via launchd (7am, 12pm, 5pm)
"""

import sys
import os
import csv
import json
import time
import re
import socket
import textwrap
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── Local Detection ────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from local_detect import is_local, get_lead_city
except ImportError:
    def is_local(c): return False
    def get_lead_city(c): return ""

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY      = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID  = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL     = "https://services.leadconnectorhq.com"
BOOKING_URL      = "https://thecalltaker.com/book.html"
DEMO_LINE        = "(615) 784-5747"
UNSUBSCRIBE_BASE = "https://thecalltaker.com/unsubscribe?id="

NTFY_SALES    = "tct-sales-63uYsIT9"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_SYSTEM   = "tct-system-vRsfXQRQ"

STATE_FILE        = os.path.expanduser("~/thecalltaker/ops/blast-engine-state.json")
LOG_FILE          = os.path.expanduser("~/thecalltaker/ops/blast-engine.log")
HEALTH_FILE       = os.path.expanduser("~/thecalltaker/ops/deliverability-health.json")

# Sending limits — root cause fix for 63% failure rate
MAX_PER_ADDRESS_PER_DAY  = 40    # per alias per calendar day
MIN_GAP_BETWEEN_SENDS    = 90    # seconds between sends from same address
MAX_RETRIES              = 3
BOUNCE_RATE_FLAG_PCT     = 3.0   # flag address if implied bounce rate exceeds this

# 5 sending aliases rotated round-robin
# GHL uses emailFrom to specify sender — alias must be verified in GHL
SENDING_ALIASES = [
    "Wallace Dobbs <wallace@thecalltaker.com>",
    "The Call Taker <hello@thecalltaker.com>",
    "The Call Taker Support <support@thecalltaker.com>",
    "The Call Taker <info@thecalltaker.com>",
    "The Call Taker Team <team@thecalltaker.com>",
]

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-BlastEngine/3.0",
}

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-BlastEngine/3.0",
}

# ─── Bounce Categorization ───────────────────────────────────────────────────
# Maps GHL error patterns to bounce types for deliverability analysis.

BOUNCE_PATTERNS = {
    "hard":          [r"550", r"551", r"553", r"invalid address", r"does not exist",
                      r"user unknown", r"no such user", r"address rejected"],
    "soft":          [r"421", r"450", r"451", r"452", r"mailbox full", r"temporarily",
                      r"try again", r"over quota"],
    "spam_block":    [r"554", r"spam", r"blocked", r"blacklist", r"spamhaus",
                      r"policy", r"content filter", r"rejected.*spam"],
    "domain_reject": [r"domain not found", r"no mx", r"mx record", r"unresolvable",
                      r"bad destination mailbox address"],
    "rate_limit":    [r"429", r"too many", r"rate limit", r"throttl"],
}


def categorize_bounce(error_text):
    """Categorize a delivery error string into a bounce type."""
    if not error_text:
        return "unknown"
    text = error_text.lower()
    for btype, patterns in BOUNCE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text):
                return btype
    return "unknown"


# ─── Email Validation ────────────────────────────────────────────────────────

JUNK_PATTERNS = [
    r"^noreply@", r"^no-reply@", r"^donotreply@", r"^do-not-reply@",
    r"^info@info\.", r"^admin@admin\.", r"^test@", r"@example\.",
    r"@test\.", r"@mailinator\.", r"@guerrillamail\.", r"@tempmail\.",
    r"@throwaway\.", r"@yopmail\.", r"@sharklasers\.", r"@grr\.la",
    r"@trashmail\.", r"@fakeinbox\.", r"@maildrop\.", r"@spamgourmet\.",
]

MX_CACHE = {}   # domain -> True/False, cached for session


def validate_email_syntax(email):
    if not email or not isinstance(email, str):
        return False, "empty"
    email = email.strip().lower()
    if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
        return False, "invalid_syntax"
    return True, "ok"


def check_junk_email(email):
    email_lower = email.lower()
    for pattern in JUNK_PATTERNS:
        if re.search(pattern, email_lower):
            return True
    return False


def check_mx_record(domain):
    """Verify domain has MX records. Tries dns.resolver first, falls back to socket."""
    if domain in MX_CACHE:
        return MX_CACHE[domain]
    # Try dnspython if available
    try:
        import dns.resolver
        dns.resolver.resolve(domain, "MX")
        MX_CACHE[domain] = True
        return True
    except ImportError:
        pass
    except Exception:
        MX_CACHE[domain] = False
        return False
    # Fallback: TCP connect check on port 25
    try:
        socket.setdefaulttimeout(5)
        socket.getaddrinfo(domain, 25, socket.AF_INET, socket.SOCK_STREAM)
        MX_CACHE[domain] = True
        return True
    except socket.gaierror:
        MX_CACHE[domain] = False
        return False


def validate_email(email):
    """Full validation: syntax + junk patterns + MX record."""
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
    "hvac":               {"word": "service call",       "value": "$350",   "job": "HVAC call",         "scenario": "AC breaks at 6pm"},
    "plumbing":           {"word": "service call",       "value": "$300",   "job": "plumbing call",     "scenario": "pipe bursts at midnight"},
    "electrical":         {"word": "service call",       "value": "$275",   "job": "electrical call",   "scenario": "power goes out in a storm"},
    "roofing":            {"word": "estimate",           "value": "$5,000", "job": "roofing job",       "scenario": "storm hits a neighborhood"},
    "locksmith":          {"word": "lockout call",       "value": "$150",   "job": "lockout",           "scenario": "someone's locked out at 11pm"},
    "dental":             {"word": "appointment",        "value": "$400",   "job": "patient visit",     "scenario": "toothache hits on a Saturday"},
    "legal":              {"word": "consultation",       "value": "$500",   "job": "case intake",       "scenario": "they need a lawyer now"},
    "towing":             {"word": "tow call",           "value": "$150",   "job": "tow",               "scenario": "car breaks down on the highway"},
    "veterinary":         {"word": "appointment",        "value": "$200",   "job": "patient visit",     "scenario": "a pet gets sick at night"},
    "medspa":             {"word": "appointment",        "value": "$500",   "job": "booking",           "scenario": "they want to book a treatment"},
    "pest-control":       {"word": "service call",       "value": "$200",   "job": "service call",      "scenario": "termites show up"},
    "garage-door":        {"word": "service call",       "value": "$300",   "job": "repair call",       "scenario": "garage door won't open"},
    "property-management":{"word": "maintenance request","value": "$250",   "job": "maintenance call",  "scenario": "tenant calls about a leak"},
    "water-damage":       {"word": "emergency call",     "value": "$2,000", "job": "restoration job",   "scenario": "a basement floods"},
    "cleaning":           {"word": "booking",            "value": "$200",   "job": "cleaning job",      "scenario": "they need a cleaning ASAP"},
    "landscaping":        {"word": "estimate",           "value": "$300",   "job": "landscaping job",   "scenario": "they want a quote this week"},
    "auto-repair":        {"word": "repair job",         "value": "$400",   "job": "repair job",        "scenario": "car won't start"},
    "general-contractor": {"word": "estimate",           "value": "$1,000", "job": "project",           "scenario": "they need work done"},
    "funeral":            {"word": "arrangement",        "value": "$3,000", "job": "arrangement",       "scenario": "a family needs help immediately"},
}

DEFAULT_INDUSTRY = {"word": "service call", "value": "$350", "job": "call", "scenario": "they need help after hours"}


def get_industry_data(tags):
    """Return industry dict from a list of tag strings."""
    if not tags:
        return "general", DEFAULT_INDUSTRY
    for tag in tags:
        key = tag.lower().strip()
        if key in INDUSTRY_MAP:
            return key, INDUSTRY_MAP[key]
    return "general", DEFAULT_INDUSTRY


# ─── A/B Subject Line Registry ───────────────────────────────────────────────
# Two variants per industry. After 100 sends of EACH, auto-lock the winner.
# Winner = higher open-implied conversion (reply rate tracked via GHL tags).
# Until 100 sends, rotate evenly. After lock, use winner only.

SUBJECT_VARIANTS = {
    # variant A: secret shopper angle
    "A": "I called {company} — nobody answered",
    # variant B: revenue loss angle
    "B": "{company} is losing {value}/month",
}

AB_THRESHOLD = 100  # sends per variant before auto-promoting winner


def get_ab_subject(state, industry_key, company, value):
    """
    Return (subject, variant) for this send.
    Rotates A/B evenly until threshold, then uses locked winner.
    """
    ab = state.setdefault("ab_testing", {})
    ind = ab.setdefault(industry_key, {
        "a_sent": 0, "b_sent": 0,
        "a_replies": 0, "b_replies": 0,
        "winner": None, "locked_at": None,
    })

    # If winner already locked, use it
    if ind["winner"]:
        variant = ind["winner"]
        subject = SUBJECT_VARIANTS[variant].format(company=company, value=value)
        return subject, variant

    # Check if we have enough data to auto-promote
    if ind["a_sent"] >= AB_THRESHOLD and ind["b_sent"] >= AB_THRESHOLD:
        a_rate = ind["a_replies"] / max(ind["a_sent"], 1)
        b_rate = ind["b_replies"] / max(ind["b_sent"], 1)
        winner = "A" if a_rate >= b_rate else "B"
        ind["winner"] = winner
        ind["locked_at"] = datetime.now().isoformat()
        log(f"A/B auto-promoted [{industry_key}]: Variant {winner} wins "
            f"(A={a_rate:.3f} B={b_rate:.3f})")
        subject = SUBJECT_VARIANTS[winner].format(company=company, value=value)
        return subject, winner

    # Still testing — rotate evenly
    if ind["a_sent"] <= ind["b_sent"]:
        variant = "A"
    else:
        variant = "B"
    subject = SUBJECT_VARIANTS[variant].format(company=company, value=value)
    return subject, variant


# ─── Address Rotation ────────────────────────────────────────────────────────

def get_sending_alias(state):
    """
    Pick the next available sending alias using round-robin rotation.
    Respects MAX_PER_ADDRESS_PER_DAY and MIN_GAP_BETWEEN_SENDS.
    Returns (alias_string, alias_index) or (None, None) if all exhausted.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    addr_state = state.setdefault("address_rotation", {})

    for offset in range(len(SENDING_ALIASES)):
        # Start from last used index + 1 to distribute evenly
        last_idx = state.get("last_alias_index", -1)
        idx = (last_idx + 1 + offset) % len(SENDING_ALIASES)
        alias = SENDING_ALIASES[idx]
        alias_key = alias.split("<")[-1].rstrip(">").strip()

        rec = addr_state.setdefault(alias_key, {
            "day": today, "sent_today": 0, "last_sent_at": None, "failed": 0,
        })

        # Reset daily counter if new day
        if rec["day"] != today:
            rec["day"] = today
            rec["sent_today"] = 0
            rec["last_sent_at"] = None

        # Check daily cap
        if rec["sent_today"] >= MAX_PER_ADDRESS_PER_DAY:
            continue

        # Check minimum gap
        if rec["last_sent_at"]:
            last_dt = datetime.fromisoformat(rec["last_sent_at"])
            elapsed = (datetime.now() - last_dt).total_seconds()
            if elapsed < MIN_GAP_BETWEEN_SENDS:
                wait_remaining = int(MIN_GAP_BETWEEN_SENDS - elapsed)
                log(f"  Alias {alias_key}: {wait_remaining}s gap remaining, trying next")
                continue

        return alias, idx, alias_key

    return None, None, None


def record_alias_send(state, alias_key, success):
    """Update alias rotation state after a send attempt."""
    rec = state["address_rotation"].get(alias_key, {})
    if success:
        rec["sent_today"] = rec.get("sent_today", 0) + 1
        rec["last_sent_at"] = datetime.now().isoformat()
    else:
        rec["failed"] = rec.get("failed", 0) + 1
    state["address_rotation"][alias_key] = rec


# ─── Email Template Builder ───────────────────────────────────────────────────

def _unsubscribe_footer_html(contact_id):
    url = f"{UNSUBSCRIBE_BASE}{contact_id}"
    return (
        f'<p style="margin-top:32px;font-size:12px;color:#999;">'
        f'You\'re receiving this because your business may benefit from AI call answering. '
        f'<a href="{url}" style="color:#999;">Unsubscribe</a></p>'
    )


def _unsubscribe_footer_text(contact_id):
    url = f"{UNSUBSCRIBE_BASE}{contact_id}"
    return f"\n\n---\nTo unsubscribe: {url}"


def _greeting(first_name):
    """Return a natural greeting. Never 'Dear Business Owner'."""
    if first_name and first_name.lower() not in ("", "owner", "there", "n/a", "na"):
        return f"Hi {first_name},"
    return "Hi,"


def build_email_html(first_name, company, industry_data, city, contact_id):
    """Standard national email — short, personal, no bullet lists."""
    scenario  = industry_data["scenario"]
    value     = industry_data["value"]
    word      = industry_data["word"]
    city_line = f" in {city}" if city and city.lower() not in ("", "your area") else ""
    greeting  = _greeting(first_name)
    footer    = _unsubscribe_footer_html(contact_id)

    return f"""<div style="font-family:Georgia,serif;color:#111;max-width:560px;line-height:1.7;font-size:16px;">

<p>{greeting}</p>

<p>I called {company}{city_line} after hours last week. Got voicemail.</p>

<p>When {scenario}, your customers start Googling and calling. The first company to pick up gets the job — not the best one, the fastest one. A missed {word} at {value} is real money gone.</p>

<p>I built something called <strong>The Call Taker</strong>. It's an AI that answers every call to {company} — nights, weekends, whenever. It sounds like a real person, gets the caller's info, and books the appointment.</p>

<p>We're running a free 14-day pilot right now. No card required, no contract, setup in 48 hours.</p>

<p>You can hear it yourself by calling <strong>{DEMO_LINE}</strong> — pretend you're a customer. Takes two minutes.</p>

<p>Worth a quick look? <a href="{BOOKING_URL}" style="color:#f97316;font-weight:600;">Book a free 15-min demo</a> and I'll show you the whole thing live.</p>

<p style="margin-top:24px;">— Wallace Dobbs<br>
<span style="font-size:14px;color:#666;">Founder, The Call Taker</span></p>

{footer}
</div>"""


def build_email_text(first_name, company, industry_data, city, contact_id):
    """Plain-text version of the national email."""
    scenario  = industry_data["scenario"]
    value     = industry_data["value"]
    word      = industry_data["word"]
    city_line = f" in {city}" if city and city.lower() not in ("", "your area") else ""
    greeting  = _greeting(first_name)
    footer    = _unsubscribe_footer_text(contact_id)

    body = textwrap.dedent(f"""
    {greeting}

    I called {company}{city_line} after hours last week. Got voicemail.

    When {scenario}, your customers start Googling and calling. The first company to
    pick up gets the job. A missed {word} at {value} is real money gone.

    I built something called The Call Taker. It's an AI that answers every call to
    {company} — nights, weekends, whenever. Sounds like a real person, gets the info,
    books the appointment.

    We're running a free 14-day pilot. No card, no contract, 48-hour setup.

    Hear it yourself: call {DEMO_LINE} and pretend you're a customer. Two minutes.

    Want to see the whole thing? Book a free 15-min demo:
    {BOOKING_URL}

    — Wallace Dobbs
    Founder, The Call Taker
    """).strip()
    return body + footer


def build_local_email_html(first_name, company, industry_data, city, contact_id):
    """Local Middle TN email — in-person CTA."""
    scenario      = industry_data["scenario"]
    value         = industry_data["value"]
    word          = industry_data["word"]
    city_display  = city if city and city.lower() not in ("", "your area") else "the Nashville area"
    greeting      = _greeting(first_name)
    footer        = _unsubscribe_footer_html(contact_id)

    return f"""<div style="font-family:Georgia,serif;color:#111;max-width:560px;line-height:1.7;font-size:16px;">

<p>{greeting}</p>

<p>I called {company} after hours last week. Got voicemail.</p>

<p>When {scenario}, your customers start calling around. First company that answers gets the {word} — and those run {value} each. That adds up fast.</p>

<p>I'm Wallace. I'm based in Brentwood and I built something called <strong>The Call Taker</strong> — an AI that answers every call to {company} around the clock. No voicemail. No missed jobs.</p>

<p>Since we're both in {city_display}, I'd rather show you in person than send a link. I can stop by, pull it up on my phone, and you can hear the AI take a live call. Takes ten minutes.</p>

<p><strong>Would it be worth ten minutes this week?</strong> Just reply with a day that works.</p>

<p style="margin-top:24px;">— Wallace Dobbs<br>
<span style="font-size:14px;color:#666;">Founder, The Call Taker | Brentwood, TN | {DEMO_LINE}</span></p>

{footer}
</div>"""


def build_local_email_text(first_name, company, industry_data, city, contact_id):
    """Plain-text local email."""
    scenario      = industry_data["scenario"]
    value         = industry_data["value"]
    word          = industry_data["word"]
    city_display  = city if city and city.lower() not in ("", "your area") else "the Nashville area"
    greeting      = _greeting(first_name)
    footer        = _unsubscribe_footer_text(contact_id)

    body = textwrap.dedent(f"""
    {greeting}

    I called {company} after hours last week. Got voicemail.

    When {scenario}, customers start calling around. First company that answers gets
    the {word}. Those run {value} each — that adds up fast.

    I'm Wallace, based in Brentwood. I built something called The Call Taker — an AI
    that answers every call to {company} around the clock.

    Since we're both in {city_display}, I'd rather show you in person. I can stop by,
    pull it up on my phone, and you'll hear the AI live. Ten minutes.

    Worth it this week? Just reply with a day that works.

    — Wallace Dobbs
    Founder, The Call Taker | Brentwood, TN | {DEMO_LINE}
    """).strip()
    return body + footer


# ─── Logging ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] blast-v3: {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ─── State Management ────────────────────────────────────────────────────────

def _empty_state():
    return {
        "sent":             {},   # email -> {contact_id, sent_at, variant, company, alias, industry}
        "failed":           {},   # email -> {reason, bounce_type, attempts, last_attempt}
        "bounced_hard":     [],   # hard bounce emails — never retry
        "bounced_soft":     [],   # soft bounce emails — may retry later
        "invalid":          [],   # failed email validation
        "address_rotation": {},   # alias_key -> {day, sent_today, last_sent_at, failed}
        "last_alias_index": -1,
        "ab_testing":       {},   # industry_key -> {a_sent, b_sent, a_replies, b_replies, winner, locked_at}
        "stats": {
            "total_sent":    0,
            "total_failed":  0,
            "total_invalid": 0,
            "total_runs":    0,
            "last_run":      None,
        },
    }


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
            # Backfill any missing keys from empty state
            empty = _empty_state()
            for k, v in empty.items():
                data.setdefault(k, v)
            return data
        except (json.JSONDecodeError, IOError):
            log("State file corrupted, starting fresh.", "WARN")
    return _empty_state()


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, default=str)
    os.replace(tmp, STATE_FILE)


# ─── GHL API ─────────────────────────────────────────────────────────────────

def ghl_request(method, path, headers=None, params=None, json_body=None, timeout=30):
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    backoff = [5, 15, 30]
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.request(
                method, url, headers=headers,
                params=params, json=json_body, timeout=timeout,
            )
            if resp.status_code == 429:
                wait = [30, 60, 120][min(attempt, 2)]
                log(f"Rate limited on {path}, waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                log(f"GHL 5xx ({resp.status_code}) on {path}, attempt {attempt+1}", "WARN")
                time.sleep(backoff[min(attempt, 2)])
                continue
            if resp.status_code in (400, 401, 403, 404, 422):
                return {"error": resp.status_code, "body": resp.text[:300]}
            return resp.json() if resp.text else {}
        except requests.exceptions.Timeout:
            log(f"Timeout on {path}, attempt {attempt+1}", "WARN")
            time.sleep(backoff[min(attempt, 2)])
        except requests.exceptions.RequestException as e:
            log(f"Request error on {path}: {e}", "ERROR")
            if attempt < MAX_RETRIES - 1:
                time.sleep(backoff[min(attempt, 2)])
    return None


def create_or_find_contact(lead):
    """Create contact in GHL or return ID of existing match."""
    tags = ["cold-email-v3"]
    if lead.get("industry"):
        tags.append(lead["industry"])

    body = {
        "firstName":   lead.get("firstName") or lead.get("first_name") or "",
        "lastName":    lead.get("lastName")  or lead.get("last_name")  or "",
        "companyName": lead.get("companyName") or lead.get("company") or "",
        "phone":       lead.get("phone", ""),
        "email":       lead.get("email", ""),
        "locationId":  GHL_LOCATION_ID,
        "tags":        tags,
        "source":      "Blast Engine v3",
    }
    if lead.get("city"):  body["city"]  = lead["city"]
    if lead.get("state"): body["state"] = lead["state"]

    resp = ghl_request("POST", "/contacts/", json_body=body)
    if resp and "contact" in resp:
        return resp["contact"]["id"]
    if resp and isinstance(resp, dict) and "id" in resp:
        return resp["id"]

    # Fall back to search by email
    search = ghl_request("GET", "/contacts/", params={
        "locationId": GHL_LOCATION_ID,
        "query":      lead["email"],
        "limit":      1,
    })
    if search and search.get("contacts"):
        return search["contacts"][0]["id"]
    return None


def send_email_ghl(contact_id, subject, html_body, text_body, email_from):
    """Send email via GHL conversations API with both plain-text and HTML."""
    payload = {
        "type":           "Email",
        "contactId":      contact_id,
        "subject":        subject,
        "html":           html_body,
        "text":           text_body,   # plain-text alternative
        "emailFrom":      email_from,
    }
    return ghl_request(
        "POST", "/conversations/messages",
        headers=CONVERSATIONS_HEADERS,
        json_body=payload,
    )


def ntfy_alert(topic, title, message, priority="default"):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={"Title": safe_title, "Priority": priority},
            timeout=10,
        )
    except Exception:
        pass


# ─── Lead Parsing ─────────────────────────────────────────────────────────────

def parse_lead_tags(raw_tags):
    """Convert CSV tags field (comma-string or list) to list of strings."""
    if not raw_tags:
        return []
    if isinstance(raw_tags, list):
        return [t.strip() for t in raw_tags if t.strip()]
    return [t.strip() for t in str(raw_tags).split(",") if t.strip()]


def extract_lead_fields(row):
    """Normalize CSV row into a consistent lead dict."""
    return {
        "email":       (row.get("email") or "").strip(),
        "firstName":   (row.get("firstName") or row.get("first_name") or row.get("firstname") or "").strip(),
        "lastName":    (row.get("lastName")  or row.get("last_name")  or "").strip(),
        "companyName": (row.get("companyName") or row.get("company") or row.get("company_name") or "").strip(),
        "phone":       (row.get("phone") or row.get("Phone") or "").strip(),
        "city":        (row.get("city") or row.get("City") or "").strip(),
        "state":       (row.get("state") or row.get("State") or "").strip(),
        "zip":         (row.get("zip") or row.get("postalCode") or "").strip(),
        "industry":    (row.get("industry") or "").strip().lower(),
        "tags":        parse_lead_tags(row.get("tags", "")),
    }


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_blast(state, csv_path):
    """Send cold emails from CSV with address rotation and A/B testing."""
    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        sys.exit(1)

    log(f"=== Blast Engine v3: Loading {csv_path} ===")
    state["stats"]["total_runs"] += 1
    state["stats"]["last_run"] = datetime.now().isoformat()

    leads = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(extract_lead_fields(row))

    log(f"Loaded {len(leads)} leads")

    sent_count    = 0
    failed_count  = 0
    invalid_count = 0
    skipped_count = 0
    alias_exhausted = False

    for i, lead in enumerate(leads):
        email   = lead["email"].lower()
        company = lead["companyName"] or "your business"

        # Skip if no email
        if not email:
            skipped_count += 1
            continue

        # Skip if already sent
        if email in state["sent"]:
            skipped_count += 1
            continue

        # Skip hard bounces permanently
        if email in state.get("bounced_hard", []):
            skipped_count += 1
            continue

        # Skip if bounced soft too recently (72h cooldown)
        if email in state.get("bounced_soft", []):
            sent_rec = state["sent"].get(email, {})
            if sent_rec.get("sent_at"):
                age = (datetime.now() - datetime.fromisoformat(sent_rec["sent_at"])).total_seconds()
                if age < 72 * 3600:
                    skipped_count += 1
                    continue

        # Validate email
        valid, reason = validate_email(email)
        if not valid:
            if email not in state["invalid"]:
                state["invalid"].append(email)
            state["stats"]["total_invalid"] += 1
            invalid_count += 1
            log(f"  INVALID: {email} ({reason})")
            continue

        # Get sending alias — respects daily cap and gap
        alias, alias_idx, alias_key = get_sending_alias(state)
        if alias is None:
            log("All sending addresses at daily cap or gap. Stopping run.", "WARN")
            alias_exhausted = True
            break

        state["last_alias_index"] = alias_idx

        # Resolve industry
        all_tags = lead["tags"][:]
        if lead["industry"]:
            all_tags.insert(0, lead["industry"])
        industry_key, industry_data = get_industry_data(all_tags)

        # Personalization
        first_name = lead["firstName"] or ""
        city       = lead["city"] or ""

        # A/B subject selection
        subject, variant = get_ab_subject(
            state, industry_key, company, industry_data["value"]
        )

        # Route: local vs national
        lead_contact = {"phone": lead["phone"], "city": city, "postalCode": lead["zip"]}
        local = is_local(lead_contact)

        if local:
            # Local email overrides subject
            city_display = city or "the Nashville area"
            subject = f"I'm in {city_display} — can I show you something?"
            html = build_local_email_html(first_name, company, industry_data, city, "PENDING_ID")
            txt  = build_local_email_text(first_name, company, industry_data, city, "PENDING_ID")
            log(f"  LOCAL: {company} ({city})")
        else:
            html = build_email_html(first_name, company, industry_data, city, "PENDING_ID")
            txt  = build_email_text(first_name, company, industry_data, city, "PENDING_ID")

        # Create / find contact in GHL
        contact_id = create_or_find_contact(lead)
        if not contact_id:
            state["failed"][email] = {
                "reason":       "contact_creation_failed",
                "bounce_type":  "unknown",
                "attempts":     1,
                "last_attempt": datetime.now().isoformat(),
            }
            state["stats"]["total_failed"] += 1
            failed_count += 1
            record_alias_send(state, alias_key, success=False)
            log(f"  FAILED (no contact): {company} ({email})")
            save_state(state)
            continue

        # Inject real contact_id into unsubscribe links
        html = html.replace("PENDING_ID", contact_id)
        txt  = txt.replace("PENDING_ID", contact_id)

        # Send
        result = send_email_ghl(contact_id, subject, html, txt, alias)

        if result and not (isinstance(result, dict) and "error" in result):
            state["sent"][email] = {
                "contact_id":  contact_id,
                "sent_at":     datetime.now().isoformat(),
                "variant":     variant,
                "company":     company,
                "alias":       alias_key,
                "industry":    industry_key,
                "local":       local,
            }
            state["stats"]["total_sent"] += 1
            # Track A/B sends
            ind = state["ab_testing"].setdefault(industry_key, {
                "a_sent": 0, "b_sent": 0, "a_replies": 0, "b_replies": 0,
                "winner": None, "locked_at": None,
            })
            ind[f"{variant.lower()}_sent"] = ind.get(f"{variant.lower()}_sent", 0) + 1
            sent_count += 1
            record_alias_send(state, alias_key, success=True)
            log(f"  SENT [{variant}] via {alias_key}: {company} ({email})")

        else:
            error_detail = ""
            if isinstance(result, dict):
                error_detail = result.get("body", str(result.get("error", "unknown")))
            else:
                error_detail = "no_response"

            bounce_type = categorize_bounce(error_detail)

            state["failed"][email] = {
                "reason":       error_detail[:150],
                "bounce_type":  bounce_type,
                "attempts":     1,
                "last_attempt": datetime.now().isoformat(),
                "company":      company,
            }

            # Hard bounces go on permanent exclusion list
            if bounce_type == "hard":
                if email not in state["bounced_hard"]:
                    state["bounced_hard"].append(email)

            state["stats"]["total_failed"] += 1
            failed_count += 1
            record_alias_send(state, alias_key, success=False)
            log(f"  FAILED [{bounce_type}]: {company} ({email}) — {error_detail[:80]}")

        save_state(state)

        # Enforce gap — wait before next send to respect MIN_GAP_BETWEEN_SENDS
        # (only needed if next lead will use the same alias — but we sleep always
        # because we don't know next alias in advance without re-checking)
        time.sleep(MIN_GAP_BETWEEN_SENDS)

    # Summary
    success_rate = sent_count / max(sent_count + failed_count, 1) * 100
    summary = (
        f"v3 blast complete: {sent_count} sent, {failed_count} failed, "
        f"{invalid_count} invalid, {skipped_count} skipped. "
        f"Success: {success_rate:.0f}%"
        + (" [ALIAS EXHAUSTED]" if alias_exhausted else "")
    )
    log(summary)

    ntfy_alert(
        NTFY_SALES,
        "Blast Engine v3 Complete",
        summary,
        priority="default",
    )
    save_state(state)


def cmd_retry(state):
    """Retry soft-failed sends. Never retries hard bounces."""
    failed = state.get("failed", {})
    hard   = set(state.get("bounced_hard", []))

    retryable = {
        k: v for k, v in failed.items()
        if k not in hard
        and v.get("bounce_type") not in ("hard", "domain_reject")
        and v.get("attempts", 0) < MAX_RETRIES
    }

    if not retryable:
        print("No retryable failures.")
        return

    log(f"Retrying {len(retryable)} failed sends...")
    retried = 0

    for email, info in list(retryable.items()):
        alias, alias_idx, alias_key = get_sending_alias(state)
        if alias is None:
            log("All aliases exhausted during retry.", "WARN")
            break

        valid, reason = validate_email(email)
        if not valid:
            del state["failed"][email]
            if email not in state["invalid"]:
                state["invalid"].append(email)
            continue

        search = ghl_request("GET", "/contacts/", params={
            "locationId": GHL_LOCATION_ID, "query": email, "limit": 1,
        })
        if not search or not search.get("contacts"):
            info["attempts"] = info.get("attempts", 0) + 1
            continue

        contact = search["contacts"][0]
        contact_id = contact["id"]
        first_name = contact.get("firstName", "")
        company    = contact.get("companyName", "your business")
        tags       = contact.get("tags", [])
        industry_key, industry_data = get_industry_data(tags)

        subject = SUBJECT_VARIANTS["A"].format(company=company, value=industry_data["value"])
        html    = build_email_html(first_name, company, industry_data, "", contact_id)
        txt     = build_email_text(first_name, company, industry_data, "", contact_id)

        result = send_email_ghl(contact_id, subject, html, txt, alias)
        state["last_alias_index"] = alias_idx

        if result and not (isinstance(result, dict) and "error" in result):
            state["sent"][email] = {
                "contact_id":  contact_id,
                "sent_at":     datetime.now().isoformat(),
                "variant":     "A-retry",
                "company":     company,
                "alias":       alias_key,
                "industry":    industry_key,
            }
            del state["failed"][email]
            state["stats"]["total_sent"] += 1
            record_alias_send(state, alias_key, success=True)
            retried += 1
            log(f"  RETRY OK: {company} ({email})")
        else:
            error_detail = ""
            if isinstance(result, dict):
                error_detail = result.get("body", "unknown")
            bounce_type = categorize_bounce(error_detail)
            info["attempts"] = info.get("attempts", 0) + 1
            info["bounce_type"] = bounce_type
            info["last_attempt"] = datetime.now().isoformat()
            if bounce_type == "hard" and email not in state["bounced_hard"]:
                state["bounced_hard"].append(email)
            record_alias_send(state, alias_key, success=False)

        time.sleep(MIN_GAP_BETWEEN_SENDS)

    log(f"Retry complete. {retried} succeeded.")
    save_state(state)


def cmd_validate(csv_path):
    """Validate emails in a CSV without sending anything."""
    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        sys.exit(1)

    valid_count   = 0
    invalid_count = 0
    results       = []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lead  = extract_lead_fields(row)
            email = lead["email"]
            if not email:
                continue
            ok, reason = validate_email(email)
            if ok:
                valid_count += 1
            else:
                invalid_count += 1
                results.append(f"  INVALID: {email} — {reason}")

    for r in results:
        print(r)

    total = valid_count + invalid_count
    rate  = valid_count / max(total, 1) * 100
    print(f"\nValid: {valid_count} | Invalid: {invalid_count} | Rate: {rate:.0f}%")


def cmd_stats(state):
    """Print delivery stats and A/B test results."""
    stats     = state["stats"]
    sent      = len(state.get("sent", {}))
    failed    = len(state.get("failed", {}))
    hard_b    = len(state.get("bounced_hard", []))
    soft_b    = len(state.get("bounced_soft", []))
    invalid   = len(state.get("invalid", []))
    attempted = sent + failed
    rate      = sent / max(attempted, 1) * 100

    print("\n╔═══════════════════════════════════════════════╗")
    print("║         BLAST ENGINE v3 — DELIVERY STATS      ║")
    print("╠═══════════════════════════════════════════════╣")
    print(f"║  Total Sent:          {stats.get('total_sent', 0):>6}                 ║")
    print(f"║  Total Failed:        {stats.get('total_failed', 0):>6}                 ║")
    print(f"║  Hard Bounces:        {hard_b:>6}                 ║")
    print(f"║  Soft Bounces:        {soft_b:>6}                 ║")
    print(f"║  Invalid Emails:      {invalid:>6}                 ║")
    print(f"║  Success Rate:        {rate:>5.1f}%                 ║")
    print(f"║  Total Runs:          {stats.get('total_runs', 0):>6}                 ║")
    print(f"║  Last Run:            {str(stats.get('last_run', 'never'))[:16]:>16}     ║")
    print("╠═══════════════════════════════════════════════╣")
    print("║  A/B TESTING SUMMARY                          ║")

    ab = state.get("ab_testing", {})
    if not ab:
        print("║  (no data yet)                                ║")
    else:
        for ind_key, data in ab.items():
            winner_str = f" [WINNER: {data['winner']}]" if data.get("winner") else ""
            a_rate = data.get("a_replies", 0) / max(data.get("a_sent", 1), 1) * 100
            b_rate = data.get("b_replies", 0) / max(data.get("b_sent", 1), 1) * 100
            print(f"║  {ind_key:<18} A={data.get('a_sent',0):>4} ({a_rate:.1f}%)  "
                  f"B={data.get('b_sent',0):>4} ({b_rate:.1f}%){winner_str}")

    print("╠═══════════════════════════════════════════════╣")
    print("║  SENDING ADDRESS DAILY STATUS                 ║")

    today  = datetime.now().strftime("%Y-%m-%d")
    addr_s = state.get("address_rotation", {})
    for alias in SENDING_ALIASES:
        alias_key = alias.split("<")[-1].rstrip(">").strip()
        rec = addr_s.get(alias_key, {})
        if rec.get("day") == today:
            sent_today = rec.get("sent_today", 0)
        else:
            sent_today = 0
        bar = "=" * int(sent_today / MAX_PER_ADDRESS_PER_DAY * 20)
        short_key = alias_key.split("@")[0]
        print(f"║  {short_key:<12} {sent_today:>2}/{MAX_PER_ADDRESS_PER_DAY} [{bar:<20}]    ║")

    print("╚═══════════════════════════════════════════════╝\n")


def cmd_health(state):
    """
    Deliverability health check.
    Flags any sending address with implied bounce rate above BOUNCE_RATE_FLAG_PCT.
    Writes results to HEALTH_FILE.
    """
    log("Running deliverability health check...")

    today   = datetime.now().strftime("%Y-%m-%d")
    results = {}

    # Per-address stats derived from state
    addr_state = state.get("address_rotation", {})

    for alias in SENDING_ALIASES:
        alias_key   = alias.split("<")[-1].rstrip(">").strip()
        display_name = alias.split("<")[0].strip()

        # Count total sends from this alias
        total_sent = sum(
            1 for rec in state["sent"].values()
            if rec.get("alias") == alias_key
        )

        # Count failures attributed to this alias
        # (We don't store alias on failures, so we use address rotation failed counter)
        rec        = addr_state.get(alias_key, {})
        total_fail = rec.get("failed", 0)

        # Today's usage
        sent_today = rec.get("sent_today", 0) if rec.get("day") == today else 0

        # Implied bounce rate (failures / total attempted)
        total_attempted = total_sent + total_fail
        bounce_rate     = total_fail / max(total_attempted, 1) * 100

        flagged = bounce_rate > BOUNCE_RATE_FLAG_PCT

        results[alias_key] = {
            "display_name":   display_name,
            "total_sent":     total_sent,
            "total_failed":   total_fail,
            "total_attempted":total_attempted,
            "implied_bounce_rate_pct": round(bounce_rate, 2),
            "flagged":        flagged,
            "sent_today":     sent_today,
            "daily_cap":      MAX_PER_ADDRESS_PER_DAY,
        }

    # Overall stats
    hard_count = len(state.get("bounced_hard", []))
    soft_count = len(state.get("bounced_soft", []))

    # Bounce breakdown by type from failed dict
    bounce_breakdown = {}
    for rec in state.get("failed", {}).values():
        bt = rec.get("bounce_type", "unknown")
        bounce_breakdown[bt] = bounce_breakdown.get(bt, 0) + 1

    health_data = {
        "generated_at":       datetime.now().isoformat(),
        "overall": {
            "total_sent":        state["stats"].get("total_sent", 0),
            "total_failed":      state["stats"].get("total_failed", 0),
            "hard_bounces":      hard_count,
            "soft_bounces":      soft_count,
            "invalid_emails":    len(state.get("invalid", [])),
            "bounce_breakdown":  bounce_breakdown,
        },
        "addresses":          results,
        "flags": {
            "bounce_rate_threshold_pct": BOUNCE_RATE_FLAG_PCT,
            "flagged_addresses": [k for k, v in results.items() if v["flagged"]],
        },
    }

    os.makedirs(os.path.dirname(HEALTH_FILE), exist_ok=True)
    tmp = HEALTH_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(health_data, f, indent=2)
    os.replace(tmp, HEALTH_FILE)

    # Console output
    print("\n╔══════════════════════════════════════════════════╗")
    print("║       DELIVERABILITY HEALTH CHECK v3             ║")
    print("╠══════════════════════════════════════════════════╣")
    for alias_key, data in results.items():
        flag_str = " [FLAGGED]" if data["flagged"] else ""
        print(f"║  {alias_key:<30} "
              f"bounce={data['implied_bounce_rate_pct']:>5.1f}%{flag_str}")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║  Hard bounces (permanent):  {hard_count:>6}               ║")
    print(f"║  Soft bounces (recoverable): {soft_count:>5}               ║")
    if bounce_breakdown:
        print("║  Bounce breakdown:                               ║")
        for bt, cnt in sorted(bounce_breakdown.items(), key=lambda x: -x[1]):
            print(f"║    {bt:<20} {cnt:>5}                     ║")
    flagged = health_data["flags"]["flagged_addresses"]
    if flagged:
        print(f"║  FLAGGED (>{BOUNCE_RATE_FLAG_PCT}% bounce): {', '.join(flagged)}")
        ntfy_alert(
            NTFY_SYSTEM,
            "[WARN] Blast Engine: Deliverability Flag",
            f"Addresses above {BOUNCE_RATE_FLAG_PCT}% bounce rate: {', '.join(flagged)}. "
            f"Check {HEALTH_FILE}",
            priority="high",
        )
    else:
        print("║  All addresses within acceptable bounce rates.   ║")
    print(f"║  Written to: {HEALTH_FILE[-40:]:>40} ║")
    print("╚══════════════════════════════════════════════════╝\n")

    log(f"Health check complete. Written to {HEALTH_FILE}")
    return health_data


def cmd_status(state):
    """Quick status: last run, queue size, today's sends."""
    today      = datetime.now().strftime("%Y-%m-%d")
    addr_state = state.get("address_rotation", {})
    total_today = sum(
        rec.get("sent_today", 0)
        for rec in addr_state.values()
        if rec.get("day") == today
    )
    daily_capacity = MAX_PER_ADDRESS_PER_DAY * len(SENDING_ALIASES)

    print(f"\nBlast Engine v3 — Status")
    print(f"  Last run:       {state['stats'].get('last_run', 'never')}")
    print(f"  Total sent:     {state['stats'].get('total_sent', 0)}")
    print(f"  Sent today:     {total_today}/{daily_capacity} ({len(SENDING_ALIASES)} addresses x {MAX_PER_ADDRESS_PER_DAY}/day)")
    print(f"  Failed (queue): {len(state.get('failed', {}))}")
    print(f"  Hard bounces:   {len(state.get('bounced_hard', []))}")
    print(f"  Invalid emails: {len(state.get('invalid', []))}")
    print(f"  A/B industries: {len(state.get('ab_testing', {}))}")
    winners = [(k, v['winner']) for k, v in state.get('ab_testing', {}).items() if v.get('winner')]
    if winners:
        print(f"  A/B winners:    {', '.join(f'{k}={w}' for k,w in winners)}")
    print()


# ─── Main ─────────────────────────────────────────────────────────────────────

USAGE = """
Usage: blast-engine-v3.py <command> [args]

Commands:
  blast <csv>     Send cold emails from a CSV lead file
  retry           Retry failed sends (skips hard bounces)
  stats           Show delivery metrics + A/B results
  validate <csv>  Validate emails without sending
  status          Quick status summary
  health          Deliverability health check (writes deliverability-health.json)
""".strip()


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    command = sys.argv[1].lower()
    state   = load_state()

    try:
        if command == "blast":
            if len(sys.argv) < 3:
                print("Usage: blast-engine-v3.py blast <path-to-csv>")
                sys.exit(1)
            cmd_blast(state, sys.argv[2])

        elif command == "retry":
            cmd_retry(state)

        elif command == "stats":
            cmd_stats(state)

        elif command == "validate":
            if len(sys.argv) < 3:
                print("Usage: blast-engine-v3.py validate <path-to-csv>")
                sys.exit(1)
            cmd_validate(sys.argv[2])

        elif command in ("status",):
            cmd_status(state)

        elif command == "health":
            cmd_health(state)

        else:
            print(f"Unknown command: {command}\n")
            print(USAGE)
            sys.exit(1)

    except KeyboardInterrupt:
        log("Interrupted by user.", "WARN")
        save_state(state)
        sys.exit(0)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log(f"CRASH: {e}\n{tb}", "ERROR")
        ntfy_alert(
            NTFY_SYSTEM,
            "[CRITICAL] Blast Engine v3 Crashed",
            f"Command: {command}\nError: {str(e)[:400]}",
            priority="urgent",
        )
        save_state(state)
        raise


if __name__ == "__main__":
    main()
