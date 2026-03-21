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

- **Branch:** `claude/fix-hologram-avatar-tZi0q`
- **Base:** `master` (last commit 2026-03-20)
- **Latest commit (March 21):** Fixed hologram avatar — real 3D rotation (preserve-3d + perspective), circular crop, cyan/teal glow, scanlines, radial pulse, 8s Y-axis spin, 12s halo orbit ring, #050A12 background
- **Working tree:** Clean after push

## Homepage Design (index.html — ~1,270 lines)

- **Color scheme:** Dark theme, green accent (#1a7a5c) for most sections, cyan (#00ffff) for hologram section
- **Layout:** Glassmorphism header, scroll spy, GSAP mobile menu
- **Hero:** Animated phone mockup (pure CSS/SVG, no images) — shows Jessica answering a call with live transcript
- **Jessica Hologram Section:** 3D rotating circular avatar with:
  - `transform-style: preserve-3d` + `perspective: 1000px`
  - `border-radius: 50%` circular image crop
  - `holospinY` 8s Y-axis rotation
  - Radial gradient pulse (0.4s alternate), scanlines (2px gaps), cyan glow (box-shadow 30px/60px)
  - Halo ring orbiting at `rotateX(70deg)` on 12s cycle
  - Section background: `#050A12`
  - Projection beam + base pedestal + data readouts
- **Sections:** Hero → Hologram → Marquee → Before/After → Demo → Pricing → FAQ → CTA → Footer
- **Pricing:** 4-tier decoy ($19/$97/$497/$997)
- **External deps:** GSAP 3.12.5 (cdnjs)
- **Font:** Google Fonts — DM Serif Display, Inter, JetBrains Mono

## Website Stats

- **Total pages:** ~210+ HTML files deployed
- **Root HTML:** 41 pages
- **Industries:** 19 pages
- **Blog:** 69 posts
- **Case Studies:** 14 + index
- **SEO Pages:** 13 (ai-answering-service/)

## Known Issues (Current)

1. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
2. **premium.css is empty** — loaded on every page, zero CSS rules
3. **Schema.org prices don't match UI** — schema says $97-$997, UI has $19/$97/$497/$997

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Website polish**: Continue refining visual effects and UX
- **SEO content**: Continue expanding blog with high-intent keyword posts
