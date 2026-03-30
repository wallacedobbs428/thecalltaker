## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-30 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$497/$997/mo pricing (3-tier). Founding rate $264 on go.html. 14-day free pilot, no card required. Demo line: (615) 784-5747. Voice AI character: GIDEON. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills = co-founder (code/integrations). William is OUT as of Mar 21.

## Revenue Status

- **MRR: $0** — zero paying customers
- **Pipeline velocity:** $54.58/day
- **Active pilots:** 0
- **Hot leads:** 35 (no active follow-up sequence — sitting untouched per VECTOR_LOG)
- **Total GHL contacts:** 6,595+
- **Stripe:** Live account, secret key expired, products not created. BLOCKS ALL REVENUE. Wallace is 16 — needs parent/guardian.

## Architecture

- **This repo** (`~/thecalltaker/` or `~/Desktop/thecalltaker/`): Website ONLY (GitHub Pages), lead tools, dashboard, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny) + 40+ ops scripts + 105+ launchd services on a Mac
- **Voice AI**: GHL Voice AI (universal demo adapts to any industry). Agent ID: 695947c64b9ed67d8f1077ad. Character: GIDEON.
- **CRM**: GoHighLevel (GHL). **API KEY CURRENTLY OFFLINE** (switching payment) — all automated engines paused
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william) + Telegram bot
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`
- **6 AI daemons** in this repo: ATLAS (site auditor), VECTOR (marketing), FORGE (infra), BLUEPRINT (architecture), PRISM (design), ORACLE (market intel) — plist files at root, scripts are `*_daemon.sh`
- **167 skills** + **163 agents** installed (see SKILL-INVENTORY.md)

## Current Branch & State

- **Branch:** `claude/setup-call-taker-system-I7JtH`
- **Working tree:** CLEAN
- **Main branch:** 2 days behind this branch (last main commit Mar 28)
- **Recent work (Mar 30):** Demo number updated site-wide to (615) 784-5747, 3 mobile layout fixes, site audit fixing 7 issues, go.html/pay.html phone+dash fixes
- **CRITICAL:** Never `git add -A` — video-ad/node_modules has 137MB files. Always add specific files.

## Website Scale

- **924 HTML pages** in `website/` directory (deployed via GitHub Pages)
- **46 HTML pages** at repo root (NOT deployed — root files don't go to GitHub Pages)
- **Breakdown:**
  - 83 blog posts (`website/blog/`)
  - 19 industry pages (`website/industries/`)
  - 13 SEO landing pages (`website/ai-answering-service/`)
  - 650 local SEO directories (`website/ai-receptionist-*-*/`) — city+industry combos
  - 6 comparison pages (`website/vs/` + 2 at root)
  - Admin portal (`website/admin/`), Client area (`website/client/`), Onboarding (`website/onboarding/`)
  - Core pages: index, signup, calculator, book, checkout, demo-showcase, pay, go, pricing, portal, etc.
  - Agency program: agency, pitch-deck, pricing-sheet, setup-guide
  - Pilot pages, try-funnel, sales toolkit, case studies

## Homepage (website/index.html)

- **Color scheme:** Green accent (#00dc82) on black (#0a0a0a)
- **Hero:** Holographic GIDEON with typewriter captions + animated phone mockup
- **GIDEON captions:** "Hey. I'm GIDEON." → "#1 AI answering service" → "answering every call" → "book, text, qualify" → "ready to make you rich" → "call our demo line"
- **Audio:** gideon-intro.mp3 + gideon-intro-short.mp3 (needs re-recording to match new captions)
- **Cursor effects v3:** Crosshair + canvas particles (desktop only, GSAP-powered)
- **Premium nav:** Glassmorphism header, scroll spy, GSAP mobile menu
- **External deps:** GSAP 3.12.5 (cdnjs), Inter font (Google Fonts)

## Key Pages

- `website/go.html` — Ad landing page, founding rate $264/mo
- `website/pay.html` + root `pay.html` — Payment pages (duplicate exists at root)
- `website/demo-showcase.html` — Live demo showcase
- `website/try-live.html` — Live try page (has "35+ businesses" credibility risk — should be updated)
- `website/ghl-answering-service.html` — GHL integration page
- `website/never-miss-a-call.html` — Pain-point landing
- `website/vs-ruby-receptionists.html`, `website/vs-smith-ai.html` — Competitor comparisons
- `website/ai-answering-service-small-business.html` — SEO landing

## Active Blockers (Ranked)

1. **$0 MRR** — No paying customers. Everything should serve getting the first one.
2. **Stripe not connected** — Wallace is 16, needs parent/guardian. BLOCKS ALL REVENUE.
3. **GHL API offline** — Switching payment. All automated outreach engines paused.
4. **35 hot leads sitting untouched** — No active follow-up sequence deployed (per VECTOR_LOG).
5. **Meta Ads** — Ad account exists (25895456013410801), needs API token.
6. **Retell.ai blocked** — Needs payment card for phone number ($2/mo).
7. **Email 63% failure rate** — DNS/SMTP config issue (per SYSTEM_STATE.md).
8. **reply-monitor** — Exit code 1, may need restart.
9. **Root vs website/ file duplication** — Root files NOT deployed but some pages exist in both places.

## Outreach System (All Paused — GHL Offline)

- **4 AI engines:** Max (reply catcher), Ben (intelligence/scoring), Sam (customer success), Donny (conversion closer)
- **Acquisition pipeline:** Scraper (17 industries × 56 metros) → Scorer (0-100) → Router (URGENT/HIGH/MEDIUM/LOW) → Outreach queue → GHL
- **Master lead list:** 1,765+ leads in `leads/master-all-industries.json`
- **Cold outreach:** blast-engine (email A/B), cold-caller (Bland.ai), funnel-engine (7-touch), gmail-sender (4 accounts)
- **Hot lead sequence (WRITTEN but NOT deployed):** 6-touch, 17 industry variants in `outreach/hot-lead-sequence-v1.md`

## Video Ad System (video-ad/)

- **Framework:** Remotion (React-based video generation)
- **Campaign:** "The $300 Ghost" — missed call pain point
- **Rendered output:** 6 MP4 files in video-ad/out/ (30s + 15s × 3 aspect ratios)
- **Status:** READY — needs FB Ads upload per PUBLISH-PLAYBOOK.md and 72-HOUR-LAUNCH-PROTOCOL.md
- **DO NOT** commit video-ad/node_modules/

## Key Rules

- AI character name is **GIDEON** (never Jessica, never "the AI")
- No dashes in any outreach copy
- No "AI receptionist" in subject lines (confirmed dead approach)
- Website files go in `website/` (only that dir deploys). Scripts go in `~/thecalltaker-ops/`
- Never commit video-ad/node_modules/ or any file over 100MB
- Sign off as Wallace in all outreach
- Hero h1: NEVER set to `display: inline` (breaks "Receptionist" word)

## Immediate Priorities (Per VECTOR_LOG)

1. Deploy the hot lead sequence to GHL (35 leads sitting untouched)
2. Get Stripe connected (blocks all revenue)
3. Upload "The $300 Ghost" video ads to FB
4. Walk into 5 Nashville businesses with leave-behind (script in outreach/)
5. Fix "35+ businesses" claim on try-live.html (credibility risk)
6. Re-record GIDEON audio to match updated captions
