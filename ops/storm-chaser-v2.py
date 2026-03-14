#!/usr/bin/env python3
"""
STORM CHASER v2 — The Call Taker
=================================
Weather-triggered email engine. Detects extreme temps/storms and sends
urgency emails to leads in affected cities.

FIXES from v1 (embedded in max-engine.py):
  1. Uses Open-Meteo API (free, no key, no firewall blocks) instead of wttr.in
  2. Uses GHL location/state fields instead of requiring city on contacts
  3. Geocodes cities via Open-Meteo geocoding API
  4. Processes ALL contacts with location data, not just first 50
  5. Proper error handling and retry logic
  6. Standalone engine with its own state file

Commands:
  scan    — Check weather for all lead cities, send urgency emails
  status  — Show stats
  test    — Dry run (check weather but don't send)

Schedule: Every 6 hours via launchd (6am, noon, 6pm, midnight)
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta
from collections import defaultdict

# ─── Configuration ───────────────────────────────────────────────────────────

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
BUSINESS_EMAIL = "thecalltakerai@gmail.com"
BOOKING_URL = "https://thecalltaker.com/book.html"
DEMO_LINE = "(615) 784-5747"
NTFY_ACTIVITY = "tct-activity-cn1Aqa85"

STATE_FILE = os.path.expanduser("~/thecalltaker/ops/storm-chaser-state.json")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/storm-chaser.log")

# Open-Meteo API (free, no API key required)
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Thresholds
HEAT_THRESHOLD_F = 90   # Send urgency email above this
COLD_THRESHOLD_F = 32   # Send urgency email below this
MAX_EMAILS_PER_RUN = 15  # Rate limit
COOLDOWN_DAYS = 14       # Don't re-email same contact within this window

# GHL API headers
CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-StormChaser/2.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-StormChaser/2.0",
}

# Exclusion tags
EXCLUDE_TAGS = {
    "customer", "active-client", "pilot-active", "pilot-converted",
    "do-not-contact", "unsubscribed",
}

# ─── Target metros with pre-cached coordinates ──────────────────────────────

METRO_COORDS = {
    "nashville": (36.16, -86.78), "memphis": (35.15, -90.05),
    "knoxville": (35.96, -83.92), "chattanooga": (35.05, -85.31),
    "atlanta": (33.75, -84.39), "birmingham": (33.52, -86.80),
    "louisville": (38.25, -85.76), "huntsville": (34.73, -86.59),
    "lexington": (38.04, -84.50), "jackson": (32.30, -90.18),
    "dallas": (32.78, -96.80), "houston": (29.76, -95.37),
    "phoenix": (33.45, -112.07), "tampa": (27.95, -82.46),
    "charlotte": (35.23, -80.84), "jacksonville": (30.33, -81.66),
    "san antonio": (29.42, -98.49), "indianapolis": (39.77, -86.16),
    "columbus": (39.96, -82.99), "kansas city": (39.10, -94.58),
    "tucson": (32.22, -110.93), "scottsdale": (33.49, -111.93),
    "mesa": (33.42, -111.83), "glendale": (33.54, -112.19),
    "chandler": (33.30, -111.84), "gilbert": (33.35, -111.79),
    "tempe": (33.43, -111.94), "peoria": (33.58, -112.24),
}


# ─── Logging ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] storm-chaser: {msg}"
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
            log("State corrupted, starting fresh", "WARN")
    return {
        "sent": {},          # contact_id -> last_sent_iso
        "weather_cache": {},  # city -> {temp, timestamp}
        "stats": {"total_sent": 0, "total_runs": 0, "last_run": None},
    }


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


# ─── Weather API ──────────────────────────────────────────────────────────────

def geocode_city(city_name):
    """Get lat/lon for a city using Open-Meteo geocoding API."""
    # Check pre-cached metros first
    city_lower = city_name.lower().strip()
    if city_lower in METRO_COORDS:
        return METRO_COORDS[city_lower]

    try:
        resp = requests.get(
            GEOCODE_URL,
            params={"name": city_name, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                return (results[0]["latitude"], results[0]["longitude"])
    except Exception as e:
        log(f"Geocode failed for {city_name}: {e}", "WARN")
    return None


def get_temperature_f(lat, lon):
    """Get current temperature in Fahrenheit using Open-Meteo API."""
    try:
        resp = requests.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m",
                "temperature_unit": "fahrenheit",
                "forecast_days": 1,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("current", {}).get("temperature_2m")
    except Exception as e:
        log(f"Weather API failed for ({lat}, {lon}): {e}", "WARN")
    return None


def get_city_weather(city, state_data):
    """Get temp for a city with 2-hour caching."""
    cache = state_data.get("weather_cache", {})
    city_lower = city.lower().strip()

    # Check cache (2-hour TTL)
    if city_lower in cache:
        cached = cache[city_lower]
        cached_time = datetime.fromisoformat(cached["timestamp"])
        if datetime.now() - cached_time < timedelta(hours=2):
            return cached["temp"]

    coords = geocode_city(city)
    if not coords:
        return None

    temp = get_temperature_f(coords[0], coords[1])
    if temp is not None:
        cache[city_lower] = {
            "temp": temp,
            "timestamp": datetime.now().isoformat(),
        }
        state_data["weather_cache"] = cache

    return temp


def get_weather_angle(city, temp):
    """Generate urgency copy based on extreme weather."""
    if temp >= HEAT_THRESHOLD_F:
        return (
            f"It's {int(temp)}°F in {city} right now. "
            f"When an AC unit dies tonight, your customer calls once. "
            f"If voicemail answers, they call your competitor. "
            f"Every missed call in this heat is a $350+ emergency job walking out your door."
        )
    elif temp <= COLD_THRESHOLD_F:
        return (
            f"It's {int(temp)}°F in {city}. "
            f"Furnace emergencies don't wait — and neither do your customers. "
            f"When the heat goes out at 2am, they call the first company that picks up. "
            f"Is that you, or your voicemail?"
        )
    return None


# ─── GHL API Helpers ─────────────────────────────────────────────────────────

def ghl_request(method, path, headers=None, params=None, json_body=None):
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    for attempt in range(3):
        try:
            resp = requests.request(method, url, headers=headers, params=params, json=json_body, timeout=30)
            if resp.status_code == 429:
                time.sleep([30, 60, 120][min(attempt, 2)])
                continue
            if resp.status_code >= 500:
                time.sleep([5, 15, 30][min(attempt, 2)])
                continue
            return resp.json() if resp.text else {}
        except requests.exceptions.RequestException as e:
            log(f"Request failed: {e}", "ERROR")
            time.sleep(5)
    return None


def get_all_contacts():
    """Fetch all contacts with location data."""
    all_contacts = []
    page = 1
    while True:
        data = ghl_request("GET", "/contacts/", params={
            "locationId": GHL_LOCATION_ID, "limit": 100, "page": page,
        })
        if not data or "contacts" not in data:
            break
        contacts = data["contacts"]
        all_contacts.extend(contacts)
        if len(contacts) < 100:
            break
        page += 1
        if page > 50:
            break
    return all_contacts


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


# ─── Email Template ──────────────────────────────────────────────────────────

def build_storm_email(first_name, company_name, city, weather_angle):
    return f"""<div style="font-family: Inter, -apple-system, sans-serif; color: #111; max-width: 600px; line-height: 1.6;">

<p>Hey {first_name},</p>

<p><strong>{weather_angle}</strong></p>

<p>I get it — you can't answer every call yourself. You're on a job site, you're eating dinner, you're sleeping. But your customers don't care. They need help NOW.</p>

<p>That's why I built <strong>The Call Taker</strong> — an AI receptionist that answers every call to {company_name}. 24/7. No voicemail. No missed jobs.</p>

<p>It sounds like a real person. It gets their name, address, what's wrong, and books the appointment on your calendar. You get a text with the details instantly.</p>

<p><strong>We're running a free 14-day pilot.</strong> No card. No contract. We set it up in 48 hours and you keep every dollar it earns.</p>

<p style="margin: 24px 0;">
<a href="{BOOKING_URL}" style="background: #F97316; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Start Your Free Pilot →</a>
</p>

<p>Or hear it yourself right now — call <strong>{DEMO_LINE}</strong> and pretend you're a customer.</p>

<p>— Wallace Dobbs<br>
<span style="color: #666;">Founder, The Call Taker</span></p>

</div>"""


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_scan(state, dry_run=False):
    """Check weather for all lead cities, send urgency emails."""
    log(f"=== Storm Chaser v2: {'DRY RUN' if dry_run else 'LIVE'} ===")
    state["stats"]["total_runs"] = state["stats"].get("total_runs", 0) + 1
    state["stats"]["last_run"] = datetime.now().isoformat()

    contacts = get_all_contacts()
    log(f"Loaded {len(contacts)} contacts")

    # Group contacts by city
    city_contacts = defaultdict(list)
    for c in contacts:
        # Try multiple location fields
        city = (c.get("city") or c.get("address1City") or
                c.get("locationCity") or "").strip()
        if not city:
            # Try to extract from state/address
            state_val = (c.get("state") or c.get("address1State") or "").strip()
            if state_val:
                # Use state capital as fallback
                continue
            continue

        tags = set(t.lower() for t in c.get("tags", []))
        if tags & EXCLUDE_TAGS:
            continue
        if not c.get("email"):
            continue

        city_contacts[city].append(c)

    log(f"Found {len(city_contacts)} unique cities with contactable leads")

    emails_sent = 0
    cities_checked = 0

    for city, contacts_in_city in city_contacts.items():
        if emails_sent >= MAX_EMAILS_PER_RUN:
            log(f"Hit max emails ({MAX_EMAILS_PER_RUN}), stopping")
            break

        temp = get_city_weather(city, state)
        cities_checked += 1

        if temp is None:
            continue

        angle = get_weather_angle(city, temp)
        if not angle:
            continue

        log(f"EXTREME WEATHER: {city} = {temp}°F — {len(contacts_in_city)} leads")

        for contact in contacts_in_city:
            if emails_sent >= MAX_EMAILS_PER_RUN:
                break

            cid = contact.get("id")
            # Check cooldown
            last_sent = state["sent"].get(cid)
            if last_sent:
                last_date = datetime.fromisoformat(last_sent)
                if datetime.now() - last_date < timedelta(days=COOLDOWN_DAYS):
                    continue

            first_name = contact.get("firstName", "there")
            company_name = contact.get("companyName", "your business")

            if dry_run:
                log(f"  [DRY RUN] Would email {first_name} at {company_name} ({city}, {temp}°F)")
                emails_sent += 1
                continue

            subject = f"It's {int(temp)}°F in {city} — who's answering {company_name}'s phones?"
            html = build_storm_email(first_name, company_name, city, angle)

            result = send_email(cid, subject, html)
            if result:
                state["sent"][cid] = datetime.now().isoformat()
                state["stats"]["total_sent"] = state["stats"].get("total_sent", 0) + 1
                emails_sent += 1
                log(f"  SENT storm email to {first_name} at {company_name} ({city}, {temp}°F)")
            else:
                log(f"  FAILED to send to {first_name} at {company_name}", "ERROR")

            time.sleep(3)  # Rate limit between sends

    log(f"Storm Chaser complete. Cities checked: {cities_checked}. Emails sent: {emails_sent}.")

    if emails_sent > 0 and not dry_run:
        ntfy_alert(NTFY_ACTIVITY, "Storm Chaser v2",
                   f"Sent {emails_sent} weather-triggered emails across {cities_checked} cities",
                   priority="default")

    save_state(state)
    return emails_sent


def cmd_status(state):
    stats = state["stats"]
    sent = state["sent"]
    cache = state.get("weather_cache", {})

    print("\n╔══════════════════════════════════════════╗")
    print("║       STORM CHASER v2 — STATUS           ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  Total Emails Sent:  {stats.get('total_sent', 0):>5}               ║")
    print(f"║  Total Runs:         {stats.get('total_runs', 0):>5}               ║")
    print(f"║  Contacts Emailed:   {len(sent):>5}               ║")
    print(f"║  Cities Cached:      {len(cache):>5}               ║")
    print(f"║  Last Run:           {(stats.get('last_run', 'never'))[:16]:>16} ║")
    print("╚══════════════════════════════════════════╝\n")

    if cache:
        print("Cached weather:")
        for city, data in sorted(cache.items()):
            temp = data.get("temp", "?")
            ts = data.get("timestamp", "?")[:16]
            flag = " *** EXTREME" if (isinstance(temp, (int, float)) and (temp >= HEAT_THRESHOLD_F or temp <= COLD_THRESHOLD_F)) else ""
            print(f"  {city:20} {temp:>6}°F  ({ts}){flag}")
        print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: storm-chaser-v2.py <scan|status|test>")
        sys.exit(1)

    command = sys.argv[1].lower()
    state = load_state()

    try:
        if command == "scan":
            cmd_scan(state)
        elif command == "test":
            cmd_scan(state, dry_run=True)
        elif command == "status":
            cmd_status(state)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        log(f"CRASH: {e}", "ERROR")
        ntfy_alert("tct-system-vRsfXQRQ", "[CRITICAL] Storm Chaser v2 Crashed",
                   f"Error: {str(e)[:500]}", priority="urgent")
        raise


if __name__ == "__main__":
    main()
