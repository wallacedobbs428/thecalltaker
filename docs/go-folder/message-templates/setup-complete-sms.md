# Setup Complete SMS — Send After AI Agent is Built

## Metadata

| Field     | Value                                                                  |
|-----------|------------------------------------------------------------------------|
| Subject   | n/a (SMS)                                                              |
| Channel   | SMS                                                                    |
| Trigger   | After voice agent is configured and tested (before client forwards)    |
| Max Length | 2 segments (~300 characters)                                          |

## Template

```
[FIRST NAME], your AI receptionist for [BUSINESS NAME] is built and ready to go! 🔥 Give it a call right now and hear it in action:

📞 [AI PHONE NUMBER]

Call it a few times, ask it anything a customer would. Once you're happy, we'll get your forwarding set up. Reply here when you're ready!
```

## Usage Notes

- Send only after the voice agent has been fully configured, tested internally, and passed QA.
- The client's AI phone number must be included — this is their first time hearing their own agent.
- Encourage them to test it themselves. This builds trust and excitement before going live.
- GHL automation tag trigger: `setup-complete`
- Next step after this: client confirms they like it, then you walk them through call forwarding (or send test-calls-done-sms.md after your 3 internal tests pass).
- If the client requests changes after hearing their agent, make the adjustments and resend this SMS with updated language like "Updated and ready — give it another listen!"
- Character count: ~275 characters (fits in 2 SMS segments).
