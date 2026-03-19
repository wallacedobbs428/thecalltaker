## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-19 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $19/$97/$497/$997/mo plans (4-tier decoy pricing). 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles demos and closing alongside Wallace.

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (universal demo). Demo line: (615) 784-5747
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/merge-all-skills-IsTcc`
- **Base:** `master` (last commit 2026-03-17)
- **Latest work (March 19):** GHL API proxy deployment prep — added /health endpoint, switched to in-memory rate limiting, uncommented routes in wrangler.toml, updated DEPLOY.md
- **Working tree:** Changes pending commit (worker.js, wrangler.toml, DEPLOY.md updates)
- **Upstream:** Synced before this session

## GHL API Proxy (NEW — March 19)

Cloudflare Worker (`tct-ghl-proxy`) proxying browser → GHL API calls so the API key never touches the browser.

- **Files:** `cloudflare/worker.js`, `cloudflare/wrangler.toml`, `cloudflare/DEPLOY.md`, `website/shared/tct-ghl-proxy.js`
- **Status:** Code ready, NOT yet deployed to Cloudflare (Wallace needs to run `wrangler deploy`)
- **Key decisions:**
  - In-memory rate limiting (not KV) — avoids free tier 1,000 KV writes/day limit
  - Routes in wrangler.toml (not dashboard) — auto-bind on deploy
  - /health endpoint added — no auth required, confirms Worker is alive + secrets set
  - PROXY_SECRET in frontend JS is safe — origin-locked + rate-limited, not the real API key
  - `echo -n` required for `wrangler secret put` to avoid trailing newline corruption

## Homepage Design (index.html)

- **Color scheme:** Green accent (#00dc82) — all CSS vars (--blue, --orange, --green) map to same green
- **Layout:** Dark theme, glassmorphism header, scroll spy, GSAP mobile menu, Lenis smooth scroll
- **Hero:** Animated phone mockup (pure CSS/SVG, no images), circuit background, floating callouts
- **Sections:** Hero → Industry strip → How It Works → Features → Demo → Pricing → FAQ → Final CTA → Footer
- **Pricing:** 4-tier decoy ($19/$97/$497/$997), urgency badge with countdown
- **External deps:** GSAP 3.12.5 (cdnjs), Lenis 1.1.18 (jsdelivr)
- **Font:** Self-hosted Inter (woff2)

## Website Stats

- **Total pages:** ~210+ HTML files deployed
- **Root HTML:** 41 pages
- **Industries:** 19 pages (expanded beyond documented 13)
- **Blog:** 69 posts
- **Case Studies:** 14 + index
- **SEO Pages:** 13 (ai-answering-service/)

## Known Issues (Current)

1. **Urgency countdown hardcoded** — needs rolling logic
2. **premium.css is empty** — loaded on every page, zero CSS rules
3. **Schema.org prices don't match UI** — schema says $97-$997, UI has $19/$97/$497/$997
4. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
5. **GHL proxy not yet deployed** — code ready, needs `wrangler deploy` on Wallace's machine

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **GHL Proxy**: Deploy to Cloudflare (4 steps in DEPLOY.md)
- **Website polish**: Fix urgency countdown, clean orphaned files, schema consistency
- **Stripe**: NOT connected (Wallace is 16). PayPal workaround live via pay.html
