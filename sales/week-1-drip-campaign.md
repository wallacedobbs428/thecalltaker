# Week 1 SMS Drip Campaign — The Call Taker

**Target:** 45 HVAC leads via GHL API
**Schedule:** Monday AM through Friday PM
**Goal:** Book demos + drive calls to (615) 784-5747

---

## MONDAY AM — "Tomorrow Is Here"

**Send time:** 8:15 AM
**Angle:** Your phones are about to ring. Is anyone answering?

```
Hey it's Wallace. Monday morning — your phones are ringing right now. How many went to voicemail before 9am? That's money walking to your competitor. Call my AI receptionist and hear what your customers COULD hear: (615) 784-5747. -Wallace
```
*(293 characters)*

---

## MONDAY PM — Social Proof / FOMO

**Send time:** 4:30 PM
**Angle:** Other HVAC companies are already moving on this.

```
I set up 3 HVAC companies this weekend with AI receptionists. All 3 had the same problem — calls going to voicemail during jobs. One owner told me he lost a $4800 install last Tuesday. Fixable overnight. Hear the demo: (615) 784-5747 -Wallace
```
*(246 characters)*

---

## TUESDAY — The Math Angle

**Send time:** 10:00 AM
**Angle:** Break down the exact dollars being lost.

```
Quick math: if you miss 3 calls a day and 1 would've been a job worth $1200, that's $6000/week walking away. The Call Taker answers every single one for $297/mo. That's a 20x return. Don't believe me — call it yourself: (615) 784-5747 -Wallace
```
*(247 characters)*

---

## WEDNESDAY — Free Audit Offer

**Send time:** 11:00 AM
**Angle:** I'll call your shop tonight and show you what your customers hear.

```
I want to try something. Tonight at 6pm I'll call your shop like a customer needing emergency repair. I'll screen-record what happens. No cost, no pitch — just showing you what your callers experience. Want me to? Reply YES. -Wallace
```
*(234 characters)*

**Follow-up if they reply YES (send immediately):**

```
Perfect. After I call your shop I'll also call my demo line so you can hear the difference side by side. You can try it now too: (615) 784-5747. Talk tonight. -Wallace
```
*(158 characters)*

**Follow-up if NO reply by 5 PM (auto-send):**

```
No worries either way. But if you're curious what a call SHOULD sound like when a customer dials in after hours, give this a ring: (615) 784-5747. Night and day difference. -Wallace
```
*(173 characters)*

---

## THURSDAY — Urgency / Scarcity

**Send time:** 9:30 AM
**Angle:** Limited setup slots remaining this month.

```
Being straight with you — I've got 5 setup slots left this month. Each one takes me a couple hours to customize. After that I'm booked into next month. If you've been thinking about it, now's the time. Hear it first: (615) 784-5747 -Wallace
```
*(242 characters)*

---

## FRIDAY — Weekend Preview

**Send time:** 12:00 PM
**Angle:** Another weekend of missed calls is coming.

```
Another weekend starts tomorrow. AC goes out Saturday afternoon, homeowner calls 3 companies — whoever answers first gets the job. Will that be you or your voicemail? Hear what answering every call sounds like: (615) 784-5747 -Wallace
```
*(235 characters)*

---

## GHL API IMPLEMENTATION NOTES

### Automation Workflow
1. **Contact list:** Tag all 45 leads as `week1-drip`
2. **Trigger:** Date-based workflow starting Monday
3. **Sending number:** Wallace's personal line or dedicated outreach number
4. **Opt-out:** GHL auto-handles STOP replies
5. **Reply handling:** Any reply triggers notification to Wallace for personal follow-up

### Tracking Fields (Custom Fields in GHL)
- `drip_day` — Which message they're on (1-6)
- `drip_replied` — Yes/No
- `drip_called_demo` — Track if they called (615) 784-5747
- `audit_requested` — Wednesday YES replies

### Response Protocol
- **Any reply at all** — Wallace calls them within 10 minutes
- **"YES" on Wednesday** — Wallace calls their shop at 6 PM, records it, sends Loom
- **"STOP" or negative** — Remove from sequence, tag as `drip-declined`
- **No reply all week** — Move to Week 2 sequence (different angles)

### Key Metrics to Track
| Metric | Target |
|--------|--------|
| Reply rate | 15%+ (7 of 45) |
| Demo line calls | 10+ |
| Audit requests (Wed) | 5+ |
| Booked demos | 3-5 |
| Closes | 1-2 |
