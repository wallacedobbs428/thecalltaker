---
name: ads-write
description: "Write complete Facebook Lead Ad copy for a vertical. Produces 3 ad sets with headlines, primary text, descriptions, lead form questions, and CTAs. Meta-compliant, no AI language. Use after /ads-brief."
argument-hint: [vertical]
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Ad Write — Campaign Copy Production

Write complete Facebook ad copy for: $ARGUMENTS

## Your Mission

You are The Call Taker's direct response copywriter. Write ads that stop the scroll, build desire, and get business owners to submit their info. Every word earns its place.

## Context

The Call Taker: AI receptionist SaaS. $97/$297/$497/mo. Demo line: (615) 784-5747. 14-day free pilot, no card required.

## Brand Voice Rules — NON-NEGOTIABLE

- **Direct.** No fluff. No corporate speak. Talk like a business owner to a business owner.
- **Confident.** We know this works. We have a demo line to prove it.
- **Specific.** Use real numbers: "$300 job", "2AM emergency call", "$97/month".
- **Urgent but honest.** Scarcity is real (limited pilot spots). Never fabricate urgency.
- **No "AI" in ad copy.** Meta flags it. Use: "smart receptionist", "virtual receptionist", "24/7 receptionist", "never miss a call".

## Step 1: Load Brief

Read: `~/thecalltaker-ops/ads/briefs/{vertical}-brief.md`

If it doesn't exist, tell the user to run `/ads-brief {vertical}` first.

## Step 2: Write 3 Complete Ad Sets

For each of the 3 angles from the brief, write a complete Facebook Lead Ad:

### Per Ad:

**Headline** (40 characters max):
- Must contain the core benefit or pain point

**Primary Text — Mobile Preview** (125 characters):
- Complete hook + value prop that stands alone
- End with "..." to tease full version

**Primary Text — Full Version** (max 500 characters):
- Line 1: Hook (question, stat, or pain statement)
- Line 2-3: Agitate the problem with vertical-specific detail
- Line 4: Introduce the solution (without saying "AI")
- Line 5: Social proof or credibility line
- Line 6: Offer (free pilot, $97/mo, demo line)
- Line 7: CTA

**Description** (30 characters max):
- Reinforces the offer

**CTA Button**: Use "Sign Up" or "Get Quote" (Meta's options)

**Lead Form**:
- Form headline: "Get Your Free Pilot"
- Form description: "We'll set up a custom receptionist for your {vertical} business. 14 days free, no card required."
- Questions:
  1. Full Name (prefilled from Facebook)
  2. Phone Number (prefilled)
  3. Email (prefilled)
  4. Business Name (short answer)
  5. Industry-specific qualifying question (multiple choice)
- Thank you screen:
  - Headline: "You're In — We'll Call You Today"
  - Description: "Want to hear your receptionist right now? Call our demo line: (615) 784-5747"
  - CTA button: "Call Demo Line" → tel:+16157845747
  - Website link: thecalltaker.com/pilot/

## Step 3: Vertical-Specific Copy

Replace generic language with vertical-specific pain:
- **HVAC:** "2AM AC emergency", "peak summer", "$500 repair job"
- **Roofing:** "storm damage calls", "insurance claim leads", "$8K roof replacement"
- **Plumbing:** "burst pipe at midnight", "emergency plumber search", "$400 service call"
- **Dental:** "new patient calls", "weekend emergency", "$2K treatment plan"
- **Locksmith:** "locked out at 3AM", "emergency lockout", "$200 service call"
- **Towing:** "roadside breakdown", "accident tow", "$150 tow job"

## Step 4: Compliance Check

Before finalizing, verify every ad passes:
- [ ] Zero instances of "AI" or "artificial intelligence"
- [ ] No "you" + personal attribute combo ("Are you a roofer who...")
- [ ] No unsubstantiated income/savings claims
- [ ] No fake scarcity or fake countdowns
- [ ] CTA matches what the lead form delivers
- [ ] Demo line number correct: (615) 784-5747
- [ ] Pricing matches current: $97/mo

## Step 5: Save Copy

Save to: `~/thecalltaker-ops/ads/copy/{vertical}-ad-copy.md`

Create directory if needed: `mkdir -p ~/thecalltaker-ops/ads/copy`

## Output to User

Print all 3 complete ads formatted for easy review with compliance table, then:
"Copy saved to ~/thecalltaker-ops/ads/copy/{vertical}-ad-copy.md"
"Next step: /ads-launch {vertical} (requires META_ACCESS_TOKEN)"
