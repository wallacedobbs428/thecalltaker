# Payment Link Mapping Audit - 2026-06-07

RIGHT lane scope: buyer-path link audit, form-first setup correction, and no-payment checkout safety. No card was entered, no payment was attempted, and no customer message/call was sent.

## Summary

Status: **public buyer path points to corrected Square checkout links pending deploy.**

Public pages now explain the scalable setup truth:

1. Choose a plan.
2. Checkout securely.
3. Complete the setup form.
4. CTOS builds the setup packet.
5. Same-day configuration begins from the completed form.
6. Forwarding/testing steps happen before launch.

## Link Map

| Source | Current link | Should route to | Status | Must fix | Blocked by Wallace/provider |
|---|---|---|---:|---:|---:|
| `pricing.html` After-Hours CTA | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/rQ8UtxYeF82XjX6RTnqJI1cBUDIZY` | same Square checkout, with form-first copy | Corrected locally and provider verified | No after deploy | No |
| `pricing.html` 24/7 CTA | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/Rj2p5FuHxMnVFeVo1d6RYNYH46SZY` | same Square checkout, with form-first copy | Corrected locally and provider verified | No after deploy | No |
| `pricing.html` Custom CTA | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/tLZqiyd4tReFcZItQuu0zniW80TZY` | same Square checkout, with form-first copy | Corrected locally and provider verified | No after deploy | No |
| `faq.html` trial CTA | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/Rj2p5FuHxMnVFeVo1d6RYNYH46SZY` | $497 Square checkout, with form-first copy | Corrected locally and provider verified | No after deploy | No |
| `checkout.html?plan=afterhours` | direct redirect | $97 Square checkout | Link OK | No | No |
| `checkout.html?plan=full247` | direct redirect | $497 Square checkout | Link OK | No | No |
| `checkout.html?plan=premium` | direct redirect | $997 Square checkout | Link OK | No | No |
| `pay.html` | direct redirect | $97 Square checkout | Link OK | No | No |
| `demo.html` post-demo cards | direct Square checkout links | matching Square checkout | Corrected locally and provider verified | No after deploy | No |

## Current Scan Result

- Public buyer-path pricing links use corrected final `checkout.square.site` URLs.
- Public site copy has been corrected locally to say setup form first.
- Local Square request templates now contain the required form-first Square-facing language.

## Remaining Payment Blockers

- Corrected Square hosted checkout copy has been read-only verified.
- Deploy and live click verification are required.
- Do not treat a Square checkout click as confirmed payment.
- Do not complete checkout or test payment without separate approval.
