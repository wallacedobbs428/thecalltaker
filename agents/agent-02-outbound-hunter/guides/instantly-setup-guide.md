# INSTANTLY.AI SETUP GUIDE — GET SENDING IN 48 HOURS
**The Call Taker | Cold Email for HVAC Companies**
**Target: 25-50 emails/day within 48 hours**

---

## IMPORTANT BEFORE YOU START

**Check the demo line FIRST:** Call (615) 784-5747 and make sure the AI voice agent sounds good. Every email you send points prospects to this number. If it's broken, DO NOT send emails. Fix the voice agent first.

**What you need:**
- Instantly.ai login credentials
- GHL login (to import leads from there OR to add replies back)
- The cold email sequences (already written — see below)
- 30 minutes of focused time

---

## PART 1: LOG IN & CHECK YOUR ACCOUNTS

### Step 1: Log into Instantly.ai
1. Go to instantly.ai
2. Log in with your credentials
3. You should see the main dashboard

**What you're looking for:** Do you already have email accounts connected? Look for a section called "Email Accounts" or "Sending Accounts" in the left sidebar.

---

### Step 2: Check Account Health
1. Click "Email Accounts" in the left sidebar
2. You should see 4 email accounts on the skylfinder.com domain

**Look for these indicators:**
- Green checkmark or "Healthy" status
- Warm-up progress (should be at least 50% complete — ideally 80%+)
- Daily sending limit (should show something like "25/day" or "50/day")

**If accounts show "Warming Up" and are under 50% complete:**
- DO NOT start sending campaigns yet
- Let them warm up for 3-5 more days
- Skip to Part 7 to set up campaigns but DON'T activate them yet

**If accounts show "Healthy" or 80%+ warm-up:**
- You're good to go
- Continue to Part 3

**If you see NO accounts or they're disconnected:**
- STOP
- You need to add email accounts first (see Part 2 below)

---

## PART 2: IF YOU NEED TO ADD EMAIL ACCOUNTS (SKIP IF ALREADY SET UP)

### Step 3: Add Sending Accounts
1. Click "Email Accounts" → "Add Account"
2. Choose your email provider (Google Workspace, Outlook, or Custom SMTP)
3. If using skylfinder.com domain: Choose "Custom SMTP"
4. Enter SMTP details (you'll need these from your domain host)

**SMTP Settings (if using skylfinder.com via standard hosting):**
- SMTP Host: mail.skylfinder.com (or check with your hosting provider)
- Port: 587 (TLS) or 465 (SSL)
- Username: your full email address (e.g., wallace@skylfinder.com)
- Password: your email password

5. Click "Connect" and test the connection
6. Enable "Warm-up Mode" — set it to 7-14 days

**Warm-up settings:**
- Start with: 5 emails/day
- Increase by: 3-5 emails/day
- Maximum: 30-50 emails/day (don't go higher)
- Reply rate simulation: ON
- Open rate simulation: ON

7. Repeat for all 4 accounts

**Important:** Don't send ANY campaigns while accounts are warming up. Wait at least 7 days.

---

## PART 3: LOAD YOUR EMAIL SEQUENCES

You have 5 city-specific cold email sequences already written. Each sequence has 3 emails spaced 3 days apart.

### Step 4: Create Your First Campaign
1. Click "Campaigns" in the left sidebar
2. Click "Create New Campaign"
3. Name it: "Birmingham AL — Missed Call Sequence"

---

### Step 5: Add Email Sequence
1. In the campaign editor, click "Add Email" or "Add Sequence Step"
2. You'll create 3 emails (one at a time)

**Email 1: The Missed Call Revenue Loss**
- **Subject:** birmingham hvac calls going to voicemail
- **Body template:**
```
Hi {{firstName}},

I called {{companyName}} at 6:47pm Thursday to test something. Straight to voicemail.

Here's the problem: you're not the only HVAC company in Birmingham. The homeowner with the broken AC isn't waiting for you to call back — they're calling your competitor.

I'm 19, and I built an AI receptionist specifically for HVAC companies. It answers every call in under 3 seconds, 24/7. {{personalizationHook}}

Call our demo line: (615) 784-5747. Hear it yourself.

Wallace
```

3. Click "Save Email"
4. Set delay: Send immediately (Email 1 has no delay)

**Email 2: The Competitor Threat**
- Click "Add Email" again
- **Subject:** your competitors are using ai now
- **Body template:**
```
{{firstName}},

Quick follow-up. I don't know if you saw my last email, but this is moving fast.

Three HVAC companies in Alabama started using AI receptionists in the last 30 days. Your competitors are answering calls while you're in a crawl space.

The Call Taker was built for HVAC. It doesn't just answer — it books appointments, handles emergencies, collects customer info, and texts you immediately.

{{personalizationHook}}

Demo line: (615) 784-5747. 2-minute call.

Wallace
```

5. Set delay: 3 days after previous email

**Email 3: The ROI Breakdown**
- Click "Add Email" again
- **Subject:** here's the math on lost calls
- **Body template:**
```
{{firstName}},

Last one from me.

Average HVAC job in Birmingham: $450. If you miss 4 calls a week, that's $93,600/year you're not even seeing.

The Call Taker costs $497/month. That's $5,964/year. One extra job per month pays for the entire year.

{{personalizationHook}}

Call (615) 784-5747. If you don't love it, no hard feelings.

Wallace
The Call Taker
```

6. Set delay: 3 days after previous email (6 days total from Email 1)

**Save the campaign** — but DON'T activate it yet.

---

### Step 6: Repeat for Other Cities
Create 4 more campaigns using the sequences from `/agents/agent-02-outbound-hunter/email-sequences/new-cities-cold-emails.md`:

1. **Louisville KY — Legacy Risk Sequence** (3 emails)
2. **Huntsville AL — Name vs Reality Sequence** (3 emails)
3. **Atlanta Suburbs GA — Growth Problem Sequence** (3 emails)
4. **Jackson MS — Weekend Opportunity Sequence** (3 emails)

**Use the exact subject lines and body copy from the sequence doc.** Just copy/paste and replace the placeholders with merge tags:
- `[Owner First Name]` → `{{firstName}}`
- `[Company Name]` → `{{companyName}}`
- `[PERSONALIZATION: "..."]` → `{{personalizationHook}}`

---

## PART 4: IMPORT YOUR LEADS

You have two options: import from GHL OR upload a CSV.

### Option A: Import from GoHighLevel (if you have leads there)
1. Log into GHL
2. Go to Contacts
3. Filter by Tag: "HVAC - Birmingham" (or whatever city you're targeting)
4. Click "Export" → Download as CSV
5. Open the CSV and make sure it has these columns:
   - First Name
   - Company Name
   - Email
   - (Optional) Phone, Website, City, State

6. Back in Instantly.ai, click "Leads" → "Import Leads"
7. Upload the CSV file
8. Map the columns:
   - Instantly "First Name" → your CSV "First Name"
   - Instantly "Company" → your CSV "Company Name"
   - Instantly "Email" → your CSV "Email"
   - Add custom field for "personalizationHook" if you have it in your CSV

9. Assign leads to campaign: Choose "Birmingham AL — Missed Call Sequence"
10. Click "Import"

### Option B: Create a CSV from scratch
If you DON'T have leads in GHL yet, create a simple CSV file:

**CSV format (open in Google Sheets or Excel):**
```
firstName,email,companyName,personalizationHook
John,john@ethridgehvac.com,Ethridge HVAC,609 Google reviews is incredible
Joseph,joseph@guinservice.com,Guin Service,Joseph you built this business from the ground up
Mike,mike@standardheating.com,Standard Heating,85 years in business since 1939
```

**Where to find leads:**
- Google Maps: Search "Birmingham HVAC" and collect company names, owners, emails
- Company websites: Look for "Contact" or "About" pages
- LinkedIn: Search for HVAC company owners in Birmingham

**Personalization hooks** (pick one per company):
- High Google review count: "Your 400+ Google reviews show you care about customers"
- Long history: "50 years in business means you know customer service matters"
- Owner name: Use their first name naturally
- Specific observation: "Saw you're closed weekends" or "I called after hours and got voicemail"

**Save as CSV** and upload to Instantly.ai (same process as Option A, step 6-10).

---

## PART 5: SET UP CAMPAIGN SETTINGS (CRITICAL)

### Step 7: Configure Daily Send Limits
1. Go back to your campaign (e.g., "Birmingham AL — Missed Call Sequence")
2. Click "Settings" or "Campaign Settings"

**Daily Send Limits:**
- If accounts are FULLY warmed (14+ days, 100% healthy): 30-50 emails/day PER account
- If accounts are 80% warmed (7-10 days): 20-25 emails/day PER account
- If accounts are 50-80% warmed: 10-15 emails/day PER account

**With 4 accounts at 25 emails/day each = 100 emails/day total** (but start with 25-50/day across ALL accounts to be safe)

**Recommended starting point:**
- Total daily emails: 25-50 (split across 4 accounts)
- Per account: 6-12 emails/day
- Increase by 10-20% per week if deliverability stays good

---

### Step 8: Set Sending Schedule
**When to send emails:**
- Monday-Friday ONLY (no weekends)
- 8:00 AM - 5:00 PM CST (HVAC owners check email during business hours)
- Spread sends throughout the day (not all at 8 AM)

**In Instantly.ai settings:**
1. Enable "Smart Sending" or "Schedule"
2. Set timezone: CST (Central Time)
3. Set sending window: 8 AM - 5 PM
4. Set days: Monday-Friday
5. Enable "Random delays" between emails (makes it look more human)

---

### Step 9: Set Up Reply Detection
**This is CRITICAL** — if someone replies, you need to STOP emailing them immediately.

1. In campaign settings, find "Reply Detection" or "Auto-pause on reply"
2. Enable "Stop sequence when lead replies"
3. Enable "Notify me of replies" → enter your email: wallacemdobbs@icloud.com
4. Enable "Mark as interested" when they reply

**What happens when someone replies:**
- Instantly.ai stops sending them emails
- You get notified
- Lead is marked "Replied" in your dashboard
- You respond manually (see Part 6 below)

---

## PART 6: ACTIVATE & MONITOR

### Step 10: Final Pre-Flight Check
Before you click "Start Campaign," check:

- [ ] Voice agent at (615) 784-5747 is working perfectly (CALL IT NOW)
- [ ] Email accounts are 80%+ warmed up (or you're willing to send at low volume)
- [ ] Sequences are loaded (3 emails each, correct spacing)
- [ ] Leads are imported (at least 10-20 per campaign to start)
- [ ] Daily send limit is set conservatively (25-50 total/day to start)
- [ ] Sending schedule is Mon-Fri, 8 AM - 5 PM CST
- [ ] Reply detection is ON
- [ ] Personalization merge tags are mapped ({{firstName}}, {{companyName}}, {{personalizationHook}})

---

### Step 11: Launch Your First Campaign
1. Go to "Birmingham AL — Missed Call Sequence"
2. Click "Start Campaign" or "Activate"
3. Confirm the settings
4. **The campaign is now LIVE**

**What happens next:**
- Instantly.ai starts sending Email 1 to your leads (spread throughout the day)
- 3 days later, Email 2 goes out (only to people who didn't reply)
- 3 days after that, Email 3 goes out
- If anyone replies, their sequence stops immediately

---

### Step 12: Monitor Daily (5 minutes/day)
**Every morning, check your Instantly.ai dashboard:**

1. **Click "Analytics" or "Dashboard"**
   - Emails sent today
   - Open rate (goal: 40-60%)
   - Reply rate (goal: 3-10%)
   - Bounce rate (goal: under 2%)

2. **Click "Replies"**
   - Read every reply
   - Categorize: Interested / Not Interested / Neutral / Question
   - Respond to interested leads FAST (within 1 hour if possible)

3. **Click "Bounces"**
   - If bounce rate is over 5%, PAUSE the campaign
   - Remove bad emails from your list
   - Check email account health

---

## PART 7: HANDLING REPLIES (THE MONEY PART)

When someone replies, you need to respond FAST and PERSONALLY. Don't use templates for replies.

### Step 13: Reply Playbook (Quick Reference)

**INTERESTED REPLY** (e.g., "Tell me more" / "How does this work?" / "What's the price?")
→ Response goal: Book a demo call
```
[First Name],

Appreciate you getting back to me.

Here's how it works: The Call Taker is an AI receptionist that answers your HVAC calls 24/7. It sounds human, books appointments into your calendar, handles emergency vs routine calls, and texts you the customer info immediately.

Easiest way to see it: call our demo line at (615) 784-5747 and ask it a few questions like a customer would.

Price is $497/month, no contract, no setup fee. Most HVAC companies book 1-2 extra jobs per month just from after-hours calls — pays for itself fast.

Want to hop on a quick 10-minute call this week? I can show you exactly how it'd work for [Company Name]. Here's my calendar: [GHL booking link]

Wallace
```

**NOT INTERESTED REPLY** (e.g., "Not interested" / "We're good" / "Remove me")
→ Response goal: Respect the no, leave door open
```
[First Name],

Totally understand — appreciate you letting me know.

If anything changes or you want to test it out down the road, the demo line's always available: (615) 784-5747.

Best of luck with the season.

Wallace
```

**QUESTION REPLY** (e.g., "How much?" / "Does it integrate with X?" / "Can it handle emergency calls?")
→ Response goal: Answer the question, then offer demo
```
[First Name],

Great question. [Answer their specific question in 1-2 sentences.]

Best way to hear it in action: call (615) 784-5747 and test it like a customer would. You'll hear exactly how it handles [their concern].

Happy to walk you through it on a quick call too if easier: [GHL booking link]

Wallace
```

**ANGRY/RUDE REPLY** (e.g., "Stop emailing me" / "How'd you get my email?")
→ Response goal: Apologize, remove immediately, stay professional
```
[First Name],

My apologies — removing you now. Won't hear from me again.

Wallace
```

---

## PART 8: DELIVERABILITY MONITORING (KEEP YOUR ACCOUNTS HEALTHY)

### Step 14: Daily Health Check (30 seconds)
**Every day, check these 3 numbers in Instantly.ai:**

1. **Bounce Rate** (goal: under 2%)
   - If 2-5%: Pause and clean your list (remove invalid emails)
   - If over 5%: STOP sending immediately, check account health

2. **Spam Rate** (goal: under 0.5%)
   - If over 1%: Your emails are hitting spam folders
   - Fix: Improve subject lines, remove spammy words, reduce volume

3. **Open Rate** (goal: 40-60%)
   - If under 30%: Subject lines aren't compelling enough
   - If over 70%: Might be spam traps or fake engagement (investigate)

---

### Step 15: Weekly Optimization (15 minutes every Friday)
**Every Friday, review your week and optimize:**

1. **Which campaign performed best?** (highest reply rate)
   - Double down on that city/sequence
   - Create similar sequences for new cities

2. **Which email in the sequence gets the most replies?**
   - Email 1, 2, or 3?
   - Consider testing a variant of that email

3. **Which subject line had the highest open rate?**
   - Use that style for future campaigns

4. **What type of replies are you getting?**
   - If mostly "not interested" → adjust your messaging
   - If mostly "how much?" → lead with ROI earlier
   - If mostly "tell me more" → you're doing great, keep going

---

## PART 9: SCALING UP (WEEKS 2-4)

### Step 16: Increase Volume Safely
**Week 1:** 25-50 emails/day (testing)
**Week 2:** If deliverability is good (bounce <2%, spam <0.5%), increase to 75-100/day
**Week 3:** If still good, increase to 100-150/day
**Week 4:** Max out at 150-200/day (50 emails/day per account)

**Never increase by more than 50% in one week.**

---

### Step 17: Expand to New Cities
Once you've sent to all leads in Birmingham, Louisville, Huntsville, Atlanta, and Jackson:

1. Research 5 new cities (see `/agents/agent-04-lead-intelligence/` for targeting criteria)
2. Build lead lists (10-20 companies per city)
3. Personalize hooks per company
4. Create new campaigns in Instantly.ai
5. Launch at 25-50/day per new city

**Target: 10-20 new cities by end of month 1 = 200-400 total HVAC leads in pipeline**

---

## PART 10: TROUBLESHOOTING

### Problem: Emails going to spam
**Symptoms:** Open rate under 20%, no replies
**Fix:**
- Remove spammy words: "free," "guarantee," "limited time," "act now"
- Shorten emails (under 100 words is safer)
- Add a plain text signature (no images, no links except one)
- Check your domain's SPF, DKIM, DMARC records (ask your email host)

### Problem: High bounce rate (over 5%)
**Symptoms:** Lots of "Email not found" errors
**Fix:**
- Use an email verification tool (NeverBounce, ZeroBounce) to clean your list
- Remove all bounced emails from future campaigns
- Don't buy email lists — find emails from company websites only

### Problem: No replies
**Symptoms:** Good open rate (40%+), but 0 replies
**Fix:**
- Your copy isn't compelling enough
- Test new subject lines (use curiosity: "saw your google reviews" vs "quick question")
- Personalize MORE (mention specific review, years in business, owner name)
- Adjust CTA (instead of "call our demo line," try "call this number and ask it a question")

### Problem: Accounts getting flagged/suspended
**Symptoms:** Instantly.ai shows "Account suspended" or "Sending disabled"
**Fix:**
- You sent too much too fast
- Pause all campaigns for 7 days
- Re-warm the accounts at 5 emails/day
- Start slower next time (don't go 0 to 50/day overnight)

---

## QUICK START CHECKLIST (DO THIS TODAY)

**Hour 1: Setup**
- [ ] Log into Instantly.ai
- [ ] Check email account health (need 80%+ warm-up)
- [ ] Create "Birmingham AL" campaign
- [ ] Load 3-email sequence (copy from `/agents/agent-02-outbound-hunter/email-sequences/new-cities-cold-emails.md`)
- [ ] Set daily limit: 25 emails/day
- [ ] Set schedule: Mon-Fri, 8 AM - 5 PM CST
- [ ] Enable reply detection

**Hour 2: Load Leads**
- [ ] Create CSV with 10-20 Birmingham HVAC companies (Google Maps search)
- [ ] Include: firstName, email, companyName, personalizationHook
- [ ] Import to Instantly.ai
- [ ] Assign to "Birmingham AL" campaign

**Hour 3: Launch**
- [ ] Call (615) 784-5747 to verify voice agent works
- [ ] Double-check all sequences, settings, merge tags
- [ ] Click "Start Campaign"
- [ ] Set reminder to check replies tomorrow morning

**Tomorrow:**
- [ ] Check Instantly.ai dashboard (5 min)
- [ ] Respond to any replies within 1 hour
- [ ] Monitor bounce rate, open rate, reply rate

**End of Week 1:**
- [ ] Review analytics (what worked, what didn't)
- [ ] Create 2nd campaign (Louisville KY)
- [ ] Increase volume to 50-75 emails/day if deliverability is good

---

## KEY METRICS TO TRACK (WRITE THESE DOWN WEEKLY)

| Metric | Week 1 | Week 2 | Week 3 | Week 4 | Goal |
|--------|--------|--------|--------|--------|------|
| Emails sent | ___ | ___ | ___ | ___ | 500+ |
| Open rate | ___% | ___% | ___% | ___% | 40-60% |
| Reply rate | ___% | ___% | ___% | ___% | 3-10% |
| Positive replies | ___ | ___ | ___ | ___ | 5+ |
| Demos booked | ___ | ___ | ___ | ___ | 1+ |
| Bounce rate | ___% | ___% | ___% | ___% | <2% |

---

## FINAL NOTES

**Remember:**
- Cold email is a NUMBERS game — 5% reply rate is GOOD (95% won't reply, and that's normal)
- Personalization is the difference between 1% and 10% reply rates
- The demo line (615) 784-5747 does the heavy lifting — your job is getting them to call it
- Speed matters — reply to interested leads within 1 hour if possible
- Don't get discouraged by "no" replies — every no gets you closer to a yes

**Target Timeline:**
- Day 1: First campaign live, 25 emails sent
- Day 7: 150+ emails sent, 3-5 replies, 1 interested lead
- Day 14: 300+ emails sent, 10+ replies, 1-2 demos booked
- Day 30: 750+ emails sent, 25+ replies, 3-5 demos booked, 1 client signed

**You got this.** Start small, stay consistent, optimize as you go.

---

## RESOURCES

**Email Sequences:** `/Users/moneymaker99/Desktop/wallace-hvac/agents/agent-02-outbound-hunter/email-sequences/new-cities-cold-emails.md`

**Reply Playbook (detailed):** Create this file at `/agents/agent-02-outbound-hunter/playbooks/reply-playbook.md` if it doesn't exist — use the examples in Part 7 above as a starting point.

**Lead Research Guide:** `/agents/agent-04-lead-intelligence/` (for finding new HVAC companies to target)

**Demo Booking Calendar:** Use GHL calendar link or create one in your GHL account (Settings → Calendars → Demo Calendar)

**Questions?** Text Wallace at [his number] or email wallacemdobbs@icloud.com.

---

**Last Updated:** 2026-02-16
**Domain:** Agent 02 — Outbound Hunter
**Output Folder:** `/agents/agent-02-outbound-hunter/guides/`
**Next Steps:** After first week of sending, create A/B test variants and expand to new cities.
