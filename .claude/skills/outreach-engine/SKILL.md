---
name: outreach-engine
description: "Drafts and queues personalized outreach for oracle-critical leads. Use when working hot leads, sending follow-ups, or via /loop 15m /outreach-engine for continuous outreach."
user-invokable: true
---

# Outreach Engine — Autonomous Lead Conversion Loop

You are a personalized outreach engine. Every run, you read the hot targets file, draft industry-specific emails and SMS for uncontacted leads, and queue them for delivery via GHL.

## Run Instructions

### Step 1: Read Hot Targets

```bash
cat ~/thecalltaker-ops/hot-targets.json 2>/dev/null
```

If file doesn't exist or is empty, log and exit this run.

### Step 2: Read Contact Log (24h Dedupe)

```bash
cat ~/thecalltaker-ops/outreach-queue.json 2>/dev/null || echo '{"queue":[],"sent":[]}'
```

Check the `sent` array. Skip any contact whose `lastOutreach` timestamp is within 24 hours.

### Step 3: Draft Personalized Outreach

For each oracle-critical contact NOT contacted in 24h:

#### Email (use cold-email patterns)

Subject lines by vertical:
- **HVAC**: "{company} — the call that got away last night"
- **Locksmith**: "{company} — your missed lockout calls are going to competitors"
- **Plumbing**: "{company} — $2K in emergency calls you didn't answer this week"
- **Dental**: "{company} — patients are calling after hours. Who's answering?"
- **Legal**: "{company} — potential clients calling at 9pm aren't leaving voicemails"
- **Roofing**: "{company} — storm season calls at 2am. Ready?"
- **Towing**: "{company} — stranded drivers don't call twice"
- **General**: "{company} — how many calls did you miss this week?"

Body template (personalize per vertical):
```
Hey {firstName},

Quick question — what happens when someone calls {company} at 9pm on a Tuesday?

If the answer is voicemail, you're losing $2K-$10K/month in jobs that go to whoever picks up first.

I built an AI receptionist that answers like your best employee — books appointments, takes messages, dispatches emergencies. It already handles calls for {similar_industry_company}.

I'm giving 3 businesses a free 14-day pilot this month. No card, no contract. You just forward your after-hours line.

Want me to set it up for {company}?

— Wallace
The Call Taker | thecalltaker.com
```

#### SMS Follow-Up

Draft a short SMS (under 160 chars):
```
Hey {firstName}, saw {company} might be missing after-hours calls. I built an AI that answers 24/7 for ${industry} businesses. Want a free 14-day pilot? No catch. — Wallace
```

### Step 4: Queue Outreach

Add drafted messages to `~/thecalltaker-ops/outreach-queue.json`:

```json
{
  "queue": [
    {
      "contactId": "ghl_id",
      "name": "Greg",
      "company": "Carolina Locksmith",
      "phone": "(919) 608-3694",
      "email": "greg@example.com",
      "industry": "locksmith",
      "score": 95,
      "email_subject": "Carolina Locksmith — your missed lockout calls...",
      "email_body": "...",
      "sms_body": "...",
      "queuedAt": "2026-03-19T14:45:00Z",
      "status": "queued"
    }
  ],
  "sent": []
}
```

### Step 5: Tag Contact in GHL

Add tag `outreach-queued` to each queued contact:
```bash
curl -s -X POST \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: 2021-07-28" \
  -H "Content-Type: application/json" \
  -d '{"tags":["outreach-queued"]}' \
  "https://services.leadconnectorhq.com/contacts/{contactId}/tags"
```

### Step 6: Execute Queued Outreach via GHL

For each queued item, send via GHL Conversations API:

**Email:**
```bash
curl -s -X POST \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: 2021-04-15" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Email",
    "contactId": "{contactId}",
    "subject": "{email_subject}",
    "html": "{email_body}",
    "emailFrom": "wallace@mail.thecalltaker.com"
  }' \
  "https://services.leadconnectorhq.com/conversations/messages"
```

**SMS:**
```bash
curl -s -X POST \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: 2021-04-15" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "SMS",
    "contactId": "{contactId}",
    "message": "{sms_body}"
  }' \
  "https://services.leadconnectorhq.com/conversations/messages"
```

After sending, move from `queue` to `sent` with timestamp:
```json
{"contactId": "...", "sentAt": "2026-03-19T14:50:00Z", "lastOutreach": "2026-03-19T14:50:00Z"}
```

### Step 7: Send Alert for Top Targets

For contacts scoring 90+, send ntfy:
```bash
bash ~/thecalltaker-ops/notify.sh \
  "OUTREACH: Sent to {name} @ {company}" \
  "Email + SMS queued for {name} ({phone}). Score: {score}. Industry: {industry}." \
  "default"
```

### Step 8: Log Run

Append to `~/thecalltaker-ops/logs/outreach-engine.log`:
```
[2026-03-19T14:50:00Z] RUN: Processed 5 targets. Sent: 3 (email+SMS). Skipped: 2 (contacted <24h). Queue: 0 remaining.
```

## Idempotency

- 24-hour contact window prevents duplicate outreach
- `outreach-queued` tag prevents re-queuing
- Sent log tracks all outreach with timestamps
- Safe to re-run — checks sent history before every action

## Error Handling

- GHL send fails → Keep in queue with `status: "failed"`, retry next run
- hot-targets.json missing → Log "No targets" and exit cleanly
- Contact has no email → Skip email, send SMS only
- Contact has no phone → Skip SMS, send email only
- Both missing → Log warning, skip contact
