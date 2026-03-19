# New Customer Onboarding Checklist

> Run this on every new customer. Print it out or keep it open during the close call.
> Goal: Jessica live on their phones before you hang up.

---

## ON THE CALL (while they're excited)

### 1. Confirm the Deal
- [ ] Plan: Starter ($497/mo) or Pro ($997/mo)
- [ ] Trial: 14 days free, billing starts Day 15
- [ ] Setup fee: waived (founding customer)
- [ ] Go-live goal: "Jessica is answering your phones tonight"

### 2. Collect Business Info
- [ ] Business name (exactly as it should appear on calls)
- [ ] Main phone number(s) to cover
- [ ] Business hours (open/close, days of week)
- [ ] After-hours rules (voicemail? emergency dispatch? always book?)
- [ ] Service area (cities, zip codes, or mile radius)
- [ ] Services offered (list the job types Jessica should book)
- [ ] Emergency vs. non-emergency rules ("burst pipe = dispatch now, dripping faucet = next day")
- [ ] Booking destination: Google Calendar / Housecall Pro / Jobber / ServiceTitan / other: ___

### 3. Send Links While on the Call
- [ ] Text them the payment link: "Sending you a quick link to lock in the trial — no charge for 14 days"
- [ ] Text them the service agreement link (or PDF): "Just the standard agreement — month to month, cancel anytime"
- [ ] Confirm they received both texts before moving on

### 4. Set Up Phone Forwarding LIVE
Walk them through it while you're on the phone:

**Option A — After-hours only (recommended for Starter)**
- iPhone: Settings → Phone → Call Forwarding → ON → enter Jessica's number
- Android: Phone app → Settings → Call Forwarding → When unanswered → enter Jessica's number
- "Turn this on when you leave the office, off when you open"

**Option B — Full 24/7 forwarding (Pro plan)**
- Call carrier: "Forward all calls from [business number] to [Jessica number]"
- Or use GHL's built-in number with porting

**Option C — Conditional (overflow)**
- Forward on busy / no answer only (carrier-level setting)
- Best for businesses that want to answer during hours but catch overflow

- [ ] Test the forward: call their business number, confirm Jessica answers
- [ ] If forwarding fails, troubleshoot carrier settings or schedule follow-up

### 5. Book Future Calls
- [ ] Day 7 tuning call: "I'll call you [day] at [time] to review how Jessica's doing — 15 minutes"
- [ ] Day 30 value review: "And one more at the 30-day mark to show you the full report"
- [ ] Add both to YOUR calendar with reminders

### 6. End the Call
- [ ] Restate: "So Jessica goes live tonight. I'm doing 3 test calls in the next hour. You'll get a text when she's ready. Day 7 we tune, Day 30 we review. Sound right?"
- [ ] "Text me anytime — I respond in minutes, not days."

---

## AFTER THE CALL (same day)

### 7. Configure Jessica in GHL
- [ ] Create/update contact in GHL with tags: `new-customer`, `in-trial`, `[plan]-plan`, `[vertical]`
- [ ] Set up Jessica's greeting: "Thanks for calling [Business Name], this is Jessica, how can I help you?"
- [ ] Configure FAQ script (top 5 questions for their vertical)
- [ ] Set routing rules: service area, job types, hours, emergency dispatch rules
- [ ] Connect booking integration (Google Calendar / Housecall Pro / Jobber / etc.)
- [ ] Set call recording ON (with consent notice in greeting)

### 8. Run Test Calls
- [ ] Test call #1: Basic booking — "I need a [service] appointment"
- [ ] Test call #2: After-hours scenario — does she follow the right rules?
- [ ] Test call #3: Edge case — out of service area, or service not offered
- [ ] Fix anything that breaks. Re-test.

### 9. Go Live
- [ ] Turn on Phase 1: after-hours or overflow only (unless Pro doing full 24/7)
- [ ] Confirm forwarding is active on their end
- [ ] Send Welcome Email #1 (auto-sent by onboarding-engine if tagged `new-customer`)
- [ ] Send ntfy confirmation: "LIVE: [business name] — Jessica active on [phone number]"

### 10. Document
- [ ] Log in `ops/call-tracker.csv`: outcome = Trial Started
- [ ] Note in GHL contact: plan, vertical, forwarding type, booking tool, any special rules
- [ ] Add to `ops/onboarding-engine.py` tracking (automatic via `new-customer` tag)

---

## QUICK REFERENCE

| Item | Where |
|------|-------|
| Demo line | (615) 784-5747 |
| Payment link | [Square/PayPal link — see payment-options.md] |
| Service agreement | docs/founding-customer-agreement.md |
| Onboarding engine | ops/onboarding-engine.py |
| 30-day playbook | docs/30-day-success-playbook.md |
| Wallace's number | (615) 653-9004 |
