# Website Monitor Recheck Ready Packet

## Current Status

Prepared for MIDDLE Website Monitor recheck after RIGHT website trust/conversion sprint.

## Pages To Check

- `/`
- `/pricing.html`
- `/faq.html`
- `/checkout.html`
- `/pay.html`
- `/setup.html`
- `/setup-confirmation.html`
- `/favicon.svg`
- `/site.webmanifest`
- `/og-image.png`

## Expected Results

| Area | Expected |
| --- | --- |
| Homepage | Offer clear, pricing path visible, social metadata clean |
| Pricing | $97/$497/$997+ plans, Square links, setup fallback |
| FAQ | Honest setup/payment/forwarding answers |
| Checkout/pay | Redirect to Square with setup fallback copy |
| Setup | Guided setup wizard, "Already checked out?" handoff, staged submit |
| Confirmation | Packet in review, no blank buttons, no live-routing claim |
| Text Us | SMS-only support CTA |
| Try-live safety | No provider call trigger |
| Brand icon | TCT monogram, no visible generic phone favicon |
| OG preview | Clean 1200x630 image, no fake stats |

## Known Blockers

- Square `redirectUrl:null` remains.
- Rendered Square item copy needs manual browser/Square-dashboard proof.
- Legacy generated pages still contain old claims and are not ready for scaled traffic.

## Traffic Recommendation

- Stage 1 only if fake customer test passes and Square fallback/handoff is accepted by MIDDLE/Wallace.
- Stage 2 and paid ads remain blocked.
- RIGHT does not approve scalable traffic from this packet alone.

## Safety Status

- Provider actions: none.
- SMS sent: none.
- Emails sent: none.
- Calls placed: none.
- Square mutation: none.
- Credential values exposed: no.
