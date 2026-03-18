---
name: ads-launch
description: "Build and launch Facebook Lead Ad campaigns via Meta Marketing API. Creates campaign, ad set, and ads — ALL PAUSED by default. Never auto-publishes. Requires META_ACCESS_TOKEN and META_AD_ACCOUNT_ID. Use after /ads-write."
argument-hint: [vertical]
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Ad Launch — Meta Campaign Builder

Build and launch Facebook campaigns for: $ARGUMENTS

## CRITICAL SAFETY RULES

1. **ALL ads created as PAUSED.** Never auto-publish.
2. **Show Wallace everything** before activating. Print full campaign structure.
3. **Require explicit "launch" confirmation** before unpausing any ad.
4. **Log every API call** to ~/thecalltaker-ops/ads/active/{vertical}-campaign.json

## Context

The Call Taker: AI receptionist SaaS. $97/$297/$497/mo. Demo line: (615) 784-5747. 14-day free pilot.

## Step 1: Check Prerequisites

Check environment variables:
```bash
echo "META_ACCESS_TOKEN: ${META_ACCESS_TOKEN:+SET}" && echo "META_AD_ACCOUNT_ID: ${META_AD_ACCOUNT_ID:+SET}"
```

If either is missing, DO NOT proceed with API calls. Instead:
1. Save the complete campaign config to `~/thecalltaker-ops/ads/active/{vertical}-campaign.json`
2. Print instructions:
   - "Get META_ACCESS_TOKEN from developers.facebook.com → Marketing API → Tools → Access Token Tool"
   - "Select ads_management and ads_read permissions"
   - "Get META_AD_ACCOUNT_ID from Meta Business Suite → Settings → Ad Account"
3. Print the full campaign structure that WILL be created once tokens are set

Also read the ad copy: `~/thecalltaker-ops/ads/copy/{vertical}-ad-copy.md`

If copy doesn't exist, tell user to run `/ads-write {vertical}` first.

## Step 2: Create Campaign (if tokens exist)

```bash
curl -X POST "https://graph.facebook.com/v21.0/act_${META_AD_ACCOUNT_ID}/campaigns" \
  -H "Authorization: Bearer ${META_ACCESS_TOKEN}" \
  -d "name=TCT - ${VERTICAL} - Lead Gen" \
  -d "objective=OUTCOME_LEADS" \
  -d "status=PAUSED" \
  -d "special_ad_categories=[]"
```

## Step 3: Create Ad Set

Targeting per vertical:
- **HVAC:** Interests: HVAC, Air conditioning, Heating
- **Roofing:** Interests: Roofing, Home improvement, General contractor
- **Plumbing:** Interests: Plumbing, Plumber, Drain cleaning
- **Dental:** Interests: Dentistry, Dental practice management
- **Locksmith:** Interests: Locksmithing, Security
- **Towing:** Interests: Towing, Roadside assistance, Auto repair

All ad sets:
- US national, Age 25-65
- Behaviors: Small business owners (ID: 6002714895372)
- Budget: $5/day (500 cents)
- Optimization: LEAD_GENERATION
- NO Advantage+ audience (manual targeting for testing)
- Status: PAUSED

## Step 4: Create Lead Form

Using questions from the ad copy file. Include:
- Privacy policy: https://thecalltaker.com/privacy.html
- Thank you page with demo line CTA

## Step 5: Create 3 Ads (ALL PAUSED)

One per angle from the copy file. Each with:
- Creative from copy file
- Lead form attached
- Link: https://thecalltaker.com/pilot/
- Status: PAUSED

## Step 6: Show Campaign Structure

Print:
```
═══════════════════════════════════════
 CAMPAIGN READY — ALL PAUSED
═══════════════════════════════════════
Campaign: TCT - {VERTICAL} - Lead Gen
  ID: {campaign_id}
  Budget: $5/day
  Status: PAUSED

Ad Set: TCT - {VERTICAL} Owners - $5/day
  ID: {adset_id}
  Targeting: {summary}
  Status: PAUSED

Ad 1: {headline} — PAUSED
Ad 2: {headline} — PAUSED
Ad 3: {headline} — PAUSED
═══════════════════════════════════════
Type "launch" to activate all ads.
Type "launch 1" to activate only Ad 1.
═══════════════════════════════════════
```

## Step 7: Wait for Confirmation

Ask: "Review the campaign above. Type 'launch' to activate all ads, 'launch N' for a specific ad, or 'cancel' to keep paused."

If "launch":
- Unpause campaign, ad set, and specified ads via API
- Send ntfy to tct-sales-63uYsIT9: "AD LAUNCHED: {vertical} | Campaign ID: {id} | Budget: $5/day | Ads: {count} active"

## Step 8: Save Campaign Data

Save all IDs to: `~/thecalltaker-ops/ads/active/{vertical}-campaign.json`

Update `~/thecalltaker-ops/ads/intelligence.json` with active campaign data.

Create directory if needed: `mkdir -p ~/thecalltaker-ops/ads/active`
