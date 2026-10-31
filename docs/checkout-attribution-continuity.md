# Email-to-checkout attribution continuity

An issued email pricing link must keep its opaque company correlation through the buyer's checkout. Browser attribution describes a touch; the server's immutable link registry, verified checkout, payment receipts and activation evidence determine business outcomes.

## Current public path

Bounded public GETs on October 31, 2026 UTC observed `/pricing` → `/card-checkout.html?plan=…` → protected `/onboarding/intake.html#setup`. The old `/setup.html` is retired; `/pre-checkout.html` returned an HTTP error. Public checkout configuration returned production SDK metadata. None of these reads submitted a form, loaded Square's SDK, enrolled a buyer or proved money moved.

The published offer still promises human onboarding review. The existing server configuration entrypoint also requires an exact per-customer owner decision. This change does not make onboarding unattended, change those promises, or grant customer/provider operating authority.

## Change

Pricing forwards a valid incoming email correlation and safe email campaign to all four current same-origin checkout anchors (three plans plus the mobile CTA) in an inline navigation step before external scripts. It does not store data, emit events, or add another telemetry producer. The canonical producer remains responsible for all browser events. Its capture step discards prior campaign/content when a different valid incoming correlation arrives, while retaining the buyer session and pending checkout.

Checkout reads its own explicit correlation without relying on the tracker. An explicit link takes its attribution from that link, rather than inheriting earlier stored campaign/content. New version-2 pending identities freeze normalized attribution, plan, correlation, buyer session and idempotency key, and verify the entire persisted snapshot before card tokenization. Checkout sends the frozen snapshot and retains it when the accepted attempt is stored. A lost response, reload or later tracker mutation cannot change the attribution on a retry.

A different explicit correlation or plan cannot replace an existing pending request. Invalid explicit correlations, corrupt storage and malformed snapshots hold before tokenization. Legacy accepted attempts retain status and protected setup recovery. Legacy uncertain attempts without a snapshot require reconciliation; the browser cannot reconstruct their original attribution or assume the earlier request was never accepted. A checkout prepared before tokenization can also retain its hold if the buyer changes plan or company link. This conservative exception remains an improvement opportunity; do not clear it automatically or mint another monetary identity.

No buyer form values, card token, payment credential or continuation token are added to the pending attribution snapshot. Existing customer setup capabilities remain in their existing body-only requests. Browser storage is not a security boundary: the server still owns validation, deduplication, billing and exact registry linkage.

## Validation and release

Tests execute actual inline pricing/checkout functions and the canonical producer in isolated VMs, including all three plans, absent/late tracking, stale company content, dropped responses, reloads, silent storage failure, conflicting links and legacy accepted recovery. Full form fixtures use synthetic Square and HTTP implementations and verify that conflict holds occur before tokenization. These are local behavioral tests, not real checkout or payment proof.

Release this website change separately from the unreleased CTOS runtime candidate. Review the exact commit and pass the existing website CI before an explicitly authorized publish/merge/deploy. The main website workflow automatically deploys to GitHub Pages on merge. Rollback is an exact revert through that reviewed release path under applicable authority; no SQL rollback is needed.
