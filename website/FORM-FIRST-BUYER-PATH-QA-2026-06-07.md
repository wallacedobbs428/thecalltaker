# Form-First Buyer Path QA - 2026-06-07

RIGHT lane scope: buyer-path truth, conversion clarity, provider safety, and public copy regression testing.

## Summary Of What Was Wrong

The previous checkout strategy promised a post-payment AI setup phone call. That is no longer the scalable buyer-path truth and could make a buyer feel surprised or misled after payment.

The corrected truth is:

1. Customer chooses a plan.
2. Customer checks out securely.
3. Customer completes the setup form.
4. CTOS creates the setup packet.
5. Same-day configuration begins from the completed form.
6. Forwarding and test-call steps happen before launch.

## Public Phrases Removed

Removed or replaced customer-facing copy that implied:

- a guaranteed post-payment AI setup phone call
- a fixed two-minute setup promise
- vague setup review before launch without explaining the setup form
- instant activation language on public setup paths

## Replacement Language Used

Core replacement language:

`After checkout, complete your setup form so we can configure your AI receptionist.`

Supporting language added:

- `Same-day setup is available once your setup form is submitted.`
- `We use your setup form to build your call flow, summary rules, transfer rules, and forwarding/testing steps.`
- `If anything is missing, we follow up before configuration.`
- `You do not need to know your phone system perfectly.`

## Files Updated In This QA Pass

- `website/index.html`
- `website/pricing.html`
- `website/demo.html`
- `website/faq.html`
- `website/checkout.html`
- `website/pay.html`
- `website/signup.html`
- public-folder legacy/static copies under `website/demo/`, `website/pages/locations/`, `website/blog/`, and `website/shared/`
- `tests/website-trial-funnel.test.js`
- `ctos/integrations/square-97-create-payment-link-request.json`
- `ctos/integrations/square-497-create-payment-link-request.json`
- `ctos/integrations/square-997-create-payment-link-request.json`
- `ctos/product/checkout-status.json`
- `ctos/product/square-links.json`
- `docs/RIGHT-LANE-SQUARE-QA-HANDOFF.md`
- `website/SQUARE-CHECKOUT-SETUP-CALL-QA-2026-06-06.md`
- `website/PAYMENT-LINK-MAPPING-AUDIT-2026-06-05.md`

## Square Checkout Wording Status

The website-side copy and local Square request templates now use form-first setup language.

Read-only Square inspection on 2026-06-07 confirmed the old Square checkout URLs still had the superseded provider-side setup-call wording from the earlier link creation. Wallace approved provider mutation, and RIGHT created three corrected Square links with form-first setup copy.

Provider read-back confirmed the corrected Square links have form-first copy and no stale setup-call wording.

## Provider Safety

- No card entered.
- No payment attempted.
- No customer message sent.
- No outbound call sent.
- No webhook triggered.
- Square provider mutation performed after Wallace approval: three corrected payment links were created.
- Deployment still required after local validation.
- No secrets printed.

## Remaining Buyer-Path Blockers

1. Deploy the corrected website.
2. Verify live pricing buttons on desktop and mobile without completing payment.
3. Confirm live homepage/pricing/FAQ/demo pages no longer show old setup language.

## Verdict

Local website-side buyer-path copy and Square hosted checkout copy are aligned with form-first setup. Remaining work is deploy and post-deploy live verification.
