---
name: file-organization
description: "Organize codebases, project structures, and file hierarchies. Use when restructuring repositories, cleaning up file layouts, establishing naming conventions, or planning directory structures for new projects."
category: engineering
---

# File Organization

Structure projects so files are findable, predictable, and maintainable.

---

## Principles

1. **Convention over configuration** — Follow established patterns, don't invent new ones
2. **Proximity** — Related files live near each other
3. **Flat over deep** — Prefer `website/blog/` over `website/content/articles/blog/posts/`
4. **Predictable names** — Anyone should guess where a file lives
5. **Separate concerns** — Code, config, data, and docs don't mix

---

## Web Project Structure

```
project/
├── website/                    # Deployable web content
│   ├── index.html              # Homepage
│   ├── signup.html             # Core pages at root
│   ├── calculator.html
│   ├── css/                    # Stylesheets
│   │   ├── main.css
│   │   └── components/
│   ├── js/                     # JavaScript
│   │   ├── app.js
│   │   └── tracking.js
│   ├── images/                 # Static images
│   │   ├── logo.svg
│   │   └── hero/
│   ├── blog/                   # Blog articles
│   │   ├── index.html          # Blog listing
│   │   └── article-slug.html   # Individual posts
│   ├── industries/             # Industry landing pages
│   │   ├── index.html          # Hub page
│   │   └── hvac.html
│   └── fonts/                  # Web fonts
├── ops/                        # Backend scripts
│   ├── scripts/
│   ├── config.py
│   └── state/                  # State files
├── docs/                       # Internal documentation
├── tests/                      # Test files
├── .github/
│   └── workflows/              # CI/CD
└── README.md
```

---

## Naming Conventions

### Files
| Type | Convention | Example |
|------|-----------|---------|
| HTML pages | kebab-case | `answering-service-hvac.html` |
| CSS files | kebab-case | `main-styles.css` |
| JS files | kebab-case | `tct-tracking.js` |
| Python scripts | kebab-case | `blast-engine.py` |
| Config files | kebab-case | `config.py`, `settings.json` |
| State files | kebab-case + `-state` | `max-state.json` |
| Test files | `test-` prefix or `test_` | `test_engine.py` |

### Directories
- Lowercase, kebab-case
- Plural for collections: `images/`, `scripts/`, `docs/`
- Singular for concepts: `website/`, `dashboard/`

---

## When to Split Files

### Split when:
- File exceeds ~500 lines (for HTML/CSS) or ~300 lines (for scripts)
- File contains unrelated functionality
- Multiple people edit the same file frequently
- You find yourself scrolling to find things

### Keep together when:
- Single-file components (HTML + inline CSS/JS for landing pages)
- Files that always change together
- Small utilities (< 50 lines)

---

## Cleanup Checklist

When reorganizing a codebase:

- [ ] Identify orphaned files (unreferenced HTML, unused CSS/JS)
- [ ] Check for duplicate files (same content, different names)
- [ ] Verify all internal links still work after moves
- [ ] Update import paths in scripts
- [ ] Update CI/CD paths if deploy directory changed
- [ ] Update documentation references
- [ ] Git move files (not delete + create) to preserve history: `git mv old new`
- [ ] Verify deployed site works after reorganization

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Everything in root | Can't find anything | Group by type or feature |
| 10+ levels deep | Hard to navigate | Flatten to 2-3 levels |
| `misc/` or `other/` folders | Junk drawer | Give proper names or delete |
| Numbered files (`page1.html`) | No meaning | Use descriptive names |
| Multiple naming conventions | Inconsistent | Pick one, apply everywhere |
| Config scattered everywhere | Hard to manage | Central config directory |
