---
name: git-workflow
description: "Follow git best practices for branching, committing, merging, and collaborating. Use when setting up branch strategies, writing commit messages, resolving merge conflicts, managing releases, or reviewing pull requests."
category: engineering
---

# Git Workflow

Clean git history, clear commit messages, and reliable branching.

---

## Branch Strategy

### Branch Types
```
main                    # Production-ready code (deploys to GitHub Pages)
├── feature/[name]      # New features
├── fix/[name]          # Bug fixes
├── claude/[name]       # Claude Code automated work
└── hotfix/[name]       # Emergency production fixes
```

### Branch Naming
```
feature/add-unsubscribe-page
fix/hero-text-splitting
claude/rebuild-outreach-stack
hotfix/broken-checkout-link
```

---

## Commit Messages

### Format
```
<type>: <short description>

[Optional body: why this change was made]
[Optional: what was changed and how]
```

### Types
| Type | When |
|------|------|
| Add | New feature or file |
| Fix | Bug fix |
| Update | Enhancement to existing feature |
| Remove | Deleting code or files |
| Refactor | Code restructure without behavior change |
| Style | CSS/formatting only changes |
| Docs | Documentation only |
| Test | Adding or fixing tests |
| Deploy | Deployment configuration |

### Good Examples
```
Add: unsubscribe page with GHL tag removal

Fix: hero h1 splitting "Receptionist" across lines
Root cause: inline display on h1 conflicted with 278px badge.
Set display:block + white-space:nowrap wrapper.

Update: blast engine daily limit from 120 to 160

Refactor: extract email sending to tct_common.send_email()

Remove: deprecated industry pages replaced by /industries/
```

### Bad Examples
```
# Too vague
Updated stuff
Fixed bug
Changes

# Too long in subject
Added a new page for unsubscribing from emails that removes the GHL tag and shows confirmation
```

---

## Common Operations

### Start New Feature
```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature
# ... make changes ...
git add specific-files.html
git commit -m "Add: feature description"
git push -u origin feature/my-feature
```

### Sync Branch with Main
```bash
git checkout feature/my-feature
git fetch origin main
git rebase origin/main
# Fix any conflicts, then:
git push --force-with-lease  # Safe force push (only your branch)
```

### Undo Last Commit (Keep Changes)
```bash
git reset --soft HEAD~1
# Changes are now staged but uncommitted
```

### Undo Changes to a File
```bash
git checkout -- path/to/file.html
```

### Stash Work in Progress
```bash
git stash push -m "WIP: feature name"
# ... do other work ...
git stash pop
```

### Cherry-Pick a Commit
```bash
git cherry-pick abc1234
```

---

## Merge Conflict Resolution

### Steps
1. **Understand both sides** — Read the conflict markers carefully
2. **Keep the correct version** — Don't blindly accept "ours" or "theirs"
3. **Test after resolving** — Conflicts can introduce subtle bugs
4. **Commit the resolution** — `git add . && git commit`

### Conflict Markers
```
<<<<<<< HEAD (your changes)
<h1>Your Version</h1>
=======
<h1>Their Version</h1>
>>>>>>> feature/other-branch
```

### Prevention
- Pull/rebase frequently (don't let branches diverge far)
- Communicate about shared files
- Keep commits small and focused

---

## Pre-Push Checklist

- [ ] All files intentionally staged (no accidental additions)
- [ ] No secrets/API keys in committed files
- [ ] Commit messages are clear and descriptive
- [ ] Code works locally (tested)
- [ ] No merge conflicts with target branch
- [ ] Branch name follows convention

---

## GitHub Pages Deployment

```
Push to main → GitHub Actions → Deploy website/ to Pages

Only files in website/ are deployed.
Only triggers when website/** files change.
```

To deploy:
```bash
git checkout main
git merge feature/my-feature
git push origin main
# GitHub Actions auto-deploys
```
