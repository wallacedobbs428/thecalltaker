# Step 1: Add Client to legacy CRM

You just got paid. First thing: get this person into legacy CRM as a contact so the system knows they exist.

---

## Click-by-click instructions

1. Open your browser and go to **app.gohighlevel.com**
2. Log in with your credentials
3. Make sure you're in the right location (top-left dropdown should show "The Call Taker" or your location). If not, click the dropdown and switch to Location ID: `tQb9YmrGDrdVUJYPKrsY`
4. In the **left sidebar**, look for the **person icon** labeled **"Contacts"** -- click it
5. You'll see your contacts list. In the **top-right corner**, click the green **"+ Add Contact"** button (it might say "Add Contact" or just have a "+" icon)
6. A form slides out from the right side. Fill in these fields:

   | Field | What to type |
   |-------|-------------|
   | **First Name** | Client's first name |
   | **Last Name** | Client's last name |
   | **Email** | Client's email address |
   | **Phone** | Client's phone number (the one they text from, NOT their business line) |
   | **Company Name** | Their business name (e.g., "Palmetto Comfort HVAC") |

7. Scroll down until you see the **"Tags"** section. It's a text field where you can type tag names.
8. Click inside the Tags field and type each of these tags **one at a time**, pressing **Enter** after each one:

   **Tag 1:** `payment-confirmed`

   **Tag 2:** Their industry tag -- pick ONE from this list:
   - `hvac`
   - `plumbing`
   - `electrical`
   - `roofing`
   - `locksmith`
   - `dental`
   - `medspa`
   - `legal`
   - `property-management`
   - `veterinary`
   - `towing`
   - `garage-door`
   - `funeral`

   **Tag 3:** Their plan tag -- pick ONE:
   - `starter` -- for Starter plan ($497/mo -- HVAC, Plumbing, Electrical)
   - `pro` -- for Pro plan ($997/mo -- all other industries)
   - `after-hours` -- if they only want after-hours coverage

9. After all three tags are added, you should see them as little colored chips/badges in the Tags field.
10. Click the green **"Save"** button at the bottom of the form.

---

## Verify it worked

1. You should see the new contact appear in your contacts list.
2. Click on their name to open their profile.
3. Check that all 3 tags are showing under their profile.
4. If the onboarding automation is already built in legacy CRM, a welcome text should fire within 60 seconds. To check:
   - In the **left sidebar**, click the **chat bubble icon** labeled **"Conversations"**
   - Find the client in the conversation list (search by name or phone)
   - Look for an automated welcome message
5. If the welcome message didn't send automatically, that's fine -- you'll send it manually in Step 2.

---

## Common mistakes

**Forgetting to add the industry tag.**
This is how the system knows what voice script to load for their AI agent. Without it, you'll have to remember their industry later. Always add it now.

**Adding the wrong plan tag.**
If you tag someone as `starter` but they paid for Pro, the system will treat them as a Starter client. Double-check the payment before tagging.

**Misspelling the email.**
If the email is wrong, they won't get any email automations (welcome emails, check-in emails, nothing). Double-check it character by character. Ask them to confirm it over text if you're not sure.

**Using the business phone instead of their personal phone.**
The Phone field should be the number they TEXT from (their cell phone). Their business line is a separate thing -- you'll deal with that in the forwarding step (Step 6). If you put the business line here, all your SMS messages will go to a landline that can't receive texts.

**Not clicking Save.**
Sounds dumb. Happens more than you'd think. If you navigate away without clicking Save, the contact is gone. Click the green Save button.

---

## What happens next

Move on to [Step 2: Send the Intake Form](02-send-intake-form.md).
