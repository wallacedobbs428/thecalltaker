# The Call Taker — Agent Memory
# Last updated: 2026-03-14

## Repo layout (actual, on this machine)
- Repo root: /home/user/thecalltaker/
- Ops scripts: /home/user/thecalltaker/ops/
- Sales assets: /home/user/thecalltaker/sales/
- Website: /home/user/thecalltaker/website/
- Outreach sequences: /home/user/thecalltaker/outreach/ (created 2026-03-14, did NOT exist before)
- NO ~/thecalltaker-ops/ on this machine — ops scripts live in ops/ inside repo root

## File naming conventions observed
- State files: ops/<engine>-state.json
- Log files: ops/<engine>.log
- ntfy topics (standardized March 2 2026):
  URGENT=tct-urgent-Hk9UOEZR, SALES=tct-sales-63uYsIT9,
  SYSTEM=tct-system-vRsfXQRQ, ACTIVITY=tct-activity-cn1Aqa85,
  William=tct-william-Qm8nR3vK

## GHL API constants (confirmed from code)
- API key: pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35
- Location ID: tQb9YmrGDrdVUJYPKrsY
- Base URL: https://services.leadconnectorhq.com
- Contacts version header: 2021-07-28
- Conversations version header: 2021-04-15
- Email body field = "html" (NOT "message")
- User-Agent header required to avoid Cloudflare 403
- Pagination: use page= param (not offset=)

## Storm trigger (2026-03-14)
- Script: /home/user/thecalltaker/ops/storm-trigger.py
- State: /home/user/thecalltaker/ops/storm-trigger-state.json
- Triggers on WMO codes: 95, 96, 99, 65, 67, 75, 82
- Targets: GHL contacts tagged water-damage OR roofing
- City cooldown: 12h (prevents re-blast during same storm)
- Contact cooldown: 30 days
- ntfy goes to SALES topic on firing
- 28 metros with pre-cached lat/lon in METRO_COORDS dict

## Cold sequences (2026-03-14)
- File: /home/user/thecalltaker/outreach/cold-sequences-v2.md
- 5 industries: HVAC, Dental, Plumbing, Legal, Roofing
- 3 emails each: Day 1 pain, Day 3 follow-up, Day 7 breakup
- CTA always points to thecalltaker.com/try-live
- Sign-off: Wallace or W.
- GHL tags per send: seq-{industry}-1/2/3

## Industry map (from blast-engine-v2.py — 19 industries)
See /home/user/thecalltaker/ops/blast-engine-v2.py INDUSTRY_MAP dict.

## Voice agent
- Demo line: (615) 784-5747
- GHL agent ID: 695947c64b9ed67d8f1077ad
- Prompt: universal demo v5 (~263 words)
- NEVER overwrite demo line with single-industry prompt
- Client lines use industry-specific prompts in ops/jessica-voice-prompt-v6/v7.md
