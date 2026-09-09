# Square Trial Checkout

Square is the approved public payment provider for The Call Taker trial funnel.
The website uses Square Web Payments inside the plan-preserving card checkout;
it does not send buyers through public `square.link` payment links.

Do not add Stripe checkout links to the public website, and never let a buyer
reach a different plan's checkout.

## Current Public Route State

| Plan | Monthly Price After Trial | Public card checkout route |
| --- | ---: | --- |
| After-Hours Capture | `$97/mo` | `/card-checkout.html?plan=afterhours` |
| Revenue Recovery System | `$497/mo` | `/card-checkout.html?plan=full247` |
| Operational Infrastructure | `$997+/mo` | `/card-checkout.html?plan=custom` |

The checkout must visibly state that no money is due today, the card is stored
by Square, the monthly amount begins after 14 days, and cancellation before
renewal prevents the next charge.

## Payment Method Compatibility

The public offer is a recurring subscription with a 14-day free phase. Square
requires a storable payment card for that contract. Credit and debit cards are
therefore the production payment methods for this checkout.

Square advertises Apple Pay, Google Pay, Cash App Pay, and Afterpay on eligible
one-time Payment Links, but those methods are not valid substitutes for a card
on file in this recurring-subscription flow. Square suppresses wallet buttons
on a correctly configured subscription link even when the generic accepted
payment-method flags are enabled. Do not show a fake wallet button, and do not
route a subscription buyer to a one-time `$0` or first-month order to make a
wallet appear.

Provider verification on 2026-09-09 also confirmed that the Checkout API's
subscription variation belongs at
`checkout_options.subscription_plan_id`. Putting it inside `quick_pay` is
silently ignored and creates a one-time order instead of a subscription.
For the current two-phase production variations, `quick_pay.price_money` must
match the paid monthly phase: Square still renders `$0 due today` from the free
phase, while a `$0` quick-pay override incorrectly renders `$0/month` after the
trial. Both the placement and the renewal amount are regression-tested.

## Website Behavior

- Pricing-card buttons route directly to the matching `/card-checkout.html` plan.
- The legacy `/checkout.html?plan=...` route preserves the selected plan and
  continues to the same card checkout.
- `website/card-checkout.html` fetches its public Square application and
  location configuration from the protected `square-trial` endpoint.
- The buyer must enter required contact details and explicitly consent to card
  storage before the trial button becomes available.
- An accepted, correlated checkout can receive a short-lived server-issued
  setup continuation while payment confirmation and activation remain separate
  provider-backed states.

## Checkout Change Validation

1. Keep all three routes above distinct and plan-bound.
2. Confirm the visible no-charge-today, renewal, and cancellation wording is
   accurate before and after JavaScript loads.
3. Run:

```bash
node tests/website-checkout-continuity.test.js
node tests/website-release-candidate-v1.test.js
node scripts/websiteaudit.js
git diff --check
```

4. After deployment, load each plan route and confirm the Square card field
   becomes available. Do not enter card details or complete an order during QA.
5. Confirm the page explains why one-time wallet methods are unavailable for
   the recurring trial instead of implying that Square or the browser failed.

## Safety Rules

- Do not create public checkout links for the `$2,500` implementation setup.
- Do not imply provider routing, SMS/email notifications, backend sync, CTOS,
  CRM, or booking automation is active from checkout alone.
- Do not send buyers to a Square link for the wrong monthly tier.
- Do not add Stripe links to public trial pages.
