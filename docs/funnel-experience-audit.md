# Funnel Experience Audit

Date: 2026-05-15

## Objective

The public funnel should feel like one premium operational system from homepage to
checkout. The emotional progression is:

1. Homepage: missed-call revenue is leaking.
2. Services: Gideon turns calls into operational handoffs.
3. Demo: hear the call flow and understand the setup.
4. Pricing: choose the operating layer.
5. Checkout: confirm the selected plan and Square trial terms.

## Scoring System

Scores use a 1-10 internal scale:

- Premium feel
- Emotional persuasion
- Consistency
- Operational realism
- Buying pressure
- Trust
- Cinematic quality

## Page Scores After This Pass

| Page | Premium | Emotional | Consistency | Realism | Buying Pressure | Trust | Cinematic |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Homepage | 8 | 8 | 7 | 8 | 7 | 7 | 9 |
| Services | 7 | 7 | 7 | 8 | 6 | 7 | 7 |
| Pricing | 8 | 7 | 8 | 8 | 7 | 8 | 8 |
| Demo | 7 | 7 | 7 | 8 | 6 | 8 | 7 |
| Checkout | 8 | 7 | 8 | 9 | 7 | 9 | 8 |

## Weakest Transition Points

- Homepage to services: services previously shifted from cinematic revenue
  recovery into generic feature/testimonial language. The page now frames
  services as operational handoff scenarios rather than generic AI answering.
- Services to pricing: pricing previously explained tiers but did not visualize
  what each tier changes operationally. Pricing now includes a plan visualization
  layer before the cards.
- Demo to checkout: demo previously felt like a separate lead-gen tool. It now
  explains that the demo proves voice flow, while checkout begins operational
  setup.
- Pricing to checkout: Square trial terms are now explicit before checkout and
  on the Square-hosted link title.

## Visual Direction System

Use restrained cinematic operations:

- Lighting: dark graphite base, controlled green signal light, limited amber for
  premium operational notes.
- Gradients: subtle radial glow only; no decorative orbs or generic SaaS blobs.
- Spacing: wide vertical pacing, fewer dense card stacks, no nested-card feeling.
- Typography: large compressed hero type, small operational kickers, restrained
  body copy.
- CTA sizing: confident pill CTAs, not oversized desperation buttons.
- Cards: low-contrast panels with 18-28px radius, fine borders, and depth from
  shadow rather than bright outlines.
- Images: phone/call-operation visuals, service-business reality, dashboards only
  when real and readable.

## Higgsfield Visual Recommendations

Do not generate fake dashboards, readable phone screens, robots, hologram-heavy
AI art, exaggerated acting, or fake customer proof.

### After-Hours Capture

Scene: dark service-business office after close, phone ringing on a counter, work
van or tools visible, calm cinematic lighting. The feeling is relief: the call is
not disappearing into voicemail.

Use for: pricing plan visual, services after-hours section.

### Revenue Recovery System

Scene: owner or dispatcher reviewing clean call notes on a real desk setup while
missed-call chaos becomes organized follow-up. Avoid readable UI. Show folders,
phone, notepad, and controlled motion.

Use for: homepage proof section, pricing featured plan, demo-to-checkout bridge.

### Operational Infrastructure

Scene: premium service operator command desk, call notes, dispatch board,
workflow map, and calm after-hours control. It should feel like an operating room
for calls, not a sci-fi control center.

Use for: checkout right rail, pricing premium card, future pilot/setup page.

## Claim-Safety Rules

- Do not imply every call is answered unless scoped routing makes that true.
- Do not claim booked revenue, booked jobs, or exact ROI without documented proof.
- Do not use fake testimonials.
- Do not imply provider routing, SMS/email workflows, direct booking, CRM sync, or
  CTOS visibility is active from checkout alone.
- Checkout starts setup; Wallace reviews setup before Gideon goes live.

## Remaining Weak Points

- Homepage still has the strongest cinematic identity; services and demo are now
  closer, but they still carry legacy structure beneath the new layer.
- Pricing now has plan visuals, but final generated visuals should replace the
  current image placeholders.
- Services has safer scenarios, but a future pass should simplify the full page
  length and remove old decorative diamond patterns entirely.
- Demo still has a functional form-first shape; it needs a future visual polish
  pass if paid traffic starts landing there directly.

## Deployment Gate

Before deploy:

- Run website trial funnel regression.
- Run hero regression.
- Check old phone numbers and old `/start`/`book.html` funnel paths.
- Scan for fake testimonial claims.
- Manually review mobile screenshots for services, pricing, demo, and checkout.
