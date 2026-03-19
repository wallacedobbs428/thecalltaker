---
name: loop-intelligence
description: "Skill health monitor that audits all skill descriptions for routing quality. Use when checking skill health, auditing descriptions, or running periodic skill maintenance. Can be invoked via /loop for recurring checks."
user-invokable: true
---

# Loop Intelligence — Skill Health Monitor

Audit all skills in `.claude/skills/` for routing quality and report issues.

## What It Does

1. **Count** all SKILL.md files
2. **Score** each description (0-10) based on:
   - Has trigger keywords ("use when", "use this", "triggers on") → +2
   - Has action verbs (create, build, write, generate, etc.) → +1
   - Length > 60 chars → +2 (30-60 → +1, <30 → -2)
   - Not empty/placeholder → required
3. **Report** skills scoring below 8
4. **Flag** empty, broken, or duplicate descriptions

## How to Run

### One-time audit
```
/loop-intelligence
```

### Recurring monitor (via /loop)
```
/loop 30m /loop-intelligence
```

## Scoring Rubric

| Score | Meaning |
|-------|---------|
| 10 | Perfect — clear triggers, unique scope, actionable |
| 8-9 | Good — has triggers and clear purpose |
| 6-7 | Needs work — missing triggers or too vague |
| 4-5 | Poor — too short, no routing value |
| 0-3 | Broken — empty, placeholder, or 404 |

## Audit Script

Run this to score all skills:

```bash
for d in .claude/skills/*/; do
  skill=$(basename "$d")
  f="$d/SKILL.md"
  [ -f "$f" ] || continue
  desc=$(awk '/^---$/{c++; next} c==1 && /^description:/{sub(/^description: */, ""); gsub(/"/, ""); print; exit}' "$f")
  len=${#desc}
  score=10
  # Empty check
  [ "$len" -lt 5 ] && score=0 && echo "0|$skill|EMPTY" && continue
  # Length scoring
  [ "$len" -lt 30 ] && score=$((score-4))
  [ "$len" -ge 30 ] && [ "$len" -lt 60 ] && score=$((score-2))
  # Trigger keywords
  echo "$desc" | grep -qi "use when\|use this\|triggers on\|also use when" || score=$((score-2))
  # Action verbs
  echo "$desc" | grep -qi "create\|build\|write\|generate\|analyze\|design\|implement\|configure\|manage\|deploy\|optimize\|review\|test\|debug\|automate" || score=$((score-1))
  [ "$score" -lt 0 ] && score=0
  [ "$score" -lt 8 ] && echo "$score|$skill|NEEDS_FIX|${desc:0:60}"
done
```

## Expected Output

When healthy:
```
TOTAL: 267 skills
SCORING 8+: 267 (100%)
SCORING <8: 0
STATUS: ALL CLEAR ✓
```

When issues found:
```
TOTAL: 267 skills
SCORING 8+: 260 (97%)
SCORING <8: 7
--- ISSUES ---
3|broken-skill|EMPTY
5|vague-skill|TOO_SHORT|Some vague description...
7|ok-skill|NO_TRIGGERS|Decent but missing use when...
```

## Fix Protocol

For any skill scoring <8:
1. Read the full SKILL.md to understand what the skill does
2. Rewrite the `description:` field in YAML frontmatter
3. Add "Use when [specific trigger conditions]" clause
4. Re-run audit to confirm score >= 8
