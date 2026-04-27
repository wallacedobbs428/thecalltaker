# 30-Day Customer Success Playbook

> Run this for every new customer. Each touchpoint is designed to build confidence, surface problems early, and lock in retention before billing starts.

---

## DAY 0 — Go Live

**Owner:** Wallace (manual) + onboarding-engine (automated)

| Task | How | Done? |
|------|-----|-------|
| Gideon configured and tested | 3 test calls, fix issues | [ ] |
| Phone forwarding active | Confirmed on call with customer | [ ] |
| Welcome SMS sent | Auto: onboarding-engine | [ ] |
| Welcome Email #1 sent | Auto: onboarding-engine | [ ] |
| legacy CRM tags applied | `new-customer`, `in-trial`, `[plan]-plan`, `[vertical]` | [ ] |
| legacy CRM task created | "Configure Gideon for [business]" | [ ] |
| ntfy alert fired | "NEW CUSTOMER" to urgent topic | [ ] |
| Day 7 + Day 30 calls booked | On Wallace's calendar | [ ] |

**Welcome Email #1 — "You're in, here's what happens next"**

Subject: Gideon is live — here's what to expect

Body:
> Hey [First Name],
>
> Gideon is officially answering your phones. Here's what you need to know:
>
> 1. **Test her yourself** — call your business number from a different phone. Try "I need a [service] appointment" and hear her handle it.
> 2. **Check your bookings** — every call she books shows up in [calendar tool]. You'll also get a text notification.
> 3. **Need anything?** — text me directly at (615) 653-9004. I respond in minutes, not days.
>
> I'll check in with you in a few days to make sure everything's dialed in.
>
> — Wallace

---

## DAY 2-3 — Quick Check-In

**Owner:** onboarding-engine (auto SMS) + Wallace (respond to replies)

**SMS to customer:**
> "Hey [first name], how are the calls going? Anything Gideon should handle differently? I can tweak her script in 5 minutes."

**What you're looking for:**
- Complaints about wrong bookings → fix routing rules
- "She sounds weird" → adjust greeting or voice
- "Nobody's called yet" → check forwarding is actually active
- No reply → good sign, follow up Day 7

**ntfy reminder to Wallace:** "Day 3 check-in: [customer name] — reply if they texted back"

---

## DAY 7 — Tuning Call

**Owner:** Wallace (15-min call) + onboarding-engine (auto SMS + ntfy)

**SMS to customer (auto):**
> "Hey [first name], this week Gideon handled [X] calls for [business]. Quick 15-min tuning call this week — when works?"

**Tuning call agenda (15 min):**
1. "How's it going overall?" (2 min — let them talk)
2. Review 3-5 call recordings together (5 min)
3. Identify script tweaks: greeting changes, FAQ additions, routing fixes (3 min)
4. Apply changes live while on the call (3 min)
5. "Anything else before we check in again at Day 30?" (2 min)

**First Wins Email — send after the tuning call:**

Subject: Your first week with Gideon — the numbers

Body:
> Hey [First Name],
>
> Here's what Gideon did for [Business Name] this week:
>
> - **[X] calls answered** (including [Y] after hours)
> - **[Z] appointments booked**
> - **Estimated revenue captured: $[amount]**
> - **Longest call: [duration]** — she handled it start to finish
>
> [One specific win — e.g., "Tuesday at 9:47 PM, Gideon booked a $600 emergency repair that would have gone to voicemail."]
>
> We tweaked [specific thing] on our tuning call today. She'll be even sharper this week.
>
> — Wallace

**ntfy to Wallace:** "Day 7 tuning due: [customer name] — book tuning call"

---

## DAY 10 — Pre-Trial-End Check-In

**Owner:** onboarding-engine (auto SMS + ntfy)

**SMS to customer:**
> "Hey [first name], your 14-day trial ends in 4 days. Billing starts [billing date] at $[amount]/mo. Want to do a quick call before then?"

**What you're watching for:**
- "Can I cancel?" → ask what's not working, try to fix it on the spot
- "Sounds good" → great, confirm payment method is set up
- No reply → follow up Day 12 with a direct text from Wallace
- Price objection → "Gideon caught [X] calls worth $[Y] this week alone. She pays for herself in one job."

**ntfy to Wallace:** "Trial ending in 4 days: [customer name] — confirm payment method"

**Day 12 manual fallback (if no Day 10 reply):**
> Text from Wallace: "Hey [first name], just checking — everything good with Gideon? Your trial wraps up [date]. Happy to hop on a 5-min call if you have any questions."

---

## DAY 14 — Trial Ends, Billing Starts

**Owner:** onboarding-engine (auto SMS + tags)

**SMS to customer:**
> "Hey [first name], your trial is done and Gideon is officially part of your team. First invoice goes out [billing date]. Any questions, I'm a text away."

**Tag changes:**
- Add: `trial-complete`, `paying-customer`
- Remove: `new-customer`, `in-trial`

**If payment method not set up:**
- Text: "Hey [first name], need to get your payment method locked in before [billing date]. Here's the link: [payment link]. Takes 60 seconds."
- Follow up in 48 hours if not completed

---

## DAY 21 — Tie to Money

**Owner:** Wallace (manual text)

Find ONE specific job Gideon caught that the customer would have missed. Pull it from legacy CRM call recordings or booking history.

**Text to customer:**
> "Hey [first name] — just pulled your logs. Tuesday at 8:47 PM, Gideon booked a [job type] for [caller name] at [address]. That's a $[amount] job that would've gone to voicemail. She's been doing that [X] times this week."

**Why this matters:** This is the single most powerful retention move. A specific dollar amount tied to a specific call they can verify. Makes the monthly fee feel like a bargain.

---

## DAY 30 — Value Review Call

**Owner:** Wallace (15-min call) + onboarding-engine (auto ntfy + email)

**ntfy to Wallace:** "30-day review due: [customer name] — run value review call"

**Value review call agenda (15 min):**
1. "How's the last month been?" (2 min)
2. Show the numbers: total calls, after-hours calls, bookings, estimated revenue (5 min)
3. "What's one thing Gideon could do better?" (3 min — take notes, fix it)
4. If on Starter: soft Pro upgrade float (3 min)
5. "Know anyone else who'd benefit from this?" — referral ask (2 min)

**Pro upgrade float (Starter customers only):**
> "So Gideon's been catching your after-hours calls. A lot of our clients find that the overflow during business hours is just as valuable — when you're on a job and can't answer, she picks up instead of voicemail. That's the Pro plan at $997/mo. Want to test it for a week?"

**Month 1 Report Email — send after the call:**

Subject: Your first month with Gideon — full report

Body:
> Hey [First Name],
>
> One month in. Here's what Gideon did for [Business Name]:
>
> - **[X] total calls answered**
> - **[Y] after-hours calls caught**
> - **[Z] appointments booked**
> - **Estimated revenue captured: $[amount]**
> - **Biggest single job: $[amount]** — [brief description]
>
> That's a [ROI]x return on your $[plan amount]/mo investment.
>
> Based on our call today, I've [updated X / added Y / tweaked Z].
>
> Here's to month 2. — Wallace

---

## ONGOING (Month 2+)

| Frequency | Action |
|-----------|--------|
| Monthly | Quick text check-in: "Everything smooth with Gideon?" |
| Monthly | Pull one specific win and text it to them (Day 21 style) |
| Quarterly | 15-min review call with updated numbers |
| Quarterly | Referral ask: "Know anyone who'd benefit?" |
| As needed | Script updates within 24 hours of request |
| As needed | Respond to any customer text within 2 hours |

---

## RED FLAGS — Escalate Immediately

| Signal | Action |
|--------|--------|
| Customer turns off forwarding | Text: "Noticed Gideon hasn't gotten calls — everything ok?" |
| 3+ days no calls (was getting calls) | Check forwarding, check carrier |
| "Cancel" or "refund" in any message | Call them within 1 hour. Fix or save. |
| Payment fails | Text payment link same day. Follow up 48hr. Pause at 7 days. |
| Negative review mentioning AI/robot | Call immediately. Offer script rewrite + comp month. |
