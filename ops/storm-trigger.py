#!/usr/bin/env python3
"""
STORM TRIGGER — The Call Taker
================================
Watches Open-Meteo for severe weather (thunderstorm / hail / flood) across
28 pre-cached metros. When a storm hits, queries GHL for water-damage and
roofing contacts in that metro and blasts a targeted storm email within the
hour.

Why it exists: roofing + water-damage leads are worthless before a storm and
extremely hot after one. This fires the right email at the exact right moment.

Commands:
  scan    — Check all metros for severe weather, send storm emails
  status  — Show stats + recent events
  test    — Dry run (check weather, log who WOULD get blasted, send nothing)

Schedule: Every 2 hours via launchd (recommended: 8am, 10am, 12pm, 2pm, 4pm,
6pm, 8pm on active days. Run cron more frequently during storm season.)

Weather codes that trigger a blast:
  95  — Thunderstorm (slight or moderate)
  96  — Thunderstorm with slight hail
  99  — Thunderstorm with heavy hail
  80+ with WMO code check — also catches heavy rain (65, 67) + freezing rain

State file: ops/storm-trigger-state.json
Log file:   ops/storm-trigger.log
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta
from collections import defaultdict

# ─── Add ops path for shared utilities ───────────────────────────────────────

sys.path.insert(0, os.path.expanduser("~/thecalltaker/ops"))

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
BUSINESS_EMAIL = "thecalltakerai@gmail.com"
PILOT_URL = "https://thecalltaker.com/try-live"
DEMO_LINE = "(615) 784-5747"

# ntfy topics (see CLAUDE.md — standardized March 2 2026)
NTFY_SALES = "tct-sales-63uYsIT9"
NTFY_SYSTEM = "tct-system-vRsfXQRQ"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"

STATE_FILE = os.path.expanduser("~/thecalltaker/ops/storm-trigger-state.json")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/storm-trigger.log")

# Open-Meteo (free, no API key)
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Severe weather WMO codes that trigger a blast
# https://open-meteo.com/en/docs — WMO Weather Interpretation Codes (WW)
SEVERE_CODES = {
    95,   # Thunderstorm: slight or moderate
    96,   # Thunderstorm with slight hail
    99,   # Thunderstorm with heavy hail
    65,   # Heavy rain at time of observation
    67,   # Heavy freezing rain
    75,   # Heavy snow fall
    82,   # Violent rain showers
}

# Contacts with these tags get the storm blast
STORM_TARGET_TAGS = {"water-damage", "roofing"}

# Contacts with these tags are EXCLUDED
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed",
}

# Cooldown: don't blast same contact more than once every 30 days
COOLDOWN_DAYS = 30

# Don't re-trigger a storm blast for the same city within this many hours
# (prevents spamming after every 2-hour check during a long storm)
CITY_COOLDOWN_HOURS = 12

# Max emails per trigger run (safety cap)
MAX_EMAILS_PER_RUN = 30

# Delay between GHL sends (seconds) — respects rate limits
SEND_DELAY_SECONDS = 5

# GHL API headers
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-StormTrigger/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-StormTrigger/1.0",
}

# ─── 28 Target metros with pre-cached coordinates ─────────────────────────────
# Same set as storm-chaser-v2.py + expanded metros requested

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


# ─── Logging ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] storm-trigger: {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ─── State management ─────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            log("State file corrupted, starting fresh", "WARN")
    return {
        # contact_id -> ISO timestamp of last storm blast
        "contact_sent": {},
        # city_key -> ISO timestamp of last storm trigger
        "city_triggered": {},
        # Historical record of all storm events fired
        "events": [],
        "stats": {
            "total_emails_sent": 0,
            "total_storm_events": 0,
            "total_runs": 0,
            "last_run": None,
        },
    }


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


# ─── Weather API ──────────────────────────────────────────────────────────────

def get_current_weather_code(lat, lon):
    """
    Fetch the current WMO weather code for a lat/lon using Open-Meteo.
    Returns (weather_code, description) or (None, None) on failure.
    """
    try:
        resp = requests.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "weather_code,precipitation,wind_speed_10m",
                "forecast_days": 1,
            },
            timeout=12,
        )
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current", {})
            code = current.get("weather_code")
            precip = current.get("precipitation", 0)
            wind = current.get("wind_speed_10m", 0)
            return code, precip, wind
    except Exception as e:
        log(f"Weather API error for ({lat},{lon}): {e}", "WARN")
    return None, None, None


def is_severe(weather_code, precipitation, wind_speed):
    """
    Determine if current conditions qualify as severe.
    Returns (True/False, reason_string).

    Primary trigger: WMO severe codes.
    Secondary trigger: heavy precipitation (>10mm/hr) even without explicit
    thunderstorm code — catches flash-flood conditions Open-Meteo sometimes
    codes as 61-67 range without escalating to 95+.
    """
    if weather_code is None:
        return False, "no data"

    if weather_code in SEVERE_CODES:
        code_labels = {
            95: "thunderstorm",
            96: "thunderstorm with hail",
            99: "thunderstorm with heavy hail",
            65: "heavy rain",
            67: "heavy freezing rain",
            75: "heavy snow",
            82: "violent rain showers",
        }
        return True, code_labels.get(weather_code, f"severe code {weather_code}")

    # Catch heavy precip at borderline codes (61-67 range)
    if precipitation and precipitation >= 10 and 60 <= weather_code <= 69:
        return True, f"heavy precipitation ({precipitation}mm/hr, code {weather_code})"

    return False, f"code {weather_code} — not severe"


# ─── GHL API helpers ──────────────────────────────────────────────────────────

def ghl_request(method, path, headers=None, params=None, json_body=None, retries=3):
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    for attempt in range(retries):
        try:
            resp = requests.request(
                method, url,
                headers=headers, params=params, json=json_body,
                timeout=30,
            )
            if resp.status_code == 429:
                wait = [30, 60, 120][min(attempt, 2)]
                log(f"Rate limited — waiting {wait}s", "WARN")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                wait = [5, 15, 30][min(attempt, 2)]
                time.sleep(wait)
                continue
            if resp.status_code >= 400:
                log(f"GHL API error {resp.status_code}: {resp.text[:200]}", "ERROR")
                return None
            return resp.json() if resp.text else {}
        except requests.exceptions.RequestException as e:
            log(f"Request exception: {e}", "ERROR")
            if attempt < retries - 1:
                time.sleep(5)
    return None


def get_contacts_by_tag(tag):
    """
    Fetch all contacts that have a specific tag.
    GHL contacts API supports tag filter via query param.
    Falls back to paginating all contacts and filtering locally if needed.
    """
    contacts = []
    page = 1
    while True:
        data = ghl_request("GET", "/contacts/", params={
            "locationId": GHL_LOCATION_ID,
            "limit": 100,
            "page": page,
            "tags": tag,
        })
        if not data or "contacts" not in data:
            break
        batch = data["contacts"]
        contacts.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > 50:
            break
    return contacts


def get_storm_targets():
    """
    Return all contacts tagged water-damage OR roofing that are not excluded.
    Deduplicates by contact ID.
    """
    seen_ids = set()
    targets = []

    for tag in STORM_TARGET_TAGS:
        contacts = get_contacts_by_tag(tag)
        for c in contacts:
            cid = c.get("id")
            if not cid or cid in seen_ids:
                continue
            seen_ids.add(cid)

            # Check exclusion tags
            contact_tags = set(t.lower() for t in c.get("tags", []))
            if contact_tags & EXCLUDE_TAGS:
                continue

            # Must have an email address
            if not c.get("email"):
                continue

            targets.append(c)

    return targets


def add_tag_to_contact(contact_id, tag):
    """Add a single tag to a GHL contact."""
    # Fetch current tags first to avoid overwriting
    data = ghl_request("GET", f"/contacts/{contact_id}")
    if not data or "contact" not in data:
        return False
    current_tags = data["contact"].get("tags", [])
    if tag in current_tags:
        return True  # Already tagged
    new_tags = current_tags + [tag]
    result = ghl_request("PUT", f"/contacts/{contact_id}", json_body={
        "locationId": GHL_LOCATION_ID,
        "tags": new_tags,
    })
    return result is not None


def send_email(contact_id, subject, html_body):
    """Send an email to a contact via GHL conversations API."""
    result = ghl_request(
        "POST", "/conversations/messages",
        headers=CONVERSATIONS_HEADERS,
        json_body={
            "type": "Email",
            "contactId": contact_id,
            "subject": subject,
            "html": html_body,
            "emailFrom": f"Wallace <{BUSINESS_EMAIL}>",
        },
    )
    return result is not None


# ─── ntfy ─────────────────────────────────────────────────────────────────────

def ntfy(topic, title, body, priority="default"):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers={
                "Title": safe_title,
                "Priority": priority,
                "Tags": "cloud,zap",
            },
            timeout=10,
        )
    except Exception as e:
        log(f"ntfy failed: {e}", "WARN")


# ─── City-to-metro matching ───────────────────────────────────────────────────

def normalize_city(city_str):
    """Lowercase, strip punctuation, handle common variations."""
    if not city_str:
        return ""
    return city_str.lower().strip().replace(".", "").replace(",", "")


def match_contact_to_metro(contact, metro_key):
    """
    Return True if a contact's city/state fields match a metro key.
    Handles partial matches (e.g., "Nashville, TN" matches "nashville").
    """
    city_fields = [
        contact.get("city", ""),
        contact.get("address1City", ""),
        contact.get("locationCity", ""),
    ]
    for raw_city in city_fields:
        if not raw_city:
            continue
        normalized = normalize_city(raw_city)
        # Direct match
        if normalized == metro_key:
            return True
        # Partial match (e.g., "nashville-davidson" or "greater nashville")
        if metro_key in normalized:
            return True
        # Handle multi-word metros
        if normalized in metro_key:
            return True
    return False


# ─── Email template ──────────────────────────────────────────────────────────

def build_storm_email(first_name, company_name, city, industry_type, storm_reason):
    """
    Build a storm-triggered email that feels urgent and personal.
    industry_type: 'roofing' or 'water-damage'
    storm_reason: human-readable description e.g. 'thunderstorm with hail'
    """
    city_title = city.title()

    if industry_type == "roofing":
        job_word = "roofing job"
        value_anchor = "$8,000–$15,000"
        pain_line = (
            f"Storm just hit {city_title}. "
            f"Every homeowner with a damaged roof is calling roofers right now — "
            f"the first ones to answer are the ones who get the job. "
            f"One missed call is a {value_anchor} job gone."
        )
        cta_line = (
            "We can have an AI answering every call at "
            f"{company_name} by tomorrow morning. "
            "Free 14-day pilot. No card."
        )
    else:
        # water-damage
        job_word = "water damage call"
        value_anchor = "$2,000–$8,000"
        pain_line = (
            f"Storm just hit {city_title}. "
            f"Basements are flooding and phones are ringing at every water damage company in the city. "
            f"The ones who answer first get the emergency jobs. "
            f"One missed call is a {value_anchor} restoration job."
        )
        cta_line = (
            "We can set up an AI that answers every call to "
            f"{company_name} 24/7 — starting today. "
            "Free 14-day pilot. No card."
        )

    subject = (
        f"Storm just hit {city_title} — {company_name} ready?"
    )

    html = f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.65;">

<p>Hey {first_name},</p>

<p>{pain_line}</p>

<p>{cta_line}</p>

<p>It takes 48 hours to set up. You forward your calls to our number. The AI answers every call with your company name, gets the address, confirms the emergency, and texts you the details immediately.</p>

<p style="margin: 24px 0;">
<a href="{PILOT_URL}" style="background: #f97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; letter-spacing: 0.3px;">Start Free Pilot — No Card Required</a>
</p>

<p>Or call the demo line right now: <strong>{DEMO_LINE}</strong>. Pretend you're a homeowner with an emergency — you'll see exactly what your customers would hear.</p>

<p style="color: #666; font-size: 13px;">You're getting this because a severe storm ({storm_reason}) just hit {city_title} and your company serves that area.</p>

<p>— Wallace<br>
<span style="color: #888; font-size: 13px;">Founder, The Call Taker | thecalltaker.com</span></p>

</div>"""

    return subject, html


# ─── Core scan logic ─────────────────────────────────────────────────────────

def cmd_scan(state, dry_run=False):
    """
    Main scan loop:
    1. Check all 28 metros for severe weather
    2. For metros with active storm, find matching water-damage/roofing contacts
    3. Blast storm email, tag contacts, log event, send ntfy to SALES
    """
    log(f"=== Storm Trigger {'DRY RUN' if dry_run else 'LIVE'} — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    state["stats"]["total_runs"] = state["stats"].get("total_runs", 0) + 1
    state["stats"]["last_run"] = datetime.now().isoformat()

    # Step 1: Check each metro for severe weather
    storm_metros = []
    for metro_key, (lat, lon) in METRO_COORDS.items():
        # Check city cooldown — don't re-trigger within CITY_COOLDOWN_HOURS
        last_triggered = state["city_triggered"].get(metro_key)
        if last_triggered:
            last_dt = datetime.fromisoformat(last_triggered)
            hours_since = (datetime.now() - last_dt).total_seconds() / 3600
            if hours_since < CITY_COOLDOWN_HOURS:
                log(f"  {metro_key}: skipped (triggered {hours_since:.1f}h ago, cooldown {CITY_COOLDOWN_HOURS}h)")
                continue

        code, precip, wind = get_current_weather_code(lat, lon)
        severe, reason = is_severe(code, precip, wind)

        if severe:
            log(f"  STORM DETECTED: {metro_key} — {reason} (code={code}, precip={precip}mm, wind={wind}km/h)")
            storm_metros.append({
                "metro": metro_key,
                "reason": reason,
                "code": code,
                "precip": precip,
                "wind": wind,
            })
        else:
            log(f"  {metro_key}: clear ({reason})")

        time.sleep(0.3)  # Be gentle with the free API

    if not storm_metros:
        log("No severe weather detected across all 28 metros. Nothing to send.")
        save_state(state)
        return

    log(f"{len(storm_metros)} metro(s) with active storms: {[m['metro'] for m in storm_metros]}")

    # Step 2: Load all storm-target contacts once (one GHL bulk fetch is cheaper than 28 separate queries)
    log("Fetching water-damage + roofing contacts from GHL...")
    all_targets = get_storm_targets()
    log(f"Found {len(all_targets)} total storm-target contacts in GHL")

    total_sent = 0
    storm_events = []

    for metro_info in storm_metros:
        metro_key = metro_info["metro"]
        storm_reason = metro_info["reason"]

        if total_sent >= MAX_EMAILS_PER_RUN:
            log(f"Hit MAX_EMAILS_PER_RUN ({MAX_EMAILS_PER_RUN}), stopping")
            break

        # Find contacts in this metro
        metro_contacts = [c for c in all_targets if match_contact_to_metro(c, metro_key)]
        log(f"  {metro_key}: {len(metro_contacts)} matching contacts")

        if not metro_contacts:
            log(f"  {metro_key}: no contacts found — skipping")
            continue

        sent_this_metro = 0
        skipped_cooldown = 0

        for contact in metro_contacts:
            if total_sent >= MAX_EMAILS_PER_RUN:
                break

            cid = contact.get("id")
            first_name = contact.get("firstName") or "there"
            company_name = contact.get("companyName") or "your company"
            email_addr = contact.get("email", "")

            # Per-contact cooldown
            last_sent = state["contact_sent"].get(cid)
            if last_sent:
                last_dt = datetime.fromisoformat(last_sent)
                days_since = (datetime.now() - last_dt).days
                if days_since < COOLDOWN_DAYS:
                    skipped_cooldown += 1
                    continue

            # Determine industry type for template
            contact_tags = [t.lower() for t in contact.get("tags", [])]
            if "roofing" in contact_tags:
                industry_type = "roofing"
            else:
                industry_type = "water-damage"

            subject, html = build_storm_email(
                first_name, company_name, metro_key, industry_type, storm_reason
            )

            storm_date_tag = f"storm-outreach-{datetime.now().strftime('%Y-%m-%d')}"

            if dry_run:
                log(
                    f"    [DRY RUN] Would email {first_name} at {company_name} "
                    f"({email_addr}, {industry_type}) — subject: {subject}"
                )
                sent_this_metro += 1
                total_sent += 1
                continue

            # Send email
            ok = send_email(cid, subject, html)
            if ok:
                # Tag the contact to prevent double-sending
                add_tag_to_contact(cid, storm_date_tag)
                state["contact_sent"][cid] = datetime.now().isoformat()
                sent_this_metro += 1
                total_sent += 1
                log(f"    SENT to {first_name} at {company_name} ({industry_type})")
            else:
                log(f"    FAILED to send to {first_name} at {company_name}", "ERROR")

            time.sleep(SEND_DELAY_SECONDS)

        log(
            f"  {metro_key}: sent={sent_this_metro}, skipped_cooldown={skipped_cooldown}"
        )

        if sent_this_metro > 0 or dry_run:
            # Mark city as triggered
            state["city_triggered"][metro_key] = datetime.now().isoformat()
            state["stats"]["total_storm_events"] = state["stats"].get("total_storm_events", 0) + 1

            # Record event
            event = {
                "timestamp": datetime.now().isoformat(),
                "metro": metro_key,
                "storm_reason": storm_reason,
                "contacts_blasted": sent_this_metro,
                "dry_run": dry_run,
            }
            state.setdefault("events", []).append(event)
            # Keep last 100 events only
            state["events"] = state["events"][-100:]
            storm_events.append(event)

    # Step 3: Update total stats
    state["stats"]["total_emails_sent"] = (
        state["stats"].get("total_emails_sent", 0) + total_sent
    )

    # Step 4: ntfy SALES topic summary
    if storm_events and not dry_run:
        lines = []
        for ev in storm_events:
            lines.append(
                f"{ev['metro'].title()}: {ev['contacts_blasted']} contacts blasted ({ev['storm_reason']})"
            )
        body = "\n".join(lines) + f"\n\nTotal emails sent this run: {total_sent}"
        ntfy(
            NTFY_SALES,
            f"[STORM TRIGGER] {len(storm_events)} city/cities hit — {total_sent} emails sent",
            body,
            priority="high",
        )
        log(f"ntfy SALES alert sent for {len(storm_events)} storm event(s)")
    elif storm_events and dry_run:
        log(f"[DRY RUN] Would have sent ntfy for {len(storm_events)} event(s)")

    log(
        f"=== Storm Trigger complete. "
        f"Metros checked: {len(METRO_COORDS)}. "
        f"Storms found: {len(storm_metros)}. "
        f"Emails sent: {total_sent}. ==="
    )

    save_state(state)
    return total_sent


# ─── Status command ───────────────────────────────────────────────────────────

def cmd_status(state):
    stats = state.get("stats", {})
    events = state.get("events", [])
    city_triggered = state.get("city_triggered", {})
    contact_sent = state.get("contact_sent", {})

    print("\n╔══════════════════════════════════════════════╗")
    print("║        STORM TRIGGER — STATUS                ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  Total Emails Sent:   {stats.get('total_emails_sent', 0):>6}               ║")
    print(f"║  Storm Events Fired:  {stats.get('total_storm_events', 0):>6}               ║")
    print(f"║  Total Scan Runs:     {stats.get('total_runs', 0):>6}               ║")
    print(f"║  Contacts Blasted:    {len(contact_sent):>6}               ║")
    print(f"║  Last Run:            {(stats.get('last_run') or 'never')[:19]:>19} ║")
    print("╚══════════════════════════════════════════════╝\n")

    if city_triggered:
        print("Recently triggered metros:")
        now = datetime.now()
        for city, ts in sorted(city_triggered.items(), key=lambda x: x[1], reverse=True)[:10]:
            hours_ago = (now - datetime.fromisoformat(ts)).total_seconds() / 3600
            cooldown_remaining = max(0, CITY_COOLDOWN_HOURS - hours_ago)
            print(f"  {city:20} {hours_ago:5.1f}h ago  (cooldown: {cooldown_remaining:.1f}h left)")
        print()

    if events:
        print("Last 10 storm events:")
        for ev in events[-10:][::-1]:
            ts = ev.get("timestamp", "")[:16]
            metro = ev.get("metro", "?").title()
            count = ev.get("contacts_blasted", 0)
            reason = ev.get("storm_reason", "?")
            dry = " [DRY RUN]" if ev.get("dry_run") else ""
            print(f"  {ts}  {metro:20} {count:>3} emails  {reason}{dry}")
        print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(
            "Usage: storm-trigger.py <scan|status|test>\n"
            "  scan   — Check all 28 metros, blast storm emails to roofing/water-damage contacts\n"
            "  status — Show stats, recent events, city cooldowns\n"
            "  test   — Dry run (check weather only, log targets, send nothing)\n"
        )
        sys.exit(1)

    command = sys.argv[1].lower()
    state = load_state()

    try:
        if command == "scan":
            cmd_scan(state, dry_run=False)
        elif command == "test":
            cmd_scan(state, dry_run=True)
        elif command == "status":
            cmd_status(state)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except KeyboardInterrupt:
        log("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log(f"CRASH: {e}\n{tb}", "ERROR")
        ntfy(
            NTFY_SYSTEM,
            "[CRITICAL] Storm Trigger Crashed",
            f"Error: {str(e)[:300]}\n\n{tb[:500]}",
            priority="urgent",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
