# The Call Taker Triage

Date: 2026-04-26

## Purpose

This document separates the `thecalltaker` repo into what should be preserved,
what should be reviewed next, and what should stop receiving attention by
default.

The repo currently mixes:

- live website funnel work
- internal admin/client/onboarding tools
- ad strategy and creative planning
- old ops scripts
- historical docs and collateral

The goal is to turn that into a shipping queue.

## Ship First

These are the highest-value uncommitted surfaces in this repo.

### Website / funnel

- `website/book.html`
- `website/script.js`
- `book.html`
- `website/demo.html`
- `website/pricing.html`

### Internal admin / onboarding

- `internal-pages/admin/index.html`
- `internal-pages/admin/js/ghl-api.js`
- `admin/index.html`
- `admin/clients.html`
- `admin/client-portal.html`
- `admin/onboarding.html`
- `onboarding-tracker.html`

### Cloudflare / demo line

- `cloudflare/gideon-demo-worker.js`
- `cloudflare/wrangler.toml`
- `ops/update-gideon-prompt.py`

### Ads / creative system

- `ads/meta-gideon-draft-package-2026-04-19.md`
- `ads/video-ad-strategy.md`
- `ads/scripts/script-01-missed-call.md`
- `ads/scripts/script-02-side-by-side.md`
- `ads/scripts/script-03-owners-night.md`
- `ads/scripts/script-04-try-it-now.md`
- `ads/scripts/script-05-what-97-buys.md`
- `ads/thumbnails/thumbnail-specs.md`

## Preserve But Review

These look useful, but should be reviewed before shipping because they may be
stale, legacy-bound, or partially superseded.

### Client / onboarding surfaces

- `client/index.html`
- `client/dashboard.html`
- `client/onboarding.html`
- `onboarding/checklist.html`
- `onboarding/live.html`
- `onboarding/next-steps.html`
- `onboarding/customer-success-playbook.md`
- `onboarding/new-client-intake-form.md`

### Ops scripts

- `ops/facebook-lead-webhook.py`
- `ops/fb-lead-ads-engine.py`
- `ops/onboarding-engine.py`
- `ops/post-payment-onboarding.py`
- `ops/payment-reminder-engine.py`
- `ops/engine-health-check.py`
- `ops/system-health-monitor.py`

### Admin / report templates

- `internal-pages/shopper-reports/_template.html`
- `internal-pages/shopper-reports/_sample.html`

## Archive / Do Not Focus First

These may contain useful ideas, but they should not block shipping. They are
lower-priority than the surfaces above.

- old collateral under `docs/`
- older sales drafts under `sales/`
- long-tail industry/location page churn
- historical GHL-era process docs
- stale prompt-history files like `ops/jessica-voice-prompt-v*.md`

## Noise / Ignore

These are not the right places to spend active recovery effort.

- `.DS_Store`
- generated shopper report instances
- backup files like `website/index.html.bak-*`
- local health snapshots like `ops/health-check-report.json`

## Decision Rule

When touching this repo:

1. Prefer the live website funnel, admin/onboarding, Cloudflare demo, and ad
   system first.
2. Do not spend time polishing historical docs unless they directly support
   live operations or sales.
3. If a file depends on dead legacy CRM behavior, preserve it only if it can be
   adapted quickly; otherwise archive it mentally and move on.
