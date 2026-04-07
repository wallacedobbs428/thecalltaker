## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-04-07 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$497/$997/mo pricing (3-tier). 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles code, voice agent, GHL, integrations. William is OUT of the business as of Mar 21.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, video ads, sales assets, ad landing pages, tracking scripts
- **Ops repo** (`~/thecalltaker-ops/`): 15+ AI agents, 222+ launchd services, workflow engine, vector pipeline, signal processor — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (universal demo), character name GIDEON (NOT Jessica). Demo line: (615) 784-5747
- **CRM**: GoHighLevel (GHL). 6,595 contacts, 54 oracle-hot leads. API KEY CURRENTLY OFFLINE (switching payment)
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william) + Telegram bot
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/ads-diagnostics-48h-2Qi3V`
- **Working tree:** clean
- **Latest commit:** 18bbde2 (Apr 6) — Update primer.md with demo pitch page rebuild status
- **CRITICAL:** Never `git add -A` — video-ad/node_modules has 137MB files that get rejected by GitHub. Always add specific files.

## Ads Infrastructure (Audited Apr 7)

### Tracking IDs
- **Google Ads:** AW-17970510102
- **GA4:** G-29LL5GPBQV
- **Meta Pixel:** 2129562004253413
- **Signals Gateway:** tracking.thecalltaker.com (SDK ID: 3084877078917435530)

### Ad Landing Pages
- **go.html** — FB ad landing ($264 founding rate). Has Meta Pixel + Signals Gateway. MISSING Google Ads gtag.
- **demo/index.html** — Full pitch page (913 lines, rebuilt Apr 6). Has Google Ads + Meta Pixel + tct-tracking.js.
- **pay.html** — Pricing page (3 tiers). Has Google Ads + tct-tracking.js.
- **signup.html** — Stripe checkout. Has Meta Pixel + Signals Gateway + Google Ads. NO tct-tracking.js.
- **checkout.html** — Plan selector. Has tct-tracking.js only (via /shared/ path). MISSING direct Google Ads + Meta Pixel.
- **thank-you.html** — Conversion confirmation. Has Google Ads. MISSING Meta Pixel inline (relies on fbq function check).

### Critical Issues Found (Apr 7 Audit)
1. **tct-tracking.js Meta Pixel ID is PLACEHOLDER** — line 36: `fbq('init', 'XXXXXXXXXX')` — never replaced with real ID 2129562004253413
2. **go.html missing Google Ads gtag** — FB ad landing page can't track Google Ads conversions
3. **checkout.html missing Google Ads + Meta Pixel** — conversion funnel gap
4. **thank-you.html missing Meta Pixel** — Lead event fires but pixel may not be loaded
5. **No Purchase/Revenue events** — no gtag('event', 'purchase') anywhere in the funnel
6. **Dashboard data stale** — last updated 2026-03-14, nearly a month old

### Campaigns
- **Facebook Lead Ads:** $30/day CBO, 3 ad sets (HVAC/Plumbing/Dental), 9 ads total
- **Google Ads:** Planned $50-150/day, search campaigns, HVAC-focused
- **FB Lead Ads Engine:** ops/fb-lead-ads-engine.py — scans every 5min, 12-touch 5-day sequence

## Homepage (website/index.html)

- **Color scheme:** Green accent (#2a9d7a / #3ab894) on black (#080a08)
- **Hero:** GIDEON hologram vault + secondary hero with phone animation
- **3,360 lines** — production homepage

## Key Rules

- AI character name is **GIDEON** (never Jessica, never "the AI")
- No dashes in any outreach copy
- No "AI receptionist" in subject lines (confirmed dead approach)
- Never commit video-ad/node_modules/ or any file over 100MB
- Sign off as Wallace in all outreach
