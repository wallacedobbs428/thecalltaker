# 3-Shot SMS Kill Sequence — The Call Taker

> Load into GHL as a 3-message workflow. Trigger: manual or tag `close-sequence`.
> Spacing: Message 1 = immediate, Message 2 = +24hrs, Message 3 = +48hrs.
> Each message includes the personalized close page URL.

---

## URL FORMAT

```
https://thecalltaker.com/close/?name={first_name}&biz={company_name}&vertical={industry}
```

Example for Greg:
```
https://thecalltaker.com/close/?name=Greg&biz=Carolina+Locksmith&vertical=locksmith
```

---

## MESSAGE 1 — THE HOOK (Day 0)

```
Hey {first_name}, this is Wallace from The Call Taker.

I built something for {company_name} — an AI receptionist that answers your phone exactly like a real employee. 24/7.

Hear it live: thecalltaker.com/close/?name={first_name}&biz={company_name_encoded}&vertical={industry}

Takes 30 seconds. Call the number on that page and tell it you need {job_word}. You'll see why I reached out.
```

**Character count:** ~340 (2 SMS segments)

---

## MESSAGE 2 — THE PAIN (Day 1, +24hrs)

```
{first_name} — quick math:

How many calls does {company_name} miss after hours? Even 2 a week at {job_value} each = {monthly_loss}/mo walking out the door.

The businesses signing up this week are locking in $97/mo — less than one missed job.

Your page is still live: thecalltaker.com/close/?name={first_name}&biz={company_name_encoded}&vertical={industry}
```

**Character count:** ~330 (2 SMS segments)

---

## MESSAGE 3 — THE CLOSE (Day 2, +48hrs)

```
Last note, {first_name}.

We're taking 10 founding customers at $97/mo. 3 spots left.

After that the price goes up and it won't come back down. No contract, cancel anytime, setup in 5 minutes.

Claim yours: thecalltaker.com/close/?name={first_name}&biz={company_name_encoded}&vertical={industry}

Either way — good luck with {company_name}. Just didn't want you to miss this.
```

**Character count:** ~320 (2 SMS segments)

---

## GHL VARIABLES

| Variable | GHL Field |
|----------|-----------|
| `{first_name}` | `{{contact.first_name}}` |
| `{company_name}` | `{{contact.company_name}}` |
| `{company_name_encoded}` | URL-encode company name (replace spaces with +) |
| `{industry}` | Contact tag matching vertical (e.g., `locksmith`, `hvac`) |
| `{job_word}` | See vertical map below |
| `{job_value}` | See vertical map below |
| `{monthly_loss}` | Calculate: job_value × 8 (2/week × 4 weeks) |

## VERTICAL MAP

| Tag | Job Word | Job Value | Monthly Loss |
|-----|----------|-----------|--------------|
| locksmith | a lockout | $150–$400 | $2,400+ |
| hvac | an HVAC repair | $300–$800 | $4,800+ |
| plumbing | a plumbing job | $250–$600 | $4,000+ |
| roofing | a roofing estimate | $500–$2,000 | $8,000+ |
| electrical | an electrical job | $200–$500 | $3,200+ |
| dental | an appointment | $200–$500 | $3,200+ |
| legal | a consultation | $300–$1,000 | $4,800+ |
| towing | a tow | $150–$400 | $2,400+ |
| pest_control | a service call | $150–$350 | $2,400+ |

---

## TOP PRIORITY SENDS

| # | Name | Business | Phone | Vertical | URL |
|---|------|----------|-------|----------|-----|
| 1 | Greg | Carolina Locksmith | (919) 608-3694 | locksmith | `close/?name=Greg&biz=Carolina+Locksmith&vertical=locksmith` |
| 2 | Pamela | Houston HVAC | (713) 367-7985 | hvac | `close/?name=Pamela&biz=Houston+HVAC&vertical=hvac` |

---

## SETUP IN GHL

1. Create workflow: **Close Sequence — 3 Shot**
2. Trigger: Contact tagged `close-sequence`
3. Step 1: Send SMS (Message 1) → Wait 24 hours
4. Step 2: Send SMS (Message 2) → Wait 24 hours
5. Step 3: Send SMS (Message 3) → Tag `close-sequence-complete`
6. Tag all 35 hot leads with `close-sequence` to fire it
