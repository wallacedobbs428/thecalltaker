## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-21 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$497/$997/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles demos and closing alongside Wallace.

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (universal demo). Demo line: (615) 784-5747
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/dark-luxury-redesign-UPpU4`
- **Base:** `master` (last commit 2026-03-20)
- **Latest work (March 21):** DARK LUXURY TECH redesign — complete visual overhaul of index.html
- **Working tree:** Modified (index.html dark luxury redesign in progress)

## Homepage Design (index.html — ~1270 lines)

- **Design direction:** DARK LUXURY TECH — Bloomberg Terminal meets Apple.com
- **Color scheme:** #07090F deep navy-black bg, #00FF88 electric green accent (single accent color), white text
- **Fonts:** Barlow Condensed (bold condensed display for all headings), JetBrains Mono (terminal readouts), Inter (body)
- **Light mode:** REMOVED — dark only
- **Layout:** Asymmetric sections, diagonal cuts, offset overlapping cards, terminal-style stat readouts
- **Hero:** Split-screen with animated phone mockup (pure CSS/SVG), Barlow Condensed uppercase headings
- **Sections:** Hero → Jessica Hologram → Industry Marquee → Problem (terminal stats) → Before/After (offset overlap) → How It Works (stacked offset) → Demo CTA (split diagonal) → Testimonials (asymmetric cards) → Pricing (featured dominant) → FAQ (split layout) → Final CTA (diagonal cut) → Footer
- **Pricing:** 3-tier ($97/$497/$997), featured card sticky + dominant right column
- **Nav:** Glassmorphism header, scroll progress bar (green glow), mobile overlay menu
- **External deps:** GSAP 3.12.5 (cdnjs)
- **Noise texture:** SVG feTurbulence at 3% opacity, overlay blend mode — premium dark feel
- **Terminal readouts:** Monospace green-on-dark bordered boxes with blinking cursor, used throughout for data callouts

## Website Stats

- **Total pages:** ~210+ HTML files deployed
- **Root HTML:** 41 pages
- **Industries:** 19 pages
- **Blog:** 69 posts
- **Case Studies:** 14 + index
- **SEO Pages:** 13 (ai-answering-service/)

## Known Issues (Current)

1. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
2. **CLAUDE.md documents 13 industries** — actual site has 19
3. **Other pages (industries, blog, etc.)** still use old color scheme — need updating to match new dark luxury system

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Website polish**: Propagate dark luxury redesign to subpages
- **SEO content**: Continue expanding blog with high-intent keyword posts
