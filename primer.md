# Primer — The Call Taker

> Last updated: 2026-03-15 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$297/$497/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Co-founder: Mills (strategy, GitHub). William (Wallace's brother) closes demos on Zoom.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/` or `/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: Bland.ai agent (universal demo), GHL-hosted. Retell.ai evaluated but blocked (needs payment card)
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
  dashboard/           # Internal dashboards (not deployed)
  tests/               # Hero regression tests
agents/                # 10 specialized agent configs (01-10)
ops/                   # Ops script mirrors/configs
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

## Recent Work (as of March 15, 2026)

- Local vs national outreach strategy implemented across all engines/templates
- 10/10 demo experience built: phone UI, Web Audio, personalization, conversion overlay
- Robotic TTS voice removed, demo consolidated to single page
- Text contrast boosted site-wide for readability
- Lead capture popup moved to dark theme with green accents
- Mobile hero centering fixed, TTS audio added to demo console
- SEO blog posts finalized

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal. 72-hour strike plan exists
- **Stripe**: NOT connected (Wallace is 16, needs parent/guardian). Biggest blocker to revenue
- **Pilot program**: 5 concurrent slots, 14-day free trial. Funnel is live
- **Outreach**: 17 industries, 20 metros. Blast engine, funnel engine, cold caller all running
- **Voice quality**: Bland.ai latency is 2-13s depending on turn complexity. All levers maxed

## Known Blockers

1. **Stripe not connected** — can't take payments. Setup guide sent via ntfy
2. **Retell.ai blocked** — needs payment card for phone number ($2/mo)
3. **Meta Ads** — needs API token from developers.facebook.com
4. **reply-monitor** — has exit code 1, may need restart
5. **Gmail SMTP passwords** — plaintext in gmail-sender.py

## Key Conventions

- **State files**: Atomic writes (tempfile + os.replace). JSON format
- **Contact registry**: File-locked cross-engine coordination. 3-day gap between same-type touches
- **GHL API**: Must set User-Agent header. Email = `html` field, SMS = `message` field. Phone: `+1XXXXXXXXXX`
- **ntfy**: 5 standardized topics. Typed API via `tct_common.py`. 30-min dedupe. War room context in every alert
- **Deployment**: Only `website/` dir deploys via GitHub Actions. Push to `main` triggers deploy
- **Hero H1**: NEVER set to `display: inline`. "Receptionist" has `no-break-word` span. Regression test exists
- **Public email**: `thecalltakerai@gmail.com` (website), `wallace@mail.thecalltaker.com` (agency ops)

## Key Files to Know

| File | Why |
|------|-----|
| `CLAUDE.md` | Complete system documentation. 44K words. Read first |
| `index.html` | Homepage. Cursor effects, phone mockup, glassmorphism nav |
| `website/index.html` | The actual deployed homepage |
| `.github/workflows/deploy.yml` | GitHub Pages deployment |
| `agents/` | 10 agent role configs |
| `website/tct-tracking.js` | Attribution tracking (UTM, gclid, fbclid) |
| `website/tests/hero-regression.py` | 11 assertions on hero H1 layout |
