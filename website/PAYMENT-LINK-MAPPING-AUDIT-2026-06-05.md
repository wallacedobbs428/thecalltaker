# Payment Link Mapping Audit - 2026-06-05

RIGHT lane scope: buyer-path link audit, approved Square payment-link creation, and no-payment checkout verification. No card was entered, no payment was attempted, and no customer message/call was sent.

## Summary

Status: **verified Square checkout links restored on buyer path.**

Action taken: Wallace approved Square checkout link repair on 2026-06-06. RIGHT created fresh Square payment links for all three plans, verified provider read-back, and installed final `checkout.square.site` URLs in the public buyer path. Each new Square link includes the setup-call reassurance: `After checkout, Gideon AI calls within 2 minutes to ask the questions needed for same-day setup.`

## Link Map

| Source | Previous/current link | Should route to | Status | Must fix | Blocked by Wallace/provider |
|---|---|---|---:|---:|---:|
| `pricing.html` After-Hours CTA | old Square checkout | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/HywRLQ4aYHQ0ojpIbsnBPnrelqAZY` | Fixed to verified Square link | No | No |
| `pricing.html` 24/7 CTA | old Square checkout | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/RFxESyTjwZQuIS2xceV8983Pvj8YY` | Fixed to verified Square link | No | No |
| `pricing.html` Custom CTA | old Square checkout | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/PCGvURHQSoL8LnXbmQ3olB0imFBZY` | Fixed to verified Square link | No | No |
| `faq.html` trial CTA | old 24/7 Square checkout | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/RFxESyTjwZQuIS2xceV8983Pvj8YY` | Fixed to verified Square link | No | No |
| `checkout.html?plan=afterhours` | old fallback | new $97 Square checkout | Fixed to direct Square redirect | No | No |
| `checkout.html?plan=full247` | old fallback | new $497 Square checkout | Fixed to direct Square redirect | No | No |
| `checkout.html?plan=premium` | old fallback | new $997 Square checkout | Fixed to direct Square redirect | No | No |
| `pay.html` | old $97 Square link | new $97 Square checkout | Fixed to direct Square redirect | No | No |
| `demo.html` post-demo plan cards | old Square checkout | matching new Square checkout | Fixed to verified Square links | No | No |
| `services.html` setup CTA | non-primary path | `/pricing.html` or setup review path | No change this pass | No | No |

## Current Scan Result

- Public buyer-path pricing links use final `checkout.square.site` URLs.
- Provider read-back confirmed all three new Square links have `checkout_redirect_url: null`.
- Provider read-back confirmed all three line-item names include `AI setup call within 2 minutes`.

## Temporary Conversion Path

- Homepage plan CTAs: direct to matching Square checkout.
- Pricing plan CTAs: direct to matching Square checkout.
- FAQ trial CTA: direct to $497 Square checkout.
- Old checkout URLs: redirect to matching Square checkout.
- Old pay URL: redirects to new $97 Square checkout.

## Remaining Payment Blockers

- Actual two-minute post-payment AI setup-call automation still needs verified Square payment event source and live-call test approval.
- Do not treat a Square checkout click as confirmed payment.
- Do not treat checkout copy alone as proof that the setup-call automation fired.
