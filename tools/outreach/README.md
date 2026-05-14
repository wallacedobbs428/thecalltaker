# CTOS Outreach Command Center

Phase 1 local command center for The Call Taker outreach.

This tool is intentionally no-send. It reads local JSON, validates fake/sample prospects, scores them, and writes a local Wallace daily queue report.

## Safety Locks

- No real prospect data is committed here.
- No SMTP.
- No Twilio.
- No CRM writes.
- No webhook calls.
- No provider endpoints.
- No automatic contact.
- No scraping.
- No payment or pricing changes.
- Output is local Markdown only.

## Files

- `prospect_schema.json`: required prospect shape.
- `sample_prospects.json`: fake sample data using `example.invalid`.
- `score_prospects.mjs`: validates and scores prospects.
- `generate_daily_queue.mjs`: writes `output/daily-queue.sample.md`.
- `output/daily-queue.sample.md`: generated fake Wallace queue.

## Commands

```bash
node --check tools/outreach/score_prospects.mjs
node --check tools/outreach/generate_daily_queue.mjs
node tools/outreach/score_prospects.mjs
node tools/outreach/generate_daily_queue.mjs
```

## Score Categories

- `A`: Wallace call review now.
- `B`: manual sequence review.
- `C`: nurture or re-research.
- `D`: bad fit or suppress.

## Next Build Lane

Build a private/local prospect storage location outside committed sample data, add import validation, and keep all provider adapters absent or dry-run only until Wallace explicitly approves live sending.
