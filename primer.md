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

- **Branch:** `claude/global-expansion-research-Vw8A6`
- **Base:** `master` (last commit 2026-03-19)
- **Latest work (March 20):** Global expansion intelligence report — researched 10 countries, ranked top 5 expansion markets (UK, Australia, Canada, Ireland, UAE), competitor landscape, voice AI maturity, local pricing
- **Working tree:** Clean after commit

## Homepage Design (index.html)

- **Color scheme:** Interior designer palette — warm bronze, cream, sage on charcoal
- **Layout:** Dark theme, glassmorphism header, scroll spy, GSAP mobile menu, Lenis smooth scroll
- **Hero:** Animated phone mockup (pure CSS/SVG, no images), circuit background, floating callouts
- **Sections:** Hero → Industry strip → How It Works → Features → Demo → Pricing → FAQ → Final CTA → Footer
- **Pricing:** 4-tier decoy ($19/$97/$497/$997), urgency badge with countdown
- **External deps:** GSAP 3.12.5 (cdnjs), Lenis 1.1.18 (jsdelivr)

## Website Stats

- **Total pages:** ~210+ HTML files deployed
- **Root HTML:** 41 pages
- **Industries:** 19 pages
- **Blog:** 69 posts
- **Case Studies:** 14 + index
- **SEO Pages:** 13 (ai-answering-service/)

## Global Expansion (NEW — March 20, 2026)

- **Report:** `docs/global-expansion-report.md` — full intelligence report
- **Top 5 markets:** UK (#1), Australia (#2), Canada (#3), Ireland (#4), UAE (#5)
- **Key insight:** All English-speaking markets deployable TODAY with zero infra change (same Retell agent)
- **Phase 1 (Now):** Extend lead scanner to UK + AU, same pitch with local currency
- **Phase 2 (Q3):** UK entity (£50), localized payment pages, UK Facebook ads
- **Phase 3 (Q4):** Ireland + Singapore via inbound + cold email
- **Blue oceans:** Ireland, Singapore, UAE, NZ — zero AI receptionist competition

## Known Issues (Current)

1. **Urgency countdown hardcoded** — needs rolling logic
2. **premium.css is empty** — loaded on every page, zero CSS rules
3. **Schema.org prices don't match UI** — schema says $97-$997, UI has $19/$97/$497/$997
4. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Global expansion**: UK + AU market entry research complete, ready for Phase 1 execution
- **Website polish**: Fix urgency countdown, clean orphaned files, schema consistency
- **SEO content**: Continue expanding blog with high-intent keyword posts
