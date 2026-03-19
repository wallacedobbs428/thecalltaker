---
name: oracle-scanner
description: "Scans GHL for oracle-hot leads, scores them 1-100, tags critical contacts, and writes hot targets. Use when running lead scoring, checking oracle pipeline, or via /loop 5m /oracle-scanner for continuous monitoring."
user-invokable: true
---

# Oracle Scanner — Lead Scoring Loop

You are a lead scoring engine. Every time you run, you scan all `oracle-hot` tagged contacts in GHL, score them, tag the best ones, and write actionable output files.

## Run Instructions

Execute these steps IN ORDER. If any GHL API call fails, log the error and continue — never crash the loop.

### Step 1: Read Intelligence

```bash
cat ~/thecalltaker-ops/shared/intelligence.json 2>/dev/null || echo '{"leads":[]}'
```

Use this data to enrich scoring decisions (industry benchmarks, conversion patterns).

### Step 2: Pull Oracle-Hot Contacts from GHL

Query the GHL proxy for all contacts tagged `oracle-hot`:

```bash
curl -s -H "Origin: https://thecalltaker.com" \
  -H "Authorization: Bearer $PROXY_SECRET" \
  "https://thecalltaker.com/api/ghl/contacts?locationId=tQb9YmrGDrdVUJYPKrsY&query=oracle-hot&limit=100"
```

If the proxy isn't available, fall back to direct GHL API:
```bash
curl -s -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: 2021-07-28" \
  "https://services.leadconnectorhq.com/contacts/?locationId=tQb9YmrGDrdVUJYPKrsY&query=oracle-hot&limit=100"
```

### Step 3: Score Each Contact (1-100)

Score formula:

| Signal | Points | How to Check |
|--------|--------|--------------|
| Last activity < 1 hour | +25 | `dateUpdated` field |
| Last activity < 24 hours | +15 | `dateUpdated` field |
| Last activity < 7 days | +5 | `dateUpdated` field |
| Email opens > 3 | +20 | Check tags for `opened-3+` or custom field |
| Reply count > 0 | +20 | Check tags for `replied` or conversation history |
| High-value vertical (HVAC, Plumbing, Dental, Legal) | +10 | Industry tag |
| Medium-value vertical (Locksmith, Roofing, Towing) | +5 | Industry tag |
| Has company name | +5 | `companyName` field |
| Has phone + email | +5 | Both fields present |
| Demo call 120s+ | +15 | `hot-demo` tag |
| Demo call 60s+ | +10 | `engaged-demo` tag |
| Texted PILOT | +20 | `pilot-text-received` tag |
| Already contacted by Wallace | -10 | `contacted` tag |
| Marked do-not-contact | -100 | `do-not-contact` tag |

Cap at 100. Minimum 0.

### Step 4: Tag Critical Contacts

For any contact scoring **90+**:
1. Add tag `oracle-critical` in GHL:
```bash
curl -s -X POST \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: 2021-07-28" \
  -H "Content-Type: application/json" \
  -d '{"tags":["oracle-critical"]}' \
  "https://services.leadconnectorhq.com/contacts/{contactId}/tags"
```
2. Send ntfy alert:
```bash
bash ~/thecalltaker-ops/notify.sh \
  "ORACLE: Score 90+ — {name} @ {company}" \
  "{name} ({phone}) scored {score}/100. Vertical: {industry}. Last active: {lastActive}." \
  "urgent"
```

### Step 5: Write Hot Targets File

Write top 5 scored contacts to `~/thecalltaker-ops/hot-targets.json`:

```json
{
  "updated": "2026-03-19T14:30:00Z",
  "targets": [
    {
      "id": "ghl_contact_id",
      "name": "Greg",
      "company": "Carolina Locksmith",
      "phone": "(919) 608-3694",
      "email": "...",
      "industry": "locksmith",
      "score": 95,
      "lastActivity": "2026-03-19T14:00:00Z",
      "tags": ["oracle-hot", "oracle-critical", "hot-demo"],
      "lastContacted": null,
      "recommendedAction": "Call NOW — demo caller, high engagement"
    }
  ]
}
```

### Step 6: Log Run

Append to `~/thecalltaker-ops/logs/oracle-scanner.log`:

```
[2026-03-19T14:30:00Z] RUN: Scanned 35 contacts. Critical: 3. Top score: 95 (Greg @ Carolina Locksmith). Actions: tagged 3 oracle-critical, wrote hot-targets.json.
```

## Idempotency

- Scoring is stateless — safe to re-run any time
- Tagging is additive — adding `oracle-critical` to a contact that already has it is harmless
- hot-targets.json is overwritten each run (latest state wins)
- Duplicate ntfy alerts are deduped by the 30-min window in tct_common

## Error Handling

- GHL API 401/403 → Log "Auth error" and stop (don't spam)
- GHL API 429 → Log "Rate limited" and skip this run
- GHL API timeout → Log "Timeout" and skip
- No contacts found → Log "0 oracle-hot contacts" and write empty targets
- intelligence.json missing → Continue without enrichment data
