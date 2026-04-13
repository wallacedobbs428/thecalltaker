#!/usr/bin/env python3
"""
UPDATE JESSICA PROMPT — The Call Taker
======================================
Deploys the v9 anti-squeaky natural voice prompt to the GHL Voice AI agent.

Voice: Uses ElevenLabs "Rachel" (21m00Tcm4TlvDq8ikWAM) — the same class of voice
GoHighLevel uses for polished public demos (e.g. +1-888-732-4197). GHL does not
publish that line's internal voice UUID; Rachel matches the standard catalog
sound most agencies use to mirror it. Audition in Voice AI → Library → Rachel.

Usage:
  python3 update-jessica-prompt.py deploy              — Demo line agent (default IDs in file / env)
  python3 update-jessica-prompt.py deploy-to <locationId> <agentId>  — Any sub-account (e.g. American Surgical)
  python3 update-jessica-prompt.py deploy-surgical      — Same as deploy-to using TCT_SURGICAL_LOCATION_ID + TCT_SURGICAL_AGENT_ID
  python3 update-jessica-prompt.py current            — Show current prompt from GHL (demo agent)
  python3 update-jessica-prompt.py test                 — Dry run (print what would be sent)
  python3 update-jessica-prompt.py fallback <name>      — jessica_deep | rachel | bella | elli
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

# ─── Voice Settings — GHL-style (Rachel) ──────────────────────────────────────
# Matches GoHighLevel's public Voice AI demo tone (+1-888-732-4197 class of sound).
# Import by Voice ID in GHL if needed: Voice AI → Library → search Rachel, or paste ID.
GHL_STYLE_VOICE = {
    "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel — ElevenLabs; standard GHL-demo-adjacent female
    "responsiveness": 1.0,
    "voiceSettings": {
        "stability": 0.5,
        "similarityBoost": 0.75,
        "speakingRate": 1.0,
        "pitch": 0,
    },
}

# Previous default + alternates (CLI: fallback <name>)
FALLBACK_VOICES = {
    "jessica_deep": "lxYfHSkYm1EzQzGhdbfc",  # Warmer/deeper Jessica variant (v9 original)
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "elli": "MF3mGyEYCl7XYWbV9V6O",
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


def update_agent(prompt, welcome_message, voice_settings, agent_id=None, location_id=None, update_voice_id=True):
    """Update voice AI agent prompt, voice, and settings.

    GHL API (2021-04-15) expects **agentPrompt** (not prompt). ElevenLabs tuning
    (stability, pitch, etc.) is set in the GHL UI; PATCH rejects voiceSettings.

    If *update_voice_id* is True and the API returns invalid voice id (e.g. Rachel
    not yet imported under My Voices), retries with prompt+welcome only so the
    account keeps its current voice.

    Returns (success: bool, voice_changed: bool).
    """
    aid = agent_id or AGENT_ID
    lid = location_id or GHL_LOCATION_ID
    body = {
        "agentPrompt": prompt,
        "welcomeMessage": welcome_message,
        "responsiveness": voice_settings.get("responsiveness", 1.0),
    }
    if update_voice_id and voice_settings.get("voiceId"):
        body["voiceId"] = voice_settings["voiceId"]

    resp = requests.patch(
        f"{GHL_BASE_URL}/voice-ai/agents/{aid}",
        headers=HEADERS,
        params={"locationId": lid},
        json=body,
        timeout=30,
    )
    if resp.status_code == 400 and "voice id is invalid" in (resp.text or "").lower() and update_voice_id:
        print("Note: Target voice ID not registered on this GHL agency — deploying prompt + welcome only. In GHL: Voice AI → your agent → Voice → import ElevenLabs `21m00Tcm4TlvDq8ikWAM` (Rachel) or pick Rachel from Library, then re-run deploy.")
        ok, _ = update_agent(prompt, welcome_message, voice_settings, agent_id=aid, location_id=lid, update_voice_id=False)
        return (ok, False)
    if resp.status_code != 200:
        print(f"Error updating agent: {resp.status_code} — {resp.text[:200]}")
        return (False, False)
    return (True, bool(body.get("voiceId")))


def cmd_current():
    """Show current prompt."""
    agent = get_current_agent()
    if not agent:
        return
    data = agent.get("agent", agent)
    print("=== Current Voice AI Agent ===")
    print(f"Name: {data.get('agentName', data.get('name', 'N/A'))}")
    print(f"Responsiveness: {data.get('responsiveness', 'N/A')}")
    print(f"Voice ID: {data.get('voiceId', 'N/A')}")
    print(f"\n--- Welcome Message ---\n{data.get('welcomeMessage', 'N/A')}")
    print(f"\n--- System Prompt ---\n{data.get('agentPrompt', data.get('prompt', 'N/A'))}")


def cmd_deploy():
    """Deploy v9 prompt + GHL-style Rachel voice to the default demo Voice AI agent."""
    print("Deploying v9 prompt + GHL-style voice (Rachel / enterprise demo class)...")
    print(f"Prompt length: {len(V9_PROMPT)} chars / ~{len(V9_PROMPT.split())} words")
    print(f"Welcome: {V9_WELCOME}")
    print(f"Voice ID: {GHL_STYLE_VOICE['voiceId']} (Rachel — matches typical GHL public demo tone)")
    print(f"Pitch: 0 | Rate: 1.0 | Stability: 0.5 | Similarity: 0.75")
    print()

    success, voice_changed = update_agent(V9_PROMPT, V9_WELCOME, GHL_STYLE_VOICE)
    if success:
        if voice_changed:
            print("SUCCESS — v9 prompt + Rachel voice (21m00Tcm4TlvDq8ikWAM) applied to demo Voice AI agent.")
        else:
            print("SUCCESS — v9 prompt + welcome deployed. Voice unchanged (import Rachel in GHL or re-run after adding voice).")
        print(f"Test demo line: call {os.environ.get('DEMO_LINE', '(615) 784-5747')}")
        print()
        print("Prefer the deeper Jessica variant?  python3 update-jessica-prompt.py fallback jessica_deep")
        print("Other alternates:  fallback bella | fallback elli")
    else:
        print("FAILED — check API key and agent ID.")


def cmd_deploy_to(location_id, agent_id):
    """Deploy same prompt + GHL-style voice to another location (e.g. American Surgical)."""
    print(f"Deploying v9 + Rachel voice to location={location_id} agent={agent_id} ...")
    success, voice_changed = update_agent(V9_PROMPT, V9_WELCOME, GHL_STYLE_VOICE, agent_id=agent_id, location_id=location_id)
    if success:
        print("SUCCESS — Voice AI agent updated. Place a test call from GHL → Test Your Agent.")
    else:
        print("FAILED — check API key, location ID, and agent ID (must be Voice AI agent in that sub-account).")


def cmd_deploy_surgical():
    """Deploy using TCT_SURGICAL_LOCATION_ID + TCT_SURGICAL_AGENT_ID from environment."""
    lid = os.environ.get("TCT_SURGICAL_LOCATION_ID", "").strip()
    aid = os.environ.get("TCT_SURGICAL_AGENT_ID", "").strip()
    if not lid or not aid:
        print("Set both in your shell or .zprofile:")
        print("  export TCT_SURGICAL_LOCATION_ID='...'   # American Surgical sub-account")
        print("  export TCT_SURGICAL_AGENT_ID='...'       # Voice AI agent id from AI Agents → Voice AI")
        print("Or run:  python3 update-jessica-prompt.py deploy-to <locationId> <agentId>")
        sys.exit(1)
    cmd_deploy_to(lid, aid)


def cmd_fallback(voice_name):
    """Deploy with a fallback voice if Jessica deep still sounds squeaky."""
    voice_name = voice_name.lower()
    if voice_name not in FALLBACK_VOICES:
        print(f"Unknown fallback voice: {voice_name}")
        print(f"Available: {', '.join(FALLBACK_VOICES.keys())}")
        return

    voice_id = FALLBACK_VOICES[voice_name]
    settings = dict(GHL_STYLE_VOICE)
    settings["voiceId"] = voice_id
    print(f"Deploying v9 prompt with fallback voice: {voice_name} ({voice_id})...")

    success, _ = update_agent(V9_PROMPT, V9_WELCOME, settings)
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
    print(f"Voice ID: {GHL_STYLE_VOICE['voiceId']} (Rachel / GHL demo class)")
    print(f"Pitch: 0 | Rate: 1.0 | Stability: 0.5 | Similarity: 0.75")
    print(f"Prompt length: {len(V9_PROMPT)} chars / ~{len(V9_PROMPT.split())} words")
    print(f"\n--- Welcome Message ---\n{V9_WELCOME}")
    print(f"\n--- System Prompt ---\n{V9_PROMPT}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: update-jessica-prompt.py <deploy|deploy-to|deploy-surgical|current|test|fallback>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "deploy":
        cmd_deploy()
    elif cmd == "deploy-to":
        if len(sys.argv) < 4:
            print("Usage: update-jessica-prompt.py deploy-to <locationId> <agentId>")
            sys.exit(1)
        cmd_deploy_to(sys.argv[2], sys.argv[3])
    elif cmd == "deploy-surgical":
        cmd_deploy_surgical()
    elif cmd == "current":
        cmd_current()
    elif cmd == "test":
        cmd_test()
    elif cmd == "fallback":
        if len(sys.argv) < 3:
            print("Usage: update-jessica-prompt.py fallback <jessica_deep|rachel|bella|elli>")
            sys.exit(1)
        cmd_fallback(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
