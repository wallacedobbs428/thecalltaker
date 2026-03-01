# 1-Month Performance Review — 30 Days After Going Live

## Metadata

| Field   | Value                                          |
|---------|-------------------------------------------------|
| Subject | Your First Month Report \| The Call Taker        |
| Channel | Email                                          |
| Trigger | 30 days after "live" tag applied               |

## Template

```
Hey [FIRST NAME],

You've been live with The Call Taker for a full month now — and we've got your numbers. Here's how your AI receptionist performed for [BUSINESS NAME]:

━━━━━━━━━━━━━━━━━━━━━━
YOUR FIRST MONTH BY THE NUMBERS
━━━━━━━━━━━━━━━━━━━━━━

📞 Total calls answered: [TOTAL_CALLS]
📋 Leads captured: [LEADS_CAPTURED]
🌙 After-hours calls handled: [AFTER_HOURS_CALLS]
⏱️ Average answer time: under 1 second

That's [AFTER_HOURS_CALLS] calls that would have gone to voicemail before The Call Taker. Every one of those is a potential customer who got a live answer instead of a beep.

HOW DOES THAT FEEL?

Take a second and think about it — every single call to [BUSINESS NAME] was answered this month. No missed calls. No voicemail. No "sorry I missed your call" callbacks. Just instant, professional answers, 24/7.

ANYTHING YOU'D LIKE TO CHANGE?

After a full month of data, this is a great time to fine-tune:

- Want to update your greeting for the season?
- Need to add or remove services?
- Want to change how your AI handles specific types of calls?
- Notification preferences working well?

Just reply to this email or text us at (615) 784-5747. We'll make any changes same-day.

WANT TO DO EVEN MORE?

[--- Include this section ONLY for Starter plan clients ---]

You're currently on the [PLAN NAME] plan. Our Pro plan includes everything you have now, plus:
- Custom call scripts for different scenarios
- Priority support with same-hour response
- Advanced analytics and weekly reports
- Multi-location support

Interested? Just reply "tell me more" and we'll break it down for you. No pressure at all.

[--- End conditional section ---]

SPREAD THE WORD

If The Call Taker has been good for [BUSINESS NAME], we'd really appreciate you telling another business owner about us. When they sign up and mention your name, you get a free month. Simple as that.

👉 thecalltaker.com

Looking forward to another great month,
Wallace & Mills — The Call Taker Team

📧 wallacemdobbs@icloud.com
📞 (615) 784-5747
```

## Usage Notes

- This is a data-driven retention email. The numbers do the selling.
- GHL automation: schedule to send 30 days after `live` tag is applied.
- **Before sending**: The stat placeholders ([TOTAL_CALLS], [LEADS_CAPTURED], [AFTER_HOURS_CALLS]) must be populated with real data from the client's call logs. Do not send this email with placeholder text.
- Data sources for stats:
  - Total calls: GHL contact activity log filtered by AI phone number
  - Leads captured: Contacts created with client's tag in the past 30 days
  - After-hours calls: Calls received outside client's stated business hours
- The conditional upsell section should only be included for Starter ($497/mo) clients. Pro clients ($997/mo) should get the email without that section.
- If the numbers are low (e.g., under 10 total calls), adjust the tone. Don't celebrate "3 calls answered" the same way you'd celebrate 150. Acknowledge it and offer to help with call volume strategies.
- The referral ask is stronger here than in previous emails — by day 30, they've seen the value.
- This email should trigger a recurring monthly review. Set up a 30-day loop after this first one.
