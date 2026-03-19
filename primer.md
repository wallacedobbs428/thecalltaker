## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-19 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $19/$97/$497/$997/mo plans (4-tier decoy pricing). 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder/partner, strategy + GitHub access).

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (universal demo). Demo line: (615) 784-5747
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/its-mills-dabnE` (Mills session)
- **Base:** `origin/main` at 81f7643 (March 19 — merged 10+ PRs including mobile centering, skill router, GHL reactivation, outreach rebuild, frontend quickstart, ads skill system)
- **Working tree:** Has new lead files (indeed-houston-2026-03-19.json + .md)
- **War room files:** `war-room/task-board.md` and `war-room/handoff-log.md` do NOT exist in this environment

## Recent Activity (March 19)

- PR #19 merged (review-skill-prs) — consolidated multiple feature branches into main
- Multiple merge commits resolving conflicts across: mobile centering, skill router, GHL reactivation workflow, outreach stack rebuild, frontend quickstart, ads skill system
- Master branch is behind origin/main (master at 2026-03-17, origin/main at 2026-03-19)
- **Indeed Houston lead gen completed:** 18 hiring-signal leads found across legal (8), vet (5), dental (4), HVAC (1), roofing (1). Files at `leads/indeed-houston-2026-03-19.json` and `.md`
- **Indeed Nashville lead gen completed earlier:** Files at `leads/indeed-nashville-2026-03-19.json` and `.md`
- **Indeed Phoenix lead gen completed:** 17 hiring-signal leads found across dental (5), HVAC/plumbing (5), veterinary (3), roofing (1), garage door (1), pest control (1), medical (1). Files at `leads/indeed-phoenix-2026-03-19.json` and `.md`

## Lead Generation Files

- `leads/indeed-phoenix-2026-03-19.json` — 17 scored leads, JSON format (8 hot, 9 warm)
- `leads/indeed-phoenix-2026-03-19.md` — Same leads with savings pitches, call priority order, market insights
- `leads/indeed-houston-2026-03-19.json` — 18 scored leads, JSON format
- `leads/indeed-houston-2026-03-19.md` — Same leads with call scripts, savings pitches, and market stats
- `leads/indeed-nashville-2026-03-19.json` — Nashville leads
- `leads/indeed-nashville-2026-03-19.md` — Nashville leads markdown

## Homepage Design (index.html)

- **Color scheme:** Green accent (#00dc82) — all CSS vars map to same green
- **Layout:** Dark theme, glassmorphism header, scroll spy, GSAP mobile menu, Lenis smooth scroll
- **Hero:** Animated phone mockup (pure CSS/SVG, no images), circuit background, floating callouts
- **Sections:** Hero -> Industry strip -> How It Works -> Features -> Demo -> Pricing -> FAQ -> Final CTA -> Footer
- **Pricing:** 4-tier decoy ($19/$97/$497/$997), urgency badge with countdown
- **External deps:** GSAP 3.12.5 (cdnjs), Lenis 1.1.18 (jsdelivr)
- **Font:** Self-hosted Inter (woff2)

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

1. **Urgency countdown hardcoded** — needs rolling logic (was set to March 21)
2. **premium.css is empty** — loaded on every page, zero CSS rules
3. **Schema.org prices don't match UI** — schema says $97-$997, UI has $19/$97/$497/$997
4. **index-v2.html orphaned** — 3,398-line duplicate sitting in root
5. **hero-phone-animation.html orphaned** — standalone test file in root
6. **41 HTML files in root** — cluttered, many could be organized
7. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live via pay.html
8. **CLAUDE.md documents 13 industries** — actual site has 19

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Lead gen**: Indeed hiring-signal scraping across metros (Nashville done, Houston done, Phoenix done). Next: Atlanta, Dallas, Memphis
- **Website polish**: Fix urgency countdown, clean orphaned files, schema consistency
- **SEO content**: Continue expanding blog with high-intent keyword posts
- **Stripe**: NOT connected (Wallace is 16). PayPal workaround live
