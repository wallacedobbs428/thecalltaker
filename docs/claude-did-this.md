# What Claude Built in GoHighLevel
**Date:** February 13, 2026

Everything below was created programmatically via the GHL API.

---

## Tags Created (11 new)
| Tag | Purpose |
|-----|---------|
| prospect | New HVAC company lead |
| demo-booked | Prospect has a demo scheduled |
| demo-completed | Demo was held |
| proposal-sent | Pricing proposal sent |
| active-client | Paying client |
| churned | Former client |
| referral | Came from a referral |
| cold-outreach | Added via cold outreach |
| follow-up-needed | Needs manual follow-up |
| hot-lead | High interest, needs fast response |
| voicemail-detected | Secret shopper confirmed they go to voicemail |

**Total tags now: 16** (5 existing + 11 new)

---

## Custom Fields Created (6 new)
| Field | Key | Type | Purpose |
|-------|-----|------|---------|
| Number of Trucks | contact.number_of_trucks | TEXT | Size of their fleet |
| Service Area | contact.service_area | TEXT | Geographic coverage |
| Biggest Challenge | contact.biggest_challenge | LARGE_TEXT | Main pain point |
| Demo Date | contact.demo_date | TEXT | When demo was/will be held |
| Secret Shopper Result | contact.secret_shopper_result | TEXT | Voicemail / Answered / No Answer |
| Plan Interest | contact.plan_interest | TEXT | Starter / Professional / Enterprise |

**Total custom fields now: 7** (1 existing + 6 new)

---

## Email Templates Created (10 new)
| Template | ID | Purpose |
|----------|-----|---------|
| Cold Outreach - Pain Email | 698f98315b8f473b21b7ca28 | Email 1 of cold sequence |
| Cold Outreach - Value Email | 698f98651823a03392c4c853 | Email 2 of cold sequence |
| Cold Outreach - Urgency Email | 698f986634468a8924d9d06c | Email 3 of cold sequence |
| Welcome Email 1 - Getting Started | 698f9866205de077601ef607 | Client onboarding |
| Welcome Email 2 - Setup in Progress | 698f9867045f70131b48406d | Client onboarding |
| Welcome Email 3 - You Are Live | 698f9868ba24ed9509eac1ee | Client onboarding |
| Welcome Email 4 - First Week Report | 698f98690503bce74f17b59b | Client onboarding |
| Welcome Email 5 - Referral Ask | 698f986ae76f01d35c37ddc8 | Client onboarding |
| Demo Follow-up | 698f986aedcae5108a4cdc39 | After demo is completed |
| Proposal Follow-up | 698f986bd2c7997b8f317272 | After proposal is sent |

**Total email templates now: 14** (4 existing + 10 new)

NOTE: Templates are created as shells. Wallace needs to open each one in GHL's email builder and paste in the copy from the sales/ and onboarding/ folders.

---

## Calendars Created (1 new)
| Calendar | ID | Duration | Purpose |
|----------|-----|----------|---------|
| Book a Demo - The Call Taker | UBlYxbB3HE7Buv5huiA9 | 15 min | Prospect demo booking |

**Total calendars now: 6** (5 existing + 1 new)

NOTE: Wallace needs to configure the calendar's availability hours in GHL UI.

---

## What the API CANNOT Do (Wallace Must Do Manually)
- Create or edit pipeline stages (scope restricted)
- Create or edit workflows/automations
- Configure Conversation AI / voice agent
- Edit email template HTML content (only create empty shells)
- Configure calendar availability/hours
- Connect custom domain
- Set up Stripe billing
- Configure form fields and webhooks
