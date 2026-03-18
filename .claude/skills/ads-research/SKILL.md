---
name: ads-research
description: "Research competitor ads in Facebook Ad Library for a vertical. Scrapes competitor names, ad counts, longevity, angles, and weaknesses. Use when analyzing what answering service competitors are running in a specific industry or market."
argument-hint: [vertical] [optional: location]
allowed-tools: WebSearch, WebFetch, Read, Write, Bash, Glob, Grep
---

# Ad Research — Competitor Intelligence

Research competitor advertising for: $ARGUMENTS

## Your Mission

You are The Call Taker's ad intelligence agent. Find every competitor running Facebook/Instagram ads for AI receptionist, answering service, or virtual receptionist products targeting the specified vertical.

## Context

The Call Taker is an AI receptionist SaaS for service businesses. $97/$297/$497/mo. Demo line: (615) 784-5747. Free 14-day pilot, no card required. Target: small business owners who miss after-hours calls.

## Step 1: Search Facebook Ad Library

Use WebSearch and WebFetch to query the Meta Ad Library:
- URL: https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q={query}
- If direct scraping is blocked (403), fall back to web search for competitor intelligence.

Search queries to run (replace {vertical} with the input vertical):
1. "AI receptionist {vertical}"
2. "answering service {vertical}"
3. "virtual receptionist {vertical}"
4. "AI phone answering {vertical}"
5. "missed calls {vertical}"
6. "after hours answering {vertical}"

Also search for known competitors by name:
- Smith.ai, Goodcall, Dialzara, Upfirst, My AI Front Desk, Cira, RingReady, AnswerConnect, Nexa, LeadTruffle, AnswerForce, Ruby Receptionists

For each competitor, extract:
- Page name / advertiser name
- Ad Library ID or Facebook page URL
- Estimated number of active ads
- Estimated days running (30+ = proven winner, 90+ = category killer)
- Ad copy preview (first 100 chars)
- Format: image / video / carousel

## Step 2: Identify Proven Winners

Filter for ads running 30+ days — these are proven performers (profitable enough to keep spending).
Flag any running 90+ days as "category killers."

## Step 3: Classify Competitor Angles

For each competitor, identify their primary angle:
- **Pain**: "Stop missing calls" / "Every missed call costs you $X"
- **Benefit**: "Answer every call 24/7" / "Never miss a lead again"
- **Social Proof**: "Trusted by X businesses" / "X calls answered"
- **Fear**: "Your competitor is answering while you sleep"
- **Price**: Leading with cost savings or specific pricing
- **Demo**: "Try it free" / "Call our demo line"

## Step 4: Build Competitor Table

Format output as:

| # | Advertiser | Ad Count | Longest Running | Days Active | Primary Angle | Weakness |
|---|-----------|----------|-----------------|-------------|--------------|----------|

Weakness = what they're NOT doing that The Call Taker can exploit (e.g., no industry specificity, no demo line, generic copy, no social proof, weak CTA, expensive per-minute pricing).

## Step 5: Extract Top 3 Winning Angles

Based on longevity (longer = more profitable), identify:
1. The #1 proven angle in this vertical
2. The #2 angle
3. An underserved angle no competitor is using

## Step 6: Save Output

Save the full research to:
```
~/thecalltaker-ops/ads/research/{vertical}-competitors.json
```

JSON structure:
```json
{
  "vertical": "{vertical}",
  "location": "{location or 'national'}",
  "researched_at": "ISO timestamp",
  "competitors": [
    {
      "name": "",
      "ad_library_id": "",
      "ad_count": 0,
      "longest_running_days": 0,
      "primary_angle": "",
      "formats": [],
      "weakness": "",
      "sample_copy": ""
    }
  ],
  "winning_angles": ["", "", ""],
  "underserved_angle": "",
  "total_competitors_found": 0
}
```

Also update `~/thecalltaker-ops/ads/intelligence.json` — merge findings into the `winning_angles` and `burned_angles` fields for this vertical.

Create directories if they don't exist: `mkdir -p ~/thecalltaker-ops/ads/research`

## Output to User

Print a summary:
1. Competitor table (formatted markdown)
2. "Top 3 winning angles in {vertical}:"
3. "Underserved angle The Call Taker should own:"
4. "Saved to ~/thecalltaker-ops/ads/research/{vertical}-competitors.json"
5. "Next step: /ads-scrape {vertical}"
