## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-04-06 | Rewrite this file at the start of every session.

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

- **Branch:** `claude/build-pitch-page-cRb2S`
- **Working tree:** clean after commit
- **Latest commit:** Rebuilt demo/index.html as full pitch page (913 lines, 12 sections)
- **CRITICAL:** Never `git add -A` — video-ad/node_modules has 137MB files that get rejected by GitHub. Always add specific files.

## Homepage (website/index.html)

- **Color scheme:** Green accent (#2a9d7a / #3ab894) on black (#080a08)
- **Hero:** GIDEON hologram vault + secondary hero with phone animation
- **Design system:** CSS vars (--bg, --surface, --accent, --t100/70/40/20/10/06), scroll reveal animations, feature cards, pricing cards, FAQ accordion
- **Pricing:** 3-tier ($97/$497/$997), founding rate $264 on go.html
- **External deps:** GSAP 3.12.5 (cdnjs for homepage only)
- **Font:** Inter (Google Fonts)
- **3,360 lines** — production homepage

## Demo Page (website/demo/index.html) — REBUILT Apr 6

- **913 lines** — full pitch page matching homepage design exactly
- **Sections (12):** Hero with demo console, stats row, problem (85% stat split), before/after comparison, 6 feature cards, 3-step how-it-works, demo CTA with live transcript, live counter bar, 3-tier pricing + cost comparison, 10-question FAQ, final CTA with guarantee, footer
- **Includes:** Meta Pixel, Google Ads tag, tct-tracking.js, shared/demo-console.css+js, tct-intent.js, tct-convert.js
- **Features:** Scroll reveal animations, FAQ accordion, nav scroll spy, theme toggle (light/dark), exit-intent popup, mobile call bar, industry-aware URL param (?industry=hvac)
- **Self-contained:** All CSS inline, no GSAP dependency (unlike homepage)

## Video Ad System (video-ad/)

- **Framework:** Remotion (React-based video generation)
- **Campaign:** "The $300 Ghost" — missed call pain point
- **Rendered output:** video-ad/out/ — 6 MP4 files ready to upload
- **DO NOT** commit video-ad/node_modules/ — contains 137MB Chrome binary

## Website Stats

- **Total pages:** ~220+ HTML files deployed
- **Key pages:** index.html (homepage), demo/index.html (pitch page), go.html (ad landing), pay.html (pricing), demo-live.html (ElevenLabs live demo)

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
- **Demo pitch page**: DONE — full rebuild pushed to claude/build-pitch-page-cRb2S
