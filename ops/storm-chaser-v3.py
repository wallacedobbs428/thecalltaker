#!/usr/bin/env python3
"""
STORM CHASER v3 — The Call Taker
=================================
Real-time storm detection using the National Weather Service (NWS) Alerts API.
Replaces v2 (temperature extremes via Open-Meteo) and storm-trigger.py
(WMO codes via Open-Meteo).

KEY UPGRADE: NWS detects ACTUAL storms — tornado warnings, severe thunderstorm
warnings, hail, high wind advisories. Not just hot/cold temps. The emails go
out within 5 minutes of NWS publishing the alert. Speed is the entire product.

Commands:
  scan    — Single pass: check NWS for active storm alerts, send emails
  monitor — Continuous loop: check every 5 minutes forever (use for launchd)
  status  — Show stats, recent storm events, city cooldowns
  test    — Dry run: detect storms, log who would be emailed, send nothing

Target industries in GHL: roofing, hvac, general-contractor
Storm types: Tornado Warning/Watch, Severe Thunderstorm Warning,
             High Wind Warning, Wind Advisory, Hail (in description)

NWS API: https://api.weather.gov/alerts/active?point={lat},{lon}
         No API key. User-Agent required.

State file:  ops/storm-chaser-state.json
Log file:    ops/storm-chaser.log
Storm log:   ops/storm-log.json  (separate append-only record of every event)
"""

import sys
import os
import json
import time
import traceback
import requests
from datetime import datetime, timedelta
from collections import defaultdict

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY      = os.environ.get("TCT_GHL_API_KEY",      "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID  = os.environ.get("TCT_GHL_LOCATION_ID",  "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL     = "https://services.leadconnectorhq.com"
BUSINESS_EMAIL   = "thecalltakerai@gmail.com"
BOOKING_URL      = "https://thecalltaker.com/book.html"
DEMO_LINE        = "(615) 784-5747"

# ntfy topics (canonical — see CLAUDE.md March 2 2026)
NTFY_URGENT   = "tct-urgent-Hk9UOEZR"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_SYSTEM   = "tct-system-vRsfXQRQ"

# Absolute paths — launchd resets cwd between runs
_BASE = os.path.expanduser("~/thecalltaker/ops")
STATE_FILE     = os.path.join(_BASE, "storm-chaser-state.json")
LOG_FILE       = os.path.join(_BASE, "storm-chaser.log")
STORM_LOG_FILE = os.path.join(_BASE, "storm-log.json")

# NWS API
NWS_BASE_URL   = "https://api.weather.gov"
NWS_USER_AGENT = "(TheCallTaker, thecalltakerai@gmail.com)"

# NWS event names that trigger email sends
# Matched as case-insensitive substring of alert.properties.event
TRIGGER_EVENTS = {
    "Tornado Warning",
    "Tornado Watch",
    "Severe Thunderstorm Warning",
    "High Wind Warning",
    "Wind Advisory",
    "Extreme Wind Warning",
    "Special Weather Statement",   # included — sometimes announces imminent severe weather
}

# Additional trigger: if description contains these keywords even for
# events not in TRIGGER_EVENTS (catches hail in statement bodies)
TRIGGER_KEYWORDS = ["hail", "tornado", "severe thunderstorm", "damaging wind", "hurricane"]

# Wind speed (mph) threshold — alerts describing winds above this fire
WIND_TRIGGER_MPH = 40

# GHL industry tags we target for storm emails.
# Contacts must have at least one of these tags.
STORM_TARGET_TAGS = {"roofing", "hvac", "general-contractor"}

# Contacts with ANY of these tags are excluded
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed",
}

# Cooldowns
CONTACT_COOLDOWN_DAYS  = 14   # Don't re-email same contact within this window
CITY_COOLDOWN_HOURS    = 6    # Don't re-trigger same city within this window
MAX_EMAILS_PER_RUN     = 15   # Safety cap per scan pass
SEND_DELAY_SECONDS     = 4    # Pause between GHL sends
MONITOR_INTERVAL_SECS  = 300  # 5 minutes between monitor loop iterations

# GHL API headers
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version":       "2021-07-28",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
    "User-Agent":    "TheCallTaker-StormChaser/3.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version":       "2021-04-15",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
    "User-Agent":    "TheCallTaker-StormChaser/3.0",
}


# ─── 28-metro coordinate map ──────────────────────────────────────────────────
# Coordinates used to query NWS point alerts.
# Same set as existing scripts so launchd plist replacement is seamless.

METRO_COORDS = {
    # Southeast
    "nashville":     (36.16,  -86.78),
    "memphis":       (35.15,  -90.05),
    "knoxville":     (35.96,  -83.92),
    "chattanooga":   (35.05,  -85.31),
    "atlanta":       (33.75,  -84.39),
    "birmingham":    (33.52,  -86.80),
    "louisville":    (38.25,  -85.76),
    "huntsville":    (34.73,  -86.59),
    "lexington":     (38.04,  -84.50),
    "jackson":       (32.30,  -90.18),
    # South / Southwest
    "dallas":        (32.78,  -96.80),
    "houston":       (29.76,  -95.37),
    "phoenix":       (33.45, -112.07),
    "san antonio":   (29.42,  -98.49),
    "new orleans":   (29.95,  -90.07),
    "oklahoma city": (35.47,  -97.52),
    # Southeast coast
    "tampa":         (27.95,  -82.46),
    "jacksonville":  (30.33,  -81.66),
    "miami":         (25.77,  -80.19),
    "charlotte":     (35.23,  -80.84),
    # Midwest
    "indianapolis":  (39.77,  -86.16),
    "columbus":      (39.96,  -82.99),
    "kansas city":   (39.10,  -94.58),
    "st louis":      (38.63,  -90.20),
    "chicago":       (41.85,  -87.65),
    "detroit":       (42.33,  -83.05),
    "minneapolis":   (44.98,  -93.27),
    # Mountain
    "denver":        (39.74, -104.98),
}

# US state code lookup keyed by metro — used for the state-wide NWS alert
# endpoint as a faster fallback when we need broad coverage.
# (Two-letter FIPS codes per NWS docs.)
METRO_STATE = {
    "nashville": "TN", "memphis": "TN", "knoxville": "TN", "chattanooga": "TN",
    "atlanta": "GA", "birmingham": "AL", "louisville": "KY", "huntsville": "AL",
    "lexington": "KY", "jackson": "MS", "dallas": "TX", "houston": "TX",
    "phoenix": "AZ", "san antonio": "TX", "new orleans": "LA",
    "oklahoma city": "OK", "tampa": "FL", "jacksonville": "FL", "miami": "FL",
    "charlotte": "NC", "indianapolis": "IN", "columbus": "OH",
    "kansas city": "MO", "st louis": "MO", "chicago": "IL", "detroit": "MI",
    "minneapolis": "MN", "denver": "CO",
}


# ─── Logging ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] storm-chaser-v3: {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ─── State management ─────────────────────────────────────────────────────────

def _default_state():
    return {
        "contact_sent":    {},   # contact_id -> ISO timestamp of last storm email
        "city_triggered":  {},   # metro_key  -> ISO timestamp of last trigger
        "seen_alert_ids":  [],   # NWS alert IDs already processed (last 500)
        "stats": {
            "total_emails_sent":   0,
            "total_storm_events":  0,
            "total_scan_runs":     0,
            "last_scan":           None,
        },
    }


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                s = json.load(f)
            # Ensure all required keys exist (handles upgrades from v2)
            defaults = _default_state()
            for k, v in defaults.items():
                s.setdefault(k, v)
            s["stats"].setdefault("total_scan_runs", 0)
            return s
        except (json.JSONDecodeError, IOError):
            log("State file corrupted — starting fresh", "WARN")
    return _default_state()


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


# ─── Storm log (append-only record of every detected event) ──────────────────

def append_storm_log(entry):
    """
    Append one storm event to storm-log.json.
    File is a JSON array. Creates it if missing.
    Atomic write: load → append → write to tmp → replace.
    """
    try:
        os.makedirs(os.path.dirname(STORM_LOG_FILE), exist_ok=True)
        existing = []
        if os.path.exists(STORM_LOG_FILE):
            try:
                with open(STORM_LOG_FILE, "r") as f:
                    existing = json.load(f)
                if not isinstance(existing, list):
                    existing = []
            except (json.JSONDecodeError, IOError):
                existing = []
        existing.append(entry)
        tmp = STORM_LOG_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(existing, f, indent=2)
        os.replace(tmp, STORM_LOG_FILE)
    except Exception as e:
        log(f"Failed to write storm log: {e}", "WARN")


# ─── NWS Alerts API ──────────────────────────────────────────────────────────

def nws_request(url, params=None):
    """
    Single NWS API request with retry.
    Returns parsed JSON dict or None.
    User-Agent is mandatory per NWS policy.
    """
    headers = {
        "User-Agent": NWS_USER_AGENT,
        "Accept":     "application/geo+json",
    }
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=20)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 503:
                # NWS occasionally 503s — wait and retry
                wait = [10, 30, 60][min(attempt, 2)]
                log(f"NWS 503, retrying in {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code == 404:
                # Point outside NWS coverage (e.g., Phoenix edge cases)
                return {"features": []}
            log(f"NWS returned {resp.status_code} for {url}", "WARN")
            return None
        except requests.exceptions.RequestException as e:
            log(f"NWS request failed (attempt {attempt+1}): {e}", "WARN")
            if attempt < 2:
                time.sleep(5)
    return None


def get_active_alerts_for_point(lat, lon):
    """
    Fetch active NWS alerts for a specific lat/lon point.
    Returns list of alert feature dicts.
    """
    url = f"{NWS_BASE_URL}/alerts/active"
    data = nws_request(url, params={"point": f"{lat},{lon}", "status": "actual"})
    if data and "features" in data:
        return data["features"]
    return []


def get_active_alerts_for_state(state_code):
    """
    Fetch all active alerts for a US state code.
    Used as a broader sweep to catch alerts that the point query might miss
    due to NWS zone polygon edge cases.
    Returns list of alert feature dicts.
    """
    url = f"{NWS_BASE_URL}/alerts/active"
    data = nws_request(url, params={"area": state_code, "status": "actual"})
    if data and "features" in data:
        return data["features"]
    return []


def classify_alert(alert_feature):
    """
    Given a single NWS alert feature, determine:
    - Whether it qualifies as a storm trigger
    - The storm type (hail/tornado/wind/severe_storm)
    - A human-readable description for the email

    Returns (is_trigger: bool, storm_type: str, description: str)
    or (False, None, None) if it doesn't qualify.
    """
    props = alert_feature.get("properties", {})
    event       = props.get("event", "")
    headline    = props.get("headline", "")
    description = props.get("description", "")
    severity    = props.get("severity", "")     # Extreme, Severe, Moderate, Minor
    certainty   = props.get("certainty", "")    # Observed, Likely, Possible, Unlikely

    full_text = f"{event} {headline} {description}".lower()

    # Skip minor/unknown severity unless it's explicitly a tornado or severe storm
    if severity.lower() in ("minor", "unknown") and "tornado" not in full_text:
        return False, None, None

    # Skip "Possible" or "Unlikely" certainty for non-tornado events
    if certainty.lower() in ("possible", "unlikely") and "tornado" not in full_text:
        return False, None, None

    # Tornado events — always fire regardless of certainty
    if "tornado warning" in event.lower():
        return True, "tornado", f"Tornado Warning — {headline or event}"
    if "tornado watch" in event.lower():
        return True, "tornado", f"Tornado Watch — {headline or event}"

    # Severe Thunderstorm Warning
    if "severe thunderstorm warning" in event.lower():
        # Check if hail is mentioned — makes it a hail event
        if "hail" in full_text:
            return True, "hail", f"Severe Thunderstorm with Hail — {headline or event}"
        return True, "severe_storm", f"Severe Thunderstorm Warning — {headline or event}"

    # High wind events
    if event.lower() in ("high wind warning", "extreme wind warning"):
        return True, "wind", f"High Wind Warning — {headline or event}"

    # Wind Advisory — only fire if 40+ mph mentioned in text
    if "wind advisory" in event.lower():
        # Look for mph figures in description
        import re
        mph_matches = re.findall(r"(\d+)\s*mph", full_text)
        max_mph = max((int(m) for m in mph_matches), default=0)
        if max_mph >= WIND_TRIGGER_MPH:
            return True, "wind", f"Wind Advisory ({max_mph}mph) — {headline or event}"
        return False, None, None

    # Keyword sweep for events NOT in TRIGGER_EVENTS but mentioning storm triggers
    for kw in TRIGGER_KEYWORDS:
        if kw in full_text:
            # Hail keyword in body of any warning/watch
            if kw == "hail":
                return True, "hail", f"Hail Alert — {headline or event}"
            if kw == "tornado":
                return True, "tornado", f"Tornado Mentioned — {headline or event}"
            if kw in ("severe thunderstorm", "damaging wind"):
                return True, "severe_storm", f"Severe Weather — {headline or event}"

    # Named-trigger-event match (covers Special Weather Statements, etc.)
    for trigger_event in TRIGGER_EVENTS:
        if trigger_event.lower() in event.lower():
            return True, "severe_storm", f"{event} — {headline or event}"

    return False, None, None


def check_metro_for_storms(metro_key, lat, lon):
    """
    Query NWS for active storm alerts affecting a metro.
    Returns list of (storm_type, description) tuples.
    De-duplicates by alert ID.
    """
    alerts = get_active_alerts_for_point(lat, lon)

    # Also check state-wide alerts — NWS point queries sometimes miss county
    # alerts at polygon edges. Combine and deduplicate.
    state_code = METRO_STATE.get(metro_key)
    if state_code:
        state_alerts = get_active_alerts_for_state(state_code)
        seen_ids = {a.get("id") for a in alerts}
        for sa in state_alerts:
            if sa.get("id") not in seen_ids:
                # Only include state alerts that reference the metro area in areaDesc
                area_desc = (sa.get("properties", {}).get("areaDesc") or "").lower()
                metro_words = metro_key.split()
                if any(w in area_desc for w in metro_words):
                    alerts.append(sa)
                    seen_ids.add(sa.get("id"))

    triggered = []
    for alert in alerts:
        is_trigger, storm_type, description = classify_alert(alert)
        if is_trigger:
            triggered.append({
                "alert_id":    alert.get("id", ""),
                "storm_type":  storm_type,
                "description": description,
            })

    return triggered


# ─── GHL helpers ──────────────────────────────────────────────────────────────

def ghl_request(method, path, headers=None, params=None, json_body=None, retries=3):
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    for attempt in range(retries):
        try:
            resp = requests.request(
                method, url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=30,
            )
            if resp.status_code == 429:
                wait = [30, 60, 120][min(attempt, 2)]
                log(f"GHL rate limited — waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                wait = [5, 15, 30][min(attempt, 2)]
                time.sleep(wait)
                continue
            if resp.status_code >= 400:
                log(f"GHL {resp.status_code}: {resp.text[:200]}", "ERROR")
                return None
            return resp.json() if resp.text else {}
        except requests.exceptions.RequestException as e:
            log(f"GHL request exception: {e}", "ERROR")
            if attempt < retries - 1:
                time.sleep(5)
    return None


def get_storm_target_contacts():
    """
    Fetch all GHL contacts tagged roofing, hvac, or general-contractor.
    Excludes contacts with exclusion tags. Must have an email address.
    Returns deduplicated list of contact dicts.
    """
    seen_ids = set()
    targets = []

    for tag in STORM_TARGET_TAGS:
        page = 1
        while True:
            data = ghl_request("GET", "/contacts/", params={
                "locationId": GHL_LOCATION_ID,
                "limit":      100,
                "page":       page,
                "tags":       tag,
            })
            if not data or "contacts" not in data:
                break
            batch = data["contacts"]
            for c in batch:
                cid = c.get("id")
                if not cid or cid in seen_ids:
                    continue
                seen_ids.add(cid)
                contact_tags = {t.lower() for t in c.get("tags", [])}
                if contact_tags & EXCLUDE_TAGS:
                    continue
                if not c.get("email"):
                    continue
                targets.append(c)
            if len(batch) < 100:
                break
            page += 1
            if page > 50:
                break

    return targets


def match_contact_to_metro(contact, metro_key):
    """
    Return True if the contact's city fields match the metro key.
    Handles multi-word metros ("kansas city", "st louis").
    """
    city_fields = [
        contact.get("city", ""),
        contact.get("address1City", ""),
        contact.get("locationCity", ""),
    ]
    metro_normalized = metro_key.lower()
    for raw in city_fields:
        if not raw:
            continue
        norm = raw.lower().strip().replace(",", "").replace(".", "")
        if norm == metro_normalized:
            return True
        if metro_normalized in norm:
            return True
        if norm in metro_normalized:
            return True
    return False


def get_contact_industry(contact):
    """
    Determine primary industry from GHL tags.
    Returns 'roofing', 'hvac', 'general-contractor', or 'general'.
    """
    tags = {t.lower() for t in contact.get("tags", [])}
    if "roofing" in tags:
        return "roofing"
    if "hvac" in tags:
        return "hvac"
    if "general-contractor" in tags:
        return "general-contractor"
    return "general"


def add_tag(contact_id, tag):
    """Add a tag to a GHL contact without overwriting existing tags."""
    data = ghl_request("GET", f"/contacts/{contact_id}")
    if not data or "contact" not in data:
        return False
    current = data["contact"].get("tags", [])
    if tag in current:
        return True
    result = ghl_request("PUT", f"/contacts/{contact_id}", json_body={
        "locationId": GHL_LOCATION_ID,
        "tags": current + [tag],
    })
    return result is not None


def tag_contact_hot(contact_id):
    """
    When a storm email lead replies, flag them HOT in GHL.
    Adds both 'hot-lead' and 'storm-reply' tags.
    Triggered by: external reply monitor or manual call to this function.
    """
    add_tag(contact_id, "hot-lead")
    add_tag(contact_id, "storm-reply")
    log(f"Tagged {contact_id} as hot-lead + storm-reply")


def send_ghl_email(contact_id, subject, html_body):
    """Send email to a contact via GHL Conversations API."""
    result = ghl_request(
        "POST", "/conversations/messages",
        headers=CONVERSATIONS_HEADERS,
        json_body={
            "type":        "Email",
            "contactId":   contact_id,
            "subject":     subject,
            "html":        html_body,
            "emailFrom":   f"Wallace at The Call Taker <{BUSINESS_EMAIL}>",
        },
    )
    return result is not None


# ─── ntfy ─────────────────────────────────────────────────────────────────────

def ntfy(topic, title, body, priority="default", tags=None):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        headers = {
            "Title":    safe_title,
            "Priority": priority,
        }
        if tags:
            headers["Tags"] = ",".join(tags)
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers=headers,
            timeout=10,
        )
    except Exception as e:
        log(f"ntfy send failed: {e}", "WARN")


# ─── Email templates ──────────────────────────────────────────────────────────
# 4 sentences max per requirement. Subject references specific storm + city.
# Different body for hail, wind, tornado, severe_storm.
# Industry-aware (roofing vs HVAC vs general contractor).

def _email_hail(first_name, company_name, city):
    """Hail alert — roofing focus."""
    city_t = city.title()
    subject = f"Hail hitting {city_t} right now — are your phones ready?"
    html = f"""<div style="font-family:-apple-system,Inter,sans-serif;color:#111;max-width:580px;line-height:1.65">

<p>Hey {first_name},</p>

<p>Hail is hitting {city_t} right now. Every homeowner with a damaged roof is calling roofers as we speak, and the first company to answer is the one that gets the job — usually worth $8,000–$18,000.</p>

<p>The Call Taker is an AI receptionist built for contractors like {company_name}: it answers every call with your company name, captures the address and damage description, and texts you the details within seconds — 24/7, no voicemail.</p>

<p>We're running a free 14-day pilot right now — no card, we set it up in 48 hours. <a href="{BOOKING_URL}" style="color:#f97316;font-weight:600">Book your free pilot here</a>, or call {DEMO_LINE} and hear exactly what your customers would hear.</p>

<p>— Wallace<br><span style="color:#888;font-size:13px">Founder, The Call Taker</span></p>
</div>"""
    return subject, html


def _email_wind(first_name, company_name, city):
    """High wind alert — HVAC + roofing + contractors."""
    city_t = city.title()
    subject = f"40mph+ winds in {city_t} — storm damage calls are coming"
    html = f"""<div style="font-family:-apple-system,Inter,sans-serif;color:#111;max-width:580px;line-height:1.65">

<p>Hey {first_name},</p>

<p>High winds are hitting {city_t} right now — that means downed trees, structural damage, and HVAC equipment failures, and every homeowner affected is going to call a contractor in the next few hours.</p>

<p>The Call Taker answers every call to {company_name} instantly with a live-sounding AI: captures the caller's name, address, and what broke, then texts you the lead so you can dispatch immediately — no missed calls, no voicemail.</p>

<p>We have a free 14-day pilot with no credit card required. <a href="{BOOKING_URL}" style="color:#f97316;font-weight:600">Claim your spot here</a> before tonight's surge hits, or call {DEMO_LINE} and hear the AI live right now.</p>

<p>— Wallace<br><span style="color:#888;font-size:13px">Founder, The Call Taker</span></p>
</div>"""
    return subject, html


def _email_tornado(first_name, company_name, city):
    """Tornado watch/warning — all trades."""
    city_t = city.title()
    subject = f"Tornado watch in {city_t} — contractors who answer first win"
    html = f"""<div style="font-family:-apple-system,Inter,sans-serif;color:#111;max-width:580px;line-height:1.65">

<p>Hey {first_name},</p>

<p>There's an active tornado watch in the {city_t} area — when the storm passes, homeowners with damage call every contractor they can find, and the first one to pick up gets the job.</p>

<p>The Call Taker makes sure {company_name} never misses that first call: our AI answers instantly, sounds like a real person, captures the damage details, and texts you the lead — even at 2am after the storm clears.</p>

<p>We're offering a free 14-day pilot, no card needed, setup in 48 hours. <a href="{BOOKING_URL}" style="color:#f97316;font-weight:600">Start your free pilot here</a> — or call {DEMO_LINE} to hear it for yourself right now.</p>

<p>— Wallace<br><span style="color:#888;font-size:13px">Founder, The Call Taker</span></p>
</div>"""
    return subject, html


def _email_severe_storm(first_name, company_name, city):
    """Generic severe weather — all trades."""
    city_t = city.title()
    subject = f"Severe storm hitting {city_t} — {company_name} ready for the calls?"
    html = f"""<div style="font-family:-apple-system,Inter,sans-serif;color:#111;max-width:580px;line-height:1.65">

<p>Hey {first_name},</p>

<p>A severe weather alert just went out for {city_t}: when the storm rolls through, your phone is going to ring with homeowners who need help fast, and whichever contractor answers first wins those jobs.</p>

<p>The Call Taker handles every inbound call for {company_name} — AI answers instantly, collects the caller's details and problem description, books the appointment or dispatches you immediately, all 24/7.</p>

<p>We're running a free 14-day pilot with no card required. <a href="{BOOKING_URL}" style="color:#f97316;font-weight:600">Claim your free pilot here</a> or call the demo line at {DEMO_LINE} to hear exactly what your customers would experience.</p>

<p>— Wallace<br><span style="color:#888;font-size:13px">Founder, The Call Taker</span></p>
</div>"""
    return subject, html


def build_storm_email(first_name, company_name, city, storm_type, industry):
    """
    Route to the correct template based on storm_type.
    Industry is logged but templates are naturally appropriate
    (hail = roofing focus, wind = HVAC/roofing, etc.)

    Returns (subject, html) tuple.
    """
    if storm_type == "hail":
        return _email_hail(first_name, company_name, city)
    elif storm_type == "wind":
        return _email_wind(first_name, company_name, city)
    elif storm_type == "tornado":
        return _email_tornado(first_name, company_name, city)
    else:
        # severe_storm or any unrecognized type
        return _email_severe_storm(first_name, company_name, city)


# ─── Core scan logic ──────────────────────────────────────────────────────────

def cmd_scan(state, dry_run=False):
    """
    Single scan pass:
    1. Query NWS for each of the 28 metros
    2. Classify alerts — tornado, hail, wind, severe storm
    3. Skip metros in city cooldown
    4. For storm metros: find matching GHL leads by industry + city
    5. Send emails immediately (within the same run)
    6. Log to storm-log.json and ntfy
    """
    run_label = "DRY RUN" if dry_run else "LIVE"
    log(f"=== Storm Chaser v3: {run_label} — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    state["stats"]["total_scan_runs"] = state["stats"].get("total_scan_runs", 0) + 1
    state["stats"]["last_scan"] = datetime.now().isoformat()

    # ── Step 1: Identify storm metros ─────────────────────────────────────────
    storm_metros = []
    seen_alert_ids = set(state.get("seen_alert_ids", []))

    for metro_key, (lat, lon) in METRO_COORDS.items():
        # City cooldown check
        last_triggered = state["city_triggered"].get(metro_key)
        if last_triggered:
            hours_since = (datetime.now() - datetime.fromisoformat(last_triggered)).total_seconds() / 3600
            if hours_since < CITY_COOLDOWN_HOURS:
                log(f"  {metro_key}: cooldown ({hours_since:.1f}h / {CITY_COOLDOWN_HOURS}h)")
                continue

        triggered_alerts = check_metro_for_storms(metro_key, lat, lon)

        # Filter alerts we've already processed
        new_alerts = [a for a in triggered_alerts if a["alert_id"] not in seen_alert_ids]

        if new_alerts:
            # Pick the most severe type (tornado > hail > wind > severe_storm)
            priority = {"tornado": 0, "hail": 1, "wind": 2, "severe_storm": 3}
            new_alerts.sort(key=lambda a: priority.get(a["storm_type"], 9))
            best = new_alerts[0]
            log(f"  STORM: {metro_key} — {best['storm_type']} — {best['description'][:80]}")
            storm_metros.append({
                "metro":       metro_key,
                "storm_type":  best["storm_type"],
                "description": best["description"],
                "alert_ids":   [a["alert_id"] for a in new_alerts],
            })
        else:
            log(f"  {metro_key}: clear")

        time.sleep(0.5)  # Gentle on the free NWS API

    if not storm_metros:
        log("No new storm alerts across all 28 metros. Nothing to send.")
        save_state(state)
        return 0

    log(f"{len(storm_metros)} metro(s) with active storms: {[m['metro'] for m in storm_metros]}")

    # ── Step 2: Fetch target contacts once (single GHL sweep is cheapest) ─────
    log("Fetching roofing + hvac + general-contractor contacts from GHL...")
    all_targets = get_storm_target_contacts()
    log(f"Found {len(all_targets)} eligible contacts in GHL")

    total_sent = 0
    storm_log_entries = []

    # ── Step 3: For each storm metro, find matching contacts and email them ───
    for metro_info in storm_metros:
        if total_sent >= MAX_EMAILS_PER_RUN:
            log(f"Reached MAX_EMAILS_PER_RUN ({MAX_EMAILS_PER_RUN}) — stopping")
            break

        metro_key   = metro_info["metro"]
        storm_type  = metro_info["storm_type"]
        description = metro_info["description"]
        alert_ids   = metro_info["alert_ids"]

        metro_contacts = [c for c in all_targets if match_contact_to_metro(c, metro_key)]
        log(f"  {metro_key}: {len(metro_contacts)} matching contacts")

        if not metro_contacts and not dry_run:
            # Log the storm even if no contacts matched — valuable intel
            append_storm_log({
                "timestamp":        datetime.now().isoformat(),
                "metro":            metro_key,
                "storm_type":       storm_type,
                "description":      description,
                "contacts_found":   0,
                "emails_sent":      0,
                "dry_run":          dry_run,
            })
            continue

        sent_this_metro = 0
        skipped_cooldown = 0
        failed = 0

        for contact in metro_contacts:
            if total_sent >= MAX_EMAILS_PER_RUN:
                break

            cid         = contact.get("id")
            first_name  = contact.get("firstName") or "there"
            company     = contact.get("companyName") or "your company"
            industry    = get_contact_industry(contact)

            # Per-contact cooldown
            last_sent = state["contact_sent"].get(cid)
            if last_sent:
                days_since = (datetime.now() - datetime.fromisoformat(last_sent)).days
                if days_since < CONTACT_COOLDOWN_DAYS:
                    skipped_cooldown += 1
                    continue

            subject, html = build_storm_email(first_name, company, metro_key, storm_type, industry)

            if dry_run:
                log(f"    [DRY RUN] {first_name} @ {company} ({industry}) — {subject[:60]}")
                sent_this_metro += 1
                total_sent += 1
                continue

            ok = send_ghl_email(cid, subject, html)
            if ok:
                state["contact_sent"][cid] = datetime.now().isoformat()
                # Tag with storm-outreach-YYYY-MM-DD for reply tracking
                date_tag = f"storm-outreach-{datetime.now().strftime('%Y-%m-%d')}"
                add_tag(cid, date_tag)
                sent_this_metro += 1
                total_sent += 1
                state["stats"]["total_emails_sent"] = state["stats"].get("total_emails_sent", 0) + 1
                log(f"    SENT: {first_name} @ {company} ({industry}, {metro_key})")
            else:
                failed += 1
                log(f"    FAILED: {first_name} @ {company}", "ERROR")

            time.sleep(SEND_DELAY_SECONDS)

        log(
            f"  {metro_key}: sent={sent_this_metro} "
            f"skipped={skipped_cooldown} failed={failed}"
        )

        # Mark alert IDs as seen
        for aid in alert_ids:
            if aid:
                seen_alert_ids.add(aid)

        # Update city cooldown and stats
        if sent_this_metro > 0 or dry_run:
            state["city_triggered"][metro_key] = datetime.now().isoformat()
            state["stats"]["total_storm_events"] = state["stats"].get("total_storm_events", 0) + 1

        # Append to storm log
        log_entry = {
            "timestamp":       datetime.now().isoformat(),
            "metro":           metro_key,
            "storm_type":      storm_type,
            "description":     description,
            "alert_ids":       alert_ids,
            "contacts_found":  len(metro_contacts),
            "emails_sent":     sent_this_metro,
            "dry_run":         dry_run,
        }
        storm_log_entries.append(log_entry)
        if not dry_run:
            append_storm_log(log_entry)

    # ── Step 4: Save alert IDs we processed (cap at 500 to avoid state bloat) ─
    all_seen = list(seen_alert_ids)[-500:]
    state["seen_alert_ids"] = all_seen

    # ── Step 5: ntfy summary ───────────────────────────────────────────────────
    if storm_log_entries:
        lines = []
        for ev in storm_log_entries:
            emoji = {"tornado": "TORNADO", "hail": "HAIL", "wind": "WIND", "severe_storm": "STORM"}.get(ev["storm_type"], "STORM")
            lines.append(
                f"[{emoji}] {ev['metro'].title()}: {ev['emails_sent']} emails sent"
            )
        body = "\n".join(lines) + f"\n\nTotal: {total_sent} emails this run"

        if total_sent > 0 and not dry_run:
            ntfy(
                NTFY_ACTIVITY,
                f"Storm Chaser v3: {len(storm_log_entries)} storm(s), {total_sent} emails",
                body,
                priority="default",
                tags=["cloud", "zap"],
            )
            # Also ping URGENT if a tornado warning was among the triggers
            tornado_metros = [e for e in storm_log_entries if e["storm_type"] == "tornado"]
            if tornado_metros:
                ntfy(
                    NTFY_URGENT,
                    f"[TORNADO] Active warnings — {len(tornado_metros)} metro(s)",
                    "\n".join(f"{e['metro'].title()}: {e['description'][:100]}" for e in tornado_metros),
                    priority="urgent",
                    tags=["rotating_light", "cloud_tornado"],
                )
        elif dry_run:
            log(f"[DRY RUN] Would ntfy: {total_sent} emails across {len(storm_log_entries)} metros")

    log(
        f"=== Scan complete. "
        f"Metros checked: {len(METRO_COORDS)}. "
        f"Storms: {len(storm_metros)}. "
        f"Emails sent: {total_sent}. ==="
    )

    save_state(state)
    return total_sent


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_monitor():
    """
    Continuous 5-minute loop. Checks NWS every MONITOR_INTERVAL_SECS seconds.
    When a storm is detected, fires email sends immediately — no human approval.
    This is the key command for real-time storm response.

    launchd should run this with RunAtLoad=True and KeepAlive=True,
    OR schedule 'scan' on a 5-minute interval if monitoring is too resource heavy.
    Ctrl-C to stop locally.
    """
    log("Storm Chaser v3 MONITOR started — checking NWS every 5 minutes")
    ntfy(
        NTFY_SYSTEM,
        "Storm Chaser v3 Monitor Started",
        "Continuous NWS monitoring active. Emails fire within 5 min of storm detection.",
        priority="low",
    )

    consecutive_errors = 0

    while True:
        try:
            state = load_state()
            sent = cmd_scan(state, dry_run=False)
            consecutive_errors = 0  # Reset on success

            if sent > 0:
                log(f"Monitor: sent {sent} storm emails this cycle")

        except KeyboardInterrupt:
            log("Monitor stopped by user (KeyboardInterrupt)")
            break
        except Exception as e:
            tb = traceback.format_exc()
            consecutive_errors += 1
            log(f"Monitor error (#{consecutive_errors}): {e}\n{tb}", "ERROR")

            if consecutive_errors >= 3:
                ntfy(
                    NTFY_SYSTEM,
                    "[CRITICAL] Storm Chaser v3 Monitor Errors",
                    f"3+ consecutive errors. Last: {str(e)[:300]}",
                    priority="urgent",
                )
                # Back off longer after repeated failures
                time.sleep(MONITOR_INTERVAL_SECS * 3)
            else:
                time.sleep(30)  # Short back-off before retry
            continue

        log(f"Monitor sleeping {MONITOR_INTERVAL_SECS}s...")
        time.sleep(MONITOR_INTERVAL_SECS)


def cmd_status(state):
    stats        = state.get("stats", {})
    contact_sent = state.get("contact_sent", {})
    city_trigger = state.get("city_triggered", {})
    seen_ids     = state.get("seen_alert_ids", [])

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║         STORM CHASER v3 — STATUS                 ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║  Total Emails Sent:    {stats.get('total_emails_sent', 0):>6}                  ║")
    print(f"║  Storm Events Fired:   {stats.get('total_storm_events', 0):>6}                  ║")
    print(f"║  Total Scan Runs:      {stats.get('total_scan_runs', 0):>6}                  ║")
    print(f"║  Contacts Emailed:     {len(contact_sent):>6}                  ║")
    print(f"║  Alert IDs Tracked:    {len(seen_ids):>6}                  ║")
    print(f"║  Last Scan:            {(stats.get('last_scan') or 'never')[:19]:>19}  ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    if city_trigger:
        now = datetime.now()
        print("Metro cooldown status:")
        for city, ts in sorted(city_trigger.items(), key=lambda x: x[1], reverse=True)[:15]:
            hours_ago = (now - datetime.fromisoformat(ts)).total_seconds() / 3600
            remaining = max(0.0, CITY_COOLDOWN_HOURS - hours_ago)
            bar = "ACTIVE" if remaining > 0 else "ready"
            print(f"  {city:22}  {hours_ago:5.1f}h ago  cooldown={remaining:.1f}h  [{bar}]")
        print()

    # Show last 10 storm events from storm-log.json
    if os.path.exists(STORM_LOG_FILE):
        try:
            with open(STORM_LOG_FILE, "r") as f:
                events = json.load(f)
            if isinstance(events, list) and events:
                print(f"Last 10 storm events (from storm-log.json, {len(events)} total):")
                for ev in events[-10:][::-1]:
                    ts      = ev.get("timestamp", "")[:16]
                    metro   = ev.get("metro", "?").title()
                    stype   = ev.get("storm_type", "?")
                    sent    = ev.get("emails_sent", 0)
                    dry     = " [DRY RUN]" if ev.get("dry_run") else ""
                    print(f"  {ts}  {metro:22}  {stype:15}  {sent:>2} emails{dry}")
                print()
        except Exception:
            pass


# ─── Main ─────────────────────────────────────────────────────────────────────

USAGE = """Usage: storm-chaser-v3.py <command>

Commands:
  scan     Single pass — detect NWS storms, send emails immediately
  monitor  Continuous 5-min loop — fires emails the moment a storm is detected
  status   Show stats, cooldowns, recent storm events
  test     Dry run — detect storms, log targets, send nothing

NWS Storm Types Detected:
  tornado      Tornado Warning / Watch
  hail         Severe Thunderstorm Warning with hail
  wind         High Wind Warning / Wind Advisory 40mph+
  severe_storm Severe Thunderstorm Warning (no hail), Special Weather Statement

Target Industries: roofing, hvac, general-contractor
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "monitor":
        # Monitor loads state on each iteration — no pre-load needed
        try:
            cmd_monitor()
        except Exception as e:
            tb = traceback.format_exc()
            log(f"MONITOR CRASH: {e}\n{tb}", "ERROR")
            ntfy(
                NTFY_SYSTEM,
                "[CRITICAL] Storm Chaser v3 Monitor Crashed",
                f"{str(e)[:400]}\n\n{tb[:500]}",
                priority="urgent",
            )
            sys.exit(1)
        return

    state = load_state()

    try:
        if command == "scan":
            cmd_scan(state, dry_run=False)
        elif command == "test":
            cmd_scan(state, dry_run=True)
        elif command == "status":
            cmd_status(state)
        else:
            print(f"Unknown command: {command}\n")
            print(USAGE)
            sys.exit(1)

    except KeyboardInterrupt:
        log("Interrupted")
        sys.exit(0)
    except Exception as e:
        tb = traceback.format_exc()
        log(f"CRASH: {e}\n{tb}", "ERROR")
        ntfy(
            NTFY_SYSTEM,
            "[CRITICAL] Storm Chaser v3 Crashed",
            f"Command: {command}\nError: {str(e)[:300]}\n\n{tb[:500]}",
            priority="urgent",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
