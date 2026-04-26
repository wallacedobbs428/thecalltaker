# The Call Taker Ship Queue

Date: 2026-04-26

## Goal

Reduce repo drift by preserving the highest-value changes in the right order.

## Batch 1: Safe Preservation

- commit recovery docs
- commit Cloudflare Gideon demo worker
- commit `wrangler.toml` rename to Gideon
- commit root `book.html` demo-number normalization
- commit admin-page `615` to `629` fixes
- commit ad script `Jessica` to `Gideon` and `615` to `629` changes

## Batch 2: Browser Legacy Removal

- commit `onboarding-tracker.html` CRM-key removal / browser-action disablement
- verify no browser-exposed CRM keys remain in high-value internal pages

## Batch 3: Duplicate Internal UI Review

- compare `admin/*` against `internal-pages/admin/*`
- decide canonical tree
- archive or ignore the losing duplicate path

## Batch 4: Website Regression Repair

- fix `website/book.html` so it matches current launch-safe booking behavior
- fix `website/demo.html` to use the live `629` line
- fix `website/pricing.html` to use the live `629` line
- repair `website/script.js` so callback widgets hit the live intake path, not
  `ntfy` only

## Batch 5: Ops Script Reality Check

- review `ops/update-gideon-prompt.py`
- either replace with provider-agnostic prompt tooling or stop treating it as a
  live path

## Batch 6: Ad System Preservation

- preserve the ad strategy docs that still support the current Meta/Creatify
  plan
- leave stale planning collateral out of the critical path

## Batch 7: Internal Surface Consolidation

- reconcile `admin/`, `client/`, `onboarding/`, and `internal-pages/`
- remove false optionality where the same function exists in multiple trees

## Batch 8: Historical Backlog Sweep

- identify dead `docs/` and `sales/` collateral that should stop counting as
  active work
- move it mentally to archive status

## Batch 9: Repo Rule Tightening

- expand ignore rules only where the files are clearly generated or disposable
- keep real product/UI work visible

## Batch 10: Re-audit And Closeout

- rerun `repo-ship-audit --repo thecalltaker`
- save a closeout snapshot
- make the remaining drift a deliberate queue, not hidden sprawl
