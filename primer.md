## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-19 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$297/$497/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles demos and closing alongside Wallace.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/` or `/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets, outreach ops scripts
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo). Voice ID: `lxYfHSkYm1EzQzGhdbfc` (deep variant, v9)
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)

## Current Branch & Recent Work

- **Branch:** `claude/add-missing-features-XFQcm`
- **Latest session (March 19):** Installed 5 Claude Code extension repos (Impeccable, Agency Agents, oh-my-claudecode, Google Workspace CLI, CLI-Anything)
- **Previous sessions (March 18):** Hero phone animation, warm palette, Lenis smooth scroll, HUD design, floating callouts, iOS-safe circuit bg, Friday urgency bar

## Claude Code Extensions Installed (March 19, 2026)

### 1. Impeccable (pbakaus/impeccable)
- 20 design commands: `/audit`, `/polish`, `/critique`, `/animate`, `/colorize`, `/bolder`, `/quieter`, `/distill`, `/extract`, `/adapt`, `/onboard`, `/typeset`, `/arrange`, `/overdrive`, `/delight`, `/clarify`, `/harden`, `/normalize`, `/optimize`, `/teach-impeccable`
- Enhanced `frontend-design` skill with 7 reference files (typography, color, spatial, motion, interaction, responsive, UX writing)
- Anti-pattern guidance to avoid generic AI aesthetics
- Location: `.claude/skills/` (20 skill folders)

### 2. Agency Agents (msitarzewski/agency-agents)
- 205 expert agent personas across 15 divisions: engineering, design, sales, marketing, product, testing, support, strategy, specialized, project-management, paid-media, integrations, game-development, spatial-computing, academic
- Activate by referencing agent names during conversation
- Location: `.claude/agents/` (15 category folders + individual .md files)

### 3. oh-my-claudecode (Yeachan-Heo/oh-my-claudecode)
- Multi-agent orchestration: `autopilot:`, `/team`, `/ralph`, `/ultrawork`, `/ultraqa`
- Deep interview: `/deep-interview` (Socratic requirements gathering)
- Team mode: `/team 3:executor "task"` (parallel workers)
- Installed via npm: `oh-my-claude-sisyphus`
- Skills + agents copied to `.claude/skills/` and `.claude/agents/`
- Settings: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` enabled in `.claude/settings.json`

### 4. Google Workspace CLI (googleworkspace/cli)
- 42+ gws skills: Gmail, Drive, Calendar, Sheets, Docs, Chat, Meet, Tasks, Forms, Keep, Admin, Slides
- 40+ recipes: batch operations, workflows, cross-service automations
- 10 personas: exec-assistant, project-manager, sales-ops, content-creator, etc.
- **Requires auth:** Run `gws auth setup` + `gws auth login` before first use (needs Google Cloud project)
- Location: `.claude/skills/gws-*`, `persona-*`, `recipe-*`

### 5. CLI-Anything (HKUDS/CLI-Anything)
- Generates CLI wrappers for any desktop app (Blender, GIMP, LibreOffice, etc.)
- Plugin files in `.claude/skills/cli-anything/`
- Supported apps: Blender, GIMP, LibreOffice, OBS Studio, Audacity, Inkscape, Kdenlive, Shotcut, Draw.io, Zoom, Mermaid, ComfyUI, NotebookLM
- **Requires:** Python 3.10+, target app installed

## Outreach Stack v2 (Rebuilt March 15, 2026)

Full 7-component outreach system rebuild. All scripts in `ops/`.

| # | Component | Script | What It Does |
|---|-----------|--------|-------------|
| C6 | Hot Lead 7-Touch | `hot-lead-converter.py` | 7-touch SMS/email/call sequence. Bland.ai voicemail Day 1. Per-touch GHL tagging. |
| C1 | Cold Caller v2 | `cold-caller-v2.py` | Bland.ai outbound calls. Hot leads first. 2x retry with 4hr gaps. |
| C2 | Storm Chaser v3 | `storm-chaser-v3.py` | NWS API storm detection. Emails within 5 min of hail/tornado/wind. |
| C3 | Blast Engine v3 | `blast-engine-v3.py` | 40/day/address, 90s gaps, 5-address rotation, A/B auto-promote. |
| C4 | Lead Quality | `lead-quality-engine.py` | Dedup + quality score 1-10. Only 5+ leads pass to blast. |
| C5 | Speed-to-Lead v2 | `speed-to-lead-v2.py` | 15s hot signal checks. SMS 60s, call 5min, email 10min. Dead lead resurrection. |
| C7 | DM Outreach v2 | `dm-outreach-v2.py` | 3-DM sequence per industry. Copy-paste export for Wallace. |
| NEW | Hot Lead 5-Step | `hot-lead-sequence.py` | 5-step SMS/email/voicemail sequence (Day 0/1/2/4/7). Pain-first + scarcity. |

## Total Skills & Agents Count

- **154 skills** in `.claude/skills/`
- **205 agent files** in `.claude/agents/`
- Settings: `.claude/settings.json` (permissions + OMC env var)

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Outreach stack**: ALL 7 components rebuilt + new hot-lead-sequence — deploy to Mac
- **Stripe**: NOT connected (Wallace is 16). PayPal/Venmo workaround live
- **Bland.ai balance**: Cold caller + voicemails require funded account
- **GHL aliases**: Blast v3 needs 5 aliases verified (wallace@, hello@, support@, info@, team@)
- **Unsubscribe page**: Blast v3 links to thecalltaker.com/unsubscribe — needs building
- **SEO content**: Continue expanding blog with high-intent keyword posts
- **Google Workspace CLI**: Needs `gws auth setup` + `gws auth login` to activate

## Known Blockers

1. Stripe not connected — PayPal/Venmo workaround live
2. GHL API unreachable from CI — deploy from Mac only
3. Retell.ai blocked — needs payment card
4. Bland.ai balance — must be funded before cold caller goes live
5. 5 GHL email aliases need verification
6. Unsubscribe page needs to be built
7. Google Workspace CLI needs auth setup (Google Cloud project + OAuth)
