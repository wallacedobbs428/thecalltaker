# Right Lane Square QA Handoff

Date: 2026-06-07

## Current Buyer-Path Truth

The Call Taker no longer uses a post-payment AI phone-call promise as the setup expectation.

Correct public flow:

1. Customer chooses a plan.
2. Customer checks out securely through Square.
3. Customer completes the setup form.
4. CTOS creates the setup packet.
5. Same-day configuration begins from the completed form.
6. The customer receives forwarding and test-call next steps.
7. The AI receptionist goes live after test confirmation.

Correct Square-facing language:

`After checkout, complete your setup form so we can configure your AI receptionist for same-day setup.`

## Corrected Square Links

These are the corrected buyer-path checkout URLs:

| Plan | Short Square link | Final checkout URL |
| --- | --- | --- |
| $97 After-Hours Capture | `https://square.link/u/ONo7eqGt` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/rQ8UtxYeF82XjX6RTnqJI1cBUDIZY` |
| $497 24/7 Call Coverage | `https://square.link/u/oPAJSalQ` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/Rj2p5FuHxMnVFeVo1d6RYNYH46SZY` |
| $997 Premium / Concierge / Priority Setup | `https://square.link/u/0L3Z4auQ` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/tLZqiyd4tReFcZItQuu0zniW80TZY` |

Provider read-back after the approved correction showed `checkout_redirect_url: null` for the links above.

## Superseded Copy Status

Read-only Square inspection on 2026-06-07 confirmed the old installed Square links carried superseded setup-call wording from the old strategy. Wallace then approved provider mutation, and RIGHT created corrected Square payment links with form-first setup copy.

During the approved correction pass, RIGHT created new Square payment links only. No card was entered, no payment was attempted, no customer message was sent, and no outbound call/webhook was triggered.

## Provider-Side Repair Result

Provider-side repair is complete for checkout copy. New Square provider read-back confirmed:

- form-first setup copy is present
- stale setup-call copy is absent
- checkout redirect URL is `null`
- order total is still `$0` for the trial start

Local request templates used:

- `ctos/integrations/square-97-create-payment-link-request.json`
- `ctos/integrations/square-497-create-payment-link-request.json`
- `ctos/integrations/square-997-create-payment-link-request.json`

Those templates now use the form-first setup language.

## Right QA Steps After Deploy

1. Verify live pricing buttons route to the corrected Square checkout URLs.
2. Confirm all three pricing buttons still land on Square.
3. Do not enter card details.
4. Do not complete checkout.
5. Confirm no route lands on an internal onboarding success page.
6. Confirm public pages still explain checkout, setup form, setup packet, forwarding/testing, and test confirmation.

## Verdict

Website-side copy and Square hosted checkout copy are corrected locally/provider-side. Remaining work is deploy and post-deploy live click verification without completing payment.
