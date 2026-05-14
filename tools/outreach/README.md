# CTOS Outreach Command Center

Phase 1/2 local command center for The Call Taker outreach.

This tool is intentionally no-send. It reads local JSON/CSV, validates fake/sample prospects, scores them, and writes local preview reports.

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
- `normalize_prospect.mjs`: normalizes manual intake fields into the scored prospect contract.
- `import_prospects.mjs`: dry-run CSV/JSON/single-record intake preview. It never contacts anyone.
- `example_import.csv`: fake manual import sample.
- `example_import.json`: fake manual import sample.
- `sms_approval_status.json`: current SMS approval gate. Defaults to blocked/no-send.
- `sms_templates.json`: human-style SMS drafts for review only.
- `generate_sms_approval_packet.mjs`: renders provider-review packet from local status/templates.
- `generate_sms_preview.mjs`: renders SMS drafts for Wallace review. It never sends.
- `sms_preview_sample.json`: fake sample merge data.
- `output/daily-queue.sample.md`: generated fake Wallace queue.
- `output/import-preview.sample.md`: generated fake import preview.

## Commands

```bash
node --check tools/outreach/score_prospects.mjs
node --check tools/outreach/generate_daily_queue.mjs
node --check tools/outreach/normalize_prospect.mjs
node --check tools/outreach/import_prospects.mjs
node tools/outreach/score_prospects.mjs
node tools/outreach/generate_daily_queue.mjs
node tools/outreach/import_prospects.mjs --input tools/outreach/example_import.csv --dry-run
node tools/outreach/import_prospects.mjs --input tools/outreach/example_import.json --dry-run
node tools/outreach/generate_sms_approval_packet.mjs
node tools/outreach/generate_sms_preview.mjs --scenario after_demo --prospect tools/outreach/sms_preview_sample.json
node tools/outreach/generate_sms_preview.mjs --scenario cold_candidate --prospect tools/outreach/sms_preview_sample.json
```

## Score Categories

- `A`: Wallace call review now.
- `B`: manual sequence review.
- `C`: nurture or re-research.
- `D`: bad fit or suppress.

## Intake Priority

Every business with a phone line can be evaluated, but not every business deserves outreach.

The importer supports `business_with_phone_line` as a generic classification, then uses A/B/C/D scoring to prioritize businesses with emergency demand, appointment value, high-ticket jobs, recurring call volume, after-hours need, weak answering paths, and owner/operator reachability.

## Next Build Lane

Build a private/local prospect storage location outside committed sample data and keep all provider adapters absent or dry-run only until Wallace explicitly approves live sending.
