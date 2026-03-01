# Step 4: Buy + Assign Phone Number

The AI agent exists but has no phone number. Nobody can call it yet. This step gets a local phone number and connects it to the agent.

---

## Click-by-click: Buy a phone number

1. In GHL, click the **gear icon** at the bottom of the left sidebar to open **Settings**
2. In the Settings left panel, look for **"Phone Numbers"** -- it might be listed under a group called "LC Phone" or "Phone System" or "Business Info". Click it.
3. You'll see a list of phone numbers already in the system (the demo line (615) 784-5747 should be there).
4. Click the **"+ Add Number"** button in the top-right area. It might say "Buy Number" or "Purchase Number" or "Add Phone Number".
5. A dialog/panel will appear with a search field. This is where you search for available numbers.
6. In the search field, type the client's **area code**:
   - Look at their intake form for their business phone number
   - Use the same area code so it looks local
   - Examples: 615 for Nashville, 813 for Tampa, 212 for NYC, 310 for LA
7. Click **"Search"** or press Enter
8. A list of available phone numbers will appear. Pick one that:
   - Has the right area code
   - Looks clean and professional (avoid numbers with lots of repeated digits like 555-0000 unless you want that)
   - Just pick one -- don't overthink it
9. Click the **"Buy"** or **"Purchase"** button next to the number you want
10. Confirm the purchase if prompted. Cost is about **$1.15/month** per number.
11. The number should now appear in your Phone Numbers list. **Write it down or copy it** -- you'll need it in the next steps.

---

## Click-by-click: Assign the number to the AI agent

Now you need to tell GHL that this phone number should be answered by the AI agent you built in Step 3.

12. Stay in Settings. In the left panel, click **"Conversation AI"** (same place you went in Step 3).
13. You'll see your list of AI agents. Find the one you just created for this client (it should say "[Business Name] - Receptionist").
14. Click on the agent name to open its settings.
15. Look for a field labeled:
    - **"Phone Number"**
    - **"Assigned Number"**
    - **"Inbound Number"**
    - **"Trigger Phone Number"**
    It's a dropdown that shows available phone numbers.
16. Click the dropdown. You should see the number you just purchased in the list.
17. Select the number you just bought.
18. Click **"Save"** (or "Update").

**If you don't see the number in the dropdown:**
- Go back to Settings > Phone Numbers and make sure the number is actually there
- Make sure the number isn't already assigned to another agent
- Try refreshing the page (Ctrl+R or Cmd+R) and then going back to the agent settings
- If it still doesn't show, the number might need a few minutes to provision -- wait 2-3 minutes and try again

---

## Record the number on the client's contact

You need to save this number somewhere easy to find, because you'll reference it in the test calls, forwarding setup, and go-live steps.

19. In the left sidebar, click **"Contacts"** (person icon)
20. Search for the client and click on their name to open their profile
21. Look for a **"Notes"** section or tab. Click **"Add Note"** or the "+" button in the Notes area.
22. Type this note:

```
AI Phone Number: (XXX) XXX-XXXX
Purchased: [today's date]
Assigned to: [Business Name] - Receptionist agent
```

Replace (XXX) XXX-XXXX with the actual number you bought.

23. Click **"Save"** on the note.

---

## You'll need this number for

- **Step 5 (Test Calls):** You'll call this number to test the AI
- **Step 6 (Call Forwarding):** The client forwards their business line to this number
- **Step 7 (Go Live):** You tell the client this is their AI number
- **Any time you need to test:** This is the direct line to their AI receptionist

---

## Common mistakes

**Buying a number with the wrong area code.**
If the client is in Tampa (813) and you buy a 615 (Nashville) number, it looks weird to their customers. Always match the client's local area code.

**Forgetting to assign the number to the agent.**
Buying the number is only half the job. If you don't assign it to the agent in Conversation AI settings, calls to that number will just ring and go nowhere. Always do both steps.

**Assigning the number to the wrong agent.**
If you have multiple agents (demo + clients), make sure you're clicking into the right agent before assigning the number. Double-check the agent name matches the client's business.

**Not recording the number.**
If you don't save the number in a note on the client's contact, you'll be digging through Settings > Phone Numbers trying to remember which number belongs to which client. Save yourself the headache -- add the note now.

---

## What happens next

The AI agent has a phone number. Time to make sure it actually works. Move on to [Step 5: Run 3 Test Calls](06-test-calls.md).

(Yes, the file is named `06-test-calls.md` -- the numbering is slightly different from the step order because call forwarding setup [Step 6 in the guide] happens after testing.)
