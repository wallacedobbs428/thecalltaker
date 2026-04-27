# Review Request — Ask for Google Review at Day 14

## Metadata

| Field     | Value                                    |
|-----------|------------------------------------------|
| Subject   | n/a (SMS)                                |
| Channel   | SMS                                      |
| Trigger   | 14 days after "live" tag applied         |
| Max Length | ~160 characters (single segment ideal)  |

## Template

```
Hey [FIRST NAME]! If you're loving The Call Taker so far, would you mind leaving us a quick Google review? It really helps us out. 🙏 [GOOGLE_REVIEW_LINK]
```

## Usage Notes

- This is a soft ask. The client has been live for 2 weeks — long enough to have an opinion, not so long that the excitement has faded.
- legacy CRM automation: schedule to send 14 days after `live` tag is applied.
- **Before activating this template**: Replace [GOOGLE_REVIEW_LINK] with the actual Google Business Profile review link for The Call Taker. To get this link:
  1. Go to Google Business Profile
  2. Click "Ask for reviews"
  3. Copy the short link
- Keep this SMS as short as possible. Single-segment (160 characters) is ideal for review requests — shorter messages get higher response rates.
- Character count of template: ~155 characters (fits in 1 SMS segment, depending on review link length. Use a short link).
- Do NOT send this to clients who have reported issues or seem unhappy. Check the 24hr-checkin and 1week-checkin responses before this fires. If there are open issues, delay or skip this message.
- If the client leaves a review, tag them `reviewed` in legacy CRM so they don't get asked again.
- Timing: Send during business hours (10am-2pm local time) for best response rate. Avoid weekends.
