# Buyer Path Traffic Stage QA - 2026-06-07

## Decision

Recommended stage: **Stage 1 - internal testing only.**

The website buyer path is safer after the Stage 4 fallback improvements, but it is not ready for controlled organic/outbound traffic or paid ads until Square post-checkout redirect/copy is confirmed inside Square or Wallace confirms the Square checkout page/receipt clearly instructs buyers to complete `https://thecalltaker.com/setup.html`.

## What Is Now Safer

| Area | Result |
| --- | --- |
| Homepage/pricing/demo/FAQ plan CTAs | Point to the current Square checkout URLs. |
| Pricing plan copy | Tells buyers to complete the setup form at `thecalltaker.com/setup.html` after checkout. |
| Legacy `/checkout.html` route | Redirects to current Square links and includes stronger after-payment setup fallback copy plus an `I already checked out` setup link. |
| Legacy `/pay.html` route | Redirects to current $97 Square link and includes stronger after-payment setup fallback copy plus an `I already checked out` setup link. |
| Setup page | Explains that paid buyers use the form after checkout so the AI receptionist can be configured. |
| Setup confirmation | Confirms the setup form was received and avoids implying automatic email/SMS/provider activation before approval. |
| FAQ | Adds `What happens after I pay?` and tells buyers to go to `thecalltaker.com/setup.html` if Square does not send them back. |
| Try-live page | Public live auto-call behavior is paused and no provider-call trigger remains in the page. |
| Sitemap | No longer advertises `try-live.html` as an active public demo flow. |

## Try-Live Safety

`website/try-live.html` is still reachable because other public pages may link to it, but it is now safety-gated:

- It is `noindex,nofollow`.
- It says live demo calling is temporarily disabled.
- Submitting the form only shows a local paused message.
- The page contains no Bland endpoint, Authorization header, hardcoded provider credential, lead API `fetch`, live-call button copy, or Google tag.

## Remaining Blockers

| Blocker | Why it matters | Blocks |
| --- | --- | --- |
| Square checkout redirect/copy not confirmed | Public Square bootstrap currently shows `redirectUrl:null`; buyers may not automatically land on setup after payment. | Stage 2 traffic, paid ads, and scaled buyer traffic |
| Square receipt/success wording not confirmed | RIGHT cannot see post-payment receipt language without paying or dashboard access. | Paid ads and scaled buyer traffic |
| Provider-side setup handoff not automated | RIGHT did not trigger calls, SMS, email, invoices, Square settings, or provider workflows. | Automated fulfillment |

## Allowed Traffic

| Traffic source | Recommendation |
| --- | --- |
| Wallace/internal phone checks | Allowed |
| Stage 1 internal fake-customer tests | Allowed after website tests and setup form staged submit pass. |
| Controlled organic social | Wait until Square checkout copy or redirect is cleaner. |
| Outbound no-answer email | Wait until Square checkout copy or redirect is cleaner. |
| Paid ads | Not allowed yet |
| Scaled social posting | Not recommended yet |

## Stage Gate

| Stage | Status | Requirement |
| --- | --- | --- |
| Stage 0 - no traffic | Cleared for website-controlled fallback only. | Try-live remains gated and setup form is live. |
| Stage 1 - internal testing | Recommended current stage. | Run fake-customer checkout-path test without card entry and confirm setup form submit/confirmation. |
| Stage 2 - controlled organic/outbound | Blocked. | Square redirect or buyer-facing checkout/receipt instructions must be clean. |
| Stage 3 - paid ads/scaled traffic | Blocked. | Square redirect/copy, CTOS intake connection, tracking plan, and Meta creative batch must be ready. |

## Next RIGHT Task

Support Wallace/provider confirmation of Square success redirects and Square buyer-facing setup instructions, then rerun the Square handoff test plan.
