# GHL Workflow Builder Guide — Hot Lead Reactivation: Founding 10

> Step-by-step manual build guide for the GHL workflow builder UI.
> This mirrors the automation in `ops/ghl-reactivation-workflow.py`.

---

## Overview

| Field | Value |
|-------|-------|
| Workflow Name | Hot Lead Reactivation — Founding 10 |
| Trigger | Contact tag added: `hot-lead-reactivation` |
| Goal | Get a demo booked |
| Target | 35 contacts currently tagged `hot-lead` |
| Messages | 5 (Message 4 is reply-triggered only) |
| Timeline | Day 0 → Day 10 |

---

## Step 1: Create the Workflow

1. Go to **Automation → Workflows → + Create Workflow**
2. Name: `Hot Lead Reactivation — Founding 10`
3. Click **Add New Trigger**
4. Select: **Contact Tag** → **Tag Added** → `hot-lead-reactivation`

---

## Step 2: Message 1 — Day 0 (Immediate)

### Primary path: SMS

1. Add action: **Send SMS**
2. Message:
```
Hey {{contact.first_name}}, quick question — are you still getting missed calls after hours?
```

### Fallback path: Email (if no phone)

1. Add **If/Else Branch** before the SMS:
   - Condition: `Contact → Phone → is not empty`
   - **YES branch** → SMS (above)
   - **NO branch** → Send Email:
     - Subject: `{{contact.first_name}}, quick question about your missed calls`
     - Body: Same question + "I built something that might help. Happy to show you in 10 minutes." + booking link

### Industry Personalization (Optional)

Add If/Else branches before Message 1:
- If custom field `industry` = `hvac` → SMS: "...are you still losing HVAC calls on nights and weekends?"
- If custom field `industry` = `plumbing` → SMS: "...are you still missing plumbing emergency calls after hours?"
- If custom field `industry` = `roofing` → SMS: "...are you still missing roofing estimate calls during storm season?"
- If custom field `industry` = `dental` → SMS: "...are you still missing new patient calls during lunch and after hours?"
- If custom field `industry` = `pest_control` → SMS: "...are you still losing pest control calls to competitors?"
- Default → generic "missed calls after hours" version

---

## Step 3: Wait + Reply Check (after Message 1)

1. Add: **Wait** → 48 hours
2. After wait, add **If/Else Branch**:
   - Condition: **Contact replied** (or tag `replied-reactivation` exists)
   - **YES** → Go to Reply Handler (Step 8)
   - **NO** → Continue to Message 2

---

## Step 4: Message 2 — Day 3

1. Add action: **Send SMS**
2. Message:
```
Hey {{contact.first_name}} — just wanted to make sure this didn't get buried. Are missed calls still an issue for you?
```
3. Add: **Wait** → 48 hours
4. Add **If/Else Branch**: Reply check → YES: Reply Handler / NO: Continue

---

## Step 5: Message 3 — Day 5

1. Add action: **Send SMS**
2. Message:
```
Got it. I built something that might actually fix that — an AI receptionist named Jessica that answers your phones 24/7, sounds completely human, and books appointments automatically.

Takes 10 minutes to show you. I'll call your actual business number so you can hear exactly what your customers would hear.

Want me to set that up this week? No cost, no commitment.
```
3. Add: **Wait** → 48 hours
4. Add **If/Else Branch**: Reply check → YES: Reply Handler / NO: Continue to Message 5

> **Note:** Message 4 is NOT in this flow. It's reply-triggered only (see Step 7).

---

## Step 6: Message 5 — Day 10 (Breakup)

**Only fires if zero replies across all prior messages.**

1. Add action: **Send SMS**
2. Message:
```
Hey {{contact.first_name}} — I'll stop reaching out after this. If missed calls ever become a problem worth solving, you can always reach me at (615) 653-9004 or book a quick demo at https://thecalltaker.com/book.

Wish you the best either way.
```
3. Add action: **Add Tag** → `reactivation-exhausted`
4. Add action: **Remove Tag** → `hot-lead-reactivation`
5. Add action: **Add Note** → `Completed full reactivation sequence with no response — {{now}}`

---

## Step 7: Message 4 — Price Hesitation (Separate Workflow)

**This is a separate workflow triggered by a manual tag.**

1. Create new workflow: `Reactivation — Price Hesitation Handler`
2. Trigger: **Contact Tag Added** → `price-hesitation`
3. Add **If/Else Branch**: Contact has tag `reactivation-enrolled`
   - **YES** → Continue
   - **NO** → End (don't send to non-reactivation contacts)
4. Add action: **Send SMS**
5. Message:
```
We're onboarding our first 10 founding customers right now — no setup fee (normally $500), and it's $197/month for the first 3 months, then standard pricing after that.

One booked job a month more than covers it. And if Jessica doesn't deliver in the first 14 days, you pay nothing.

Want to be one of the 10?
```
6. Add action: **Remove Tag** → `price-hesitation`

---

## Step 8: Reply Handler Branch

**When any inbound SMS reply is detected at any point in the sequence:**

1. Add action: **Remove from Workflow** (stops all pending waits/messages)
2. Add action: **Add Tag** → `replied-reactivation`
3. Add action: **Send Internal Notification** (Email to Wallace):
   - To: `thecalltakerai@gmail.com`
   - Subject: `Reactivation Reply — {{contact.first_name}}`
   - Body: `{{contact.first_name}} replied to the reactivation sequence. Message: {{message.body}}`
4. Add action: **Send Internal Notification** (SMS to Wallace):
   - To: `(615) 653-9004`
   - Body: `REACTIVATION REPLY: {{contact.first_name}} replied. Call them NOW: {{contact.phone}}`
5. Add action: **Create Task**:
   - Title: `Follow up with {{contact.first_name}} within 2 hours`
   - Due: 2 hours from now
   - Assigned to: Wallace
6. Add: **Wait** → 2 hours
7. Add **If/Else Branch**: Contact has tag `contacted`
   - **YES** → End
   - **NO** → Send SMS reminder to Wallace only:
     - `REMINDER: {{contact.first_name}} replied to reactivation 2hrs ago and hasn't been contacted. Phone: {{contact.phone}}`

---

## Step 9: Enroll the 35 Contacts

To trigger the workflow for all 35 hot leads:

### Option A: Bulk tag in GHL UI
1. Go to **Contacts**
2. Filter by tag: `hot-lead`
3. Select all (up to 35 contacts)
4. Bulk action → **Add Tag** → `hot-lead-reactivation`

### Option B: Use the Python script
```bash
python3 ops/ghl-reactivation-workflow.py enroll
```
This finds all contacts tagged `hot-lead` and adds `hot-lead-reactivation` to each one.

### Option C: GHL API (curl)
For each contact ID:
```bash
curl -X POST "https://services.leadconnectorhq.com/contacts/{CONTACT_ID}/tags" \
  -H "Authorization: Bearer pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35" \
  -H "Version: 2021-07-28" \
  -H "Content-Type: application/json" \
  -d '{"tags": ["hot-lead-reactivation"]}'
```

---

## Tags Reference

| Tag | When Applied | Purpose |
|-----|-------------|---------|
| `hot-lead` | Pre-existing | Source tag (35 contacts) |
| `hot-lead-reactivation` | Enrollment | Workflow trigger |
| `reactivation-enrolled` | After scan | Prevents double-enrollment |
| `replied-reactivation` | On reply | Marks responders |
| `price-hesitation` | Manual (Wallace) | Triggers Message 4 |
| `reactivation-exhausted` | After Message 5 | Marks non-responders |
| `demo-booked` | Manual (Wallace) | Goal achieved |
| `contacted` | Manual (Wallace) | Reply handler resolution |

---

## Python Script vs GHL Workflow

The Python script (`ops/ghl-reactivation-workflow.py`) is the **recommended** approach because:

1. **Reply detection** — GHL native workflows can't reliably detect inbound SMS replies as branch conditions in all cases. The Python script polls for replies every run.
2. **Industry personalization** — 19 industries with custom hooks. GHL would need 19 If/Else branches.
3. **Contact registry** — Cross-engine coordination prevents over-contacting leads that other engines already touched.
4. **Rate limiting** — 15 SMS/run cap, 1.5s pacing between sends.
5. **State tracking** — Full audit trail in `ghl-reactivation-state.json`.
6. **Crash recovery** — Atomic state writes, ntfy crash alerts, can resume from any point.

If you prefer the GHL native workflow, follow Steps 1-8 above. Both approaches use the same message copy and timing.

---

## Deployment (Python Script)

```bash
# Preview all messages first
python3 ops/ghl-reactivation-workflow.py preview

# Enroll all 35 hot leads
python3 ops/ghl-reactivation-workflow.py enroll

# Run the first cycle (scan + send)
python3 ops/ghl-reactivation-workflow.py run

# Check status
python3 ops/ghl-reactivation-workflow.py status

# Install launchd (on Mac)
cp ops/com.thecalltaker.reactivation.scan.plist ~/Library/LaunchAgents/
cp ops/com.thecalltaker.reactivation.send.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.thecalltaker.reactivation.scan.plist
launchctl load ~/Library/LaunchAgents/com.thecalltaker.reactivation.send.plist
```
