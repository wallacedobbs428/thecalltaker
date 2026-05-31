# Right Lane Square QA Handoff

Date: 2026-05-31

## Root Cause

The old Square payment links carried a provider-side checkout return URL back to `https://thecalltaker.com/client/onboarding.html`. The repo-side click hijacker was already removed; the remaining failure was Square link configuration.

Left Builder Agent used the connected Square credentials to create fresh Square payment links for all three current pricing tiers. The new links omit any checkout redirect URL and provider read-back shows `checkout_redirect_url: null` for each new link.

## Provider Action Completed

No payment was made. No card was entered. No customer message, deploy, DNS change, or secret output occurred.

Fresh Square links created:

| Plan | New button href | Square final checkout URL observed |
| --- | --- | --- |
| $97 After-Hours Capture | `https://square.link/u/cSiXiuLx` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/hJjmqQxRSZpjYjmSHgAXinmluuNZY` |
| $497 24/7 Call Coverage | `https://square.link/u/TQseWnAY` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/1tWHNkKGJtpgOJO1AfVRb2S1N37YY` |
| $997 Premium / Concierge / Priority Setup | `https://square.link/u/RSjzTrCn` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/59zmn4oORY93mWoxst60LnrhuEVZY` |

Pricing files changed:

- `website/pricing.html`
- `pricing.html`

Local preview:

- `http://127.0.0.1:8775/pricing.html`

## Image Status

Website pricing visuals were not changed.

Mapped plan assets for Square image parity:

| Plan | Matching website/pricing asset |
| --- | --- |
| $97 After-Hours Capture | `assets/images/plan-visuals/after-hours-capture-v3.png` |
| $497 24/7 Call Coverage | `assets/images/plan-visuals/247-call-coverage-v3.png` |
| $997 Premium / Concierge / Priority Setup | `assets/images/plan-visuals/custom-call-coverage-v3.png` |

Square payment-link images are not attached. The public Square Checkout API path used for these recurring subscription payment links does not expose a per-link image field. Wallace waived Square payment-link image parity on 2026-05-31 and approved deployment without checkout images.

## Right QA Steps

1. Open `http://127.0.0.1:8775/pricing.html`.
2. Confirm the pricing page design and visuals match the current intended page.
3. Click the $97 `Start Free Trial` button and confirm it stays on Square checkout.
4. Click the $497 `Start Free Trial` button and confirm it stays on Square checkout.
5. Click the $997 `Start Free Trial` button and confirm it stays on Square checkout.
6. Do not enter card details and do not complete checkout.
7. Confirm no pricing button routes to `/client/onboarding.html`, `transactionId`, `orderId`, or any internal success/onboarding page.
8. Confirm homepage `Start Free Trial` buttons still route only to `/pricing.html`.

## Pass Criteria

- All three pricing buttons land on Square checkout and remain there.
- New Square links show the right plan names, $0 trial today, and monthly renewal terms.
- No active pricing href uses the old Square links.
- No active pricing href or pricing script references `/client/onboarding.html`, `transactionId`, or `orderId`.
- No checkout completion or payment is attempted during QA.

## Current Verdict

Checkout links are ready for Wallace preview, Right QA, and deploy. Payment-link image parity is waived for this deploy.
