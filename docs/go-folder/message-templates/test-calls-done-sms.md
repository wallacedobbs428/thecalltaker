# Test Calls Complete SMS — All 3 Tests Passed

## Metadata

| Field     | Value                                |
|-----------|--------------------------------------|
| Subject   | n/a (SMS)                            |
| Channel   | SMS                                  |
| Trigger   | After all 3 test calls pass          |
| Max Length | 2 segments (~300 characters)        |

## Template

```
[FIRST NAME], great news — all 3 test calls passed! Your AI sounds awesome and it's handling [BUSINESS NAME] calls like a pro. 💪

Last step: activate call forwarding so real calls start going to your AI. It takes about 60 seconds.

Want me to walk you through it right now, or would you rather do a quick call? Just reply here!
```

## Usage Notes

- Send after completing 3 internal test calls that cover: a standard service inquiry, an after-hours call, and an edge case (e.g., wrong number or unusual request).
- The 3-test standard is our QA bar. Do not send this message until all 3 pass cleanly.
- GHL automation tag trigger: `tests-passed`
- Offer both self-service and guided options for call forwarding. Most clients prefer a quick walkthrough.
- Common forwarding instructions by carrier:
  - **AT&T / T-Mobile**: Dial `*61*[AI PHONE NUMBER]#` then press call
  - **Verizon**: Dial `*71[AI PHONE NUMBER]` then press call
  - **Landline / VoIP**: Varies — walk them through their provider's admin panel
- If the client wants to do it themselves, send the relevant forwarding instructions as a follow-up SMS.
- Character count: ~295 characters (fits in 2 SMS segments).
