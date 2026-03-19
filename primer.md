## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-19 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$297/$497/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles demos and closing alongside Wallace.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/` or `/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets, outreach ops scripts
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo). Voice ID: `lxYfHSkYm1EzQzGhdbfc` (deep variant, v9)
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)

## Current Branch & Recent Work

- **Branch:** `claude/skill-router-setup-AATlZ`
- **Latest session (March 19):** Added Skill Router to CLAUDE.md — auto-trigger table mapping conversational triggers to all 12 skills (ads pipeline, GHL, UI/UX, LightRAG, session hooks, config, Claude API, simplify, loop). Router rules: sequential ad pipeline, skill chaining, proactive invocation.
- **Previous sessions (March 18):** Warm palette redesign for phone animation, hero phone animation prototype, premium motion system (Lenis + scroll reveals), HUD design, floating callouts, iOS-safe circuit bg, Friday urgency bar.

## Skills System (12 Skills Available)

All skills live in `.claude/skills/` (local) and `/home/claude/.claude/skills/` (global). The Skill Router in CLAUDE.md auto-detects when to invoke them.

| Skill | Slash Command | Purpose |
|-------|--------------|---------|
| Ad Research | `/ads-research` | Competitor ad intelligence from Facebook Ad Library |
| Ad Scrape | `/ads-scrape` | Deep creative analysis of competitor ads |
| Ad Brief | `/ads-brief` | Creative strategy + targeting + compliance brief |
| Ad Write | `/ads-write` | Write 3 complete Facebook Lead Ad sets |
| Ad Launch | `/ads-launch` | Build Meta campaigns (ALL PAUSED by default) |
| Ad Report | `/ads-report` | Live metrics + kill/scale/hold decisions |
| GHL Automation | `/ghl-automation` | Full GoHighLevel CRM API operations |
| UI/UX Pro Max | `/ui-ux-pro-max` | Agency-tier frontend with design system |
| LightRAG | `/lightrag` | Knowledge graph build + query |
| Session Start Hook | `/session-start-hook` | Startup hooks for Claude Code web |
| Update Config | `/update-config` | Settings, permissions, hooks, env vars |
| Claude API | `/claude-api` | Anthropic SDK / Agent SDK usage |
| Simplify | `/simplify` | Code quality review + cleanup |
| Loop | `/loop` | Recurring task runner on interval |

## Outreach Stack v2 (Rebuilt March 15, 2026)

Full 7-component outreach system rebuild. All scripts in `ops/`.

| # | Component | Script | What It Does |
|---|-----------|--------|-------------|
| C6 | Hot Lead 7-Touch | `hot-lead-converter.py` | 7-touch SMS/email/call sequence |
| C1 | Cold Caller v2 | `cold-caller-v2.py` | Bland.ai outbound calls |
| C2 | Storm Chaser v3 | `storm-chaser-v3.py` | NWS API storm detection emails |
| C3 | Blast Engine v3 | `blast-engine-v3.py` | 40/day/address, 5-address rotation |
| C4 | Lead Quality | `lead-quality-engine.py` | Dedup + quality score 1-10 |
| C5 | Speed-to-Lead v2 | `speed-to-lead-v2.py` | 15s hot signal checks |
| C7 | DM Outreach v2 | `dm-outreach-v2.py` | 3-DM sequence per industry |
| NEW | Hot Lead 5-Step | `hot-lead-sequence.py` | 5-step SMS/email/voicemail (Day 0-7) |

## Website Pages (128+ Live)

Deployed via GitHub Pages. Only `website/` directory gets deployed.

- Core: index.html, signup.html, calculator.html, book.html, checkout.html, demo-showcase.html, etc.
- 13 industry pages in `website/industries/`
- 54+ blog posts in `website/blog/`
- 13 SEO landing pages in `website/ai-answering-service/`
- 13 case studies in `website/case-studies/`
- Try funnel, agency program, toolkit, demo share pages

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Outreach stack**: ALL 7 components rebuilt + hot-lead-sequence — deploy to Mac
- **Stripe**: NOT connected (Wallace is 16). PayPal/Venmo workaround live
- **SEO content**: Continue expanding blog with high-intent keyword posts
- **Skill system**: Router deployed — all 12 skills auto-trigger on context

## Known Blockers

1. Stripe not connected — PayPal/Venmo workaround live
2. GHL API unreachable from CI — deploy from Mac only
3. Retell.ai blocked — needs payment card
4. Bland.ai balance — must be funded before cold caller goes live
5. 5 GHL email aliases need verification
6. Unsubscribe page needs to be built
