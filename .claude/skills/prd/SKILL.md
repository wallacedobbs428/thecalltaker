---
name: prd
description: "Write Product Requirements Documents (PRDs) for new features, products, or system changes. Use when planning what to build, defining scope, writing user stories, setting success metrics, or documenting technical requirements. Covers problem statements, user personas, feature specs, acceptance criteria, and launch plans."
category: product
---

# PRD — Product Requirements Document

Write clear, actionable PRDs that engineering can build from without ambiguity.

---

## PRD Template

```markdown
# PRD: [Feature Name]

**Author:** [Name]
**Date:** [YYYY-MM-DD]
**Status:** Draft | In Review | Approved | In Progress | Shipped
**Priority:** P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)

---

## 1. Problem Statement

**What problem are we solving?**
[1-3 sentences. Be specific. Include data if available.]

**Who has this problem?**
[Target user/persona. Be specific about segment.]

**How do they solve it today?**
[Current workaround or competitor solution.]

**Why now?**
[Why this is urgent/important at this moment.]

---

## 2. Goals & Success Metrics

**Primary goal:** [One sentence]

**Success metrics:**
| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| [e.g., Demo-to-pilot rate] | 10% | 25% | 30 days |
| [e.g., Support tickets/week] | 15 | 5 | 60 days |

**Non-goals (explicitly out of scope):**
- [Thing we are NOT building]
- [Thing we are NOT optimizing for]

---

## 3. User Stories

As a [persona], I want to [action] so that [outcome].

1. As a **prospect**, I want to hear my AI receptionist before buying so that I know it actually works for my industry.
2. As a **pilot user**, I want to see how many calls my AI answered so that I can justify upgrading to paid.
3. As **Wallace**, I want to see which leads are hottest so that I call the right people first.

---

## 4. Feature Specification

### 4.1 [Feature/Component Name]
**Description:** [What it does]
**User flow:**
1. User does X
2. System responds with Y
3. User sees Z

**Requirements:**
- [ ] Must do A
- [ ] Must do B
- [ ] Must NOT do C

**Edge cases:**
- What if user does X without Y?
- What if API is down?
- What if data is missing?

### 4.2 [Next Feature/Component]
...

---

## 5. Technical Requirements

**Architecture:**
- [Where this lives: website repo, ops repo, GHL, etc.]
- [What it integrates with]
- [Data storage needs]

**API dependencies:**
- [External APIs needed]
- [Rate limits to consider]

**Performance requirements:**
- [Response time targets]
- [Volume/scale expectations]

---

## 6. Design / UX

**Wireframes:** [Link or ASCII mockup]
**Copy:** [Key text/messaging]
**Mobile:** [Mobile-specific requirements]

---

## 7. Launch Plan

**Phase 1 (MVP):**
- [Minimum to ship]
- Timeline: [X days]

**Phase 2 (Enhancement):**
- [Nice-to-haves after MVP proves out]

**Rollout:**
- [ ] Internal testing
- [ ] 3 pilot users
- [ ] All users
- [ ] Public launch

**Rollback plan:**
- [How to revert if something goes wrong]

---

## 8. Open Questions

- [ ] [Unresolved question 1]
- [ ] [Unresolved question 2]
```

---

## Writing Tips

1. **Start with the problem, not the solution** — If you can't articulate the problem clearly, you're not ready to build
2. **One PRD per feature** — Don't bundle unrelated changes
3. **Be specific about scope** — "Non-goals" section prevents scope creep
4. **Write acceptance criteria as tests** — "When X, then Y" format
5. **Include edge cases** — Happy path is easy, edges are where bugs live
6. **Metrics before building** — If you can't measure success, reconsider
7. **Keep it short** — 1-2 pages for small features, 3-5 for large ones

---

## Quick PRD (For Small Features)

When a full PRD is overkill:

```markdown
## [Feature Name]
**Problem:** [1 sentence]
**Solution:** [1-2 sentences]
**Acceptance criteria:**
- [ ] When X happens, Y should occur
- [ ] Z should NOT happen
**Out of scope:** [What this doesn't include]
**Ship by:** [Date]
```
