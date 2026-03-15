#!/usr/bin/env python3
"""
UPDATE JESSICA PROMPT — The Call Taker
======================================
Deploys the v9 anti-squeaky natural voice prompt to the GHL Voice AI agent.

Usage:
  python3 update-jessica-prompt.py deploy   — Push v9 prompt + voice settings to GHL
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

# ─── v9 Anti-Squeaky Natural Voice Prompt ─────────────────────────────────────
# TTS rules: no exclamation points, no ALL CAPS, no $ signs, numbers spelled out,
# short sentences, commas/dashes for rhythm, contractions written out for low pitch

V9_PROMPT = """You are Jessica, a calm, warm AI receptionist on The Call Taker demo line. You adapt to any business — plumber, dentist, lawyer, locksmith, HVAC, towing, vet, roofer, anything.

GREETING: Use the welcome message, then wait.

DEMO FLOW:
1. Ask what they do. Keep it easy — "So what kind of business do you run?"
2. Once they tell you, you are their receptionist. Warm, steady, like you have worked there for years.
3. Handle the call. Get their name, what is going on, how urgent, and best callback number. Confirm it back.
4. If they throw a scenario at you — handle it. Book it, dispatch it, calm the caller down.
5. Drop this in naturally — "I can also text your customer a confirmation, flag emergencies for your on-call tech, and handle Spanish-speaking callers."

AFTER ABOUT 60 SECONDS — BREAK CHARACTER:
"So that is exactly what your customers hear. Every call, 24/7. No voicemail, no hold music, no missed jobs."

CLOSE:
- "We have a free 14-day pilot. We set up your greeting, your hours, your dispatch rules — everything. No card needed."
- "We are only taking on three businesses this month so we can really dial it in. Want me to grab you a spot?"
- If yes — "I just need your name, email, company name, industry, and best phone number."
- If on the fence — "Think about last Tuesday night. Someone needed a job done. They called you, got voicemail, called the next guy instead. That is a three hundred to five hundred dollar job — gone. We fix that for ninety-seven dollars a month."

RULES:
- Two to three sentences max per response. Short and calm.
- Never repeat yourself. Never say you are an AI while in character.
- Read phone numbers one digit at a time.
- If you did not catch something — "Sorry, say that one more time for me."
- Pricing — "Ninety-seven a month for after-hours. Two ninety-seven for full 24/7. No contracts, cancel whenever."
- Who built this — "A kid named Wallace Dobbs. He is sixteen and he is building the future of how businesses answer phones."
- Emergency — "That sounds serious. Please call 911 first, and I will make sure the team knows right away."
"""

V9_WELCOME = "Thanks for calling The Call Taker — this is Jessica. Tell me what kind of business you run, and I will show you how I handle your calls."

# ─── Voice Settings ───────────────────────────────────────────────────────────
# Deep, warm female voice — eliminates squeaky/tinny sound
V9_VOICE_SETTINGS = {
    "voiceId": "lxYfHSkYm1EzQzGhdbfc",  # Jessica deep variant (ElevenLabs)
    "responsiveness": 1.0,
    # ElevenLabs-specific settings (if supported by GHL API)
    "voiceSettings": {
        "stability": 0.75,
        "similarityBoost": 0.85,
        "speakingRate": 0.95,
        "pitch": -1,
    },
}

# Fallback voices if Jessica deep still sounds squeaky
FALLBACK_VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",    # Most natural female ElevenLabs voice
    "bella": "EXAVITQu4vr4xnSDxMaL",      # Young, warm, extremely natural
    "elli": "MF3mGyEYCl7XYWbV9V6O",       # Calm, smooth, professional
}


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


def update_agent(prompt, welcome_message, voice_settings):
    """Update voice AI agent prompt, voice, and settings."""
    body = {
        "prompt": prompt,
        "welcomeMessage": welcome_message,
        "responsiveness": voice_settings.get("responsiveness", 1.0),
        "voiceId": voice_settings.get("voiceId"),
    }
    # Include voice tuning settings if GHL supports them
    if "voiceSettings" in voice_settings:
        body["voiceSettings"] = voice_settings["voiceSettings"]

    resp = requests.patch(
        f"{GHL_BASE_URL}/voice-ai/agents/{AGENT_ID}",
        headers=HEADERS,
        params={"locationId": GHL_LOCATION_ID},
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
    """Deploy v9 prompt + voice settings to GHL."""
    print("Deploying v9 anti-squeaky natural voice prompt...")
    print(f"Prompt length: {len(V9_PROMPT)} chars / ~{len(V9_PROMPT.split())} words")
    print(f"Welcome: {V9_WELCOME}")
    print(f"Voice ID: {V9_VOICE_SETTINGS['voiceId']} (Jessica deep variant)")
    print(f"Pitch: -1 | Rate: 0.95 | Stability: 0.75 | Similarity: 0.85")
    print()

    success = update_agent(V9_PROMPT, V9_WELCOME, V9_VOICE_SETTINGS)
    if success:
        print("SUCCESS — v9 prompt + voice settings deployed to Jessica.")
        print(f"Test it now: call {os.environ.get('DEMO_LINE', '(615) 784-5747')}")
        print()
        print("If still squeaky after testing:")
        print("  1. Try Rachel voice: python3 update-jessica-prompt.py fallback rachel")
        print("  2. Try Bella voice:  python3 update-jessica-prompt.py fallback bella")
    else:
        print("FAILED — check API key and agent ID.")


def cmd_fallback(voice_name):
    """Deploy with a fallback voice if Jessica deep still sounds squeaky."""
    voice_name = voice_name.lower()
    if voice_name not in FALLBACK_VOICES:
        print(f"Unknown fallback voice: {voice_name}")
        print(f"Available: {', '.join(FALLBACK_VOICES.keys())}")
        return

    voice_id = FALLBACK_VOICES[voice_name]
    settings = dict(V9_VOICE_SETTINGS)
    settings["voiceId"] = voice_id
    print(f"Deploying v9 prompt with fallback voice: {voice_name} ({voice_id})...")

    success = update_agent(V9_PROMPT, V9_WELCOME, settings)
    if success:
        print(f"SUCCESS — v9 prompt deployed with {voice_name} voice.")
        print(f"Test it now: call {os.environ.get('DEMO_LINE', '(615) 784-5747')}")
    else:
        print("FAILED — check API key and agent ID.")


def cmd_test():
    """Dry run — show what would be deployed."""
    print("=== DRY RUN — v9 Anti-Squeaky Prompt ===")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Location ID: {GHL_LOCATION_ID}")
    print(f"Voice ID: {V9_VOICE_SETTINGS['voiceId']} (Jessica deep)")
    print(f"Pitch: -1 | Rate: 0.95 | Stability: 0.75 | Similarity: 0.85")
    print(f"Prompt length: {len(V9_PROMPT)} chars / ~{len(V9_PROMPT.split())} words")
    print(f"\n--- Welcome Message ---\n{V9_WELCOME}")
    print(f"\n--- System Prompt ---\n{V9_PROMPT}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: update-jessica-prompt.py <deploy|current|test|fallback [voice]>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "deploy":
        cmd_deploy()
    elif cmd == "current":
        cmd_current()
    elif cmd == "test":
        cmd_test()
    elif cmd == "fallback":
        if len(sys.argv) < 3:
            print("Usage: update-jessica-prompt.py fallback <rachel|bella|elli>")
            sys.exit(1)
        cmd_fallback(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
