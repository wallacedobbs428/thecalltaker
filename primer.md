## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-21 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$497/$997/mo plans (3-tier). 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles demos and closing alongside Wallace. AI personality = "Jessica."

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (universal demo). Demo line: (615) 784-5747
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/analyze-design-audit-nXeVY`
- **Base:** `master` (last commit 2026-03-20)
- **Latest commits (March 20):** Major homepage rebuild — hologram Jessica section, 4-color brand system, scroll animations, light/dark toggle, scroll progress bar
- **Working tree:** Clean (no staged or unstaged changes)

## Homepage Design (index.html — 1,270 lines)

- **Color scheme:** Dark warm palette — `--bg: #0c0b0a`, `--accent: #1a7a5c` (green), `--amber: #c27c3a`
- **Fonts:** DM Serif Display (headings), Inter (body), JetBrains Mono (labels/monospace)
- **Layout:** Dark theme, glassmorphism nav, scroll progress bar, light/dark toggle, GSAP phone animation
- **Hero:** "It's 2 AM. Your phone rings. Jessica answers." + animated phone mockup showing 5-screen call flow (ring → connect → capture → book → notify)
- **Sections (9):** Hero → Jessica Hologram → Industry Marquee → Problem (85% stat) → Before/After → How It Works (3 steps) → Demo CTA (giant phone#) → Testimonials (3 quotes) → Pricing ($97/$497/$997) → FAQ (6 questions) → Final CTA → Footer
- **Pricing:** 3-tier: After-Hours $97, Full 24/7 $497 (featured), Pro $997
- **External deps:** GSAP 3.12.5 (cdnjs), Google Fonts (DM Serif Display, Inter, JetBrains Mono)
- **Jessica Hologram:** Spinning logo with scan lines, orbit rings, projection beam, floating data readouts
- **Phone animation:** 5-state GSAP timeline (~30s loop): incoming ring → connected/waveform → detail capture (typewriter) → calendar booking → text notification + $350 saved
- **Reveal animations:** 5 types (up, left, right, scale, stagger) via IntersectionObserver
- **Light mode:** Full CSS variable swap, toggle button bottom-right, localStorage persistence
- **Mobile:** Responsive grid collapses, mobile call bar fixed bottom, nav links hidden except CTA
- **GA:** Deferred load (G-29LL5GPBQV + AW-17970510102)

## Known Issues (Current)

1. **Schema.org prices don't match UI** — schema says $97-$997, UI shows $97/$497/$997 (no $19 tier anymore, but lowPrice correct)
2. **jessica-logo.png dependency** — hologram section requires this image file
3. **Inline styles heavy** — sections 2-9 use extensive inline styles rather than CSS classes
4. **No tct-tracking.js** — attribution tracking script not loaded on homepage
5. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
6. **CLAUDE.md documents 13 industries** — actual site has more

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Design audit**: Analyze current homepage for quality, conversion, and UX issues
- **Website polish**: Clean up inline styles, fix schema consistency
- **SEO content**: Continue expanding blog with high-intent keyword posts
