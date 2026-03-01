# You're Live SMS — Call Forwarding Confirmed

## Metadata

| Field     | Value                                      |
|-----------|--------------------------------------------|
| Subject   | n/a (SMS)                                  |
| Channel   | SMS                                        |
| Trigger   | After call forwarding is verified working  |
| Max Length | 2 segments (~300 characters)              |

## Template

```
[FIRST NAME], YOU'RE LIVE! 🎉 Every call to [BUSINESS NAME] is now answered by your AI receptionist — 24 hours a day, 7 days a week. No more missed calls, ever.

Try it! Call your own business number right now and hear it.

Your dashboard: https://thecalltaker.com/onboarding/live.html

We'll check in with you tomorrow to see how it's going!
```

## Usage Notes

- This is a milestone moment. The tone should be celebratory and exciting.
- Only send after verifying call forwarding is actually working — place a test call to their business number and confirm the AI picks up.
- GHL automation tag trigger: `live`
- The `live` tag also triggers the youre-live-email.md (full welcome package) and starts the check-in sequence (24hr-checkin.md at +24h, review-request.md at +14d, 1week-checkin.md at +7d, 1month-review.md at +30d).
- Dashboard link should show their call activity once live.
- The "we'll check in tomorrow" sets the expectation for 24hr-checkin.md.
- Character count: ~298 characters (fits in 2 SMS segments).
