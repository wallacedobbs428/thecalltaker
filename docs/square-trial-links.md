# Square Trial Links

Square is the approved public checkout provider for The Call Taker trial funnel.

Do not add Stripe checkout links to the public website. Do not reuse the `$97`
Square link for higher tiers.

## Current Public Link State

| Plan | Monthly Price After Trial | Square Link State |
| --- | ---: | --- |
| After-Hours Capture | `$97/mo` | Configured: `https://square.link/u/2hfmRPY7` |
| Revenue Recovery System | `$497/mo` | Configured: `https://square.link/u/S305ewBr` |
| Operational Infrastructure | `$997+/mo` | Configured: `https://square.link/u/OpwWF9Sa` |

Each Square-hosted checkout title must state the renewal terms visibly:

- `After-Hours Capture: 14 days free, then $97/mo`
- `Revenue Recovery System: 14 days free, then $497/mo`
- `Operational Infrastructure: 14 days free, then $997/mo`

## Website Behavior

- Generic `Start Free Trial` buttons route to `/checkout.html`.
- Pricing-card buttons include the selected plan in the URL:
  - `/checkout.html?plan=afterhours`
  - `/checkout.html?plan=full247`
  - `/checkout.html?plan=premium`
- Each plan continues to its matching Square recurring trial checkout.
- If a future plan lacks a verified Square trial link, leave its
  `SQUARE_TRIAL_LINKS` value blank so checkout falls back to calling Wallace
  instead of sending buyers to the wrong payment link.

## Adding Missing Square Links Later

1. Create the Square recurring invoice or payment link for the exact tier.
2. Confirm the buyer sees no charge today, a 14-day trial, and the correct
   monthly amount after trial.
3. Add only the verified Square URL to `SQUARE_TRIAL_LINKS` in
   `website/checkout.html`.
4. Update `tests/website-trial-funnel.test.js` so it requires the new Square
   URL for that tier.
5. Run:

```bash
node tests/website-trial-funnel.test.js
npm --prefix ads/mcp-video run verify --if-present
git diff --check
```

6. Push, wait for GitHub Pages and Website Trial Funnel Regression, then
   live-verify the matching `/checkout.html?plan=...` path.

## Safety Rules

- Do not create public checkout links for the `$2,500` implementation setup.
- Do not imply provider routing, SMS/email notifications, backend sync, CTOS,
  CRM, or booking automation is active from checkout alone.
- Do not send buyers to a Square link for the wrong monthly tier.
- Do not add Stripe links to public trial pages.
