# Daily Operations — 15-Minute Morning Check

Everything you need to do every day to keep The Call Taker running smooth. This should take about 15 minutes once you get the rhythm down.

**legacy CRM Login:** [app.gohighlevel.com](https://app.gohighlevel.com)
**Location ID:** tQb9YmrGDrdVUJYPKrsY

---

## Daily Morning Routine (15 Minutes)

Do this every morning before you do anything else. Coffee first, then this.

---

### Step 1: Check ntfy Notifications from Overnight (2 min)

These are push notifications from our bots — new leads, form submissions, errors, anything that happened while you were sleeping.

1. Open the **ntfy app** on your phone (or go to [ntfy.sh](https://ntfy.sh) in a browser)
2. Check the main topic: `tct-xK9mW4vR7pLd`
3. Check the war room topic: `tct-warroom-Kx7mN9pQ`
4. Read through every notification since your last check
5. If anything looks urgent (e.g., "client call failed," "agent down"), handle it first before continuing

**What you're looking for:**
- New demo callers (someone tried the demo line)
- Form submissions from the website
- Bot errors or failures
- Lead finder results
- Anything that says "URGENT" or "ERROR"

---

### Step 2: Review Missed Calls in legacy CRM (3 min)

Any call that came in and didn't get answered needs your attention.

1. Go to [app.gohighlevel.com](https://app.gohighlevel.com) and log in
2. Look at the **left sidebar**
3. Click **"Conversations"** (it has a chat bubble icon)
4. You'll see a list of all conversations. At the top of that list, look for a **filter or search bar**
5. Click the **filter icon** (looks like a funnel, top-right area of the conversation list)
6. In the filter options, look for **"Type"** or **"Call Status"**
7. Select **"Missed"** or **"Missed Calls"**
8. Click **"Apply"** or **"Filter"**
9. You'll now see only missed calls

**For each missed call:**
- Click on the conversation to see who called
- Check if they're an existing contact or a new lead
- If they're new: make sure a contact was created (it usually is automatic)
- If they're existing: check if it's a client's customer who needs a callback
- Decide: Does someone need to call them back? If yes, do it or note it down

---

### Step 3: Check Pipeline Stages — Anyone Stuck? (3 min)

The pipeline shows where every deal/lead is in the sales process. If someone has been sitting in the same stage for too long, they need attention.

1. In the **left sidebar**, click **"Opportunities"** (it has a dollar sign or funnel icon)
2. Make sure you're looking at the right pipeline (if you have multiple, there's a dropdown at the top to switch)
3. You'll see a **Kanban board** — columns represent stages (like "New Lead," "Demo Booked," "Trial," "Active Client," etc.)
4. **Scan each column from left to right**
5. Look for any card that's been sitting in the same stage for more than a few days

**Red flags:**
- Someone in "Demo Booked" for more than 3 days — did they actually do the demo? Follow up.
- Someone in "Trial" for more than 14 days — trial should be ending, time to convert or check in.
- Someone in "Proposal Sent" for more than 5 days — they need a nudge.

**To check how long a card has been in a stage:**
1. Click on the card (the contact's name/deal)
2. A panel will open on the right side showing details
3. Look for the **"Stage Changed"** date or activity history at the bottom
4. If it's been too long, take action (send a follow-up, make a call, etc.)

---

### Step 4: Scan for New Form Submissions (3 min)

Check if anyone filled out a form on the website (demo request, contact form, etc.).

1. In the **left sidebar**, click **"Contacts"**
2. You'll see a list of all contacts
3. Click the **"Sort"** option (usually near the top of the list, or click on the column header)
4. Sort by **"Date Created"** — newest first (click the column header, or look for a sort dropdown)
5. Look at the contacts created **today and yesterday**
6. Check if any have the tags that indicate a form submission (like `demo-request`, `website-lead`, etc.)

**Alternative faster method:**
1. Click **"Contacts"** in the left sidebar
2. Click **"Smart Lists"** or **"Filters"** at the top
3. Add a filter: **"Date Created"** → **"is today"** (or "is in the last 24 hours")
4. Click **"Apply"**
5. This shows only brand-new contacts

**For each new contact:**
- Check their tags — where did they come from?
- Check if they've been contacted yet (click their name → look at activity/conversation)
- If they haven't been contacted: reach out ASAP (speed to lead matters)

---

### Step 5: Verify AI Agents Are Still Running (4 min)

Make sure every client's AI receptionist is actually turned on and working.

1. Click the **gear icon** at the bottom of the left sidebar (this is **Settings**)
2. In the Settings menu, look in the left panel for **"Conversation AI"** (it might be under a section like "AI" or you may need to scroll down)
3. Click **"Conversation AI"**
4. You'll see a list of all your AI agents
5. **For each agent**, check the **status indicator**:
   - **"Active"** (usually shown with a green dot or green text) = Good, it's running
   - **"Inactive"** or **"Paused"** (usually gray or red) = Problem, it's not answering calls
6. If any agent is NOT active:
   - Click on that agent's name
   - Look for a toggle or button that says **"Activate"** or **"Enable"**
   - Turn it on
   - Click **"Save"** if there's a save button

**If an agent won't activate:**
- Check if the phone number is still assigned (see Troubleshooting guide)
- Check if there are any error messages displayed on the agent page
- If nothing works, see the Troubleshooting doc (09-troubleshooting.md)

---

## Weekly Check (Every Monday — 30 min)

Do this every Monday morning, right after your daily check.

---

### 1. Review Each Client's Call Volume (10 min)

You want to know: Is the AI actually getting calls? If a client is paying us and getting zero calls, something is wrong (either with their forwarding or their business is slow).

1. Go to **Settings** (gear icon, bottom-left)
2. Click **"Phone Numbers"** in the Settings menu
3. You'll see all your phone numbers listed
4. For each number that belongs to an active client:
   - Note the number and which client it belongs to
5. Now go to **"Conversations"** in the left sidebar
6. Use the **search bar** at the top to search for the phone number, or filter by it
7. Count how many calls/conversations happened in the last 7 days

**Alternative method using Reporting:**
1. In the left sidebar, look for **"Reporting"** or **"Dashboard"**
2. Click it
3. Set the date range to **"Last 7 days"**
4. Look at call metrics — total calls, calls per number, etc.

**What to look for:**
- Client getting 0 calls this week → Check if call forwarding is still active on their end
- Client getting way more calls than usual → Great, but make sure AI is handling them well
- Client getting calls but lots of "missed" → AI agent might be down, check it

---

### 2. Check for Clients Approaching Monthly Review (5 min)

Every client should get a monthly check-in. Keep track of when each client started so you know when their monthly review is due.

1. Go to **"Contacts"** in the left sidebar
2. Filter by the tag **"active-client"** (or whatever tag you use for paying clients):
   - Click **"Filters"** at the top
   - Choose **"Tags"** → **"contains"** → type **"active-client"**
   - Click **"Apply"**
3. For each active client, click their name
4. Look at their **"Date Created"** or the date they became a client
5. If their monthly anniversary is this week → schedule their review (see Monthly Review Template below)

---

### 3. Update "At Risk" Clients (10 min)

At-risk = low usage, complaints, or they've hinted at canceling.

1. While you're reviewing clients, flag anyone who:
   - Had fewer than 5 calls this week (unless their business is seasonal)
   - Sent a complaint or negative message
   - Hasn't responded to your last check-in
2. For flagged contacts:
   - Go to their contact profile (Contacts → click their name)
   - Scroll down to **"Tags"**
   - Click **"+ Add Tag"**
   - Type **"at-risk"** and press Enter
   - Click **"Save"** (if needed)
3. For each at-risk client, send them a personal check-in message:
   - Go to **Conversations** → find their conversation
   - Send a friendly message asking how things are going
   - Example: "Hey [Name], just checking in — how's the AI receptionist working out for you this week? Any calls that didn't go well? I want to make sure everything is dialed in."

---

### 4. Review MRR and Pipeline Numbers (5 min)

Quick financial health check.

1. Go to **"Opportunities"** in the left sidebar
2. Count the deals in each stage — write it down or screenshot it
3. Calculate current MRR:
   - Count clients in "Active" or "Live" stage
   - Multiply by their plan price ($497 Starter or $997 Pro)
   - That's your MRR
4. Check pipeline health:
   - How many new leads this week?
   - How many demos booked?
   - How many trials started?
   - How many closed/won?

**Track these numbers every week so you can see trends.**

---

## Monthly Client Review Template

Use this for every active client, once a month.

---

### Internal Review (For You)

Fill this out before reaching out to the client:

```
Client Name: _______________
Plan: Starter ($497) / Pro ($997)
Date Started: _______________
Review Period: [Month] [Year]

CALLS THIS MONTH:
- Total calls answered by AI: ___
- Total missed calls: ___
- After-hours calls handled: ___

LEADS CAPTURED:
- New leads from calls: ___
- Appointments booked: ___
- Forms submitted: ___

ISSUES:
- Any complaints received? Y/N
  If yes, what: _______________
- Any downtime? Y/N
  If yes, when/how long: _______________
- Any script changes requested? Y/N

RECOMMENDATIONS:
- _______________
- _______________
```

---

### Client-Facing Monthly Recap (Copy-Paste This)

Copy this text, fill in the blanks, and send it to the client via email or SMS:

```
Hey [Client Name],

Here's your monthly Call Taker recap for [Month]:

Calls Answered: [NUMBER]
Your AI receptionist handled [NUMBER] calls this month, making sure every caller got a professional greeting and accurate information about your business.

Leads Captured: [NUMBER]
[NUMBER] new potential customers were captured and added to your system.

After-Hours Coverage: [NUMBER] calls
[NUMBER] calls came in outside business hours — calls that would have gone to voicemail without us.

Everything is running smoothly on our end. [ADD ANY SPECIFIC NOTE — like "We updated your holiday hours last week" or "We noticed a spike in calls on Tuesdays, which is great."]

If you want us to adjust anything — hours, the greeting script, how calls are routed — just let me know. We're here to make sure every call counts.

Talk soon,
[Your Name]
The Call Taker
```

---

### If Numbers Are Low

If the client had very few calls (under 10 in a month), don't panic. Send this version instead:

```
Hey [Client Name],

Quick monthly check-in for [Month]:

Your AI receptionist handled [NUMBER] calls this month. I want to make sure we're capturing every call — can you confirm that call forwarding is still active on your end?

A quick test: Call your business number from a different phone and make sure it rings through to our system. If it goes to your voicemail instead of us, the forwarding may have gotten reset (this happens sometimes with carrier updates).

If everything checks out and call volume is just naturally lower right now, no worries — we're here and ready whenever the calls pick up.

Let me know if you need anything adjusted.

[Your Name]
The Call Taker
```

---

## Quick Reference: What "Normal" Looks Like

So you know when to worry and when things are fine:

| Metric | Healthy | Investigate | Problem |
|--------|---------|-------------|---------|
| Daily calls per client | 3-15 | 1-2 | 0 for 3+ days |
| Missed call rate | Under 5% | 5-15% | Over 15% |
| AI agent status | Active | — | Inactive |
| Lead response time | Under 5 min | 5-30 min | Over 30 min |
| Client check-in response | Within 48 hrs | 2-5 days | No response 5+ days |

---

## End of Day (Optional but Recommended — 5 min)

Before you close the laptop:

1. Quick scan of ntfy for anything that came in during the day
2. Make sure no unread conversations are sitting in legacy CRM
3. Check that all AI agents still show "Active"
4. If anything needs attention tomorrow, send yourself a note in the war room topic:
   ```
   curl -s -d "TOMORROW: Follow up with [client name] about [issue]" https://ntfy.sh/tct-warroom-Kx7mN9pQ
   ```

That's it. 15 minutes in the morning, 5 minutes at night, and you're on top of everything.
