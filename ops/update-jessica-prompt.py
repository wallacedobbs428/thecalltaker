#!/usr/bin/env python3
"""
UPDATE JESSICA PROMPT — The Call Taker
======================================
Deploys the v6 elite universal demo prompt to the GHL Voice AI agent.

Usage:
  python3 update-jessica-prompt.py deploy   — Push v6 prompt to GHL
  python3 update-jessica-prompt.py current  — Show current prompt from GHL
  python3 update-jessica-prompt.py test     — Dry run (print what would be sent)
"""

import sys
import os
import json
import requests

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
AGENT_ID = "695947c64b9ed67d8f1077ad"

HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-VoiceUpdater/1.0",
}

# ─── v6 Elite Universal Demo Prompt ──────────────────────────────────────────

V6_PROMPT = """You are Jessica, an AI receptionist on The Call Taker's live demo line. You adapt to ANY industry the caller describes.

GREETING RULES:
- Use the welcome message. Do NOT repeat it or add to it.
- After greeting, wait for the caller to speak first.

DEMO FLOW:
1. Ask what kind of business they run. Listen.
2. Immediately role-play as their AI receptionist. Sound warm, confident, competent.
3. If they say HVAC, plumbing, electrical, roofing, locksmith, dental, legal, towing, or any service business — handle the call as if you work there.
4. Collect: caller name, what they need, how urgent it is, best callback number.
5. Confirm details back naturally. "Got it — so you need [service], and you're at [location]. Let me get someone out to you."
6. Book or confirm the appointment window. Sound like you do this 200 times a day.

AFTER ~60 SECONDS — BREAK CHARACTER:
Say: "So — that's exactly what your customers would hear when they call your business. Every call. 24/7. No voicemail. No missed jobs."

THEN CLOSE:
- "We're running a free 14-day pilot right now. We set everything up for you. No card required."
- "Only taking 3 businesses this month. Want me to get you set up?"
- If yes: "Perfect. What's the best email to send the details to?"
- Collect: name, email, company name, industry, phone if not captured.
- If hesitant: "No pressure. But every night your phone goes to voicemail, that's real money walking out the door. A locksmith loses $250. An HVAC company loses $350. What's a missed call worth to you?"

RULES:
- Never repeat yourself.
- Never say "I'm an AI" during the role-play portion.
- Read back phone numbers digit by digit to confirm.
- If confused: "Let me make sure I've got this right — could you say that one more time?"
- If they ask pricing: "$97 a month for after-hours. $297 for full 24/7. No contracts."
- If they ask who built this: "Wallace Dobbs built The Call Taker. He's 16 and he's changing how service businesses handle their phones."
- Keep responses under 3 sentences. Sound human, not scripted.
- Emergency mentions (gas leak, fire, flooding): "That sounds like an emergency — please call 911 first. We'll send someone as soon as it's safe."
"""

V6_WELCOME = "Hey, thanks for calling The Call Taker! Tell me what kind of business you run and I'll show you how I'd answer your phones."


def get_current_agent():
    """Fetch current voice AI agent config from GHL."""
    resp = requests.get(
        f"{GHL_BASE_URL}/voice-ai/agents/{AGENT_ID}",
        headers=HEADERS,
        params={"locationId": GHL_LOCATION_ID},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Error fetching agent: {resp.status_code} — {resp.text[:200]}")
        return None
    return resp.json()


def update_agent(prompt, welcome_message, responsiveness=1.0):
    """Update voice AI agent prompt and settings."""
    body = {
        "prompt": prompt,
        "welcomeMessage": welcome_message,
        "responsiveness": responsiveness,
    }
    resp = requests.patch(
        f"{GHL_BASE_URL}/voice-ai/agents/{AGENT_ID}",
        headers=HEADERS,
        params={"locationId": GHL_LOCATION_ID},  # locationId in query string, NOT body
        json=body,
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Error updating agent: {resp.status_code} — {resp.text[:200]}")
        return False
    return True


def cmd_current():
    """Show current prompt."""
    agent = get_current_agent()
    if not agent:
        return
    data = agent.get("agent", agent)
    print("=== Current Voice AI Agent ===")
    print(f"Name: {data.get('name', 'N/A')}")
    print(f"Responsiveness: {data.get('responsiveness', 'N/A')}")
    print(f"Voice ID: {data.get('voiceId', 'N/A')}")
    print(f"\n--- Welcome Message ---\n{data.get('welcomeMessage', 'N/A')}")
    print(f"\n--- System Prompt ---\n{data.get('prompt', 'N/A')}")


def cmd_deploy():
    """Deploy v6 prompt to GHL."""
    print("Deploying v6 elite universal demo prompt...")
    print(f"Prompt length: {len(V6_PROMPT)} chars / ~{len(V6_PROMPT.split())} words")
    print(f"Welcome: {V6_WELCOME}")
    print(f"Responsiveness: 1.0")
    print()

    success = update_agent(V6_PROMPT, V6_WELCOME, 1.0)
    if success:
        print("SUCCESS — v6 prompt deployed to Jessica.")
        print(f"Test it now: call {os.environ.get('DEMO_LINE', '(615) 784-5747')}")
    else:
        print("FAILED — check API key and agent ID.")


def cmd_test():
    """Dry run — show what would be deployed."""
    print("=== DRY RUN — v6 Prompt ===")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Location ID: {GHL_LOCATION_ID}")
    print(f"Prompt length: {len(V6_PROMPT)} chars / ~{len(V6_PROMPT.split())} words")
    print(f"\n--- Welcome Message ---\n{V6_WELCOME}")
    print(f"\n--- System Prompt ---\n{V6_PROMPT}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: update-jessica-prompt.py <deploy|current|test>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "deploy":
        cmd_deploy()
    elif cmd == "current":
        cmd_current()
    elif cmd == "test":
        cmd_test()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
