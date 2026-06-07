# Buyer Path Traffic Stage QA - 2026-06-07

## Decision

Recommended stage: **Stage 1 - controlled organic/internal traffic only.**

The website buyer path is safer after the Stage 3 fixes, but it is not ready for paid ads or scaled traffic until Square post-checkout redirect/copy is confirmed inside Square.

## What Is Now Safer

| Area | Result |
| --- | --- |
| Homepage/pricing/demo/FAQ plan CTAs | Point to the current Square checkout URLs. |
| Legacy `/checkout.html` route | Redirects to current Square links and includes setup fallback copy if redirect fails. |
| Legacy `/pay.html` route | Redirects to current $97 Square link and includes setup fallback copy if redirect fails. |
| Setup page | Explains that paid buyers are in the right place if Square did not automatically send them back. |
| Setup confirmation | Avoids implying automatic email/SMS provider actions before approval. |
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
| Square checkout redirect/copy not confirmed | Public Square bootstrap currently shows `redirectUrl:null`; buyers may not automatically land on setup after payment. | Paid ads and scaled buyer traffic |
| Square receipt/success wording not confirmed | RIGHT cannot see post-payment receipt language without paying or dashboard access. | Paid ads and scaled buyer traffic |
| Provider-side setup handoff not automated | RIGHT did not trigger calls, SMS, email, invoices, Square settings, or provider workflows. | Automated fulfillment |

## Allowed Traffic

| Traffic source | Recommendation |
| --- | --- |
| Wallace/internal phone checks | Allowed |
| Controlled organic social | Allowed only if Wallace monitors buyer questions and can manually send `https://thecalltaker.com/setup.html` after purchase if needed. |
| Outbound no-answer email | Allowed only at low volume and with setup-form fallback link available. |
| Paid ads | Not allowed yet |
| Scaled social posting | Not recommended yet |

## Next RIGHT Task

Verify the deployed Stage 3 patch live, then support Wallace/provider confirmation of Square success redirects and Square buyer-facing setup instructions.
