## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

# Primer — The Call Taker

> Last updated: 2026-03-18 | Rewrite this file at the start of every session.

## What This Is

AI Receptionist SaaS for service businesses. Pricing: $97 After-Hours / $497 Starter / $997 Pro. 14-day free pilot. Demo line: (615) 784-5747. Built by Wallace Dobbs (16yo founder, @moneymaker99). Co-founder: Mills (strategy, GitHub). William (Wallace's brother) closes demos on Zoom.

## Architecture

- **This repo** (`/home/user/thecalltaker/`): Website (GitHub Pages), lead tools, dashboard, sales assets
- **Ops repo** (`~/thecalltaker-ops/`): 4 AI engines (Max, Ben, Sam, Donny), 40+ ops scripts, state files, logs — all on launchd on a Mac
- **Voice AI**: GHL Voice AI agent (Jessica, universal demo)
- **CRM**: GoHighLevel (GHL). All contacts, conversations, pipelines
- **Notifications**: ntfy.sh (5 topics: urgent, sales, system, activity, william)
- **Deployment**: GitHub Pages via GitHub Actions. Only `website/` gets deployed.

## Current Branch & State

- **Branch:** `claude/fix-pricing-rebuild-site-7plmf`
- **Working tree:** Clean (no staged or unstaged changes)
- **No upstream set** — will need `git push -u origin` on first push

## Recent Work (March 17, 2026)

Latest commits show a burst of pricing/payment work:
1. **Founding customer pricing page** — 4-tier decoy layout + payment workflow (`b6c7461`)
2. **PayPal fixes** — Mobile redirect fix, abandonment recovery with card trust lines + fat buttons + thank-you page (`b36bd41`, `2439830`)
3. **Urgency bar** — 7 spots counter + Friday deadline + auto-waitlist (`f898b29`)
4. **Google Ads** — Dynamic conversion values + reassurance button copy (`b6dd19f`)
5. **Loom video showcase** — Page for escalation sequence (`63b1a13`)
6. **FB Lead Ad** — Thank-you page with tap-to-call CTA (`69b4452`)
7. **Homepage rewrites** — 3 weakest sections rewritten + Jessica demo worker added (`a773a7f`)
8. **Pricing sweep (March 15)** — $97 After-Hours / $497 Starter / $997 Pro across full site (`23d6f2a`)
9. **Demo showcase audit** — Fixed old orange design (`4b4e4bb`)

## Website Structure (128+ pages)

- `website/index.html` — homepage (glassmorphism nav, cursor effects, phone mockup, industry selector)
- `website/signup.html` — purchase flow
- `website/calculator.html` — ROI calculator
- `website/book.html` — demo booking (GHL calendar)
- `website/checkout.html` — plan checkout
- `website/industries/` — 13 industry pages
- `website/blog/` — 39+ blog articles (3 per industry)
- `website/case-studies/` — 13 case studies
- `website/ai-answering-service/` — 13 SEO landing pages
- `website/try-funnel/` — $97 funnel pages
- `website/agency-program/` — agency partner pages
- `website/toolkit/` — sales toolkit (password: tctoolkit)
- `website/demo/` — shareable demo pages with `?industry=` param

## Active Priorities

- **Revenue**: Get to first paid customer. $20K MRR goal.
- **Pricing**: New tier structure ($97/$497/$997) deployed across site. Founding customer pricing page live.
- **PayPal**: Workaround live (Stripe blocked — Wallace is 16). Mobile redirect + abandonment fixes deployed.
- **Urgency/scarcity**: 7 spots counter, Friday deadlines, auto-waitlist mechanisms in place.
- **Google Ads + FB Leads**: Dynamic conversion values + thank-you pages deployed.

## Known Blockers

1. Stripe not connected — PayPal/Venmo workaround live
2. GHL API unreachable from CI — deploy from Mac only
3. Retell.ai blocked — needs payment card
4. Bland.ai balance — must be funded before cold caller goes live
