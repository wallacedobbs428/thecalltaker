## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-23 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $19/$97/$497/$997/mo plans (4-tier decoy pricing). 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles demos and closing alongside Wallace.

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on Wallace's Mac (NOT available in this environment)
- **Voice AI**: GHL Voice AI agent (universal demo). Demo line: (615) 784-5747
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/overnight-systems-audit-bcw6P`
- **Base:** `master` (last commit 2026-03-22 — Gideon hero cleanup)
- **Latest commits (March 22):** Gideon voice hero — ElevenLabs Jessica, 3D environment, particles, eye tracking, bloom/flicker/scanlines, GSAP animations, neon aqua-teal palette
- **Working tree:** Clean

## Homepage Design (index.html)

- **Color scheme:** Green accent (#00dc82) / aqua-teal for Gideon hero
- **Layout:** Dark theme, glassmorphism header, scroll spy, GSAP mobile menu, Lenis smooth scroll
- **Hero:** Gideon — 3D room environment, ElevenLabs Jessica voice, particle effects, eye tracking, bloom/scanlines
- **Sections:** Hero → Industry strip → How It Works → Features → Demo → Pricing → FAQ → Final CTA → Footer
- **Pricing:** 4-tier decoy ($19/$97/$497/$997)
- **External deps:** GSAP 3.12.5, Lenis 1.1.18, ElevenLabs
- **Font:** Self-hosted Inter (woff2)

## Key Directories

- `agents/` — 10 agent configs (agent-01 through agent-10)
- `ops/` — 60+ ops scripts + plist definitions (local copies, NOT the live ones on Mac)
- `website/` — deployed to GitHub Pages
- `docs/` — guides, scripts, SEO audits
- `outreach/` — email/SMS sequences
- `ads/` — ad creatives
- `ben/`, `max/`, `sam/` — engine-specific assets

## Environment Constraints

- **This is a cloud/CI environment** — no launchd, no macOS services, no ~/thecalltaker-ops/
- All ops infrastructure runs on Wallace's Mac locally
- This repo is WEBSITE ONLY — no daemon scripts, no plists, no Python ops
- Cannot check live service status from here

## Active Blockers

1. **Stripe not connected** — Wallace is 16, needs parent/guardian. BLOCKS ALL REVENUE.
2. **Retell.ai blocked** — needs payment card
3. **Meta Ads** — needs API token
4. **Email 63% failure** — DNS/SMTP config needs diagnosis
5. **MRR: $0** — no paying clients yet

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Website**: Gideon hero shipped, continue polish
- **SEO**: Expand blog with high-intent keyword posts
- **Outreach**: Multi-industry cold email + call campaigns running on Mac
