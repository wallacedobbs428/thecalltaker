# Square Checkout Setup Call QA - 2026-06-06

RIGHT lane scope: approved Square payment-link creation, buyer-path link update, and no-payment validation.

## Result

Status: **Square checkout copy fixed.**

Each plan now routes to a fresh Square checkout page whose provider read-back confirms:

- Line-item name includes `AI setup call within 2 minutes`.
- Description says `After checkout, Gideon AI calls within 2 minutes to ask the questions needed for same-day setup.`
- `$0` trial checkout total is preserved.
- `checkout_redirect_url` is `null`.

## Current Links

| Plan | Short Square link | Final checkout URL |
|---|---|---|
| After-Hours Capture | `https://square.link/u/oHYfrPux` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/HywRLQ4aYHQ0ojpIbsnBPnrelqAZY` |
| 24/7 Call Coverage | `https://square.link/u/Z65m9l44` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/RFxESyTjwZQuIS2xceV8983Pvj8YY` |
| Premium Concierge Priority Setup | `https://square.link/u/Xm0k4F4D` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/PCGvURHQSoL8LnXbmQ3olB0imFBZY` |

## Buyer-Path Files Updated

- `website/index.html`
- `website/pricing.html`
- `website/demo.html`
- `website/faq.html`
- `website/checkout.html`
- `website/pay.html`

## Safety Notes

- No card was entered.
- No payment was attempted.
- No customer message was sent.
- No outbound call was sent.
- No secrets were printed.
- Square provider mutation did occur: three new payment links were created with Wallace approval.

## Remaining Blocker

The checkout page now promises a Gideon AI setup call within 2 minutes after checkout, but the live automation from verified Square payment event to outbound setup call is not yet verified. Next RIGHT/MIDDLE work should dry-run the Square payment event intake, then connect the approved voice-call provider only after Wallace approves the live-call test.
