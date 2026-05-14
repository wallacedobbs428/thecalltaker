# Meta/Higgsfield Command Center

Status: local launch-gate tooling. No posting and no paid spend are enabled.

The goal is to turn creative work into a repeatable operating system:

- register each asset
- score it against The Call Taker creative standard
- separate organic readiness from paid readiness
- block fake-live claims and AI-slop hard fails
- produce a daily review output Wallace can act on

## Tooling

Files:

- `tools/creative/creative_assets.sample.json`
- `tools/creative/launch_gate.mjs`
- `tools/creative/output/launch-gate.sample.md`
- `tests/meta-creative-launch-gate.test.mjs`

Run:

```bash
node tools/creative/launch_gate.mjs
node tests/meta-creative-launch-gate.test.mjs
```

## Verdicts

Organic can move faster than paid.

Organic requires:

- no hard fails
- understandable first two seconds
- safe offer and claim
- clear next action
- native-feed fit

Paid requires:

- score `85+`
- zero hard fails
- clear learning purpose
- sound-off comprehension
- CTA and landing path match
- no fake UI, fake numbers, fake proof, or unsupported claims

## Hard Fails

Hold the asset if it has:

- fake phone UI
- readable generated screen text
- fake phone numbers
- unsupported guarantees
- fake live activation
- provider routing claims
- every-call claims
- price or offer mismatch
- brand pronunciation not verified
- no clear close
- looks AI-generated before the offer is clear

## Operating Result

This gives Wallace a real decision surface:

- post organic
- revise for organic
- hold
- paid-ready after Wallace approval

It does not post to Facebook or Instagram, call Meta, call Higgsfield, deploy website changes, or spend budget.
