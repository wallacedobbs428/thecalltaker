# Setup Form Buyer Path QA - 2026-06-07

RIGHT lane scope: wire the public setup form into the website buyer path after Square checkout without mutating Bland, Square, SMS, email, calls, webhooks, or provider systems.

## Execution Summary

- Added a public setup form at `/setup.html`.
- Added a buyer-safe confirmation page at `/setup-confirmation.html`.
- Added local browser-only setup payload handling in `/setup-form.js`.
- Replaced old `/start.html` and `/signup.html` routes with redirects to `/setup.html`.
- Added setup-form links to homepage pricing, pricing page, FAQ CTA, checkout fallback, pay fallback, services CTA, and audit CTA.
- Kept the three live Square checkout URLs unchanged.
- Removed stale floating/exit callback JS behavior by turning removed-widget handlers into safe no-ops.
- Removed stale floating callback CSS selectors from the funnel stylesheet.

## Current Buyer Path

1. Visitor chooses a plan on homepage or pricing.
2. Plan button opens the correct Square checkout link.
3. Website copy and fallback links direct the buyer to `/setup.html` after checkout.
4. Buyer submits business details, summary destinations, hours, services, emergency rules, transfer number, greeting preference, and forwarding authorization.
5. Browser stores the setup receipt locally for the session and redirects to `/setup-confirmation.html`.
6. Confirmation page tells the buyer the setup form was received and that forwarding/testing must be confirmed before launch.

## Safe Staged Behavior

- No CTOS backend endpoint was found in the deploy repo.
- The public form does not pretend CTOS received a hosted backend submission.
- The form does not trigger SMS, email, calls, Bland, Square, or webhook actions.
- Default payment status is `paid_unverified`.
- If phone provider or forwarding status is unknown, the receipt status becomes `forwarding_instructions_needed`.

## Verified

- Required LEFT setup fields exist on `/setup.html`.
- Unknown phone provider submission succeeds and returns `forwarding_instructions_needed`.
- Missing required fields fail validation.
- Confirmation copy matches the approved receipt direction.
- True 390px mobile viewport measurement passes with zero horizontal overflow offenders.
- Mobile setup screenshot shows readable fields, no random green phone/callback circle, and a moon theme toggle.
- Mobile confirmation screenshot shows wrapped receipt copy and no random green phone/callback circle.
- Browser submit test redirected to `/setup-confirmation.html?status=forwarding_instructions_needed`.

## Commands Run

- `node tests/website-setup-form.test.js`
- `node tests/website-trial-funnel.test.js`
- `node tests/website-onboarding-safety.test.js`
- `node tests/website-client-regression.test.js`
- `git diff --check`
- Static scans for unsafe setup-call promises.
- Static scans for floating phone/callback widget markers.
- Local browser screenshots and true 390px overflow checks through Chrome device emulation.

## Remaining Blockers

- Square checkout itself was not modified in this pass. Buyers can see setup-form links on the website, but Square will not automatically force a return to `/setup.html` unless Square checkout/redirect settings are confirmed and approved.
- No hosted CTOS setup ingestion endpoint is wired in this deploy repo yet.
- `try-live.html` still contains a separate live demo flow that appears to initiate a real Bland call from the browser. RIGHT did not touch Bland/provider behavior under the current directive.

## Traffic Readiness

- Main website pricing-to-setup path: ready for controlled organic/outbound traffic with the stated staged behavior.
- Paid ads: still blocked until Square return/setup handoff and CTOS/backend intake are real.
- Provider automation: blocked pending Wallace/provider approval.
