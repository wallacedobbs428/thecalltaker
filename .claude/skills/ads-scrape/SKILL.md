---
name: ads-scrape
description: "Deep-scrape competitor ad creative from Facebook Ad Library. Analyzes hooks, copy structure, CTAs, and formats to identify what's working and what's burned out. Use after /ads-research."
argument-hint: [vertical]
allowed-tools: WebSearch, WebFetch, Read, Write, Bash, Glob, Grep
---

# Ad Scrape — Creative Deep Analysis

Deep-analyze competitor ad creative for: $ARGUMENTS

## Your Mission

You are The Call Taker's ad creative analyst. Take the competitor data from /ads-research and break down exactly WHY the winning ads work — hook by hook, line by line.

## Context

The Call Taker is an AI receptionist SaaS. $97/$297/$497/mo. Demo line: (615) 784-5747. 14-day free pilot. NEVER use "AI" in ad copy — use "24/7 receptionist", "smart receptionist", "virtual receptionist."

## Step 1: Load Research Data

Read the research file:
```
~/thecalltaker-ops/ads/research/{vertical}-competitors.json
```

If it doesn't exist, tell the user to run `/ads-research {vertical}` first.

## Step 2: Scrape Each Competitor's Ads

For each competitor from the research:
- Use WebSearch/WebFetch to find their Facebook Ad Library page and landing pages
- Search: "site:facebook.com/ads/library {advertiser name}" and their website
- Extract from each active ad:
  - Full primary text (the main copy)
  - Headline
  - Description
  - CTA button text
  - Format (image/video/carousel)
  - Link destination (landing page URL)
  - Estimated run duration

## Step 3: Classify Every Ad

For each ad, classify:

**Hook Type** (first line of copy):
- Stat hook: "87% of callers hang up if no one answers"
- Question hook: "How many calls did you miss last week?"
- Pain hook: "Every missed call is money walking to your competitor"
- Story hook: "Last month, a plumber in Nashville..."
- Direct hook: "Your phone rings. Nobody answers. You just lost $500."

**Body Structure**:
- Problem → Solution → CTA
- Social proof → Benefit → CTA
- Pain → Agitate → Solve → CTA
- Benefit stack → Proof → CTA

**Offer**: Free trial/demo, specific price, ROI guarantee, no commitment

**CTA Strength** (1-5):
- 1 = "Learn More" (weak)
- 3 = "Start Free Trial" (medium)
- 5 = "Get Your AI Receptionist Now" (strong + specific)

## Step 4: Identify the #1 Performing Angle

Based on longevity (longest running = most profitable):
- Which hook type appears most in 30+ day ads?
- Which body structure converts best?
- Which offer type has the longest survival?
- Which CTA gets used by the top spenders?

## Step 5: Save Analysis

Save to:
```
~/thecalltaker-ops/ads/scrape/{vertical}-ad-analysis.json
```

JSON structure:
```json
{
  "vertical": "{vertical}",
  "analyzed_at": "ISO timestamp",
  "total_ads_analyzed": 0,
  "ads": [
    {
      "advertiser": "",
      "primary_text": "",
      "headline": "",
      "description": "",
      "cta_button": "",
      "format": "",
      "landing_page": "",
      "days_running": 0,
      "hook_type": "",
      "body_structure": "",
      "offer": "",
      "cta_strength": 0
    }
  ],
  "winning_hook_type": "",
  "winning_body_structure": "",
  "winning_offer": "",
  "top_3_hooks": ["", "", ""],
  "burned_angles": [],
  "opportunity_gaps": []
}
```

Update `~/thecalltaker-ops/ads/intelligence.json` with winning/burned angles.

Create directories if needed: `mkdir -p ~/thecalltaker-ops/ads/scrape`

## Output to User

Print:
1. "Analyzed X ads from Y competitors in {vertical}"
2. "The winning angle: {hook_type} + {body_structure} + {offer}"
3. "Top 3 hooks that have run the longest:" (with actual copy)
4. "Burned angles to AVOID:" (short-lived ads = losers)
5. "Opportunity gaps The Call Taker can exploit:"
6. "Saved to ~/thecalltaker-ops/ads/scrape/{vertical}-ad-analysis.json"
7. "Next step: /ads-brief {vertical}"
