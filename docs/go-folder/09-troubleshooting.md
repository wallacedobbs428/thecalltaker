# Troubleshooting — Fix Common Problems

When something breaks, find the problem below and follow the fix. Every fix is click-by-click.

**GHL Login:** [app.gohighlevel.com](https://app.gohighlevel.com)
**Location ID:** tQb9YmrGDrdVUJYPKrsY

---

## Problem 1: AI Isn't Answering Calls

The phone rings but the AI never picks up. Calls go to voicemail or just ring out.

### Check A: Is the AI Agent Active?

1. Log into [app.gohighlevel.com](https://app.gohighlevel.com)
2. Click the **gear icon** at the bottom of the left sidebar (this opens **Settings**)
3. In the Settings left panel, scroll down and click **"Conversation AI"**
4. You'll see a list of all your AI agents
5. Find the agent for the client whose calls aren't being answered
6. Look at the **status** next to the agent name
   - If it says **"Active"** with a green indicator → The agent is on. Move to Check B.
   - If it says **"Inactive"** or **"Paused"** or has a gray/red indicator → This is the problem.

**Fix:** Click on the agent name to open it. Look for a **toggle switch** or **"Activate" button** (usually at the top right of the agent page). Flip it to Active/On. Click **"Save"** if prompted.

---

### Check B: Is a Phone Number Assigned to the Agent?

An agent can be "Active" but if no phone number is connected to it, calls won't reach it.

1. Stay in **Settings** (gear icon, bottom of left sidebar)
2. Click **"Phone Numbers"** in the Settings left panel
3. You'll see a list of all phone numbers in the account
4. Find the phone number that belongs to this client
5. Click on that phone number
6. Look for where it says which **agent, workflow, or user** the number is assigned to
7. If it's **not assigned to the correct AI agent** → This is the problem.

**Fix:**
1. Click the phone number to open its settings
2. Look for an assignment option — it might say **"Forward to"**, **"Assign to"**, or **"Connected Agent"**
3. Select the correct AI agent from the dropdown
4. Click **"Save"**

---

### Check C: Is Call Forwarding Still Active on the Client's End?

Even if everything is perfect in GHL, if the client's phone company isn't forwarding calls to us, nothing will work.

1. Call the **client's business phone number** from your personal phone
2. Listen to what happens:
   - If you hear the AI greet you → Forwarding works. Problem is elsewhere.
   - If you hear the client's personal voicemail → Forwarding is off.
   - If it just rings and rings → Forwarding is off or broken.

**Fix:** Contact the client and have them re-do call forwarding:
- **Most carriers:** Pick up the business phone, dial `*72` then the forwarding number (our number), then press Call. Wait for confirmation tone.
- **T-Mobile/some others:** Dial `**21*[our number]#` and press Call.
- **To cancel forwarding** (for testing): Dial `*73` and press Call.

Tell the client: "Pick up your business phone, dial star-seven-two, then dial [our number], and press call. You should hear a confirmation beep or message."

---

## Problem 2: AI Says the Wrong Business Name

The AI answers and says "Thank you for calling Smith Plumbing" but the client is Johnson Plumbing.

### Fix:

1. Click the **gear icon** (bottom of left sidebar) to open **Settings**
2. Click **"Conversation AI"** in the Settings left panel
3. Find the agent that's saying the wrong name
4. **Click on the agent's name** to open it
5. You'll see the agent's configuration page. Look for the section labeled **"Instructions"**, **"Prompt"**, **"Script"**, or **"System Message"** — this is the big text box that tells the AI how to behave
6. Use **Ctrl+F** (or Cmd+F on Mac) to search for the wrong business name in the text
7. **Replace every instance** of the wrong name with the correct name
8. Scroll through the entire script to make sure you caught them all
9. Click **"Save"** (button at the top right or bottom of the page)
10. **Test it:** Call the number to confirm the AI now says the right name

---

## Problem 3: AI Gives Wrong Hours/Services/Pricing

The AI tells callers the business is open on Sundays when it's not. Or says they do a service they don't offer. Or quotes the wrong price.

### Fix:

Same process as Problem 2 — you're editing the agent's instructions.

1. **Settings** (gear icon) → **"Conversation AI"**
2. Click the agent that has wrong info
3. Find the **Instructions/Prompt/Script** text box
4. Search for the incorrect information:
   - For hours: Look for "hours", "open", "close", "schedule", days of the week
   - For services: Look for "services", "offer", "provide", or the specific wrong service name
   - For pricing: Look for "$", "price", "cost", "rate", or specific dollar amounts
5. **Update the information** to what's correct
6. Click **"Save"**
7. **Test it:** Call the number and ask about whatever was wrong to confirm the fix

**Pro tip:** When you update a client's info, do a full read-through of the entire script. If one thing was wrong, there might be other outdated info too.

---

## Problem 4: Client Isn't Getting Text Notifications

The AI answers calls, but the client never gets a text or email telling them about the call.

### Check A: Is the Client's Phone Number Correct?

1. Click **"Contacts"** in the left sidebar
2. Search for the client's name in the search bar at the top
3. Click on their name to open their contact profile
4. Check the **Phone** field — is the number correct? Right area code? No typos?
5. If it's wrong:
   - Click the **phone number field** to edit it
   - Type the correct number
   - Click **"Save"** or click outside the field to save

---

### Check B: Is the Notification Workflow Active?

Notifications are sent by automated workflows. If the workflow got turned off, no notifications go out.

1. Click **"Automations"** in the left sidebar (might also be called **"Workflows"**)
2. You'll see a list of all workflows
3. Find the workflow that handles notifications for this client (it might be named something like "Call Notification," "New Call Alert," or include the client's name)
4. Look at the **status** column:
   - **"Active"** or **"Published"** (green) → Workflow is running. Problem is elsewhere.
   - **"Draft"**, **"Inactive"**, or **"Paused"** (gray/yellow) → This is the problem.

**Fix:**
1. Click on the workflow name
2. Look for a **toggle switch** at the top right of the workflow builder, or a **"Publish"** / **"Activate"** button
3. Turn it on / click Publish
4. If it asks "Are you sure?" click **"Yes"** or **"Confirm"**
5. The status should now show Active/Published

---

## Problem 5: Contact Was Created but No Tags Applied

A new contact appeared in GHL but they don't have the right tags (like `demo-request` or `water-damage` or the client's vertical tag).

### Fix: Manually Add Tags

1. Click **"Contacts"** in the left sidebar
2. Find the contact — use the search bar to search by name, email, or phone number
3. Click on the **contact's name** to open their profile
4. Scroll down on the contact detail page until you see **"Tags"**
5. Click **"+ Add Tag"** or click in the tags area
6. Type the tag name you want to add (e.g., `demo-request`, `hvac`, `water-damage`, `active-client`)
7. If the tag already exists in the system, it will show up as a suggestion — click it
8. If it's a new tag, type the full name and press **Enter** to create it
9. Repeat for all tags that should be on this contact
10. Click **"Save"** if there's a save button (some versions auto-save)

**Common tags to check:**
- Industry tag: `hvac`, `plumbing`, `roofing`, `electrical`, `dental`, `medspa`, `legal`, `property-management`, `restoration`, `veterinary`, `locksmith`, `garage-door`, `towing`, `funeral`
- Status tags: `active-client`, `customer`, `demo-request`, `trial`, `cold-outreach`
- Source tags: `website-lead`, `referral`, `cold-lead`

---

## Problem 6: Client Says Calls Go to Voicemail Sometimes

Some calls get answered by the AI, but others go to the client's personal voicemail. It's inconsistent.

### Why This Happens:

The client's carrier is using **"conditional" call forwarding** instead of **"unconditional" call forwarding**.

- **Conditional forwarding** = only forwards when the client doesn't answer (after 15-25 seconds of ringing). Sometimes the phone picks up on the client's end first, sometimes the forwarding kicks in. It's unreliable.
- **Unconditional forwarding** = every single call gets forwarded immediately. No ringing on the client's phone at all. This is what we want.

### Fix Option 1: Set Up Unconditional Forwarding

Have the client do this from their business phone:

**For most carriers (AT&T, Verizon):**
1. Pick up the phone
2. Dial `*72`
3. Then dial our number (the number we gave them to forward to)
4. Press Call
5. Wait for a confirmation tone or message
6. Hang up

**For T-Mobile:**
1. Pick up the phone
2. Dial `**21*[our number]#`
3. Press Call
4. Wait for confirmation

**For Sprint/Other:**
1. Pick up the phone
2. Dial `*72[our number]`
3. Press Call

### Fix Option 2: Client Calls Their Carrier

If the dial codes don't work or you're not sure which carrier they have:

Tell the client: "Call your phone carrier's customer service. Tell them: 'I want to set up unconditional call forwarding on my business line to [our number]. I want ALL calls forwarded, not just unanswered calls.' They'll set it up for you."

### How to Verify It's Working:

1. Have the client confirm they set up forwarding
2. Call their business number from YOUR phone
3. The AI should pick up within 2-3 rings
4. Do this 3 times at different times — morning, afternoon, evening
5. If all 3 reach the AI, forwarding is solid

---

## Problem 7: AI Sounds Robotic/Unnatural

The AI answers but sounds stiff, awkward, or clearly like a robot. Callers are hanging up or getting put off.

### Fix A: Improve the Agent Prompt

1. **Settings** (gear icon) → **"Conversation AI"**
2. Click the agent that sounds bad
3. Find the **Instructions/Prompt/Script** section
4. Make these changes to the text:

**Use contractions:** Change "I am" to "I'm", "we will" to "we'll", "do not" to "don't", "it is" to "it's"

**Shorter sentences:** Break up any long sentences. If a response is more than 2 sentences, cut it down.

**Add personality cues at the top of the prompt.** Add something like:
```
You are a friendly, natural-sounding receptionist. Speak casually and warmly, like you're talking to a neighbor. Use short sentences. Don't over-explain. If you don't know something, say "Let me have someone get back to you on that" instead of giving a long disclaimer.
```

**Remove formal language:** Delete phrases like "Thank you for your inquiry" or "We appreciate your call." Replace with "Hey, thanks for calling!" or "No problem at all!"

5. Click **"Save"**
6. Call and test

### Fix B: Adjust Voice Settings

1. While you're on the agent page, look for **"Voice"** settings — it might be a tab, a section, or a dropdown
2. If available, try:
   - **Change the voice** to a different option (some sound more natural than others)
   - **Adjust speed** — if the AI talks too fast or too slow, tweak it
   - **Adjust pitch** — a slightly lower pitch often sounds more natural
3. Click **"Save"**
4. Call and test again

---

## Problem 8: GHL Won't Load / 403 Error / Cloudflare Error

You're trying to access GHL and getting an error page instead of the app.

### If This Happens in a Web Browser:

1. **Try refreshing the page** — press F5 or Cmd+R
2. **Clear your browser cache:**
   - Chrome: Click the three dots (top right) → **"Settings"** → **"Privacy and security"** → **"Clear browsing data"** → Check "Cached images and files" → Click **"Clear data"**
   - Safari: Click **"Safari"** in the menu bar → **"Settings"** → **"Privacy"** → **"Manage Website Data"** → search for "gohighlevel" → **"Remove"**
3. **Try incognito/private mode:**
   - Chrome: Cmd+Shift+N
   - Safari: Cmd+Shift+N
4. **Try a different browser** entirely (if you're in Safari, try Chrome, or vice versa)
5. **Check if GHL is down for everyone:** Go to [status.gohighlevel.com](https://status.gohighlevel.com) or search Twitter for "GoHighLevel down"

### If This Happens with API Calls (Python/Code):

This is a **Cloudflare block**. GHL's Cloudflare protection blocks requests that look like bots.

**The fix:** Every API call to GHL MUST include a custom User-Agent header.

```python
headers = {
    "Authorization": "Bearer pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35",
    "User-Agent": "TheCallTaker/1.0",
    "Content-Type": "application/json"
}
```

**Without the User-Agent header, you will get a 403 Forbidden error every time.** Python's default urllib User-Agent is banned by Cloudflare. Always include `"User-Agent": "TheCallTaker/1.0"` in every request.

If you're using `curl`, add the header:
```bash
curl -H "Authorization: Bearer YOUR_KEY" -H "User-Agent: TheCallTaker/1.0" https://services.leadconnectorhq.com/...
```

---

## Problem 9: Pipeline Card Won't Move / Can't Drag

You're trying to drag a card from one pipeline stage to another and it won't move. The card snaps back to where it was.

### Fix A: Refresh and Try Again

1. Press **F5** or **Cmd+R** to refresh the page
2. Wait for the page to fully load (give it 5-10 seconds)
3. Try dragging the card again — click and hold, then drag slowly to the new column

### Fix B: Move the Card Manually (Skip Dragging)

If dragging keeps failing, just change the stage from inside the card:

1. **Click on the card** (the contact/deal name) — don't try to drag, just click
2. A detail panel will open on the right side
3. Look for a field called **"Stage"** or **"Pipeline Stage"**
4. Click the **dropdown** next to Stage
5. Select the stage you want to move the card to
6. The card will automatically move to that column
7. Close the detail panel (click X or click outside it)

### Fix C: Browser Issue

If nothing works:
1. Try a different browser
2. Clear your cache (see Problem 8 instructions)
3. If still broken, GHL might be having issues — check [status.gohighlevel.com](https://status.gohighlevel.com)

---

## Problem 10: Client Wants to Cancel

Someone wants to stop their subscription. Here's exactly what to do.

### Step 1: Don't Panic. Ask Why.

Before doing anything in the system, have a real conversation:

- "I'm sorry to hear that. Can I ask what's not working for you?"
- Listen. Really listen.
- Common reasons: Not enough calls, AI makes mistakes, they found another service, budget issues, they don't see the value.

### Step 2: Try to Save the Account

Based on their reason:

| Their Reason | Your Response |
|---|---|
| "Not enough calls" | "Let me check your call forwarding — sometimes it gets reset. Let's make sure every call is actually reaching us." |
| "AI makes mistakes" | "I can fix that today. What specifically did it get wrong? I'll update the script right now." |
| "Too expensive" | "Would a lower tier work? We can adjust the plan to fit your budget." |
| "Don't see the value" | "Can I show you the numbers? Here's how many calls we've handled for you..." |
| "Found another service" | "No hard feelings. Can I ask what they're offering that we aren't? I want to learn." |

### Step 3: If They Still Want to Cancel

Be gracious. Don't guilt-trip or argue. Here's the process:

**A. Update their contact tags:**
1. Go to **Contacts** → search for the client → click their name
2. Scroll down to **Tags**
3. **Remove** these tags (click the X next to each):
   - `live`
   - `active-client`
   - `customer`
4. **Add** this tag:
   - Click **"+ Add Tag"**
   - Type `churned`
   - Press Enter
5. Save if prompted

**B. Move their pipeline card:**
1. Go to **Opportunities** in the left sidebar
2. Find their card
3. Click on the card
4. Change the **Stage** dropdown to **"Churned"** (or whatever your last stage is called)
5. Close the panel

**C. Turn off their call forwarding:**
Contact the client and have them cancel forwarding:
- Most carriers: Pick up the phone, dial `*73`, press Call
- T-Mobile: Dial `##21#`, press Call
- Or: "Call your carrier and tell them to remove call forwarding."

**D. Deactivate their AI agent (but don't delete it):**
1. **Settings** → **Conversation AI**
2. Find their agent
3. Click the agent name
4. Find the **Activate/Deactivate toggle** and turn it **OFF**
5. Click **Save**

**DO NOT delete the contact or the agent.** Keep everything in the system. If they want to come back in 3 months, you can reactivate everything in 5 minutes instead of rebuilding from scratch.

**E. Send a gracious goodbye:**
```
Hey [Client Name],

I've gone ahead and deactivated your account. Call forwarding should be turned off on your end now too.

It was great working with you. If anything changes down the road or you want to try us again, everything is saved — we can get you back up and running in no time.

Wishing you the best,
[Your Name]
The Call Taker
```

---

## Quick Diagnostic Checklist

When something's broken and you don't know what, run through this:

```
[ ] AI agent is Active (Settings → Conversation AI)
[ ] Phone number is assigned to the agent (Settings → Phone Numbers)
[ ] Call forwarding is working (call the business number yourself)
[ ] Notification workflow is Active (Automations)
[ ] Contact has correct tags (Contacts → click contact → Tags)
[ ] Client's phone/email is correct in their profile
[ ] GHL is not down (status.gohighlevel.com)
[ ] API calls include User-Agent header (for code issues)
```

If you've checked all of these and it's still broken, screenshot the problem and send it to the war room:
```
curl -s -d "BUG: [describe the problem] — checked all diagnostics, can't figure it out" https://ntfy.sh/tct-warroom-Kx7mN9pQ
```
