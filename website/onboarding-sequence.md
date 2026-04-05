# 24-Hour Onboarding SMS Sequence

**Trigger:** Wallace tags contact `payment-received` in GHL
**Goal:** Get call forwarding active within 24 hours. Personal touch prevents churn.
**Wire into:** GHL Automation → Trigger: Tag Added → payment-received

---

## IMMEDIATE (0 min after payment-received tag)

```
Welcome to The Call Taker, {first_name}. GIDEON goes live on your phones today. I'll call you personally within the hour to get everything set up. -Wallace
```

**GHL action:** Send SMS → contact phone

---

## 1 HOUR (if no setup call completed)

**GHL condition:** Contact does NOT have tag `setup-complete`

```
Hey {first_name} — Wallace here. Calling you now to get GIDEON live. If you miss me, here's the setup link: thecalltaker.com/setup — takes 5 minutes. -Wallace
```

**GHL action:** Send SMS → contact phone + Create Task "Call {first_name} NOW — setup incomplete"

---

## 3 HOURS (setup confirmation)

**GHL condition:** Contact does NOT have tag `setup-complete`

```
{first_name} — quick check. Did you get a chance to forward your after-hours number? One step and GIDEON is live tonight. Reply DONE when it's set up. -Wallace
```

**GHL action:** Send SMS → contact phone
**Reply handler:** If reply contains DONE/done/yes → add tag `setup-complete` → send "You're live. GIDEON is answering your phones right now. Sleep well tonight. -Wallace"

---

## 24 HOURS (first night recap)

**GHL condition:** Contact HAS tag `setup-complete`

```
Hey {first_name} — first night check-in. How many calls did GIDEON answer? Log in at thecalltaker.com/dashboard to see the full report. -Wallace
```

**GHL action:** Send SMS → contact phone

---

## DAY 3 (early win reinforcement)

**GHL condition:** Contact HAS tag `setup-complete`

```
{first_name} — 3 days in. GIDEON has answered {calls_answered} calls that would've gone to voicemail. Just wanted you to know it's working. -Wallace
```

**GHL action:** Send SMS → contact phone (pull call count from pilot state or Sam engine)

---

## TAGS USED

| Tag | Meaning |
|-----|---------|
| `payment-received` | Trigger — Wallace adds after confirming PayPal |
| `setup-complete` | Customer forwarded their number |
| `onboarding-day1` | 1-hour SMS sent |
| `onboarding-day1-check` | 3-hour check sent |
| `onboarding-recap` | 24-hour recap sent |
| `onboarding-day3` | Day 3 reinforcement sent |

---

## NOTES FOR WINDOW 3 (Engineering)

- Wire each step as a GHL Automation workflow
- Use "Wait" steps with tag conditions (not time-only)
- The DONE reply handler needs a GHL inbound message trigger filtered by `payment-received` tag
- {calls_answered} in Day 3 message: pull from pilot-state.json or Sam engine's call counter
- All SMS use GHL conversations API (same as all other engines)
- If customer replies at ANY point with a question → pause sequence + ntfy URGENT to Wallace
