# The Call Taker — Installed Skills & Agents Inventory

> **Purpose:** Paste this into any new Claude Code session so Claude knows every skill and agent installed, what each does, and when to use it.
> **Last updated:** March 19, 2026

---

## How This Works

Skills live in `.claude/skills/` and are invoked with `/skill-name` slash commands. Agents live in `.claude/agents/` and are automatically used by the Agent tool when tasks match their description. You don't need to tell Claude to use them — Claude sees the skill list in its system prompt and triggers them automatically. This document exists so YOU know what's installed and can reference it.

---

## SLASH COMMAND SKILLS (9 installed)

### Meta Ads Pipeline (6 skills — run in order)

| Skill | Slash Command | What It Does | When To Use |
|-------|--------------|--------------|-------------|
| **ads-research** | `/ads-research [vertical]` | Searches Facebook Ad Library for competitor ads in a vertical. Finds competitor names, ad counts, longevity, angles, weaknesses. | "What ads are competitors running for HVAC?" or "Research locksmith Facebook ads" |
| **ads-scrape** | `/ads-scrape [vertical]` | Deep-analyzes competitor ad creative — hooks, copy structure, CTAs, formats. Identifies what's working and what's burned out. | After `/ads-research`. "Break down why their ads work" |
| **ads-brief** | `/ads-brief [vertical]` | Generates a complete creative brief — targeting, angles, hooks, compliance checklist, testing framework. | After `/ads-scrape`. "Write me an ad brief for plumbing" |
| **ads-write** | `/ads-write [vertical]` | Writes 3 full ad sets — headlines, primary text, descriptions, lead form questions, CTAs. Meta-compliant, no "AI" language. | After `/ads-brief`. "Write the actual ad copy for dental" |
| **ads-launch** | `/ads-launch [vertical]` | Builds Facebook Lead Ad campaigns via Meta Marketing API. Creates campaign + ad set + ads — ALL PAUSED by default. Never auto-publishes. | After `/ads-write`. "Launch the HVAC campaign" — requires `META_ACCESS_TOKEN` and `META_AD_ACCOUNT_ID` env vars |
| **ads-report** | `/ads-report [vertical]` | Pulls live performance metrics for active Meta ad campaigns. Reports spend, CPL, leads. Recommends kill/scale/hold decisions against vertical benchmarks. | "How are our ads doing?" or "Pull today's ad numbers" — run daily |

**Full ads pipeline order:** `/ads-research` → `/ads-scrape` → `/ads-brief` → `/ads-write` → `/ads-launch` → `/ads-report` (daily)

**CPL benchmarks built in:** Towing $12, Locksmith $15, HVAC $18, Plumbing $20, Roofing $22, Dental $35

---

### CRM & Operations (1 skill)

| Skill | Slash Command | What It Does | When To Use |
|-------|--------------|--------------|-------------|
| **ghl-automation** | `/ghl-automation` | Manages GoHighLevel via REST API v2 — contacts, pipelines, opportunities, tags, custom fields, calendars, appointments, conversations, workflows, voice AI. | Any GHL task: "Create a contact in GHL", "Move this lead to the pipeline", "Set up a booking calendar", "Update the voice AI agent", "Tag all pilot leads" |

**Key GHL constants (built into skill):**
- API Key: `pit-771d5b3f-...`
- Location ID: `tQb9YmrGDrdVUJYPKrsY`
- Contacts API: `2021-07-28`, Conversations API: `2021-04-15`
- Email body = `"html"`, SMS body = `"message"`

---

### Knowledge Graphs (1 skill)

| Skill | Slash Command | What It Does | When To Use |
|-------|--------------|--------------|-------------|
| **lightrag** | `/lightrag` | Builds and queries knowledge graphs using LightRAG (`lightrag-hku` Python package). Inserts documents, queries with 5 search modes (naive, local, global, hybrid, mix). | "Build a knowledge graph from our lead data", "Set up RAG for customer support", "Query the knowledge base" |

---

### Frontend Design (1 skill)

| Skill | Slash Command | What It Does | When To Use |
|-------|--------------|--------------|-------------|
| **ui-ux-pro-max** | `/ui-ux-pro-max` | Agency-tier UI/UX design system. Maps user journeys, builds design tokens, handles all 5 interaction states, dark/light mode, WCAG AA accessibility, physics-based motion. Mobile-first. | Any frontend work: "Build a landing page", "Redesign the dashboard", "Make it look premium", any React/HTML/CSS/Tailwind task |

**Always runs a UX audit first.** Outputs single-file HTML/CSS/JS or React JSX.

---

## AGENTS (2 installed)

Agents are NOT slash commands — they're automatically invoked by the Agent tool when a task matches their description.

### call-taker-army

**What it is:** The Call Taker's 10-agent command center. Covers all business operations.

**10 specialized functions:**
1. **Voice Agent Engineering** — fix voice agent issues, optimize prompts, configure GHL voice AI settings
2. **Outbound Sales** — write cold emails, SMS sequences, call scripts for any industry
3. **Content Creation** — social media posts, blog content, marketing copy across platforms
4. **Lead Intelligence** — research companies in specific markets, build lead profiles with scoring
5. **Conversion Optimization** — build/redesign website pages, landing pages, funnels
6. **GHL Systems** — design pipelines, workflows, automations in GoHighLevel
7. **Competitive Analysis** — research competitor pricing, features, weaknesses, build battle cards
8. **Demo Closing** — prepare demo scripts, objection handling, pre-demo checklists
9. **Client Success** — onboarding checklists, welcome emails, GHL setup for new clients
10. **Growth Strategy** — weekly intelligence briefs, bottleneck analysis, roadmap updates

**Triggers on:** Any Call Taker business task — voice agent, sales, content, leads, website, GHL, competitors, demos, clients, strategy.

---

### diagnostics-sentinel

**What it is:** Systems diagnostics engineer and SRE. Runs comprehensive health checks.

**What it checks:**
- Code health (tests, lint, type errors, builds)
- Dependency health (installed, compatible, secure)
- Configuration health (env vars, secrets, settings)
- Infrastructure health (services, ports, disk, memory, processes)
- Application health (API endpoints, response times, data integrity)
- Log analysis (errors, warnings, unusual patterns)
- Performance baselines

**Triggers on:** "Check if services are healthy", "Run diagnostics", after deployments, when errors are detected, log anomalies, or proactively when failures are observed.

---

## QUICK REFERENCE — When To Say What

| You Want To... | Say This |
|----------------|----------|
| Research competitor Facebook ads | `/ads-research hvac` |
| Analyze competitor ad creative | `/ads-scrape hvac` |
| Generate an ad strategy brief | `/ads-brief hvac` |
| Write actual ad copy | `/ads-write hvac` |
| Launch ads (paused) on Meta | `/ads-launch hvac` |
| Check ad performance | `/ads-report` |
| Do anything in GoHighLevel | `/ghl-automation` + describe the task |
| Build a knowledge graph | `/lightrag` |
| Build/redesign any UI | `/ui-ux-pro-max` |
| Fix voice agent / write emails / research leads / prep demo / anything business | Just describe the task (call-taker-army auto-triggers) |
| Run system health checks | Just say "run diagnostics" (diagnostics-sentinel auto-triggers) |

---

## What's NOT Installed (From Previous Sessions)

The screenshots show 45 + 19 + 154 skills were added in earlier sessions on other branches, but those branches were never merged into main. The skills referenced in those sessions (vue, vite, vitest, agentic-workflow, deploy-to-vercel, code-refactoring, backend-patterns, performance-optimization, api-design-principles, monitoring-observability, prd, task-planning, churn-prevention, search-optimization, shadcn-ui, etc.) are **not currently installed**. Only the 9 skills and 2 agents listed above are live.

---

## File Locations

```
.claude/
├── agents/
│   ├── call-taker-army.md          # 10-agent business command center
│   └── diagnostics-sentinel.md     # System health & diagnostics
├── agent-memory/
│   └── call-taker-army/            # Persistent memory for the army agent
├── skills/
│   ├── ads-research/SKILL.md       # Facebook Ad Library competitor research
│   ├── ads-scrape/SKILL.md         # Deep ad creative analysis
│   ├── ads-brief/SKILL.md          # Creative strategy brief generator
│   ├── ads-write/SKILL.md          # Ad copy production (3 ad sets)
│   ├── ads-launch/SKILL.md         # Meta API campaign builder (paused)
│   ├── ads-report/SKILL.md         # Live performance metrics + kill/scale
│   ├── ghl-automation/SKILL.md     # GoHighLevel CRM automation
│   ├── lightrag/SKILL.md           # Knowledge graph RAG pipeline
│   └── ui-ux-pro-max/SKILL.md     # Agency-tier frontend design
└── settings.json                   # Permissions (all tools allowed)
```
