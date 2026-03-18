## REPO IDENTITY — READ FIRST
This is the WEBSITE repo. Website work only.
For agents and ops → ~/thecalltaker-ops/
Never build daemon scripts or plists here.

---

## Session Start Protocol
At the beginning of EVERY session, before doing anything else:
1. Read `primer.md` in full
2. Rewrite `primer.md` completely based on what you now know about the current state of the project — including recent changes, active priorities, known blockers, file structure, and any context that would help you hit the ground running next session
3. Confirm to the user: "Primer updated." then proceed normally

## Git Context Injection
At the start of every session, run:
```bash
bash memory.sh
```
Read the full output before doing anything. Treat this as ground truth for the current repo state. Never assume branch, staged files, or recent changes — always check memory.sh output first.

---

# The Call Taker — Project Documentation

> AI Receptionist SaaS for service businesses. $97/$497/$997/mo plans. 14-day free pilot. Demo line: (615) 784-5747

## Product & Pricing
- **After-Hours Starter:** $97/mo — AI answers after hours only
- **Starter:** $497/mo — Full 24/7 AI receptionist
- **Pro:** $997/mo — 24/7 + priority support + advanced features
- **Pilot:** 14-day free trial, no card required, max 5 concurrent slots
- **Agency:** $47/client wholesale for agency partners

## Architecture Overview

Two repos, 60+ Python scripts, 170+ launchd services running 24/7 on a single Mac.

```
~/Desktop/thecalltaker/          # Website, lead tools, dashboard
~/thecalltaker-ops/              # All engines, ops scripts, state files, logs
  ├── max/                       # Max engine — reply catcher + follow-up machine
  ├── ben/                       # Ben engine — intelligence + conversion scoring
  ├── sam/                       # Sam engine — customer success
  ├── donny/                     # Donny engine — conversion closer
  ├── ops/                       # 40+ ops scripts (email, calls, scraping, etc.)
  ├── logs/                      # Centralized logs + metrics
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
- **What it does:** Catches replies, classifies sentiment, follows up with warm leads, detects demo callers, weather-triggered urgency emails, William's call sheet, breakup emails, referral asks, lead reactivation

### Ben — Intelligence + Conversion Engine
- **File:** `~/thecalltaker-ops/ben/ben-engine.py` (2,847 lines)
- **State:** `ben/ben-state.json`
- **Commands:** morning, sms, reengage, score, uptime, domain-health, review-watch, forecast, competitors, outreach, roi-report, testimonial, ab-results, territory, health-report, evening, status, all
- **Schedule:** 10 launchd services
- **What it does:** Weather-aware briefings, lead scoring (0-10), SMS blasts, re-engage ghosted leads, Voice AI uptime, email domain health, bad-review targeting, revenue forecasting, competitor monitoring, ROI emails, testimonial requests, A/B analysis, territory analysis

### Sam — Customer Success
- **File:** `~/thecalltaker-ops/sam/sam-engine.py` (2,037 lines)
- **State:** `sam/sam-state.json`
- **Commands:** support, health, checkin, referral, upsell, nps, usage, onboard, win, report, status, all
- **Schedule:** 5 launchd services (support every 15min, health 6am, checkin 8am, referral 11am, report 7pm)
- **What it does:** Auto-responds to customer issues, health scoring 1-10, milestone check-ins (day 3/7/14/30 then monthly), referral requests, upsell detection, NPS surveys, usage reports, CRITICAL keyword detection (cancel/refund/lawyer/BBB) → war room alerts

### Donny — Conversion Closer
- **File:** `~/thecalltaker-ops/donny/donny-engine.py` (2,952 lines)
- **State:** `donny/donny-state.json`
- **Commands:** score, speed, objection, hotlist, close, trial, urgency, recover, funnel, win, revenue, report, status, all
- **Schedule:** 8 launchd services (speed+objection every 10min, score every 2hr)
- **What it does:** 0-100 closing score combining all engine signals, speed-to-lead detection, objection handling, William's priority call list, multi-step closing sequences, free trial offers, urgency pressure, dead lead recovery, funnel analysis, revenue countdown to $20K MRR

## Key Ops Scripts

| Script | Purpose | Schedule |
|--------|---------|----------|
| `blast-engine.py` | Cold email with A/B testing, warmup ramp, 19 industries | Every run |
| `cold-caller.py` | Bland.ai outbound: 20 calls/day + 15 secret shopper | 10am + 6pm |
| `funnel-engine.py` | 7-touch multi-channel inbound funnel + 4-email trust sequence | 6x daily |
| `drip-engine.py` | Nurture sequences (calculator-lead + demo-listener DISABLED) | Daily |
| `gmail-sender.py` | 4 Gmail SMTP accounts, 160/day, score-based targeting | 3x daily |
| `rescue-email-engine.py` | Review-mining personalized emails | Daily |
| `partner-outreach.py` | 240 agencies across 8 industries, 20/day | 11am |
| `onboarding-automator.py` | Auto-onboard new customers | Every 30min |
| `lemlist-engine.py` | Lemlist campaign management + lead import | Daily |
| `daily-call-sheet.py` | 15 scored leads + call scripts to ntfy | 8am |
| `reply-monitor.py` | Classifies replies HOT/WARM/NEGATIVE, auto-responds | Continuous |
| `notification-hub.py` | Monitors GHL for replies, demo calls, email opens | Continuous |
| `missed-call-textback.py` | Auto-SMS to missed callers | Continuous |
| `sms-followup.py` | SMS follow-ups after Bland.ai calls (2h + 24h) | 3x daily |
| `ssl-a2p-checker.py` | SSL cert + A2P SMS monitoring | Hourly |
| `revenue-tracker.py` | MRR tracking | 7pm |
| `google-maps-scraper.py` | Multi-source scraper, 8 industries x 200+ cities | On demand |
| `context-builder.py` | Daily brain scan: full system snapshot | 6am |
| `crash-monitor.py` | All launchd services, auto-restarts, ntfy alerts | Every 5min |
| `dashboard-api.py` | Metrics collection, dashboard JSON + funnel + A/B data | Every 5min |
| `daily-report-engine.py` | Nightly performance summary | 9pm |
| `weekly-report-engine.py` | Sunday weekly totals and trends | Sun 9:30pm |
| `ab-tracker.py` | A/B conversion attribution | 8:30pm |
| `speed-alert.py` | Speed-to-lead SMS alerts every 2 min | Every 2min |
| `demo-line-monitor.py` | PILOT text trigger + call duration tagging + daily summary | Multiple |
| `pilot-onboarding-engine.py` | 14-day free pilot: scan, onboard, expire | 6x daily |
| `pilot-conversion-engine.py` | Day 7 + Day 12 conversion emails | 2x daily |
| `try-funnel-engine.py` | $97/mo After-Hours cold sequence + nurture + upgrade | 2x daily |
| `agency-outreach.py` | Agency white-label cold email + scraper | Daily 11:30am |
| `lead-recycler.py` | Weekly lead recycling rotation | Sun 8am |
| `warm-lead-rescue.py` | Cross-engine warm lead finder | On demand |
| `multi-industry-lead-gen.py` | 500+ leads across 17 industries × 20 metros | On demand |
| `lead-list-builder.py` | Combines scraped data into scored CSV/JSON | On demand |
| `ghl-lead-importer.py` | Imports hot-100 leads into GHL | On demand |
| `hot-lead-notify.py` | 4-tier lead scoring, tap-to-call ntfy, outreach queue | 2x daily |
| `ntfy-hub.py` | Unified notification engine | 4 launchd services |
| `hot-lead-converter.py` | 7-touch SMS/email/call sequence | Continuous |
| `cold-caller-v2.py` | Bland.ai outbound v2, hot leads first, 2x retry | 2x daily |
| `storm-chaser-v3.py` | NWS API storm detection, emails within 5 min | Continuous |
| `blast-engine-v3.py` | 40/day/address, 90s gaps, 5-address rotation | 3x daily |
| `lead-quality-engine.py` | Dedup + quality score 1-10, only 5+ pass | Continuous |
| `speed-to-lead-v2.py` | 15s hot signal checks, SMS/call/email cascade | Continuous |
| `dm-outreach-v2.py` | 3-DM sequence per industry, copy-paste export | On demand |
| `hot-lead-sequence.py` | 5-step SMS/email/voicemail (Day 0/1/2/4/7) | 3x daily |

## Infrastructure

### Shared Utilities (`ops/tct_common.py`)
Central module: centralized logging, GHL API wrapper (retry + rate limiting), ntfy notifications, contact registry (file-locked), email validation (MX caching), state file management (atomic writes), metrics collection, crash wrapper (`engine_main()`).

### API Credentials
All in `ops/config.py` with environment variable fallbacks:
- **GHL:** `pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35` (env: `TCT_GHL_API_KEY`)
- **Bland.ai:** `org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969` (env: `TCT_BLAND_API_KEY`)
- **Lemlist:** `1884b87d8e73813f479b4764dc0e1294` (env: `TCT_LEMLIST_API_KEY`)
- **GHL Location ID:** `tQb9YmrGDrdVUJYPKrsY`

### ntfy Topics (5 Topics)
- **URGENT:** `tct-urgent-Hk9UOEZR` — human replies, demo callers, booked demos, checkout clicks
- **SALES:** `tct-sales-63uYsIT9` — daily/weekly reports, pipeline, A/B results, briefings
- **SYSTEM:** `tct-system-vRsfXQRQ` — crashes, restarts, API errors, health checks
- **ACTIVITY:** `tct-activity-cn1Aqa85` — every email/SMS/call sent, enrichments, tags
- **William:** `tct-william-Qm8nR3vK` — William's call sheets, hot leads only

### Ntfy Hub v2 — Unified Notification Engine
- **Script:** `ops/ntfy-hub.py` — 6 commands: prime, nopilot, milestone, summary, status, test
- **State:** `ops/ntfy-hub-state.json`
- **launchd (4 services):** prime (3:25pm), nopilot (6pm+9pm), summary (9pm), milestone (every 30min)
- **Typed API (in tct_common.py):** `notify_demo_call()`, `notify_pilot_signup()`, `notify_payment()`, `notify_hot_reply()`, `notify_pilot_text()`, `notify_engine_crash()`
- **Priority levels:** CRITICAL → `urgent`, HIGH → `high`, INFO → `default`, LOW → `low`
- **Dedupe:** 30-min window by `phone:event_type`. Payment never deduped.
- **War room context:** Every alert appends calls/demos/pilots/revenue/MRR/beta-spots

### GHL API Notes
- Email body field = `"html"` (NOT `"message"`)
- SMS body field = `"message"`
- Phone format: `+1XXXXXXXXXX`
- Conversations API version: `2021-04-15`
- Contacts API version: `2021-07-28`
- Pagination: `page=` param (NOT `offset=`)
- User-Agent header MUST be set to avoid Cloudflare 403
- Message objects can be strings — always check `isinstance(msg, dict)`

### GHL Calendar
- Demo Booking Calendar ID: `h4IlzccZ1m3JprEQqpMJ`
- Widget slug: `thecalltaker-demo`
- Schedule: Mon-Fri 9am-5pm, Sat 10am-2pm, 30min slots
- Embed URL: `https://api.leadconnectorhq.com/widget/booking/h4IlzccZ1m3JprEQqpMJ`

## Voice AI
- **Agent ID:** `695947c64b9ed67d8f1077ad`
- **Agent Name:** "The Call Taker - Demo Line"
- **Welcome:** "Hey, thanks for calling The Call Taker! This is a live AI demo..."
- **UNIVERSAL DEMO:** Adapts to ANY industry — caller says "locked out" → locksmith mode, "AC broken" → HVAC mode, etc. After ~1 min pitches free 14-day pilot.
- **Voice ID:** `w9rPM8AIZle60Nbpw7nl` (current), Jessica backup: `lxYfHSkYm1EzQzGhdbfc`
- **Prompt:** Universal demo, ~263 words (v5), pain-first closer with revenue anchor + scarcity
- **Responsiveness:** 1.0 (max)
- **Mid-call actions:** NONE (removed for latency)
- **Knowledge base:** Removed (latency)
- **Speed fix (Feb 27):** Prompt 925→160 words, responsiveness 0.8→1.0, greeting 16→10 words
- **Pain-first closer (March 2):** v5 prompt. Simulates pain, revenue anchor ($2K-10K/mo), scarcity (3 businesses this month), price anchor ($97/mo)
- **Demo line rule:** Demo line (615) 784-5747 = ALWAYS universal demo. Client lines = industry-specific. NEVER overwrite demo line.
- **Industry prompts:** Locksmith, HVAC, Water Damage in `~/Desktop/voice-agent-speed-fix/industry-prompts/`
- **Retell agent:** Agent ID: `agent_5acbcae27d34f7f82f1355e546`. BLOCKED: needs payment card.
- **API:** PATCH `/voice-ai/agents/{id}?locationId=` (plural "agents"), needs `locationId` in query string
- **Pricing response:** "$97/mo after-hours, $297/mo full 24/7, no contracts"

## Website

**Deployment:** GitHub Pages via GitHub Actions. ONLY files inside `website/` get deployed.
**Deploy workflow:** `.github/workflows/deploy.yml` — triggers on push to `main` when `website/**` changes.
**Total: 128+ pages live on thecalltaker.com**

### Core Pages (in `website/`)
- `index.html` — homepage with industry selector + premium nav + cursor effects
- `signup.html` — 3-step purchase flow
- `calculator.html` — ROI calculator (lead capture + war room alert)
- `book.html` — demo booking (GHL calendar embed)
- `checkout.html` — plan checkout (routes to /pilot/ until Stripe connected)
- `demo-showcase.html` — live demo line showcase
- `your-results.html` — 30-day results simulator (shareable URL)
- `your-audit.html` — personalized audit reports (noindex)
- `compare.html` — AI vs alternatives comparison
- `services.html`, `partners.html`, `thank-you.html`, `privacy.html`, `terms.html`, `404.html`
- `portal.html` — customer self-service (noindex)
- `blog.html` — blog index
- `industries.html` — industries hub

### Industry Pages (13) — `website/industries/`
HVAC, Roofing, Plumbing, Electrical, Dental, MedSpa, Legal, Property Mgmt, Veterinary, Locksmith, Garage Door, Towing, Funeral

### Blog Articles (54+) — `website/blog/`
3 per industry + SEO articles. Green/black design system. Inter font. Schema.org markup.

### $97 Try Funnel — `website/try-funnel/`
- `index.html` — landing page
- `checkout.html` — $97 Stripe checkout
- `upgrade.html` — upsell to $297/$497

### Agency Program — `website/agency-program/`
- `agency.html`, `pitch-deck.html`, `pricing-sheet.html`, `setup-guide.html`

### Sales Toolkit (password: tctoolkit) — `website/toolkit/`
- `index.html`, `call-cheatsheet.html`, `objection-handler.html`, `case-studies.html`

### Demo Share Pages — `website/demo/`
- `index.html` — reads `?industry=` URL param to auto-select industry

### SEO Landing Pages (13) — `website/ai-answering-service/`
- Hub page + 12 industry pages targeting "AI answering service for [industry]"

### Case Studies (13) — `website/case-studies/`
- Hub page + 13 individual case studies across all industries

## Premium Navigation (March 1, 2026)
- Glassmorphism header: transparent → frosted blur on scroll
- Nav underline animation, scroll spy, header CTA morph
- Mobile: fullscreen overlay with GSAP stagger animations
- Scroll progress bar: 3px orange gradient fixed at top
- CTA link: `/pilot/` (Start Free Pilot)

## Cursor Effects v3 — Crosshair + Canvas Particles (March 2, 2026)
- Desktop only (`@media (pointer:fine) and (hover:hover)`)
- SVG crosshair cursor + velocity-reactive canvas particle trail
- FPS auto-degrade: <45fps → halves particles, <30fps → kills all
- Hero: spotlight, text scatter, floating SVG icons
- Magnetic hover: buttons pull at 150px, nav links at 80px
- Card effects: 3D tilt, dynamic shadows, conic-gradient border glow
- **CRITICAL — Hero H1 rules:**
  - NEVER set `.hero h1` to `display: inline`
  - Text scatter MUST preserve word-level grouping (inline-block wrappers)
  - "Receptionist" is in `<span class="no-break-word">` — do NOT remove
  - Regression test: `python3 website/tests/hero-regression.py`

## Hero Phone Mockup (March 1, 2026)
- Pure CSS/SVG animated phone — zero external images
- 5 notification cards with stagger animations
- 3 floating bubbles (hidden on mobile)
- Old classes removed: `.hero-image`, `.hero-image-badge`

## Attribution Tracking
- `tct-tracking.js` captures UTM params, gclid, fbclid, referrer, landing page
- Stored in `sessionStorage` as `tct_attribution` (first-touch)
- `getTctAttributionTags()` — returns GHL tag array
- `getTctAttributionNotes()` — returns full attribution string
- Integrated into popup form, calculator, signup, and book pages

## Pilot Program (14-Day Free Trial)
- **Directory:** `~/thecalltaker-ops/pilot/`
- **Max Slots:** 5 concurrent
- **Onboarding Engine:** scans for `pilot-signup` tag, auto-onboards
- **Conversion Engine:** Day 7 check-in, Day 10 ROI, Day 12 urgency, post-expiry follow-ups
- **State:** `~/thecalltaker-ops/pilot/pilot-state.json` (atomic writes)
- **GHL Tags:** `pilot-signup` (trigger), `pilot-active` (during), `pilot-expired` / `pilot-converted` (after)
- **CTA Strategy:** All outreach → "free 14-day pilot, no card, no risk"

## Acquisition Engine v4 — Continuous Lead Machine (March 6, 2026)
Three-engine self-feeding pipeline: **Scraper → Scorer/Router → Outreach Queue Consumer**

### Lead Scraper v4 (`lead-scraper-v3.py`)
- 6x daily pipeline (scrape→enrich→score), 5 industries × 5 metros per batch
- Data: Bing + DDG search → visit websites → extract phone/email/name + JSON-LD reviews
- Master list: `~/Desktop/thecalltaker/leads/master-all-industries.json` — 1,765+ leads
- Cursor-based rotation: 17 industries × 56 metros, full rotation ~6 days
- Enrichment: 45-60% hit rate (DDG snippets + JSON-LD)

### Scorer & Router (`hot-lead-notify.py`)
- Score 0-100: Industry tier (30), reviews (20), metro (15), team size (10), no website (8), rating (7), email (5), owner (5)
- URGENT (70+) → ntfy tap-to-call. HIGH (60-69) → batch digest. MEDIUM (45-59) → outreach queue. LOW (<45) → logged.

### Outreach Queue (`outreach-queue.py`)
- Imports MEDIUM leads → GHL contacts tagged `outreach-queue` + `pilot-candidate`
- 30 imports/run, blast-engine + funnel-engine pick them up automatically

## Demo Line Monitor — Hardened (March 2, 2026)
- **Script:** `ops/demo-line-monitor.py` — 10 commands
- **Test:** `ops/demo-funnel-test.py` — 49 assertions
- **PILOT text trigger:** keyword detection → scarcity-aware auto-reply → tags → URGENT ntfy
- **Beta spots:** 3/month, resets monthly, phone-locked to prevent gaming
- **Call tiers:** `demo-caller` (all), `engaged-demo` (60s+), `hot-demo` (120s+ → CRITICAL escalation)
- **Hot Lead Escalation:** 15min reminder if no `contacted` tag, 1hr hard escalation
- **No-Activity Watchdog:** Daily 3pm, alerts if 0 calls or texts in 24h

## Demo Follow-Up Engine v2 — Pain-First (March 2, 2026)
- **4-touch pain-first sequence:**
  1. Touch 1 (10min): SMS pain hook
  2. Touch 2 (1hr): Email — missed calls cost + scarcity + $97 anchor
  3. Touch 3 (next morning): SMS to prospect + ntfy alert to Wallace with call script
  4. Touch 4 (day 2): Hard scarcity SMS — "1 pilot spot left this week"
- Industry-aware: `get_job_word()` maps 17 industry tags to job words

## Secret Shopper System (Feb 27, 2026)
- `secret-shopper.py` — 30 calls/batch, generates branded proof reports
- Reports at `website/shopper-reports/{contact_id}.html`
- Dashboard at `dashboard/shopper-dashboard.html`
- 4 launchd services (evening, night, check, saturday)
- 19 industries with per-industry scenarios

## Monitoring & Alerting
- **Crash Monitor:** Every 5 min, auto-restarts, URGENT for revenue-critical services
- **Dashboard:** `dashboard/index.html` — auto-refreshes every 5 min
- **Daily Reports:** `~/thecalltaker-ops/reports/{YYYY-MM-DD}.json` — 9pm nightly
- **Weekly Reports:** Sunday 9:30pm
- **Error Log:** `~/thecalltaker-ops/logs/errors.log`
- **Combined Log:** `~/thecalltaker-ops/logs/all-engines.log`

## State Files (All atomic-written via tempfile + os.replace)
- `max/max-state.json` — replies, followups, demo callers, sentiment
- `ben/ben-state.json` — lead scores, ROI reports, territory
- `sam/sam-state.json` — customer health, issues, checkins, NPS
- `donny/donny-state.json` — closing scores, speed responses, objections
- `ops/blast-state.json`, `ops/funnel-state.json`, `pilot/pilot-state.json`
- `ops/try-funnel-state.json`, `ops/agency-outreach-state.json`, `ops/lead-recycler-state.json`
- `ops/contact-registry.json` — cross-engine contact coordination (file-locked)

## Contact Registry
`ops/contact-registry.json` — all engines read/write through `tct_common.py`:
- `check_registry(contact_id, touch_type)` → `(ok, reason)`
- `update_registry(contact_id, engine_name, touch_type)` → records touch
- Min 3-day gap between same-type touches, max 2 emails/week per lead
- File-locked (fcntl), 30-day auto-prune

## Multi-Industry Outreach
- **17 Industries:** Locksmith, HVAC, Plumbing, Electrical, Roofing, Pest Control, Towing, Dental, Med Spa, Legal, Veterinary, Auto Repair, Cleaning, Property Mgmt, Water Damage, Landscaping, General Contractor
- **56 Metros:** Core 20 + Sun Belt + Mid-market + Florida/SE expansion waves
- **Lead List:** `leads/master-all-industries.csv` (1,765 leads), `hot-100.csv`, per-industry CSVs
- **Templates:** `outreach/universal/` — 3 emails, 2 SMS, 1 cold call script

## How to Restart Things
```bash
# Single service
launchctl unload ~/Library/LaunchAgents/com.thecalltaker.max.monitor.plist
launchctl load ~/Library/LaunchAgents/com.thecalltaker.max.monitor.plist

# All crashed services
python3 ~/thecalltaker-ops/ops/crash-monitor.py restart

# Check status
python3 ~/thecalltaker-ops/ops/crash-monitor.py status

# Run engine manually
python3 ~/thecalltaker-ops/max/max-engine.py monitor
python3 ~/thecalltaker-ops/ben/ben-engine.py score
python3 ~/thecalltaker-ops/sam/sam-engine.py support
python3 ~/thecalltaker-ops/donny/donny-engine.py speed
```

## Known Issues / TODOs
1. **Stripe not connected** — needs parent/guardian (Wallace is 16). PayPal bridge live.
2. **stripe-webhook-handler.py** — signature verification stubbed (returns True)
3. **reply-monitor** service has exit code 1 — check and restart if needed
4. **Gmail SMTP passwords** in plaintext in `gmail-sender.py` — move to env vars
5. **Meta Ads** — Ad Account ID 25895456013410801, needs API token
6. **ColdDMs** — CANCELED ($174/mo). Instagram DMs handled by dm-tracker script.

## Disabled Services
1. **[2026-03-02] com.thecalltaker.toolcosts — DISABLED.** Crashed in loop due to macOS TCC. Fix: change OUTPUT_FILE to `~/thecalltaker-ops/`.

## Resolved Issues
1. **[2026-02-27] Pilot engines never ran from launchd** — macOS TCC blocking `~/Desktop/`. Fixed: moved to `~/thecalltaker-ops/pilot/`. Full postmortem in ops logs.
