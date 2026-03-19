---
name: task-planning
description: "Plan and break down complex tasks into actionable steps. Use when organizing projects, creating sprint plans, estimating work, prioritizing backlogs, or structuring multi-step implementations. Covers task decomposition, dependency mapping, risk identification, and progress tracking."
category: project-management
---

# Task Planning

Break complex work into clear, ordered, actionable steps.

---

## Task Decomposition Framework

### Step 1: Define the Outcome
Before breaking down tasks, write a single sentence:
> "When this is done, [specific measurable outcome]."

Example: "When this is done, cold leads receive a 5-step automated follow-up sequence over 7 days."

### Step 2: Identify Components
List every piece needed:
```
- [ ] Data: What inputs/state files needed?
- [ ] Logic: What decisions/scoring/routing?
- [ ] Integrations: What APIs/services?
- [ ] Output: What gets sent/saved/displayed?
- [ ] Config: What settings/limits?
- [ ] Monitoring: How do we know it's working?
```

### Step 3: Order by Dependencies
```
[Independent tasks — can be done in parallel]
  ├── Task A (no dependencies)
  ├── Task B (no dependencies)
  └── Task C (no dependencies)

[Dependent tasks — must follow order]
  ├── Task D (depends on A)
  ├── Task E (depends on A + B)
  └── Task F (depends on D + E)

[Final tasks — after everything else]
  ├── Testing
  ├── Documentation
  └── Deployment
```

---

## Task Template

```markdown
## Task: [Name]

**Goal:** [One sentence outcome]
**Priority:** P0/P1/P2/P3
**Estimated effort:** Small (< 2hr) | Medium (2-8hr) | Large (1-3 days)

### Subtasks
- [ ] [Specific actionable step]
- [ ] [Specific actionable step]
- [ ] [Specific actionable step]

### Dependencies
- Requires: [What must be done first]
- Blocks: [What can't start until this is done]

### Acceptance Criteria
- [ ] [Testable condition that proves it works]
- [ ] [Another testable condition]

### Risks
- [What could go wrong and how to mitigate]
```

---

## Prioritization Matrix

### Eisenhower Matrix for Features
```
                    URGENT              NOT URGENT
              ┌─────────────────┬─────────────────┐
  IMPORTANT   │   DO FIRST      │   SCHEDULE       │
              │ Revenue-blocking│ Strategic growth  │
              │ Customer-facing │ Technical debt    │
              │ bugs            │ New features      │
              ├─────────────────┼─────────────────┤
  NOT         │   DELEGATE      │   ELIMINATE       │
  IMPORTANT   │ Nice-to-haves   │ Vanity metrics   │
              │ Style tweaks    │ Over-engineering  │
              │ Internal tools  │ Unused features   │
              └─────────────────┴─────────────────┘
```

### ICE Scoring
For each feature, score 1-10:
- **I**mpact: How much will this move the needle?
- **C**onfidence: How sure are we it'll work?
- **E**ase: How easy is it to implement?

Score = (I + C + E) / 3. Work on highest scores first.

---

## Sprint Planning Template

```markdown
## Sprint: [Date Range]

### Sprint Goal
[One sentence: what's the most important outcome this sprint?]

### Committed Work
| Task | Owner | Priority | Estimate | Status |
|------|-------|----------|----------|--------|
| [Task 1] | [Name] | P0 | Small | To Do |
| [Task 2] | [Name] | P1 | Medium | To Do |
| [Task 3] | [Name] | P1 | Small | To Do |

### Stretch Goals (if time permits)
- [ ] [Nice-to-have 1]
- [ ] [Nice-to-have 2]

### Blockers
- [Known blocker and plan to resolve]

### Done Definition
- Code committed and pushed
- Tests pass
- Deployed (or deployment instructions written)
- Documentation updated
```

---

## Risk Assessment

For each major task, evaluate:

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| API rate limiting | High | Medium | Implement backoff, batch requests |
| State file corruption | Low | High | Atomic writes, backup on each write |
| External service outage | Medium | High | Graceful degradation, retry logic |
| Scope creep | High | Medium | Strict acceptance criteria, say no |

---

## Progress Tracking

### Daily Standup Format
```
**Yesterday:** [What was completed]
**Today:** [What's planned]
**Blockers:** [What's stuck]
```

### Task States
```
Backlog → To Do → In Progress → In Review → Done
                       ↓
                   Blocked → [Resolve blocker] → In Progress
```
