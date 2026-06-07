# Square Redirect Manual Action Packet - 2026-06-07

## Purpose

Make sure a paid buyer does not get lost after Square checkout. The desired post-payment destination is:

`https://thecalltaker.com/setup.html`

RIGHT performed read-only public checks only. No card information was entered, no payment was attempted, no invoice was created, no Square settings were changed, and no provider action was triggered.

## Current Checkout Link Status

| Plan | Checkout URL | HTTP status | Public static title | `redirectUrl` | Setup URL visible in static Square HTML | Old AI-call wording visible in static Square HTML |
| --- | --- | --- | --- | --- | --- | --- |
| $97 After-Hours Capture | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/HywRLQ4aYHQ0ojpIbsnBPnrelqAZY` | 200 | The Call Taker | `null` | No | No |
| $497 Revenue Recovery System | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/RFxESyTjwZQuIS2xceV8983Pvj8YY` | 200 | The Call Taker | `null` | No | No |
| $997+ Operational Infrastructure | `https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/PCGvURHQSoL8LnXbmQ3olB0imFBZY` | 200 | The Call Taker | `null` | No | No |

## What RIGHT Could Prove

- All three Square checkout links return HTTP 200.
- All three public Square bootstrap payloads show `orderIsOpen:true`.
- All three public Square bootstrap payloads show `storeIsAcceptingPayments:true`.
- All three public Square bootstrap payloads show `redirectUrl:null`.
- Static Square HTML does not show the old AI-call-within-2-minutes language.
- Static Square HTML does not show `https://thecalltaker.com/setup.html`.
- Static Square HTML does not expose enough rendered order detail for RIGHT to verify each buyer-visible item title/description without dashboard access or a full browser-rendered checkout proof.

## Required Square Dashboard Change

Wallace or the Square owner should check each checkout link inside Square and set one or both of these:

1. Success/redirect URL:
   `https://thecalltaker.com/setup.html`

2. Buyer-facing checkout or receipt description:
   `After checkout, complete your setup form at thecalltaker.com/setup.html so we can configure your AI receptionist for same-day setup.`

If Square supports plan-specific redirects, use:

- `$97`: `https://thecalltaker.com/setup.html?source=square&plan=afterhours`
- `$497`: `https://thecalltaker.com/setup.html?source=square&plan=full247`
- `$997+`: `https://thecalltaker.com/setup.html?source=square&plan=premium`

## Are New Square Links Required?

Not proven. The current links are live and accepting payments. New links are only required if Square cannot add success redirect/copy to the existing links.

Do not create new Square links unless Wallace explicitly approves.

## Proof RIGHT Needs After Wallace Changes Square

For each of the three links, RIGHT needs a new read-only proof showing:

- The checkout page still loads.
- The buyer-visible item title is correct.
- The old AI-call-within-2-minutes wording is absent.
- The buyer-visible setup instruction is present, or the Square dashboard shows the success redirect set to `https://thecalltaker.com/setup.html`.
- Public/static bootstrap no longer shows `redirectUrl:null`, if Square exposes that value publicly.

No live payment is required for the first proof pass.

## Traffic Gate

| Traffic type | Status |
| --- | --- |
| Stage 1 internal testing | Allowed after website fallback checks pass. |
| Stage 2 controlled organic/outbound | Wait until Square checkout copy or redirect is cleaner. |
| Paid ads | Blocked. |

## Provider Actions Taken By RIGHT

None. RIGHT did not mutate Square, send emails, send SMS, trigger calls, create invoices, create payment links, or call provider webhooks.
