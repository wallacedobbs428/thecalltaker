# Ads Launch Checklist — April 26, 2026

Use this before turning ads on.

## 1. App Health

Run:

```bash
curl -L -sS https://thecalltaker.vercel.app/api/health
```

Pass:
- `status` is `ok`
- no cron shows `stale: true`

## 2. Public Launch Audit

Run:

```bash
zsh /Users/moneymaker99/thecalltaker/ops/public-launch-audit.sh
```

Pass:
- every check returns `PASS`
- no launch page contains:
  - `leadconnectorhq`
  - `rest.gohighlevel`
  - `pit-`
  - old demo number `615`

## 3. Live Funnel Pages

Check:
- `https://thecalltaker.com/`
- `https://thecalltaker.com/signup.html`
- `https://thecalltaker.com/pilot/`
- `https://thecalltaker.com/calculator.html`
- `https://thecalltaker.com/try-live.html`
- `https://thecalltaker.com/start.html`
- `https://thecalltaker.com/pay.html`

Pass:
- page loads
- CTA copy points to the live demo number `+1 (629) 269-9697`
- no stale March urgency copy on the path you are buying traffic into

## 4. Lead Intake Smoke

Run one real production smoke post:

```bash
zsh /Users/moneymaker99/thecalltaker-ops/ops/smoke-test-public-lead.sh
```

Pass:
- returns `ok: true`
- lead id is created

## 5. Demo Line

Check:
- call `+1 (629) 269-9697`
- answer speed is acceptable
- opener sounds right
- no dead air
- no wrong business name

## 6. Payment Path

Decide one source of truth for today:
- `pay.html`
- booked demo only

Pass:
- ads do not send buyers into a broken or mock checkout path

## 7. Callback Workflow

Verify:
- someone is watching the queue
- missed-call recovery is on
- callback owner is clear
- first 10 leads today will be acknowledged fast

## 8. Freeze

After checks pass:
- do not change landing page copy unless it is a break/fix
- do not change intake routing
- do not change demo number
- only react to real failures
