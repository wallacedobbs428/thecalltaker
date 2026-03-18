## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-18 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$497/$997/mo plans (updated March 15). 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Co-founder: Mills (strategy, GitHub). William (Wallace's brother) closes demos on Zoom.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/` or `/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets, outreach ops scripts
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo). Voice ID: `lxYfHSkYm1EzQzGhdbfc` (deep variant, v9)
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)

## Current Branch & Recent Work

- **Branch:** `claude/setup-frontend-quickstart-8rUsw`
- **Working tree:** primer.md modified, `ads/` untracked
- **Latest commits (March 17):** Loom video showcase page, Google Ads dynamic conversion values, urgency bar (7 spots + Friday deadline), PayPal mobile redirect fix, onboarding SMS sequence, PayPal abandonment fix, founding customer pricing page (4-tier decoy layout), FB Lead Ad thank-you page, Jessica demo worker rewrite
- **March 15:** Pricing update ($97/$497/$997), Phase 1 design audit on demo-showcase.html
- **March 18 session:** Full QA audit of website HTML files — found 30+ issues including critical pricing inconsistencies, broken links, exposed API keys, and missing meta tags

## QA Audit Findings (March 18, 2026)

Critical issues found in this session:
1. **GHL API key exposed** in 26 client-side HTML files (pit-771d5b3f...)
2. **Premium plan shows $497 instead of $997** on checkout.html and signup.html
3. **pay.html broken links** from index.html and demo.html CTA buttons
4. **fb-thank-you.html tap-to-call** missing +1 prefix
5. **Calculator ROI** divides by $297 (old pricing)
6. **checkout.html** uses GitHub dark theme (#0d1117) instead of brand colors
7. **index.html** missing og:image meta tag
8. Full report delivered in conversation

## Outreach Stack v2 (Rebuilt March 15, 2026)

Full 7-component outreach system rebuild. All scripts in `ops/`.

| # | Component | Script | What It Does |
|---|-----------|--------|-------------|
| C6 | Hot Lead 7-Touch | `hot-lead-converter.py` | 7-touch SMS/email/call sequence |
| C1 | Cold Caller v2 | `cold-caller-v2.py` | Bland.ai outbound calls |
| C2 | Storm Chaser v3 | `storm-chaser-v3.py` | NWS API storm detection emails |
| C3 | Blast Engine v3 | `blast-engine-v3.py` | 40/day/address email rotation |
| C4 | Lead Quality | `lead-quality-engine.py` | Dedup + quality score |
| C5 | Speed-to-Lead v2 | `speed-to-lead-v2.py` | 15s hot signal checks |
| C7 | DM Outreach v2 | `dm-outreach-v2.py` | 3-DM sequence per industry |
| NEW | Hot Lead 5-Step | `hot-lead-sequence.py` | 5-step SMS/email/voicemail |
| Sys | Health Monitor | `system-health-monitor.py` | Component health monitoring |
| Sys | Dashboard | `master-dashboard.html` | Visual command center |

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **FIX QA ISSUES**: Critical pricing bugs, exposed API keys, broken links
- **Founding customer pricing page** live with PayPal flow
- **Loom video showcase** page added for escalation sequence
- **Google Ads** dynamic conversion values configured
- **Stripe**: NOT connected (Wallace is 16). PayPal/Venmo workaround live
- **Bland.ai balance**: Cold caller + voicemails require funded account

## Known Blockers

1. Stripe not connected — PayPal/Venmo workaround live
2. GHL API unreachable from CI — deploy from Mac only
3. Retell.ai blocked — needs payment card
4. Bland.ai balance — must be funded before cold caller goes live
5. 5 GHL email aliases need verification
6. Unsubscribe page needs to be built
