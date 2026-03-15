## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-15 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$297/$497/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Co-founder: Mills (strategy, GitHub). William (Wallace's brother) closes demos on Zoom.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/` or `/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo). Voice ID: `lxYfHSkYm1EzQzGhdbfc` (deep variant, v9)
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)

## Repo Structure (this repo, top-level)

```
CLAUDE.md              # 44K system doc — the bible. Read before touching anything
primer.md              # THIS FILE — session context primer
index.html             # Homepage (glassmorphism nav, cursor effects, phone mockup)
website/               # All deployed pages (82 pages, GitHub Pages via Actions)
  industries/          # 13 industry landing pages
  blog/                # 39 blog articles
  case-studies/        # 5 case studies
  pilot/               # Pilot signup flow
  try-funnel/          # $97 starter funnel
  agency-program/      # White-label partner program
  toolkit/             # Sales toolkit (password-gated)
  shared/              # Shared CSS/JS (demo-console.css, demo-experience.css, ui.css)
  dashboard/           # Internal dashboards (not deployed)
  tests/               # Hero regression tests
agents/                # 10 specialized agent configs (01-10)
ops/                   # Voice prompt versions + deploy scripts
sales/                 # Sales assets
outreach/              # Email/SMS templates, call scripts
docs/                  # Trust email sequence, GBP guide
onboarding/            # Customer onboarding assets
tools/                 # Internal tools
ben/, max/, sam/       # Engine state/config mirrors
.github/workflows/     # deploy.yml — deploys website/ to GitHub Pages on push to main
```

## 4 AI Engines (in ops repo)

| Engine | Role | Key File |
|--------|------|----------|
| **Max** | Reply catcher + follow-up machine | `max/max-engine.py` (3,302 lines) |
| **Ben** | Intelligence + conversion scoring | `ben/ben-engine.py` (2,847 lines) |
| **Sam** | Customer success | `sam/sam-engine.py` (2,037 lines) |
| **Donny** | Conversion closer | `donny/donny-engine.py` (2,952 lines) |

## Current Session Context (March 15, 2026)

- On branch `claude/fix-jessica-voice-agent-vt0s0`, 1 commit ahead of remote
- Working tree is clean — no staged or unstaged changes
- Recent work: PayPal/Venmo checkout built, 3-touch close sequence for 35 hot leads, Jessica voice v9, mobile fixes, demo page green theme

## Recent Work (as of March 15, 2026)

- **PayPal/Venmo checkout** — Accept $97/$297/$497 payments today (Stripe blocked)
- **3-touch close sequence** — Built for 35 hot leads
- **Jessica voice agent v9** — Anti-squeaky rewrite. Deeper voice, pitch -1, rate 0.95, stability 0.75, similarity 0.85
- **Demo page colors** — All orange replaced with green (#00C96B)
- **Deploy script upgraded** — v9 with voice settings, fallback voices
- **Competitor research** — Pricing/feature comparison for Smith.ai, Ruby, AnswerConnect, PATLive, Numa, Goodcall (in progress this session)

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal. 72-hour strike plan exists
- **Stripe**: NOT connected (Wallace is 16, needs parent/guardian). PayPal/Venmo checkout built as workaround
- **Voice quality**: v9 prompt deployed. Test by calling (615) 784-5747
- **Pilot program**: 5 concurrent slots, 14-day free trial. Funnel is live
- **Outreach**: 17 industries, 20 metros. Blast engine, funnel engine, cold caller all running
- **Competitor comparison pages**: Research in progress for website content

## Known Blockers

1. **Stripe not connected** — can't take card payments. PayPal/Venmo workaround live
2. **GHL API unreachable from CI** — voice agent settings must be deployed from Mac
3. **Retell.ai blocked** — needs payment card for phone number ($2/mo)
4. **Meta Ads** — needs API token from developers.facebook.com
5. **reply-monitor** — has exit code 1, may need restart
6. **Gmail SMTP passwords** — plaintext in gmail-sender.py

## Voice Agent Quick Reference

| Item | Value |
|------|-------|
| Agent ID | `695947c64b9ed67d8f1077ad` |
| Voice ID (v9) | `lxYfHSkYm1EzQzGhdbfc` (Jessica deep) |
| Prompt version | v9 (`ops/jessica-voice-prompt-v9.md`) |
| Deploy script | `ops/update-jessica-prompt.py` |
| Fallback voices | Rachel, Bella, Elli |

## Key Conventions

- **State files**: Atomic writes (tempfile + os.replace). JSON format
- **Contact registry**: File-locked cross-engine coordination. 3-day gap between same-type touches
- **GHL API**: Must set User-Agent header. Email = `html` field, SMS = `message` field. Phone: `+1XXXXXXXXXX`
- **ntfy**: 5 standardized topics. Typed API via `tct_common.py`. 30-min dedupe
- **Deployment**: Only `website/` dir deploys via GitHub Actions. Push to `main` triggers deploy
- **Hero H1**: NEVER set to `display: inline`. "Receptionist" has `no-break-word` span
- **Demo page colors**: Green (#00C96B), NOT orange
- **Public email**: `thecalltakerai@gmail.com` (website), `wallace@mail.thecalltaker.com` (agency ops)
