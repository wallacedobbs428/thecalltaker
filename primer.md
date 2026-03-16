## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-16 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$297/$497/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Co-founder: Mills (strategy, GitHub). William (Wallace's brother) closes demos on Zoom.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/` or `/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets, outreach ops scripts
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo). Voice ID: `lxYfHSkYm1EzQzGhdbfc` (deep variant, v9)
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)

## Outreach Stack v2 (Rebuilt March 15, 2026)

Full 7-component outreach system rebuild. All scripts in `ops/`.

| # | Component | Script | What It Does |
|---|-----------|--------|-------------|
| C6 | Hot Lead 7-Touch | `hot-lead-converter.py` | 7-touch SMS/email/call sequence. Bland.ai voicemail Day 1. Per-touch GHL tagging. |
| C1 | Cold Caller v2 | `cold-caller-v2.py` | Bland.ai outbound calls. Hot leads first. 2x retry with 4hr gaps. |
| C2 | Storm Chaser v3 | `storm-chaser-v3.py` | NWS API storm detection. Emails within 5 min of hail/tornado/wind. |
| C3 | Blast Engine v3 | `blast-engine-v3.py` | 40/day/address, 90s gaps, 5-address rotation, A/B auto-promote. |
| C4 | Lead Quality | `lead-quality-engine.py` | Dedup + quality score 1-10. Only 5+ leads pass to blast. |
| C5 | Speed-to-Lead v2 | `speed-to-lead-v2.py` | 15s hot signal checks. SMS 60s, call 5min, email 10min. Dead lead resurrection. |
| C7 | DM Outreach v2 | `dm-outreach-v2.py` | 3-DM sequence per industry. Copy-paste export for Wallace. |
| NEW | Hot Lead 5-Step | `hot-lead-sequence.py` | 5-step SMS/email/voicemail sequence (Day 0/1/2/4/7). Pain-first + scarcity. |
| Sys | Health Monitor | `system-health-monitor.py` | Green/yellow/red for all components. SMS alert on red. |
| Sys | Dashboard | `master-dashboard.html` | Visual command center. Auto-refreshes 60s. |

## Current Branch & Recent Work

- **Branch:** `claude/fix-mobile-centering-gn0lP`
- **Latest session (March 16):** Upgraded hero CTA on all 18 industry pages to dual mobile/desktop pattern. Mobile gets `tel:` link, desktop gets `/demo` link. CSS media query at 769px toggles visibility. Also: closer war room v2, mobile centering fixes, pay page updates from earlier commits.
- **Previous session (March 15):** Created `hot-lead-sequence.py`, added 10 SEO blog posts, homepage trust layer.

## Industry Page Hero CTA Upgrade (March 16, 2026)

All 18 industry pages in `website/industries/` (excluding index.html hub) now have:
- **Mobile CTA** (`hero-cta-mobile`): `tel:+16157845747` link — "Hear Jessica Answer Your Calls Now"
- **Desktop CTA** (`hero-cta-desktop`): `../demo` link — "Hear Jessica Answer Your Calls Now"
- **Sub-text**: "Live demo line — call now or try it online"
- **CSS**: `.hero-cta-desktop{display:none}` default, `@media(min-width:769px)` swaps visibility
- **Second CTA** (Try Demo section ~line 520) left untouched — still original phone number link

## Hot Lead Sequence (March 15, 2026)

New 5-step follow-up script at `ops/hot-lead-sequence.py`:
- Step 1 (Day 0): SMS pain hook + pilot offer
- Step 2 (Day 1): Email with missed call costs, competitor angle, case studies
- Step 3 (Day 2): Bland.ai voicemail drop
- Step 4 (Day 4): SMS social proof + scarcity countdown
- Step 5 (Day 7): Breakup email
- Commands: scan, send, status, run, test (dry run)
- State: `ops/hot-lead-sequence-state.json`
- Rate limits: 20 SMS/day, 30 emails/day
- Contact registry integration for cross-engine coordination
- 19 industries with pain hooks in INDUSTRY_HOOKS dict
- launchd templates in docstring (scan every 2hrs, send 3x daily)

## Homepage Trust Layer (March 15, 2026)

Added 4 trust elements to `website/index.html`:

1. **Trust Logo Bar** — Infinite-scroll bar with 6 logos. Positioned between hero and demo sections.
2. **Live Call Counter** — Fixed floating badge: "Jessica has answered X calls this month".
3. **Uptime Badge** — Pill badge in hero: "99.9% Uptime - 24/7/365 - Answers in Under 2 Rings".
4. **Response Time Claim** — Hero proof stat updated to "< 2 Rings Answer Speed".
5. **Live Demo Nav Link** — Added `/try-live.html` link to both desktop nav and mobile menu.

## Blog Posts (82+ pages total, 54+ blog posts)

All in `website/blog/`. Green/black design system. Inter font. Schema.org Article markup. OG/Twitter meta. Mid-article and bottom CTAs. Related posts section. Mobile responsive.

### New Posts Added (March 15, 2026) — Batch 1
- `answering-service-water-damage.html` — Water damage answering service
- `after-hours-answering-service-small-business.html` — After-hours answering for small business
- `how-many-calls-small-business-miss.html` — Missed call statistics
- `virtual-receptionist-cost-2026.html` — Virtual receptionist pricing guide
- `best-ai-phone-answering-service.html` — Best AI answering services ranked

### New Posts Added (March 15, 2026) — Batch 2
- `answering-service-pest-control.html` — Best pest control answering service (emergency routing, seasonal surges, termite/bed bug/rodent)
- `answering-service-auto-repair.html` — Auto repair shops losing $8K/mo in missed calls (hands-on work problem, Monday rush)
- `answering-service-cleaning-companies.html` — Best cleaning company answering service (residential/commercial, Airbnb turnovers, recurring revenue)
- `missed-calls-cost-contractors.html` — Data-driven missed call cost analysis by trade (roofing, plumbing, HVAC, electrical, GC, painting, landscaping, concrete)
- `ai-receptionist-vs-voicemail.html` — AI receptionist vs voicemail deep dive (80% hang-up stat, psychology, revenue math, comparison table)

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Outreach stack**: ALL 7 components rebuilt + new hot-lead-sequence — deploy to Mac
- **Stripe**: NOT connected (Wallace is 16). PayPal/Venmo workaround live
- **Bland.ai balance**: Cold caller + voicemails require funded account
- **GHL aliases**: Blast v3 needs 5 aliases verified (wallace@, hello@, support@, info@, team@)
- **Unsubscribe page**: Blast v3 links to thecalltaker.com/unsubscribe — needs building
- **SEO content**: Continue expanding blog with high-intent keyword posts

## Known Blockers

1. Stripe not connected — PayPal/Venmo workaround live
2. GHL API unreachable from CI — deploy from Mac only
3. Retell.ai blocked — needs payment card
4. Bland.ai balance — must be funded before cold caller goes live
5. 5 GHL email aliases need verification
6. Unsubscribe page needs to be built
