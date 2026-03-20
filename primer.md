## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-20 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$297/$497/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles demos and closing alongside Wallace.

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (universal demo). Demo line: (615) 784-5747
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/work-session-continuation-DcuWo`
- **Base:** `master` (last commit 2026-03-19)
- **Latest work (March 20):** Evergreen countdown timer (rolling weekly), hero live ticker, pricing fixed ($97/$297/$497), Schema.org updated, urgency badge with pulsing dot + spots counter, memory system set up
- **Working tree:** Changes pending commit

## Homepage Design (index.html)

- **Color scheme:** Dark theme with green accent (`#00dc82`) on near-black background
- **Layout:** Glassmorphism header, scroll spy, GSAP mobile menu, Lenis smooth scroll
- **Hero:** Animated phone mockup (pure CSS/SVG, no images), circuit background, floating callouts, live ticker cycling through real activity messages
- **Sections:** Hero → Industry strip → How It Works → Features → Demo → Pricing → FAQ → Final CTA → Footer
- **Pricing:** 3-tier ($97/$297/$497), evergreen countdown to end of week, pilot spots counter (3→2→1), "Most Popular" badge on $297
- **Urgency:** Red pulsing dot + countdown timer + spots remaining — resets every Sunday automatically
- **Nav:** Glassmorphism header, scroll progress bar, mobile overlay menu
- **External deps:** GSAP 3.12.5 (cdnjs), Lenis 1.1.18 (jsdelivr)
- **Font:** Self-hosted Inter (woff2)

## Website Stats

- **Total pages:** ~210+ HTML files deployed
- **Root HTML:** 41 pages
- **Industries:** 19 pages (expanded beyond documented 13)
- **Blog:** 69 posts
- **Case Studies:** 14 + index
- **SEO Pages:** 13 (ai-answering-service/)
- **Pilot funnel:** 3 pages
- **Try funnel:** 3 pages

## Known Issues (Current)

1. **premium.css is empty** — loaded on every page, zero CSS rules
2. **index-v2.html orphaned** — duplicate sitting in root
3. **hero-phone-animation.html orphaned** — standalone test file in root
4. **41 HTML files in root** — cluttered, many could be organized into subdirectories
5. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
6. **CLAUDE.md documents 13 industries** — actual site has 19

## Resolved This Session

1. **Urgency countdown** — was hardcoded to March 21. Now evergreen, resets every Sunday midnight
2. **Full 24/7 price** — was $497 (same as Premium). Fixed to $297
3. **Schema.org** — was missing free pilot offer. Added $0 pilot offer to schema
4. **Hero badge** — was static. Now cycles through live activity messages every 4s with animated transitions

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Website polish**: Clean orphaned files, schema consistency
- **SEO content**: Continue expanding blog with high-intent keyword posts
- **Stripe**: NOT connected (Wallace is 16). PayPal workaround live via pay.html
