# Square Checkout Form-First Setup QA - 2026-06-07

RIGHT lane scope: buyer-path truth correction and no-provider-mutation QA.

## Result

Status: **corrected Square form-first setup links created and verified.**

The correct buyer expectation is now:

1. Checkout securely.
2. Complete the setup form.
3. CTOS creates the setup packet.
4. Same-day configuration begins from the completed form.
5. Forwarding and test-call steps are sent before launch.

## Current Links

| Plan | Short Square link | Final checkout URL |
|---|---|---|
| After-Hours Capture | `https://square.link/u/ONo7eqGt` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/rQ8UtxYeF82XjX6RTnqJI1cBUDIZY` |
| 24/7 Call Coverage | `https://square.link/u/oPAJSalQ` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/Rj2p5FuHxMnVFeVo1d6RYNYH46SZY` |
| Premium Concierge Priority Setup | `https://square.link/u/0L3Z4auQ` | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/tLZqiyd4tReFcZItQuu0zniW80TZY` |

## Required Square-Facing Copy

`After checkout, complete your setup form so we can configure your AI receptionist for same-day setup.`

## Safety Notes

- No card was entered.
- No payment was attempted.
- No customer message was sent.
- No outbound call was sent.
- No secrets were printed.
- Square provider mutation was performed only after Wallace approval: three corrected payment links were created.

## Provider Verification

Read-only provider verification after creation confirmed:

- form-first setup copy is present
- stale setup-call copy is absent
- `checkout_redirect_url` is `null`
- no payment or charge was attempted

## Remaining Blocker

Deploy the website and verify live pricing/FAQ/demo/start links route to the corrected Square checkout URLs without completing payment.
