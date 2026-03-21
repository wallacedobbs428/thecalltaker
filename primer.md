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

- **Branch:** `claude/worldwide-section-theme-toggle-uaHon`
- **Base:** `master` (last commit 2026-03-20)
- **Latest commit:** Added "Worldwide" section to homepage — SVG world map with highlighted countries, pulsing city dots, terminal stats, noise texture, scroll reveal. Placed between marquee and problem section.
- **Working tree:** Clean

## Homepage Design (index.html — ~1,543 lines)

- **Color scheme:** Warm dark palette — `--bg: #0c0b0a`, green accent (#1a7a5c), amber (#c27c3a)
- **Light mode:** Full CSS variable swap (html.light), toggle button fixed bottom-right, persists via localStorage
- **Layout:** Dark theme, glassmorphism header, scroll progress bar, GSAP phone animation
- **Hero:** Animated phone mockup (pure CSS/SVG, 5-state GSAP timeline), Jessica hologram section
- **Sections:** Hero → Jessica Hologram → Marquee → **Worldwide (NEW)** → Problem → Before/After → How It Works → Demo CTA → Testimonials → Pricing → FAQ → Final CTA → Footer
- **Worldwide section:** SVG world map, 12 highlighted countries, 8 pulsing city dots with tooltips, terminal stats (195+ / 24/7 / Any Language), noise texture overlay, "Jessica" quote + CTA
- **Pricing:** 4-tier decoy ($19/$97/$497/$997), urgency badge
- **Nav:** Glassmorphism header, scroll progress bar, mobile overlay menu
- **External deps:** GSAP 3.12.5 (cdnjs), Google Fonts (Inter, DM Serif Display, JetBrains Mono)
- **Existing scroll reveal system:** IntersectionObserver for `.reveal`, `.reveal-left`, `.reveal-right`, `.reveal-scale`, `.reveal-stagger` classes

## Website Stats

- **Total pages:** ~210+ HTML files deployed
- **Root HTML:** 41 pages
- **Industries:** 19 pages
- **Blog:** 69 posts
- **Case Studies:** 14 + index
- **SEO Pages:** 13 (ai-answering-service/)

## Known Issues (Current)

1. **Urgency countdown may be hardcoded** — check if still referencing a past date
2. **premium.css is empty** — loaded on every page, zero CSS rules
3. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
4. **CLAUDE.md documents 13 industries** — actual site has 19

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Website polish**: Worldwide section done, extend theme toggle to subpages
- **SEO content**: Continue expanding blog with high-intent keyword posts
