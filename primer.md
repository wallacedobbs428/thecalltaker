## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-21 | Rewrite this file at the start of every session.

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

- **Branch:** `claude/design-audit-overhaul-SU2Y4`
- **Base:** `master` (last commit 2026-03-17 on master)
- **Latest commits (March 20):** Hologram Jessica projection, logo interstitial, full website rebuild with 4-color brand system, sliding scroll animations, light/dark mode toggle, scroll progress bar
- **Working tree:** Clean (no staged or unstaged changes)

## Homepage Design (index.html)

- **Recent rebuild:** Complete website rebuild with all sections in 4-color brand system
- **Hero:** Phone animation swapped in as homepage, Jessica hologram projection
- **Logo:** Jessica headset line art on dark background, 3D rotating with orbit ring
- **Sections:** Hero → Industry strip → How It Works → Features → Demo → Pricing → FAQ → Final CTA → Footer
- **Pricing:** 4-tier decoy ($19/$97/$497/$997)
- **External deps:** GSAP 3.12.5 (cdnjs), Lenis (smooth scroll)

## Website Stats

- **Total pages:** ~210+ HTML files deployed
- **Root HTML:** 41 pages
- **Industries:** 19 pages
- **Blog:** 69 posts
- **Case Studies:** 14 + index
- **SEO Pages:** 13 (ai-answering-service/)
- **Pilot funnel:** 3 pages
- **Try funnel:** 3 pages

## Known Issues (Current)

1. **Urgency countdown hardcoded to March 21, 2026** — expires today, needs rolling logic
2. **premium.css is empty** — loaded on every page, zero CSS rules
3. **Schema.org prices don't match UI** — schema says $97-$997, UI has $19/$97/$497/$997
4. **index-v2.html orphaned** — duplicate sitting in root
5. **hero-phone-animation.html orphaned** — standalone test file in root
6. **41 HTML files in root** — cluttered
7. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
8. **CLAUDE.md documents 13 industries** — actual site has 19

## Active Priorities

- **Design Audit & Overhaul** — multi-prompt workflow in progress (Prompt 1: audit, Prompt 2: hologram fix, Prompt 3: full overhaul, Prompt 4: QA gate)
- **Revenue**: Get to first paid customer. $20K MRR goal
- **Website polish**: Fix urgency countdown, clean orphaned files, schema consistency
