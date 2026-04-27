# Step 6: Run 3 Test Calls

Before going live, you MUST run 3 test calls to make sure everything works. Don't skip this. If the AI says the wrong business name or forgets to ask for a phone number, the client will hear about it from an angry customer.

---

## Before you start

Have these things ready:

- [ ] The **AI phone number** from Step 4 (this is the number you call)
- [ ] The client's **intake form** open so you can check if the AI is saying the right stuff
- [ ] Your **personal phone** (use this to make the calls -- NOT the client's number, NOT a legacy CRM number)
- [ ] A pen/paper or notes app to write down anything that's wrong

---

## TEST 1: Standard Service Call

This tests the normal everyday scenario -- someone calls because they need a service.

### What to do

1. Pick up your personal phone
2. Dial the AI phone number (the one you bought in Step 4)
3. Wait for the AI to answer
4. When it picks up, say something like a normal customer would:

   **HVAC:** "Hi, my AC isn't cooling. I need someone to come take a look."
   **Plumbing:** "Hey, my kitchen faucet is leaking pretty bad."
   **Locksmith:** "I'm locked out of my house, can someone come help?"
   **Dental:** "I need to schedule a cleaning."
   **Legal:** "I was in a car accident and need to talk to someone."
   **Roofing:** "I think my roof has some storm damage."
   **Electrical:** "My outlets in the kitchen stopped working."
   **Property Management:** "I'm a tenant and my heater is broken."
   **Medspa:** "I'm interested in getting Botox, can I schedule a consultation?"
   **Veterinary:** "My dog has been acting lethargic and won't eat."
   **Towing:** "My car broke down on the highway, I need a tow."
   **Garage Door:** "My garage door won't open."
   **Funeral:** "I need to make arrangements for a family member."

5. When the AI asks for your info, give fake details:
   - Name: **"John Smith"**
   - Phone: **"555-123-4567"**
   - Address: **"123 Main Street"**
6. Answer the AI's questions naturally, like a real customer would
7. Let the call play out until the AI wraps up

### Checklist -- ALL of these must pass

- [ ] AI greeted with the **correct business name** (not "The Call Taker", not another client's name)
- [ ] AI used the **correct receptionist name** (Gideon, Sarah, whatever they chose)
- [ ] AI asked for your **name**
- [ ] AI asked for your **phone number**
- [ ] AI asked for your **address or location**
- [ ] AI asked **what you need help with** (or acknowledged what you said)
- [ ] AI mentioned **callback time or scheduling** ("someone will call you back within 15 minutes" or "let me check availability")
- [ ] AI sounded **natural and friendly** (not robotic, not awkward, not cutting you off)
- [ ] AI did NOT say any **[BRACKETS]** or placeholder text

### After the call

1. Open legacy CRM in your browser
2. In the left sidebar, click **"Contacts"** (person icon)
3. In the search bar, type **"John Smith"**
4. If the contact was created, click on it and check:
   - Was the phone number captured correctly?
   - Was the address captured?
   - Was any note or summary of the call logged?
5. Also check: Did a notification go out? If there's an automation that texts the business owner when a new lead comes in, check if it fired. Go to Conversations and look for an outbound message to the client.

---

## TEST 2: Emergency Call

This tests how the AI handles urgent situations. The AI needs to stay calm, be reassuring, and still collect all the info.

### What to do

1. Call the AI phone number again from your personal phone
2. This time, sound more **urgent and stressed** -- talk faster, sound worried:

   **HVAC:** "I have no AC and it's 100 degrees in my house, I have a baby here, I need someone NOW"
   **Plumbing:** "My pipe burst and water is everywhere, it's flooding my kitchen!"
   **Locksmith:** "I'm locked out of my car at a gas station at night with my kid in the backseat"
   **Electrical:** "I smell something burning from my electrical panel"
   **Roofing:** "A tree just fell on my roof and it's raining inside"
   **Property Management:** "My apartment is flooding from the unit above me"
   **Towing:** "I'm on the side of the interstate and it's dark"

3. Give different fake info this time:
   - Name: **"Jane Doe"**
   - Phone: **"555-987-6543"**
   - Address: **"456 Oak Avenue"**
4. Be emotional but cooperative -- let the AI guide the conversation

### Checklist -- ALL of these must pass

- [ ] AI **recognized the urgency** (didn't respond with a casual "sure, let me schedule something for next week")
- [ ] AI was **reassuring** ("I understand this is urgent, let me get someone to help you right away" or similar)
- [ ] AI still **collected all the info** even though it's urgent (name, phone, address, issue)
- [ ] AI promised a **fast callback** within the correct timeframe the client specified
- [ ] If the client has an on-call tech: AI mentioned **dispatch or immediate help** ("I'm going to reach out to our on-call technician right now")
- [ ] If the client does NOT have an on-call tech: AI did NOT mention dispatching anyone
- [ ] Call felt like the AI actually **cared** about the emergency

### After the call

1. Go to legacy CRM > Contacts > search "Jane Doe"
2. Check that the contact was created with the right info
3. Check if an emergency/urgent notification was sent (if automations exist for this)

---

## TEST 3: After-Hours / General Questions

This tests how the AI handles non-service-request calls -- just people asking questions.

### What to do

1. Call the AI phone number one more time
2. Ask general questions:
   - "What are your hours?"
   - "Do you guys serve [a city in their service area]?"
   - "How much does [one of their services] cost?" (only if pricing is enabled for this client)
3. Also try acting like an existing customer:
   - "I have an appointment tomorrow, just wanted to confirm"
   - "Someone was supposed to come out yesterday and nobody showed up"

### Checklist -- ALL of these must pass

- [ ] AI correctly stated **business hours** (matches what's in the intake form)
- [ ] AI correctly identified **service area** ("Yes, we serve [city]" or "I'm not sure if we serve that area, let me have someone get back to you")
- [ ] AI handled **pricing** correctly:
  - If pricing is enabled: gave price ranges from the script
  - If pricing is NOT enabled: said something like "I'd want to make sure you get an accurate quote -- let me have someone reach out with exact pricing"
  - Did NOT make up prices that aren't in the script
- [ ] AI handled the **existing customer** scenario appropriately (didn't try to collect lead info, offered to have someone call them back, was helpful)
- [ ] AI did NOT say anything **incorrect** (wrong hours, wrong services, wrong area)

---

## If ANY test fails

Don't panic. Here's how to fix it:

1. **Write down exactly what went wrong.** Be specific: "AI said business hours were 9-5 but they're actually 8-6" or "AI forgot to ask for phone number" or "AI said [BUSINESS NAME] instead of the actual name."

2. Open legacy CRM: click the **gear icon** > **Settings** > **Conversation AI**

3. Find the client's agent in the list and **click on it** to open the settings

4. Find the **Agent Instructions / System Prompt** field (the big text area)

5. **Find and fix the issue:**
   - Wrong business name? Search for it in the script and correct it
   - Wrong hours? Find the hours section and update it
   - Missing question (didn't ask for phone #)? Check if the script says to ask for it -- if not, add an instruction like "Always ask for the caller's phone number"
   - Said a [BRACKET]? Search for `[` and replace the remaining placeholder
   - AI was too casual during emergency? Add a line to the script: "If the caller describes an emergency or urgent situation, respond with empathy and urgency. Reassure them that help is on the way."

6. Click **"Save"**

7. **Run the failed test again.** Call the AI number and repeat the same scenario.

8. Keep fixing and re-testing until **ALL 3 tests pass.**

---

## Clean up test contacts

After all tests pass, delete the fake contacts so they don't clutter the system:

1. Go to legacy CRM > **Contacts** (person icon in left sidebar)
2. Search for **"John Smith"**
3. Click on the contact
4. Look for a **"Delete"** option -- it might be:
   - A trash icon in the top-right of the contact profile
   - Under a **"..."** (three dots) menu
   - At the very bottom of the contact profile
5. Click **"Delete"** and confirm
6. Repeat for **"Jane Doe"**

---

## All 3 tests passed?

Move on to setting up call forwarding: [Step 5: Set Up Call Forwarding](05-setup-forwarding.md).

Then: [Step 7: Go Live](07-go-live.md).
