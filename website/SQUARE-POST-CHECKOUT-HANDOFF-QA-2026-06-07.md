# Square Post-Checkout Handoff QA - 2026-06-07

## Scope

RIGHT reviewed the public buyer handoff from The Call Taker pricing pages into Square checkout and back into the setup form. This audit used only public/read-only page checks. No payment, card entry, invoice, Square dashboard mutation, SMS, email, call, or provider action was performed.

## Current Square Links Tested

| Plan | Public Square URL | Read-only result | Notes |
| --- | --- | --- | --- |
| $97 After-Hours Capture | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/HywRLQ4aYHQ0ojpIbsnBPnrelqAZY` | HTTP 200 | Public Square bootstrap shows order open and store accepting payments. |
| $497 Revenue Recovery System | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/RFxESyTjwZQuIS2xceV8983Pvj8YY` | HTTP 200 | Public Square bootstrap shows order open and store accepting payments. |
| $997+ Operational Infrastructure | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/PCGvURHQSoL8LnXbmQ3olB0imFBZY` | HTTP 200 | Public Square bootstrap shows order open and store accepting payments. |

## Website Link Mapping

| Website surface | Current behavior | Result |
| --- | --- | --- |
| `website/index.html` pricing buttons | Directs to the three current Square URLs above. | Pass |
| `website/pricing.html` plan buttons and sticky CTA | Directs to the current Square URLs above. | Pass |
| `website/demo.html` post-demo plan buttons | Directs to the current Square URLs above. | Pass |
| `website/faq.html` CTA | Directs to the current $497 Square URL. | Pass |
| `website/checkout.html` legacy redirect map | Redirects plan aliases to the current Square URLs and includes setup-form fallback copy. | Pass |
| `website/pay.html` direct $97 helper | Redirects to the current $97 Square URL and includes setup-form fallback copy. | Pass |
| `website/setup.html` | Clearly tells paid buyers they are in the right place if Square did not send them back automatically. | Pass |

## Post-Checkout Handoff Risk

The public Square page bootstrap data currently shows `redirectUrl:null`. RIGHT did not mutate Square settings, so the automatic post-payment return path cannot be confirmed from the website repo alone.

Must-fix before scaled traffic: Wallace or the Square owner should confirm each Square checkout link has either:

1. A success/redirect URL to `https://thecalltaker.com/setup.html`, ideally with a plan query such as `?source=square&plan=afterhours`, `?source=square&plan=full247`, or `?source=square&plan=premium`.
2. Buyer-facing Square checkout or receipt copy that says: `After checkout, complete your setup form at https://thecalltaker.com/setup.html. If Square does not automatically send you back, return to that link after checkout.`

## Old Setup-Call Language

No public website buyer-path page should promise that AI will call within 2 minutes after payment. The website now uses form-first setup copy instead.

The Square checkout pages are controlled inside Square. RIGHT did not find the old 2-minute AI-call wording in the static public HTML returned by Square, but the rendered Square checkout app and receipt/success content still need Wallace/provider dashboard confirmation.

## Traffic Recommendation

Stage 1 controlled traffic only until Square redirect/copy is confirmed. The public website path is safer now, but a paying buyer can still be confused after Square if Square itself does not return them to the setup form or show setup instructions.

Paid ads remain blocked until the Square post-checkout handoff is confirmed end to end.
