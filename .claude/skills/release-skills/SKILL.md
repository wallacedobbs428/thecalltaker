---
name: release-skills
description: "Universal release workflow supporting Node.js, Python, Rust, Claude Plugins, and generic projects. Auto-detects project config, generates multi-language changelogs, manages version bumps, and creates release commits with tags."
---

# Release Skills — Universal Release Workflow

Multi-language release automation supporting Node.js, Python, Rust, Claude Plugins, and generic projects.

## Core Features

### Auto-Detection
Automatically identifies project configuration by scanning for version files (package.json, pyproject.toml, Cargo.toml, marketplace.json, or VERSION files) and changelog files using glob patterns.

### Multi-Language Support
Changelogs generated in detected languages following naming conventions like `CHANGELOG.zh.md` or `CHANGELOG_JP.md`, with built-in section title translations across seven languages.

### Conventional Commits
Changes categorized by commit type (feat, fix, docs, refactor, perf, test, style, chore) and organized into language-appropriate changelog sections.

## Workflow Steps

1. **Detect configuration** and scan for version/changelog files
2. **Analyze git log** since last tag to categorize changes
3. **Determine version bump** (major/minor/patch) based on change types
4. **Generate multi-language changelogs** with contributor attribution
5. **Group changes by skill/module** and commit separately
6. **Update version files** while preserving formatting
7. **Obtain user confirmation** before finalizing release
8. **Create release commit and tags**, optionally pushing to remote

## Notable Features

- **Third-party attribution**: Identifies non-owner contributors via GitHub PR metadata and appends `(by @username)` attribution
- **Dry-run mode**: Preview all changes without execution
- **Hook system**: Optional `.releaserc.yml` configuration for `prepare_artifact` and `publish_artifact` hooks
- **README synchronization**: Detects and updates documentation when options, features, or syntax change
