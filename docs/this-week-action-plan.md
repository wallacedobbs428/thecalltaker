# This Week's Action Plan — First Paying Client

> Goal: 1 demo booked by Wednesday. 1 pilot started by Friday. 1 paid client by Sunday.
> Week of March 13, 2026

## Monday — Score + Strike First 5

Morning (8-9am):
- Run lead-scorer: `python3 max/lead-scorer.py score`
- Review the ranked list — screenshot your top 10
- Pick the 5 highest-scored leads with phone numbers

Midday (10am-12pm):
- Manually text the top 5 using the Day 0 SMS from docs/outreach-playbook.md
- Personalize each one — use their name, their industry, their city
- After sending, tag each one `wallace-texted` in GHL

Afternoon (1-3pm):
- Post 20 comments on HVAC/plumbing/dental Instagram accounts in Nashville + Memphis + Atlanta
- Comments should be helpful, not salesy ("Great work! How do you handle after-hours emergency calls?")
- Follow 10 target businesses on Instagram

Evening (6-8pm):
- Check for any replies from the top 5
- If anyone replied, respond immediately using objection handlers from docs/outreach-playbook.md
- Log all activity in a notebook or note

## Tuesday — Follow Up + Expand

Morning (8-9am):
- Check GHL for any email opens or reply notifications
- Anyone who opened but didn't respond → send Day 2 SMS (social proof message from playbook)

Midday (10am-12pm):
- Text the next 5 leads (leads #6-10 from the scored list)
- Same process: personalize, send Day 0 SMS, tag `wallace-texted`

Afternoon (1-3pm):
- 20 more Instagram comments on target industry accounts
- Check for demo line calls — anyone who called gets a personal follow-up text within 15 minutes
- Send Email 1 (Pure Pain) from docs/email-sequences.md to leads #1-5 from Monday

Evening:
- Reply to every single message/DM/text that came in today
- Start tracking: who opened, who replied, who's ghosting

## Wednesday — Blaster Day + Demo Push

Morning (8-9am):
- Run outreach-blaster: `python3 max/outreach-blaster.py send`
- This hits all remaining hot leads who haven't been contacted in 7 days
- Check results notification on ntfy

Midday (10am-12pm):
- Anyone from Mon/Tue who replied positively → call them personally
- Use the closing script from docs/outreach-playbook.md Section 4
- Goal: book at least 1 demo call or get 1 person to call (615) 784-5747

Afternoon (1-3pm):
- Send Day 2 SMS (social proof) to Tuesday's batch (leads #6-10)
- Send Email 2 (Social Proof) to Monday's batch (leads #1-5)
- 20 Instagram comments

Evening:
- Wallace + William sync: who's closest to converting? Who needs a Zoom demo?
- If anyone booked a demo, prep William with the lead's info + industry

## Thursday — Call Day

Morning (8-10am):
- Call EVERY lead who replied to any SMS or email — don't text, CALL
- Use the closing script from docs/outreach-playbook.md
- If they're interested: collect their info (business name, phone, industry, hours)
- If they say "send info": redirect to demo line (615) 784-5747

Midday (11am-1pm):
- Follow up with anyone who called the demo line but didn't text PILOT
- "Hey [name], saw you checked out our demo line — what'd you think? Want me to set one up for [company]?"
- Send Day 5 SMS (scarcity/last chance) to Monday's original batch

Afternoon (2-4pm):
- Send Email 3 (Final Offer) to Monday's batch
- Text anyone who opened emails but didn't reply: "hey [name], saw you checked out my email — any questions about the AI receptionist?"
- 20 Instagram comments

Evening:
- If someone said yes → tag them `pilot-signup` in GHL immediately
- The pilot onboarding engine auto-fires welcome sequence

## Friday — Close or Free Pilot Push

Morning (8-9am):
- Run lead-scorer again: `python3 max/lead-scorer.py score` — see if scores changed
- Anyone still cold from Monday gets the final offer: free pilot, no credit card, no risk

Midday (10am-12pm):
- Send the breakup email (Email 5) to anyone completely cold
- For warm leads who haven't committed: offer the free pilot directly
- "hey [name], tell you what — let me just set it up for [company] free for 14 days. if you don't like it, just turn it off. zero risk on your end"

Afternoon (1-3pm):
- Call top 3 warmest leads one more time
- If they pick up: close them. Use urgency: "I only have 3 pilot spots and 2 are spoken for"
- 20 Instagram comments

Evening:
- Status check: do we have a pilot started? A demo booked? Any warm leads?
- Plan weekend follow-ups if needed

## Weekend — Don't Stop

Saturday:
- Text anyone who replied during the week but didn't commit
- "hey [name], hope you're having a good weekend. just wanted to see if you made a decision on the AI receptionist pilot. still got a spot for [company]"
- Check demo line for weekend callers

Sunday:
- Run `python3 max/lead-scorer.py score` — fresh scores going into next week
- Review the week: how many texted, how many replied, how many demoed, how many piloted
- Plan next week based on what worked

## Daily Habits (Every Single Day)

- [ ] Check GHL for new replies/opens (morning + evening)
- [ ] 20 Instagram comments on target industry accounts
- [ ] Respond to every reply within 15 minutes
- [ ] Log who you contacted and what happened
- [ ] Check ntfy for demo line calls and hot signals

## Key Numbers to Track

| Metric | Target | Actual |
|--------|--------|--------|
| Total leads texted | 35 | |
| SMS replies received | 8-10 | |
| Demo line calls | 3-5 | |
| Demo meetings booked | 1-2 | |
| Pilot signups | 1 | |
| Paid conversions | 1 | |

## Tools at Your Disposal

- Lead scorer: `python3 max/lead-scorer.py score`
- Outreach blaster: `python3 max/outreach-blaster.py send`
- Outreach copy: `docs/outreach-playbook.md`
- Email sequences: `docs/email-sequences.md`
- Demo line: (615) 784-5747
- Closing script: Section 4 of outreach-playbook.md
- Objection handlers: Section 2 of outreach-playbook.md

## The Mindset

You have 35 hot leads. You need 1 to say yes. That's a 3% close rate. You've got the tools, the copy, the demo line, and the product. The only thing between you and your first paying client is picking up the phone and sending the texts.

Don't overthink it. Don't wait for the perfect moment. Just start texting Monday morning.

---

*Created March 13, 2026*
