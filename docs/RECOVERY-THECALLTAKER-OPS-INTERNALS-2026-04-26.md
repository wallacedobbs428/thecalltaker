# Recovery — Ops + Internal Pages (2026-04-26)

This document records the decision boundary for the remaining `ops/` and `internal-pages/` drift in `thecalltaker`.

## What `internal-pages/` actually is

`internal-pages/` is not the canonical live internal system.

It appears to be:
- a hidden internal/admin UI tree
- a shopper-report archive
- a parallel war-room surface

It also contains hardcoded legacy CRM browser-side assumptions, including:
- `internal-pages/admin/js/ghl-api.js`
- old `services.leadconnectorhq.com` references
- old `(615) 784-5747` demo references

### Decision

`internal-pages/` is **quarantined** for now.

That means:
- do not treat it as the production admin surface
- do not merge it into the current live funnel blindly
- do not delete it casually
- review it later as an archive / recovery / extraction source

## What the remaining `ops/` drift actually is

The remaining `ops/` changes are mixed.

There are three categories:

### 1. Safe preserve

Changes that are clearly beneficial without lying about the current stack:
- number normalization from old `615` demo line to live `629` line
- `Jessica` to `Gideon` wording updates
- observational/logging improvements
- engine paths that point to the consolidated `thecalltaker-ops` repo

### 2. Hold for re-architecture

Files that were partially translated away from GHL but still assume a working provider sync layer:
- `ops/demo-followup-sms.py`
- `ops/facebook-lead-webhook.py`
- `ops/fb-lead-ads-engine.py`
- `ops/onboarding-engine.py`
- `ops/payment-reminder-engine.py`
- `ops/post-payment-onboarding.py`
- `ops/system-health-monitor.py`
- `ops/hot-lead-converter.py`
- `ops/hot-lead-sequence.py`
- `ops/ghl-reactivation-workflow.py`

These often now point at:
- `TCT_PROVIDER_SYNC_DISABLED`
- `TCT_LEGACY_CRM_LOCATION_ID`
- `https://crm-disabled.invalid`

That is useful as a signpost, but not a finished working architecture.

### 3. Legacy / reject

Anything still pretending the old browser-side / direct CRM path is alive should not be preserved as active current truth.

Examples:
- direct client-side CRM admin helpers
- scripts that still behave as if the old provider is the current backend
- scripts whose only current state is “disabled but still structurally dependent on the dead system”

## Recovery rule from here

For `ops/` and `internal-pages/`:

- preserve only what compounds
- quarantine what is useful but not current
- reject what would mislead future us

## Next extraction targets

1. Preserve safe public-facing copy and collateral updates.
2. Preserve safe number-normalization changes in public industry pages.
3. Leave provider-dependent ops engines unshipped until they are rebuilt against the current stack.
4. Treat `internal-pages/` as an archive source, not as a live admin surface.
