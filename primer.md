## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-30 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$497/$997/mo pricing (3-tier). 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles code, voice agent, GHL, integrations. William is OUT of the business as of Mar 21.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, video ads, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 15+ AI agents, 222+ launchd services, workflow engine, vector pipeline, signal processor — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (universal demo), character name GIDEON (NOT Jessica). Demo line: (615) 784-5747
- **CRM**: GoHighLevel (GHL). 6,595 contacts, 54 oracle-hot leads. API KEY CURRENTLY OFFLINE (switching payment)
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william) + Telegram bot
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/ntfy-call-list-notification-MeZjP`
- **Working tree:** clean
- **Last commit:** Added `ops/ntfy-call-list.py` — sends formatted call list to ntfy SALES topic
- **CRITICAL:** Never `git add -A` — video-ad/node_modules has 137MB files that get rejected by GitHub. Always add specific files.

## Homepage (website/index.html)

- **Color scheme:** Green accent (#00dc82) on black (#0a0a0a)
- **Hero:** Holographic GIDEON with typewriter captions + animated phone mockup
- **Pricing:** 3-tier ($97/$497/$997), founding rate $264 on go.html
- **External deps:** GSAP 3.12.5 (cdnjs)
- **Font:** Inter (Google Fonts)

## Ops Scripts (ops/)

- `ntfy-call-list.py` — NEW: reads closer-data.json, formats leads by score, sends to ntfy SALES. Run: `python3 ops/ntfy-call-list.py`
- `hot-lead-converter.py` — 7-touch follow-up sequence for hot leads
- `blast-engine-v2/v3.py` — cold email engines
- `speed-to-lead-v2.py` — monitors GHL for hot signals
- `system-health-monitor.py` — engine health checks
- `close-35-sequence.py` — closing sequence
- 34 total Python scripts in ops/

## Call List Data

- **Source:** `website/closer-data.json` — 5 leads with scores, scripts, voicemails
- **Top lead:** Greg, Carolina Locksmith, score 8/10 (replied + engaged demo)
- **Pipeline:** 32 in sequence, 23 texts sent, 0 replies, $0 MRR
- **Pay URL:** thecalltaker.com/pay
- **Demo line:** (629) 269-9697

## Key Rules

- AI character name is **GIDEON** (never Jessica, never "the AI")
- No dashes in any outreach copy
- No "AI receptionist" in subject lines (confirmed dead approach)
- All writes go to ~/thecalltaker-ops/ for scripts, ~/Desktop/thecalltaker/website/ for web pages
- Never commit video-ad/node_modules/ or any file over 100MB
- Sign off as Wallace in all outreach
- Update CLAUDE.md before every git commit

## Active Priorities

- **Revenue**: $0 MRR, 0 paying customers. Pipeline velocity $54.58/day
- **GHL API**: Offline (switching payment). When back: activate workflow engine, pre-call warmer, 15 micro-campaigns
- **Stripe**: Live account but secret key expired. Products not yet created
- **Video ads**: "The $300 Ghost" rendered and ready. Needs FB Ads upload per PUBLISH-PLAYBOOK.md
