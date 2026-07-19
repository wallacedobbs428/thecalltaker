# Website Buyer Path RC V1 — Capability Inventory

Date: 2026-07-19
Evidence basis: `docs/Shipped/CTOS-GIDEON-LIVE.md`, `docs/Shipped/INTEGRATIONS-OPEN.md`, current public-site source, and local regression/visual QA.

## Live and proven

- Gideon demo line answers voice calls at `(629) 269-9697`.
- Approved greeting and caller-intake questions can collect caller identity, callback details, reason for calling, urgency, and requested next step.
- The current Retell/CTOS architecture stores call records and supports transcript/summary evidence.
- The public site can preserve an exact plan through pricing, pre-checkout, and embedded Square card checkout.

## Available with configuration and testing

- After-hours, all-call, and overflow answering modes.
- Business hours, service area, approved questions, hard limits, and urgent-call rules.
- Appointment-request capture without promising that an appointment is booked.
- Approved summary destinations and notification paths.
- Multilingual intake where the selected voice/call flow is configured and tested.

## Limited or scope-dependent

- Live transfer, dispatch, booking, calendar/tool connections, automated follow-up, recording availability, multi-location routing, and owner escalation.
- The `$997+` offer is a base scope; work above the base requires an exact quote and feasibility review.
- Call-pattern review and tuning only when included in the agreed scope and supported by available evidence.

## Planned or not proven for universal public claims

- Guaranteed instant SMS after every call.
- Universal direct calendar booking or dispatch.
- Guaranteed monthly reporting for every plan.
- Exact answer-time, uptime, setup-time, revenue, close-rate, or launch-time guarantees.
- Apple Pay, Google Pay, Cash App Pay, or Afterpay for the recurring card-backed free trial. Square permits those methods for eligible one-time purchases, but the recurring trial requires a storable eligible credit/debit card.

## Buyer-path contract

1. Buyer selects exactly one of `afterhours`, `full247`, or `custom`.
2. Missing or invalid plan returns to pricing; no silent `$497` default exists.
3. Square Web Payments SDK tokenizes the card for storage; raw card details do not pass through The Call Taker servers.
4. The backend creates the customer/card/subscription and must return a receipt plus a signed, single-purpose setup token bound to that purchased plan.
5. Setup refuses direct or unsigned access, locks the plan, and submits to the protected setup-intake endpoint.
6. Production deployment remains blocked until step 4 and the corresponding backend verification in step 5 are implemented and tested together.
