## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-16 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. $97/$297/$497/mo plans. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Co-founder: Mills (strategy, GitHub). William (Wallace's brother) closes demos on Zoom.

## Architecture

- **This repo** (`~/Desktop/thecalltaker/` or `/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, agent configs, sales assets, outreach ops scripts
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo). Voice ID: `lxYfHSkYm1EzQzGhdbfc` (deep variant, v9)
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)

## Current Branch & State

- **Branch:** `claude/thecalltaker-mobile-centering-yA6JR`
- **Working tree clean** — no staged or unstaged changes
- **No upstream set** for this branch
- **Master branch** at same point (2026-03-15)

## Current Task (March 16, 2026)

Auditing `website/index.html` for mobile horizontal overflow issues. Full CSS/HTML analysis across inline styles + 4 external CSS files (below-fold.css, demo-console.css, premium.css, ui-dark.css).

## Homepage Structure

The homepage (`website/index.html`) is 3,126 lines with:
- Inline CSS (lines 63-683): Core layout, hero, phone mockup, nav, mobile menu
- External CSS: below-fold.css (minified, all below-hero sections), demo-console.css (shared demo player), premium.css (premium visual layer), ui-dark.css (dark theme shared UI)
- Dark theme (green accent `#00dc82` on `#0a0a0a` background)
- Phone mockup in hero (280px device, floating bubbles)
- Demo console sections (shared component, max-width 560px / 640px large)
- AI Call Flow visualizer (6-node horizontal track)
- Missed Call Wall (grid with inbox + stats)
- Revenue simulators (2 of them)
- Testimonial carousel (infinite scroll)
- Pricing grid (3 columns)
- Industry selector with pills
- Mobile sticky call bar
- Cursor effects (desktop only, tiered)

## Key CSS Files

| File | Purpose |
|------|---------|
| Inline in index.html (63-683) | Hero, nav, phone mockup, hero responsive |
| `/shared/below-fold.css` | All sections below hero (problem, features, demo, pricing, FAQ, footer, etc.) |
| `/shared/demo-console.css` | Demo console player component |
| `/shared/premium.css` | Premium visual layer (edge-lit, shadows, gradients, motion) |
| `/shared/ui-dark.css` | Shared dark-theme header, mobile nav, call bar |

## Active Priorities

- **Mobile overflow audit** — identify all CSS causing horizontal scroll on mobile
- **Revenue**: Get to first paid customer. $20K MRR goal
- **Stripe**: NOT connected (Wallace is 16). PayPal/Venmo workaround live

## Known Blockers

1. Stripe not connected — PayPal/Venmo workaround live
2. GHL API unreachable from CI — deploy from Mac only
3. Retell.ai blocked — needs payment card
