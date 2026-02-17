# Call Taker Command Center — Agent Memory
# Last updated: 2026-02-17

## Email Outreach — What's Been Built

### Instantly.ai Sequences (3 complete, 7 emails each, 14-day cadence)
- File: `/Users/moneymaker99/Desktop/wallace-hvac/sales/instantly-sequences-all-three.md`
- Sequence 1: Missed Call Angle (default for cold/unknown leads)
- Sequence 2: After-Hours Angle (use for leads tested with voicemail, heating markets, Nov-Mar)
- Sequence 3: Growth Angle (use for bigger companies, 5+ trucks, growing operations)
- All emails: under 100 words, {{firstName}} + {{companyName}} merge tags, Reply STOP in every email
- Demo line appears in email 3 of every sequence (not email 1 — earn it first)
- Price ($497/mo) appears in email 4+ only — never email 1 or 2

### Existing Shorter Sequences (already in /sales/)
- `cold-email-sequence.md` — original 3-email sequence
- `cold-email-sequence-extended.md` — emails 4-7 add-ons
- `instantly-sequences-all-three.md` — NEW: full 7-email angle-based sequences (Feb 17)

## Sales Rules (from playbook)
- Never lead with price. Order: pain → amplify → demo line → THEN price
- If they ask price first: "$497 = less than one service call" then redirect to demo
- Demo line: (615) 784-5747 — push this before any booking link
- Book demo at thecalltaker.com/demo.html

## GHL Key References
- API Key: pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35
- Location ID: tQb9YmrGDrdVUJYPKrsY
- Voice AI Agent ID: 695947c64b9ed67d8f1077ad
- Voice Jerry ID: XA2bIQ92TabjGbpO2xRr
- Demo Calendar ID: h4IlzccZ1m3JprEQqpMJ
- SMS phone: +16156539004 | Voice AI demo: +16157845747

## Sales Tools Built

### Secret Shopper Report Generator (Feb 17, 2026)
- File: `/Users/moneymaker99/Desktop/wallace-hvac/shopper-report.html`
- Internal tool only — blocked from search engines via robots.txt (noindex meta + robots.txt Disallow)
- Wallace fills in form after a test call → JS generates a print-ready PDF-style report
- Revenue math: missedCalls * 0.67 (lost callers) * $350 = monthly loss; *12 = annual
- Grade colors: A=green, B=light-green, C=amber, D=orange, F=red
- Comparison table rows auto-adapt based on what Wallace selected (voicemail/person/answering svc)
- Design: dark navy form on page, clean white report for printing
- After-hours row hidden in report if not tested

## Current Blockers (as of Feb 17)
- A2P 10DLC SMS campaign: IN PROGRESS — all SMS outreach failing until approved
- SSL cert on thecalltaker.com: pending GitHub Pages issuance
- Stripe: not connected
- Voice agent: intermittent issues (random pauses, topic changes) — needs retesting
