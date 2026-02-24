# The Call Taker — System Documentation

> AI Receptionist SaaS for service businesses. $497/mo. Demo line: (615) 784-5747
> Built and run by Wallace Dobbs (@moneymaker99)

## Architecture Overview

Two repos, 60+ Python scripts, 80+ launchd services running 24/7 on a single Mac.

```
~/Desktop/thecalltaker/          # Website, lead tools, dashboard
~/thecalltaker-ops/              # All engines, ops scripts, state files, logs
  ├── max/                       # Max engine — reply catcher + follow-up machine
  ├── ben/                       # Ben engine — intelligence + conversion scoring
  ├── sam/                       # Sam engine — customer success
  ├── donny/                     # Donny engine — conversion closer
  ├── ops/                       # 40+ ops scripts (email, calls, scraping, etc.)
  ├── logs/                      # Centralized logs + metrics (NEW)
  │   ├── all-engines.log        # Combined log from all engines
  │   ├── errors.log             # Errors only
  │   ├── crash-monitor.log      # Crash detection log
  │   └── metrics/               # Daily JSON metrics for dashboard
  ├── leads/                     # Lead data files
  └── sales/                     # Sales assets
```

## The 4 Engines

### Max — Reply Catcher + Follow-Up Machine
- **File:** `~/thecalltaker-ops/max/max-engine.py` (3,302 lines)
- **State:** `max/max-state.json`
- **Commands:** monitor, followup, pipeline, report, status, all, indeed, opens, stale, william, escalate, referral, reactivate, seasonal, winback, digest, sentiment, attribution, cleanup, competitor
- **Schedule:** 8 launchd services (monitor every 30min, followup 9am, pipeline midnight, report 8pm, seasonal 11am, digest 7:30am, reactivate 2pm, winback Mon 10am)
- **APIs:** GHL (contacts, conversations, messages), wttr.in (weather), ntfy.sh
- **What it does:** Catches replies, classifies sentiment (positive/negative/objection/question), follows up with warm leads, detects demo line callers, sends weather-triggered urgency emails, generates William's call sheet, sends breakup emails to cold leads, asks for referrals, reactivates old leads with Google reviews angle

### Ben — Intelligence + Conversion Engine
- **File:** `~/thecalltaker-ops/ben/ben-engine.py` (2,847 lines)
- **State:** `ben/ben-state.json`
- **Commands:** morning, sms, reengage, score, uptime, domain-health, review-watch, forecast, competitors, outreach, roi-report, testimonial, ab-results, territory, health-report, evening, status, all
- **Schedule:** 10 launchd services
- **APIs:** GHL, wttr.in, ntfy.sh, DuckDuckGo (review scraping)
- **What it does:** Weather-aware morning briefings, enhanced lead scoring (0-10), SMS blasts, re-engages warm leads who ghosted, monitors Voice AI uptime, checks email domain health, finds bad-review businesses to target, revenue forecasting, competitor price monitoring, personalized ROI emails, testimonial requests, A/B testing analysis, territory market analysis, system health reports

### Sam — Customer Success
- **File:** `~/thecalltaker-ops/sam/sam-engine.py` (2,037 lines)
- **State:** `sam/sam-state.json`
- **Commands:** support, health, checkin, referral, upsell, nps, usage, onboard, win, report, status, all
- **Schedule:** 5 launchd services (support every 15min, health 6am, checkin 8am, referral 11am, report 7pm)
- **APIs:** GHL, ntfy.sh
- **What it does:** Auto-responds to customer issues with knowledge base answers, health scoring 1-10, milestone check-ins (day 3/7/14/30 then monthly), referral requests at optimal moments, upsell detection (Starter->Pro), NPS surveys, weekly usage reports, onboarding tracking, win story capture, CRITICAL keyword detection (cancel/refund/lawyer/BBB) triggers immediate war room alerts

### Donny — Conversion Closer
- **File:** `~/thecalltaker-ops/donny/donny-engine.py` (2,952 lines)
- **State:** `donny/donny-state.json`
- **Commands:** score, speed, objection, hotlist, close, trial, urgency, recover, funnel, win, revenue, report, status, all
- **Schedule:** 8 launchd services (speed+objection every 10min, score every 2hr, etc.)
- **APIs:** GHL, ntfy.sh
- **What it does:** Unified 0-100 closing score combining ALL engine signals, speed-to-lead (detects hot signals every 10min, responds immediately), objection handling, William's priority call list, multi-step closing sequences for 70+ scored leads, free trial offers, limited-time urgency pressure, dead lead recovery, conversion funnel analysis, win pattern analysis, revenue countdown to $20K MRR

## Key Ops Scripts

| Script | Purpose | Schedule |
|--------|---------|----------|
| `blast-engine.py` | Cold email with A/B testing, warmup ramp, 13 industries | Every run |
| `cold-caller.py` | Bland.ai outbound: 20 calls/day + 15 secret shopper | 10am + 6pm |
| `drip-engine.py` | 3 nurture sequences (13 templates), 18+ industry placeholders | Daily |
| `gmail-sender.py` | 4 Gmail SMTP accounts, 160/day, score-based targeting | 3x daily |
| `rescue-email-engine.py` | Review-mining personalized emails, industry-specific | Daily |
| `partner-outreach.py` | 240 agencies across 8 industries, 20/day | 11am |
| `onboarding-automator.py` | Auto-onboard new customers | Every 30min |
| `lemlist-engine.py` | Lemlist campaign management + lead import | Daily |
| `daily-call-sheet.py` | 15 scored leads + call scripts to ntfy | 8am |
| `reply-monitor.py` | Classifies inbound replies HOT/WARM/NEGATIVE, auto-responds | Continuous |
| `notification-hub.py` | Monitors GHL for new replies, demo calls, email opens | Continuous |
| `missed-call-textback.py` | Auto-SMS to missed callers | Continuous |
| `sms-followup.py` | SMS follow-ups after Bland.ai calls (2h + 24h) | 3x daily |
| `ssl-a2p-checker.py` | SSL cert + A2P SMS monitoring | Hourly |
| `revenue-tracker.py` | MRR tracking | 7pm |
| `google-maps-scraper.py` | Multi-source scraper (Bing, DDG), 8 industries x 200+ cities | On demand |
| `context-builder.py` | Daily brain scan: full system snapshot | 6am |
| `crash-monitor.py` | Watches all launchd services, auto-restarts, ntfy alerts | Every 5min |
| `dashboard-api.py` | Collects metrics from all engines, generates dashboard JSON + funnel + A/B data | Every 5min |
| `daily-report-engine.py` | Nightly performance summary: emails, SMS, calls, replies, demos, errors | 9pm |
| `weekly-report-engine.py` | Sunday weekly totals, trends, best performers, WoW comparison | Sun 9:30pm |
| `ab-tracker.py` | A/B conversion attribution: groups contacts by variant, cross-references Max/Donny | 8:30pm |

## Infrastructure

### Shared Utilities (`ops/tct_common.py`)
Central module providing:
- **Centralized logging** — writes to engine-specific + combined + error logs in `~/thecalltaker-ops/logs/`
- **GHL API wrapper** — retry (5s/15s/30s backoff), 429 rate limiting (30s/60s/120s), response validation, metrics tracking
- **ntfy notifications** — header sanitization, 3-attempt retry
- **Contact registry** — file-locked read-modify-write to prevent cross-engine race conditions
- **Email validation** — syntax, junk patterns, MX records with caching
- **State file management** — atomic writes (tempfile + os.replace), corruption detection + backup
- **Metrics collection** — per-run JSON metrics for dashboard
- **Crash wrapper** — `engine_main()` wraps execution with try/except, sends ntfy crash alerts

Usage in any script:
```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/thecalltaker-ops/ops"))
from tct_common import *
```

### API Credentials
All in `ops/config.py` with environment variable fallbacks:
- **GHL:** `pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35` (env: `TCT_GHL_API_KEY`)
- **Bland.ai:** `org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969` (env: `TCT_BLAND_API_KEY`)
- **Lemlist:** `1884b87d8e73813f479b4764dc0e1294` (env: `TCT_LEMLIST_API_KEY`)
- **Clay:** `92b80eb729dc2be9cbf2` (env: `TCT_CLAY_API_KEY`)
- **GHL Location ID:** `tQb9YmrGDrdVUJYPKrsY`

### ntfy Topics
- **Ops:** `tct-xK9mW4vR7pLd` — daily reports, system status
- **War Room:** `tct-warroom-Kx7mN9pQ` — hot leads, customer crises, demos booked
- **William:** `tct-william-Qm8nR3vK` — call sheets, hot leads only
- **Calls:** `tct-calls-Wk4mP8nJ` — Bland.ai call results

### GHL API Notes
- Email body field = `"html"` (NOT `"message"`)
- SMS body field = `"message"`
- Phone format: `+1XXXXXXXXXX`
- Conversations API version: `2021-04-15`
- Contacts API version: `2021-07-28`
- Pagination: use `page=` param (NOT `offset=`)
- User-Agent header MUST be set to avoid Cloudflare 403
- Message objects can be strings — always check `isinstance(msg, dict)`

### Voice AI
- Agent ID: `695947c64b9ed67d8f1077ad`
- Voice: Jessica (`lxYfHSkYm1EzQzGhdbfc`)
- PATCH endpoint needs `locationId` in query string, not body

### Monitoring & Alerting
- **Crash Monitor:** `ops/crash-monitor.py` — every 5 min, checks all launchd services, auto-restarts crashed ones, sends ntfy alert
- **Dashboard:** `~/Desktop/thecalltaker/dashboard/index.html` — open in browser, auto-refreshes every 5 min, includes conversion funnel + A/B test performance sections
- **Daily Reports:** `~/thecalltaker-ops/reports/{YYYY-MM-DD}.json` — generated 9pm nightly by `daily-report-engine.py`
- **Weekly Reports:** `~/thecalltaker-ops/reports/weekly-{YYYY-MM-DD}.json` — generated Sunday 9:30pm by `weekly-report-engine.py`
- **A/B Tracking:** `ops/ab-tracker-state.json` — per-variant sent/reply/demo counts, updated 8:30pm daily
- **Dashboard Data:** `ops/dashboard-api.py` generates `dashboard-data.json` every 5 min
- **Error Log:** `~/thecalltaker-ops/logs/errors.log` — all ERROR/CRITICAL from all engines
- **Combined Log:** `~/thecalltaker-ops/logs/all-engines.log` — everything from all engines

### Logs
All centralized in `~/thecalltaker-ops/logs/`:
```
logs/
├── all-engines.log          # Combined from all engines
├── errors.log               # ERROR + CRITICAL only
├── crash-monitor.log        # Crash detection + restarts
├── max.log                  # Max engine only
├── ben.log                  # Ben engine only
├── sam.log                  # Sam engine only
├── donny.log                # Donny engine only
├── crash-monitor-stdout.log # launchd stdout
├── crash-monitor-stderr.log # launchd stderr
├── dashboard-stdout.log     # Dashboard snapshot stdout
└── metrics/                 # Daily JSON metrics
    ├── 2026-02-24.json
    └── ...
```

## How to Restart Things

### Restart a single engine service
```bash
launchctl unload ~/Library/LaunchAgents/com.thecalltaker.max.monitor.plist
launchctl load ~/Library/LaunchAgents/com.thecalltaker.max.monitor.plist
```

### Restart all crashed services
```bash
python3 ~/thecalltaker-ops/ops/crash-monitor.py restart
```

### Check all service status
```bash
python3 ~/thecalltaker-ops/ops/crash-monitor.py status
```

### View dashboard data in terminal
```bash
python3 ~/thecalltaker-ops/ops/dashboard-api.py status
```

### Check specific engine logs
```bash
tail -50 ~/thecalltaker-ops/logs/max.log
tail -50 ~/thecalltaker-ops/logs/errors.log
```

### Run an engine command manually
```bash
python3 ~/thecalltaker-ops/max/max-engine.py monitor
python3 ~/thecalltaker-ops/ben/ben-engine.py score
python3 ~/thecalltaker-ops/sam/sam-engine.py support
python3 ~/thecalltaker-ops/donny/donny-engine.py speed
```

## State Files
Each engine saves state to JSON. State files are atomic-written (tempfile + os.replace) to prevent corruption.

- `max/max-state.json` — reply IDs, followup tracking, demo callers, weather sent, sentiment log
- `ben/ben-state.json` — lead scores, re-engaged contacts, ROI reports, territory analysis
- `sam/sam-state.json` — customer health scores, issues, checkins, referrals, NPS
- `donny/donny-state.json` — closing scores, close sequences, speed responses, objections
- `ops/blast-state.json` — email sent/bounced/skipped counts, daily limits
- `ops/contact-registry.json` — cross-engine contact coordination (who sent what, when)

## Contact Registry
Shared file at `ops/contact-registry.json`. All engines read/write through `tct_common.py` functions:
- `check_registry(contact_id, touch_type)` — returns `(ok, reason)` before contacting a lead
- `update_registry(contact_id, engine_name, touch_type)` — records a touch after sending
- Enforces: minimum 3-day gap between same-type touches, max 2 emails/week per lead
- File-locked (fcntl) to prevent race conditions between concurrent engines
- Touches older than 30 days auto-pruned

## Website Pages
Located in `~/Desktop/thecalltaker/`:
- `index.html` — main site with industry selector, `/?industry=` URL param
- `signup.html` — 3-step purchase flow
- `calculator.html` — ROI calculator
- `your-audit.html` — personalized audit reports (noindex)
- 8 industry pages: `hvac.html`, `roofing.html`, `plumbing.html`, `electrical.html`, `dental.html`, `medspa.html`, `legal.html`, `property-management.html`
- `industries.html` — industry hub
- `dashboard/index.html` — master command center dashboard (NEW)
- `dashboard/pipeline.html` — pipeline-specific dashboard

## Known Issues / TODOs
1. **Stripe not connected** — needs parent/guardian (Wallace is 16). Setup guide sent via ntfy.
2. **stripe-webhook-handler.py** — signature verification is stubbed out (returns True). When Stripe is connected, implement HMAC-SHA256 verification.
3. **reply-monitor** service has exit code 1 — check `launchctl list | grep reply-monitor` and restart if needed.
4. **Gmail SMTP passwords** are in plaintext in `gmail-sender.py`. Move to environment variables when possible.
5. **Meta Ads** — Ad Account ID 25895456013410801, needs API token from developers.facebook.com.
6. **ColdDMs** — Scale plan ($174/mo), no API available for automation.

## Team
- **Wallace Dobbs** — founder/CEO, builds everything, funds everything
- **William** (Wallace's brother) — demo closer, face on Zoom calls
- **Mills** — co-founder/partner, strategy, has GitHub access
- **Max** — 24/7 AI reply catcher + follow-up machine
- **Ben** — 24/7 AI intelligence engine
- **Sam** — 24/7 AI customer success
- **Donny** — 24/7 AI conversion closer
