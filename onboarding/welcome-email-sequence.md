# The Call Taker — Welcome Email Sequence

5-email onboarding sequence for new HVAC clients.
Sent via GHL automated workflow triggered by signup.

---

## Email 1: Welcome + What Happens Next

**Trigger:** Immediately after payment is processed (Day 0)
**From:** Wallace Dobbs <wallacemdobbs@icloud.com>
**Subject:** Welcome to The Call Taker — here's what happens next

---

Hi {{contact.first_name}},

Welcome to The Call Taker! We are genuinely excited to be working with {{contact.company_name}}.

Starting now, you will never miss another customer call. No more voicemails. No more lost jobs. Every single call to your business gets answered, every single time.

Here is exactly what is happening right now:

**In the next 24 hours, our team is:**

1. Building your custom AI receptionist trained on your business — your services, your hours, your pricing, and your voice
2. Setting up call forwarding so every call to your business line is answered
3. Connecting your calendar so appointments get booked in real time
4. Configuring text and email notifications so you know about every call the moment it happens

**What do you need to do right now?**

Nothing. We have everything we need from your intake form. If we need any clarification, we will reach out directly.

**Timeline:**

Your AI receptionist will be live and answering calls within 48 hours. We will have you do a quick test call before we flip the switch so you can hear exactly how it sounds.

If you have any questions in the meantime, just reply to this email or text us at {{owner.phone}}.

We are going to make sure your phone never goes unanswered again.

Talk soon,

**{{sender.name}}**
The Call Taker
{{sender.phone}}
{{sender.email}}

---

## Email 2: We're Setting Up Your AI Receptionist

**Trigger:** Day 1 (24 hours after signup)
**From:** Wallace Dobbs <wallacemdobbs@icloud.com>
**Subject:** Your AI receptionist is almost ready

---

Hi {{contact.first_name}},

Quick update — we are in the middle of setting up your AI receptionist for {{contact.company_name}} and everything is looking great.

**Here is what we have configured so far:**

- **Your custom greeting** — callers will hear your company name and get a professional, friendly welcome every time
- **Call handling** — your AI knows your services, your hours, your service area, and how to answer the most common questions your customers ask
- **Appointment booking** — connected to your calendar so the AI can book jobs in real time while the customer is still on the phone
- **Text notifications** — you will get a text summary after every single call so you always know what is happening
- **Emergency protocol** — if a caller has a true emergency, your AI knows exactly what to do and who to contact

**What happens next:**

Tomorrow, we will reach out to schedule a quick test call. You will call your own business number, talk to the AI, and make sure everything sounds right. If you want anything tweaked, we will adjust it on the spot.

**One quick thing to do now:**

Save this number in your phone contacts: **{{notification.phone}}**

Label it "The Call Taker Notifications" — this is the number your text notifications will come from. Adding it to your contacts makes sure it does not get filtered as spam.

Almost there. You are going to love this.

Best,

**{{sender.name}}**
The Call Taker
{{sender.phone}}
{{sender.email}}

---

## Email 3: You're Live

**Trigger:** Day 2 (when system goes live after client test call)
**From:** Wallace Dobbs <wallacemdobbs@icloud.com>
**Subject:** You're live — every call is now answered

---

Hi {{contact.first_name}},

It is official. Your AI receptionist is live and answering calls for {{contact.company_name}} right now.

Every call to your business is being picked up. No more voicemails. No more missed opportunities. Your phone is covered 24 hours a day, 7 days a week.

**Here is what to expect:**

- **Text notifications** — You will receive a text after every call with a summary of who called, what they needed, and what action was taken
- **Calendar bookings** — When the AI books an appointment, it shows up directly on your calendar. You will also get a notification
- **Emergency alerts** — If someone calls with an emergency, your on-call tech will be notified immediately per the protocol we set up

**A few common first-week questions:**

**"What if someone asks something weird or unusual?"**
The AI will do its best to help based on your business information. If it cannot answer a question, it will politely take the caller's information and let them know someone will call them back. You will get a notification flagged as "needs follow-up."

**"What if I need to change my hours or add a promotion?"**
Just text or email us. We will update your AI within one business day. Seasonal changes, holiday hours, new specials — just let us know.

**"What if I want to listen to how the AI handled a call?"**
We can provide call summaries and transcripts. Just ask and we will walk you through how to access them.

**"What if I get a notification and need to call the customer back?"**
Just call them from your normal business line. The AI captured their info — you have their name and number right in the notification text.

**Your support contact:**

If anything comes up — anything at all — just reach out:

- **Reply to this email**
- **Text:** {{sender.phone}}
- **Call:** {{sender.phone}}

We are monitoring your calls closely this first week to make sure everything runs smoothly. If we notice anything that needs adjusting, we will fix it proactively.

Congratulations — you just solved your missed call problem.

Let's go,

**{{sender.name}}**
The Call Taker
{{sender.phone}}
{{sender.email}}

---

## Email 4: Your First Week Report

**Trigger:** Day 7 (7 days after go-live)
**From:** Wallace Dobbs <wallacemdobbs@icloud.com>
**Subject:** Your first week with The Call Taker — here are the numbers

---

Hi {{contact.first_name}},

You have been live for one week. Here is how your AI receptionist performed for {{contact.company_name}}:

---

**YOUR FIRST WEEK BY THE NUMBERS**

| Metric | Count |
|---|---|
| Total calls answered | {{stats.total_calls}} |
| Appointments booked | {{stats.appointments_booked}} |
| After-hours calls answered | {{stats.after_hours_calls}} |
| Emergency calls dispatched | {{stats.emergency_calls}} |
| Calls requiring follow-up | {{stats.followup_needed}} |

---

**Here is what that means for your business:**

Without The Call Taker, **{{stats.after_hours_calls}} calls** would have gone to voicemail — that is {{stats.after_hours_calls}} potential customers who might have called your competitor instead.

At your average job value of ${{contact.avg_job_value}}, those calls represent approximately **${{stats.estimated_revenue}} in recovered revenue** this week alone.

Every one of those calls was answered live. Every caller got a professional experience. Every lead was captured.

**Tips to get even more value:**

1. **Forward all your numbers.** If you have a Google Business number, a website click-to-call number, or any secondary lines that are not forwarded yet, let us know and we will set them up. Every line that rings should be answered.

2. **Update us on seasonal promotions.** Running a spring tune-up special? A discount on new installs? Tell us and we will train the AI to mention it on every call.

3. **Check your calendar integration.** Make sure booked appointments are showing up correctly. If anything looks off, let us know now and we will fix it.

4. **Let us know about holiday hours.** If your hours change for any upcoming holidays, give us a heads-up and we will adjust the AI.

---

We are going to keep watching things closely over the next week. If you have any questions, want to see call transcripts, or want to change anything about how the AI handles calls, just let us know.

How is everything feeling so far? Just hit reply and let me know.

Best,

**{{sender.name}}**
The Call Taker
{{sender.phone}}
{{sender.email}}

---

## Email 5: How's It Going + Referral Ask

**Trigger:** Day 14 (14 days after go-live)
**From:** Wallace Dobbs <wallacemdobbs@icloud.com>
**Subject:** Quick question about your experience

---

Hi {{contact.first_name}},

You are two weeks in with The Call Taker. I have a quick question:

**How is everything working for you?**

Seriously — I want to know. Is the AI handling calls the way you expected? Are the notifications helpful? Is there anything that is been bugging you that we could fix?

Just hit reply and tell me. Even if it is just "everything is great" — I would love to hear it.

---

**If you are happy with the service, I have two small asks:**

**1. Would you be willing to share a quick testimonial?**

It does not have to be long. One or two sentences about your experience is all we need. Something like:

> "Before The Call Taker, we were missing calls every day. Now every call gets answered and my calendar stays full." — {{contact.first_name}}, {{contact.company_name}}

Just reply to this email with a sentence or two and we will take care of the rest. Or if you are feeling generous, you can leave us a Google review here: {{review.link}}

**2. Know another HVAC company that is losing calls to voicemail?**

We would love to help them too. And here is the deal:

**For every company you refer that signs up with The Call Taker, we will credit your next month of service.**

That is real money back in your pocket just for spreading the word. If you know someone, just reply with their name and number and we will take it from there. We will never cold-call anyone — we will mention that you referred them and keep it low-pressure.

---

**Your 2-week numbers:**

| Metric | Count |
|---|---|
| Total calls answered | {{stats.total_calls_2wk}} |
| Appointments booked | {{stats.appointments_2wk}} |
| After-hours calls answered | {{stats.after_hours_2wk}} |
| Estimated revenue recovered | ${{stats.revenue_2wk}} |

---

Thanks for trusting us with your phones, {{contact.first_name}}. We are not going anywhere — your calls are covered.

As always, if you need anything at all:

- **Reply to this email**
- **Text:** {{sender.phone}}
- **Call:** {{sender.phone}}

Talk soon,

**{{sender.name}}**
The Call Taker
{{sender.phone}}
{{sender.email}}

---

## Sequence Summary

| Email | Day | Subject | Trigger |
|---|---|---|---|
| 1 | 0 | Welcome to The Call Taker — here's what happens next | Payment processed |
| 2 | 1 | Your AI receptionist is almost ready | 24 hours after signup |
| 3 | 2 | You're live — every call is now answered | System goes live (manual trigger) |
| 4 | 7 | Your first week with The Call Taker — here are the numbers | 7 days after go-live |
| 5 | 14 | Quick question about your experience | 14 days after go-live |

**GHL Setup Notes:**

- Emails 1, 2, 4, and 5 are time-based triggers in the workflow
- Email 3 is triggered manually (or by a tag/pipeline stage change) when the system goes live — do NOT set this on a timer since go-live timing varies
- All emails should have a "from" name of the assigned onboarding specialist or account manager, not a generic company name
- Merge fields ({{contact.first_name}}, etc.) must be mapped to the correct GHL custom fields
- Stats fields ({{stats.total_calls}}, etc.) should be pulled from the reporting dashboard and inserted manually or via Zapier/API before sending emails 4 and 5
