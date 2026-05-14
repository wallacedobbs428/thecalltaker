# Prospect Scoring And CTOS Command Center Spec

## Purpose

Define a safe, CTOS-native scoring model and command center for The Call Taker outreach. This document is implementation-ready but does not enable sending, scraping, provider writes, CRM sync, SMS, calls, webhooks, or payment changes.

## Prospect Record

```json
{
  "prospectId": "example-hvac-nashville-001",
  "businessName": "Example HVAC",
  "industry": "HVAC",
  "city": "Nashville",
  "state": "TN",
  "serviceArea": "Nashville metro",
  "website": "https://example.invalid",
  "publicPhone": "+10000000000",
  "ownerOrManager": {
    "name": "Unknown",
    "source": "not-found"
  },
  "sources": [
    "https://example.invalid"
  ],
  "hours": {
    "listed": "Mon-Fri 8am-5pm",
    "afterHoursLanguage": "unknown"
  },
  "callPath": {
    "tested": false,
    "result": "not-tested",
    "notes": "No call placed."
  },
  "signals": {
    "emergencyService": false,
    "adSpendVisible": false,
    "reviewCount": null,
    "reviewRating": null,
    "reviewPain": [],
    "websiteContactFriction": []
  },
  "proofAngle": "missed-call education",
  "complianceNotes": "manual review required before outreach",
  "score": null,
  "category": null,
  "nextAction": "research"
}
```

Use real prospect data only in local/private storage unless Wallace explicitly approves a storage location. Committed examples must use fake data.

## Scoring Model

Score from 0 to 100.

### Fit Score: 30 Points

- Industry fit: 0-10
  - 10: HVAC, plumbing, roofing, water damage, locksmith, towing, electrical, garage door
  - 7: dental, med spa, urgent clinic, medical/surgical supply, property management
  - 4: general local service with phone dependence
  - 0: low phone urgency or wrong market
- Owner-operated/local decision maker: 0-8
- Service-area business with clear inbound demand: 0-6
- Right size: 0-6
  - Best: enough demand to miss calls, small enough that owner still cares directly.

### Urgency Score: 25 Points

- Emergency or after-hours service language: 0-8
- Seasonal or event-driven spikes: 0-5
- Website/contact friction: 0-5
- Public review themes around communication, responsiveness, missed calls, slow callbacks: 0-5
- Call-path issue observed safely: 0-2

### Revenue Potential: 20 Points

- High value per qualified call: 0-8
- Visible lead acquisition investment: ads, SEO, reviews, multiple landing pages: 0-5
- Strong local SEO/review footprint: 0-4
- Multiple crews/locations/services: 0-3

### Reachability: 15 Points

- Public phone works: 0-4
- Owner/manager identifiable from public sources: 0-4
- Public business email/contact path: 0-3
- Social channel active: 0-2
- Local proximity or strong market reason: 0-2

### Proof/Angle Fit: 10 Points

- Clear proof angle available: 0-4
- Secret-shopper or call-path angle safe and factual: 0-3
- Demo preview likely to be relevant: 0-3

## Deductions

- National franchise or corporate procurement: minus 20
- Existing strong call center or AI with good customer experience: minus 15
- No public sources for key fields: minus 10
- Sensitive category where outreach could be inappropriate: minus 20
- Requires private/terms-violating data collection: disqualify
- Compliance uncertainty for SMS/DM: do not use that channel until reviewed

## Categories

### A: Call Wallace Now

Score: 80-100

Requirements:

- Clear fit.
- Strong urgency or call-path issue.
- Reachable decision maker or business line.
- Safe proof angle.

Action:

- Prepare Wallace call sheet.
- Manual call or warm email from Wallace.
- No automation.

### B: Send Sequence

Score: 60-79

Requirements:

- Good fit with some urgency signals.
- Enough personalization for safe email.

Action:

- Send to manual review queue.
- Draft 5-touch sequence.
- No SMS unless compliant.

### C: Nurture

Score: 40-59

Requirements:

- Some fit but weak urgency or incomplete data.

Action:

- Add to educational nurture queue.
- Re-research later or during seasonal trigger.

### D: Bad Fit

Score: 0-39 or disqualified

Action:

- Do not contact or suppress from active outreach.
- Record reason.

## Command Center Data Model

### Tables Or Files

`prospects`

- `prospect_id`
- `business_name`
- `industry`
- `city`
- `state`
- `website`
- `public_phone`
- `owner_name`
- `owner_source`
- `service_area`
- `hours_summary`
- `emergency_language`
- `review_count`
- `review_rating`
- `review_pain_summary`
- `website_friction_summary`
- `call_path_result`
- `proof_angle`
- `score`
- `category`
- `status`
- `next_action`
- `next_action_due`
- `owner`
- `compliance_notes`

`touches`

- `touch_id`
- `prospect_id`
- `channel`
- `template_id`
- `sent_by`
- `sent_at`
- `manual_or_automated`
- `outcome`
- `notes`

`call_sheets`

- `call_sheet_id`
- `prospect_id`
- `prepared_at`
- `opening`
- `missed_call_risk`
- `proof_angle`
- `likely_objection`
- `recommended_next_step`
- `activation_boundary`

`proof_items`

- `proof_id`
- `label`
- `approved_language`
- `substantiation_status`
- `redaction_status`
- `allowed_channels`
- `expires_or_review_by`

### Status Values

- `research`
- `qualified`
- `sequence-ready`
- `manual-review`
- `touched`
- `replied`
- `hot-call-needed`
- `preview-sent`
- `wallace-call-booked`
- `setup-review-started`
- `won`
- `lost`
- `nurture`
- `bad-fit`
- `do-not-contact`

## Command Center Views

### Daily Wallace Queue

Fields:

- A leads due today
- Business name
- Phone
- Industry
- Missed-call risk
- Best opener
- Objection
- Last touch
- Next action

### Research Queue

Fields:

- Missing owner/contact
- Missing call-path result
- Missing proof angle
- Missing source URL
- Needs compliance review

### Sequence Queue

Fields:

- B leads ready for manual email draft
- Required personalization fields
- Recommended sequence angle
- Compliance footer status

### Nurture Queue

Fields:

- Seasonal follow-up date
- Industry trigger
- Reason not ready now

### Reporting Dashboard

Fields:

- New prospects researched
- A/B/C/D distribution
- Touches drafted
- Replies
- Wallace calls booked
- Setup reviews started
- Won/lost reasons
- Safety exceptions

## Acceptance Criteria For Phase 1 Build

- The command center can run with fake example data.
- No provider or CRM writes exist.
- No sending code exists.
- All templates are drafts.
- Every real prospect record requires a source URL.
- SMS/DM records require a compliance status.
- Forbidden fake-live phrases are scanned in docs/templates.
- Wallace can open one daily queue and know who to call next.

## Forbidden Claim Scan

Future checks should fail outreach docs/templates if they include unsafe claims such as:

- `You're Live`
- `GIDEON IS LIVE`
- `answering every call`
- `answering calls right now`
- `Call forwarding activated`
- `Hear AI Live`
- `provider routing active`
- `live activation complete`
- `guaranteed booked jobs`
- `automatic backend sync`
- `missing zero`

Allowed boundary wording:

- `backend sync is not configured`
- `provider routing is not confirmed`
- `live activation requires review`
- `setup is saved for review`

## Next Build Lane

Build a no-send command center:

1. Add schema files and fake example data.
2. Add validation for required source URLs and compliance flags.
3. Add a local-only scoring script.
4. Add a daily Wallace queue generator.
5. Add a forbidden-claim scan for outreach docs.
6. Keep provider adapters absent or explicit dry-run stubs.
