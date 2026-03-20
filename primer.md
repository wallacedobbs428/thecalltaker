## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-20 | Rewrite this file at the start of every session.

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

- **Branch:** `claude/work-session-continuation-DcuWo`
- **Base:** `master` (last commit 2026-03-19)
- **Latest commits (March 19):** Interior designer palette (warm bronze, cream, sage on charcoal), live ops dashboard with deadline countdown, 2050 aesthetic redesign (dot grid, grain texture, monospace data UI), timing polish, brightness + slide-up animation fixes, merged 8+ feature PRs
- **Working tree:** Clean (no staged or unstaged changes)

## Homepage Design (index.html)

- **Color scheme:** Interior designer palette — warm bronze, cream, sage on charcoal background
- **Layout:** Dark theme, glassmorphism header, scroll spy, GSAP mobile menu, Lenis smooth scroll
- **Hero:** Animated phone mockup (pure CSS/SVG, no images), circuit background, floating callouts
- **Sections:** Hero → Industry strip → How It Works → Features → Demo → Pricing → FAQ → Final CTA → Footer
- **Pricing:** 4-tier decoy ($19/$97/$497/$997), urgency badge with countdown to Friday deadline
- **Nav:** Glassmorphism header, scroll progress bar, mobile overlay menu
- **External deps:** GSAP 3.12.5 (cdnjs), Lenis 1.1.18 (jsdelivr)
- **Font:** Self-hosted Inter (woff2)
- **Recent design work:** 2050 aesthetic (dot grid, grain texture, monospace data UI), live ops dashboard section, slide-up entrance animations

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

1. **Urgency countdown hardcoded to March 21, 2026** — expires tomorrow, needs rolling logic
2. **premium.css is empty** — loaded on every page, zero CSS rules
3. **Schema.org prices don't match UI** — schema says $97-$997, UI has $19/$97/$497/$997
4. **index-v2.html orphaned** — duplicate sitting in root
5. **hero-phone-animation.html orphaned** — standalone test file in root
6. **41 HTML files in root** — cluttered, many could be organized into subdirectories
7. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
8. **CLAUDE.md documents 13 industries** — actual site has 19

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Website polish**: Fix urgency countdown, clean orphaned files, schema consistency
- **SEO content**: Continue expanding blog with high-intent keyword posts
- **Stripe**: NOT connected (Wallace is 16). PayPal workaround live via pay.html
