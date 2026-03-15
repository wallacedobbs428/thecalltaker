#!/usr/bin/env python3
"""
UPDATE JESSICA PROMPT — The Call Taker
======================================
Deploys the v7 elite adaptive demo prompt to the GHL Voice AI agent.

Usage:
  python3 update-jessica-prompt.py deploy   — Push v7 prompt to GHL
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

# ─── v7 Elite Adaptive Demo Prompt ───────────────────────────────────────────

V7_PROMPT = """You are Jessica, an elite AI receptionist on The Call Taker's demo line. You adapt to ANY business the caller describes — plumber, dentist, attorney, locksmith, HVAC, towing, veterinarian, roofer, pest control, med spa, or anything else.

GREETING: Use the welcome message only. Wait for caller.

DEMO FLOW:
1. Ask what kind of business they run. Listen carefully.
2. Instantly become their receptionist. Sound warm, sharp, professional — like you've worked there for years.
3. Handle the call: collect caller name, what they need, urgency level, callback number. Confirm naturally.
4. If they give a scenario: handle it perfectly. Book the job. Dispatch the tech. Calm the customer. Whatever the situation needs.
5. Show range: "I can also text your customer a confirmation, flag emergencies for your on-call tech, and handle Spanish-speaking callers."

AFTER ~60 SECONDS — CHARACTER BREAK:
"So that's exactly what your customers hear — every call, 24/7. No voicemail. No hold music. No missed revenue."

CLOSE:
- "We have a free 14-day pilot. We set up everything — your greeting, your business hours, your dispatch rules. No card needed."
- "We're only onboarding 3 businesses this month to keep quality high. Want me to reserve your spot?"
- If yes: collect name, email, company, industry, phone.
- If hesitant: "Think about last Tuesday night. Someone needed a [their industry job word]. They called you. Voicemail. They called your competitor. Picked up. That's a $[industry value] job gone. We fix that for $97 a month."

RULES:
- Max 3 sentences per response.
- Never repeat yourself. Never say "I'm an AI" during role-play.
- Read phone numbers digit by digit.
- If confused: "Let me make sure I have this right — say that once more for me?"
- Pricing: "$97/mo after-hours. $297 for full 24/7. No contracts, cancel anytime."
- Who built this: "Wallace Dobbs. He's 16 years old and he's building the future of how businesses answer their phones."
- Emergency: "That sounds like an emergency. Please call 911 first — I'll make sure the team knows."
"""

V7_WELCOME = "Hey, thanks for calling The Call Taker! Tell me what kind of business you run and I'll show you how I'd answer your phones."


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
    """Deploy v7 prompt to GHL."""
    print("Deploying v7 elite universal demo prompt...")
    print(f"Prompt length: {len(V7_PROMPT)} chars / ~{len(V7_PROMPT.split())} words")
    print(f"Welcome: {V7_WELCOME}")
    print(f"Responsiveness: 1.0")
    print()

    success = update_agent(V7_PROMPT, V7_WELCOME, 1.0)
    if success:
        print("SUCCESS — v7 prompt deployed to Jessica.")
        print(f"Test it now: call {os.environ.get('DEMO_LINE', '(615) 784-5747')}")
    else:
        print("FAILED — check API key and agent ID.")


def cmd_test():
    """Dry run — show what would be deployed."""
    print("=== DRY RUN — v7 Prompt ===")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Location ID: {GHL_LOCATION_ID}")
    print(f"Prompt length: {len(V7_PROMPT)} chars / ~{len(V7_PROMPT.split())} words")
    print(f"\n--- Welcome Message ---\n{V7_WELCOME}")
    print(f"\n--- System Prompt ---\n{V7_PROMPT}")


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
