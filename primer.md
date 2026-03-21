## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-21 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $19/$97/$497/$997/mo plans (4-tier decoy pricing). 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills (co-founder) handles demos and closing alongside Wallace.

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (universal demo). Demo line: (615) 784-5747
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`

## Current Branch & State

- **Branch:** `claude/install-skills-5xB0P`
- **Base:** `master` (last commit 2026-03-20)
- **Latest commits (March 20):** Complete website rebuild — hologram Jessica projection, logo interstitial, unique section layouts, scroll animations, light/dark mode, 4-color brand system, scroll progress bar
- **Working tree:** Clean (no staged or unstaged changes)

## Skills Installed (March 21)

94 skills now installed in `~/.claude/skills/`, including 3 new packs:

1. **Trail of Bits Security (61 skills)** — CodeQL, Semgrep, AFL++, variant analysis, vulnerability scanners (Solana, Cosmos, Cairo, TON, Substrate, Algorand), fuzzing, audit tools
2. **Researcher (5 skills)** — deep-research, github-research, research-planning, literature-search, literature-review
3. **Figma-to-Code (implement-design)** — 1:1 visual fidelity Figma → production code translation

## Homepage Design (index.html)

- **Latest:** Hologram-style Jessica projection with scan lines + orbit rings
- **Color scheme:** 4-color brand system (green/dark base)
- **Layout:** Dark theme, glassmorphism header, scroll spy, GSAP mobile menu, Lenis smooth scroll
- **Hero:** Animated phone mockup (pure CSS/SVG, no images), circuit background, floating callouts
- **Sections:** Hero → Industry strip → How It Works → Features → Demo → Pricing → FAQ → Final CTA → Footer
- **New features:** Jessica logo interstitial (3D rotating with orbit ring), sliding scroll animations, light/dark mode toggle, thicker scroll progress bar (4px gradient + glow)
- **External deps:** GSAP 3.12.5 (cdnjs), Lenis 1.1.18 (jsdelivr)
- **Font:** Self-hosted Inter (woff2)

## Website Stats

- **Total pages:** ~210+ HTML files deployed
- **Root HTML:** 41 pages
- **Industries:** 19 pages
- **Blog:** 69 posts
- **Case Studies:** 14 + index
- **SEO Pages:** 13 (ai-answering-service/)

## Key Metrics

- **MRR:** $0 (pre-revenue)
- **GHL Contacts:** 4,787
- **Hot Leads:** 35
- **Top targets:** Greg @ Carolina Locksmith (919) 608-3694, Pamela @ Houston HVAC (713) 367-7985

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Security**: All new code audited via Trail of Bits skills before shipping
- **Research**: Competitive intelligence and data-backed strategy via researcher skills
- **Design fidelity**: Figma → production via implement-design skill
- **Stripe**: NOT connected (Wallace is 16). PayPal workaround live
