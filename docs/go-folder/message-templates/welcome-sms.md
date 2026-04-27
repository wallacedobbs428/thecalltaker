# Welcome SMS — Send Immediately After Payment

## Metadata

| Field     | Value                                |
|-----------|--------------------------------------|
| Subject   | n/a (SMS)                            |
| Channel   | SMS                                  |
| Trigger   | Immediately after payment confirmed  |
| Max Length | 2 segments (~300 characters)        |

## Template

```
Hey [FIRST NAME]! Payment received — welcome to The Call Taker! 🎉 We're pumped to get [BUSINESS NAME] set up. Your intake form is headed to your inbox right now. Fill it out and your AI receptionist will be live within 2 hours. Let's go!
```

## Usage Notes

- Send immediately upon payment confirmation in legacy CRM.
- This is the very first touchpoint after purchase — tone should be high-energy and reassuring.
- If payment comes in after business hours, the SMS still sends immediately. The 2-hour SLA begins when they submit the intake form, not when they pay.
- legacy CRM automation tag trigger: `payment-confirmed`
- Ensure the welcome email (welcome-email.md) fires within 5 minutes of this SMS.
- Character count: ~243 characters (fits in 2 SMS segments).
