# Ads Launch Status — April 26, 2026

## Canonical Demo Number

- E.164: `+16292699697`
- Display: `(629) 269-9697`
- Rule: all new ad CTAs and hear-it-live CTAs use `629`, not legacy `615`

## Canonical Landing Page

- Primary ad landing page: `https://thecalltaker.com/`

## Core Funnel Paths

- Homepage: `https://thecalltaker.com/`
- Signup: `https://thecalltaker.com/signup.html`
- Pilot: `https://thecalltaker.com/pilot/`
- Calculator: `https://thecalltaker.com/calculator.html`
- Try Live: `https://thecalltaker.com/try-live.html`
- Start: `https://thecalltaker.com/start.html`
- Pay: `https://thecalltaker.com/pay.html`

## Operating Rules

- No GHL dependency in the public ad funnel
- Public leads post into the live app intake
- `thecalltaker.vercel.app/api/health` must stay `ok`
- If a CTA sends someone to buy now, the flow must be explicit, not inferred

## Ad Handoff Rules

- `CALL_NOW` creative points at the canonical demo number
- plan-specific CTAs can use:
  - `start.html?plan=after-hours`
  - `start.html?plan=starter`
  - `start.html?plan=pro`

## Morning Commands

```bash
zsh /Users/moneymaker99/thecalltaker/ops/public-launch-audit.sh
zsh /Users/moneymaker99/thecalltaker/ops/ads-preflight.sh
```
