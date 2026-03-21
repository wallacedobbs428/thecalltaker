## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-21 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$497/$997/mo plans (3-tier). 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder). William (demos/Zoom).

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (universal demo). Demo line: (615) 784-5747. AI name: **Jessica**
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/install-dependencies-SQKs7`
- **Base:** `master` (last commit 2026-03-20)
- **Latest commits (March 20):** Full website rebuild — hologram Jessica section, Jessica logo interstitial, new brand system (4-color), unique section layouts, scroll progress bar, light/dark mode toggle, sliding scroll animations
- **Working tree:** Clean (no staged or unstaged changes)

## Homepage Design (index.html — 1,270 lines)

### Color System
- `--bg: #0c0b0a` (near-black)
- `--accent: #1a7a5c` (muted green)
- `--accent-hover: #2a9d7a` (brighter green)
- `--amber: #c27c3a` (warm amber)
- `--green: #2a9d7a` (same as accent-hover)
- Text opacity scale: `--t100` through `--t06` (warm off-white rgba(237,232,225,x))
- Light mode: Full variable swap via `html.light` class

### Fonts
- DM Serif Display (headings) — Google Fonts
- Inter (body) — Google Fonts
- JetBrains Mono (labels/mono) — Google Fonts

### Page Structure (11 sections)
1. **Hero** — 2-column grid: copy left, animated phone right. 5-state GSAP animation (ring → connect → capture → book → text). Step counter synced to animation.
2. **Jessica Hologram** — 90vh spinning logo with orbit rings, scan lines, flicker effect, projection beam, data readouts. Uses `jessica-logo.png`.
3. **Industry Marquee** — scrolling ticker (13 industries, duplicated for seamless loop)
4. **The Problem** — split grid: giant 85% stat left, missed call cost right
5. **Before/After** — 2-column comparison (without vs with The Call Taker)
6. **How It Works** — 3-step horizontal timeline with connecting line
7. **Demo CTA** — full-bleed, massive phone number typography
8. **Testimonials** — 3 offset quotes (alternating left/right), not cards
9. **Pricing** — 3 tiers: After-Hours $97, Full 24/7 $497 (featured), Pro $997
10. **FAQ** — left title + right accordion (6 questions)
11. **Final CTA** — giant serif headline + dual buttons
12. **Footer** — 4-column grid (brand, product, resources, contact)

### Key Features
- Light/dark mode toggle (fixed bottom-right, localStorage persistence)
- Scroll progress bar (green gradient, fixed top)
- Scroll reveal animations (5 types: fade-up, slide-left, slide-right, scale, stagger)
- Phone animation: GSAP timeline with particles, typing effect, waveform, calendar
- Mobile call bar (fixed bottom, green background)
- FAQ accordion (single-open behavior)
- Deferred GA loading (scroll/click/mousemove/touchstart trigger)
- Film grain overlay (SVG noise, fixed, pointer-events:none)

### External Dependencies
- GSAP 3.12.5 (cdnjs)
- Google Fonts (DM Serif Display, Inter, JetBrains Mono)
- jessica-logo.png (local image)

### Architecture Notes
- Single file: ~826 lines CSS + ~320 lines HTML + ~125 lines JS
- All inline (no external CSS or JS files besides GSAP and fonts)
- 4 scattered `<style>` blocks for responsive overrides (between HTML sections)
- Heavy inline styles on sections 2-9

## Known Issues (Current)

1. **No tct-tracking.js** — attribution tracking script missing from homepage
2. **No lead capture form** — no popup, no email form, no inline form
3. **No hamburger menu** — mobile just hides nav links, no overlay menu (old version had GSAP mobile overlay)
4. **jessica-logo.png dependency** — breaks "zero external images" approach from earlier
5. **Scattered responsive styles** — 4 `<style>` blocks between sections instead of consolidated
6. **Inline style soup** — sections 2-9 use heavy inline styles, hard to maintain
7. **Schema.org reviewCount: 47** — may not match real review count
8. **Phone readout says "v2.1"** — version number in production UI is odd
9. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
10. **Pricing changed to 3-tier** — was 4-tier ($19/$97/$497/$997), now 3-tier ($97/$497/$997)

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Website polish**: Attribution tracking, lead capture, mobile nav
- **SEO content**: Continue expanding blog with high-intent keyword posts
- **Stripe**: NOT connected (Wallace is 16). PayPal workaround live via pay.html
