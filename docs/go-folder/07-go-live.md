# Step 7: Go Live

All 3 tests passed. Call forwarding is set up. Time to flip the switch and make it official.

---

## 1. Confirm with the client

Open legacy CRM > **Conversations** (chat bubble in left sidebar) > find the client.

Send this text (SMS):

```
Great news -- your AI receptionist is set up and sounds perfect! I just ran 3 test calls and everything passed. Ready to go live? I'll walk you through activating call forwarding -- takes about 2 minutes.
```

**Wait for their response.** Don't proceed until they say "yes" or "ready" or "let's do it." This is their business line -- you need their explicit green light.

---

## 2. Walk them through call forwarding

If you haven't done the forwarding step yet:

1. Ask what carrier they use
2. Send them the matching instructions from [05-setup-forwarding.md](05-setup-forwarding.md)
3. Wait for them to confirm they did it

If forwarding is already set up from Step 5, skip to step 3 below.

---

## 3. Verify forwarding is active

Once they confirm forwarding is done:

1. Pick up your personal phone
2. Call the client's **BUSINESS phone number** (NOT the AI number -- the number their customers call)
3. The AI should answer with the client's business name greeting
4. If it works: tell them "It's live! I just called your business number and your AI answered perfectly."
5. If it doesn't work:
   - Have them re-do the forwarding code (they may have dialed it wrong)
   - Make sure they used the full 10-digit AI number
   - Make sure they pressed "Call" after dialing the code
   - Wait 2-3 minutes and try again (sometimes it takes a moment to activate)
   - If it still doesn't work: check the carrier-specific instructions in [05-setup-forwarding.md](05-setup-forwarding.md)

---

## 4. Tag them as "live" in legacy CRM

1. In legacy CRM, click **"Contacts"** (person icon in left sidebar)
2. Search for the client and click on their name
3. Scroll down to the **"Tags"** section on their profile
4. Click inside the tags field and type: `live` -- press **Enter**
5. Type: `active-client` -- press **Enter**
6. (Optional but recommended) Remove the `payment-confirmed` tag:
   - Find the `payment-confirmed` tag chip/badge
   - Click the **X** on it to remove it
   - This keeps your tags clean -- they're no longer "just paid," they're "live"
7. Click **"Save"** at the bottom of the profile

---

## 5. Move them in the pipeline (if you have one set up)

If you've built a pipeline in legacy CRM:

1. In the left sidebar, click **"Opportunities"** (it might show as a dollar sign icon or "Pipeline")
2. Find the pipeline called "Client Lifecycle" or whatever you named it
3. Look for the client's card/deal -- it should be in a "Paid" or "Onboarding" stage
4. **Drag the card** to the **"Live / Active"** stage
5. If you don't have a pipeline set up yet, skip this -- it's not critical right now

---

## 6. Send the "You're Live" messages

### Automated (if automations are built)

If you've built a legacy CRM automation that triggers when the `live` tag is added, the welcome messages should fire automatically. Check Conversations to see if they went out.

### Manual (if automations aren't built yet)

**Send this SMS** from legacy CRM Conversations:

```
You're LIVE! Every call to your business number is now answered by your AI receptionist 24/7. You'll get a text every time a new lead comes in.

Your dashboard: https://thecalltaker.com/onboarding/live.html

Try it right now -- call your own number and hear your AI answer!
```

**Send the "You're Live" email** if you have one ready. Check [message-templates/](message-templates/) for a template.

### From your personal phone

Also send a personal text from your own phone (NOT from legacy CRM -- this feels more personal):

```
Hey [FIRST NAME], it's [your name] from The Call Taker. You're all set! Try calling your own number right now and you'll hear your AI answer. Let me know if you want anything tweaked. Welcome aboard!
```

Replace `[FIRST NAME]` with their name and `[your name]` with either "Wallace" or "Mills."

---

## 7. Share their dashboard and portal links

These are the links the client will use going forward:

- **Live dashboard:** https://thecalltaker.com/onboarding/live.html
- **Client portal:** https://thecalltaker.com/portal.html

If you haven't sent these yet, include them in your "you're live" message or send a follow-up:

```
Here are your links to save:

Your live dashboard: https://thecalltaker.com/onboarding/live.html
Your portal: https://thecalltaker.com/portal.html

Bookmark these -- you can check call activity, update settings, and reach us anytime.
```

---

## 8. Set up check-in reminders

The client needs to hear from you after going live. Set these reminders for yourself (phone alarm, calendar event, or legacy CRM task):

- **24 hours after go-live:** Text them asking how it's going, if any calls came in yet
- **1 week after go-live:** Review call volume, ask if they're happy, handle any tweaks
- **1 month after go-live:** Full performance review -- how many calls, how many leads captured, are they getting value

If legacy CRM automations handle these, great. If not, set a phone alarm right now so you don't forget.

**24-hour check-in message** (send tomorrow):

```
Hey [FIRST NAME]! Your AI has been live for about 24 hours -- how's it going? Any calls come through yet? Let me know if you want anything adjusted.
```

**1-week check-in message:**

```
Hey [FIRST NAME], you've been live for about a week now! How's the AI receptionist working out? I'd love to hear about any calls you've gotten. If there's anything you want tweaked (greeting, how it handles certain questions, etc.), just let me know.
```

---

## Client is officially live!

Here's what should be true right now:

- [ ] Client's business phone forwards to their AI number
- [ ] AI answers with the correct business name and greeting
- [ ] AI correctly handles service calls, emergencies, and general questions
- [ ] Client is tagged `live` + `active-client` in legacy CRM
- [ ] Client received "you're live" text and email
- [ ] Client received personal welcome text from you
- [ ] Client has their dashboard and portal links
- [ ] 24-hour, 1-week, and 1-month check-in reminders are set

---

## What happens next

- Daily: Check the [Daily Operations Guide](08-daily-operations.md) every morning
- If issues come up: [Troubleshooting Guide](09-troubleshooting.md)
- Need to look something up in legacy CRM: [legacy CRM Quick Reference](10-ghl-how-to.md)
