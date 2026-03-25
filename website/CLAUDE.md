# The Call Taker — Website Repo (thecalltaker)

## Who I am
Wallace Dobbs, 16, sole owner. This is the GitHub Pages site repo.
Alias to open this repo: `site` (cd ~/Desktop/thecalltaker/website)

## Stack
- GitHub Pages — static HTML only, no build step, no npm
- 93 HTML pages, plain HTML/CSS/JS
- Font: Inter (global)
- Colors: Green/black (homepage). 37 industry/blog pages still have OLD blue/red — do not match those, update them to green/black when touched.
- GSAP 3.12.5 loaded via CDN for hologram animations
- Deploy: git push origin main (auto-deploys to thecalltaker.com)

## Key files
- index.html — homepage, hologram lives here
- go.html — FB ad landing page (single offer, single form, $264 price)
- pay.html — pricing page (3 tiers, $97/$497/$497)
- demo-live.html — ElevenLabs Flash v2.5 via Cloudflare Worker live demo

## AI Character
Name is **GIDEON** (not Jessica — update any reference you see)

## Hologram rules
- ONLY #hologram3d rotates
- .glass-hud panels are siblings inside .holo-wrap — they NEVER rotate
- Backup tag: website-stable-march18

## Pricing (site-displayed)
- $97/mo After-Hours, $497/mo Starter, $997/mo Pro
- Founding rate: $264/mo (used in ads and go.html)
- PayPal payment page: thecalltaker.com/pay
- Stripe is NOT connected (under appeal)

## Humanize rules
- No dashes in any outward-facing copy
- No AI-sounding language
- Text like a real person

## DO NOT
- Add npm, package.json, or any build tooling
- Touch blue/red pages unless converting them to green/black
- Use "Jessica" anywhere — always GIDEON
