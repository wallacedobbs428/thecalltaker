# The Call Taker — Project Context

## What This Is
AI receptionist service for HVAC companies. Answers every call 24/7 so they never lose a job to voicemail again.

## Current Priority: GET FIRST PAYING HVAC CLIENT

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
├── calculator.html — standalone missed call revenue calculator (4-step interactive, lead capture)
├── compare.html — comparison page: Call Taker vs voicemail vs answering vs receptionist
├── partners.html — partner/reseller program page with application form
├── privacy.html — Privacy policy (required for Facebook ads)
├── terms.html — Terms of service
├── thank-you.html — form submission confirmation (conversion tracking fires here)
├── admin-setup.html — internal GHL setup tool (NOT public)
├── styles.css — shared design system (dark + green theme)
├── script.js — shared interactions (reveals, FAQ, mobile nav)
├── 404.html — custom error page with nav + conversion CTAs
├── CNAME — custom domain: thecalltaker.com
├── favicon.svg — site icon
├── robots.txt — search engine directives (blocks admin-setup.html)
├── sitemap.xml — SEO sitemap (14 pages: index, demo, audit, blog, 2 articles, calculator, compare, partners, privacy, terms)
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

## A2P 10DLC Registration Status (as of Feb 17, 2026)
- **Brand status: APPROVED**
- **Campaign status: REJECTED** — re-submission in progress
- **Blocker:** GitHub Pages SSL cert not yet issued for thecalltaker.com — GHL compliance bot can't crawl the site over HTTPS, so all compliance checks fail
- **DNS:** Correct (4 A records pointing to GitHub IPs, www CNAME to wallacedobbs428.github.io)
- **SSL fix:** Waiting for GitHub to issue cert — check Settings > Pages > "Enforce HTTPS" becoming clickable
- **SMS consent added to:** demo.html, audit.html, privacy.html (Section 2a), terms.html (Section 4a)
- **Checkbox must NOT be required** — A2P rules say consent checkbox can't be mandatory
- **Once SSL is fixed:** Re-submit campaign with `https://thecalltaker.com/demo.html` as opt-in URL
- **CRITICAL:** All SMS outreach is FAILING until campaign is approved — carriers are dropping messages

## What's NOT Built Yet (Needs Wallace)
- ~~Custom domain~~ — DONE (thecalltaker.com connected)
- A2P 10DLC campaign approval (blocked by SSL cert — see above)
- Stripe billing (not connected)
- Email template content (shells exist, need copy pasted in GHL UI)
- Business email address (optional — currently using wallacemdobbs@icloud.com)
- Social media profiles

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
