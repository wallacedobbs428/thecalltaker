# Step 2: Send the Intake Form

The client is in GHL. Now you need their business info (hours, services, how they want calls handled) before you can build their AI agent. The intake form collects all of this.

---

## Click-by-click: Send the form link via SMS

1. In GHL, look at the **left sidebar** and click the **chat bubble icon** labeled **"Conversations"**
2. You'll see a list of conversations. In the **search bar at the top**, type the client's name or phone number
3. Click on their conversation to open it
4. At the bottom of the conversation, you'll see a message input box. Above it or next to it, there are channel tabs: **SMS**, **Email**, **WhatsApp**, etc.
5. Make sure **"SMS"** is selected (click on it if it isn't). This is important -- email might get buried, but they'll see a text immediately
6. Click inside the message box and **copy-paste this exact message** (then replace [FIRST NAME] with their actual first name):

```
Hey [FIRST NAME]! Welcome to The Call Taker!

To get your AI receptionist set up, fill out this quick form -- takes about 5 minutes:

https://thecalltaker.com/onboarding/intake.html

Once you submit it, we'll have your AI answering calls within 2 hours. Let me know if you have any questions!
```

7. Double-check the message looks right and the link is correct
8. Click **"Send"** (the blue/green send button, or press Enter)

---

## If they don't fill it out: follow-up messages

People get busy. Don't let this stall your onboarding.

### After 30 minutes -- no submission

Go back to their conversation in GHL and send this:

```
Hey [FIRST NAME], just checking in -- did you get a chance to fill out the setup form? The sooner we get your info, the sooner your AI starts catching calls: https://thecalltaker.com/onboarding/intake.html
```

### After 2 hours -- still nothing

Send this:

```
[FIRST NAME] -- I want to make sure we get you set up today. If you're having trouble with the form, just text me the info and I'll fill it out for you. I need: your business hours, services you offer, your business phone number, and any special instructions for how calls should be handled.
```

### If they call or text back with questions instead of filling out the form

This happens a lot. Don't get frustrated. Here's how to handle it:

1. Answer their question directly
2. Then redirect them: "Great question! You can include that info in the setup form too -- it takes about 5 min: https://thecalltaker.com/onboarding/intake.html"
3. If they flat-out refuse to do the form or say they'd rather just tell you: **collect the info yourself over text or phone.** You need at minimum:
   - Business name (exactly how they want the AI to say it)
   - Business hours (every day)
   - Services they offer
   - Business phone number (the one customers call)
   - How fast they can call back (e.g., "within 15 minutes")
   - Whether they have an on-call tech for emergencies
   - Whether the AI should give pricing info or not
   - Their service area (cities, zip codes, or radius)
   - A name for the AI receptionist (or just use "Jessica")

---

## Where to find their submission once they fill it out

The intake form at `https://thecalltaker.com/onboarding/intake.html` submits data via webhook. Here's how to find it:

**Option A: Check their GHL contact profile**
1. Go to **Contacts** (person icon in left sidebar)
2. Search for the client
3. Click their name
4. Look in the **Activity** tab or **Notes** section -- the form data may appear as a note or activity entry (depends on how the webhook is set up)

**Option B: Check GHL form submissions**
1. Click the **gear icon** at the bottom of the left sidebar to go to **Settings**
2. In the left panel, look for **"Integrations"** or **"Webhooks"**
3. Click it and look for recent incoming webhook data from the intake form

**Option C: Check ntfy notifications**
If the form is set up to send a notification to the `tct-xK9mW4vR7pLd` ntfy topic, you'll get a push notification on your phone when someone submits.

---

## Common mistakes

**Sending the form link via Email instead of SMS.**
Most clients will see a text within minutes but might not check email for hours. Always send SMS first. You can send an email backup too if you want, but SMS is primary.

**Not following up.**
If you send the form and then walk away for 3 hours, you just lost momentum. The client was excited when they paid -- capture that energy. Follow up at 30 min and 2 hours.

**Sending the wrong form link.**
The intake form URL is: `https://thecalltaker.com/onboarding/intake.html`
NOT the demo page, NOT the portal, NOT the live page. Double-check before sending.

---

## What happens next

Once you have their form submission (or the info they gave you over text/phone), move on to [Step 3: Set Up the AI Voice Agent](03-setup-voice-agent.md).
