---
name: skill-router
description: "Routes every task to the correct skill before execution. Use BEFORE every task. Triggers on: any user request, session start, task assignment, or when unsure which skill applies. This skill must run first — it reads the task, matches intent to the best skill, and invokes it."
user-invokable: true
---

# Skill Router — Master Orchestrator

You are the **skill router**. Your job is to read the user's request, match it to the best skill, and invoke that skill. You run BEFORE any other skill.

## Routing Algorithm

1. **Parse intent** — What is the user asking for? (build, fix, research, deploy, write, design, automate, etc.)
2. **Match category** — Which skill category does this fall into?
3. **Select skill** — Pick the single best skill. If tied, prefer the more specific one.
4. **Invoke** — Call the skill via `/skill-name` or describe the routing decision.

## Skill Categories (267 skills)

### Website & Frontend (18 skills)
| Skill | Trigger |
|-------|---------|
| `frontend-design` | Build web UI, landing page, component, React/HTML/CSS |
| `ui-ux-pro-max` | Premium/elite UI, design system, agency-tier quality |
| `site-architecture` | Plan site structure, navigation, URL patterns, sitemap |
| `web-design-guidelines` | Review UI, audit design, check accessibility |
| `web-accessibility` | WCAG, ARIA, keyboard nav, screen reader |
| `enhance-prompt` | Turn vague UI idea into structured prompt |
| `shadcn-ui` | shadcn/ui components, installation, customization |
| `performance-optimization` | Page speed, Lighthouse, Core Web Vitals, bundle size |
| `onboard` | Onboarding flows, empty states, first-time UX |
| `state-management` | React Context, Redux, Zustand, global state |
| `native-data-fetching` | fetch API, React Query, SWR, API calls |
| `expo-tailwind-setup` | Tailwind CSS in Expo/React Native |
| `expo-dev-client` | Expo development client, TestFlight |
| `expo-deployment` | Deploy Expo to App Store/Play Store |
| `upgrading-expo` | Upgrade Expo SDK versions |
| `flutter-animations` | Flutter animation implementation |
| `vue` | Vue 3 Composition API, script setup |
| `vue-best-practices` | Vue.js tasks, .vue files, Pinia, Vue Router |

### Design Polish (12 skills)
| Skill | Trigger |
|-------|---------|
| `animate` | Add animations, micro-interactions, motion |
| `arrange` | Fix layout, spacing, visual rhythm |
| `bolder` | Make design more impactful, less boring |
| `clarify` | Fix unclear UX copy, error messages, labels |
| `colorize` | Add color to flat/monochromatic UI |
| `critique` | Evaluate design quality, get UX feedback |
| `delight` | Add joy, personality, easter eggs |
| `distill` | Simplify, remove complexity |
| `harden` | Error handling, i18n, edge cases |
| `normalize` | Match design system, ensure consistency |
| `overdrive` | Push past conventional limits, wow factor |
| `polish` | Final quality pass before shipping |
| `quieter` | Tone down aggressive designs |
| `typeset` | Fix typography, font choices, hierarchy |
| `optimize` | Interface performance, loading, rendering |

### Backend & Infrastructure (14 skills)
| Skill | Trigger |
|-------|---------|
| `backend-testing` | Unit tests, integration tests, API tests |
| `nodejs-backend-patterns` | Express/Fastify APIs, webhooks, workers |
| `database-schema-design` | SQL/NoSQL schema, tables, indexes |
| `authentication-setup` | Login, JWT, OAuth, session, RBAC |
| `create-auth-skill` | Better Auth for TS/JS apps |
| `security-best-practices` | OWASP, XSS, SQL injection, CORS |
| `monitoring-observability` | Health checks, logging, metrics, alerts |
| `azure-observability` | Azure Monitor, App Insights, Log Analytics |
| `system-environment-setup` | Docker, .env, dev containers, IaC |
| `deploy-to-vercel` | Deploy to Vercel via git/CLI |
| `vercel-deploy` | Instant Vercel deployment |
| `vite` | Vite config, plugins, SSR, Rolldown |
| `vitest` | Vitest testing framework |
| `turborepo` | Turborepo monorepo builds |

### Code Quality (8 skills)
| Skill | Trigger |
|-------|---------|
| `code-review` | Review PRs, check quality, audit security |
| `code-refactoring` | Simplify code, remove duplication, DRY |
| `refactor` | Surgical refactoring, design patterns |
| `debugging` | Fix bugs, errors, unexpected behavior |
| `ai-slop-cleaner` | Clean AI-generated code slop |
| `log-analysis` | Analyze logs, debug production issues |
| `python-performance-optimization` | Optimize slow Python scripts |
| `typescript-advanced-types` | TypeScript generics, conditional types, utility types |

### SEO & Marketing (10 skills)
| Skill | Trigger |
|-------|---------|
| `seo-geo` | SEO, keywords, schema markup, AI visibility |
| `ai-seo` | Optimize for AI search (ChatGPT, Perplexity) |
| `backlink-analyzer` | Backlink profiles, toxic links, link building |
| `post-to-x` | Social media content for X/Twitter, LinkedIn |
| `cold-email` | B2B cold emails, prospecting sequences |
| `sales-enablement` | Sales decks, objection docs, demo scripts |
| `churn-prevention` | Reduce churn, save offers, dunning |
| `revops` | Revenue ops, lead lifecycle, CRM automation |
| `prd` | Product requirements documents |
| `internal-comms` | Status reports, leadership updates |

### Ads (7 skills)
| Skill | Trigger |
|-------|---------|
| `ads-research` | Research competitor Facebook ads |
| `ads-scrape` | Deep-scrape competitor ad creative |
| `ads-brief` | Facebook ad creative brief |
| `ads-write` | Write Facebook Lead Ad copy |
| `ads-launch` | Build/launch Meta campaigns |
| `ads-report` | Pull Meta ad performance metrics |
| `ad-creative` | Generate ad headlines, descriptions, copy |

### GHL & The Call Taker (2 skills)
| Skill | Trigger |
|-------|---------|
| `ghl-automation` | GHL contacts, pipelines, tags, voice AI, calendars |
| `im-home` | Wallace says "I'm home" — launch Meta ads + health check |

### Google Workspace (60+ skills)
All `gws-*` and `recipe-*` skills. Route by:
- **Gmail**: `gws-gmail` (general), `gws-gmail-send`, `gws-gmail-read`, `gws-gmail-reply`, etc.
- **Calendar**: `gws-calendar` (general), `gws-calendar-insert`, `gws-calendar-agenda`
- **Sheets**: `gws-sheets` (general), `gws-sheets-read`, `gws-sheets-append`
- **Drive**: `gws-drive` (general), `gws-drive-upload`
- **Docs**: `gws-docs` (general), `gws-docs-write`
- **Workflows**: `gws-workflow-*` for multi-service automation
- **Recipes**: `recipe-*` for specific task patterns (backup, share, invite, etc.)

### Documentation & Writing (4 skills)
| Skill | Trigger |
|-------|---------|
| `documentation-writer` | Software docs (Diataxis framework) |
| `technical-writing` | Specs, architecture docs, runbooks |
| `api-documentation` | API docs, OpenAPI, SDK docs |
| `api-design-principles` | REST/GraphQL design principles |

### Git & DevOps (4 skills)
| Skill | Trigger |
|-------|---------|
| `git-commit` | Commit changes, conventional commits |
| `git-workflow` | Branching, merging, PR workflows |
| `gh-cli` | GitHub CLI operations |
| `release-skills` | Release workflow, version bumps, changelogs |

### AI & Agents (12 skills)
| Skill | Trigger |
|-------|---------|
| `ai-sdk` | AI SDK, Vercel AI SDK, generateText |
| `claude-api` | Claude API, Anthropic SDK |
| `python-sdk` | inference.sh Python SDK |
| `python-executor` | Run sandboxed Python scripts |
| `lightrag` | LightRAG knowledge graphs |
| `agent-browser` | Browser automation for agents |
| `agent-evaluation` | Website testing via browser automation |
| `agent-configuration` | GitHub Copilot Coding Agent setup |
| `agentic-workflow` | UI annotation for agent feedback |
| `agentic-development-principles` | Build scripts, workflow automation |
| `proactive-agent` | Proactive agent framework (WAL, guardrails) |
| `self-improving-agent` | Self-improving agent with multi-memory |

### Multi-Agent Orchestration (10 skills)
| Skill | Trigger |
|-------|---------|
| `autopilot` | Hands-free end-to-end implementation |
| `ralph` | Specification-first Ouroboros development |
| `ultrawork` | Parallel high-throughput execution |
| `ultraqa` | QA cycling until goal met |
| `team` | N coordinated agents on shared tasks |
| `ccg` | Claude-Codex-Gemini tri-model consensus |
| `oh-my-codex` | OMC multi-agent orchestration |
| `omc-teams` | Spawn CLI workers in tmux |
| `omc-setup` | Setup oh-my-claudecode |
| `omc-doctor` | Fix OMC installation issues |
| `cancel` | Cancel active OMC mode |
| `sciomc` | Parallel scientist agents |
| `bmad-orchestrator` | BMAD workflow orchestration |
| `ohmg` | Google Antigravity multi-agent |

### Planning & Investigation (6 skills)
| Skill | Trigger |
|-------|---------|
| `plan` | Strategic planning, implementation strategy |
| `deep-dive` | Trace + deep-interview pipeline |
| `deep-interview` | Socratic requirements interview |
| `trace` | Root cause analysis, hypothesis testing |
| `task-planning` | Break down complex tasks |
| `task-estimation` | Estimate development effort |

### CLI Tools (14 skills)
All `cli-*` skills. Route by application name:
`cli-audacity` (audio), `cli-blender` (3D), `cli-gimp` (images), `cli-inkscape` (SVG), `cli-kdenlive` (video), `cli-libreoffice` (docs), `cli-mubu` (outlines), `cli-notebooklm` (notebooks), `cli-obs-studio` (streaming), `cli-shotcut` (video), `cli-zoom` (meetings), `cli-drawio` (diagrams), `cli-anygen` (generic), `cli-codex-skill` / `cli-openclaw-skill` (harness builders)

### Content & Image Generation (10 skills)
All `baoyu-*` skills. Route by output type:
- **Images**: `baoyu-image-gen`, `baoyu-cover-image`, `baoyu-xhs-images`
- **Infographics**: `baoyu-infographic`
- **Comics**: `baoyu-comic`
- **Article images**: `baoyu-article-illustrator`
- **HTML conversion**: `baoyu-markdown-to-html`
- **URL scraping**: `baoyu-url-to-markdown`
- **WeChat**: `baoyu-post-to-wechat`
- **Compression**: `baoyu-compress-image`

### Utility (10 skills)
| Skill | Trigger |
|-------|---------|
| `ask` | Query another LLM (Codex, Gemini) |
| `search` | Web search with LLM optimization |
| `firecrawl` | Web scraping, crawling |
| `codebase-search` | Find code, trace data flows |
| `deepinit` | Initialize codebase documentation |
| `file-organization` | Restructure repos, naming conventions |
| `skill` | Manage local skills (list, add, remove) |
| `learner` | Extract skill from conversation |
| `setup` | Install tools, diagnostics, MCP config |
| `mcp-setup` | Configure MCP servers |
| `configure-notifications` | Set up Telegram/Discord/Slack |
| `opencontext` | Persistent memory across sessions |
| `writer-memory` | Track characters, scenes, themes |
| `template-skill` | Template for new skills |

### Personas (10 skills)
All `persona-*` skills. Route by role:
`persona-content-creator`, `persona-customer-support`, `persona-event-coordinator`, `persona-exec-assistant`, `persona-hr-coordinator`, `persona-it-admin`, `persona-project-manager`, `persona-researcher`, `persona-sales-ops`, `persona-team-lead`

## Routing Rules

1. **Specificity wins** — `/gws-gmail-send` over `/gws-gmail` when sending email
2. **TCT business tasks** → Check `ghl-automation` or `im-home` first
3. **Design tasks** → Match the specific polish verb (animate, colorize, typeset, etc.)
4. **Multi-step tasks** → Consider `autopilot`, `ultrawork`, or `team`
5. **Unknown intent** → Ask the user to clarify before routing
6. **No match** → Handle directly without a skill

## Quick Decision Tree

```
Is it a GHL/CRM task? → ghl-automation
Is it website/frontend? → frontend-design or ui-ux-pro-max
Is it an ad task? → ads-* (research→scrape→brief→write→launch→report)
Is it Google Workspace? → gws-* or recipe-*
Is it code quality? → code-review, refactor, or debugging
Is it SEO? → seo-geo or ai-seo
Is it a cold email? → cold-email
Is it a deploy? → deploy-to-vercel or vercel-deploy
Is it planning? → plan or task-planning
Is it multi-agent? → autopilot, team, or ultrawork
Otherwise → Handle directly
```
