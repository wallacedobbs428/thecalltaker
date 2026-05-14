# Outreach Prospect Intake and Import

Status: Phase 2 local/no-send workflow.

This workflow turns manually researched prospects into normalized, scored outreach records. It does not scrape, send messages, call prospects, write to a CRM, or touch provider systems.

## Inputs

- Manual CSV import: `tools/outreach/example_import.csv`
- Manual JSON import: `tools/outreach/example_import.json`
- Single prospect JSON object through `--single`
- Dry-run preview only through `--dry-run`

Committed examples must use fake `example.invalid` domains and fake phone numbers. Real prospect lists belong in a private local workspace outside git until Wallace approves a storage policy.

## Normalization

The importer normalizes:

- industry aliases such as `plumber` to `plumbing`
- category aliases such as `emergency service` to `emergency_service`
- phone numbers into a safe display format when possible
- public business email format, if present
- missing optional fields into `unknown` or `not researched`

It adds:

- `data_source`
- `import_status`
- `review_required`
- `compliance_notes`

Every normalized record keeps the no-send boundary in its compliance notes.

## Rejected Records

Records are rejected when they are missing required intake fields, contain invalid public email syntax, use private-looking personal email domains in sample imports, or use non-example domains in committed sample files.

Rejected records appear in the preview with reasons. They are not scored.

## Every Business With A Phone Line

The Call Taker can evaluate every business with a phone line, but eligibility is not priority.

`business_with_phone_line` exists for generic prospects where missed-call value is not yet proven. These records should stay lower priority until research confirms at least one strong signal:

- emergency demand
- appointment value
- high-ticket job value
- after-hours need
- recurring call volume
- poor answering path
- owner/operator reachable

A/B/C/D scoring decides action:

- `A`: Wallace manual call review now
- `B`: manual sequence review
- `C`: nurture or re-research
- `D`: suppress or bad fit

## Commands

```bash
node tools/outreach/import_prospects.mjs --input tools/outreach/example_import.csv --dry-run
node tools/outreach/import_prospects.mjs --input tools/outreach/example_import.json --dry-run
node tools/outreach/import_prospects.mjs --single '{"business_name":"Example HVAC","industry":"hvac","category":"emergency_service","phone":"555-010-1212","website":"https://example.invalid/example-hvac","city":"Huntsville","state":"AL","source_url":"https://example.invalid/sources/example-hvac"}' --dry-run
```

The output is local Markdown at `tools/outreach/output/import-preview.sample.md` unless `--output` is provided.

Private local researched prospects can be previewed without committing them:

```bash
node tools/outreach/import_prospects.mjs --input tools/outreach/private/prospects.csv --private-local --dry-run
```

Private mode accepts real researched domains locally, but it still does not send anything. `tools/outreach/private/` and `tools/outreach/output/private/` are ignored by git.

## Safety Boundary

- No email sending.
- No SMS sending.
- No phone calls.
- No webhook calls.
- No CRM, GHL, LeadConnector, or provider writes.
- No scraping.
- No real private prospect data in git.
- No activation, routing, or backend sync.

SMS copy, when later approved and compliant, should sound like a real human text instead of polished corporate grammar. That does not change the no-send status of this phase.
