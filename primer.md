## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-19 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$297/$497/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles demos and closing alongside Wallace.

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets, outreach ops scripts
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo). Voice ID: `lxYfHSkYm1EzQzGhdbfc`
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)

## Current Session — March 19, 2026

- **Branch:** `claude/create-skill-router-Q74Id`
- **Task:** Create a CLAUDE.md skill router in home directory
- **Status:** Created `/home/user/CLAUDE.md` with routing table for 14 available skills
- **Issue:** User says they added ~32 skills via `skills.sh` from Mac but only 10 SKILL.md files exist on this system. The Mac-local skills didn't sync to the cloud environment.

## Skills Available (14 total)

### Project Skills (9) — in `.claude/skills/`
ads-research, ads-scrape, ads-brief, ads-write, ads-launch, ads-report, ghl-automation, ui-ux-pro-max, lightrag

### System Skills (5) — built-in
update-config, simplify, loop, claude-api, session-start-hook

## Recent Git History

- 33b3fdf (Mar 18): Redesign warm palette + slow-mo phone animation
- c032bbc (Mar 18): Hero phone animation prototype
- 82cc4e9 (Mar 18): Lenis smooth scroll + scroll-triggered reveals
- 2932514: Added ads skill system (6 slash commands)
- b6c7461: Founding customer pricing page + 4-tier layout

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Skill Router**: Complete CLAUDE.md with all skills properly routed
- **Outreach stack**: 7 components rebuilt — deploy to Mac
- **Stripe**: NOT connected (Wallace is 16). PayPal/Venmo workaround live
- **SEO content**: Continue expanding blog with high-intent keyword posts

## Known Blockers

1. Stripe not connected — PayPal/Venmo workaround live
2. GHL API unreachable from CI — deploy from Mac only
3. Retell.ai blocked — needs payment card
4. Bland.ai balance — must be funded before cold caller goes live
5. Additional skills from Mac not synced to cloud environment
