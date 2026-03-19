---
name: technical-writing
description: "Write clear technical documentation, guides, and content. Use when creating setup guides, how-to docs, runbooks, changelogs, README files, onboarding docs, or technical blog content. Covers document structure, audience-appropriate language, and technical accuracy."
category: documentation
---

# Technical Writing

Write documentation that people actually read and find useful.

---

## Core Principles

1. **Write for your reader, not yourself** — Who is reading this? What do they already know?
2. **Lead with the answer** — Don't make readers wade through context to find what they need
3. **Show, then tell** — Example first, explanation second
4. **One idea per paragraph** — If it has two ideas, split it
5. **Use active voice** — "Click the button" not "The button should be clicked"

---

## Document Types

### How-To Guide (Task-Oriented)
**Purpose:** Help someone accomplish a specific task.
**Structure:**
```
## How to [Do the Thing]

**Prerequisites:**
- Thing you need first
- Another prerequisite

**Steps:**
1. Do this first
2. Then do this
3. Finally do this

**Verify:** [How to confirm it worked]

**Troubleshooting:**
- If X happens → do Y
- If Z happens → do W
```

### Reference Doc (Information-Oriented)
**Purpose:** Provide complete, accurate details.
**Structure:**
```
## [Component Name]

**What it is:** [1 sentence]
**Where it lives:** [File path / URL]

### Configuration
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| ... | ... | ... | ... |

### API / Interface
[Methods, endpoints, parameters]

### Examples
[Code examples for common use cases]
```

### Runbook (Operations)
**Purpose:** Handle incidents and routine operations.
**Structure:**
```
## [Incident/Task Name]

**When to use:** [Trigger condition]
**Severity:** [Low/Medium/High/Critical]
**Time to resolve:** [Expected duration]

### Diagnosis
1. Check X: `command to run`
2. If X shows Y → go to Step 3
3. If X shows Z → go to "Escalation"

### Fix
1. Run: `specific command`
2. Verify: `verification command`
3. Expected output: [what success looks like]

### Escalation
- Contact: [who to contact]
- Provide: [what info to share]
```

### Changelog
```
## [Version] — YYYY-MM-DD

### Added
- New feature description

### Changed
- What was modified and why

### Fixed
- Bug that was fixed

### Removed
- What was removed and why
```

---

## Writing Style

### Do
- Use short sentences (< 25 words)
- Use bullet points for lists of 3+
- Use code blocks for commands, file paths, and code
- Use tables for structured comparisons
- Use bold for key terms on first use
- Include expected output for commands
- Write "you" not "the user"

### Don't
- Don't use jargon without defining it
- Don't write walls of text
- Don't assume the reader knows the context
- Don't use "simply" or "just" (if it were simple, they wouldn't need docs)
- Don't mix instructions with explanations (separate them)
- Don't write "please" in instructions (it's not a request)

---

## Templates

### Setup Guide Opening
```markdown
# Getting Started with [Product]

Get [Product] running in under [X] minutes.

## What You'll Need
- [Prerequisite 1]
- [Prerequisite 2]

## Quick Start

### 1. [First Step Name]
```bash
command to run
```
[One sentence explaining what this does]
```

### Troubleshooting Section
```markdown
## Troubleshooting

### [Error message or symptom]
**Cause:** [Why this happens]
**Fix:** [Exact steps to resolve]

### [Another common issue]
**Cause:** [Why]
**Fix:** [Steps]
```

### Internal Doc Header
```markdown
# [Document Title]
> Last updated: YYYY-MM-DD | Owner: [Name]
> Status: Draft | Active | Deprecated

[One-line summary of what this doc covers]
```
