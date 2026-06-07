# Try-Live Safety Lockdown QA - 2026-06-07

## Finding

`website/try-live.html` was still reachable publicly and contained live provider-call behavior. Before the fix, the page could collect form values in the browser and attempt to trigger a live call.

Secret-safe note: `website/try-live.html` previously contained a possible secret present. The value is not printed here and was removed from the public HTML.

## What Changed

| Area | Result |
| --- | --- |
| Public metadata | Changed to `noindex,nofollow` and paused-demo messaging. |
| Hero copy | Changed from active live-call promise to clear paused-demo state. |
| Form submit | Replaced provider calls with a local-only paused message. |
| Lead API call | Removed from the try-live submit flow. |
| Bland call request | Removed from the try-live submit flow. |
| Provider credential | Removed from public HTML. |
| Google tag on try-live | Removed from the paused page to avoid outside-service contact from that flow. |
| Meta/Signals Gateway tracking on try-live | Removed from the paused page to avoid pageview/lead tracking from that paused flow. |
| Shared site script on try-live | Removed so the paused page does not inject popups, tracking helpers, or shared lead behavior. |
| Bottom CTA | Replaced auto-call CTA with setup-form CTA. |
| Redirect helper | `website/try.html` now noindexes and points to `/try-live.html`. |
| Sitemap | Removed `try-live.html` listing. |

## Verification Markers

`tests/website-provider-safety.test.js` now fails if `website/try-live.html` contains:

- Bland API endpoint markers
- Authorization/header credential markers
- live-call button/status copy
- lead/provider `fetch`
- Google Tag Manager script
- Meta/Signals tracking scripts
- shared `script.js` include
- sitemap listing for `try-live.html`

## Current Status

The public page can still be visited from old links, but it cannot trigger a live demo call from the browser after this patch. Visitors see that live demo calling is temporarily disabled and are pointed to the setup form or direct demo line instead.

## Remaining Recommendation

Keep live demo calling paused until Wallace explicitly approves a provider-safe backend flow with no browser-exposed credentials and with rate limits, logging, and manual approval gates.
