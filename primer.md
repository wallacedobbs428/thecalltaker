## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-28 | Rewrite this file at the start of every session.

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

- **Branch:** `claude/check-wallace-mcp-amplify-HcptO`
- **Base:** `main` (last commit 2026-03-28)
- **Latest commits (March 28):** GIDEON self-use case study, Caller Demand Map audit tool, personalized demo pages, FB ad landing page
- **Working tree:** `mcp-video-understand/` is untracked (new MCP server built this session)

## Recent Work (March 28)

- Built `mcp-video-understand/` MCP server — gives Claude the ability to understand video files via frame extraction, scene change detection, audio transcription (Whisper), and metadata. 5 tools: analyze-video, extract-frames, transcribe-audio, get-video-info, describe-scene.

## Homepage Design (index.html)

- **Color scheme:** Green accent (#00dc82) — all CSS vars map to same green
- **Layout:** Dark theme, glassmorphism header, scroll spy, GSAP mobile menu, Lenis smooth scroll
- **Hero:** Animated phone mockup (pure CSS/SVG, no images), circuit background, floating callouts
- **Sections:** Hero -> Industry strip -> How It Works -> Features -> Demo -> Pricing -> FAQ -> Final CTA -> Footer
- **Pricing:** 4-tier decoy ($19/$97/$497/$997), urgency badge with countdown
- **External deps:** GSAP 3.12.5 (cdnjs), Lenis 1.1.18 (jsdelivr)

## Website Stats

- **Total pages:** ~210+ HTML files deployed
- **Root HTML:** 41 pages
- **Industries:** 19 pages
- **Blog:** 69 posts
- **Case Studies:** 14 + index
- **SEO Pages:** 13 (ai-answering-service/)
- **Pilot funnel:** 3 pages
- **Try funnel:** 3 pages

## MCP Servers

- **mcp-video-understand/** — Video understanding server. Node.js + ffmpeg. 5 tools. Requires ffmpeg on PATH. Optional Whisper transcription via TCT_OPENAI_API_KEY env var.

## Known Issues (Current)

1. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
2. **CLAUDE.md documents 13 industries** — actual site has 19
3. **premium.css is empty** — loaded on every page, zero CSS rules

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal
- **Website polish**: Fix urgency countdown, clean orphaned files, schema consistency
- **SEO content**: Continue expanding blog with high-intent keyword posts
