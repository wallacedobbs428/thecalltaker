# Pricing / Setup Clarity QA - 2026-06-07

## Objective

Confirm the buyer understands the correct order:

1. choose plan
2. checkout
3. complete setup form
4. setup packet reviewed
5. forwarding/testing next steps
6. live after confirmation

## Result

PASS

## Current Pricing

- $97 After-Hours Capture
- $497 24/7 Call Coverage
- $997+ Custom Call Coverage

## Buyer-Path Checks

| Page | Result |
| --- | --- |
| Homepage pricing section | Square checkout links and setup-form-after-checkout links present |
| Pricing cards | Each plan has Square CTA and setup fallback copy |
| Pricing flow cards | Checkout -> Setup Form -> Setup Packet |
| FAQ | "What happens after I pay?" explains Square fallback and setup review |
| Checkout fallback | Sends buyers to Square and tells them to complete setup form after checkout |
| Pay fallback | Same safe $97 fallback path |
| Setup | "Already checked out?" card clarifies what to do if Square does not redirect |
| Confirmation | Says packet is in review and routing starts only after test confirmation |

## Remaining Blocker

Square `redirectUrl` remains `null`. Automatic post-checkout setup redirect requires Square dashboard/manual action.
