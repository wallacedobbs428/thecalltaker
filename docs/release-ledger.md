# Release Ledger

Last updated: May 14, 2026

This ledger is the source of truth for what is live, what is only local or branch-only, and what remains open. Future lanes should update this file when release state changes.

## Current Live Release State

- Last reconciled against `origin/main`: `825699d`
- Note: docs-only ledger pushes may advance `origin/main` after this line is written. Verify the current hash with `git rev-parse --short origin/main`.
- GitHub Pages deploy artifact: `website/`
- Live website: `https://thecalltaker.com/`
- Latest completed live releases:
  - May 14 homepage/demo release
  - Hero regression fix
  - `website/client` safety-port
  - onboarding live-claim cleanup
  - premium offer strategy docs
  - claim-safety polish release
  - American Surgical proof engine docs
  - no-send outreach command center
- Pages verified live:
  - `https://thecalltaker.com/`
  - `https://thecalltaker.com/demo.html`
  - `https://thecalltaker.com/pay.html`
  - `https://thecalltaker.com/pilot/`
- Latest workflow status:
  - `adcde6b` claim-safety polish: Deploy to GitHub Pages, Hero Headline Regression, and Notify on push passed.
  - `6c8c670` release ledger docs: Notify on push passed. No website deploy was required.
  - `825699d` release ledger reconciliation docs: Notify on push passed. No website deploy was required.

## Completed Tracks

| Track | Commit | Pushed | Deployed | Live Verified | Notes |
| --- | --- | --- | --- | --- | --- |
| May 14 homepage/demo release | `a31caf4`, `47fb718`, `cf2ea95`, `2ab96fc` | yes | yes | yes | Integrated stability, call-flow QA, and demo polish into the May 14 website release. |
| Hero regression fix | `402deb1` | yes | yes | yes | Restored and guarded the homepage hero headline regression; live workflow passed. |
| `website/client` safety-port | `b5ff7f9` | yes | yes | yes | Ported safe setup flow into deployed `website/client`; root `client/` remains non-live-facing. |
| Onboarding live-claim cleanup | `2fbbdd8` | yes | yes | yes | Hardened deployed onboarding copy so it does not imply live provider activation. |
| Premium offer strategy docs | `6b94930` | yes | not applicable | not applicable | Docs-only strategy record. LEFT does not own pricing strategy. |
| Claim-safety polish release | `adcde6b` | yes | yes | yes | Softened fake-live and unsupported claim language, cleaned proof wording, and fixed demo mobile CTA pressure. |
| American Surgical proof engine docs | `5d58a2c` | yes | not applicable | not applicable | Docs-only proof strategy record. Catch-up email, website proof, and outreach proof are still not complete. |
| Outreach Revenue Machine architecture | `5f6d506` | yes | not applicable | not applicable | Docs-only architecture record. No sending enabled by this commit. |
| No-send outreach command center | `a9ca327` | yes | not applicable | not applicable | Local tooling/docs for no-send outreach queue work. No provider sending is enabled. |
| Release ledger reconciliation | `825699d` | yes | not applicable | not applicable | Docs-only update after parallel lane progress. Notify on push passed. |

## Open Tracks

### Outreach Revenue Machine

- Architecture committed: `05d49ce`; superseded/live docs committed in `5f6d506`.
- Current status: architecture docs and no-send command center are on current `origin/main`.
- Command center build: `a9ca327`.
- Phase 2 intake/import: open unless a future `origin/main` commit confirms it.
- Sending: not enabled.
- Provider calls/webhooks/email/SMS: not approved from this lane.
- Integration status: docs/tooling are pushed, but outreach sending remains disabled unless Wallace explicitly approves it.

### American Surgical Proof Engine

- Strategy docs: pushed in `5d58a2c`; Wallace acceptance and implementation remain pending.
- Catch-up email drafts: branch commit `2855a99` exists, but it is not included in current `origin/main`.
- Catch-up email send/Gmail draft: not sent and not created from this lane.
- Website proof: not added.
- Outreach proof: not integrated.
- Current status: docs exist on `origin/main`, but this is not a sent email, live website proof, or integrated outreach proof.

## Lane Ownership Rules

- LEFT owns release truth, checklist governance, deployment readiness, live verification, rollback framing, and release hygiene.
- MIDDLE owns offer strategy, premium pricing architecture, proof strategy, and business positioning decisions.
- RIGHT owns outreach and revenue-machine implementation.
- One topic gets one owner lane.
- No cross-lane ownership unless Wallace explicitly changes it.
- LEFT may make claim-safety edits only when directly tied to release hygiene or live-site safety.

## Definition Of Done

Nothing is complete until it is:

1. Built.
2. Committed.
3. Integrated.
4. Pushed.
5. Deployed, if applicable.
6. Live verified, if applicable.
7. Accepted by Wallace.

Local work, branch-only work, screenshots, reports, and unpushed commits are not done.

## Current Warnings

- Root `client/` is not live-facing unless code is moved under `website/` or the deploy workflow changes.
- `website/` is the GitHub Pages deploy artifact.
- Do not make provider/live activation claims unless the live provider state has been verified and approved.
- Do not enable or run outreach sending without Wallace approval.
- Do not publish a public `$2,500` package unless future MIDDLE-owned strategy changes approve it.
- Do not edit payment/Square config from LEFT release hygiene work.

## Next Best Moves

- RIGHT: finish outreach Phase 2 intake/import without enabling sending.
- MIDDLE: reconcile American Surgical catch-up email drafts, website proof, and outreach proof integration.
- LEFT: maintain this release ledger and verify every new push that affects the live site.
