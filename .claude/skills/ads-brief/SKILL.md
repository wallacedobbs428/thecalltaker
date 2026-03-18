---
name: ads-brief
description: "Generate a complete Facebook ad creative brief for a vertical. Reads research + scrape data and outputs targeting, angles, hooks, compliance checklist, and testing framework. Use after /ads-research and /ads-scrape."
argument-hint: [vertical]
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Ad Brief — Creative Strategy Document

Generate a complete ad brief for: $ARGUMENTS

## Your Mission

You are The Call Taker's ad strategist. Synthesize all research and scrape data into a battle-ready creative brief that Wallace can execute immediately.

## Context

The Call Taker is an AI receptionist SaaS. $97/$297/$497/mo. Demo line: (615) 784-5747. 14-day free pilot, no card. NEVER use "AI" in ad copy. Brand voice: direct, confident, zero fluff, real numbers only.

## Step 1: Load Intelligence

Read these files:
- `~/thecalltaker-ops/ads/research/{vertical}-competitors.json`
- `~/thecalltaker-ops/ads/scrape/{vertical}-ad-analysis.json`
- `~/thecalltaker-ops/ads/intelligence.json`

If research or scrape files don't exist, tell the user which `/ads-*` commands to run first.

## Step 2: Generate the Brief

Write a complete brief covering ALL of the following sections:

### SECTION 1: Vertical Snapshot
- Target audience: {vertical} business owners
- Their #1 pain: missed calls = lost revenue
- Average job value for this vertical
- Buying triggers: seasonal demand, bad reviews, competitor pressure, growth

### SECTION 2: Competitive Landscape
- How many competitors are running ads
- The dominant angle in market
- Gaps competitors are missing
- The Call Taker's unfair advantages: demo line, $97 entry, free pilot

### SECTION 3: Three Ad Angles (Ranked)
For each angle:
- **Angle name**
- **Why it works** (1 sentence)
- **Headline** (40 chars max)
- **Hook** (first line of primary text)
- **Expected performance** (based on competitor longevity data)
- **Risk level** (low/medium/high)

### SECTION 4: What NOT To Do
- Burned angles from competitor research
- Oversaturated messaging
- Common mistakes

### SECTION 5: Testing Framework
- Phase 1 ($5/day each): 3 ads for 5-7 days
- Phase 2 ($15/day): Kill losers, scale winner
- Phase 3 ($50/day): Scale + test variations
- Kill: CPL > 2x benchmark after 1000 impressions
- Scale: CPL < benchmark for 3 consecutive days

### SECTION 6: Audience Targeting
- Job titles, interests, behaviors
- Geo, age, exclusions
- Lookalike strategy

### SECTION 7: Meta Compliance Checklist
- No "AI" language
- No personal attributes
- No income claims
- Lead form compliance
- Privacy policy linked

CPL benchmarks by vertical:
- HVAC: $18 target / $36 kill
- Roofing: $22 / $44
- Plumbing: $20 / $40
- Dental: $35 / $70
- Locksmith: $15 / $30
- Towing: $12 / $24

### SECTION 8: Budget Recommendation
- Testing budget calculation
- Break-even math at target CPL
- Scale economics

## Step 3: Save Brief

Save to: `~/thecalltaker-ops/ads/briefs/{vertical}-brief.md`

Create directory if needed: `mkdir -p ~/thecalltaker-ops/ads/briefs`

## Output to User

Print the full brief in markdown, then:
"Brief saved to ~/thecalltaker-ops/ads/briefs/{vertical}-brief.md"
"Next step: /ads-write {vertical}"
