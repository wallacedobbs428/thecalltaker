# LOCAL OUTREACH AUDIT — Premature Purchase Asks

> **Date:** March 15, 2026
> **Rule:** Local leads (within 1 hour of Brentwood, TN) should NEVER be asked to buy, sign up, or start a trial before an in-person meeting.

## Files Updated (Local routing added)

### Python Engines (auto-detect local leads via `ops/local_detect.py`)

| Engine | File | Status |
|--------|------|--------|
| Blast Engine v2 | `ops/blast-engine-v2.py` | UPDATED — local leads get in-person CTA email |
| Hot Lead Converter | `ops/hot-lead-converter.py` | UPDATED — all 5 touches have local variants |
| Outbound SMS Engine | `ops/outbound-sms-engine.py` | UPDATED — all 3 touches have local variants |
| Demo Follow-Up SMS | `ops/demo-followup-sms.py` | UPDATED — local leads get in-person CTA |

### Sales Templates (local sections added)

| Template | File | Status |
|----------|------|--------|
| Cold Email Sequence | `sales/cold-email-sequence.md` | UPDATED — 3 local email variants added |
| Cold Call Script | `sales/cold-call-script.md` | UPDATED — local call script + rules added |
| Voicemail Drops | `sales/voicemail-drop-scripts.md` | UPDATED — 3 local voicemail variants added |
| SMS Cold Outreach | `sales/sms-cold-outreach.md` | UPDATED — 3 local SMS + 2 follow-ups added |

## Files NOT Yet Updated (Manual review needed)

These files contain outreach copy that may ask local leads to buy/signup before in-person. They need manual review because they either run on a separate ops machine or are used manually by Wallace:

| File | Issue | Priority |
|------|-------|----------|
| `ops/storm-chaser-v2.py` | Weather-triggered emails push pilot signup for ALL leads | LOW — weather triggers are mostly national |
| `ops/payment-reminder-engine.py` | Post-demo conversion reminders push $97/mo | MEDIUM — local demo leads should get in-person follow-up instead |
| `ops/facebook-lead-webhook.py` | Auto-responder pushes demo line + pilot | LOW — Facebook ads are mostly national |
| `sales/sms-follow-up-sequences.md` | Post-demo follow-ups push pilot signup | MEDIUM — needs local variant section |
| `sales/linkedin-outreach.md` | DM sequences push demo booking link | LOW — LinkedIn is mostly national |
| `sales/cold-dm-scripts.md` | Instagram DMs push demo line + pricing | LOW — DMs are mostly national |
| `sales/saturday-blitz-outreach.md` | Weekend blitz pushes pilot/pricing | HIGH — Saturday blitz is local-heavy |
| `onboarding/referral-request-email.md` | Referral asks go to ALL contacts | LOW — referrals are post-sale |
| `agents/agent-02-outbound-hunter/email-sequences/` | City-specific cold emails push pilot | MEDIUM — some cities are local |
| `agents/agent-02-outbound-hunter/sms-sequences/` | Re-blast templates push pilot | MEDIUM — some contacts are local |

## Local Detection Logic

**File:** `ops/local_detect.py`

**Detects local leads by:**
1. Phone area code: 615, 629 (Nashville metro)
2. Zip code prefix: 370xx - 381xx (Middle Tennessee)
3. City name: 50+ cities within ~1 hour of Brentwood
4. GHL tags: "nashville", "middle-tn", "local-lead", "local"

**Usage in any engine:**
```python
from local_detect import is_local, get_lead_city

if is_local(contact):
    city = get_lead_city(contact)
    # Use in-person appointment CTA
else:
    # Use Zoom demo / free pilot CTA
```

## Key Rules

1. **Local first touch = "Can I stop by for 10 minutes?"** — never "Book a demo" or "Start your pilot"
2. **Never mention pricing** to a local lead before the in-person meeting
3. **Never send a website link** as the CTA for local leads — the CTA is always "reply with a time"
4. **Always reference being local:** "I'm right here in Brentwood," "I'm in [City] every day"
5. **Trust mechanism = the in-person visit**, not social proof or demo line
6. **After the in-person meeting:** Then pitch the pilot, pricing, etc.
