---
name: ads-report
description: "Pull live performance metrics for all active Meta ad campaigns. Reports spend, CPL, leads, and recommends kill/scale/hold decisions. Compares against vertical benchmarks. Use daily to monitor ad performance."
argument-hint: [optional: vertical]
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Ad Report — Performance Dashboard

Pull performance report for: $ARGUMENTS (or all active campaigns if no vertical specified)

## Context

The Call Taker: AI receptionist SaaS. CPL benchmarks:
- Towing: $12 target / $24 kill
- Locksmith: $15 / $30
- HVAC: $18 / $36
- Plumbing: $20 / $40
- Roofing: $22 / $44
- Dental: $35 / $70

## Step 1: Load Active Campaigns

If a vertical was specified, read:
```
~/thecalltaker-ops/ads/active/{vertical}-campaign.json
```

If no vertical, glob all: `~/thecalltaker-ops/ads/active/*-campaign.json`

If no campaigns found: "No active campaigns. Run /ads-launch {vertical} first."

## Step 2: Check for API Tokens

```bash
echo "META_ACCESS_TOKEN: ${META_ACCESS_TOKEN:+SET}"
```

If tokens exist, pull live data from Meta API:
```bash
curl -G "https://graph.facebook.com/v21.0/${CAMPAIGN_ID}/insights" \
  -H "Authorization: Bearer ${META_ACCESS_TOKEN}" \
  -d "fields=spend,impressions,clicks,cpc,cpm,actions,cost_per_action_type" \
  -d "date_preset=last_7d"
```

If no tokens, generate report from campaign config with "PENDING_LAUNCH" status.

## Step 3: Extract Metrics

For each campaign:
- **Spend**: Total $ spent
- **Impressions**: Times shown
- **Clicks**: Link clicks
- **CTR**: Click-through rate
- **Leads**: From actions where action_type = "lead"
- **CPL**: Cost per lead (spend / leads)

Per-ad breakdown:
```bash
curl -G "https://graph.facebook.com/v21.0/${ADSET_ID}/insights" \
  -H "Authorization: Bearer ${META_ACCESS_TOKEN}" \
  -d "fields=spend,impressions,actions,cost_per_action_type" \
  -d "level=ad" \
  -d "date_preset=last_7d"
```

## Step 4: Generate Recommendations

For each ad:

**KILL** (red): CPL > 2x benchmark after 1,000+ impressions → pause immediately
**HOLD** (yellow): CPL between 1x-2x benchmark OR < 1,000 impressions → keep running
**SCALE** (green): CPL < benchmark for 3+ consecutive days → increase budget
**TEST NEW** (blue): All 3 ads killed → return to /ads-brief for new angles

## Step 5: Format Report

```
═══════════════════════════════════════
 AD PERFORMANCE REPORT — {date}
═══════════════════════════════════════

{VERTICAL} Campaign — {days} days active
Budget: ${daily}/day | Total Spend: ${total}
Leads: {count} | CPL: ${cpl} (benchmark: ${bench})

  Ad 1: "{headline}"
    Spend: ${x} | Leads: {n} | CPL: ${x}
    → RECOMMENDATION

  Ad 2: "{headline}"
    Spend: ${x} | Leads: {n} | CPL: ${x}
    → RECOMMENDATION

  Ad 3: "{headline}"
    Spend: ${x} | Leads: {n} | CPL: ${x}
    → RECOMMENDATION

ACTIONS:
  1. {action item}
  2. {action item}

ROI MATH:
  {leads} leads × 20% close rate = {clients} clients
  {clients} × $97/mo = ${mrr}/mo MRR
  Ad spend: ${spend} → Payback: {days} days
═══════════════════════════════════════
```

## Step 6: Save Report & Update Intelligence

Save to: `~/thecalltaker-ops/ads/reports/{vertical}-{date}.json`

Update `~/thecalltaker-ops/ads/intelligence.json`:
- Update `cpls_by_vertical` with latest actual CPL
- Update `total_spend` and `total_leads`
- Move killed angles to `burned_angles`
- Move scaled angles to `winning_angles`

Create directory if needed: `mkdir -p ~/thecalltaker-ops/ads/reports`

## Step 7: Notification

If campaigns are active and have data, send to ntfy SALES topic (tct-sales-63uYsIT9):
```
AD REPORT: {vertical} | Spend: ${spend} | Leads: {leads} | CPL: ${cpl} | Action: {primary recommendation}
```

## Output to User

Print the full formatted report, then:
"Report saved to ~/thecalltaker-ops/ads/reports/{vertical}-{date}.json"
"Intelligence updated."
