# The Call Taker — Project Context

## What This Is
AI receptionist for service businesses across 8 industries: HVAC, Plumbing, Electrical, Roofing, Dental, Med Spa, Legal, Property Management. Answers every call 24/7 so they never lose a customer to voicemail again.

## Current Priority: $100K BY MAY 2026

**Pricing (2 tiers):**
| | Starter | Pro |
|---|---|---|
| Price | $497/mo | $997/mo |
| Setup | $500 one-time | $500 one-time |
| Trial | 7 days free | 7 days free |
| For | HVAC, Plumbing, Electrical | Dental, Legal, Roofing, MedSpa, Property Mgmt |

**"Founding 20":** First 20 customers locked in at launch pricing for life.
**Target:** 45 clients × ~$700 avg MRR = ~$33K MRR by May 2026
**Channels:** Bland.ai cold calls (20/day), Ben SMS (30/day), cold email (blast + Lemlist), secret shopper (15/evening), daily human call sheet (15/morning), Instagram DMs

## Wallace Shorthand
- **ss** = screenshot or screenshots (context-dependent) — check `/Users/moneymaker99/Screenshots/` for most recent `.png` files (NOT Desktop)

## Team Roster
| Member | Role | What They Do |
|--------|------|-------------|
| **Wallace** | Founder / CEO / Builder | Builds the tech, funds ALL subscriptions, primary operator, runs the business |
| **William** | Demo Closer / Brother | Zoom demo calls, cold calls from daily call sheet, presents to prospects |
| **Mills** | Co-Founder / Partner / Caller | GitHub access, strategy, makes cold calls from daily call sheet |
| **Claude** | Chief Builder | Builds everything — website, agents, strategy, content, integrations |
| **Max** | 24/7 Sales Engine | Cold emails, follow-ups, reply monitor, pipeline mgmt, daily reports |
| **Ben** | 24/7 Senior Closer | ROI angles, re-engagement, lead scoring, SMS, morning/evening briefings |
| **Sam** | 24/7 Customer Success | Support monitor, health scoring, milestone check-ins, referral requests |

## Subscriptions (Wallace pays all)
- GoHighLevel
- Instantly.ai (Free Trial)
- GitHub (free)
- Claude Code
- Domain (thecalltaker.com)
- Google Ads ($6/day)
- ColdDMs Scale plan ($174/mo)
- Lemlist

## Owner
Wallace Dobbs — wallacemdobbs@icloud.com

## Tech Stack
- **Website**: Static HTML/CSS/JS on GitHub Pages (~/Desktop/wallace-hvac/ — files are in project root, NOT a website/ subdirectory)
- **CRM/Backend**: GoHighLevel (API key in ~/Desktop/thecalltaker/.env)
- **Billing**: Stripe (NOT YET CONNECTED)
- **Website URL**: https://thecalltaker.com/ (GitHub Pages via wallacedobbs428/thecalltaker repo)
- **GitHub Repo**: github.com/wallacedobbs428/thecalltaker (shared — both Mills + Wallace have push access)

## GoHighLevel Connection
- **API Key**: pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35
- **Location ID**: tQb9YmrGDrdVUJYPKrsY
- **Base URL**: https://services.leadconnectorhq.com
- **API Version Header**: Version: 2021-07-28
- **Phone**: +16156539004 (SMS) / +16157845747 (Voice AI demo line)
- **Demo Calendar ID**: h4IlzccZ1m3JprEQqpMJ
- **Staff User**: wallace@thecalltaker.com / CallTaker2026! (user ID: g4Ocu4qnhv7O8CrqpDTC)

## GHL API Notes
- Tags: POST/GET via /locations/{locationId}/tags
- Custom Fields: POST/GET via /locations/{locationId}/customFields
- Contacts: CRUD via /contacts/
- Calendars: CRUD via /calendars/
- Pipelines: GET via /opportunities/pipelines (CREATE is scope-restricted)
- Workflows: GET only via /workflows/
- Email Templates: POST via /emails/builder (creates empty shells, content must be added in GHL UI)
- Funnels/Pages: READ-ONLY — cannot create or edit pages via API

## File Structure
```
~/Desktop/wallace-hvac/
├── CLAUDE.md (this file)
├── docs/
│   ├── audit-report.md — full project audit
│   ├── claude-did-this.md — everything built in GHL via API
│   ├── google-business-profile-setup.md — step-by-step GBP setup guide
│   ├── stripe-setup-guide.md — Stripe + GHL payment setup
│   ├── ghl-email-templates.md — content for 10 GHL email template shells
│   ├── wallace-checklist.md — manual tasks only Wallace can do
│   ├── first-week-action-plan.md — day-by-day plan for week 1 outreach
│   └── daily-activity-tracker.md — printable daily outreach tracker
├── index.html — home + pricing + how-it-works + before/after + case study + founder story + FAQ
├── demo.html — booking form + demo phone + GHL calendar embed
├── audit.html — Free Missed Call Audit lead capture page
├── blog.html — blog index page with article cards + newsletter signup
├── blog-missed-call-cost.html — SEO article: cost of missed calls (with newsletter)
├── blog-ai-vs-answering.html — SEO article: AI vs answering services (with newsletter)
├── calculator.html — standalone missed call revenue calculator (4-step interactive, lead capture + war room alert)
├── signup.html — self-service purchase flow (3-step: business info → plan → confirm, creates GHL contact + war room alert)
├── your-audit.html — personalized missed call audit report (URL-parameter driven, noindex)
├── industries.html — industries page: HVAC, plumbing, electrical, roofing, pest control, garage door/locksmith
├── compare.html — comparison page: Call Taker vs voicemail vs answering vs receptionist
├── partners.html — partner/reseller program page with application form
├── privacy.html — Privacy policy (required for Facebook ads)
├── terms.html — Terms of service
├── thank-you.html — form submission confirmation (conversion tracking fires here)
├── admin-setup.html — internal GHL setup tool (NOT public)
├── shopper-report.html — INTERNAL: Secret Shopper Report Generator (noindex) — fill out after a test call, generates a print-ready PDF audit report to send the prospect
├── styles.css — shared design system (dark + green theme)
├── script.js — shared interactions (reveals, FAQ, mobile nav)
├── 404.html — custom error page with nav + conversion CTAs
├── CNAME — custom domain: thecalltaker.com
├── favicon.svg — site icon
├── portal.html — customer self-service portal (noindex, blocked by robots.txt)
├── robots.txt — search engine directives (blocks admin-setup.html, shopper-report.html, portal.html)
├── sitemap.xml — SEO sitemap (15 pages: index, demo, audit, blog, 2 articles, calculator, compare, industries, partners, privacy, terms)
├── sales/ (70+ files — cold outreach, content, partnerships, ads, campaigns)
│   ├── cold-email-sequence.md — 3-email cold outreach (Instantly)
│   ├── cold-email-sequence-extended.md — Emails 4-7 (free audit, social proof, video, breakup)
│   ├── cold-call-script.md — phone script + objection handling
│   ├── cold-dm-scripts.md — Instagram/Facebook/LinkedIn DM scripts
│   ├── facebook-ad-copy.md — Facebook/Instagram paid ad copy + targeting
│   ├── hvac-lead-list.md — 27 HVAC companies in Middle TN
│   ├── one-page-proposal.md — proposal template
│   ├── one-pager-sales-sheet.md — printable sales sheet
│   ├── secret-shopper-template.md — voicemail detection tracking
│   ├── missed-call-audit-report.md — post-secret-shop report
│   ├── audit-report-template.md — detailed audit report template
│   ├── demo-script.md — live demo call walkthrough
│   ├── short-form-video-scripts.md — 5 TikTok/Reels scripts v1
│   ├── instagram-reels-scripts-v2.md — 5 new Reels/TikTok scripts v2
│   ├── facebook-groups-guide.md — 20 HVAC Facebook groups + strategy
│   ├── facebook-group-posts-ready.md — 10 ready-to-post group posts
│   ├── referral-partner-outreach-package.md — 10 partner types + commission
│   ├── plumber-partnership-pitch.md — plumber referral pitch
│   ├── electrician-partnership-pitch.md — electrician referral pitch
│   ├── sms-follow-up-sequences.md — 18 texts across 5 SMS sequences
│   ├── sms-cold-outreach.md — cold text messages + follow-ups
│   ├── post-audit-sms-sequence.md — 5-text post-audit SMS sequence
│   ├── google-ads-campaign.md — 33 keywords, 5 ad groups
│   ├── google-business-posts.md — 10 GBP posts
│   ├── social-media-posts.md — 20 posts with schedule
│   ├── twitter-content-calendar.md — 20 tweets across 4 weeks
│   ├── objection-handling-playbook.md — 20 objections with responses
│   ├── classified-ads-local-platforms.md — Craigslist, Nextdoor, etc.
│   ├── craigslist-ads-ready.md — 3 ready-to-post ads
│   ├── nextdoor-posts.md — 5 Nextdoor templates
│   ├── linkedin-outreach.md — full LinkedIn playbook
│   ├── loom-video-script.md — personalized video outreach (3 versions)
│   ├── voicemail-drop-scripts.md — 5 voicemail scripts
│   ├── email-signature.md — full/short/HTML signature versions
│   ├── warm-intro-templates.md — 3 warm intro request emails
│   ├── re-engagement-email.md — 2 variations for cold leads
│   ├── competitor-comparison-chart.md — vs Ruby, Smith.ai, etc.
│   ├── case-study-template.md — hypothetical case study
│   ├── checklist-phone-system-audit.md — 10-point self-audit checklist
│   ├── blog-ai-vs-answering-services.md — SEO blog post
│   ├── blog-missed-call-cost.md — SEO blog post
│   ├── 2026-hvac-missed-call-report.md — lead magnet report
│   ├── podcast-guest-pitch-kit.md — 15 podcasts + pitch templates
│   ├── trade-show-battle-plan.md — 10 events + booth setup
│   ├── competitive-intelligence-report.md — 9 competitors + battlecards
│   ├── sales-cheat-sheet.md — one-page reference card for live calls
│   ├── client-referral-program.md — client referral program with commission structure
│   ├── agency-reseller-program.md — white-label reseller program for agencies
│   ├── multi-trade-expansion-kit.md — expansion to plumbing, electrical, roofing
│   ├── spring-summer-campaign-kit.md — spring/summer AC season campaign
│   ├── premium-growth-package.md — $797/mo done-for-you marketing upsell
│   ├── webinar-workshop-kit.md — free webinar/workshop script for HVAC owners
│   ├── retargeting-campaign.md — retargeting ad copy and email sequences
│   ├── youtube-video-scripts.md — YouTube SEO long-form video scripts
│   ├── supplier-distributor-partnership.md — HVAC supply house partnership kit
│   ├── newsletter-strategy.md — 12-issue HVAC Growth Report newsletter plan
│   ├── missed-call-calculator-strategy.md — calculator lead magnet strategy
│   ├── direct-response-sales-letter.md — long-form AIDA sales letter
│   ├── roi-guarantee-offer.md — 30-day money-back ROI guarantee strategy
│   ├── storm-season-blitz-campaign.md — storm season marketing campaign
│   └── competitor-secret-shopper-report.md — competitor phone audit report template
├── docs/
│   ├── audit-report.md — full project audit
│   ├── claude-did-this.md — everything built in GHL via API
│   ├── google-business-profile-setup.md — step-by-step GBP setup guide
│   ├── stripe-setup-guide.md — Stripe + GHL payment setup
│   ├── ghl-email-templates.md — content for 10 GHL email template shells
│   ├── wallace-checklist.md — manual tasks only Wallace can do
│   ├── first-week-action-plan.md — day-by-day plan for week 1 outreach
│   ├── daily-activity-tracker.md — printable daily outreach tracker
│   └── weekly-outreach-playbook.md — 90-day week-by-week outreach playbook
├── sam/ (Sam — customer success engine)
│   ├── sam-engine.py — Python3 customer success engine (6 commands)
│   ├── install-sam.sh — launchd installer (5 services)
│   ├── uninstall-sam.sh — stops all Sam services
│   ├── sam-state.json — tracks customer health, checkins, referrals
│   └── sam-log.txt — full activity log
└── onboarding/ (11 files — client lifecycle management)
    ├── new-client-intake-form.md — questions for new clients
    ├── onboarding-steps.md — setup process day-by-day
    ├── welcome-email-sequence.md — 5-email welcome series
    ├── client-agreement-template.md — service agreement/TOS
    ├── customer-success-playbook.md — retention + churn prevention
    ├── kickoff-call-script.md — first call with paying clients
    ├── 30-day-checkin-email.md — 30-day check-in template
    ├── monthly-report-template.md — performance report template
    ├── upsell-scripts.md — scripts for all 4 add-ons
    ├── referral-request-email.md — 3 referral request versions
    └── cancellation-save-script.md — 6 cancellation save scenarios
```

## What's Built in GHL (via API)
- 11 tags for sales pipeline tracking
- 6 custom fields for prospect data
- 10 email template shells (need content added in GHL UI)
- 1 demo booking calendar (round-robin, Mon-Fri 9-5, Sat 10-2 CST)
- 2 pipelines (Marketing + New Leads HVAC)
- 7 active workflows + 3 inactive
- AI voice agent on +16157845747 (HVAC receptionist prompt configured)
- Staff user created for calendar assignment
- Demo form wired to create contacts with prospect + demo-booked tags

## A2P 10DLC Registration Status (as of Feb 22, 2026)
- **Brand status: APPROVED**
- **Campaign status: APPROVED** — SMS sending fully operational
- **SSL:** LIVE (Let's Encrypt, expires May 18 2026)
- **SMS consent on:** demo.html, audit.html, privacy.html (Section 2a), terms.html (Section 4a)

## Max v3 — Reply Catcher + Follow-Up Machine
- **Location:** `max/` directory
- **Engine:** `max/max-engine.py` (Python3, zero dependencies)
- **Installer:** `bash max/install-max.sh` (4 launchd services)
- **Uninstaller:** `bash max/uninstall-max.sh`
- **State:** `max/max-state.json` (tracks replies, demo callers, secret shopper, weather emails)
- **Logs:** `max/max-log.txt`
- **What changed in v3:** Cold outreach REMOVED (handled by Instantly + blast scripts). Max now focuses on catching replies and converting warm leads.
- **Schedule (4 services):**
  - Reply monitor: every 30 min (replies + demo line calls + secret shopper triggers + weather emails)
  - Warm follow-ups: daily at 9am (3-round personalized sequence for leads who replied)
  - Pipeline: daily at midnight (flags engaged leads for stage changes)
  - Daily report: daily at 8pm (sends engagement summary via ntfy)
- **Key features:**
  - Demo line call detection — immediate follow-up email + URGENT war room alert
  - Secret shopper auto-trigger — sends "I called your business" email when lead tagged `voicemail-confirmed`
  - Weather-triggered emails — sends urgency emails to leads in cities with extreme weather (max 5/day, 14-day cooldown per contact)
  - Warm follow-up sequence — Day 2, Day 5, Day 8 personalized emails with seasonal urgency
  - Seasonal angles — auto-adjusts messaging for winter/spring/summer/fall
- **Alerts:** War room (tct-warroom-Kx7mN9pQ) for replies + demo calls + engaged leads; ops (tct-xK9mW4vR7pLd) for daily reports
- **Status:** `python3 max/max-engine.py status`

## Ben — 24/7 Senior Sales Closer
- **Location:** `ben/` directory
- **Engine:** `ben/ben-engine.py` (Python3, zero dependencies)
- **Installer:** `bash ben/install-ben.sh`
- **Uninstaller:** `bash ben/uninstall-ben.sh`
- **How Ben differs from Max:**
  - Different email angles: ROI math, competitor pressure, after-hours emergencies, seasonal urgency
  - Coordinates with Max — reads Max's state file, never emails the same lead Max just emailed
  - Re-engages leads Max gave up on (3 follow-ups, no response) with fresh angles
  - Sends SMS when A2P approves (auto-detects by trying + stopping if it fails)
  - Scores all leads 1-10 and ntfy-alerts hot leads (8+) for Wallace to call
  - Sends morning briefing (7am) and evening summary (9pm) to ntfy
- **Schedule:**
  - Morning briefing: 7:00 AM (pipeline status + today's plan)
  - Cold outreach: 11:00 AM (ROI/competition emails, 15/day max)
  - SMS blasts: 1:00 PM (when A2P approves, 15/day max)
  - Re-engagement: 2:00 PM (fresh angles for Max's cold leads, 10/day max)
  - Lead scoring: 3:00 PM (scores all leads, flags hot ones)
  - Evening summary: 9:00 PM (combined team stats + tomorrow's plan)

## Sam — 24/7 Customer Success Team Member
- **Location:** `sam/` directory
- **Engine:** `sam/sam-engine.py` (Python3, zero dependencies)
- **Installer:** `bash sam/install-sam.sh`
- **Uninstaller:** `bash sam/uninstall-sam.sh`
- **How Sam differs from Max/Ben:**
  - Sam only operates on contacts tagged "customer" or "active-client"
  - Max/Ben only operate on non-customer contacts (leads)
  - Sam reads Max + Ben state files (read-only) for team context
  - Built-in knowledge base with auto-responses for common issues
  - Critical keyword detection (cancel, refund, lawyer, BBB) triggers IMMEDIATE war room alerts
  - Health scoring 1-10 with at-risk flagging
  - Milestone check-ins at day 3, 7, 14, 30, then monthly
  - Referral flow: Sam detects trigger → alerts Wallace with call script → fallback email after 48h
  - Referral triggers: 30-day mark, post-issue-resolution, high health score (min 45 days between asks)
- **Schedule:**
  - Support monitor: every 15 min (scans customer conversations, auto-responds)
  - Health scoring: 6:00 AM (scores all customers, flags at-risk to war room)
  - Milestone check-ins: 8:00 AM (day 3/7/14/30 + monthly emails)
  - Referral requests: daily 11:00 AM (alerts Wallace to call, email fallback after 48h)
  - Daily report: 7:00 PM (customer health summary to ntfy)
- **Status:** `python3 sam/sam-engine.py status`

## Team Schedule (no conflicts)
```
  Every 10m  — DONNY: Speed-to-lead + objection handling
  Every 15m  — SAM: Support monitor + auto-respond
  Every 30m  — MAX: Reply monitor
  Every 2hr  — DONNY: Lead scoring (0-100)
  6:00 AM    — SAM: Health scoring
  7:00 AM    — BEN: Morning briefing
  7:30 AM    — MAX: Digest / DONNY: Funnel + hotlist
  8:00 AM    — SAM: Milestone check-ins
  9:00 AM    — MAX: Follow-ups
  10:30 AM   — DONNY: Close + trial sequences
  11:00 AM   — BEN: Outreach / SAM: Referral check / MAX: Seasonal
  12:30 PM   — DONNY: Urgency messages
  1:00 PM    — BEN: SMS
  2:00 PM    — BEN: Re-engagement / MAX: Reactivate
  2:30 PM    — DONNY: Recover lost leads
  3:00 PM    — BEN: Lead scoring
  7:00 PM    — SAM: Daily report
  8:00 PM    — MAX: Daily report
  8:30 PM    — DONNY: Revenue report
  9:00 PM    — BEN: Evening summary
  9:30 PM    — DONNY: Win report
  Midnight   — MAX: Pipeline cleanup
  Mon 10AM   — MAX: Win-back campaign
```

## Instantly.ai
- **Plan:** Free Trial (24/250 contacts uploaded, no API access)
- **API:** Locked behind Hyper Growth paid plan — cannot automate via API
- **Workaround:** Wallace uses Instantly UI manually; Max handles outreach via GHL email API instead
- **4 sending accounts** on skylfinder.com domain (warming up)

## $100K Sprint Infrastructure (thecalltaker-ops/)
- **Cold Caller:** `ops/cold-caller.py` — Bland.ai outbound, 20 cold calls/day + 15 secret shopper/evening
- **Daily Call Sheet:** `ops/daily-call-sheet.py` — 15 scored leads + scripts to ntfy at 8am daily
- **Blast Engine:** `ops/blast-engine.py` — unified email sender, warmup ramp 20→200/day, A/B testing 3 templates
- **Partner Outreach:** `ops/partner-outreach.py` — 240 agencies across 8 industries, 20/day at 11am
- **Revenue Tracker:** `ops/revenue-tracker.py` — MRR tracking toward $33K goal, 7pm daily report
- **Stripe Webhook:** `ops/stripe-webhook-handler.py` — localhost:8787, auto-tags customers on payment
- **Secret Shopper List:** `ops/secret-shopper-list.py` — 15 priority businesses to call nightly at 6pm
- **Google Maps Scraper:** `ops/google-maps-scraper.py` — Bing + DDG scraper, 200+ US cities
- **Email Domain:** wallace@mail.thecalltaker.com (SPF + DMARC verified, GHL dedicated sending)
- **Conversion Funnel:** cold email → personalized audit page → signup page → GHL contact + war room alert

## Ads & Tracking
- **Google Ads:** Campaign #1 live, $6/day budget, Performance Max, pending policy review
- **Google Ads Tag:** AW-17970510102 (installed on all 26 public HTML pages)
- **Google Ads Account:** Customer ID visible in ads.google.com dashboard
- **Meta/Facebook Ads:** Ad Account ID: 25895456013410801 (Business: "The Call Taker")
- **Meta Business Suite:** business.facebook.com (logged in as Colin Clorp / Mills)
- **Meta API:** Need access token from developers.facebook.com (not yet created)
- **Conversion tracking:** thank-you.html is the conversion URL for both Google + Meta

## Donny — 24/7 Conversion Closer
- **Location:** `donny/` directory
- **Engine:** `donny/donny-engine.py` (Python3, zero dependencies)
- **Installer:** `bash donny/install-donny.sh`
- **8 launchd services:** speed+objection (10min), score (2hr), funnel+hotlist (7:30am), close+trial (10:30am), urgency (12:30pm), recover (2:30pm), revenue (8:30pm), report+win (9:30pm)
- **Commands:** score, speed, objection, hotlist, close, trial, urgency, recover, funnel, win, revenue, report, status, all
- **0-100 closing score** combining ALL engine signals (behavioral + intelligence + recency)
- **Speed-to-lead:** detects hot signals every 10 min and responds immediately
- Tags contacts `donny-closing` when in active close sequence
- Reads ALL engine state files (max, ben, sam, blast, rescue, partner, drip, onboarding)

## Platforms & API Keys
- **Apollo.io:** API key dALEloy-0-6gg7abTMfIZw (free plan — search/enrichment API blocked, use UI only)
- **Clay:** API key 92b80eb729dc2be9cbf2 (no public REST API — works through UI/webhooks only)
- **Bardeen:** Chrome extension installed (browser automation)
- **n8n:** Self-hosted at localhost:5678, launchd service running
- **Lemlist:** Active account (email sequences)
- **ColdDMs:** Scale plan ($174/mo), NO API — manual only

## What's NOT Built Yet (Needs Wallace)
- ~~Custom domain~~ — DONE (thecalltaker.com connected)
- ~~A2P 10DLC~~ — APPROVED (SMS sending works)
- ~~SSL~~ — LIVE (Let's Encrypt, expires May 18 2026)
- ~~Google Ads~~ — LIVE ($6/day, Performance Max campaign)
- Meta/Facebook Ads API token (need to create app at developers.facebook.com)
- Stripe billing (not connected — needs parent/guardian for Stripe account, setup guide sent via ntfy)
- Email template content (shells exist, need copy pasted in GHL UI)
- Social media profiles

## Revenue Split — Wallace & Mills Partnership

**Context:** Wallace funds ALL subscriptions (~$174/mo+), originated the idea, builds the tech, runs sales, and is the face of the brand. Mills is co-founder with GitHub access and strategy input.

**Recommended Structure:**
1. **Subscription costs come off the top first** — Wallace gets reimbursed for all tool costs before any split
2. **Profit split: 75/25 (Wallace/Mills)** — reflects who's funding, building, and selling
3. **Alternative: 70/30** — if Mills takes on more active work (outreach, content, etc.)

**Example at 5 clients ($2,485/mo revenue):**
- $174 costs off the top = $2,311 profit
- 75/25: Wallace $1,733 / Mills $578
- 70/30: Wallace $1,618 / Mills $693

**Important:** Agree on the split BEFORE the first client pays. Easier to negotiate when there's no money on the table.

**3-way split (Wallace / William / Mills):** When Wallace is ready, Claude will scan all project data — funding records, build contributions, sales activity, hours invested, risk taken — to produce a data-backed revenue split recommendation across all 3 members. NOT active yet — Wallace will trigger this when the time is right.

**Age note:** Both Wallace and Mills are 16. Stripe account requires a parent/guardian (18+ requirement).

## Design System (styles.css)
- Background: #0a0f1a (near-black navy)
- Card bg: #111827 / Elevated: #1a2332
- Primary accent: #10b981 (emerald green)
- Light accent: #34d399 (hover/glow green)
- Text: #ffffff (headings), #94a3b8 (body), #64748b (muted)
- Font: Inter (Google Fonts), 17px base
- Mobile-first responsive
- Subtle scroll reveal animations (fade-in, 16px translateY)
- Apple/Stripe/Linear inspired — clean, premium, lots of whitespace

## GHL Embeds on Website
- demo.html has a working GHL calendar booking iframe (calendar ID: h4IlzccZ1m3JprEQqpMJ)
- demo.html form submits via GHL widget endpoint (API key removed from client-side code)
- Demo phone number: (615) 784-5747
