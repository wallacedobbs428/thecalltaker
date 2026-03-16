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

## Outreach Stack v2 (Rebuilt March 15-16, 2026)

Full 7-component outreach system rebuild + 3 new engines. All scripts in `ops/`.

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
| NEW | GHL Reactivation | `ghl-reactivation-workflow.py` | 5-message "Founding 10" reactivation targeting 35 hot leads. Reply detection, industry personalization. |
| NEW | FB Lead Ads v2 | `fb-lead-ads-engine.py` | **30-sec speed-to-lead + 12-touch 5-day sprint.** SMS+email instant, variant-specific copy, YES/opt-out reply detection, benchmark tracking. |
| Sys | Health Monitor | `system-health-monitor.py` | Green/yellow/red for all components. SMS alert on red. |
| Sys | Dashboard | `master-dashboard.html` | Visual command center. Auto-refreshes 60s. |

## Current Branch & Recent Work

- **Branch:** `claude/ghl-reactivation-workflow-dCWZZ`
- **Latest session (March 16):** Built GHL reactivation workflow, Facebook Lead Ads v2 speed-to-lead engine (12-touch, 5-day sprint), demo booking page, campaign setup docs.
- **Previous session (March 15):** Created `hot-lead-sequence.py`, 5 SEO blog posts batch 1 & 2, homepage trust layer.

## GHL Reactivation Workflow — Founding 10 (March 16, 2026)

New reactivation engine at `ops/ghl-reactivation-workflow.py`:
- Trigger: Contact tagged `hot-lead-reactivation`
- 5-message sequence: Day 0 SMS, Day 3 SMS, Day 5 value pitch SMS, Day 10 breakup SMS
- Message 4 (price-hesitation) is reply-triggered only — activated by `price-hesitation` tag
- Reply handler: pauses sequence, tags `replied-reactivation`, alerts Wallace, creates 2hr follow-up task
- Industry personalization: 19 industries with custom missed-call hooks
- Exhaustion: after Message 5 with no reply → `reactivation-exhausted` tag, removes trigger tag
- GHL workflow builder guide at `docs/ghl-reactivation-workflow-guide.md`
- Commands: scan, send, enroll, status, run, preview
- State: `ops/ghl-reactivation-state.json`
- Enrolls all 35 contacts currently tagged `hot-lead`

## Facebook Lead Ads Engine v2 — Speed-to-Lead (March 16, 2026)

Full 12-touch, 5-day follow-up sprint at `ops/fb-lead-ads-engine.py`:
- **30-second speed-to-lead**: Scan plist runs every 5 min. SMS #1 + Email #1 fire instantly on detection.
- **12-touch sequence**: 6 SMS + 6 emails over Days 0-5 with time-of-day constraints (morning 8-11am, afternoon 12-5pm)
- **Variant-specific copy**: missed-revenue, after-hours, hiring-headache — each gets unique SMS #2 and email templates
- **Vertical pain points**: HVAC, Plumbing, Dental industry-specific SMS #5 copy
- **Reply detection**: YES-intent keywords (20+), opt-out keywords (stop/unsubscribe/etc.)
- **YES reply**: Tags `fb-lead-interested`, creates 30-min follow-up task, ntfy URGENT
- **Opt-out**: Tags `fb-lead-opted-out`, removes source tag, kills sequence
- **Benchmark tracking**: Median response time, contact rate, lead-to-demo, CPL, cost per demo
- **Commands**: scan, followup, status, sequence, benchmarks, preview
- **Demo booking page**: `docs/demo.html` (GHL calendar embed + demo line CTA)
- Campaign checklist: `docs/fb-lead-ads-campaign-setup.md`
- Day 1-7 playbook: `docs/fb-lead-ads-playbook.md`
- Tracking CSV: `ops/fb-lead-tracking-template.csv`
- State: `~/thecalltaker-ops/fb-lead-ads-state.json`
- Logs: `~/thecalltaker-ops/logs/fb-lead-ads-engine.log`
- launchd: scan every 5min (`com.thecalltaker.fb-leads.scan`), followup every 30min (`com.thecalltaker.fb-leads.followup`)

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Facebook Ads**: Deploy Lead Ads campaign — needs Meta API token from developers.facebook.com
- **Reactivation**: Deploy Founding 10 sequence to 35 hot leads
- **Outreach stack**: ALL 7 components rebuilt + new engines — deploy to Mac
- **Stripe**: NOT connected (Wallace is 16). PayPal/Venmo workaround live
- **Bland.ai balance**: Cold caller + voicemails require funded account
- **GHL aliases**: Blast v3 needs 5 aliases verified
- **Unsubscribe page**: Blast v3 links to thecalltaker.com/unsubscribe — needs building
- **SEO content**: Continue expanding blog with high-intent keyword posts

## Known Blockers

1. Stripe not connected — PayPal/Venmo workaround live
2. GHL API unreachable from CI — deploy from Mac only
3. Retell.ai blocked — needs payment card
4. Bland.ai balance — must be funded before cold caller goes live
5. 5 GHL email aliases need verification
6. Unsubscribe page needs to be built
