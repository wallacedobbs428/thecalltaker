# CTOS Execution Adapters

Purpose: define how CTOS connects policy-based revenue workflows to real providers without bypassing safety, limits, or logging.

## Adapter Rule

An adapter may execute only when:

- the campaign policy allows the action
- the provider connection is present
- the action passes channel limits
- the lead/message is source-backed
- no escalation trigger exists
- the adapter logs the result back into CTOS

## Providers

- Instagram: inbound DMs, outbound DMs, low-risk replies, follow-up scheduling
- Instantly: campaign draft, approved list import, campaign start, reply/bounce tracking
- Facebook: group posts, DMs if supported, comments/replies, lead creation
- Square: payment status reads and webhook handling; no product/link mutation from CTOS

## Logging

Every adapter write must update:

- queue item status
- message history JSONL
- lead stage
- revenue scoreboard if revenue movement occurred
- escalation queue if blocked or outside policy

## Failure Handling

If a provider blocks, rate-limits, or returns trust-risk errors, CTOS must:

1. stop the queue item
2. mark `failed_provider_block`
3. log the provider class without secrets
4. create an escalation if revenue-critical
5. avoid retry loops until policy permits retry

## Secrets

Adapter specs list env var names only. Values must never be printed or stored in CTOS.
