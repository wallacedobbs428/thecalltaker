## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-18 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$297/$497/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Co-founder: Mills (strategy, GitHub). William (Wallace's brother) closes demos on Zoom.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/` or `/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets, outreach ops scripts
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo). Voice ID: `lxYfHSkYm1EzQzGhdbfc` (deep variant, v9)
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)

## Current Branch & Recent Work

- **Branch:** `claude/build-ads-skill-system-Y1JSa`
- **Latest session (March 18):** Built complete ads skill system — 6 slash commands replacing a full ad agency. Roofing campaign structured with 3 complete Facebook Lead Ads.

## Ad System (Built March 18, 2026)

### 6 Slash Command Skills (in `.claude/skills/`)

| Skill | What It Does |
|-------|-------------|
| `/ads-research` | Scrapes competitor ads from Facebook Ad Library by vertical |
| `/ads-scrape` | Deep-analyzes competitor ad creative: hooks, structure, CTAs |
| `/ads-brief` | Generates strategic brief: angles, targeting, compliance, testing framework |
| `/ads-write` | Writes 3 complete Facebook Lead Ads per vertical, Meta-compliant |
| `/ads-launch` | Builds Meta campaign via API — ALL PAUSED, requires explicit launch confirmation |
| `/ads-report` | Pulls live performance, compares against CPL benchmarks, recommends kill/scale/hold |

### Pipeline Flow
```
/ads-research → /ads-scrape → /ads-brief → /ads-write → /ads-launch → /ads-report
     ↓              ↓             ↓            ↓             ↓            ↓
  intelligence.json ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←← (feeds back)
```

### Roofing Campaign (Ready to Launch)

**10 competitors analyzed.** Top: AnswerConnect (365 days), Smith.ai (180 days), My AI Front Desk (150 days).

**3 Ads (ALL PAUSED):**
1. "Storm Season. Missed Calls. Lost Jobs." — storm urgency angle (zero competition)
2. "$97/Mo Beats Your $800 Receptionist" — price disruption angle
3. "That 2AM Call Was a $15,000 Roof Job" — emotional story angle

**Lead Form:** 5 questions → Thank You → Call Demo Line (615) 784-5747

**CPL Benchmarks:** Roofing $22 target / $44 kill. Testing at $5/day per ad ($15/day total).

### Ad System Files (in `~/thecalltaker-ops/ads/`)
- `research/roofing-competitors.json` — 10 competitors with angles + weaknesses
- `scrape/roofing-ad-analysis.json` — top 3 ad deconstructions
- `briefs/roofing-brief.md` — complete strategic brief
- `copy/roofing-ad-copy.md` — 3 complete ads ready to paste
- `active/roofing-campaign.json` — full campaign config + API commands
- `intelligence.json` — shared state across all 6 skills
- `reports/roofing-2026-03-18.json` — baseline report

### Ad System Scripts (in `~/thecalltaker-ops/ops/`)
- `meta-setup-wizard.py` — interactive wizard to set META_ACCESS_TOKEN + META_AD_ACCOUNT_ID
- `ads-health-check.py` — full system health check (credentials, skills, files, API)
- `ads-daily-report.py` — daily performance report with kill/scale logic + ntfy
- `com.thecalltaker.ads-daily-report.plist` — launchd template for 9AM daily report

### BLOCKER: Meta API Credentials
- META_ACCESS_TOKEN: NOT SET
- META_AD_ACCOUNT_ID: Known from config: `25895456013410801`
- FIX: `python3 ~/thecalltaker-ops/ops/meta-setup-wizard.py`
- Once set → run `/ads-launch roofing` to build campaign via API

## Outreach Stack v2 (Rebuilt March 15, 2026)

| # | Component | Script | What It Does |
|---|-----------|--------|-------------|
| C6 | Hot Lead 7-Touch | `hot-lead-converter.py` | 7-touch SMS/email/call sequence |
| C1 | Cold Caller v2 | `cold-caller-v2.py` | Bland.ai outbound calls |
| C2 | Storm Chaser v3 | `storm-chaser-v3.py` | NWS storm detection emails |
| C3 | Blast Engine v3 | `blast-engine-v3.py` | 40/day/address, A/B auto-promote |
| C4 | Lead Quality | `lead-quality-engine.py` | Dedup + quality score |
| C5 | Speed-to-Lead v2 | `speed-to-lead-v2.py` | 15s hot signal checks |
| C7 | DM Outreach v2 | `dm-outreach-v2.py` | 3-DM sequence per industry |
| NEW | Hot Lead 5-Step | `hot-lead-sequence.py` | 5-step follow-up (Day 0/1/2/4/7) |

## Active Priorities

1. **Meta Ads:** Set credentials → launch roofing campaign → get first ad leads
2. **Revenue:** Get to first paid customer. $20K MRR goal
3. **Outreach stack:** Deploy all 7 components to Mac
4. **Stripe:** NOT connected (Wallace is 16). PayPal/Venmo workaround live
5. **SEO content:** Continue expanding blog

## Known Blockers

1. Meta API credentials not set — run meta-setup-wizard.py
2. Stripe not connected — PayPal/Venmo workaround live
3. GHL API unreachable from CI — deploy from Mac only
4. Retell.ai blocked — needs payment card
5. Bland.ai balance — must be funded before cold caller goes live
