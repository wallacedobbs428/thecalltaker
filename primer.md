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

- **Branch:** `claude/setup-call-taker-system-I7JtH` (feature branch, not yet merged to main)
- **Last commits (Mar 30):** Site audit fixes, mobile layout fixes, demo number update (629→615), go.html/pay.html fixes
- **Working tree:** CLEAN — no staged or unstaged changes
- **CRITICAL:** Never `git add -A` — video-ad/node_modules has 137MB files that get rejected by GitHub. Always add specific files.

## Homepage (website/index.html)

- **Color scheme:** Green accent (#00dc82) on black (#0a0a0a)
- **Hero:** Holographic GIDEON with typewriter captions + animated phone mockup
- **GIDEON captions:** "Hey. I'm GIDEON." → "#1 AI answering service" → "answering every call" → "book, text, qualify" → "ready to make you rich" → "call our demo line"
- **Audio:** gideon-intro.mp3 + gideon-intro-short.mp3 (needs re-recording to match new captions)
- **Pricing:** 3-tier ($97/$497/$997), founding rate $264 on go.html
- **External deps:** GSAP 3.12.5 (cdnjs)
- **Font:** Inter (Google Fonts)

## Video Ad System (video-ad/)

- **Framework:** Remotion (React-based video generation)
- **Campaign:** "The $300 Ghost" — missed call pain point
- **Rendered output:** video-ad/out/ — 6 MP4 files (30s + 15s × 3 aspect ratios)
- **Launch protocol:** 72-HOUR-LAUNCH-PROTOCOL.md
- **DO NOT** commit video-ad/node_modules/

## Website Stats

- **Total pages:** ~220+ HTML files deployed
- **Recent work (Mar 30):** Site-wide demo number update to (615) 784-5747, mobile layout fixes (comparison, demo CTA, testimonials), site audit fixing 7 issues

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
- **New GIDEON audio**: Captions updated, audio file needs re-recording to match
