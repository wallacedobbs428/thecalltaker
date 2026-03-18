## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-18 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$497/$997/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder). Co-founder: Mills (strategy, GitHub). William (Wallace's brother) closes demos on Zoom.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/` or `/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets, outreach ops scripts
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo). Voice ID: `lxYfHSkYm1EzQzGhdbfc`
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)

## Session Memory System (March 18, 2026)

Two-file memory architecture — zero overlap:
- **`~/.claude/CLAUDE.md` (Global):** Wallace's identity, operating format (3 windows), non-negotiable standards, tech stack, installed skills, coordination protocol. Loads on EVERY session regardless of project.
- **`CLAUDE.md` (Project):** Product/pricing, architecture, all 4 engines, 40+ ops scripts, APIs, ntfy topics, GHL notes, Voice AI, website pages (128+), pilot program, acquisition engine v4, demo line monitor, state files, contact registry, known issues.

## Outreach Stack v2 (Rebuilt March 15, 2026)

Full 7-component outreach system. All scripts in `ops/`:

| # | Component | Script |
|---|-----------|--------|
| C1 | Cold Caller v2 | `cold-caller-v2.py` |
| C2 | Storm Chaser v3 | `storm-chaser-v3.py` |
| C3 | Blast Engine v3 | `blast-engine-v3.py` |
| C4 | Lead Quality | `lead-quality-engine.py` |
| C5 | Speed-to-Lead v2 | `speed-to-lead-v2.py` |
| C6 | Hot Lead 7-Touch | `hot-lead-converter.py` |
| C7 | DM Outreach v2 | `dm-outreach-v2.py` |
| NEW | Hot Lead 5-Step | `hot-lead-sequence.py` |
| Sys | Health Monitor | `system-health-monitor.py` |
| Sys | Dashboard | `master-dashboard.html` |

## Recent Work (March 17-18, 2026)

- **Loom video showcase page** for escalation sequence
- **Dynamic Google Ads conversion values** + reassurance button copy
- **Urgency bar:** 7 spots counter + Friday deadline + auto-waitlist
- **PayPal mobile redirect fix** + onboarding SMS sequence
- **PayPal abandonment fix:** card trust lines + fat buttons + thank-you page
- **Founding customer pricing page:** 4-tier decoy layout + payment workflow
- **FB Lead Ad thank-you page** with tap-to-call CTA
- **Homepage section rewrites** + Jessica demo worker
- **Demo-showcase.html** — fixed old orange design
- **Pricing sweep:** $97 After-Hours / $497 Starter / $997 Pro across full site

## Homepage Trust Layer (March 15, 2026)

Added: infinite-scroll trust logo bar, live call counter badge, uptime badge, response time claim, live demo nav link.

## Blog Posts (54+ articles)

All in `website/blog/`. Green/black design system. Inter font. Schema.org Article markup.

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Outreach stack**: ALL 7 components rebuilt + hot-lead-sequence — deploy to Mac
- **Stripe**: NOT connected (Wallace is 16). PayPal bridge live
- **Bland.ai balance**: Cold caller + voicemails require funded account
- **SEO content**: Continue expanding blog

## Known Blockers

1. Stripe not connected — PayPal bridge workaround live
2. GHL API unreachable from CI — deploy from Mac only
3. Retell.ai blocked — needs payment card
4. Bland.ai balance — must be funded before cold caller goes live
