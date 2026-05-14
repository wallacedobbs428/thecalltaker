# Outreach Command Center Phase 1

## Purpose

This document explains the no-send CTOS Outreach Command Center implemented in `tools/outreach/`.

Wallace should be able to answer:

1. Who should I contact?
2. Why are they a fit?
3. What pain angle should I use?
4. What proof angle is allowed?
5. What next action should happen?
6. Should this be self-close education or a Wallace call?
7. What should not be sent yet?

## Current Status

- Local tooling exists.
- Fake sample prospects exist.
- Scoring works across A/B/C/D categories.
- Daily queue generation works.
- No sending exists.
- No provider writes exist.
- No real prospect data is committed.

## Implementation

Files:

- `tools/outreach/prospect_schema.json`
- `tools/outreach/sample_prospects.json`
- `tools/outreach/score_prospects.mjs`
- `tools/outreach/generate_daily_queue.mjs`
- `tools/outreach/output/daily-queue.sample.md`
- `tests/outreach-command-center.test.mjs`

## Manual Workflow

1. Research a prospect from public, lawful sources.
2. Store the prospect in a private/local data file, not in committed sample data.
3. Validate and score the prospect locally.
4. Open the generated daily queue.
5. Wallace reviews A leads first.
6. B leads go to manual sequence review.
7. C leads stay in nurture.
8. D leads are suppressed.

## No-Send Boundary

This phase does not:

- send email
- send SMS
- make calls
- trigger webhooks
- write to any CRM
- write to providers
- scrape
- deploy
- change payment configuration

The command center only prints local scoring output and writes a local Markdown report.

## Data Boundary

Committed data must remain fake. Use `example.invalid`, fake phone numbers, and fake names only.

Real prospect records belong in a private, ignored, or operator-approved storage location in a later lane.

## Acceptance Criteria

- The sample data validates.
- The scoring output includes A/B/C/D categories.
- The daily queue includes Wallace next actions.
- The system remains no-send.
- Provider/sending pattern scans remain clean or only match no-send documentation.
