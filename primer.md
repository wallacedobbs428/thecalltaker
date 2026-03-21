## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-21 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for every small business with a phone line. PayPal bridge pricing: $264/$664/$1,164. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Mills = co-founder/strategy. William = demo closer.

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, 6 AI agents (Atlas, Oracle, Forge, Vector, Prism, Blueprint), intelligence layer
- **Voice AI**: GHL + Bland.ai universal demo agent. Demo line: (615) 784-5747
- **CRM**: GoHighLevel (4,787 contacts, 35 hot leads, $0 MRR)
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via `.github/workflows/deploy.yml` — triggers on `website/**` changes to `main`
- **Payment**: PayPal bridge at thecalltaker.com/pay (Stripe under appeal — Wallace is 16)

## Current Branch & State

- **Branch:** `claude/install-skills-ElbLd` (also tracks on remote)
- **Base:** `master` — both point at same commit `c5dfcb0`
- **Latest commits (March 20):** Jessica brand rebuild — hologram projection, logo interstitial, full section redesign, scroll bar, light/dark toggle, 4-color brand system
- **Working tree:** Clean (no staged or unstaged changes)

## Homepage (website/index.html — 1,270 lines)

- **Brand:** "Jessica" AI receptionist identity, hologram aesthetic
- **Theme:** Dark with green accent, 4-color brand system
- **Hero:** Animated phone mockup, circuit background, floating callouts
- **Key sections:** Hero → Industry → How It Works → Features → Demo → Pricing → FAQ → CTA → Footer
- **External deps:** GSAP 3.12.5 (cdnjs)
- **Logo:** Jessica headset line art on dark background with orbit rings
- **Interstitial:** 3D rotating Jessica logo with orbit ring

## Payment Flow

- **pay.html** — PayPal bridge ($264/$664/$1,164 tiers)
- **signup.html** — 3-step purchase flow
- **pilot/** — free pilot funnel (ghost + index.html)

## Key Hot Leads

- Greg @ Carolina Locksmith (919) 608-3694
- Pamela @ Houston HVAC (713) 367-7985
- 35 total hot leads in GHL pipeline

## Active Priorities

1. **REVENUE**: Convert 35 hot leads → first dollar of MRR. Today.
2. **Website**: Jessica brand rebuild is live, polish and verify all flows
3. **Payment**: PayPal bridge is the path — Stripe under appeal
4. **Ops**: 6 AI agents + 30 launchd services running on Mac

## Known Issues

1. **Stripe not connected** — Wallace is 16, PayPal/Venmo workaround live
2. **$0 MRR** — need first paying customer
3. **Intelligence layer** at ~/thecalltaker-ops/shared/intelligence.json — 6 agents feed into this
