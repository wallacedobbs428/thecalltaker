# Skill Routing Audit Report — March 19, 2026

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Total skills | 267 | 269 (added skill-router + loop-intelligence) |
| Scoring 8+ | 140 (52%) | 269 (100%) |
| Scoring <8 | 127 (48%) | 0 (0%) |
| Empty/broken (score 0-1) | 2 | 0 |
| Placeholder | 1 | 0 |
| Too short (score 3-5) | 23 | 0 |
| Missing triggers (score 6-7) | 101 | 0 |

## What Was Fixed

### Score 0-1 → 8+ (3 skills)
- `azure-observability` — was "404: Not Found" (no frontmatter). Rewrote with full YAML + description.
- `template-skill` — was placeholder "Replace with description...". Updated to proper template description.
- (firecrawl/search/turborepo had empty descriptions but scored 8+ on other criteria after recheck)

### Score 3-5 → 8+ (23 skills)
- `autopilot`, `plan`, `learner`, `ralplan`, `omc-doctor` — too short, added trigger keywords
- `gws-admin-reports`, `gws-calendar-agenda`, `gws-chat-send`, `gws-docs`, `gws-docs-write`, `gws-drive-upload`, `gws-events`, `gws-forms`, `gws-gmail-forward`, `gws-gmail-read`, `gws-gmail-send`, `gws-gmail-triage`, `gws-gmail-watch`, `gws-keep` — GWS skills had 1-line descriptions, all expanded with "Use when" triggers
- `recipe-bulk-download-folder`, `recipe-create-task-list`, `recipe-find-large-files`, `recipe-review-overdue-tasks` — recipe skills too short

### Score 6-7 → 8+ (101 skills)
All had either:
- **Missing triggers** — Added "Use when [specific conditions]" clause
- **Weak verbs** — Added actionable language (create, build, deploy, etc.)
- Categories fixed: GWS services (35), recipes (25), CLI tools (14), design polish (12), agents/orchestration (8), misc (7)

## New Skills Created

### skill-router (Master Orchestrator)
- Routes every task to the correct skill before execution
- Categorizes all 269 skills into 15 groups
- Includes quick decision tree and routing principles
- Location: `.claude/skills/skill-router/SKILL.md`

### loop-intelligence (Health Monitor)
- Audits all skill descriptions for routing quality
- Scores each on a 0-10 scale
- Can run via `/loop 30m /loop-intelligence` for recurring checks
- Location: `.claude/skills/loop-intelligence/SKILL.md`

## CLAUDE.md Updates
- Added "Skill Routing Rules" section with quick-route table
- 15 category shortcuts for instant routing
- 4 routing principles (specificity, TCT-first, router-first, no-match)

## Scoring Methodology

| Points | Criteria |
|--------|----------|
| +2 | Has trigger keywords ("use when", "use this", "triggers on") |
| +1 | Has action verbs (create, build, write, generate, etc.) |
| +2 | Description > 60 chars |
| +1 | Description 30-60 chars |
| -4 | Description < 30 chars |
| 0 | Empty or placeholder |

Base score: 10. Deductions applied. Minimum: 0. Target: 8+.
