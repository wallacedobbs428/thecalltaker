---
name: ads
description: Paid advertising strategy, auditing, creative development, budget planning, and competitor analysis for Meta (Facebook/Instagram) and Google Ads. Use when the user mentions ads, advertising, campaigns, ad creative, ad budget, ROAS, CPL, Meta Ads, Facebook Ads, Google Ads, or ad auditing.
---

# Ads Command Center — The Call Taker

Paid advertising skill for AI Receptionist SaaS ($97/$497/$997/mo). Business: The Call Taker — AI receptionist for service businesses. Demo line: (615) 784-5747. Founded by Wallace Dobbs.

## Business Context

- **Product:** AI receptionist that answers calls 24/7 for service businesses
- **Pricing:** $97/mo (After-Hours Starter), $497/mo (Business Pro), $997/mo (Enterprise)
- **Free trial:** 14-day pilot, no card required
- **Target industries:** HVAC, Plumbing, Locksmith, Electrical, Roofing, Dental, Legal, Med Spa, Towing, Pest Control, Veterinary, Property Management, Auto Repair
- **Target metros:** Nashville, Memphis, Atlanta, Dallas, Houston, Phoenix, Tampa, Charlotte + 48 more
- **Meta Ad Account ID:** 25895456013410801
- **Key conversion actions:** Pilot signup, demo call (615) 784-5747, calculator lead, book demo
- **Landing pages:** thecalltaker.com/pilot/, thecalltaker.com/demo/, thecalltaker.com/calculator.html, thecalltaker.com/book.html
- **Video ads ready:** "The $300 Ghost" campaign — 30s + 15s cuts in 9:16, 4:5, 1:1 formats (video-ad/out/)
- **Pain points to target:** Missed calls = lost revenue ($300-$500/missed job), after-hours coverage, no voicemail, slow response time
- **Proof points:** 24/7 coverage, books appointments, texts details, qualifies leads, $97/mo < cost of 1 missed call
- **Voice AI character:** GIDEON (never say "Jessica" or "the AI")

## Commands

When the user runs `/ads`, parse the subcommand from their input. Supported subcommands:

### `/ads audit`
Run a full paid advertising account audit. Ask which platform (Meta or Google), then systematically check:

**Account Structure:**
- Campaign naming conventions and organization
- Ad set / ad group structure (by industry? by metro? by funnel stage?)
- Budget allocation across campaigns
- Bidding strategy appropriateness

**Tracking & Attribution:**
- Meta Pixel / Google Tag installed and firing correctly
- Conversion events configured (Lead, Purchase, ViewContent, InitiateCheckout)
- UTM parameters on all ad URLs
- Attribution window settings
- tct-tracking.js integration with ad platforms

**Targeting:**
- Audience definitions (custom, lookalike, interest-based)
- Geographic targeting (metro-level for service businesses)
- Exclusions (existing customers, employees, irrelevant demos)
- Frequency caps

**Creative:**
- Ad format mix (video, image, carousel)
- Hook variety and testing
- Copy length and CTA clarity
- Mobile optimization
- Landing page alignment

**Performance:**
- CPL (cost per lead) by campaign
- ROAS if purchase tracking exists
- CTR benchmarks (>1% for cold, >3% for retarget)
- Frequency (watch for ad fatigue >3.0)
- Relevance/quality scores

Output a scored audit report (A/B/C/F per category) with specific fix recommendations prioritized by impact.

### `/ads meta`
Meta (Facebook/Instagram) specific campaign strategy and optimization:

- Campaign structure recommendation (CBO vs ABO)
- Advantage+ vs manual placement analysis
- Audience strategy: broad vs stacked interests vs lookalikes
- Creative testing framework (hook variants, format testing)
- Retargeting funnel setup (website visitors, video viewers, engagers)
- Budget recommendations based on market size and CPL targets
- Scaling playbook (when to increase budget, duplicate, or restructure)
- iOS 14.5+ considerations and Conversions API setup
- Advantage+ Shopping campaigns for service businesses

When asked, generate specific campaign blueprints with:
- Campaign objective
- Budget (daily/lifetime)
- Audience definition
- Ad creative specs
- Landing page URL
- Expected CPL range

### `/ads google`
Google Ads strategy and setup guidance:

- Search campaign structure (branded, competitor, service keywords)
- Keyword research by industry and metro
- Negative keyword lists
- Ad copy templates (RSAs with 15 headlines, 4 descriptions)
- Extensions (sitelinks, callouts, structured snippets, call)
- Local Services Ads (LSA) strategy for service businesses
- Performance Max campaign considerations
- Landing page optimization for Quality Score
- Budget allocation: Search vs Display vs YouTube vs PMax

### `/ads creative`
Ad creative development and testing:

- Generate ad copy variants (primary text, headline, description)
- Video ad scripts (hook + pain + proof + CTA format)
- Image ad concepts and specs
- Carousel ad storylines
- A/B test plans (what to test, how many variants, when to call a winner)
- Hook bank: 10+ hooks per industry vertical
- UGC-style script templates
- Before/after ad concepts

**Creative framework for The Call Taker:**
- Hook: Pain point or curiosity gap (missed call scenario)
- Agitate: Revenue loss, competitor advantage, frustrated customers
- Solution: GIDEON answers 24/7, books appointments, texts details
- Proof: Specific numbers ($300-500/missed call, 24/7 coverage, $97/mo)
- CTA: "Start your free 14-day pilot" or "Call our demo line"

**The $300 Ghost campaign assets (already rendered):**
- ghost-30s-reel.mp4, ghost-30s-feed.mp4, ghost-30s-square.mp4
- ghost-15s-reel.mp4, ghost-15s-feed.mp4, ghost-15s-square.mp4
- Launch protocol: 72-HOUR-LAUNCH-PROTOCOL.md
- Publish playbook: PUBLISH-PLAYBOOK.md

### `/ads budget`
Budget allocation and scaling recommendations:

- Monthly budget planning by platform
- CPL targets by industry ($15-40 for service businesses)
- ROAS modeling (LTV of $97/mo x avg 8mo retention = $776 LTV)
- Budget splits: prospecting vs retargeting (80/20 rule)
- Scaling triggers (when CPL < target for 3+ days, scale 20%)
- Kill triggers (when CPL > 2x target for 3+ days, pause)
- Daily budget minimums per campaign type
- Seasonal adjustments (HVAC summer/winter, tax season for legal)
- Cash flow considerations (Wallace is bootstrapped, every dollar matters)

**Default assumptions:**
- Target CPL: $20-30 for pilot signups
- Monthly budget range: $500-2000 (early stage)
- Primary platform: Meta (Facebook/Instagram)
- Secondary: Google Search (branded + high-intent)
- LTV: $776 (based on $97/mo x 8 months avg)
- Target ROAS: 3:1 minimum

### `/ads plan`
Full campaign planning with audience/creative/funnel strategy:

1. **Objective alignment:** What's the #1 goal right now? (Pilots? Paid signups? Demo calls?)
2. **Audience mapping:** Cold → Warm → Hot funnel with specific audiences per stage
3. **Creative plan:** What assets exist, what needs to be created, test matrix
4. **Landing page selection:** Which page for which audience temperature
5. **Budget allocation:** By campaign, by week, with scaling rules
6. **Timeline:** Week-by-week launch plan
7. **KPI targets:** CPL, CPA, ROAS, CTR, frequency by campaign
8. **Measurement plan:** How to track, when to optimize, when to kill

Output a structured campaign plan document ready to execute.

### `/ads competitor`
Competitive advertising intelligence:

- Identify competitors running ads (Smith.ai, Ruby, AnswerConnect, Nexa, PATLive, Davinci)
- Meta Ad Library research (what creative they're running)
- Google Ads auction insights and keyword gaps
- Competitive positioning angles:
  - Price: The Call Taker at $97 vs Smith.ai $292+ vs Ruby $449+
  - AI vs Human: Faster, 24/7, never sick, never rude, scales instantly
  - Industry-specific: Trained for YOUR business type
  - Risk: Free 14-day pilot, no contracts, cancel anytime
- Counter-messaging for competitor claims
- Ad copy that directly addresses competitor weaknesses
- Comparison landing page strategy (vs-smith-ai.html, vs-ruby-receptionists.html already exist)

## Output Format

Always structure responses with:
1. **Executive summary** (1-2 sentences: what to do RIGHT NOW)
2. **Detailed analysis/recommendations** (the meat)
3. **Action items** (numbered list, priority order)
4. **Metrics to watch** (what to track after implementing)

## Rules

- Wallace is 16 and bootstrapped — respect budget constraints, prioritize high-ROI moves
- Start with Meta Ads (Facebook/Instagram) — it's the primary platform
- Always recommend the free pilot as the primary conversion action (lowest friction)
- Use "GIDEON" when referring to the AI voice agent, never "Jessica" or "the AI"
- No dashes in ad copy (confirmed dead approach per brand rules)
- Reference existing assets before suggesting new ones to create
- Include specific numbers in recommendations (budget amounts, CPL targets, audience sizes)
- When suggesting creative, match The Call Taker's brand voice: direct, pain-aware, revenue-focused, slightly aggressive but professional
