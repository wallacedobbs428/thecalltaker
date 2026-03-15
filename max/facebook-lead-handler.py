#!/usr/bin/env python3
"""
Facebook Lead Ad Webhook Handler — The Call Taker
Receives Facebook Lead Ad form submissions, creates GHL contacts, sends instant SMS + ntfy.

Setup:
  1. Run: python3 facebook-lead-handler.py serve (listens on port 8089)
  2. Set Facebook webhook URL to: https://your-domain.com/facebook-lead (via ngrok or server)
  3. Verify token: tct-fb-verify-2026

Usage:
  python3 facebook-lead-handler.py serve     # Start webhook server
  python3 facebook-lead-handler.py test      # Send test lead
  python3 facebook-lead-handler.py status    # Show today's stats
"""

import json
import sys
import os
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ===================================================
# CONFIG
# ===================================================

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

FB_VERIFY_TOKEN = os.environ.get("TCT_FB_VERIFY_TOKEN", "tct-fb-verify-2026")
WEBHOOK_PORT = int(os.environ.get("TCT_FB_WEBHOOK_PORT", "8089"))

# ntfy topics
NTFY_SALES = "tct-sales-63uYsIT9"
NTFY_URGENT = "tct-urgent-Hk9UOEZR"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "facebook-leads.log")
STATE_FILE = os.path.join(SCRIPT_DIR, "facebook-lead-state.json")

# Industry display names
INDUSTRY_NAMES = {
    "hvac": "HVAC", "plumbing": "Plumbing", "dental": "Dental",
    "roofing": "Roofing", "electrical": "Electrical", "locksmith": "Locksmith",
    "towing": "Towing", "pest-control": "Pest Control", "legal": "Legal",
    "med-spa": "Med Spa", "veterinary": "Veterinary", "property-mgmt": "Property Management",
    "garage-door": "Garage Door",
}

# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] FB-LEAD: {msg}"
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
        "User-Agent": "FBLeadHandler/1.0 TheCallTaker",
    }
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    for attempt in range(3):
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            if e.code == 429:
                time.sleep(30 * (attempt + 1))
                continue
            error_body = e.read().decode() if e.fp else ""
            log(f"GHL Error {e.code}: {method} {path} — {error_body[:200]}")
            return None
        except Exception as e:
            log(f"GHL Error: {e}")
            if attempt < 2:
                time.sleep(5)
                continue
            return None
    return None


def send_ntfy(topic, title, message, priority="high"):
    """Send ntfy notification."""
    url = f"https://ntfy.sh/{topic}"
    # Sanitize headers (no newlines)
    safe_title = title.replace("\n", " ").replace("\r", "")[:200]
    headers = {
        "Title": safe_title,
        "Priority": priority,
        "Tags": "facebook,lead",
    }
    data = message.encode("utf-8")
    req = Request(url, data=data, headers=headers, method="POST")
    for attempt in range(3):
        try:
            with urlopen(req, timeout=10) as resp:
                return True
        except Exception as e:
            log(f"ntfy error (attempt {attempt+1}): {e}")
            time.sleep(2)
    return False


def save_state(data):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, STATE_FILE)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"leads_today": 0, "leads_total": 0, "last_lead": None, "today": None, "leads": []}


# ===================================================
# LEAD PROCESSING
# ===================================================

def process_lead(name, business, industry, phone):
    """Process a single Facebook lead: GHL contact + SMS + ntfy."""
    log(f"Processing lead: {name} / {business} / {industry} / {phone}")

    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")
    if state.get("today") != today:
        state["leads_today"] = 0
        state["today"] = today

    # Format phone
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    formatted_phone = f"+{digits}"

    industry_display = INDUSTRY_NAMES.get(industry, industry.title() if industry else "Service")

    # 1. Create GHL contact
    tags = ["facebook-lead", "hot-lead", "pilot-candidate"]
    if industry:
        tags.append(industry)

    contact_resp = ghl_request("POST", "/contacts/", {
        "firstName": name.split()[0] if name else "",
        "lastName": " ".join(name.split()[1:]) if name and len(name.split()) > 1 else "",
        "companyName": business,
        "phone": formatted_phone,
        "locationId": GHL_LOCATION_ID,
        "tags": tags,
        "source": "Facebook Lead Ad",
    })

    contact_id = None
    if contact_resp and "contact" in contact_resp:
        contact_id = contact_resp["contact"].get("id")
        log(f"GHL contact created: {contact_id}")
    else:
        log(f"GHL contact creation failed for {name}")

    # 2. Send instant SMS
    first_name = name.split()[0] if name else ""
    sms_text = (
        f"Hey{' ' + first_name if first_name else ''}, this is Wallace from The Call Taker — "
        f"you just requested info about our 24/7 receptionist for {industry_display.lower()} businesses. "
        f"Can I show you a quick demo? Reply YES and I'll call you in 5 minutes."
    )

    if contact_id:
        sms_resp = ghl_request("POST", "/conversations/messages", {
            "type": "SMS",
            "contactId": contact_id,
            "message": sms_text,
        }, version="2021-04-15")
        if sms_resp:
            log(f"SMS sent to {formatted_phone}")
        else:
            log(f"SMS failed to {formatted_phone}")

    # 3. Send ntfy alert
    ntfy_title = f"[FACEBOOK LEAD] {name} — {business}"
    ntfy_body = (
        f"Name: {name}\n"
        f"Business: {business}\n"
        f"Industry: {industry_display}\n"
        f"Phone: {phone}\n"
        f"---\n"
        f"SMS auto-sent. Reply YES = call in 5 min.\n"
        f"Contact ID: {contact_id or 'FAILED'}"
    )
    send_ntfy(NTFY_URGENT, ntfy_title, ntfy_body, priority="urgent")

    # 4. Update state
    state["leads_today"] = state.get("leads_today", 0) + 1
    state["leads_total"] = state.get("leads_total", 0) + 1
    state["last_lead"] = {
        "name": name,
        "business": business,
        "industry": industry,
        "phone": phone,
        "time": datetime.now().isoformat(),
        "contact_id": contact_id,
    }
    state.setdefault("leads", []).append({
        "name": name,
        "business": business,
        "industry": industry,
        "phone": phone,
        "time": datetime.now().isoformat(),
        "date": today,
    })
    save_state(state)

    log(f"Lead processed: {name} ({business}) — {industry_display}")
    return contact_id


# ===================================================
# WEBHOOK SERVER
# ===================================================

class LeadWebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for Facebook Lead Ad webhooks."""

    def do_GET(self):
        """Facebook webhook verification."""
        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(self.path).query)

        mode = params.get("hub.mode", [None])[0]
        token = params.get("hub.verify_token", [None])[0]
        challenge = params.get("hub.challenge", [None])[0]

        if mode == "subscribe" and token == FB_VERIFY_TOKEN and challenge:
            log("Facebook webhook verification successful")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(challenge.encode())
        else:
            log(f"Webhook verification failed: mode={mode}, token={token}")
            self.send_response(403)
            self.end_headers()

    def do_POST(self):
        """Handle incoming lead data."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 1048576:  # 1MB limit
            self.send_response(413)
            self.end_headers()
            return

        body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            log(f"Invalid JSON received: {body[:200]}")
            self.send_response(400)
            self.end_headers()
            return

        log(f"Webhook received: {json.dumps(data)[:500]}")

        # Facebook sends data in entry[].changes[].value.leadgen_id format
        # But we also accept direct POST from our landing page
        name = ""
        business = ""
        industry = ""
        phone = ""

        # Try Facebook format first
        entries = data.get("entry", [])
        if entries:
            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    # Facebook Lead Ads: need to fetch lead data via Graph API
                    leadgen_id = value.get("leadgen_id")
                    if leadgen_id:
                        log(f"Facebook leadgen_id: {leadgen_id} — fetch via Graph API")
                        # Note: Full Graph API fetch requires FB access token
                        # For now, log and alert — leads also come through landing page
                        send_ntfy(NTFY_SALES,
                            "[FB LEADGEN] New lead via native form",
                            f"Leadgen ID: {leadgen_id}\nFetch via Graph API to get details.",
                            priority="high")

        # Direct POST format (from landing page)
        if not name:
            name = data.get("firstName", data.get("name", ""))
            business = data.get("companyName", data.get("businessName", data.get("business", "")))
            industry = data.get("industry", "")
            phone = data.get("phone", "")

        if name or phone:
            process_lead(name, business, industry, phone)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def log_message(self, format, *args):
        """Suppress default HTTP logging — we use our own."""
        pass


def start_server():
    """Start the webhook server."""
    server = HTTPServer(("0.0.0.0", WEBHOOK_PORT), LeadWebhookHandler)
    log(f"Facebook Lead webhook server starting on port {WEBHOOK_PORT}")
    log(f"Verify token: {FB_VERIFY_TOKEN}")
    print(f"\n  Facebook Lead Ad Webhook Server")
    print(f"  Listening on port {WEBHOOK_PORT}")
    print(f"  Verify token: {FB_VERIFY_TOKEN}")
    print(f"  Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Server stopped")
        server.server_close()


def send_test_lead():
    """Send a test lead through the pipeline."""
    print("Sending test lead...")
    cid = process_lead(
        name="Test Lead",
        business="Test HVAC Co",
        industry="hvac",
        phone="6155550199",
    )
    print(f"Test complete. Contact ID: {cid}")


def show_status():
    """Show today's lead stats."""
    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")

    total = state.get("leads_total", 0)
    today_count = state.get("leads_today", 0) if state.get("today") == today else 0
    last = state.get("last_lead")

    print()
    print(f"  Facebook Lead Handler Status")
    print(f"  Today: {today_count} leads")
    print(f"  Total: {total} leads")
    if last:
        print(f"  Last: {last['name']} ({last['business']}) — {last.get('time', 'unknown')}")
    print()

    # Industry breakdown
    leads = state.get("leads", [])
    if leads:
        by_industry = {}
        for l in leads:
            ind = l.get("industry", "unknown")
            by_industry[ind] = by_industry.get(ind, 0) + 1
        print("  By Industry:")
        for ind, count in sorted(by_industry.items(), key=lambda x: -x[1]):
            print(f"    {INDUSTRY_NAMES.get(ind, ind):20s} {count}")
    print()


# ===================================================
# MAIN
# ===================================================

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "serve"

    if cmd == "serve":
        start_server()
    elif cmd == "test":
        send_test_lead()
    elif cmd == "status":
        show_status()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 facebook-lead-handler.py [serve|test|status]")
        sys.exit(1)
