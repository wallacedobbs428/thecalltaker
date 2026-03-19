---
name: payment-monitor
description: "Monitors GHL for payment-pending contacts, escalates stalled payments, celebrates new payments, and triggers onboarding. Use when tracking payments or via /loop 5m /payment-monitor for continuous monitoring."
user-invokable: true
---

# Payment Monitor — Conversion Tracking Loop

You are a payment tracking engine. Every run, you monitor contacts in payment stages, escalate stalls, celebrate conversions, and trigger onboarding.

## Run Instructions

### Step 1: Read Payment State

```bash
cat ~/thecalltaker-ops/payment-log.json 2>/dev/null || echo '{"pending":[],"stalled":[],"paid":[],"lastRun":"never"}'
```

### Step 2: Pull Payment-Pending Contacts

Query GHL for contacts tagged `payment-pending`:
```bash
curl -s -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: 2021-07-28" \
  "https://services.leadconnectorhq.com/contacts/?locationId=tQb9YmrGDrdVUJYPKrsY&query=payment-pending&limit=50"
```

### Step 3: Check Pending Duration & Escalate

For each payment-pending contact, calculate hours since tagged:

**> 2 hours pending → Escalate to `payment-stalled`:**
1. Add tag `payment-stalled` in GHL
2. Log escalation
3. Send ntfy alert:
```bash
bash ~/thecalltaker-ops/notify.sh \
  "PAYMENT STALLED: {name} @ {company}" \
  "{name} ({phone}) has been payment-pending for {hours}h. May need a nudge." \
  "high"
```

**> 24 hours pending → Re-engagement sequence:**
1. Draft re-engagement SMS (different angle):
```
Hey {firstName}, just checking in — saw you were looking at The Call Taker for {company}. Still want that free 14-day pilot? I saved a spot for you. Just reply YES. — Wallace
```
2. Draft re-engagement email:
```
Subject: {firstName}, your pilot spot is still open

Hey {firstName},

I noticed you started signing up for The Call Taker pilot for {company} but didn't finish. No worries — I saved your spot.

Quick reminder: it's a free 14-day pilot. No card needed. You just forward your after-hours number and our AI starts answering calls like your best employee.

3 other {industry} businesses signed up this week. I can only handle 5 pilots at a time.

Want me to set it up? Just reply YES.

— Wallace
```
3. Send via GHL (same pattern as outreach-engine)
4. Add tag `payment-reengaged` in GHL
5. Log re-engagement

### Step 4: Detect New Payments

Query GHL for contacts tagged `paid` that are NOT in our `paid` log:
```bash
curl -s -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: 2021-07-28" \
  "https://services.leadconnectorhq.com/contacts/?locationId=tQb9YmrGDrdVUJYPKrsY&query=paid&limit=50"
```

For each NEW paid contact (not in payment-log.json `paid` array):

1. **Tag `founding-customer` in GHL:**
```bash
curl -s -X POST \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: 2021-07-28" \
  -H "Content-Type: application/json" \
  -d '{"tags":["founding-customer","pilot-active"]}' \
  "https://services.leadconnectorhq.com/contacts/{contactId}/tags"
```

2. **Send celebration ntfy (URGENT):**
```bash
bash ~/thecalltaker-ops/notify.sh \
  "PAYMENT: {name} @ {company} PAID!" \
  "{name} just paid! Company: {company}. Phone: {phone}. Plan: {plan}. FIRST CUSTOMER LETS GO." \
  "urgent"
```

3. **Update intelligence.json revenue counter:**
Read `~/thecalltaker-ops/shared/intelligence.json`, increment `revenue.mrr` by plan amount, write back.

4. **Log to payment-log.json:**
Add to `paid` array:
```json
{
  "contactId": "...",
  "name": "...",
  "company": "...",
  "phone": "...",
  "plan": "$97/mo",
  "paidAt": "2026-03-19T15:00:00Z"
}
```

### Step 5: Write Updated State

Write full state back to `~/thecalltaker-ops/payment-log.json` with:
- Updated `pending` list (with hours tracked)
- Updated `stalled` list
- Updated `paid` list
- `lastRun` timestamp

### Step 6: Log Run

Append to `~/thecalltaker-ops/logs/payment-monitor.log`:
```
[2026-03-19T15:00:00Z] RUN: Pending: 2, Stalled: 1, New payments: 0, Total paid: 0. MRR: $0.
```

## Idempotency

- Payment detection checks against `paid` log — same contact won't trigger twice
- Stall escalation checks existing tags — won't re-tag
- Re-engagement has 24h minimum — won't spam
- Safe to run every 5 minutes without side effects

## Error Handling

- GHL API fails → Log error, preserve current state, try next run
- payment-log.json corrupt → Start fresh with empty state
- intelligence.json missing → Skip revenue update, log warning
- No pending contacts → Log "0 pending" and exit cleanly
