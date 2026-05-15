# Social Agent Contract

Status: local handoff contract. No posting is enabled by this document.

The Call Taker social agent should consume generated JSON from `tools/creative/output/`, not scrape docs or infer readiness from captions.

## Inputs

Candidate handoff:

```text
tools/creative/output/social-agent-handoff.sample.json
```

Approval-applied handoff:

```text
tools/creative/output/social-agent-approved.sample.json
```

7-day calendar:

```text
tools/social/output/social-calendar.sample.json
```

## Trust Rules

The posting agent may only consider a candidate when:

- `post_allowed` is `true`
- `approval_status` is `approved_for_manual_post`
- `blocked_policy.auto_publish_allowed` is `false`
- the asset file exists and passes visual QA outside this JSON

Even then, this repo does not post. A separate posting agent must perform the final action after Wallace/operator approval.

## Fields

- `platform`: `facebook` or `instagram`
- `asset_id`: creative registry ID
- `format`: expected post format
- `caption`: post caption candidate
- `story_frames`: optional story/reel frame text
- `cta`: desired next action
- `landing_path`: CTA destination
- `hashtags`: candidate hashtags
- `post_allowed`: approval gate output
- `approval_status`: approval state
- `required_manual_checks`: checks before actual posting

## Do Not Do

- Do not post candidates with `post_allowed: false`.
- Do not launch paid spend from this handoff.
- Do not call Meta, Instagram, Facebook, Higgsfield, or provider APIs from these tools.
- Do not publish assets that fail visual QA, pronunciation QA, claim safety, or landing-page match.
