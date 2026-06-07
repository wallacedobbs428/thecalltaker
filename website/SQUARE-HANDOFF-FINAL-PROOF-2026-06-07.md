# Square Handoff Final Proof - 2026-06-07

## Scope

Read-only audit of the three current Square checkout URLs. No card entered. No Square settings changed. No provider mutation.

## Checkout Link Results

| Plan | URL | HTTP | Redirect URL | Result |
| --- | --- | ---: | --- | --- |
| $97 After-Hours Capture | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/HywRLQ4aYHQ0ojpIbsnBPnrelqAZY` | 200 | `redirectUrl:null` | Opens Square checkout shell |
| $497 24/7 Call Coverage | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/RFxESyTjwZQuIS2xceV8983Pvj8YY` | 200 | `redirectUrl:null` | Opens Square checkout shell |
| $997+ Custom Call Coverage | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/PCGvURHQSoL8LnXbmQ3olB0imFBZY` | 200 | `redirectUrl:null` | Opens Square checkout shell |

## Findings

- Old "AI setup call within 2 minutes" language was absent from the fetched Square shell.
- Static Square fetch exposes checkout title and bootstrap data, but rendered item descriptions are loaded by Square frontend JS. Browser rendering was not available from the sandbox, so rendered item description copy is not fully proven here.
- `redirectUrl` is still `null` on all three Square checkout shells.
- Square dashboard/manual action is still required if Wallace wants buyers automatically redirected to `https://thecalltaker.com/setup.html` after checkout.

## Website-Controlled Fallback

Implemented/verified fallback language:

> After checkout, complete your setup form at thecalltaker.com/setup.html so we can configure your AI receptionist.

The fallback appears on pricing cards, checkout fallback pages, and setup page handoff copy. This is the maximum safe website-controlled fallback while Square redirect remains unconfirmed.

## Stage Impact

- Must-fix for paid ads: yes.
- Must-fix for controlled Stage 1 traffic: no, if MIDDLE accepts the website-controlled fallback.
- Blocked by Wallace/Square dashboard: automatic post-checkout redirect and rendered Square item-description proof.
