# The Call Taker — Installed Skills & Agents Inventory

> **Purpose:** Reference doc so Claude knows every skill and agent installed, what each does, and when to use it.
> **Last updated:** March 19, 2026
> **Totals:** 167 skills, 163 agents

---

## How This Works

Skills live in `.claude/skills/` and are invoked with `/skill-name` slash commands. Agents live in `.claude/agents/` and are automatically used by the Agent tool when tasks match their description. Claude sees the skill list in its system prompt and triggers them automatically.

---

## SKILL SOURCES

| Source | What It Added | Count |
|--------|--------------|-------|
| **Custom (The Call Taker)** | ads-brief/scrape/write/launch/report/research, ghl-automation, lightrag, ui-ux-pro-max | 9 skills |
| **oh-my-claudecode** | autopilot, ultrawork, ultraqa, ralph, team, ccg, ask, plan, trace, deep-dive, deep-interview, ai-slop-cleaner, learner, + more | 29 skills |
| **Impeccable** | audit, polish, normalize, typeset, arrange, animate, colorize, bolder, quieter, distill, harden, optimize, overdrive, frontend-design, + more | 21 skills |
| **Google Workspace CLI** | gws-gmail, gws-calendar, gws-drive, gws-sheets, gws-docs, gws-chat, gws-meet, gws-tasks, gws-forms, gws-keep, + 80 recipes/personas/workflows | 93 skills |
| **CLI-Anything** | cli-blender, cli-gimp, cli-inkscape, cli-zoom, cli-obs-studio, cli-libreoffice, cli-drawio, cli-audacity, cli-kdenlive, cli-shotcut, + more | 15 skills |

| Source | What It Added | Count |
|--------|--------------|-------|
| **Custom (The Call Taker)** | call-taker-army, diagnostics-sentinel | 2 agents |
| **oh-my-claudecode** | analyst, architect, code-reviewer, code-simplifier, critic, debugger, designer, document-specialist, executor, explore, git-master, planner, qa-tester, scientist, security-reviewer, test-engineer, tracer, verifier, writer | 19 agents |
| **Agency Agents** | 142 expert persona agents across: engineering, sales, marketing, design, product, testing, support, project-mgmt, academic, paid-media, specialized, game-dev, spatial-computing, strategy | 142 agents |

---

## QUICK REFERENCE — Most Useful Skills

### The Call Taker Business (Custom)
| Command | What It Does |
|---------|-------------|
| `/ads-research [vertical]` | Research competitor Facebook ads |
| `/ads-scrape [vertical]` | Deep-analyze competitor ad creative |
| `/ads-brief [vertical]` | Generate creative strategy brief |
| `/ads-write [vertical]` | Write 3 full ad sets (Meta-compliant) |
| `/ads-launch [vertical]` | Build Meta campaigns (all PAUSED) |
| `/ads-report [vertical]` | Pull live ad performance metrics |
| `/ghl-automation` | GoHighLevel CRM operations |
| `/lightrag` | Build/query knowledge graphs |
| `/ui-ux-pro-max` | Agency-tier frontend design |

### Autonomous Workflows (oh-my-claudecode)
| Command | What It Does |
|---------|-------------|
| `/autopilot` | Full autonomous execution from idea to code |
| `/ultrawork` | Parallel execution engine for high-throughput tasks |
| `/ultraqa` | QA cycling — test, verify, fix, repeat until done |
| `/ralph` | Self-referential loop until task completion |
| `/team` | N coordinated agents on shared task list |
| `/ccg` | Claude-Codex-Gemini tri-model orchestration |
| `/ask` | Ask Claude, Codex, or Gemini via CLI |
| `/plan` | Strategic planning with interview workflow |
| `/trace` | Evidence-driven tracing for debugging |
| `/deep-dive` | Trace → deep-interview pipeline |
| `/deep-interview` | Socratic interview before execution |
| `/ai-slop-cleaner` | Clean AI-generated code slop |
| `/learner` | Extract a learned skill from conversation |
| `/omc-setup` | Setup oh-my-claudecode |
| `/mcp-setup` | Configure MCP servers |
| `/sciomc` | Parallel scientist agents for analysis |
| `/external-context` | Web searches and doc lookup |
| `/cancel` | Cancel any active OMC mode |

### Design System (Impeccable)
| Command | What It Does |
|---------|-------------|
| `/audit` | Comprehensive design quality audit |
| `/polish` | Final quality pass before shipping |
| `/normalize` | Match design to your design system |
| `/typeset` | Fix typography issues |
| `/arrange` | Fix layout, spacing, visual rhythm |
| `/animate` | Add purposeful animations |
| `/colorize` | Add strategic color |
| `/bolder` | Amplify safe/boring designs |
| `/quieter` | Tone down aggressive designs |
| `/distill` | Strip to essence, remove complexity |
| `/harden` | Better error handling, i18n, resilience |
| `/optimize` | Improve performance |
| `/overdrive` | Push past conventional design limits |
| `/frontend-design` | Production-grade frontend interfaces |
| `/critique` | UX evaluation |
| `/extract` | Extract reusable components/tokens |
| `/clarify` | Improve UX copy and microcopy |
| `/onboard` | Design onboarding flows |
| `/adapt` | Cross-device/screen adaptation |
| `/delight` | Add joy and personality |
| `/teach-impeccable` | One-time design context setup |

### Google Workspace (GWS CLI)
| Command | What It Does |
|---------|-------------|
| `/gws-gmail` | Send, read, manage email |
| `/gws-gmail-send` | Send an email |
| `/gws-gmail-read` | Read a message |
| `/gws-gmail-triage` | Show unread inbox summary |
| `/gws-calendar` | Manage calendars and events |
| `/gws-calendar-agenda` | Show upcoming events |
| `/gws-calendar-insert` | Create a new event |
| `/gws-drive` | Manage files, folders, shared drives |
| `/gws-drive-upload` | Upload a file |
| `/gws-sheets` | Read and write spreadsheets |
| `/gws-docs` | Read and write Google Docs |
| `/gws-chat` | Manage Chat spaces and messages |
| `/gws-meet` | Manage Google Meet |
| `/gws-tasks` | Manage task lists and tasks |
| `/gws-forms` | Read and write Google Forms |
| `/gws-keep` | Manage Google Keep notes |
| `/gws-slides` | Read and write presentations |
| `/gws-people` | Manage contacts and profiles |

**GWS requires auth:** Run `gws auth setup` + `gws auth login` on your Mac first.

### CLI-Anything (Desktop App Control)
| Command | What It Does |
|---------|-------------|
| `/cli-blender` | Control Blender via CLI |
| `/cli-gimp` | Control GIMP via CLI |
| `/cli-inkscape` | Control Inkscape via CLI |
| `/cli-zoom` | Control Zoom via CLI |
| `/cli-obs-studio` | Control OBS Studio via CLI |
| `/cli-libreoffice` | Control LibreOffice via CLI |
| `/cli-drawio` | Control Draw.io via CLI |
| `/cli-audacity` | Control Audacity via CLI |
| `/cli-kdenlive` | Control Kdenlive via CLI |
| `/cli-shotcut` | Control Shotcut via CLI |

---

## AGENTS (163 total — auto-triggered, no slash command needed)

### The Call Taker Custom (2)
- **call-taker-army** — 10-agent business command center (voice, sales, content, leads, website, GHL, competitors, demos, clients, strategy)
- **diagnostics-sentinel** — System health checks, SRE diagnostics

### oh-my-claudecode (19)
analyst, architect, code-reviewer, code-simplifier, critic, debugger, designer, document-specialist, executor, explore, git-master, planner, qa-tester, scientist, security-reviewer, test-engineer, tracer, verifier, writer

### Agency Agents by Category (142)
- **Engineering (22):** senior-developer, software-architect, backend-architect, frontend-developer, mobile-app-builder, devops-automator, sre, security-engineer, ai-engineer, data-engineer, database-optimizer, code-reviewer, technical-writer, git-workflow-master, incident-response-commander, rapid-prototyper, embedded-firmware-engineer, solidity-smart-contract-engineer, threat-detection-engineer, autonomous-optimization-architect, ai-data-remediation-engineer, + more
- **Sales (8):** sales-coach, sales-engineer, sales-pipeline-analyst, sales-outbound-strategist, sales-deal-strategist, sales-account-strategist, sales-proposal-strategist, sales-discovery-coach
- **Marketing (22):** content-creator, seo-specialist, growth-hacker, social-media-strategist, tiktok-strategist, linkedin-content-creator, instagram-curator, twitter-engager, reddit-community-builder, podcast-strategist, app-store-optimizer, ai-citation-strategist, + regional specialists
- **Design (8):** ui-designer, ux-architect, ux-researcher, brand-guardian, visual-storyteller, image-prompt-engineer, whimsy-injector, inclusive-visuals-specialist
- **Product (4):** product-manager, feedback-synthesizer, sprint-prioritizer, trend-researcher, behavioral-nudge-engine
- **Testing (8):** accessibility-auditor, api-tester, evidence-collector, performance-benchmarker, reality-checker, test-results-analyzer, tool-evaluator, workflow-optimizer
- **Support (6):** support-responder, analytics-reporter, executive-summary-generator, finance-tracker, infrastructure-maintainer, legal-compliance-checker
- **Project Mgmt (5):** project-shepherd, experiment-tracker, jira-workflow-steward, studio-operations, studio-producer, project-manager-senior
- **Paid Media (7):** ppc-strategist, paid-social-strategist, creative-strategist, programmatic-buyer, search-query-analyst, tracking-specialist, auditor
- **Specialized (20+):** mcp-builder, salesforce-architect, workflow-architect, developer-advocate, document-generator, compliance-auditor, recruitment-specialist, agents-orchestrator, blockchain-security-auditor, supply-chain-strategist, + more
- **Academic (5):** anthropologist, geographer, historian, narratologist, psychologist
- **Game Dev (5):** game-designer, level-designer, narrative-designer, technical-artist, game-audio-engineer
- **Spatial Computing (5):** visionos-spatial-engineer, xr-immersive-developer, xr-interface-architect, xr-cockpit-interaction-specialist, macos-spatial-metal-engineer
- **Strategy (2):** nexus-strategy, terminal-integration-specialist

---

## File Structure

```
.claude/
├── agents/                         # 163 agent files (.md)
│   ├── call-taker-army.md          # Custom: 10-agent business ops
│   ├── diagnostics-sentinel.md     # Custom: system health
│   ├── analyst.md ... writer.md    # oh-my-claudecode: 19 agents
│   └── engineering-*.md, sales-*.md, marketing-*.md ...  # Agency Agents: 142
├── agent-memory/
│   └── call-taker-army/            # Persistent memory
├── skills/                         # 167 skill directories
│   ├── ads-*/                      # Custom: Meta ads pipeline (6)
│   ├── ghl-automation/             # Custom: GoHighLevel CRM
│   ├── lightrag/                   # Custom: Knowledge graphs
│   ├── ui-ux-pro-max/             # Custom: Frontend design
│   ├── autopilot/ ... ultrawork/  # oh-my-claudecode (29)
│   ├── audit/ ... typeset/        # Impeccable design (21)
│   ├── gws-*/                      # Google Workspace CLI (93)
│   └── cli-*/                      # CLI-Anything (15)
└── settings.json                   # Permissions (all tools allowed)
```
