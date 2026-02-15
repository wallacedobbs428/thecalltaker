# The Call Taker — Client Onboarding Steps

Complete checklist for onboarding a new HVAC client from signup to ongoing service.

Each step is marked: **[AUTO]** = automated / **[MANUAL]** = requires human action.

---

## Day 0: Signup

_Trigger: Client completes payment._

- [ ] **[AUTO]** Payment processed and confirmed via Stripe/payment processor
- [ ] **[AUTO]** Welcome Email #1 sent: "Welcome to The Call Taker — here's what happens next"
- [ ] **[AUTO]** Client added to GHL as new contact with tag `active-client`
- [ ] **[AUTO]** Client added to GHL pipeline: "Onboarding" → Stage: "New Signup"
- [ ] **[AUTO]** Internal Slack/text notification sent to onboarding team: "New client signed up: [Business Name]"
- [ ] **[MANUAL]** Review intake form for completeness — follow up on any missing fields
- [ ] **[MANUAL]** Create GHL sub-account for client (if applicable)
- [ ] **[MANUAL]** Add client to internal tracking spreadsheet / project management tool
- [ ] **[MANUAL]** Assign onboarding specialist to this client

**Day 0 Owner:** Onboarding Specialist
**Target Completion:** Within 2 hours of signup

---

## Day 1: Setup & Configuration

_Trigger: Intake form reviewed and complete._

### AI Receptionist Configuration

- [ ] **[MANUAL]** Configure AI receptionist with client's business information:
  - Business name and greeting script
  - Services offered
  - Business hours and after-hours handling rules
  - Service area
  - Pricing responses (service call fee, estimate policy, etc.)
  - Emergency protocol and on-call technician contact
  - Things the AI should never say
  - Special instructions, promotions, seasonal offers
- [ ] **[MANUAL]** Set AI receptionist tone/personality per client preference
- [ ] **[MANUAL]** Program FAQ answers from intake form

### Phone System Setup

- [ ] **[MANUAL]** Set up call forwarding from client's business number to our AI
  - Provide client with forwarding instructions for their carrier if needed
  - Confirm forwarding method: full forwarding, overflow, or after-hours only
- [ ] **[MANUAL]** Verify the forwarding is active and calls are routing correctly
- [ ] **[MANUAL]** Set up the outbound caller ID / notification number

### Calendar & Scheduling Setup

- [ ] **[MANUAL]** Connect to client's calendar system (Google Calendar, Jobber, ServiceTitan, etc.)
- [ ] **[MANUAL]** Configure appointment types with correct durations
- [ ] **[MANUAL]** Set scheduling rules: same-day, next-day, advance window, buffer time
- [ ] **[MANUAL]** Block out any restricted times per client instructions
- [ ] **[MANUAL]** Test booking a sample appointment — confirm it shows on client calendar

### Notifications Setup

- [ ] **[MANUAL]** Configure text notifications for owner (and any additional recipients)
- [ ] **[MANUAL]** Configure email notifications for owner (and any additional recipients)
- [ ] **[MANUAL]** Set notification triggers per client preferences (every call, bookings only, emergencies, etc.)
- [ ] **[MANUAL]** Send a test notification to confirm delivery

### Automated Sequences Setup

- [ ] **[MANUAL]** Set up appointment confirmation text (sent to customer after booking)
- [ ] **[MANUAL]** Set up appointment reminder text (sent to customer day before / morning of)
- [ ] **[MANUAL]** Set up missed-call follow-up text (if applicable)
- [ ] **[MANUAL]** Set up review request text (sent after completed appointment — if client wants this)

### Communications

- [ ] **[AUTO]** Welcome Email #2 sent: "Your AI receptionist is almost ready"
- [ ] **[AUTO]** Move GHL pipeline stage to "Setup In Progress"

### Internal QA

- [ ] **[MANUAL]** Internal test call #1: Call as a customer needing AC repair — verify greeting, info capture, and booking
- [ ] **[MANUAL]** Internal test call #2: Call as a customer with an emergency — verify emergency protocol triggers
- [ ] **[MANUAL]** Internal test call #3: Call asking common questions — verify AI gives correct answers
- [ ] **[MANUAL]** Internal test call #4: Call after hours (if applicable) — verify after-hours handling
- [ ] **[MANUAL]** Verify all test notifications were received by the right people
- [ ] **[MANUAL]** Document any issues found and fix before client test

**Day 1 Owner:** Onboarding Specialist + Technical Setup Team
**Target Completion:** End of business day

---

## Day 2: Client Testing & Go-Live

_Trigger: Internal QA passed._

### Client Test Call

- [ ] **[MANUAL]** Schedule a brief call/text with the client: "We're ready for you to test"
- [ ] **[MANUAL]** Client calls their own business number and interacts with the AI
- [ ] **[MANUAL]** Client confirms the following work correctly:
  - Greeting sounds right
  - AI captures caller information properly
  - Appointment is booked and appears on their calendar
  - Text/email notification is received
  - Emergency scenario works (if they want to test it)
- [ ] **[MANUAL]** Client provides feedback — note any changes requested
- [ ] **[MANUAL]** Implement any adjustments based on client feedback
- [ ] **[MANUAL]** Re-test if adjustments were significant

### Go-Live

- [ ] **[MANUAL]** Flip system to LIVE — confirm all calls are now being handled
- [ ] **[AUTO]** Welcome Email #3 sent: "You're live — every call is now answered"
- [ ] **[AUTO]** Move GHL pipeline stage to "Live"
- [ ] **[AUTO]** Add tag `live` to client contact in GHL
- [ ] **[MANUAL]** Post in internal channel: "[Business Name] is now live"

**Day 2 Owner:** Onboarding Specialist
**Target Completion:** By noon if possible — go live before afternoon call volume

---

## Day 3-6: Soft Monitoring Period

_No client-facing actions. Internal monitoring only._

- [ ] **[MANUAL]** Monitor first 48 hours of live calls — review transcripts/summaries for quality
- [ ] **[MANUAL]** Check for any calls the AI handled incorrectly or awkwardly
- [ ] **[MANUAL]** Verify all notifications are being delivered consistently
- [ ] **[MANUAL]** Verify appointments are syncing to calendar correctly
- [ ] **[MANUAL]** Make proactive adjustments to AI configuration if patterns emerge
- [ ] **[MANUAL]** If any issues are found, fix immediately and notify client

**Owner:** Onboarding Specialist
**Target:** Check call logs at least once per day during this period

---

## Day 7: First Week Check-In

_Trigger: 7 days after go-live._

- [ ] **[AUTO]** Welcome Email #4 sent: "Your first week with The Call Taker — here are the numbers"
  - Include: total calls answered, appointments booked, after-hours calls caught, estimated revenue recovered
- [ ] **[MANUAL]** Personal check-in with client via call or text:
  - "How's the first week going?"
  - "Are you happy with how the AI is handling calls?"
  - "Anything you want us to change or improve?"
- [ ] **[MANUAL]** Document any feedback or change requests
- [ ] **[MANUAL]** Implement any requested adjustments within 24 hours
- [ ] **[AUTO]** Move GHL pipeline stage to "Week 1 Complete"

**Day 7 Owner:** Onboarding Specialist or Account Manager
**Target Completion:** Same day

---

## Day 14: Two-Week Follow-Up

_Trigger: 14 days after go-live._

- [ ] **[AUTO]** Welcome Email #5 sent: "How's it going?" + referral ask
- [ ] **[MANUAL]** Review 2-week performance data:
  - Total calls answered
  - Appointments booked
  - After-hours calls handled
  - Emergency calls dispatched
  - Calls that required human follow-up
  - Estimated revenue impact
- [ ] **[MANUAL]** Share 2-week summary with client (can be done via text, email, or brief call)
- [ ] **[MANUAL]** Ask for a testimonial or Google review if client is happy
- [ ] **[MANUAL]** Introduce referral program: credit on next month for each referral that signs up
- [ ] **[AUTO]** Move GHL pipeline stage to "Week 2 Complete"
- [ ] **[MANUAL]** Transition client from Onboarding Specialist to Account Manager (if separate roles)

**Day 14 Owner:** Onboarding Specialist → handoff to Account Manager
**Target Completion:** Same day

---

## Day 30: First Month Review

_Trigger: 30 days after go-live._

- [ ] **[AUTO]** First monthly performance report generated and emailed to client
- [ ] **[MANUAL]** Account Manager reviews report and adds personal note
- [ ] **[MANUAL]** Brief check-in call with client:
  - Review numbers
  - Discuss any seasonal adjustments needed
  - Confirm satisfaction — address any concerns
  - Remind about referral program
- [ ] **[AUTO]** Move GHL pipeline stage to "Active Client"
- [ ] **[AUTO]** Client exits onboarding email sequence — enters ongoing client nurture sequence

**Day 30 Owner:** Account Manager
**Target Completion:** Within 3 days of the 30-day mark

---

## Ongoing Monthly (Repeating)

_Trigger: 1st of each month (or anniversary date)._

- [ ] **[AUTO]** Monthly performance report generated and emailed:
  - Calls answered
  - Appointments booked
  - After-hours calls caught
  - Emergency dispatches
  - Estimated revenue recovered
  - Month-over-month comparison
- [ ] **[MANUAL]** Account Manager reviews report for any red flags (drop in calls, increase in failed handoffs)
- [ ] **[MANUAL]** Quarterly check-in call (every 3 months):
  - Review performance
  - Update business info (hours, services, staff changes, new promotions)
  - Optimize AI settings based on call data
  - Discuss upsell opportunities if applicable
- [ ] **[MANUAL]** Update seasonal settings as needed:
  - Spring: AC tune-up promotions
  - Summer: Emergency AC priority messaging
  - Fall: Heating tune-up promotions
  - Winter: Emergency heating priority messaging
- [ ] **[AUTO]** Invoice generated and payment processed
- [ ] **[AUTO]** If payment fails, trigger dunning sequence (retry + notification emails)

**Ongoing Owner:** Account Manager
**Cadence:** Monthly report (automated), quarterly call (manual)

---

## Cancellation Process

_Trigger: Client requests cancellation._

- [ ] **[MANUAL]** Account Manager reaches out personally to understand reason for cancellation
- [ ] **[MANUAL]** Offer to resolve any issues — attempt to retain
- [ ] **[MANUAL]** If client confirms cancellation, process 30-day notice per agreement
- [ ] **[MANUAL]** Remove call forwarding on cancellation effective date
- [ ] **[MANUAL]** Deactivate AI receptionist for this client
- [ ] **[AUTO]** Send cancellation confirmation email
- [ ] **[AUTO]** Update GHL: remove `active-client` and `live` tags, add `cancelled` tag
- [ ] **[AUTO]** Move GHL pipeline stage to "Cancelled"
- [ ] **[MANUAL]** Send a "We'd love to have you back" email 60 days after cancellation

---

## Quick Reference: Automation Summary

| Step | Automated? | Tool/System |
|---|---|---|
| Welcome emails (1-5) | AUTO | GHL email sequence |
| Pipeline stage updates | AUTO | GHL workflow |
| Internal new-signup alert | AUTO | GHL → Slack/text notification |
| Monthly performance reports | AUTO | GHL + reporting dashboard |
| Invoice & payment processing | AUTO | Stripe + GHL |
| Payment failure dunning | AUTO | Stripe + GHL |
| AI configuration | MANUAL | AI platform admin panel |
| Call forwarding setup | MANUAL | Client's phone carrier + our system |
| Calendar connection | MANUAL | Calendar platform |
| Notification setup | MANUAL | GHL / AI platform |
| Internal QA test calls | MANUAL | Phone |
| Client test call | MANUAL | Phone |
| Check-in calls/texts | MANUAL | Phone / text |
| Feedback implementation | MANUAL | AI platform admin panel |
| Seasonal updates | MANUAL | AI platform admin panel |
