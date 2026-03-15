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
website/               # All deployed pages (93 pages, GitHub Pages via Actions)
  industries/          # 13 industry landing pages
  blog/                # 49 blog articles (upgraded with SEO machine)
  case-studies/        # 5 case studies (NOTE: these are fabricated — no real customers yet)
  pilot/               # Pilot signup flow — PRIMARY CONVERSION PATH
  walkin.html          # Walk-in closer kit (NEW — print-ready leave-behind for Nashville)
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

- On branch `claude/fix-jessica-voice-agent-vt0s0`, synced with remote
- **CRITICAL BUSINESS STATE**: 4,787 GHL contacts, 35 hot leads, 0 paying customers, $0 MRR, 0 demos booked
- Fake social proof REMOVED this session — replaced with honest "founding member" positioning
- All homepage CTAs consolidated to `/pilot/` (single conversion path)
- Walk-in closer kit built at `/walkin.html` for Nashville in-person sales

## Recent Work (as of March 15, 2026)

### This Session — Revenue-Critical Changes
- **Walk-in closer kit** (`/walkin.html`) — print-ready page for Nashville walk-ins with QR code to demo line
- **Fake social proof removed** — 6 fabricated testimonials, Google Review badges, fake 4.9/23 rating all deleted
- **Founding member positioning** — 5 spots, locked price, founder access, honest "hear it yourself" cards
- **Single conversion path** — all book.html links on homepage redirected to /pilot/
- **Schema.org aggregateRating removed** — was fake (0 real reviews exist)

### Previous Sessions
- **Conversion tracking** — scroll depth, click heatmap, session metrics in tct-tracking.js
- **Blog SEO machine** — all 49 blog posts upgraded (author, title format, cover images, mid-article CTAs)
- **Mobile overhaul** — dual sticky bottom bar with call + pilot CTA
- **Phase 3 full build** — revenue counter, industry selector, pricing dominance, case studies rebuild
- **Phase 2 full build** — competitor kill section, trust signals, demo upgrade, OG tags
- **Phase 1** — hero split layout with product image

## Active Priorities

1. **GET FIRST CUSTOMER** — Nothing else matters. Wallace should walk into Nashville businesses TODAY with walkin.html on his phone
2. **Call the 35 hot leads** — Every single one, today. Not email. Phone calls.
3. **Stripe still blocked** — Wallace is 16, needs parent/guardian. PayPal/Venmo workaround exists
4. **Case studies are fabricated** — Need to be replaced with real customer stories once first customer signs
5. **Pilot page testimonials** — Still have fake quotes, should be updated to match homepage founding member angle

## Audit Findings (This Session)

### Why 0 Customers Despite 35 Hot Leads:
1. No human follow-up — automation runs but nobody calls leads back
2. Fake social proof was destroying trust (now fixed)
3. Too many conversion paths was causing confusion (now fixed)

### Competitor Gaps:
1. Competitors have established trust (Smith.ai: 5K+ businesses, Ruby: 14K+, BBB ratings)
2. Competitors offer instant self-serve onboarding (Goodcall: 5-min setup)
3. Competitors have deep CRM integrations (Smith.ai: 30+ integrations)

## Known Blockers

1. **Stripe not connected** — can't take card payments. PayPal/Venmo workaround live
2. **GHL API unreachable from CI** — voice agent settings must be deployed from Mac
3. **Retell.ai blocked** — needs payment card for phone number ($2/mo)
4. **Meta Ads** — needs API token from developers.facebook.com
5. **reply-monitor** — has exit code 1, may need restart
6. **Gmail SMTP passwords** — plaintext in gmail-sender.py
7. **Cold caller dead** — Bland.ai cold calling hasn't run since Feb 24

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
- **Single conversion path**: ALL CTAs should go to `/pilot/`. Do NOT add book.html links.
- **No fake social proof**: Do NOT add fabricated testimonials, fake review badges, or invented customer names
