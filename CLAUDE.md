# The Call Taker — System Documentation

> AI Receptionist SaaS for service businesses. $97/$297/$497/mo. Demo line: (615) 784-5747
> Built and run by Wallace Dobbs (@moneymaker99)

## Architecture Overview

Two repos, 60+ Python scripts, 86 launchd services running 24/7 on a single Mac.

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
| `blast-engine.py` | Cold email with A/B testing, warmup ramp, 19 industries | Every run |
| `cold-caller.py` | Bland.ai outbound: 20 calls/day + 15 secret shopper | 10am + 6pm |
| `funnel-engine.py` | 7-touch multi-channel inbound funnel (email+SMS+Bland.ai call) + 4-email trust sequence for site visitors, 19 industries | 6x daily (8am-6pm) |
| `drip-engine.py` | 1 nurture sequence (calculator-lead + demo-listener DISABLED — replaced by funnel-engine) | Daily |
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
| `speed-alert.py` | Speed-to-lead SMS alerts to Wallace every 2 min | Every 2min |
| `demo-line-monitor.py` | PILOT text trigger + call duration tagging + daily demo summary | pilot-text 5min, call-track 15min, summary 9:15pm |
| `pilot-onboarding-engine.py` | 14-day free pilot: scan, onboard, expire (3 slots max) | 6x daily (8am-6pm) |
| `pilot-conversion-engine.py` | Day 7 + Day 12 conversion emails with real call stats | 2x daily (9:30am, 3:30pm) |
| `try-funnel-engine.py` | $97/mo After-Hours Starter: cold sequence + nurture + upgrade | 2x daily (10am, 2pm) |
| `agency-outreach.py` | Agency white-label cold email + scraper + import | Daily 11:30am |
| `lead-recycler.py` | Weekly lead recycling: premium→$97→pilot→breakup rotation | Sun 8am |
| `warm-lead-rescue.py` | Cross-engine warm lead finder + personal follow-up sender | On demand |
| `multi-industry-lead-gen.py` | Scrapes 500+ leads across 17 industries × 20 metros, scores 1-100 | On demand |
| `lead-list-builder.py` | Combines scraped data into scored CSV/JSON, generates hot-100 | On demand |
| `ghl-lead-importer.py` | Imports hot-100 leads into GHL with industry tags + pilot-candidate | On demand |

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
- **GHL Location ID:** `tQb9YmrGDrdVUJYPKrsY`

### ntfy Topics (4-Tier System, Feb 25 2026)
- **URGENT:** `tct-urgent-Hk9UOEZR` — real human replies, demo callers, booked demos, checkout clicks, cold escalations. Checked every 5 min.
- **SALES:** `tct-sales-63uYsIT9` — daily/weekly reports, pipeline updates, A/B results, tool cost alerts, morning briefings. Checked 1-2x/day.
- **SYSTEM:** `tct-system-vRsfXQRQ` — engine crashes, service restarts, API errors, health checks. Only checked when something seems broken.
- **ACTIVITY:** `tct-activity-cn1Aqa85` — every email/SMS/call sent, leads enriched, contacts tagged, auto-responders, scrapers. High volume, rarely checked.
- **William:** `tct-william-Qm8nR3vK` — William's call sheets, hot leads only (unchanged)

### GHL API Notes
- Email body field = `"html"` (NOT `"message"`)
- SMS body field = `"message"`
- Phone format: `+1XXXXXXXXXX`
- Conversations API version: `2021-04-15`
- Contacts API version: `2021-07-28`
- Pagination: use `page=` param (NOT `offset=`)
- User-Agent header MUST be set to avoid Cloudflare 403
- Message objects can be strings — always check `isinstance(msg, dict)`

### GHL Calendar
- Demo Booking Calendar ID: `h4IlzccZ1m3JprEQqpMJ`
- Widget slug: `thecalltaker-demo`
- Schedule: Mon-Fri 9am-5pm, Sat 10am-2pm, 30min slots
- Embed URL: `https://api.leadconnectorhq.com/widget/booking/h4IlzccZ1m3JprEQqpMJ`
- All 13 industry pages use this calendar ID

### Premium Navigation (March 1, 2026)
- **Location:** `website/index.html` (inline CSS + JS)
- **Glassmorphism header:** Transparent on hero → frosted blur (`backdrop-filter: blur(20px)`) on scroll
- **Nav underline animation:** Orange underline slides left-to-right on hover via `::after` pseudo-element
- **Scroll spy:** Active section highlighted in nav (`.active` class toggled on `a[href^="#"]`)
- **Header CTA:** Ghost/outline style → filled orange with glow pulse animation after hero scroll
- **Mobile menu:** Fullscreen overlay (`#mobileOverlay`) with GSAP stagger animations on `#mobileMenu li`
- **Hamburger morph:** 3-line → X via CSS transforms on `.mobile-toggle.active span`
- **Scroll progress bar:** `#scrollProgress` — 3px orange gradient fixed at top, z-index 1100
- **Accessibility:** `aria-expanded` on hamburger, `role="dialog"` + `aria-modal` on overlay, Escape key closes menu
- **CTA link:** `/pilot/` (Start Free Pilot) — separate from nav-links for independent styling/visibility
- **Mobile hides:** `.nav-links` + `.header-cta` hidden at 768px, hamburger + overlay take over

### Cursor Effects v3 — Crosshair + Canvas Particles (March 2, 2026)
- **Location:** `website/index.html` (inline CSS `cx-*` classes + JS at bottom)
- **Dependency:** GSAP 3.12.5 from cdnjs CDN (already loaded)
- **Desktop only:** `@media (pointer:fine) and (hover:hover)` + JS matchMedia + prefers-reduced-motion. Zero code on mobile/tablet.
- **Custom cursor:** SVG crosshair (32x32) — 4 orange lines + white center ring + filled orange dot. Drop-shadow glow intensifies on button lock-on (`.locked` class).
- **Canvas particle trail:** Velocity-reactive spawning (fast=3, medium=2, slow=1, stopped=0). Particles: 2-5px, gravity drift downward like embers, 60% orange #F97316, 25% amber #FBBF24, 15% white. Max 100 particles. Fade over 0.5-0.8s.
- **FPS auto-degrade:** Samples 60 frames. <45fps → halves max to 50 particles. <30fps → kills all particles, falls back to just SVG crosshair.
- **Hero effects:** (1) Spotlight — 500px radial glow revealing circuit grid pattern via CSS mask, (2) Text scatter — h1 letters push 1-3px from cursor within 90px radius, elastic snap-back, (3) 6 floating SVG icons (phone, checkmark, chat, bolt, shield, signal) at 8% opacity, repel from cursor like objects in water within 150px
- **Magnetic hover:** Buttons pull at 150px range, nav links at 80px, elastic snap-back on leave. Button sweep-fill gradient on hover (CSS ::after). Nav underline draws in like pen stroke (CSS scaleX transition).
- **Card effects:** 3D tilt (10deg), dynamic shadow shifts with cursor position, light reflection gradient follows cursor (CSS --mx/--my vars), conic-gradient border glow orbits card on hover (GSAP-animated --border-angle).
- **Click:** 12-particle burst from click point + crosshair snap-scale animation (0.7→1 elastic).
- **Scroll-reactive sections:** hero=full particles, features=reduced, demo=cursor-only, pricing=full particles, footer=no particles.
- **Class gating:** `html.has-cursor` on init. If GSAP missing or reduced-motion, normal cursor.
- **Size:** ~9KB JS, ~2.5KB CSS
- **To disable:** Remove `CURSOR EFFECTS v3` CSS block + cursor `<script>` block
- **Hero copy:** "An AI Receptionist Trained For Your Business" — universal multi-industry (plumber, dentist, attorney, locksmith). Updated title + OG + Twitter meta.
- **Hero subline:** Desktop (`.subtitle-desktop`) = long version emphasizing custom AI per business. Mobile (`.subtitle-mobile`) = shorter version. Toggled via CSS at 768px breakpoint. `max-width: 600px` on `.hero .subtitle`.

### Hero Phone Mockup (March 1, 2026)
- **Location:** `website/index.html` — replaced Unsplash stock photo with pure CSS/SVG animated phone
- **No external images:** Zero network requests, instant load, no Lighthouse penalty
- **Phone device:** Dark gradient frame (`#1a1a2e` → `#0f0f1a`) with orange accent border + glow shadow
- **5 notification cards:** Stagger-animated (`.phone-notif` with `animation-delay: .6s/.1.4s/2.2s/3s`). Shows: locksmith emergency call, HVAC appointment booked, details texted, dental patient, roofing estimate
- **Status bar:** "AI Active" with green pulse dot, "The Call Taker" branding, "24/7"
- **3 floating bubbles:** "3 calls answered this hour", "$2,400 in jobs booked today", "0 missed calls" — hidden on mobile
- **Responsive:** Scales down at 1024px (260px wide) and 768px (240px wide, smaller padding/radii)
- **Old classes removed:** `.hero-image`, `.hero-image-badge`, `.hero-image img` — all replaced with `.hero-phone`, `.phone-device`, etc.

### Public Contact Email
- **Email:** `thecalltakerai@gmail.com` — used across all 80+ public-facing website pages
- **Agency operational emails:** `wallace@mail.thecalltaker.com` — NOT changed (used in setup-guide.html + pricing-sheet.html)

### Attribution Tracking
- `tct-tracking.js` captures UTM params, gclid, fbclid, referrer, landing page on first touch
- Stored in `sessionStorage` as `tct_attribution` (first-touch, don't overwrite)
- `getTctAttributionTags()` — returns GHL tag array like `['source-google', 'medium-cpc']`
- `getTctAttributionNotes()` — returns full attribution string for GHL contact notes
- Integrated into popup form, calculator.html, signup.html, and book.html

### Voice AI
- Agent ID: `695947c64b9ed67d8f1077ad`
- Agent Name: "The Call Taker - Demo Line"
- Business Name: "The Call Taker (Demo)"
- Welcome: "Hey, thanks for calling The Call Taker! This is a live AI demo. Tell me what kind of business you run and I will show you how I handle your calls."
- **UNIVERSAL DEMO:** Adapts to ANY industry — caller says "locked out" → locksmith mode, "AC broken" → HVAC mode, "need a dentist" → dental mode. After ~1 min pitches free 14-day pilot.
- Voice ID: `w9rPM8AIZle60Nbpw7nl` (current), Jessica backup: `lxYfHSkYm1EzQzGhdbfc`
- **Prompt:** Universal demo, ~263 words (v5), pain-first closer with revenue anchor + scarcity. Full text in `~/Desktop/voice-agent-speed-fix/industry-prompts/universal-demo.md`
- **Responsiveness:** 1.0 (max) — respond as fast as possible after caller stops
- **Mid-call actions:** NONE (removed Feb 27 — were adding 200-500ms latency per turn)
- **Knowledge base:** Removed (reduces latency)
- **After-call:** Extract name action still active. Call-end workflow `6e7084f1-a3f2-4ca7-95e8-59c7ba5b1526` fires post-call.
- **Speed fix (Feb 27):** Prompt 925→160 words (v3), responsiveness 0.8→1.0, greeting 16→10 words, removed mid-call data extraction actions + knowledge base. 7 Bland.ai test calls run. Anti-repeat + digit readback workarounds deployed. Full audit: `~/Desktop/voice-agent-speed-fix/CALL-AUDIT.md`
- **Pain-first closer (March 2):** v5 prompt (~263 words). Closer now simulates pain ("imagine nobody picked up — $300-500 job gone"), revenue anchor ("$2K-10K/mo in missed calls"), scarcity ("3 businesses this month"), price anchor ("$97/mo, less than one missed job"). Team detection section compressed to save words.
- **GHL latency:** Info collection turns: 2-4.5s. Complex turns: 5-13s. GHL has no model selection, no max_tokens, no response_length setting. All available levers maxed.
- **Demo line rule:** Demo line (615) 784-5747 = ALWAYS universal demo prompt. Client lines = industry-specific prompts. NEVER overwrite the demo line with a single-industry prompt.
- **Industry prompts (for clients):** Locksmith, HVAC, Water Damage — all in `~/Desktop/voice-agent-speed-fix/industry-prompts/`. Universal demo prompt also there.
- **Platform comparison:** Retell.ai recommended for voice layer (~600ms latency, 7.5x faster than GHL). Full analysis: `~/Desktop/voice-agent-speed-fix/PLATFORM-COMPARISON.md`
- **Retell agent:** Also updated to universal demo. Agent ID: `agent_5acbcae27d34f7f82f1355e546`, LLM: `llm_c1d92953d343725223ebc9ae02ec`. BLOCKED: needs payment card for phone number ($2/mo).
- **API:** PATCH `/voice-ai/agents/{id}?locationId=` (plural "agents"), GET `/voice-ai/agents?locationId=` to list
- PATCH endpoint needs `locationId` in query string, not body
- Demo breaks character after ~1 min to pitch The Call Taker and collect prospect info
- If asked about pricing: "$97/mo after-hours, $297/mo full 24/7, no contracts"
- **GHL bugs (workarounds deployed):** TTS repeat loop → "Never repeat yourself" instruction (Call 7: 0 repeats). Phone number glitches → digit readback instruction (Call 7: clean in 2s). Variable latency → GHL platform limit, no fix available.

### Monitoring & Alerting
- **Crash Monitor:** `ops/crash-monitor.py` — every 5 min, checks all launchd services, auto-restarts crashed ones, sends ntfy alert
- **Dashboard:** `~/Desktop/thecalltaker/dashboard/index.html` — open in browser, auto-refreshes every 5 min, includes conversion funnel + A/B test performance sections
- **Daily Reports:** `~/thecalltaker-ops/reports/{YYYY-MM-DD}.json` — generated 9pm nightly by `daily-report-engine.py`
- **Weekly Reports:** `~/thecalltaker-ops/reports/weekly-{YYYY-MM-DD}.json` — generated Sunday 9:30pm by `weekly-report-engine.py`
- **A/B Tracking:** `ops/ab-tracker-state.json` — per-variant sent/reply/demo counts, updated 8:30pm daily
- **Dashboard Data:** `ops/dashboard-api.py` generates `dashboard-data.json` every 5 min
- **Error Log:** `~/thecalltaker-ops/logs/errors.log` — all ERROR/CRITICAL from all engines
- **Combined Log:** `~/thecalltaker-ops/logs/all-engines.log` — everything from all engines

### Speed-to-Lead Alert System
- **Script:** `ops/speed-alert.py` — monitors GHL conversations every 2 minutes
- **launchd:** `com.thecalltaker.ops.speed-alert.plist` (every 120 seconds)
- **What it does:** Detects inbound replies, demo calls, hot signals; sends SMS to Wallace (+16156539004, GHL contact DtKLG28VzgUb6q3brILD) + ntfy war room backup
- **Hot keywords:** interested, pricing, demo, sign me up, ready, how much, schedule, etc.
- **Commands:** `watch` (continuous), `check` (single pass), `status`, `test`

### Demo Line Monitor (March 2, 2026)
- **Script:** `ops/demo-line-monitor.py` — 6 commands: pilot-text, call-track, summary, run, status, all
- **State:** `ops/demo-line-monitor-state.json`
- **launchd (3 services):**
  - `com.thecalltaker.demo.pilot-text` — every 5 min (catches PILOT texts)
  - `com.thecalltaker.demo.call-track` — every 15 min (tags calls by duration)
  - `com.thecalltaker.demo.summary` — 9:15pm daily (stats to ntfy SALES)
- **PILOT text trigger:** Detects "pilot", "interested", "yes", "sign me up", etc. → scarcity-aware auto-reply (counts down from 3 spots/month, resets monthly; spots=0 gets "making an exception" message) → tags `demo-to-pilot` + `hot-lead` → URGENT ntfy alert
- **Beta spots counter:** `beta_spots_remaining` (3/month), `beta_spots_month`, `beta_signups_this_month` in state. Resets on new month. Visible in `status` command.
- **Call duration tiers:** `demo-caller` (all), `engaged-demo` (60s+), `hot-demo` (120s+ → URGENT alert)
- **Tracking doc:** `~/Desktop/thecalltaker/demo-line/TRACKING-SETUP.md`
- **Works alongside:** demo-followup-engine (4-touch pain-first sequence), max (reply catching), notification-hub (routing), demo-qa (test calls)

### Demo Follow-Up Engine v2 — Pain-First (March 2, 2026)
- **Script:** `ops/demo-followup-engine.py` — 4 commands: scan, send, run, status
- **State:** `ops/demo-followup-state.json`
- **4-touch pain-first sequence:**
  - Touch 1 (10min): SMS pain hook — "that AI you just talked to? That's what your customers hear at 2am..."
  - Touch 2 (1hr): Email — "[Company] is losing $2K-$10K/month in missed calls" + scarcity (3 spots) + $97 anchor
  - Touch 3 (next morning 7-9am): SMS to prospect ("how many calls did [Company] miss last night?") + ntfy alert to Wallace with call script
  - Touch 4 (day 2): Hard scarcity SMS — "1 pilot spot left this week... After that it's $97/mo"
- **Industry-aware:** `get_job_word()` maps 17 industry tags to job words (service call, appointment, case, etc.)
- **Stores:** tags, industry per contact for personalized messaging
- **launchd:** `com.thecalltaker.demo.followup` (every 15 min, runs scan+send)

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
python3 ~/thecalltaker-ops/ops/funnel-engine.py status
python3 ~/thecalltaker-ops/pilot/pilot-onboarding-engine.py status
python3 ~/thecalltaker-ops/pilot/pilot-conversion-engine.py status
```

## State Files
Each engine saves state to JSON. State files are atomic-written (tempfile + os.replace) to prevent corruption.

- `max/max-state.json` — reply IDs, followup tracking, demo callers, weather sent, sentiment log
- `ben/ben-state.json` — lead scores, re-engaged contacts, ROI reports, territory analysis
- `sam/sam-state.json` — customer health scores, issues, checkins, referrals, NPS
- `donny/donny-state.json` — closing scores, close sequences, speed responses, objections
- `ops/blast-state.json` — email sent/bounced/skipped counts, daily limits
- `ops/funnel-state.json` — 7-touch funnel enrollments + trust sequence enrollments, steps completed, daily send counts
- `pilot/pilot-state.json` — pilot enrollments, slots, waitlist, conversion tracking
- `ops/try-funnel-state.json` — $97 cold sequence, nurture, upgrade enrollments
- `ops/agency-outreach-state.json` — agency cold email tracking, template A/B stats
- `ops/lead-recycler-state.json` — recycled contacts, rotation tracking, breakup counts
- `ops/contact-registry.json` — cross-engine contact coordination (who sent what, when)

## Contact Registry
Shared file at `ops/contact-registry.json`. All engines read/write through `tct_common.py` functions:
- `check_registry(contact_id, touch_type)` — returns `(ok, reason)` before contacting a lead
- `update_registry(contact_id, engine_name, touch_type)` — records a touch after sending
- Enforces: minimum 3-day gap between same-type touches, max 2 emails/week per lead
- File-locked (fcntl) to prevent race conditions between concurrent engines
- Touches older than 30 days auto-pruned

## Website Pages
**Deployment:** GitHub Pages via GitHub Actions. ONLY files inside `website/` get deployed.
**Deploy workflow:** `.github/workflows/deploy.yml` — triggers on push to `main` when `website/**` changes.
**Total: 82 pages live on thecalltaker.com** (as of Feb 25, 2026)

### Core Pages (in `website/`)
- `index.html` — homepage with industry selector + premium nav (glassmorphism, scroll spy, GSAP mobile menu) + cursor effects
- `signup.html` — 3-step purchase flow ($97/$297/$497)
- `calculator.html` — ROI calculator (lead capture + war room alert)
- `book.html` — demo booking (GHL calendar embed, ID: h4IlzccZ1m3JprEQqpMJ)
- `checkout.html` — $97/$297/$497 plan checkout (routes to /pilot/ until Stripe connected)
- `demo-showcase.html` — live demo line showcase
- `your-results.html` — 30-day results simulator (shareable URL)
- `your-audit.html` — personalized audit reports (noindex)
- `compare.html` — AI vs alternatives comparison
- `services.html` — feature overview
- `partners.html` — partner info
- `thank-you.html` — conversion confirmation (Google Ads tracking)
- `privacy.html` — privacy policy
- `terms.html` — terms of service
- `404.html` — custom error page
- `portal.html` — customer self-service (noindex)
- `blog.html` — blog index
- `industries.html` — industries hub

### Industry Pages (13) — `website/industries/`
HVAC, Roofing, Plumbing, Electrical, Dental, MedSpa, Legal, Property Mgmt, Veterinary, Locksmith, Garage Door, Towing, Funeral

### Blog Articles (39) — `website/blog/`
3 per industry: missed-call-cost, best-answering-service, + industry-specific topic

### $97 Try Funnel — `website/try-funnel/`
- `index.html` — landing page
- `checkout.html` — $97 Stripe checkout
- `upgrade.html` — upsell to $297/$497
- `try.html` (root) — redirect to try-funnel/

### Agency Program — `website/agency-program/`
- `agency.html` (root) — partner page with revenue calculator
- `pitch-deck.html` — slide presentation
- `pricing-sheet.html` — $47/client wholesale pricing
- `setup-guide.html` — agency onboarding

### Sales Toolkit (password: tctoolkit) — `website/toolkit/`
- `index.html`, `call-cheatsheet.html`, `objection-handler.html`, `case-studies.html`

### Case Studies (5) — `website/case-studies/`
- `index.html` — hub page with aggregate stats + card grid
- `palmetto-comfort.html` — HVAC, Charleston SC, 41%→0% missed, +$8,400/mo
- `arctic-air-pros.html` — HVAC, Phoenix AZ, +$14,200/mo, 29x ROI
- `reliable-rooter.html` — Plumbing, Tampa FL, solo plumber +72% revenue
- `precision-plumbing.html` — Plumbing, Atlanta GA, replaced $1,400 answering service
- `rapid-key-locksmith.html` — Locksmith, Nashville TN, +65% emergency revenue
- All CTAs → book.html (free pilot). Used in trust email sequence + outreach.

### Trust Email Sequence — `docs/trust-email-sequence.md`
- 4-email sequence for site visitors who didn't convert (48hr cadence)
- Email 1: Case study drop (industry-matched)
- Email 2: Demo video link
- Email 3: Personal note from Wallace
- Email 4: Last-chance pilot offer with expiry
- Trigger: `website-visitor` or `calculator-lead` tag + 48hr no conversion

### Demo Video Script — `sales-toolkit/demo-video-script.md`
- 3-minute Loom walkthrough: call demo line live → show GHL backend → numbers → close
- Pre-record checklist, word-for-word script, post-recording distribution plan

### Google Business Profile Guide — `docs/google-business-profile-guide.md`
- Full GBP setup, optimization, review collection strategy, citation building
- Review request templates for pilot users (SMS + email)
- Weekly Google Post content calendar
- Directory listing priority list (Yelp, BBB, Bing, Apple Maps, Clutch, G2)

### Internal (NOT deployed — local only)
- `dashboard/` — tool-costs, warroom, pipeline, morning-briefing, sitemap-visual
- `sales-toolkit/` — demo-video-script.md + duplicate of /toolkit/
- `reports/` — web-audit.html, replies report
- `docs/` — trust-email-sequence.md, google-business-profile-guide.md
- Root-level old industry pages — replaced by /industries/

## Pilot Program (14-Day Free Trial)
- **Directory:** `~/thecalltaker-ops/pilot/` (moved from Desktop Feb 27 — macOS TCC fix)
- **Max Slots:** 5 concurrent pilots
- **Onboarding Engine:** `pilot-onboarding-engine.py` — scans for `pilot-signup` tag, auto-onboards (welcome email/SMS, forwarding instructions, GHL tags, war room + William alerts)
- **Conversion Engine:** `pilot-conversion-engine.py` — Day 7 check-in, Day 10 ROI, Day 12 urgency, post-expiry Day 15/17/21
- **State:** `~/thecalltaker-ops/pilot/pilot-state.json` (shared by both engines, atomic writes)
- **Heartbeats:** `pilot-onboarding.heartbeat`, `pilot-conversion.heartbeat` (written each run)
- **Results Simulator:** `your-results.html` — 3-question form → personalized 30-day projection dashboard, shareable via URL hash
- **CTA Strategy:** All outreach engines updated from "buy at $X/mo" → "free 14-day pilot, no card, no risk"
- **launchd:** `com.thecalltaker.pilot.onboarding` (6x daily, runs scan+touchpoints+expire), `com.thecalltaker.pilot.conversion` (2x daily, runs check+post-expiry)
- **GHL Tags:** `pilot-signup` (trigger), `pilot-active` (during), `pilot-expired` / `pilot-converted` (after)

## Multi-Industry Outreach System (Feb 27 2026)
- **Target:** ANY service business that answers phones — 17 industries, 20 metros
- **Industries:** Locksmith, HVAC, Plumbing, Electrical, Roofing, Pest Control, Towing, Dental, Med Spa, Legal, Veterinary, Auto Repair, Cleaning, Property Mgmt, Water Damage, Landscaping, General Contractor
- **Target Metros:** Nashville, Memphis, Knoxville, Chattanooga, Atlanta, Birmingham, Louisville, Huntsville, Lexington, Jackson MS, Dallas, Houston, Phoenix, Tampa, Charlotte, Jacksonville, San Antonio, Indianapolis, Columbus OH, Kansas City
- **Lead List:** `~/Desktop/thecalltaker/leads/master-all-industries.csv` (600 leads), `hot-100.csv`, per-industry CSVs in `by-industry/`
- **Scoring:** 1-100 based on: small team (+20), no website (+15), high reviews (+15), high-value industry (+15), has email (+10), top 10 metro (+5)
- **GHL Import:** Top 100 imported, tagged `pilot-candidate` + industry tag, top 25 tagged `hot-lead`
- **Templates:** `~/Desktop/thecalltaker/outreach/universal/` — 3 emails, 2 SMS, 1 cold call script (all universal with [INDUSTRY] variable)
- **Industry Hooks:** `~/Desktop/thecalltaker/outreach/industry-hooks.md` — one-liner pain points per industry
- **Call Tracker:** `~/Desktop/thecalltaker/sales-toolkit/call-tracker-v2.html` — loads from hot-100.json, filter by industry, auto-populated scripts, outcome tracking
- **Engine Updates:** blast-engine.py + funnel-engine.py both updated to handle 19 industries (13 original + 6 new)
- **Background Scraper:** `multi-industry-lead-gen.py` runs in background to fill industry gaps; when done, re-run `lead-list-builder.py build` to update lists

## 72-Hour Revenue Strike Plan (March 2, 2026)
- **File:** `~/Desktop/thecalltaker/72-HOUR-STRIKE.md`
- Hour-by-hour 3-day battle plan: Day 1 blitz (50 calls), Day 2 convert (50 calls), Day 3 close (30 calls)
- 30-second cold call script, voicemail script, SMS follow-up copy
- KPI targets: 130 calls, 100 SMS, 50 emails, 8 demo calls, 3 PILOT texts, 1 paid
- Top 5 objection rebuttals, industry job value table, revenue anchor lines
- Uses same pain/scarcity messaging as Voice AI prompt + demo followup engine

## Known Issues / TODOs
1. **Stripe not connected** — needs parent/guardian (Wallace is 16). Setup guide sent via ntfy.
2. **stripe-webhook-handler.py** — signature verification is stubbed out (returns True). When Stripe is connected, implement HMAC-SHA256 verification.
3. **reply-monitor** service has exit code 1 — check `launchctl list | grep reply-monitor` and restart if needed.
4. **Gmail SMTP passwords** are in plaintext in `gmail-sender.py`. Move to environment variables when possible.
5. **Meta Ads** — Ad Account ID 25895456013410801, needs API token from developers.facebook.com.
6. **ColdDMs** — CANCELED ($174/mo, no API). Instagram DM targeting handled by dm-tracker script.

## Disabled Services
1. **[2026-03-02] com.thecalltaker.toolcosts — DISABLED.** Internal cost-tracking dashboard updater. Crashed in infinite loop due to macOS TCC blocking writes to `~/Desktop/thecalltaker/dashboard/tool-costs-data.json`. Not revenue-essential — just generates internal API cost reports. Disabled to stop crash-monitor churn. Fix later by changing OUTPUT_FILE to `~/thecalltaker-ops/`. Postmortem: `~/thecalltaker-ops/logs/crash-postmortem-toolcosts.md`

## Known Issues (Resolved)
1. **[2026-02-27] Pilot onboarding + conversion engines never ran from launchd** — Root cause: scripts were in `~/Desktop/` (macOS TCC-protected directory). Python couldn't even open the file. Fix: moved both scripts to `~/thecalltaker-ops/pilot/`, updated plists, added startup self-test + crash handler + heartbeat + null safety. Also fixed conversion plist passing nonexistent `run` command (changed to `check`). Crash-monitor upgraded with consecutive crash tracking + URGENT alerts for rapid crashes. Full postmortem: `~/thecalltaker-ops/logs/crash-postmortem-pilot-onboarding.md`

## Coordination Protocol

> **MANDATORY: Before starting any work session, read `war-room/task-board.md` and `war-room/handoff-log.md`. Before ending any work session, update both files.**

- **Task Board:** `~/Desktop/thecalltaker/war-room/task-board.md` — live task tracker with WALLACE/MILLS/SHARED columns
- **Handoff Log:** `~/Desktop/thecalltaker/war-room/handoff-log.md` — session-by-session changelog (what was done, what changed, what's next, blockers)
- **Rules:** `~/Desktop/thecalltaker/war-room/rules.md` — lane ownership, shared decisions, conflict resolution
- **Lane ownership:** Wallace = sales/outreach/content/ads/pricing. Mills = code/repos/voice agent/GHL/integrations. William = demos/Zoom calls.
- **Cross-lane work:** Log it on the task board FIRST. Emergency exceptions must be logged after.
- **Shared decisions:** Goes in SHARED section — no one moves forward until both agree.
- **Engine changes:** Log which file, what changed, and whether launchd was restarted.

## Team
- **Wallace Dobbs** — founder/CEO, builds everything, funds everything
- **William** (Wallace's brother) — demo closer, face on Zoom calls
- **Mills** — co-founder/partner, strategy, has GitHub access
- **Max** — 24/7 AI reply catcher + follow-up machine
- **Ben** — 24/7 AI intelligence engine
- **Sam** — 24/7 AI customer success
- **Donny** — 24/7 AI conversion closer

## Secret Shopper System (Feb 27, 2026)
- **Engine:** `~/thecalltaker-ops/secret-shopper.py` — precision daily shopper (30 calls/batch)
- **Commands:** `call`, `check`, `status`, `dashboard`
- **NOT the same as:** `secret-shopper-blitz.py` (mass 200-call campaigns) or `secret-shopper-list.py` (manual list)
- **Data flow:** CSV leads → score/filter → Bland.ai calls → check outcomes → generate HTML reports → SMS + email with report link → tag GHL → dashboard JSON
- **Lead sources:** `~/Desktop/thecalltaker/leads/hot-100.csv` (primary), `master-all-industries.csv` (fallback)
- **Reports:** `~/Desktop/thecalltaker/website/shopper-reports/{contact_id}.html` — branded proof reports (noindex)
- **Dashboard:** `~/Desktop/thecalltaker/dashboard/shopper-dashboard.html` — loads `shopper-dashboard-data.json`
- **Call Script:** `~/Desktop/thecalltaker/outreach/shopper-call-script.md` — Wallace's morning follow-up script
- **State:** `~/thecalltaker-ops/shopper-state.json`
- **Results CSV:** `~/thecalltaker-ops/shopper-results.csv`
- **launchd (4 services):**
  - `com.thecalltaker.shopper.evening` — call at 6pm daily
  - `com.thecalltaker.shopper.night` — call at 9:30pm daily
  - `com.thecalltaker.shopper.check` — check every 10 min
  - `com.thecalltaker.shopper.saturday` — call Sat 9am
- **GHL tags added:** `shopper-failed`, `hot-lead`, `shopper-called`, `shopper-{date}`
- **Exclusions:** Skips customer, active-client, pilot-active, donny-closing, do-not-contact, unsubscribed, shopper-called
- **Bland.ai 402:** Auto-stops + ntfy SYSTEM alert if balance depleted
- **19 industries supported** with per-industry scenarios and job values
