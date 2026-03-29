## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-29 | Rewrite this file at the start of every session.

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

- **Branch:** `main`
- **Working tree:** check with `git status`
- **CRITICAL:** Never `git add -A` — video-ad/node_modules has 137MB files that get rejected by GitHub. Always add specific files.

## Homepage (website/index.html)

- **Color scheme:** Green accent (#00dc82) on black (#0a0a0a)
- **Hero:** Holographic GIDEON with typewriter captions + animated phone mockup
- **GIDEON captions (updated Mar 28):** "Hey. I'm GIDEON." → "#1 AI answering service" → "answering every call" → "book, text, qualify" → "ready to make you rich" → "call our demo line"
- **Audio:** gideon-intro.mp3 + gideon-intro-short.mp3 (needs re-recording to match new captions)
- **Pricing:** 3-tier ($97/$497/$997), founding rate $264 on go.html
- **External deps:** GSAP 3.12.5 (cdnjs)
- **Font:** Inter (Google Fonts)

## Video Ad System (video-ad/)

- **Framework:** Remotion (React-based video generation)
- **Campaign:** "The $300 Ghost" — missed call pain point
- **Compositions:**
  - TheGhost30 (30s master) + TheGhost15 (15s cutdown)
  - 3 hook variants: Aggressive, Authority, Curiosity
  - 3 aspect ratios per composition: 9:16 Reel, 4:5 Feed, 1:1 Square
- **Rendered output:** video-ad/out/ — 6 MP4 files ready to upload
  - ghost-30s-reel.mp4, ghost-30s-feed.mp4, ghost-30s-square.mp4
  - ghost-15s-reel.mp4, ghost-15s-feed.mp4, ghost-15s-square.mp4
- **Scenes:** HookScene, PainScene, AnchorScene, ProofScene, CTAScene
- **Components:** AnimatedText, Background, EndCard, PhoneMockup
- **Launch protocol:** 72-HOUR-LAUNCH-PROTOCOL.md (FB Ads phased rollout)
- **Publish playbook:** PUBLISH-PLAYBOOK.md (upload order, captions, targeting)
- **DO NOT** commit video-ad/node_modules/ — contains 137MB Chrome binary + 109MB webpack cache

## Website Stats

- **Total pages:** ~220+ HTML files deployed
- **Key new pages (Mar 28-29, Mills):**
  - ai-answering-service-small-business.html (SEO landing)
  - ghl-answering-service.html (GHL integration page)
  - never-miss-a-call.html (pain-point landing)
  - vs-ruby-receptionists.html (Ruby comparison)
  - vs-smith-ai.html (Smith.ai comparison)
  - demo/carolina-locksmith.html (personalized demo)
  - we-use-it.html (self-use case study with live stats)

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
