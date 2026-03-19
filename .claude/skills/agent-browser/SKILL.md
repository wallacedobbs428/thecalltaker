---
name: agent-browser
description: "Browser automation for AI agents via inference.sh. Use when the user needs to navigate web pages, interact with elements, take screenshots, fill forms, scrape data, or automate web interactions."
allowed-tools: Bash(infsh *)
---

# Agentic Browser

Browser automation for AI agents via [inference.sh](https://inference.sh). Uses Playwright under the hood with a simple `@e` ref system for element interaction.

## Quick Start

> Requires inference.sh CLI (`infsh`).

```bash
infsh login
infsh app run agent-browser --function open --input '{"url": "https://example.com"}' --session new
```

## Core Workflow

1. **Open** - Navigate to URL, get `@e` refs for elements
2. **Interact** - Use refs to click, fill, drag, etc.
3. **Re-snapshot** - After navigation/changes, get fresh refs
4. **Close** - End session (returns video if recording)

## Functions

| Function | Description |
|----------|-------------|
| `open` | Navigate to URL, configure browser (viewport, proxy, video recording) |
| `snapshot` | Re-fetch page state with `@e` refs after DOM changes |
| `interact` | Perform actions using `@e` refs (click, fill, drag, upload, etc.) |
| `screenshot` | Take page screenshot (viewport or full page) |
| `execute` | Run JavaScript code on the page |
| `close` | Close session, returns video if recording was enabled |

## Interact Actions

| Action | Description | Required Fields |
|--------|-------------|-----------------|
| `click` | Click element | `ref` |
| `dblclick` | Double-click element | `ref` |
| `fill` | Clear and type text | `ref`, `text` |
| `type` | Type text (no clear) | `text` |
| `press` | Press key (Enter, Tab, etc.) | `text` |
| `select` | Select dropdown option | `ref`, `text` |
| `hover` | Hover over element | `ref` |
| `check` | Check checkbox | `ref` |
| `uncheck` | Uncheck checkbox | `ref` |
| `drag` | Drag and drop | `ref`, `target_ref` |
| `upload` | Upload file(s) | `ref`, `file_paths` |
| `scroll` | Scroll page | `direction`, `scroll_amount` |
| `back` | Go back in history | - |
| `wait` | Wait milliseconds | `wait_ms` |
| `goto` | Navigate to URL | `url` |

## Element Refs

Elements are returned with `@e` refs. Refs are invalidated after navigation — always re-snapshot after clicking links/buttons, form submissions, or dynamic content loading.

## Features

- **Video Recording**: Enable with `"record_video": true` in open
- **Cursor Indicator**: `"show_cursor": true` for visible cursor in screenshots/video
- **Proxy Support**: Route traffic via `proxy_url`, `proxy_username`, `proxy_password`
- **File Upload**: Use `upload` action with `file_paths` array
- **Drag and Drop**: Use `drag` action with `ref` and `target_ref`
- **JavaScript Execution**: Run custom JS with `execute` function

## References

- `references/commands.md` — Full function reference
- `references/snapshot-refs.md` — Ref lifecycle and troubleshooting
- `references/session-management.md` — Session persistence
- `references/authentication.md` — Login flows, OAuth, 2FA
- `references/video-recording.md` — Recording workflows
- `references/proxy-support.md` — Proxy configuration
