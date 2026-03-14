#!/usr/bin/env python3
"""
DEMO BOOKED WEBHOOK HANDLER — The Call Taker
=============================================
Lightweight Flask webhook that GHL calls when a demo is booked on the calendar.
Triggers the hot-lead-converter notify command to alert Wallace immediately.

GHL Workflow Setup:
  Trigger: Calendar → Appointment Created (Calendar ID: h4IlzccZ1m3JprEQqpMJ)
  Action:  Webhook → POST to this server with contact data

Run: python3 demo-booked-webhook.py
Port: 5089
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 5089
CONVERTER_SCRIPT = os.path.expanduser("~/thecalltaker/ops/hot-lead-converter.py")
LOG_FILE = os.path.expanduser("~/thecalltaker/ops/demo-booked-webhook.log")


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] demo-booked-webhook: {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}

            # Extract contact ID from GHL webhook payload
            contact_id = (
                data.get("contactId")
                or data.get("contact_id")
                or data.get("contact", {}).get("id", "")
            )
            source = data.get("source", "ghl-calendar-webhook")

            log(f"Demo booked webhook received. Contact: {contact_id}")

            # Trigger the converter notification
            if contact_id:
                subprocess.Popen(
                    [sys.executable, CONVERTER_SCRIPT, "notify", contact_id, source],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())

        except Exception as e:
            log(f"Error: {e}")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        """Health check endpoint."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "service": "demo-booked-webhook",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
        }).encode())

    def log_message(self, format, *args):
        """Suppress default access logs."""
        pass


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    log(f"Demo booked webhook listening on port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down")
        server.server_close()
