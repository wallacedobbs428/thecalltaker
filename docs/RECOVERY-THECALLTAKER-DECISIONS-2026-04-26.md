# The Call Taker Recovery Decisions

Date: 2026-04-26

## Purpose

This document turns repo triage into explicit decisions.

The goal is not to preserve every local edit. The goal is to preserve what
improves the live business and reject what would drag us backward.

## Commit Now

These changes align with the current live direction and should be preserved
first.

### Demo identity / number normalization

- `book.html`
  - updates demo number from `615` to `629`
  - points the booking embed at `demo.html` instead of the dead legacy booking
    widget
- `admin/index.html`
- `admin/clients.html`
- `admin/client-portal.html`
- `admin/onboarding.html`
  - all update stale `615` demo references to the live `629` line

### Browser-side legacy CRM removal

- `onboarding-tracker.html`
  - removes exposed browser-side CRM API config
  - disables browser CRM search/tag creation paths that no longer fit the
    architecture
  - replaces that behavior with explicit internal-app-only messaging

### Cloudflare demo worker

- `cloudflare/gideon-demo-worker.js`
  - new worker for live Gideon TTS demo generation
- `cloudflare/wrangler.toml`
  - renames worker from `jessica-demo` to `gideon-demo`

### Ad creative standardization

- `ads/scripts/script-01-missed-call.md`
- `ads/scripts/script-02-side-by-side.md`
- `ads/scripts/script-03-owners-night.md`
- `ads/scripts/script-04-try-it-now.md`
- `ads/scripts/script-05-what-97-buys.md`
  - replace `Jessica` with `Gideon`
  - update the live demo number from `615` to `629`

### Recovery control docs

- `docs/RECOVERY-THECALLTAKER-TRIAGE-2026-04-26.md`
- `docs/RECOVERY-THECALLTAKER-DECISIONS-2026-04-26.md`

## Hold For Review

These may be useful, but they should not be committed blindly.

### Duplicate internal admin tree

- `internal-pages/admin/*`
- `internal-pages/war-room/index.html`

Reason:
- may be useful as a preserved internal UI set
- duplicates root/admin surfaces
- likely needs consolidation before shipping

### Long-form ad planning docs

- `ads/video-ad-strategy.md`
- `ads/brand/video-brand-guide.md`
- `ads/research/video-tools-comparison.md`
- `ads/thumbnails/thumbnail-specs.md`
- `ads/meta-gideon-draft-package-2026-04-19.md`

Reason:
- likely valuable
- not launch-critical
- should be preserved after core website/admin cleanup

## Do Not Commit In Current Form

These changes conflict with the current live standard or reintroduce broken
behavior.

### Website callback regression

- `website/script.js`

Why:
- replaces live lead submission with `ntfy` notifications only for callback
  widgets
- removes the public lead submission helper instead of routing through the live
  intake path
- that is a regression from the current launch-safe funnel architecture

### Website booking regression

- `website/book.html`

Why:
- reintroduces the old `615` demo number
- restores a direct `api.leadconnectorhq.com` booking iframe
- conflicts with the no-browser-GHL / no-dead-legacy rule

### Website stale-number surfaces

- `website/demo.html`
- `website/pricing.html`

Why:
- still contain multiple `615` references
- not aligned with the live `629` demo standard
- should be corrected before any ship decision

### Legacy CRM prompt updater

- `ops/update-gideon-prompt.py`

Why:
- still built around a disabled legacy CRM path
- user guidance is explicit: we are not depending on getting that access back
- preserve only if it becomes a provider-agnostic prompt tool later

## Archive Mentally, Not Operationally

These areas may contain ideas, but they should not block execution now.

- large `docs/` collateral backlog
- older `sales/` draft backlog
- older prompt history under `ops/jessica-voice-prompt-v*.md`
- broad historical script/content churn under `agents/`, `sales/`, and
  long-tail industry pages

## Current Execution Rule

1. Preserve clean wins first.
2. Do not commit regressions just because they are recent.
3. Prefer surfaces that reduce legacy dependency, normalize the live brand, or
   improve the real operator system.
4. Treat duplicate UI trees and content backlogs as secondary until the live
   website and admin path are clean.
