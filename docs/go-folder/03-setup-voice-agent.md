# Step 3: Set Up the AI Voice Agent

This is the big one. You're building their custom AI receptionist that will actually answer their phone. Take your time -- a bad script means bad calls means a refund request.

---

## What you need before starting

Open these up and have them ready:

- [ ] The client's **intake form submission** (their business info, hours, services, etc.)
- [ ] The matching **industry voice script** from the `voice-scripts/` folder in this repo:
  - `voice-scripts/hvac.md` -- for HVAC clients
  - `voice-scripts/plumbing.md` -- for Plumbing clients
  - `voice-scripts/electrical.md` -- for Electrical clients
  - `voice-scripts/roofing.md` -- for Roofing clients
  - `voice-scripts/locksmith.md` -- for Locksmith clients
  - `voice-scripts/dental.md` -- for Dental clients
  - `voice-scripts/medspa.md` -- for Med Spa clients
  - `voice-scripts/legal.md` -- for Legal clients
  - `voice-scripts/property-management.md` -- for Property Management clients
  - `voice-scripts/veterinary.md` -- for Veterinary clients
  - `voice-scripts/towing.md` -- for Towing clients
  - `voice-scripts/garage-door.md` -- for Garage Door clients
  - `voice-scripts/funeral.md` -- for Funeral Home clients

If the voice script for their industry doesn't exist yet, use the HVAC one as a base and swap out the industry-specific details.

---

## Click-by-click: Create the AI agent in GHL

### Get to the Conversation AI settings

1. Open GHL in your browser: **app.gohighlevel.com**
2. Make sure you're in the correct location (top-left dropdown should say "The Call Taker")
3. Look at the **bottom of the left sidebar** for the **gear icon** -- click it to open **Settings**
4. You're now in the Settings page. Look at the **left panel** (inside Settings, there's another sidebar menu)
5. Scroll down or look for a section called **"Conversation AI"** -- it might be listed under a group called "AI" or "Phone" or "Business Tools". Click **"Conversation AI"**
6. You should see a page that lists AI agents. You might see "Jessica" or the demo agent already there.

### Create a new agent

7. In the top-right area of the Conversation AI page, click the **"+ Create Agent"** button (it might say "Add New Agent" or "Create New" or just a "+" icon)
8. A setup dialog/page will appear. Fill in:
   - **Agent Name:** Type `[Client Business Name] - Receptionist`
     - Example: `Palmetto Comfort - Receptionist`
     - Example: `Rapid Key Locksmith - Receptionist`
   - **Agent Type:** Select **"Inbound Call"** (NOT "Chat" or "SMS" -- we want phone calls)
9. Click **"Next"** or **"Create"** (whatever the button says to proceed)

### Set up the script/instructions

This is the most important part. The instructions field tells the AI exactly how to behave, what to say, what questions to ask, and what to do in different situations.

10. You should now be on the agent's settings/edit page. Look for a large text field labeled one of these:
    - **"Agent Instructions"**
    - **"System Prompt"**
    - **"Instructions"**
    - **"Prompt"**
    It's the biggest text area on the page -- you can't miss it.

11. Open the matching industry voice script file from `voice-scripts/` (see the list above). Open it in a text editor or in this repo.

12. **Select and copy the ENTIRE script** from the voice script file (Ctrl+A, Ctrl+C on Windows, or Cmd+A, Cmd+C on Mac).

13. **Paste it** into the Agent Instructions field in GHL (click inside the field, then Ctrl+V or Cmd+V).

14. **Now you have to replace every [BRACKET] placeholder with the client's real info.** This is where mistakes happen, so go slow.

    Do a **Ctrl+F** (or Cmd+F) search inside the text field for `[` -- this will highlight every bracket you need to replace. Go through each one:

    | Placeholder | Replace with | Where to find it |
    |------------|-------------|-----------------|
    | `[BUSINESS NAME]` | Their exact business name, e.g., "Palmetto Comfort" | Intake form, "Business Name" field |
    | `[AI NAME]` | The name they want the AI to use, e.g., "Jessica", "Sarah", "Emma" | Intake form. If they left it blank, use **"Jessica"** |
    | `[SERVICES]` | Comma-separated list of their services | Intake form, "Services" field. Example: "AC repair, heating installation, duct cleaning, maintenance plans" |
    | `[BUSINESS HOURS]` | Their hours in spoken format | Intake form. Example: "Monday through Friday 8 AM to 5 PM, Saturday 9 AM to 1 PM, closed Sundays" |
    | `[CALLBACK TIME]` | How fast they promise to call back | Intake form. Example: "within 15 minutes" or "within 30 minutes" or "within the hour" |
    | `[ON-CALL TECH NAME]` | Name of their on-call/emergency tech | Intake form. If they DON'T have one, see note below |
    | `[ON-CALL TECH PHONE]` | On-call tech's phone number | Intake form. If they DON'T have one, see note below |
    | `[SERVICE AREA]` | Cities, neighborhoods, or zones they serve | Intake form. Example: "Nashville, Franklin, Brentwood, and the greater Davidson County area" |
    | `[PRICING INFO]` | Their pricing ranges or standard rates | Intake form. If they said NO to pricing, see note below |

    **If they DON'T have an on-call tech:**
    Find the section in the script about on-call/emergency dispatch and **DELETE the entire paragraph/section**. Don't leave a blank bracket -- remove it completely. The AI should instead say something like "I'll make sure someone gets back to you as quickly as possible."

    **If they said NO to sharing pricing info:**
    Find the pricing section in the script and **DELETE it entirely**. Replace it with a line like: "If asked about pricing, say: I'd want to make sure you get an accurate quote -- let me have someone reach out to you with exact pricing for your specific situation."

15. After replacing ALL brackets, do one more **Ctrl+F search for `[`** to make sure you didn't miss any. If you find a `[` still in there, you missed one -- go back and fix it.

### Set the voice

16. On the same agent settings page, look for a field or dropdown labeled:
    - **"Voice"**
    - **"Voice Model"**
    - **"Voice Selection"**
    It might be near the top, bottom, or in an "Advanced Settings" section.

17. Our default voice is Voice ID: `w9rPM8AIZle60Nbpw7nl` -- this is what Jessica uses on the demo line. Keep this same voice unless the client specifically requested a different voice (male voice, different accent, etc.).

18. If you can see a voice dropdown, select the matching voice. If you see a text field for Voice ID, paste: `w9rPM8AIZle60Nbpw7nl`

19. If you can't find the voice setting at all, check under **"Advanced Settings"** or **"Voice Configuration"** -- sometimes it's collapsed/hidden.

### Set the greeting message

20. Look for a field labeled:
    - **"Greeting"**
    - **"Opening Message"**
    - **"First Message"**
    - **"Welcome Message"**

21. Type this greeting (replacing the brackets with real info):

```
Hey, thanks for calling [BUSINESS NAME], this is [AI NAME] -- how can I help you today?
```

Example: "Hey, thanks for calling Palmetto Comfort, this is Jessica -- how can I help you today?"

### Save everything

22. Click the **"Save"** button (usually bottom-right or top-right of the page). It might say "Save Agent" or "Update" or "Create Agent".

23. You should see a success message or the agent should now appear in your agents list.

---

## Verify it worked

1. Go back to the Conversation AI agents list (Settings > Conversation AI)
2. Find the agent you just created -- it should show the client's business name
3. Click on it to open it
4. Scan through the script one more time:
   - Is the business name correct?
   - Are the hours correct?
   - Are the services listed correctly?
   - Is the service area right?
   - Are there any remaining `[BRACKETS]` that you missed?
5. If everything looks good, move on

---

## Common mistakes

**Forgetting to replace a [BRACKET].**
This is the #1 mistake. The AI will literally say "Thanks for calling [BUSINESS NAME]" on a real call. Always do a final Ctrl+F search for `[` before saving.

**Leaving the on-call tech section in when they don't have one.**
The AI will say "Let me dispatch [ON-CALL TECH NAME] to your location" -- to a tech that doesn't exist. Delete the whole section if there's no on-call tech.

**Leaving pricing info in when they said no.**
Some clients will be furious if the AI quotes prices they didn't approve. If they said no to pricing on the intake form, delete the pricing section entirely.

**Selecting the wrong agent type.**
If you pick "Chat" instead of "Inbound Call", the agent will handle website chat, not phone calls. Make sure you select **"Inbound Call"**.

**Not saving.**
Click Save. Then click the agent again to make sure your changes are actually there. GHL sometimes doesn't save if there's a validation error you didn't notice.

---

## What happens next

The agent is created but it doesn't have a phone number yet. Move on to [Step 4: Buy + Assign Phone Number](04-buy-phone-number.md).
