# American Surgical Proof Engine

## Executive Decision

American Surgical is the current proof client for The Call Taker's qualified-call workflow. The proof should be used carefully: it can support internal qualification, sales-call context, outreach personalization, and future case-study work, but it should not become public named proof until Wallace and the client approve the framing.

The current safest proof angle is not revenue. It is operational filtering:

- Gideon handled real calls in an active medical-supply workflow.
- Gideon separated team-worthy requests from lower-priority/noise calls.
- Qualified handoffs were reviewed before client delivery.
- Lower-value calls were suppressed instead of bothering the client.

Do not claim booked revenue, guaranteed recovered revenue, automatic order completion, zero missed calls, or fully automated provider routing unless separate proof exists.

## Audited Proof Assets

### Repo Assets

- `website/client-portal/data/f2cc5aff26fe3564f1da876c49949444ee058bfb6c32818a.json`
  - Identifies American Surgical Specialties Company as an active medical/surgical supply client.
  - Shows an After-Hours plan and `ctos_supabase_ct_calls` as the stats source.
  - Is stale for the current proof window: generated on `2026-04-23` and shows zero calls. Do not use it to substantiate May call counts.
- `website/client-portal/index.html`
  - Displays client dashboard metrics from static JSON snapshots.
  - Useful as dashboard context, not as current proof.
- `website/shared/proof-metrics.json`
  - Contains aggregate public proof metrics for the website.
  - Not American Surgical-specific. Do not use these numbers as American Surgical proof.
- `sales/case-study-template.md`
  - Clearly hypothetical/template material. Do not use as real proof.
- `website/shared/case-studies-data.js`
  - Contains legacy/general case-study style data.
  - Do not combine it with American Surgical proof unless every claim is separately verified and approved.

### Adjacent Operations Assets

The strongest American Surgical proof artifacts currently live outside the website repo in local operations/business-brain material:

- `business-brain/client-operations/AMERICAN-SURGICAL-PROOF-BRIEF.md`
- `business-brain/client-operations/AMERICAN-SURGICAL-DAILY-QUALIFIED-HANDOFF-RULES.md`
- `business-brain/client-operations/AMERICAN-SURGICAL-QUALIFIED-CALLS-CATCH-UP-PREVIEW.md`
- `business-brain/golden-business-sprint-review/god-mode/AMERICAN-SURGICAL-PROOF-ACCEPTANCE-CRITERIA.md`
- `thecalltaker-ops/reports/american-surgical-final-proof-summary-2026-05-13.json`
- `thecalltaker-ops/reports/american-surgical-final-proof-asset-2026-05-13.md`
- `thecalltaker-ops/reports/american-surgical-qualified-catchup-live-2026-05-13.json`

Those operations artifacts substantiate the high-level proof counts and delivery concept, but raw proof files can contain private caller details. Do not copy raw call details, phone numbers, transcripts, item numbers, purchase-order context, provider message IDs, or internal tokens into website copy.

## Substantiated Proof Facts

Use these only with the governance rules below:

- Active proof client: American Surgical.
- Industry context: medical/surgical supply.
- Verified sender path: The Call Taker notification sender.
- Client inbox path: American Surgical sales inbox.
- Current proof window: calls since May 4, 2026.
- Total calls evaluated: 14.
- Qualified/team-worthy calls identified: 4.
- Suppressed/lower-value calls: 10.
- Qualified themes included quote requests, instrument/item requests, order or purchase-order intent, and product/shipping follow-up.
- The proof value is filtering and handoff quality, not guaranteed revenue.
- Recurring automation must remain disabled until Wallace explicitly approves it.

## Proof Usage Levels

### Level 1: Internal Only

Allowed:

- Named client.
- Exact high-level counts.
- Operational architecture notes.
- Delivery status summaries.
- Qualification/suppression logic.
- Redacted proof packet references.

Not allowed:

- Raw caller details.
- Caller phone numbers.
- Raw transcripts.
- Purchase-order numbers.
- Exact item numbers.
- Provider message IDs.
- Unredacted email bodies.
- Secrets, tokens, or provider dashboard data.

### Level 2: Anonymized Sales-Call Proof

Allowed:

- "In one active medical-supply workflow..."
- Exact counts if Wallace approves the sales-call framing.
- Themes of team-worthy calls.
- Explanation of suppression as client attention protection.

Example:

> In one active medical-supply workflow, Gideon evaluated 14 calls since May 4, surfaced 4 that appeared team-worthy, and suppressed 10 lower-priority/noise calls before bothering the client.

### Level 3: Anonymized Website Proof

Allowed only after Wallace approves public use:

- Anonymous industry label.
- No client name.
- No private caller details.
- Conservative operational framing.

Safer website line:

> In an active medical-supply workflow, Gideon helped separate team-worthy requests from low-priority noise before handoff review.

Use exact counts on the website only after a claim-safety review confirms the source, date range, and redaction rules.

### Level 4: Named Case Study

Requires:

- Wallace approval.
- Client approval for named use.
- Redacted proof packet.
- Approved date range.
- Approved screenshots/assets.
- Final claim-safety review.

Until then, do not publish "American Surgical" as named public proof.

## Safe Proof Package Draft

### One-Sentence Summary

In one active medical-supply workflow, Gideon evaluated 14 calls since May 4, identified 4 that appeared team-worthy, and suppressed 10 lower-priority/noise calls before client handoff review.

### Sales-Call Proof Line

This is not just AI answering the phone. In one active medical-supply workflow, the useful work was filtering 14 calls into 4 worth team attention and 10 that were not worth interrupting the client.

### Outreach-Safe Proof Line

We are using an active medical-supply workflow to prove the model: capture the calls, identify the few worth team attention, and suppress the noise.

### Website-Safe Proof Line

In an active medical-supply workflow, Gideon helped separate team-worthy requests from low-priority noise before handoff review.

### What Not To Say

- "Gideon generated revenue for American Surgical."
- "Gideon booked orders automatically."
- "American Surgical proves every missed call becomes money."
- "American Surgical had zero missed calls."
- "The system guarantees recovered revenue."
- "Provider routing is fully automated."
- "Every call is answered and resolved."
- "SMS, email, CRM, CTOS, and follow-up workflows are fully live" unless each path has current proof.

## Daily Qualified-Call-Only System Spec

### Send To Client

Send only qualified, team-worthy handoffs that appear to require American Surgical action:

- quote requests,
- product or instrument inquiries,
- order status,
- purchase-order intent,
- shipping or delivery questions,
- return/repair/RMA,
- warranty,
- account/billing/invoice,
- facility or sales follow-up.

Each qualified handoff should include only the minimum useful operational details:

- caller name if captured,
- callback number if captured and needed,
- facility/company if captured,
- call time,
- plain-English reason for call,
- what Gideon captured,
- what remains unresolved,
- urgency or callback indicator,
- recommended next move,
- call/audit ID.

### Suppress

Suppress calls that are:

- wrong number,
- spam/vendor solicitation,
- patient or medical-advice style calls,
- too short to determine intent,
- missing a usable callback path when one is required,
- low-confidence noise,
- not actionable for the American Surgical team,
- duplicates already processed.

Suppressed calls still count as proof of attention filtering, but they should not be sent as action items.

### Wallace Review

Wallace should review:

- ambiguous qualification cases,
- any first run after a code or policy change,
- any catch-up batch,
- any public-facing proof framing,
- any recurring workflow activation.

### Daily Summary Email Rule

Do not send empty daily digests by default. If no qualified unsent calls exist:

- send zero client emails,
- record the no-send result internally,
- preserve the state needed to prove no duplicates were sent.

If Wallace wants a daily internal operator summary, keep it separate from the client handoff path.

### CTOS Proof Storage

CTOS should store proof safely with a redacted operational ledger:

- client ID or slug,
- call ID,
- qualification status,
- suppression reason if suppressed,
- handoff status,
- delivery provider label,
- delivery timestamp when applicable,
- idempotency key,
- audit row ID,
- operator approval marker for live sends,
- redacted summary,
- private-detail pointer, not raw private details in public exports.

Suggested statuses:

- `qualified_pending_review`
- `qualified_sent`
- `suppressed_noise`
- `suppressed_wrong_number`
- `suppressed_duplicate`
- `send_failed`
- `send_skipped_duplicate`

## Catch-Up Email Strategy

### Purpose

The American Surgical catch-up email should close the gap between captured calls and the now-approved qualified handoff path. It should give the team only useful calls to act on and set the expectation that future emails are qualified-only.

### Include

- Date range covered.
- Short note that only qualified calls are included.
- The 4 qualified/team-worthy call summaries.
- Clear next action for each qualified item.
- A concise note that lower-priority/noise calls were suppressed.
- Calm transition language for future qualified-only handoffs.

### Do Not Include

- Suppressed calls as action items.
- Raw transcripts.
- Internal debug details.
- Provider implementation details.
- Secrets or tokens.
- Revenue claims.
- Claims that Gideon completed work the team still needs to do.
- Defensive explanations of the setup path.

### Tone

Use a calm operator tone:

- concise,
- practical,
- no hype,
- no apology spiral,
- focused on what the team should do next.

Safe structure:

```text
Subject: Gideon catch-up: qualified calls since May 4

Quick catch-up from Gideon. This includes only calls that appeared to need team follow-up. Lower-priority/noise calls were filtered out so your team does not have to sort through them.

Qualified follow-ups:
1. [redacted summary + recommended next move]
2. [redacted summary + recommended next move]
3. [redacted summary + recommended next move]
4. [redacted summary + recommended next move]

Going forward, Gideon will only send qualified handoffs when there is something worth team attention.
```

Do not send this email from this document. Do not create a Gmail draft unless Wallace asks for it in a separate task.

## Future Website / Outreach Checklist

- Verify the proof source files and date range.
- Produce a redacted public proof packet.
- Get Wallace approval for anonymous proof language.
- Get client approval before named public use.
- Keep raw caller details out of website and outreach assets.
- Run a claim-safety scan before publishing any proof copy.
- Keep revenue claims out unless the client verifies downstream revenue.
- Keep provider/backend activation claims out unless current live evidence exists.
- If proof is added to the website, deploy and live-verify after approval.
- If proof is added to outreach, keep it anonymized unless named approval exists.

## Ownership Rule

MIDDLE owns American Surgical proof strategy and governance.

LEFT may track claim-safety release status and website-safe copy gates.

RIGHT may use only approved, anonymized proof lines for outreach and must not alter proof claims or introduce named client claims.
