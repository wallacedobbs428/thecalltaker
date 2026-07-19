# Website and Buyer Path Release Candidate V1

## Verdict

`BLOCKED_NOT_DEPLOYABLE`

The website source candidate is reconciled and locally QA-passing, but the production Square trial API currently returns `ok`, `plan`, `renewalAmount`, and `receipt` only. The candidate correctly requires a signed `setupToken` before opening setup. Deploying the website before the API issues and verifies that token would allow an enrollment to succeed but block the setup handoff. The page now prevents a duplicate submission and tells the buyer not to retry, but that is a safety fallback, not a launch-ready path.

## Release identity

- Branch: `codex/website-buyer-path-rc-v1-20260719`
- Base: `7f8fb8f30235f83629742a8ad108b761fc0efec9`
- Candidate commit: resolve with `git rev-parse HEAD` after the atomic commit; the final handoff records the immutable value.
- Deploy target if separately authorized after blocker closure: GitHub Pages, `thecalltaker.com`, `main`, `.github/workflows/deploy.yml`.
- Deployment authority in this work: none.

## Scope

- Homepage and Meet Gideon light/dark redesign.
- Pricing mobile menu and correct `$97`, `$497`, `$997+` plan visuals.
- Exact-plan pre-checkout, legacy checkout, card checkout, and setup continuity.
- Signed receipt/plan setup boundary in the public client.
- Retired pilot route.
- Demo claims and booking-language cleanup.
- FAQ, start, signup, terms, and privacy reconciliation.
- GitHub Pages clean-artifact inclusion for `/pilot/`.

## Changed files

- `.github/workflows/deploy.yml`
- `website/index.html`
- `website/pricing.html`
- `website/demo.html`
- `website/pilot/index.html`
- `website/pre-checkout.html`
- `website/checkout.html`
- `website/pay.html`
- `website/card-checkout.html`
- `website/setup.html`
- `website/setup-form.js`
- `website/faq.html`
- `website/start.html`
- `website/signup.html`
- `website/terms.html`
- `website/privacy.html`
- `tests/website-checkout-continuity.test.js`
- `tests/website-setup-form.test.js`
- `tests/website-stage1-proof.test.js`
- `tests/website-trial-funnel.test.js`
- `tests/website-release-candidate-v1.test.js`
- `docs/release-candidates/website-buyer-path-rc-v1-route-manifest.json`
- `docs/release-candidates/website-buyer-path-rc-v1-capability-inventory.md`
- `docs/release-candidates/WEBSITE-BUYER-PATH-RC-V1-2026-07-19.md`

## QA receipts

- Automated: `node --test tests/website-*.test.js` — 11/11 passing.
- Diff hygiene: `git diff --check` — passing.
- Local routes: homepage, pricing, demo, pilot, three plan-bound pre-checkouts, checkout, pay, setup, FAQ, start, signup, terms, and privacy returned HTTP 200.
- Desktop 1280×720: Meet Gideon light and dark verified with no horizontal overflow.
- Responsive matrix: homepage, pricing, demo, FAQ, and blocked setup checked at 320×568, 390×844, 430×932, and 768×1024 with no broken images or horizontal overflow after the narrow FAQ footer correction.
- Theme computed colors: light card `rgb(255,255,255)`, light heading `rgb(20,18,16)`, dark card `rgba(5,13,10,.96)`, dark heading `rgb(230,245,235)`.
- Pricing visual sources: `$97` bedside after-hours scene, `$497` receptionist/revenue-recovery scene, `$997+` woman/business-owner handshake scene.
- Production baseline: all audited routes returned 200 except `/pilot/`, which returned 404; the candidate adds a 615-byte inert redirect.
- Browser-engine limit: the executed visual matrix used the available in-app browser. A real Safari desktop run remains required before production proof can be called complete.

## Performance and asset notes

- Candidate HTML sizes: homepage 175,405 bytes; pricing 65,470; demo 54,591; setup 33,331; pilot redirect 615.
- Local HTTP responses completed in under 100 ms during the route sweep; these are development-server checks, not a production latency claim.
- No new third-party runtime dependency was added.
- Pilot dead form/tracking/notification code was removed instead of shipped behind a redirect.
- No horizontal overflow was observed across the executed responsive matrix after the narrow FAQ footer correction.

## Legal-review flags

- Terms and Privacy now match the current trial, renewal, cancellation, provider, tracking, and data-handling description used by the candidate.
- They are production-oriented business drafts, not attorney-approved documents, and the site does not claim attorney approval.
- Counsel review and an immutable approved-version receipt remain required before legal clearance can be promoted to proven.

## Required backend closure

Implement and test one shared signed setup-admission contract in the `call-taker-os` backend:

1. `POST /api/public/square-trial` returns `setupToken` only after enrollment succeeds.
2. The token binds plan ID, subscription/payment receipt reference, issued-at, expiry, and a nonce; it is signed server-side and contains no secret.
3. `POST /api/public/setup-intake` verifies signature, expiry, exact plan, receipt binding, and one-time/replay rules before accepting setup.
4. The setup payload maps the verified admission into the backend's required `billing_admission` contract.
5. Integration tests cover all three plans, invalid signature, expired token, plan substitution, receipt substitution, replay, API failure before enrollment, and missing token after enrollment.

Do not weaken the website back to an unsigned query-string gate to avoid this work.

## Deployment plan after blocker closure and exact authority

1. Rebase or cherry-pick the atomic candidate onto current `main` and rerun the complete website plus backend contract suites.
2. Verify the clean Pages artifact locally and confirm only whitelisted public files are present.
3. Obtain exact deploy authority naming the candidate commit, `main`, `.github/workflows/deploy.yml`, `thecalltaker.com`, and any required backend commit/deployment order.
4. Deploy backend first; verify config GET and contract tests without creating a live subscription.
5. Deploy the website through the named GitHub Pages workflow.
6. Validate cache-busted production routes, all three plan selections, Square card field rendering, and signed setup redirect.
7. Rebuild the Lane 4 traffic/readiness receipt against the deployed hashes. Keep paid traffic `HOLD/$0` until all required runtime receipts and legal/privacy clearance are current.

## Rollback plan

1. Revert the exact website candidate commit on `main` and redeploy the Pages workflow.
2. If backend closure shipped separately, revert the backend only after confirming the prior website does not depend on its response shape.
3. Purge/expire edge cache as supported, then validate cache-busted homepage, pricing, checkout, setup, terms, and privacy hashes.
4. Preserve failed-deploy and runtime evidence; do not delete enrollment or setup receipts.

## Provider and mutation receipt

- Square provider calls: none.
- Supabase/provider reads: none.
- Email, SMS, phone calls, webhooks, notification sends: none.
- Launchd/scheduler changes: none.
- Deployment, push, merge, traffic launch, spend, or billing changes: none.
- Secret values read, printed, changed, or committed: none.
- External state mutation: none.
