# The Call Taker — Project Context

## What This Is
AI receptionist service for HVAC companies. Answers every call 24/7 so they never lose a job to voicemail again.

## Current Priority: GET FIRST PAYING HVAC CLIENT

## Owner
Wallace Dobbs — wallacemdobbs@icloud.com

## Tech Stack
- **Website**: Static HTML/CSS/JS on GitHub Pages (~/Desktop/wallace-hvac/website/)
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
│   └── wallace-checklist.md — manual tasks only Wallace can do
├── website/ (GitHub Pages deployment — 2-page site, CNAME: thecalltaker.com)
│   ├── index.html — home + pricing + how-it-works (single scrolling page)
│   ├── demo.html — booking form + demo phone + GHL calendar embed
│   ├── admin-setup.html — internal GHL setup tool (NOT public)
│   ├── styles.css — shared design system (dark + green theme)
│   ├── script.js — shared interactions (reveals, FAQ, mobile nav)
│   ├── 404.html — custom error page
│   ├── CNAME — custom domain: thecalltaker.com
│   ├── favicon.svg — site icon
│   ├── robots.txt — search engine directives
│   ├── sitemap.xml — SEO sitemap (index + demo only)
│   ├── about.html — (DEPRECATED, unlinked, kept on disk)
│   ├── how-it-works.html — (DEPRECATED, content folded into index.html)
│   └── pricing.html — (DEPRECATED, content folded into index.html)
├── sales/
│   ├── cold-email-sequence.md — 3-email cold outreach
│   ├── cold-call-script.md — phone script + objection handling
│   ├── cold-dm-scripts.md — Instagram/Facebook/LinkedIn DM scripts
│   ├── facebook-ad-copy.md — Facebook/Instagram paid ad copy + targeting
│   ├── hvac-lead-list.md — 27 HVAC companies in Middle TN
│   ├── one-page-proposal.md — proposal template
│   ├── secret-shopper-template.md — voicemail detection tracking
│   ├── missed-call-audit-report.md — post-secret-shop report to send prospects
│   ├── demo-script.md — live demo call walkthrough
│   ├── short-form-video-scripts.md — 5 TikTok/Reels scripts (30-60s each)
│   ├── facebook-groups-guide.md — 20 HVAC Facebook groups + engagement strategy
│   ├── referral-partner-outreach-package.md — 10 partner types + commission structure
│   ├── sms-follow-up-sequences.md — 18 texts across 5 SMS sequences
│   ├── google-ads-campaign.md — 33 keywords, 5 ad groups, budget plan
│   ├── social-media-posts.md — 20 Instagram/Facebook posts with schedule
│   ├── objection-handling-playbook.md — 20 objections with exact responses
│   ├── classified-ads-local-platforms.md — Craigslist, Nextdoor, LinkedIn, etc.
│   ├── 2026-hvac-missed-call-report.md — free lead magnet report (downloadable)
│   ├── podcast-guest-pitch-kit.md — 15 podcasts + 3 pitch templates + media kit
│   ├── trade-show-battle-plan.md — 10 events + booth setup + follow-up system
│   └── competitive-intelligence-report.md — 9 competitors + battlecards + objection matrix
└── onboarding/
    ├── new-client-intake-form.md — questions for new HVAC clients
    ├── onboarding-steps.md — setup process day-by-day
    ├── welcome-email-sequence.md — 5-email client welcome series
    ├── client-agreement-template.md — service agreement/TOS
    └── customer-success-playbook.md — retention, churn prevention, referrals, upsell
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

## What's NOT Built Yet (Needs Wallace)
- ~~Custom domain~~ — DONE (thecalltaker.com connected)
- Stripe billing (not connected)
- Email template content (shells exist, need copy pasted in GHL UI)
- Business email address (optional — currently using wallacemdobbs@icloud.com)
- Social media profiles

## Design System (website/styles.css)
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
