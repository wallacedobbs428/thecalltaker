---
name: indeed-leads
description: "Find companies posting receptionist, front desk, or phone answering jobs on Indeed. These businesses are actively paying to hire someone to answer phones — making them perfect AI receptionist prospects. Returns scored lead lists with company info and outreach angles."
argument-hint: [metro/city] [optional: industry filter] [optional: count]
allowed-tools: WebSearch, WebFetch, Read, Write, Bash, Glob, Grep
---

# Indeed Lead Finder — Hiring Signal Intelligence

Find businesses hiring receptionists: $ARGUMENTS

## Your Mission

You are The Call Taker's hiring-signal intelligence agent. Companies posting receptionist, front desk, or phone answering jobs on Indeed are **actively spending money** to hire someone to answer phones. The Call Taker replaces that hire for $97-$497/mo — no benefits, no PTO, no training, no turnover, works 24/7.

This is the highest-intent lead source available. A company posting a receptionist job today is a company that needs The Call Taker TODAY.

## Context

The Call Taker is an AI receptionist SaaS for service businesses. $97/$297/$497/mo plans. Demo line: (615) 784-5747. Free 14-day pilot, no card required.

**The pitch to Indeed leads:** "I saw you're hiring a receptionist. What if I told you there's an AI that does the same job for $97/mo — answers every call 24/7, books appointments, never calls in sick, and you can try it free for 14 days?"

## Step 1: Search Indeed via Web Search

Use WebSearch to find active job postings. Run these queries for the specified metro:

### Primary Queries (receptionist/front desk)
1. `site:indeed.com "receptionist" "{metro}" -remote`
2. `site:indeed.com "front desk" "{metro}" -remote`
3. `site:indeed.com "phone answering" OR "answer phones" "{metro}"`
4. `site:indeed.com "receptionist" "{metro}" "HVAC" OR "plumbing" OR "dental" OR "legal" OR "veterinary"`
5. `site:indeed.com "office manager" "answer phones" "{metro}"`

### Industry-Specific Queries (if industry filter provided)
6. `site:indeed.com "receptionist" "{industry}" "{metro}"`
7. `site:indeed.com "{industry}" "front desk" OR "phones" "{metro}"`

### Salary Signal Queries (higher salary = more pain = better lead)
8. `site:indeed.com "receptionist" "{metro}" "$15" OR "$16" OR "$17" OR "$18" OR "$19" OR "$20"`
9. `site:indeed.com "receptionist" "{metro}" "urgently hiring" OR "immediate" OR "ASAP"`

### Fallback Queries (if Indeed results are thin)
10. `"hiring receptionist" "{metro}" {industry}` — catches company career pages
11. `site:ziprecruiter.com "receptionist" "{metro}"` — ZipRecruiter as backup
12. `site:glassdoor.com "receptionist" jobs "{metro}"` — Glassdoor as backup

## Step 2: Extract Company Data from Job Postings

For each job posting found, use WebFetch on the Indeed listing URL or search for the company directly. Extract:

| Field | Source |
|-------|--------|
| Company name | Indeed job posting |
| Job title posted | Indeed listing |
| Salary offered | Indeed listing (if shown) |
| Industry | Indeed company info or infer from job description |
| "Urgently hiring" badge | Indeed listing |
| Date posted | Indeed listing |
| Company location | Indeed listing |

Then search for the company directly to get contact info:
- `"{company name}" "{metro}" phone number`
- `"{company name}" "{metro}" owner`
- Visit company website (WebFetch) for phone, email, owner name

## Step 3: Score Each Lead (0-100)

Indeed leads start with a 20-point bonus because they have **active hiring intent**.

| Signal | Points |
|--------|--------|
| **Active receptionist job posting** (baseline) | +20 |
| Urgently hiring / ASAP / Immediate | +15 |
| Salary $16+/hr (high pain — expensive hire) | +10 |
| Service industry (HVAC, plumbing, dental, legal, etc.) | +15 |
| Small company (under 50 employees) | +10 |
| Owner name found | +5 |
| Email found | +5 |
| Phone found | +5 |
| Multiple receptionist jobs posted (recurring need) | +10 |
| Bad reviews mentioning phones/communication | +5 |

### ROI Calculation for Outreach

For each lead, calculate the savings pitch:
- **Receptionist salary:** $15-20/hr × 40hrs × 52 weeks = $31,200-$41,600/year
- **Plus benefits:** ~30% overhead = $40,560-$54,080/year total cost
- **The Call Taker:** $97-$497/mo = $1,164-$5,964/year
- **Savings:** $35,000-$53,000/year

Use the posted salary to calculate exact savings for the outreach angle.

## Step 4: Research Top Leads

For leads scoring 60+, do deeper research:

1. **Visit their website** (WebFetch) — look for:
   - "Call us" messaging (phone-dependent business)
   - No online booking (phone-only scheduling)
   - After-hours messaging or lack thereof
   - Current team size from About page

2. **Check Google Reviews** — search `"{company name}" "{metro}" reviews`:
   - Look for missed-call complaints
   - "Couldn't reach anyone"
   - "Went to voicemail"
   - Low star ratings mentioning communication

3. **Check if they've posted receptionist jobs before** — search `site:indeed.com "{company name}" receptionist`:
   - Recurring postings = high turnover = massive pain point
   - Multiple open receptionist roles = growing need

## Step 5: Output Format

Write results to: `leads/indeed-{metro}-{date}.md`

### Summary
- Metro: {metro}
- Industry filter: {if any}
- Total companies found hiring: X
- Scored 70+ (HOT): X
- Scored 50-69 (WARM): X
- Total estimated annual savings if all convert: ${X}

### Hot Leads (70+ Score) — CALL THESE TODAY

For each lead:
```
### {Company Name} — Score: {X}/100
- Hiring for: {Job Title} at ${salary}/hr
- Posted: {date} | {Urgently hiring badge if yes}
- Industry: {type}
- Phone: {number}
- Email: {email}
- Website: {url}
- Owner: {name}
- Location: {address}
- Indeed URL: {link to job posting}
- Annual receptionist cost: ${calculated}
- The Call Taker savings: ${calculated}/year
- Pain signals: {review quotes, recurring postings, etc.}
- Outreach angle: "I saw you're hiring a {job title} at ${salary}/hr. What if you could replace that $X/year cost with an AI that answers every call 24/7 for $97/mo? Free 14-day pilot, no card required."
```

### Warm Leads (50-69 Score)

Same format, briefer notes.

## Step 6: GHL-Ready Export

Write JSON to `leads/indeed-{metro}-{date}.json`:

```json
[
  {
    "name": "Company Name",
    "phone": "+1XXXXXXXXXX",
    "email": "contact@company.com",
    "website": "https://...",
    "owner_name": "First Last",
    "city": "Metro",
    "state": "ST",
    "industry": "industry-tag",
    "score": 85,
    "tags": ["pilot-candidate", "hot-lead", "indeed-hiring", "industry-hvac"],
    "job_title": "Front Desk Receptionist",
    "salary_posted": "$17/hr",
    "annual_receptionist_cost": 41600,
    "tct_annual_savings": 35636,
    "pain_signals": ["urgently hiring", "3rd receptionist posting in 6 months"],
    "outreach_angle": "Personalized pitch referencing their job posting",
    "source": "indeed-leads",
    "indeed_url": "https://indeed.com/..."
  }
]
```

## Step 7: Generate Outreach Scripts

Create a call script file at `leads/indeed-{metro}-call-scripts.md`:

### Cold Call Script (for Indeed leads)

> "Hi, is this {owner_name}? This is Wallace with The Call Taker. I noticed you're hiring a {job_title} — sounds like you need someone answering your phones. Quick question: what if I told you there's an AI that does the same job for $97 a month? It answers every call 24/7, books appointments, and never calls in sick. You'd save about ${savings} a year compared to that hire. We do a free 14-day pilot — no card, no risk. Want to hear how it sounds? I can have you call our demo line right now: 615-784-5747."

### Email Template (for Indeed leads)

> Subject: Saw you're hiring a receptionist — what if you didn't have to?
>
> Hi {owner_name},
>
> I noticed {company_name} is looking for a {job_title} at ${salary}/hr. That's going to cost you about ${annual_cost}/year with benefits.
>
> What if an AI could do the same job for $97/month?
>
> The Call Taker is an AI receptionist built for {industry} businesses. It answers every call 24/7, books appointments, captures caller info, and never takes a day off.
>
> That's ${savings}/year back in your pocket.
>
> We offer a free 14-day pilot — no credit card, no contracts. You can hear it in action right now: (615) 784-5747
>
> Want me to set one up for {company_name}?
>
> — Wallace Dobbs, The Call Taker

## Rules

1. **Phone format:** Always +1XXXXXXXXXX
2. **No duplicates:** Check against existing leads in `leads/` directory
3. **Freshness matters:** Prioritize jobs posted in last 7 days — stale listings may already be filled
4. **Skip remote/virtual roles:** We're targeting local service businesses
5. **Skip huge companies:** 200+ employees probably have corporate phone systems already
6. **Save the Indeed URL:** The job posting URL is proof for the outreach angle
7. **Calculate real savings:** Use the actual posted salary, not estimates
8. **Default count:** Find at least 15 leads per metro unless fewer exist
