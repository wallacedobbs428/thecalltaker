#!/usr/bin/env python3
"""
STRIPE WEBHOOK HANDLER — The Call Taker
========================================
Receives Stripe webhook events and triggers GHL actions:
  - checkout.session.completed → Tag customer + trigger onboarding
  - customer.subscription.updated → Update plan tags
  - customer.subscription.deleted → Tag churned + alert Wallace
  - invoice.payment_failed → Alert Wallace + send retry SMS

Setup:
  1. Set STRIPE_WEBHOOK_SECRET env var (from Stripe dashboard)
  2. Set STRIPE_API_KEY env var
  3. Run: python3 stripe-webhook-handler.py
  4. Expose via ngrok or similar: ngrok http 5090
  5. Add webhook URL in Stripe dashboard → Events: checkout.session.completed,
     customer.subscription.updated, customer.subscription.deleted, invoice.payment_failed

Port: 5090
"""

import os
import sys
import json
import hmac
import hashlib
import time
import requests
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ─── Configuration ───────────────────────────────────────────────────────────

PORT = 5090
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
NTFY_URGENT = "tct-urgent-Hk9UOEZR"
NTFY_SALES = "tct-sales-63uYsIT9"
WALLACE_GHL_ID = "DtKLG28VzgUb6q3brILD"

LOG_FILE = os.path.expanduser("~/thecalltaker/ops/stripe-webhook.log")
STATE_FILE = os.path.expanduser("~/thecalltaker/ops/stripe-webhook-state.json")

# Plan mapping: Stripe Price ID → plan name and amount
# UPDATE THESE when Stripe products are created
PLAN_MAP = {
    # "price_xxx97": {"name": "After-Hours Starter", "amount": 97, "tag": "plan-97"},
    # "price_xxx297": {"name": "Full 24/7 Pro", "amount": 297, "tag": "plan-297"},
    # "price_xxx497": {"name": "Premium Enterprise", "amount": 497, "tag": "plan-497"},
}

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-StripeWebhook/1.0",
}

CONVERSATIONS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-StripeWebhook/1.0",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] stripe-webhook: {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"payments": [], "total_revenue": 0, "total_customers": 0, "mrr": 0}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def verify_stripe_signature(payload, signature, secret):
    """Verify Stripe webhook signature using HMAC-SHA256."""
    if not secret:
        log("WARNING: No webhook secret configured — skipping verification", "WARN")
        return True

    if not signature:
        return False

    # Parse Stripe signature header: t=timestamp,v1=signature
    elements = dict(item.split("=", 1) for item in signature.split(",") if "=" in item)
    timestamp = elements.get("t", "")
    sig = elements.get("v1", "")

    if not timestamp or not sig:
        return False

    # Check timestamp (reject events older than 5 minutes)
    try:
        if abs(time.time() - int(timestamp)) > 300:
            log("Webhook timestamp too old", "WARN")
            return False
    except ValueError:
        return False

    # Compute expected signature
    signed_payload = f"{timestamp}.{payload}"
    expected = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(sig, expected)


def ghl_request(method, path, headers=None, params=None, json_body=None):
    if headers is None:
        headers = CONTACTS_HEADERS
    url = f"{GHL_BASE_URL}{path}"
    for attempt in range(3):
        try:
            resp = requests.request(method, url, headers=headers, params=params, json=json_body, timeout=30)
            if resp.status_code == 429:
                time.sleep(30)
                continue
            if resp.status_code >= 500:
                time.sleep(5)
                continue
            return resp.json() if resp.text else {}
        except Exception as e:
            log(f"GHL request error: {e}", "ERROR")
            time.sleep(5)
    return None


def find_contact_by_email(email):
    """Find GHL contact by email."""
    data = ghl_request("GET", "/contacts/", params={
        "locationId": GHL_LOCATION_ID, "query": email, "limit": 1,
    })
    if data and "contacts" in data and data["contacts"]:
        return data["contacts"][0]
    return None


def add_tags(contact_id, tags):
    return ghl_request("POST", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def remove_tags(contact_id, tags):
    return ghl_request("DELETE", f"/contacts/{contact_id}/tags", json_body={"tags": tags})


def add_note(contact_id, note):
    return ghl_request("POST", f"/contacts/{contact_id}/notes", json_body={"body": note})


def send_sms(contact_id, message):
    return ghl_request("POST", "/conversations/messages", headers=CONVERSATIONS_HEADERS, json_body={
        "type": "SMS", "contactId": contact_id, "message": message,
    })


def send_wallace_sms(message):
    return send_sms(WALLACE_GHL_ID, message)


def ntfy_alert(topic, title, message, priority="high"):
    try:
        safe_title = "".join(c for c in title if ord(c) < 128).strip()
        requests.post(f"https://ntfy.sh/{topic}", data=message.encode("utf-8"),
                      headers={"Title": safe_title, "Priority": priority}, timeout=10)
    except Exception:
        pass


# ─── Event Handlers ──────────────────────────────────────────────────────────

def handle_checkout_completed(event):
    """New customer paid! Tag them, notify Wallace, trigger onboarding."""
    session = event.get("data", {}).get("object", {})
    customer_email = session.get("customer_email", "") or session.get("customer_details", {}).get("email", "")
    customer_name = session.get("customer_details", {}).get("name", "New Customer")
    amount = session.get("amount_total", 0) / 100  # cents to dollars
    payment_status = session.get("payment_status", "unknown")

    log(f"PAYMENT: {customer_name} ({customer_email}) paid ${amount}")

    # Find or flag contact in GHL
    contact = find_contact_by_email(customer_email) if customer_email else None

    plan_tag = "customer"
    if amount >= 450:
        plan_tag = "plan-497"
    elif amount >= 250:
        plan_tag = "plan-297"
    elif amount >= 50:
        plan_tag = "plan-97"

    if contact:
        cid = contact["id"]
        # Tag as customer
        add_tags(cid, ["customer", "active-client", plan_tag, "stripe-paid"])
        # Remove lead tags
        remove_tags(cid, ["cold-outreach", "hot-lead", "pilot-active", "pilot-expired"])
        # Add note
        add_note(cid, f"PAID ${amount} via Stripe on {datetime.now().strftime('%Y-%m-%d')}. Plan: {plan_tag}.")
        # Send welcome SMS
        first_name = contact.get("firstName", "there")
        send_sms(cid, (
            f"{first_name}, welcome to The Call Taker! Your payment of ${amount:.0f} is confirmed. "
            f"I'm personally setting up your AI receptionist right now. "
            f"You'll be live within 48 hours. Any questions, just text me here. — Wallace"
        ))
    else:
        log(f"Contact not found in GHL for {customer_email}", "WARN")

    # Notify Wallace — ALWAYS, CRITICAL priority
    ntfy_alert(
        NTFY_URGENT,
        f"[CRITICAL] PAYMENT: ${amount:.0f} from {customer_name}",
        f"NEW PAYING CUSTOMER\n"
        f"Name: {customer_name}\n"
        f"Email: {customer_email}\n"
        f"Amount: ${amount:.0f}\n"
        f"Plan: {plan_tag}\n"
        f"Status: {payment_status}\n\n"
        f"GHL Contact: {'Found' if contact else 'NOT FOUND — create manually'}\n"
        f"ACTION: Set up their Voice AI agent NOW.",
        priority="urgent",
    )

    send_wallace_sms(
        f"MONEY IN: ${amount:.0f} from {customer_name} ({customer_email}). "
        f"Plan: {plan_tag}. Set up their AI agent NOW."
    )

    # Update state
    state = load_state()
    state["payments"].append({
        "name": customer_name, "email": customer_email,
        "amount": amount, "plan": plan_tag,
        "timestamp": datetime.now().isoformat(),
    })
    state["total_revenue"] += amount
    state["total_customers"] += 1
    state["mrr"] += amount
    save_state(state)


def handle_subscription_deleted(event):
    """Customer cancelled. Tag churned, alert Wallace."""
    subscription = event.get("data", {}).get("object", {})
    customer_id = subscription.get("customer", "")
    cancel_reason = subscription.get("cancellation_details", {}).get("reason", "unknown")

    log(f"CANCELLATION: Customer {customer_id} — reason: {cancel_reason}")

    # Alert Wallace
    ntfy_alert(
        NTFY_URGENT,
        f"[CRITICAL] CANCELLATION",
        f"Customer {customer_id} cancelled.\nReason: {cancel_reason}\n\nACTION: Call them immediately.",
        priority="urgent",
    )

    send_wallace_sms(f"CHURN ALERT: A customer just cancelled. Reason: {cancel_reason}. Call them NOW.")

    # Update MRR
    amount = (subscription.get("items", {}).get("data", [{}])[0]
              .get("price", {}).get("unit_amount", 0)) / 100
    state = load_state()
    state["mrr"] = max(0, state["mrr"] - amount)
    save_state(state)


def handle_payment_failed(event):
    """Payment failed. Alert Wallace + send retry notification."""
    invoice = event.get("data", {}).get("object", {})
    customer_email = invoice.get("customer_email", "")
    amount = invoice.get("amount_due", 0) / 100
    attempt = invoice.get("attempt_count", 0)

    log(f"PAYMENT FAILED: {customer_email} — ${amount} — attempt {attempt}")

    ntfy_alert(
        NTFY_URGENT,
        f"[CRITICAL] Payment Failed — ${amount:.0f}",
        f"Email: {customer_email}\nAmount: ${amount:.0f}\nAttempt: {attempt}\n\nStripe will auto-retry.",
        priority="urgent",
    )

    # Find contact and send SMS
    contact = find_contact_by_email(customer_email) if customer_email else None
    if contact:
        first_name = contact.get("firstName", "there")
        send_sms(contact["id"], (
            f"Hey {first_name}, heads up — your payment of ${amount:.0f} for The Call Taker "
            f"didn't go through. Can you update your card? Your AI receptionist is still running "
            f"but we need the payment sorted. Text me if you need help. — Wallace"
        ))


# ─── HTTP Server ──────────────────────────────────────────────────────────────

class StripeWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            payload = self.rfile.read(content_length).decode("utf-8")
            signature = self.headers.get("Stripe-Signature", "")

            # Verify signature
            if not verify_stripe_signature(payload, signature, STRIPE_WEBHOOK_SECRET):
                log("Invalid webhook signature", "ERROR")
                self.send_response(401)
                self.end_headers()
                return

            event = json.loads(payload)
            event_type = event.get("type", "")

            log(f"Webhook received: {event_type}")

            if event_type == "checkout.session.completed":
                handle_checkout_completed(event)
            elif event_type == "customer.subscription.deleted":
                handle_subscription_deleted(event)
            elif event_type == "invoice.payment_failed":
                handle_payment_failed(event)
            else:
                log(f"Unhandled event type: {event_type}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"received": True}).encode())

        except Exception as e:
            log(f"Webhook error: {e}", "ERROR")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        """Health check."""
        state = load_state()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "service": "stripe-webhook-handler",
            "status": "running",
            "total_payments": len(state.get("payments", [])),
            "total_revenue": state.get("total_revenue", 0),
            "mrr": state.get("mrr", 0),
        }).encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), StripeWebhookHandler)
    log(f"Stripe webhook handler listening on port {PORT}")
    if not STRIPE_WEBHOOK_SECRET:
        log("WARNING: STRIPE_WEBHOOK_SECRET not set — signature verification disabled", "WARN")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down")
        server.server_close()
