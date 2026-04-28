# NTFY Notification Policy

This is the current rule set for The Call Taker notification volume.

## Keep urgent phone alerts

- Confirmed pilot signups saved by the live intake API
- Confirmed self-serve signup requests that need a fast callback
- Immediate callback requests such as `go-page-callback`
- First-dollar / closed-deal alerts from explicit operator actions
- Real system-failure alerts from monitors and critical CTOS owner alerts

## Keep, but route to lower-noise sales topics

- Industry-page lead submissions
- Referral submissions
- Partner applications
- Calculator submissions

These should notify only after the backend confirms a saved lead.

## Remove from phone alerts

- Browser-side pageview/activity beacons
- Scroll-depth beacons
- Exit-intent beacons
- Idle-time beacons
- Checkout-click alerts
- Newsletter-signup alerts
- Popup lead-magnet alerts pretending to be pilot signups
- Any frontend success alert that can fire before the API confirms save

## Architecture rule

- Public pages do not post directly to `ntfy` for lead notifications.
- The live intake API decides whether a saved lead deserves:
  - urgent topic
  - sales topic
  - no phone alert

## Current intent

- Fewer notifications
- Higher trust
- Every urgent alert should be something Wallace can act on immediately
