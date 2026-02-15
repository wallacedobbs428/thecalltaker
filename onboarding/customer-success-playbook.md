# The Call Taker — Customer Success Playbook

**The system that keeps clients happy, eliminates churn, and turns every HVAC company into a referral machine.**

**Owner:** Wallace Dobbs
**Last Updated:** February 2026

---

> This playbook is the difference between a one-month subscription and a lifetime customer. Every client who stays 12 months is worth $3,564 (Starter) or $5,964 (Professional). Every client who cancels after month one cost you time, setup labor, and reputation. Retention is the entire game.

---

## Table of Contents

1. [The First 48 Hours — Onboarding Checklist](#1-the-first-48-hours--onboarding-checklist)
2. [The First 30 Days — Weekly Check-In Schedule](#2-the-first-30-days--weekly-check-in-schedule)
3. [Monthly Performance Report Template](#3-monthly-performance-report-template)
4. [Churn Prevention — Red Flags and Save Plays](#4-churn-prevention--red-flags-and-save-plays)
5. [Referral Generation System](#5-referral-generation-system)
6. [Upsell Strategy — Starter to Professional](#6-upsell-strategy--starter-to-professional)

---

## 1. The First 48 Hours — Onboarding Checklist

The first 48 hours determine whether a client feels confident or anxious. Speed, communication, and a flawless first impression are everything. The client should never wonder "what's happening with my account?" — you tell them before they have to ask.

---

### Hour 0-1: Payment Confirmed — Immediate Actions

**Automated (GHL Workflow):**
- [ ] Payment processed and confirmed via Stripe
- [ ] Welcome Email #1 sent: "Welcome to The Call Taker — here's what happens next"
- [ ] Client added to GHL as new contact with tag `active-client`
- [ ] Client added to GHL pipeline: "Onboarding" > Stage: "New Signup"
- [ ] Internal notification sent to Wallace: "New client signed up: [Business Name]"

**Manual — Within 60 Minutes of Signup:**
- [ ] Review the completed intake form for completeness
- [ ] Flag any missing fields and prepare follow-up questions
- [ ] Add client to internal tracking spreadsheet

---

### Hour 1-2: The Welcome Call

**Purpose:** Make the client feel like they made the right decision. Collect any missing info. Set clear expectations.

**Welcome Call Script:**

> "Hey [First Name], this is Wallace with The Call Taker. I just wanted to call you personally to say welcome aboard — we are fired up to be working with [Company Name].
>
> I have your intake form right here and everything looks great. I just want to confirm a few things so we can get your AI receptionist built exactly the way you want it.
>
> **[Confirm the following — ask only if missing or unclear from the intake form:]**
>
> 1. Your main business number that we will be answering — is that [number]?
> 2. Do you want us answering all calls, just after-hours, or overflow only?
> 3. Walk me through what happens right now when a customer calls and nobody picks up.
> 4. What is your service call fee or diagnostic fee? [This is what the AI will quote.]
> 5. Do you offer free estimates? For what — replacements only, or everything?
> 6. Who is your on-call tech for emergencies, and what counts as an emergency for you?
> 7. What calendar system are you on — Google Calendar, Jobber, ServiceTitan, Housecall Pro?
> 8. How do you want to be notified — text, email, or both?
> 9. Is there anything you absolutely do NOT want the AI to say or promise?
> 10. Any current promotions or seasonal specials you are running right now?
>
> **[After collecting info:]**
>
> Perfect. Here is exactly what happens next. My team is going to build out your AI receptionist today. We will configure your greeting, your services, your scheduling rules, your emergency protocol — the whole thing. Tomorrow, I am going to have you call your own business number and test it. You will talk to the AI, pretend you are a customer, and make sure everything sounds right. If you want anything tweaked, we fix it on the spot. Once you give us the thumbs up, we flip it live and every call to your business gets answered from that point forward.
>
> Any questions for me right now?
>
> Alright [First Name], you are going to love this. I will be in touch tomorrow for the test call. If you need anything in the meantime, you have my cell."

**After the call:**
- [ ] Document all info collected
- [ ] Update GHL contact record with any new details
- [ ] Note client's communication preference (text vs. call vs. email)
- [ ] Note client's personality and tone preference for future interactions

---

### Hours 2-12: Build and Configure

- [ ] Configure AI receptionist with all business information:
  - Custom greeting script using company name
  - Services offered with correct terminology
  - Business hours and after-hours handling rules
  - Service area (cities, counties, zip codes)
  - Pricing responses (service call fee, estimate policy)
  - Emergency protocol and on-call technician contact info
  - Restricted phrases — things the AI must never say
  - Current promotions or seasonal offers
- [ ] Set AI receptionist tone/personality per client preference
- [ ] Program FAQ answers from intake form responses
- [ ] Set up call forwarding instructions for client's carrier
- [ ] Connect to client's calendar system
- [ ] Configure appointment types with correct durations
- [ ] Set scheduling rules (same-day, next-day, advance window, buffer time)
- [ ] Block restricted times per client instructions
- [ ] Configure text notifications for owner and any additional recipients
- [ ] Configure email notifications if requested
- [ ] Set notification triggers per client preferences
- [ ] Set up appointment confirmation text (sent to customer after booking)
- [ ] Set up appointment reminder text (day before / morning of)

---

### Hours 12-24: Internal QA Testing

**Run all four test calls before the client ever touches the system:**

- [ ] **Test Call #1 — Standard Service Call:** Call as a homeowner needing AC repair. Verify greeting, information capture, and appointment booking.
- [ ] **Test Call #2 — Emergency Scenario:** Call as a homeowner with no heat / gas smell. Verify emergency protocol triggers correctly and on-call tech gets notified.
- [ ] **Test Call #3 — Common Questions:** Call asking about pricing, service area, hours, financing, and brands serviced. Verify AI gives correct answers for every one.
- [ ] **Test Call #4 — After-Hours Call:** Call outside business hours. Verify after-hours handling works correctly (booking, message, or emergency routing as configured).

**After testing:**
- [ ] Verify all test notifications were received by the right people
- [ ] Verify test appointment appeared on client's calendar
- [ ] Document any issues found
- [ ] Fix all issues before proceeding
- [ ] Send client a text: "Hey [First Name], your AI receptionist is built and looking great. We have been testing it all day. Ready for you to give it a try tomorrow — I will reach out in the morning to set that up."

---

### Hours 24-36: Client Test Call

**Text or call the client to schedule the test:**

> "Hey [First Name], it's Wallace. Your AI receptionist is ready for you to test. Whenever you have 5 minutes today, call your own business number and talk to it like you are a customer. Try booking an appointment, ask it a question, see how it sounds. Then shoot me a text and tell me what you think. If anything needs tweaking, I will fix it on the spot."

**What to confirm during the client test:**
- [ ] Greeting sounds right (company name, tone, personality)
- [ ] AI captures caller information properly
- [ ] Appointment is booked and appears on their calendar
- [ ] Text/email notification is received by the owner
- [ ] Emergency scenario works correctly (if they want to test it)
- [ ] Client provides feedback on anything they want changed

**After the client test:**
- [ ] Implement any adjustments based on client feedback
- [ ] Re-test if adjustments were significant
- [ ] Confirm with client that everything sounds good

---

### Hours 36-48: Go Live

**Pre-launch confirmation text:**

> "Hey [First Name], everything is dialed in. I am flipping you live right now. From this moment, every call to [Company Name] is being answered. You will start getting text notifications for each call. If anything feels off in the first few hours, text me immediately and I will fix it. Congrats — you just solved your missed call problem."

**Go-live actions:**
- [ ] Flip system to LIVE
- [ ] Confirm call forwarding is active and routing correctly
- [ ] Welcome Email #3 sent automatically: "You're live — every call is now answered"
- [ ] Move GHL pipeline stage to "Live"
- [ ] Add tag `live` to client contact in GHL
- [ ] Post in internal channel: "[Business Name] is now live"

**Ideal go-live timing:** Before noon. Go live before afternoon call volume picks up so the client sees results on Day 1.

---

## 2. The First 30 Days — Weekly Check-In Schedule

The first 30 days are the danger zone. This is when clients are deciding whether The Call Taker is worth keeping. Your job is to make the value undeniable before the second invoice hits.

---

### Week 1 (Days 1-7): Daily Monitoring

**Daily tasks — every day for the first 7 days:**

- [ ] Review every call transcript/summary from the previous day
- [ ] Check for calls the AI handled incorrectly or awkwardly
- [ ] Verify notifications are being delivered consistently
- [ ] Verify appointments are syncing to the calendar correctly
- [ ] Make proactive adjustments to AI configuration if patterns emerge
- [ ] If any issue is found, fix it immediately and notify the client

**Day 3 — Unprompted Check-In Text:**

> "Hey [First Name], it's Wallace. Just checking in — your AI has handled [X] calls in the first 3 days. Everything is running smooth on our end. How is it looking on yours? Anything you want us to adjust?"

**Why this matters:** The client did not ask for this text. That is the point. Proactive communication tells them someone is watching, someone cares, and they are not just another subscription. Most SaaS companies disappear after signup. You do the opposite.

**Day 7 — First Week Check-In Call:**

> "Hey [First Name], it's Wallace. You have been live for a week so I wanted to check in and share your numbers.
>
> In your first week, your AI receptionist answered [X] calls. [X] appointments were booked. [X] of those were after-hours calls that would have gone to voicemail before.
>
> At your average job value of $[X], those after-hours calls alone represent roughly $[X] in revenue you would have lost.
>
> How is everything feeling on your end? Are you happy with how the AI is handling calls? Anything you want us to change or improve?
>
> **[Listen. Take notes. Do not get defensive about anything.]**
>
> Perfect. I am going to keep monitoring everything this week and I will have a full performance report for you at the two-week mark. If anything comes up before then, you have my number."

**After the call:**
- [ ] Document all feedback and change requests
- [ ] Implement any requested adjustments within 24 hours
- [ ] Move GHL pipeline stage to "Week 1 Complete"
- [ ] Welcome Email #4 sent automatically: "Your first week by the numbers"

---

### Week 2 (Days 8-14): First Performance Report

**Daily tasks (reduced cadence):**

- [ ] Review call logs every other day (Monday, Wednesday, Friday)
- [ ] Flag any AI handling issues and fix within 24 hours
- [ ] Monitor notification delivery

**Day 14 — Two-Week Performance Report:**

Send the client their first performance summary. This can be done via text, email, or a brief call — match the client's preferred communication style.

**Data to include:**
- Total calls answered (Week 1 + Week 2)
- Appointments booked
- After-hours calls handled
- Emergency calls dispatched
- Calls that required human follow-up
- Estimated revenue impact (after-hours calls x average job value)

**Day 14 — Follow-Up Text After Sending Report:**

> "Hey [First Name], just sent over your two-week numbers. [X] calls answered, [X] appointments booked, roughly $[X] in revenue that would have walked if nobody picked up the phone. Pretty solid for two weeks.
>
> Quick question — if you are happy with how things are going, would you be willing to share a quick one-sentence testimonial I could use? Something like 'Before The Call Taker, we were missing calls every day. Now every call gets answered.' Totally optional, but it would mean a lot.
>
> Also — know any other HVAC companies that are losing calls to voicemail? For every company you refer that signs up, I will give you a $50 credit on your next invoice. Just send me their name and number and I will take it from there."

**After sending:**
- [ ] Move GHL pipeline stage to "Week 2 Complete"
- [ ] Welcome Email #5 sent automatically: "Quick question about your experience" (includes referral ask)
- [ ] Note whether client is a strong referral candidate (enthusiastic, vocal, well-connected)

---

### Week 3 (Days 15-21): Optimization Adjustments

**This is the tuning week.** By now you have 2-3 weeks of real call data. Use it.

**Optimization checklist:**

- [ ] Review all call transcripts from Weeks 1-2 for recurring patterns
- [ ] Identify the top 5 questions callers are asking that the AI could handle better
- [ ] Update the AI's FAQ responses based on real call data
- [ ] Adjust scheduling rules if the client is getting booked at inconvenient times
- [ ] Refine the greeting if callers seem confused or if the tone is off
- [ ] Add any new services, promotions, or seasonal messaging the client has mentioned
- [ ] Check if any callers are asking questions the AI was not trained to answer — add those answers
- [ ] Verify the emergency protocol is working as intended with real call data
- [ ] Send the client a brief update on what was optimized:

> "Hey [First Name], quick update. I reviewed all of your call data from the first few weeks and made a few improvements to your AI:
>
> - Updated the FAQ answers based on the most common questions your callers are asking
> - [Specific adjustment #2]
> - [Specific adjustment #3]
>
> Everything should be even smoother now. No action needed on your end."

---

### Week 4 (Days 22-30): 30-Day Review Call

**This is the most important call in the entire client relationship.** The second invoice is about to hit. If the client does not feel like The Call Taker is paying for itself, they will cancel. This call locks them in.

**30-Day Review Call Script:**

> "Hey [First Name], it's Wallace. You have officially been live with The Call Taker for a full month, so I wanted to jump on a quick call and walk you through how things are going.
>
> **Here are your 30-day numbers:**
>
> - Total calls answered: [X]
> - Appointments booked by the AI: [X]
> - After-hours calls caught: [X]
> - Emergency calls dispatched: [X]
> - Calls flagged for your follow-up: [X]
>
> **Here is what that means in dollars:**
>
> At your average job value of $[X], the [X] after-hours calls alone represent approximately $[X] in revenue that would have gone to a competitor if nobody picked up. Your investment in The Call Taker this month was $[297/497]. Your estimated return was $[X]. That is a [X]:1 ROI.
>
> **[Pause. Let the numbers sink in.]**
>
> How are you feeling about everything? Is there anything about the way the AI handles calls that you want us to change?
>
> **[Listen carefully. Address every concern.]**
>
> A couple of things looking ahead:
>
> 1. Are there any seasonal changes coming up? Summer is when HVAC call volume spikes, so if you are going to be running any promotions or extending hours, let me know and I will update the AI.
>
> 2. Have your hours, services, or staff changed at all? I want to make sure the AI always has your latest information.
>
> 3. **[If client is on Starter and call volume is high:]** I noticed you are averaging [X] calls per month. That is on the higher end for the Starter plan. When you are ready, the Professional plan gives you [specific Pro features — priority support, advanced reporting, multi-location support, etc.]. No pressure at all, but I wanted you to know it is there.
>
> Last thing — you have been awesome to work with. If you know any other HVAC companies that are still sending calls to voicemail, I will give you a $50 credit on your next invoice for every one you send my way. Just text me their name and number and I will handle it from there.
>
> Thanks for trusting us with your phones, [First Name]. We are not going anywhere."

**After the call:**
- [ ] Document all feedback
- [ ] Implement any requested changes within 24 hours
- [ ] Update seasonal settings if applicable
- [ ] Move GHL pipeline stage to "Active Client"
- [ ] Client exits onboarding email sequence, enters ongoing nurture sequence
- [ ] Set reminder for quarterly check-in (Day 90)
- [ ] If client expressed high satisfaction, tag as `referral-candidate` in GHL
- [ ] If client expressed concerns, tag as `at-risk` and create immediate action plan

---

## 3. Monthly Performance Report Template

Send this report on the 1st of every month (or the client's billing anniversary). The report should take less than 5 minutes to compile once you have the data. Automate as much as possible through GHL.

---

### THE CALL TAKER — MONTHLY PERFORMANCE REPORT

**Client:** [Company Name]
**Report Period:** [Month Year]
**Prepared by:** Wallace Dobbs, The Call Taker

---

#### Call Summary

| Metric | This Month | Last Month | Change |
|---|---|---|---|
| **Total Calls Answered** | [X] | [X] | [+/- X] |
| **Appointments Booked** | [X] | [X] | [+/- X] |
| **After-Hours Calls Answered** | [X] | [X] | [+/- X] |
| **Emergency Calls Dispatched** | [X] | [X] | [+/- X] |
| **Calls Requiring Follow-Up** | [X] | [X] | [+/- X] |
| **Average Answer Time** | [X] sec | [X] sec | [+/- X] |

---

#### Revenue Impact

| Metric | Value |
|---|---|
| **After-Hours Calls Caught** | [X] calls |
| **Average Job Value** | $[X] |
| **Estimated Revenue Recovered** | **$[X]** |
| **Your Monthly Investment** | $[297 or 497] |
| **Estimated ROI** | **[X]:1** |
| **Estimated Revenue Recovered (Year-to-Date)** | $[X] |

*Revenue recovered estimate = after-hours calls caught x average job value x 40% booking rate. This is a conservative estimate — actual revenue impact may be higher when accounting for overflow calls caught during business hours.*

---

#### Customer Satisfaction Indicators

| Indicator | Status |
|---|---|
| **Calls Completed Without Transfer/Escalation** | [X]% |
| **Appointments Successfully Booked on First Call** | [X]% |
| **Emergency Calls Dispatched Within Protocol** | [X]% |
| **Callers Who Hung Up Mid-Call** | [X] ([X]%) |
| **Repeat Callers (Called Back After AI Interaction)** | [X] |

---

#### How You Compare

| Metric | Your Business | Industry Average* |
|---|---|---|
| **Call Answer Rate** | 100% (with The Call Taker) | 62% |
| **After-Hours Availability** | 24/7 | Business hours only |
| **Average Speed to Answer** | Under 3 seconds | 4+ rings (18+ seconds) |
| **Customer Callback Required** | Only for flagged calls | Every after-hours call |
| **Appointments Booked Automatically** | [X]% | 0% (manual booking) |

*Industry averages based on HVAC industry call-handling data and ServiceTitan benchmarks.*

---

#### Highlights This Month

- [Specific win — e.g., "Your AI caught a no-heat emergency call at 11:47 PM on January 14th and dispatched your on-call tech within 2 minutes. The customer was thrilled."]
- [Specific win — e.g., "7 appointments were booked after 6 PM — all of these would have been voicemails."]
- [Optimization made — e.g., "We updated your AI's response to questions about financing based on caller patterns."]

---

#### Recommendations

- [Actionable suggestion — e.g., "Your after-hours call volume has increased 20% month-over-month. Consider extending your regular hours or adding a weekend dispatch technician."]
- [Seasonal note — e.g., "Spring tune-up season starts next month. Let us know if you want to add a promotion message to the AI's script."]
- [Upsell if appropriate — e.g., "Your call volume is consistently above 80 calls/month. The Professional plan includes advanced reporting and priority support — let me know if you would like to discuss."]

---

**Questions or changes?** Reply to this email or text Wallace at (615) 653-9004.

*The Call Taker — thecalltaker.com*

---

### Report Delivery Protocol

1. Generate the report data from GHL / call logs
2. Fill in the template
3. Add 2-3 personalized highlights (do not send a generic report — every client should see something specific to their business)
4. Email the report on the 1st of the month (or billing anniversary)
5. Follow up with a text 24 hours later:

> "Hey [First Name], sent over your monthly report. [X] calls answered, roughly $[X] in recovered revenue. Your AI is earning its keep. Let me know if you have any questions."

---

## 4. Churn Prevention — Red Flags and Save Plays

Losing a client costs more than the lost revenue. It costs setup time, reputation, and referral potential. The goal is to catch problems before the client even thinks about cancelling.

---

### 5 Warning Signs a Client Is About to Cancel

**Red Flag #1: They stop responding to check-in messages.**

- What it looks like: You send a text or email and get nothing back. No reply to the weekly check-in. No reply to the monthly report. Silence.
- Why it matters: Engaged clients respond. Silent clients are either unhappy or have forgotten about you — both are dangerous.
- **Action:** Call them directly within 48 hours. Do not send another text. A phone call shows you noticed and you care.

> "Hey [First Name], it's Wallace. I sent over your report a couple days ago and wanted to make sure everything is going well. Sometimes no news is good news, but I just want to confirm you are happy with how the AI is handling things. Everything good?"

---

**Red Flag #2: Call volume drops significantly with no seasonal explanation.**

- What it looks like: Client was averaging 40 calls/month, suddenly drops to 12. No seasonal reason (it is not December for an AC-heavy company).
- Why it matters: They may have turned off call forwarding, started answering calls themselves again, or reduced their advertising. Any of these means they are pulling away.
- **Action:** Call them immediately.

> "Hey [First Name], I noticed your call volume dropped quite a bit this month — from about [X] to [X]. Just wanted to check in and make sure everything is set up correctly on the forwarding side. Is there anything going on with the business I should know about? I want to make sure you are getting the full value."

---

**Red Flag #3: They ask about their contract terms or cancellation policy.**

- What it looks like: "Hey, are we locked into this?" or "What is the cancellation process?" or "Is there a cancellation fee?"
- Why it matters: They are not asking out of curiosity. They are considering leaving.
- **Action:** Do not answer the question and move on. Address it directly and ask what is going on.

> "Of course — there is no contract, you can cancel anytime with 30 days notice, no fees. But I want to be real with you — when someone asks me that, it usually means something is not working the way they expected. What is going on? Is there something about the service that is bothering you? Because I would rather fix it than lose you."

---

**Red Flag #4: They complain about the same issue more than once.**

- What it looks like: "The AI keeps quoting the wrong service call fee" or "I told you to fix the scheduling window and it is still wrong."
- Why it matters: One complaint is normal. Two complaints about the same issue means you dropped the ball on follow-through, and the client is losing trust.
- **Action:** Fix it immediately — within the hour, not within 24 hours. Then follow up personally to confirm.

> "Hey [First Name], I want to sincerely apologize. You told us about this issue and it should have been fixed the first time. I just went in and corrected it personally, and I tested it myself to make sure it is right. I am going to monitor your calls for the next 48 hours to make sure this does not happen again. This is on us and I take full responsibility."

---

**Red Flag #5: Their payment fails and they do not update it quickly.**

- What it looks like: Card declines. Dunning email goes out. No response for 3+ days.
- Why it matters: If they cared about keeping the service, they would update their card the same day. A slow response to a failed payment often means they were already thinking about cancelling and the failed payment gave them an excuse.
- **Action:** Call on Day 2 of failed payment. Do not wait for the automated dunning sequence to run its course.

> "Hey [First Name], it's Wallace. Looks like the card on file got declined — that happens, no big deal. I just want to make sure your AI stays active and keeps answering your calls. Can you shoot me an updated card or I can take it over the phone right now? Also — while I have you — how is everything going with the service?"

---

### Exact Response for Each Cancellation Reason

When a client says they want to cancel, your first job is to understand the real reason. Your second job is to offer a solution before accepting the cancellation.

---

**Reason 1: "It's too expensive."**

> "I hear you, and I respect that — every dollar matters. Before we process anything, let me pull up your numbers real quick. Last month, your AI answered [X] calls and booked [X] appointments. At your average job value of $[X], that is roughly $[X] in revenue The Call Taker helped you capture. Your investment was $[297/497]. So the service is actually making you money, not costing you money.
>
> But if cash flow is tight right now, I have an option: I can pause your account for up to 60 days at no charge. Your AI goes offline, your billing stops, and when you are ready to come back, we flip it right back on with all your settings saved. No setup fee, no hassle. Would that help?"

---

**Reason 2: "I'm not getting enough value / I don't see the results."**

> "That is important feedback and I appreciate you being straight with me. Can I ask — when you say you are not seeing results, what were you expecting to see that you are not? ... Okay, let me look at your data.
>
> [Pull up their actual metrics.]
>
> Here is what I am seeing: [X] calls answered, [X] after-hours catches, [X] appointments booked. Is it possible the value is there but it is not as visible because you are not reviewing the notifications or reports? Or is it that the call volume itself is low?
>
> If the volume is the issue, I want to make sure your forwarding is set up correctly on all your lines — your main number, your Google Business number, your website click-to-call. Sometimes clients only forward one line and miss the rest. Can we check that together right now?"

---

**Reason 3: "I hired an office person / my wife is answering now."**

> "That is great — having someone dedicated to the phones is huge. And I would never try to replace a real person. But here is what I would ask you to think about: what happens at lunch? What happens when she is on another call? After 5 PM? Weekends? Holidays? Sick days?
>
> The Call Taker is not meant to replace your office person — it is her backup. It catches every call she cannot get to. And honestly, a lot of our clients who have office staff keep The Call Taker specifically for after-hours and overflow. It takes the pressure off everyone.
>
> What if we restructured your setup to after-hours and overflow only? Same price, but the AI only picks up the calls that would otherwise hit voicemail. That way your office person handles everything during the day and the AI covers the gaps."

---

**Reason 4: "I'm going out of business / closing / retiring."**

> "Man, I am sorry to hear that. I genuinely hope things work out. We will get your account closed out — no hassle, no hard feelings. And listen — if things change down the road, or if you end up starting something new, your setup is saved and we can have you back live in 24 hours. I wish you all the best, [First Name]."

*Do not try to save this one. Be gracious. They may come back, and they will definitely remember how you treated them on the way out.*

---

**Reason 5: "The AI isn't handling calls well / customers are complaining."**

> "I take that seriously. Can you tell me specifically what happened? Which calls were the issue? ... Let me pull those up right now.
>
> [Review the specific call transcripts with the client.]
>
> Okay, I see what happened here. [Explain what went wrong and why.] Here is what I am going to do: I am going to fix this today. I am going to retrain the AI on [specific issue], test it myself with three different scenarios, and then I will send you a recording of the test calls so you can hear the improvement before another customer calls.
>
> I do not want you to cancel over something I can fix. Give me 48 hours. If you are not happy with the improvement, I will process the cancellation with no questions asked and I will credit you for this month. Fair?"

---

### The "Pause Instead of Cancel" Offer

This is your most powerful save tool. When a client wants to cancel for any reason except going out of business, offer the pause.

**The Pause Offer:**

> "I completely understand. Before we process the cancellation, I want to offer you something: instead of cancelling outright, what if we pause your account? Here is how it works:
>
> - Your billing stops immediately — no charges while you are on pause
> - Your AI configuration is saved exactly as it is — all your settings, your greeting, your scheduling rules, everything
> - You can pause for up to 60 days
> - When you are ready to come back, we flip it live in 24 hours with no setup fee
>
> That way you are not paying anything while you figure things out, but you also do not lose all the work we put into building your system. If after 60 days you still want to cancel, we process it then. No pressure. Does that sound fair?"

**Why this works:**
- It removes the financial objection immediately
- It reduces the finality of the decision (pause feels lighter than cancel)
- 40-60% of paused clients reactivate because they start missing calls again within 2-3 weeks
- It keeps the door open for the win-back campaign

**GHL actions when a client pauses:**
- [ ] Deactivate AI receptionist
- [ ] Stop billing via Stripe
- [ ] Remove `live` tag, add `paused` tag
- [ ] Move pipeline stage to "Paused"
- [ ] Set calendar reminder: Day 14 of pause (check-in), Day 45 (reactivation offer), Day 55 (final notice)
- [ ] Do NOT delete any configuration

---

### Win-Back Campaign for Lost Clients

For clients who cancel (not pause), run this sequence. The goal is to bring them back within 90 days, before they forget about you.

**Day 1 (Cancellation Day):**

Send a gracious cancellation confirmation. No guilt, no pressure.

> "Hey [First Name], your account is now closed. All your AI settings are saved for 90 days in case you ever want to come back — no setup fee, we just flip it on. I genuinely appreciate you giving The Call Taker a shot, and I wish you and [Company Name] nothing but success. If you ever need anything, you know where to find me. — Wallace"

**Day 14 — The Check-In Text:**

> "Hey [First Name], it's Wallace. Just checking in — how is everything going with the phones since you left The Call Taker? Hope all is well."

*This is not a sales pitch. It is a genuine check-in. If they are already frustrated with missed calls, they will tell you. If not, you stay top of mind.*

**Day 30 — The Data Nudge:**

> "Hey [First Name], quick thought. Since you have been off The Call Taker, you have been live for about a month without AI answering. Do you know how many calls are going to voicemail? When you were with us, your AI was catching an average of [X] after-hours calls per month — that was roughly $[X] in revenue. Just wanted to put that out there. If you ever want to come back, your settings are still saved and I can have you live again in 24 hours."

**Day 60 — The Incentive Offer:**

> "Hey [First Name], Wallace here. I have a one-time offer for you: come back to The Call Taker this month and I will give you your first month at 50% off — that is $[148.50 or 248.50] to get back up and running. Your AI settings are still saved, so there is zero setup. We can have you answering calls again by tomorrow. This offer is good through [date — 2 weeks out]. Just text me 'I'm in' and I will handle the rest."

**Day 90 — The Final Reach-Out:**

> "Hey [First Name], last message from me — I promise I am not going to keep bugging you. Your saved AI settings expire at the end of this month. After that, if you want to come back, we would need to do a fresh setup. No hard feelings either way — I just did not want you to lose the work we built without knowing about it. If you want to reactivate, just let me know before [date]. Hope business is treating you well."

**GHL automation for win-back:**
- [ ] Tag cancelled clients with `win-back-sequence`
- [ ] Set up GHL workflow with timed text messages at Day 14, 30, 60, and 90
- [ ] If client re-engages, remove from sequence and tag as `reactivated`
- [ ] Track win-back conversion rate monthly

---

## 5. Referral Generation System

Referrals are the lowest-cost, highest-conversion source of new clients. A referred HVAC company converts at 3-5x the rate of a cold lead because trust is already established. This section is about getting those referrals consistently, not accidentally.

---

### When to Ask for Referrals — The 5 Perfect Moments

**Moment 1: After the first week check-in (Day 7) — IF the client is happy.**

Only ask if the client has expressed genuine satisfaction during the Week 1 call. If they had complaints, fix those first and wait until Week 2.

**Moment 2: After delivering the two-week performance report (Day 14).**

This is the primary referral ask moment. The client has data showing the AI is working. They have numbers to point to. They feel good. Ask now.

**Moment 3: Immediately after resolving a problem or complaint.**

Counter-intuitive, but powerful. When you fix an issue fast and the client says "wow, that was quick" or "thanks for handling that" — that is a moment of peak trust. They just experienced your customer service at its best.

> "Happy to do it — that is what we are here for. Hey, while I have you — do you know any other HVAC companies that could use this kind of support?"

**Moment 4: After delivering a monthly report that shows strong ROI.**

When the numbers are undeniable — high call volume, strong revenue recovered — the client feels smart for using The Call Taker. That is when they are most willing to recommend it.

**Moment 5: After a seasonal volume spike (first hot week of summer / first cold snap of winter).**

When the AI handled a surge of calls during a peak period and the client saw the value in real time, they are primed to tell other HVAC owners about it.

> "Your AI caught [X] calls during that cold snap last week — [X] of those were after midnight. Pretty wild, right? If you know anyone else in HVAC who is still sending those calls to voicemail, send them my way. $50 credit on your next bill for each one that signs up."

---

### The Exact Referral Ask Script

**In-person or on a call:**

> "Hey [First Name], I have a quick question for you. You have been seeing the results — [X] calls answered, $[X] in revenue recovered. I am glad it is working for you.
>
> Here is the thing — the best way I grow this business is through guys like you who are already seeing results and know other HVAC owners. So I will just ask straight up: do you know one or two other HVAC companies that are still losing calls to voicemail?
>
> If you send someone my way and they sign up, I will knock $50 off your next month's bill. No limit — refer five guys, that is $250 off. All you have to do is text me their name and number, or shoot them a quick text with my number. I will handle the rest. I will never cold-call anyone or pressure them — I will just mention you sent me and let the demo line do the talking."

**Via text (after a positive interaction):**

> "Hey [First Name], glad everything is running smooth. Quick ask — know any other HVAC companies that are still sending calls to voicemail? I will give you a $50 credit on your next invoice for each one you refer that signs up. Just text me their name and number and I will take it from there. No cold-calling — I just mention you recommended us."

---

### Referral Incentive Structure

| Action | Reward |
|---|---|
| Client refers an HVAC company | **$50 credit** on client's next invoice |
| Referred company signs up | Credit applied automatically |
| No limit on referrals | Refer 5 = $250 off. Refer 6 = free month (Starter). |
| Referral does not sign up | No penalty, no awkwardness |

**Why $50 credit instead of cash:**
- Credits keep the client as a paying customer (they are reducing their bill, not leaving)
- $50 is meaningful on a $297 bill (17% discount) without being so large it feels gimmicky
- It is simple to track and apply in Stripe/GHL
- Clients can stack credits — 6 referrals in a month = their Starter plan is free that month

**Tracking referrals:**
- When a client sends a referral, add the referring client's name to the new prospect's GHL contact record in the `referral_source` custom field
- When the referred company signs up, apply the $50 credit to the referring client's next Stripe invoice
- Send the referring client a confirmation text:

> "Hey [First Name], [Referred Company Name] just signed up. $50 credit applied to your next bill. Thanks for spreading the word — you are the reason we grow."

---

### Pre-Written Referral Messages — Make It Easy

Give clients a text or email they can copy-paste and forward to another HVAC owner. Eliminate all friction. They should not have to think about what to say.

**Pre-written text the client can forward:**

> "Hey [Name], I started using this AI receptionist for my HVAC business a couple months ago and it has been a game changer. It answers every call 24/7, books the appointment, and texts me the details. No more missed calls, no more voicemail. The company is called The Call Taker. If you want to hear what it sounds like, call their demo line: (615) 784-5747. It picks up in 2 seconds and handles the call like a real person. My guy Wallace runs it — tell him I sent you. His number is (615) 653-9004."

**Send this to the client via text:**

> "Hey [First Name], here is a text you can forward to any HVAC owner you think could use The Call Taker. Just copy and paste it — change the name at the top and hit send. Easy as that:
>
> [Paste the pre-written text above]
>
> Every referral that signs up = $50 off your next bill. Thanks for helping us grow."

**Pre-written email the client can forward:**

> Subject: This thing answers my HVAC calls 24/7 — you should check it out
>
> Hey [Name],
>
> Wanted to pass this along. I have been using an AI receptionist called The Call Taker for my HVAC business and it has been great. Every call gets answered, appointments get booked automatically, and I get a text with the details after every call. No more missed calls, no more losing jobs to voicemail.
>
> It is $297/month, no contract, and they set everything up in 48 hours.
>
> If you want to hear it, call their demo line: (615) 784-5747. It sounds like a real receptionist.
>
> The owner is Wallace — good dude, knows the trades. His number is (615) 653-9004 or you can check out thecalltaker.com.
>
> Worth a look.
>
> [Client's Name]

**Send this email template to the client:**

> "Hey [First Name], here is an email you can forward to anyone in HVAC who might need The Call Taker. Just change the name at the top and send it. Each signup = $50 off your bill.
>
> [Paste the pre-written email above]"

---

## 6. Upsell Strategy — Starter to Professional

Moving a client from $297/mo to $497/mo is the single highest-leverage revenue action in the business. No new customer acquisition cost. No new setup. Pure incremental revenue of $200/mo ($2,400/year) per upgrade.

---

### When to Suggest the Upgrade

**Never suggest the upgrade before Day 30.** The client needs to be fully onboarded, seeing results, and trusting you before you introduce a higher price point. Premature upselling destroys trust.

**The 4 Upgrade Triggers — Suggest the upgrade when any of these are true:**

**Trigger 1: Call volume consistently exceeds 60 calls/month for 2+ months.**

High volume means the client is getting heavy use and heavy value. They are the ideal candidate because the per-call cost of the service is already extremely low for them.

**Trigger 2: The client asks for a feature that is only available on Professional.**

This is the easiest upsell because the client is telling you what they want. Do not give it away for free. Position it as the natural next step.

> "Great news — that feature is included in the Professional plan. Want me to walk you through what else you would get?"

**Trigger 3: The client adds a second business phone number or location.**

Expansion signals growth. Growth signals a company that can afford and benefit from the Professional tier.

**Trigger 4: The 90-day quarterly review call.**

By the 90-day mark, the client has 3 months of data, strong ROI proof, and established trust. The quarterly call is a natural moment to discuss whether their current plan still fits.

---

### How to Position the Value

**Rule #1:** Never position the upgrade as "more features for more money." Position it as "your business has outgrown the Starter plan."

**Rule #2:** Use their own data to make the case. The numbers should do the selling.

**Rule #3:** Frame it as recognition of their success, not an upsell. They are growing. This is the next step for a growing company.

**The Positioning Framework:**

| Starter Plan ($297/mo) | Professional Plan ($497/mo) |
|---|---|
| Designed for 1-2 truck operations | Designed for 3+ truck operations |
| Standard call handling | Priority call handling and advanced routing |
| Monthly performance report | Weekly performance reports with deeper analytics |
| Standard support (24-hour response) | Priority support (same-day response) |
| Single location | Multi-location support |
| Standard scheduling | Advanced scheduling with tech assignment |
| Basic notifications | Advanced notifications with call categorization |
| Seasonal updates on request | Proactive seasonal optimization (we update before you ask) |

*Note: Adjust the specific feature differentiation based on your actual plan tiers. The key is that Professional should solve problems that high-volume clients specifically face.*

---

### The "Your Volume Says You're Ready" Conversation

**Use this during a monthly report review or quarterly check-in when the client's data supports the upgrade.**

> "Hey [First Name], I have been looking at your numbers and I want to share something with you. Over the last [2-3] months, your AI has been handling an average of [X] calls per month. That puts you well above where most of our Starter plan clients sit.
>
> You are running a bigger operation than the Starter plan was designed for, and honestly, you are leaving some value on the table. Let me explain what I mean.
>
> Right now on the Starter plan, you are getting [specific limitation — e.g., monthly reports, standard support response times, single-location setup]. On the Professional plan, you would get [specific benefit that solves a real problem they have — e.g., weekly reports so you can spot trends faster, same-day support so issues get fixed immediately, multi-line support for your second office number].
>
> Here is the math. You are paying $297 right now. The Professional plan is $497. That is an extra $200 a month — which is less than the value of ONE additional call your AI catches. And with [specific Pro feature], you are going to capture even more.
>
> I am not trying to sell you something you do not need. But your call volume is telling me you have outgrown the Starter plan, and I would rather tell you that than watch you hit a ceiling.
>
> What do you think? Want me to move you over?"

**If they hesitate:**

> "No pressure at all. Tell you what — why don't I upgrade you to Professional for the next 30 days, and if you do not feel the difference, I will move you right back to Starter. You can see for yourself whether the extra features are worth it for your operation."

**If they say no:**

> "Totally fine. The Starter plan is still a great fit right now. I will keep watching your numbers, and if things change, we can revisit it. No hard feelings."

*Document the conversation in GHL. Set a reminder to revisit in 60 days. Do not ask again before then.*

---

### Upsell Tracking

- [ ] Tag clients who are potential upgrade candidates as `upsell-candidate` in GHL
- [ ] Track which trigger prompted the conversation (volume, feature request, expansion, quarterly review)
- [ ] Track conversion rate: how many upsell conversations result in upgrades
- [ ] Track timing: how many months after signup does the average upgrade happen
- [ ] Goal: 20% of Starter clients upgrade to Professional within 6 months

---

## Quick Reference: Customer Success Calendar

| Timeframe | Action | Owner |
|---|---|---|
| Hour 0-1 | Welcome call, info collection | Wallace |
| Hours 2-24 | Build AI, configure, internal QA | Wallace |
| Hours 24-36 | Client test call | Wallace |
| Hours 36-48 | Go live | Wallace |
| Day 3 | Proactive check-in text | Wallace |
| Day 7 | Week 1 check-in call + first stats | Wallace |
| Day 14 | Two-week performance report + referral ask | Wallace |
| Day 15-21 | Optimization week — tune AI based on data | Wallace |
| Day 28-30 | 30-day review call | Wallace |
| Monthly | Performance report | Wallace |
| Quarterly | Quarterly review call + upsell evaluation | Wallace |
| Ongoing | Monitor for churn red flags | Wallace |
| As needed | Seasonal updates (spring/summer/fall/winter) | Wallace |

---

## The Golden Rules of Customer Success

1. **Respond to every client message within 4 hours.** This is non-negotiable. Speed of response is the number one driver of client satisfaction in service businesses.

2. **Never send a generic message.** Every text, email, and report should reference something specific to their business. Use their name, their company name, their actual numbers.

3. **Fix problems before being asked.** If you see an issue in the call logs, fix it and then tell the client you fixed it. Do not wait for them to notice and complain.

4. **Deliver the monthly report even if the client never asks for it.** The report is not just data — it is a monthly reminder that The Call Taker is working and worth paying for.

5. **Ask for referrals when the client feels smart, not when you feel desperate.** The best referral moment is right after you show them a strong performance report or solve a problem quickly.

6. **Never argue with a client who wants to cancel.** Understand. Empathize. Offer the pause. If they still want out, process it with grace. They will remember how you handled the exit, and some of them will come back.

7. **The first 48 hours and the 30-day review are the two moments that determine retention.** Nail the onboarding, nail the 30-day call, and you will keep clients for years.

---

*The Call Taker — thecalltaker.com — (615) 784-5747*
*$297/mo Starter | $497/mo Professional | No Contracts | Cancel Anytime*