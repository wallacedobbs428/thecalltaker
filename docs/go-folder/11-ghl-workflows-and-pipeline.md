# GHL Workflows & Pipeline Setup — Click-by-Click Guide

> **Who this is for:** Wallace and Mills. No GHL experience assumed.
> **What this does:** Sets up a 13-stage client lifecycle pipeline and 7 automated workflows so that when a client pays, every follow-up message, check-in, and internal alert fires automatically.
> **Login:** [app.gohighlevel.com](https://app.gohighlevel.com)
> **Location ID:** tQb9YmrGDrdVUJYPKrsY

---

## Table of Contents

1. [Create the Client Lifecycle Pipeline](#section-1-create-the-client-lifecycle-pipeline)
2. [Build the 7 Workflows](#section-2-build-the-7-workflows)
   - [Workflow 1: Welcome Sequence](#workflow-1-welcome--new-client)
   - [Workflow 2: Intake Form Received](#workflow-2-intake-received--start-setup)
   - [Workflow 3: Setup Complete](#workflow-3-setup-complete--test-calls)
   - [Workflow 4: You're Live](#workflow-4-go-live--client-active)
   - [Workflow 5: 24-Hour Check-in](#workflow-5-24hr-check-in)
   - [Workflow 6: 1-Week Check-in](#workflow-6-1-week-check-in)
   - [Workflow 7: Review Request](#workflow-7-review-request--day-14)
3. [How to Build Any Workflow (Generic Walkthrough)](#section-3-how-to-build-any-workflow-generic-walkthrough)
4. [Tags Reference](#section-4-tags-reference)

---

## SECTION 1: Create the Client Lifecycle Pipeline

A pipeline is a visual board (like Trello) where each column is a stage. You drag client cards from left to right as they move through your process. This pipeline tracks every client from first contact to churn.

### Pipeline Name

```
Client Lifecycle
```

### Stages (in this exact order, left to right)

| # | Stage Name             | What It Means                                                       |
|---|------------------------|---------------------------------------------------------------------|
| 1 | Lead                   | Someone who showed interest but hasn't booked or paid yet           |
| 2 | Demo Booked            | They scheduled a demo call                                         |
| 3 | Demo Completed         | The demo call happened                                              |
| 4 | Proposal Sent          | You sent them pricing / a proposal                                 |
| 5 | Payment Received       | They paid — they're a client now                                    |
| 6 | Intake Form Submitted  | They filled out the intake form with their business info            |
| 7 | Setup In Progress      | You're building their AI receptionist                               |
| 8 | Testing                | The AI is built — you or the client are running test calls          |
| 9 | Client Approved        | Client heard the test calls and approved                            |
| 10 | Live / Active         | Call forwarding is on, AI is answering real calls                   |
| 11 | Monthly Review Due    | Time for their monthly performance check-in                         |
| 12 | At Risk               | Client is unhappy, low usage, might cancel                          |
| 13 | Churned               | Client cancelled                                                    |

### Click-by-Click: Create the Pipeline

1. Open your browser. Go to **app.gohighlevel.com**. Log in.

2. Look at the **left sidebar** (the vertical menu on the left side of the screen). Find and click **"Opportunities"**. It looks like a dollar sign icon (`$`) or a funnel icon. If you don't see it by name, hover over the icons until you find "Opportunities."

3. You'll land on the Opportunities page. At the top of the page, you should see either:
   - An existing pipeline name with a dropdown arrow next to it, OR
   - A mostly empty page

4. Look for **"+ Create Pipeline"** or **"+ Add Pipeline"** — it's usually a button near the top right, or inside a dropdown at the top left if you click the pipeline name area. Click it.

5. A dialog box will pop up asking for the pipeline name. Type:
   ```
   Client Lifecycle
   ```
   Then click **"Save"** or **"Create."**

6. You'll now see the pipeline board with one default stage (usually called "New" or "Stage 1"). Click on the **stage name text** to rename it. Change it to:
   ```
   Lead
   ```
   Press Enter or click the checkmark to save.

7. Now you need to add the remaining 12 stages. Look for a **"+ Add Stage"** button — it's usually on the far right of the stage columns, or at the end of the board. Click it.

8. A new blank stage appears. Type the name:
   ```
   Demo Booked
   ```
   Press Enter or click Save.

9. Click **"+ Add Stage"** again. Type:
   ```
   Demo Completed
   ```

10. Repeat this process for every remaining stage. Click **"+ Add Stage"** and type the name, one at a time:
    ```
    Proposal Sent
    Payment Received
    Intake Form Submitted
    Setup In Progress
    Testing
    Client Approved
    Live / Active
    Monthly Review Due
    At Risk
    Churned
    ```

11. After all 13 stages are created, verify they appear in the correct left-to-right order. If a stage is in the wrong position, you can **drag it** by clicking and holding the stage header and moving it left or right.

12. Click **"Save"** if there's a save button, or your changes may auto-save.

### How to Use the Pipeline Day-to-Day

- **New lead comes in:** Go to Opportunities, click **"+ Add Opportunity"** (or **"+ Add"**) in the "Lead" column. Fill in their name and contact info. Save.
- **They book a demo:** Drag their card from "Lead" to "Demo Booked."
- **Demo happens:** Drag to "Demo Completed."
- **You send pricing:** Drag to "Proposal Sent."
- **They pay:** Drag to "Payment Received."
- **They submit intake form:** Drag to "Intake Form Submitted."
- **You're building their AI:** Drag to "Setup In Progress."
- **AI is built, testing:** Drag to "Testing."
- **Client approves:** Drag to "Client Approved."
- **They're live:** Drag to "Live / Active." This is their home until something changes.
- **Monthly review time:** Drag to "Monthly Review Due." After the review, drag back to "Live / Active."
- **They're unhappy or might cancel:** Drag to "At Risk."
- **They cancelled:** Drag to "Churned."

> **Tip:** You can also move pipeline stages automatically using workflows (covered in Section 2). That way you don't have to drag cards manually — they move themselves when the right tag gets added.

---

## SECTION 2: Build the 7 Workflows

A **workflow** is an automation that fires when something happens (a trigger), then runs a series of actions in order. For example: "When someone gets the tag `payment-confirmed`, wait 0 minutes, then send them a welcome SMS, then wait 5 minutes, then send them a welcome email."

You'll build 7 workflows total. Each one is described below with exact click-by-click instructions.

---

### Workflow 1: Welcome -- New Client

**What it does:** When a new client pays and gets tagged `payment-confirmed`, this workflow immediately sends them a welcome SMS, then a welcome email 5 minutes later, then a reminder to fill out the intake form 10 minutes after that. It also sends you (Wallace/Mills) a push notification so you know someone just paid.

**Name:** `Welcome — New Client`
**Trigger:** Tag `payment-confirmed` is added to a contact.

**Actions in order:**

| Step | Action                  | Details                                                                                         |
|------|-------------------------|-------------------------------------------------------------------------------------------------|
| 1    | Send SMS                | See welcome SMS template below                                                                  |
| 2    | Wait 5 minutes          |                                                                                                 |
| 3    | Send Email              | Subject: "Welcome to The Call Taker — let's get you set up!" / Body: see welcome email below   |
| 4    | Wait 10 minutes         |                                                                                                 |
| 5    | Send SMS                | Intake form reminder (see below)                                                                |
| 6    | Internal Notification   | ntfy push: "New client! [CONTACT NAME] just paid"                                              |

**Welcome SMS text** (paste this exactly):
```
Hey {{contact.first_name}}! Payment received — welcome to The Call Taker! We're pumped to get {{contact.company_name}} set up. Your intake form is headed to your inbox right now. Fill it out and your AI receptionist will be live within 2 hours. Let's go!
```

**Welcome Email subject:**
```
Welcome to The Call Taker — let's get you set up!
```

**Welcome Email body** (paste this exactly):
```
Hey {{contact.first_name}},

Welcome aboard! We're stoked to have {{contact.company_name}} joining The Call Taker.

Your payment is confirmed and we're ready to build your AI receptionist. Here's exactly what happens next:

1. Fill out your intake form — takes about 5 minutes. This tells us your business hours, services, how you want calls handled, and what your AI should sound like.

   https://thecalltaker.com/onboarding/intake.html

2. We build your AI — once you submit the form, we configure your voice agent, train it on your business, and run test calls to make sure it sounds perfect.

3. You go live — we walk you through call forwarding and flip the switch. Every call to your business gets answered by your AI receptionist, 24/7.

How fast does this happen? Your AI will be live within 2 hours of submitting the intake form. Most clients are up and running the same day they sign up.

If you have any questions along the way, we're right here:

Email: wallacemdobbs@icloud.com
Phone: (615) 784-5747
Web: thecalltaker.com

Talk soon,
Wallace & Mills — The Call Taker Team
```

**Intake form reminder SMS** (Step 5):
```
Quick reminder — fill out your setup form so we can get your AI live: https://thecalltaker.com/onboarding/intake.html
```

#### Click-by-Click: Build This Workflow

1. In GHL, look at the **left sidebar**. Find and click **"Automation"** (it has a lightning bolt icon). You might also see it called "Workflows" in some GHL versions.

2. You'll land on the Automations/Workflows page. Click the **"+ Create Workflow"** button in the top-right corner.

3. A popup appears asking you to choose a template or start from scratch. Click **"Start from Scratch"** (or "Blank Workflow"). Then click **"Continue"** or **"Create."**

4. You're now in the workflow builder. At the top of the screen, you'll see the workflow name (probably says "Untitled Workflow" or similar). **Click on that name** and change it to:
   ```
   Welcome — New Client
   ```
   Press Enter.

5. **Set the trigger.** You'll see a box at the top of the workflow canvas that says something like "Add New Trigger" or "Workflow Trigger." Click on it.

6. A panel slides open on the right side (or a popup appears) with a list of trigger types. You need to find **"Contact Tag"** — scroll through the list or use the search bar and type "tag." Click **"Contact Tag."**

7. Now configure the trigger:
   - **Filter/Action:** Select **"Is Added"** (not "Is Removed").
   - **Tag:** Type `payment-confirmed` in the tag field. If it appears in a dropdown, click it. If it doesn't exist yet, type it exactly as shown and it will be created when you first use it.
   - Click **"Save Trigger"** (or the save button at the bottom of the panel).

8. **Add the first action (Send SMS).** Below the trigger box on the canvas, you'll see a **"+"** icon or "Add Action" button. Click it.

9. A list of available actions appears. Find and click **"Send SMS"** (it might be under a "Communications" category or just in the main list).

10. A configuration panel opens. Fill in:
    - **Phone Number Field:** Leave as default (it will use the contact's phone number automatically).
    - **Message body:** Paste the welcome SMS text from above. To insert the contact's first name, look for a **"Custom Values"** button (sometimes shown as `{{ }}` or a dropdown labeled "Insert Field"). Click it, find "Contact First Name," and click it — it will insert `{{contact.first_name}}` into the message. Do the same for company name if needed.
    - Click **"Save Action"** (or the save button).

11. **Add a Wait step.** Click the **"+"** below the SMS action. Find and click **"Wait"** in the action list.

12. Configure the wait:
    - **Wait for:** Select **"Time Delay"** (not "Specific Date" or "Event").
    - **Duration:** Type `5`.
    - **Unit:** Select **"Minutes."**
    - Click **"Save Action."**

13. **Add the Welcome Email.** Click the **"+"** below the Wait step. Find and click **"Send Email."**

14. Configure the email:
    - **Subject:** Type: `Welcome to The Call Taker — let's get you set up!`
    - **Body/Content:** You'll see an email editor. Paste the welcome email body from above. Use the `{{ }}` or "Custom Values" button to insert `{{contact.first_name}}` and `{{contact.company_name}}` where needed.
    - **From Name:** Type `The Call Taker` (or leave as your default).
    - **From Email:** Use your configured sending email.
    - Click **"Save Action."**

15. **Add another Wait step.** Click **"+"**, select **"Wait"**, set to **10 minutes**, save.

16. **Add the intake form reminder SMS.** Click **"+"**, select **"Send SMS"**, paste the reminder text from above, save.

17. **Add the internal notification.** Click **"+"** below the last action. You have two options for the ntfy push notification:

    **Option A — Use "Send Webhook" action (RECOMMENDED):**
    - Find and click **"Webhook"** or **"Custom Webhook"** in the action list.
    - **Method:** POST
    - **URL:** `https://ntfy.sh/tct-xK9mW4vR7pLd`
    - **Body:** `New client! {{contact.full_name}} just paid`
    - Save.

    **Option B — Use "Internal Notification" action:**
    - If you see an "Internal Notification" or "Send Notification" action, click it.
    - Set the notification text to: `New client! {{contact.full_name}} just paid`
    - This sends an in-app notification inside GHL (not a phone push notification). You'll still want Option A for phone alerts.

    > **Use both** if you want — the webhook sends a phone push via ntfy, and the internal notification shows up inside GHL.

18. **Turn the workflow ON.** Look at the **top-right area** of the workflow builder. You'll see a toggle switch or a "Publish" / "Save & Publish" button. Click it to activate the workflow. The toggle should turn green or the status should say "Active" or "Published."

19. Click **"Save"** if there's a separate save button.

**This workflow is now live.** Whenever you add the tag `payment-confirmed` to a contact in GHL, this entire sequence fires automatically.

---

### Workflow 2: Intake Received -- Start Setup

**What it does:** When a client submits the intake form and gets tagged `intake-submitted`, this workflow sends them a confirmation SMS, moves their pipeline card to "Intake Form Submitted," adds a setup tag, and notifies you to start building their AI.

**Name:** `Intake Received — Start Setup`
**Trigger:** Tag `intake-submitted` is added to a contact.

**Actions in order:**

| Step | Action                      | Details                                                                                               |
|------|-----------------------------|-------------------------------------------------------------------------------------------------------|
| 1    | Send SMS                    | See text below                                                                                        |
| 2    | Move Pipeline Stage         | Move to "Intake Form Submitted" in Client Lifecycle pipeline                                         |
| 3    | Add Tag                     | Add tag `setup-in-progress`                                                                          |
| 4    | Webhook (ntfy)              | POST to `https://ntfy.sh/tct-xK9mW4vR7pLd` — body: "[CONTACT NAME] submitted intake form — start setup" |

**SMS text:**
```
Got it! We're building your AI receptionist now. This usually takes about an hour. I'll text you when it's ready to test.
```

#### Click-by-Click: Build This Workflow

1. Left sidebar, click **"Automation"** (lightning bolt).
2. Click **"+ Create Workflow"** (top right).
3. Click **"Start from Scratch"**, then **"Continue."**
4. Click the workflow name at the top, rename to:
   ```
   Intake Received — Start Setup
   ```

5. **Set the trigger:** Click the trigger area, select **"Contact Tag"**, set to **"Is Added"**, type `intake-submitted`, save.

6. **Add Send SMS action:** Click **"+"**, select **"Send SMS"**, paste the SMS text from above, save.

7. **Add Move Pipeline Stage action:** Click **"+"** below the SMS. Look for an action called **"Update Opportunity"** or **"Pipeline Stage Change"** or **"Move to Pipeline Stage."** The exact name varies by GHL version. Click it.
   - **Pipeline:** Select **"Client Lifecycle"** from the dropdown.
   - **Stage:** Select **"Intake Form Submitted"** from the dropdown.
   - If it asks about creating a new opportunity vs. updating existing: choose **"Update Existing Opportunity"** (you want to move their existing card, not create a duplicate).
   - Save.

   > **Note:** If you don't see a "Move Pipeline Stage" action, look for "Update Opportunity" or "Create/Update Opportunity." The field names may differ, but the concept is the same: pick the pipeline, pick the stage.

8. **Add Tag action:** Click **"+"**, find the action called **"Add Tag"** or **"Add/Remove Tag"**. Select **"Add"**, type `setup-in-progress`, save.

9. **Add Webhook (ntfy) action:** Click **"+"**, select **"Webhook"** or **"Custom Webhook."**
   - **Method:** POST
   - **URL:** `https://ntfy.sh/tct-xK9mW4vR7pLd`
   - **Body:** `{{contact.full_name}} submitted intake form — start setup`
   - Save.

10. **Turn the workflow ON** using the toggle/publish button at the top right.
11. Click **"Save."**

---

### Workflow 3: Setup Complete -- Test Calls

**What it does:** When you're done building a client's AI agent and tag them `setup-complete`, this workflow texts them their test number so they can hear their AI, moves their pipeline card to "Testing," and notifies you to run your own test calls.

**Name:** `Setup Complete — Test Calls`
**Trigger:** Tag `setup-complete` is added to a contact.

**Actions in order:**

| Step | Action                 | Details                                                                                      |
|------|------------------------|----------------------------------------------------------------------------------------------|
| 1    | Send SMS               | See text below                                                                               |
| 2    | Move Pipeline Stage    | Move to "Testing" in Client Lifecycle pipeline                                               |
| 3    | Webhook (ntfy)         | POST to `https://ntfy.sh/tct-xK9mW4vR7pLd` — body: "[CONTACT NAME] agent is built — run test calls" |

**SMS text:**
```
{{contact.first_name}}, your AI receptionist for {{contact.company_name}} is built and ready to go! Give it a call right now and hear it in action:

[AI PHONE NUMBER]

Call it a few times, ask it anything a customer would. Once you're happy, we'll get your forwarding set up. Reply here when you're ready!
```

> **IMPORTANT:** Before this workflow fires, you must manually replace `[AI PHONE NUMBER]` with the client's actual AI phone number. You can either:
> - Store their AI number in a GHL custom field (e.g., `{{contact.ai_phone_number}}`) and use that variable, OR
> - Send this SMS manually instead of through the workflow, since each client has a different number.

#### Click-by-Click: Build This Workflow

1. Left sidebar, click **"Automation"** (lightning bolt).
2. Click **"+ Create Workflow"** (top right).
3. Click **"Start from Scratch"**, then **"Continue."**
4. Rename to:
   ```
   Setup Complete — Test Calls
   ```

5. **Set the trigger:** Click trigger area, select **"Contact Tag"**, set to **"Is Added"**, type `setup-complete`, save.

6. **Add Send SMS action:** Click **"+"**, select **"Send SMS"**, paste the SMS text from above. Replace `[AI PHONE NUMBER]` with the custom field variable if you've set one up (see note above). Save.

7. **Add Move Pipeline Stage action:** Click **"+"**, select **"Update Opportunity"** or **"Pipeline Stage Change."**
   - Pipeline: **Client Lifecycle**
   - Stage: **Testing**
   - Save.

8. **Add Webhook (ntfy):** Click **"+"**, select **"Webhook."**
   - Method: POST
   - URL: `https://ntfy.sh/tct-xK9mW4vR7pLd`
   - Body: `{{contact.full_name}} agent is built — run test calls`
   - Save.

9. **Turn the workflow ON.** Save.

---

### Workflow 4: Go Live -- Client Active

**What it does:** When a client's call forwarding is set up and you tag them `live`, this workflow sends them a congratulations SMS immediately, a "you're live" email 5 minutes later, moves their pipeline card to "Live / Active," adds the `active-client` tag, and sends you a celebration push notification.

**Name:** `Go Live — Client Active`
**Trigger:** Tag `live` is added to a contact.

**Actions in order:**

| Step | Action                  | Details                                                                    |
|------|-------------------------|----------------------------------------------------------------------------|
| 1    | Send SMS                | See "You're Live" SMS text below                                           |
| 2    | Wait 5 minutes          |                                                                            |
| 3    | Send Email              | Subject + body below                                                       |
| 4    | Move Pipeline Stage     | Move to "Live / Active" in Client Lifecycle pipeline                       |
| 5    | Add Tag                 | `active-client`                                                            |
| 6    | Webhook (ntfy)          | POST to `https://ntfy.sh/tct-xK9mW4vR7pLd` — body: "[CONTACT NAME] is LIVE!" |

**"You're Live" SMS text:**
```
{{contact.first_name}}, you're LIVE! Your AI receptionist is answering calls for {{contact.company_name}} right now, 24/7. Every call gets picked up. No more voicemail. Welcome to the future of your business. We'll check in with you tomorrow to make sure everything's perfect.
```

**"You're Live" Email subject:**
```
You're live — your AI receptionist is answering calls right now
```

**"You're Live" Email body:**
```
Hey {{contact.first_name}},

Your AI receptionist is officially live and answering every call to {{contact.company_name}}. Here's what to know:

WHAT'S HAPPENING NOW:
- Every inbound call to your business number is being answered by your AI receptionist
- It handles scheduling, pricing questions, emergency routing, and basic service inquiries
- It works 24 hours a day, 7 days a week — nights, weekends, holidays

WHAT TO EXPECT:
- You'll receive notifications when calls come in
- If a caller needs to speak to a human, the AI will collect their info and notify you immediately
- Most clients see a noticeable drop in missed calls within the first 48 hours

IF SOMETHING SEEMS OFF:
- Call your own number and test it anytime
- Text or email us and we'll adjust anything on the fly:
  Email: wallacemdobbs@icloud.com
  Phone: (615) 784-5747

We'll check in with you tomorrow and again at the 1-week mark. If you need anything before then, just reply to this email.

Welcome aboard,
Wallace & Mills — The Call Taker Team
```

#### Click-by-Click: Build This Workflow

1. Left sidebar, click **"Automation"** (lightning bolt).
2. Click **"+ Create Workflow"**, then **"Start from Scratch"**, then **"Continue."**
3. Rename to:
   ```
   Go Live — Client Active
   ```

4. **Set the trigger:** Click trigger area, select **"Contact Tag"**, **"Is Added"**, type `live`, save.

5. **Add Send SMS:** Click **"+"**, select **"Send SMS"**, paste the "You're Live" SMS text, save.

6. **Add Wait:** Click **"+"**, select **"Wait"**, set to **5 minutes**, save.

7. **Add Send Email:** Click **"+"**, select **"Send Email."**
   - Subject: paste the subject line from above.
   - Body: paste the email body from above. Use `{{ }}` custom values to insert contact fields.
   - Save.

8. **Add Move Pipeline Stage:** Click **"+"**, select **"Update Opportunity"** or **"Pipeline Stage Change."**
   - Pipeline: **Client Lifecycle**
   - Stage: **Live / Active**
   - Save.

9. **Add Tag:** Click **"+"**, select **"Add Tag"**, type `active-client`, save.

10. **Add Webhook (ntfy):** Click **"+"**, select **"Webhook."**
    - Method: POST
    - URL: `https://ntfy.sh/tct-xK9mW4vR7pLd`
    - Body: `{{contact.full_name}} is LIVE!`
    - Save.

11. **Turn the workflow ON.** Save.

---

### Workflow 5: 24hr Check-in

**What it does:** 24 hours after a client goes live, this workflow automatically sends them a check-in text asking how things are going. It also notifies you that the check-in was sent.

**Name:** `24hr Check-in`
**Trigger:** Tag `live` is added to a contact.

**Actions in order:**

| Step | Action              | Details                                                                                   |
|------|---------------------|-------------------------------------------------------------------------------------------|
| 1    | Wait 24 hours       |                                                                                           |
| 2    | Send SMS            | See text below                                                                            |
| 3    | Webhook (ntfy)      | POST to `https://ntfy.sh/tct-xK9mW4vR7pLd` — body: "24hr check-in sent to [CONTACT NAME]" |

**24hr Check-in SMS text:**
```
Hey {{contact.first_name}}, it's been about 24 hours since your AI went live — how's everything going? Any calls come through that you want us to look at? We can tweak anything on the fly. Just reply here.
```

#### Click-by-Click: Build This Workflow

1. Left sidebar, click **"Automation"** (lightning bolt).
2. Click **"+ Create Workflow"**, then **"Start from Scratch"**, then **"Continue."**
3. Rename to:
   ```
   24hr Check-in
   ```

4. **Set the trigger:** Click trigger area, select **"Contact Tag"**, **"Is Added"**, type `live`, save.

5. **Add Wait:** Click **"+"**, select **"Wait"**, set to **24 hours** (type `24`, select "Hours" or `1` and select "Days"), save.

6. **Add Send SMS:** Click **"+"**, select **"Send SMS"**, paste the check-in SMS text, save.

7. **Add Webhook (ntfy):** Click **"+"**, select **"Webhook."**
   - Method: POST
   - URL: `https://ntfy.sh/tct-xK9mW4vR7pLd`
   - Body: `24hr check-in sent to {{contact.full_name}}`
   - Save.

8. **Turn the workflow ON.** Save.

---

### Workflow 6: 1-Week Check-in

**What it does:** 7 days after a client goes live, this workflow sends them a detailed check-in email reviewing their first week. It also notifies you.

**Name:** `1-Week Check-in`
**Trigger:** Tag `live` is added to a contact.

**Actions in order:**

| Step | Action              | Details                                                                                     |
|------|---------------------|---------------------------------------------------------------------------------------------|
| 1    | Wait 7 days         |                                                                                             |
| 2    | Send Email          | Subject + body below                                                                        |
| 3    | Webhook (ntfy)      | POST to `https://ntfy.sh/tct-xK9mW4vR7pLd` — body: "1-week check-in sent to [CONTACT NAME]" |

**1-Week Check-in Email subject:**
```
Your first week with The Call Taker — how's it going?
```

**1-Week Check-in Email body:**
```
Hey {{contact.first_name}},

It's been one week since your AI receptionist went live at {{contact.company_name}}. We wanted to check in and see how things are going.

A FEW QUESTIONS:
- Are calls being handled the way you expected?
- Have you noticed any calls that the AI could have handled better?
- Any changes to your services, hours, or pricing we should update?

If everything's running smooth, great — no need to reply. We'll keep monitoring from our end.

If there's anything you want adjusted, just reply to this email or text us at (615) 784-5747 and we'll make changes same-day.

Thanks for trusting us with your calls,
Wallace & Mills — The Call Taker Team
```

#### Click-by-Click: Build This Workflow

1. Left sidebar, click **"Automation"** (lightning bolt).
2. Click **"+ Create Workflow"**, then **"Start from Scratch"**, then **"Continue."**
3. Rename to:
   ```
   1-Week Check-in
   ```

4. **Set the trigger:** Click trigger area, select **"Contact Tag"**, **"Is Added"**, type `live`, save.

5. **Add Wait:** Click **"+"**, select **"Wait"**, set to **7 days**, save.

6. **Add Send Email:** Click **"+"**, select **"Send Email."**
   - Subject: paste the subject line from above.
   - Body: paste the email body from above.
   - Save.

7. **Add Webhook (ntfy):** Click **"+"**, select **"Webhook."**
   - Method: POST
   - URL: `https://ntfy.sh/tct-xK9mW4vR7pLd`
   - Body: `1-week check-in sent to {{contact.full_name}}`
   - Save.

8. **Turn the workflow ON.** Save.

---

### Workflow 7: Review Request -- Day 14

**What it does:** 14 days after a client goes live, this workflow sends them a text asking for a Google review or testimonial. No ntfy notification on this one — it's a set-and-forget ask.

**Name:** `Review Request — Day 14`
**Trigger:** Tag `live` is added to a contact.

**Actions in order:**

| Step | Action         | Details          |
|------|----------------|------------------|
| 1    | Wait 14 days   |                  |
| 2    | Send SMS       | See text below   |

**Review Request SMS text:**
```
Hey {{contact.first_name}}, you've been using The Call Taker for 2 weeks now and we'd love to hear how it's going. If you've got 30 seconds, a quick Google review would mean the world to us: [GOOGLE REVIEW LINK]

And if you've got a specific result you've noticed — like fewer missed calls or more booked jobs — we'd love to feature {{contact.company_name}} as a case study. No pressure at all. Just reply here if you're open to it!
```

> **IMPORTANT:** Replace `[GOOGLE REVIEW LINK]` with your actual Google Business Profile review link once you have one. Until then, you can remove that sentence or leave a placeholder.

#### Click-by-Click: Build This Workflow

1. Left sidebar, click **"Automation"** (lightning bolt).
2. Click **"+ Create Workflow"**, then **"Start from Scratch"**, then **"Continue."**
3. Rename to:
   ```
   Review Request — Day 14
   ```

4. **Set the trigger:** Click trigger area, select **"Contact Tag"**, **"Is Added"**, type `live`, save.

5. **Add Wait:** Click **"+"**, select **"Wait"**, set to **14 days**, save.

6. **Add Send SMS:** Click **"+"**, select **"Send SMS"**, paste the review request SMS text, save.

7. **Turn the workflow ON.** Save.

---

## SECTION 3: How to Build Any Workflow (Generic Walkthrough)

This section covers the general process for creating any workflow in GHL. Reference this whenever you need to build something new beyond the 7 workflows above.

### Step 1: Find the Automations Section

1. Log in to GHL at **app.gohighlevel.com**.
2. Look at the **left sidebar** (vertical menu on the left).
3. Click **"Automation"** — it has a **lightning bolt** icon.
4. You'll see a list of all existing workflows. Active ones have a green toggle; inactive ones have a gray toggle.

### Step 2: Create a New Workflow

1. Click **"+ Create Workflow"** in the top-right corner.
2. You'll see two options:
   - **Start from Scratch** — blank workflow, you build everything.
   - **Use a Recipe/Template** — GHL has pre-built templates for common tasks. These can save time but you usually need to customize them.
3. Click **"Start from Scratch"**, then **"Continue"** (or **"Create"**).
4. Click the workflow name at the top of the screen to rename it. Use a clear, descriptive name.

### Step 3: Set a Trigger

The trigger is what starts the workflow. Click the trigger box at the top of the canvas.

**Available trigger types you'll use most often:**

| Trigger Type               | When It Fires                                                    | Example Use                             |
|----------------------------|------------------------------------------------------------------|-----------------------------------------|
| **Contact Tag (Added)**    | When a specific tag is added to a contact                       | `payment-confirmed` tag added           |
| **Contact Tag (Removed)**  | When a specific tag is removed from a contact                   | `active-client` removed (they churned)  |
| **Form Submitted**         | When a contact fills out a GHL form                              | Intake form submitted                   |
| **Appointment Status**     | When an appointment status changes (booked, confirmed, etc.)    | Demo call booked                        |
| **Pipeline Stage Changed** | When an opportunity moves to a specific pipeline stage           | Moved to "Live / Active"                |
| **Contact Created**        | When a new contact is created in GHL                             | New lead added                          |
| **Inbound Webhook**        | When an external system sends a POST request to a GHL webhook   | Stripe payment notification             |
| **Date/Time**              | At a specific time on a recurring schedule                       | Every Monday at 9 AM                    |

**How to configure a trigger:**
1. Click the trigger box.
2. Select the trigger type from the list.
3. Fill in the details (which tag, which form, which pipeline stage, etc.).
4. Click **"Save Trigger."**

> **You can have multiple triggers on the same workflow.** Click "Add New Trigger" below the first trigger to add a second one. For example, a workflow could fire when EITHER the `payment-confirmed` tag is added OR a specific form is submitted.

### Step 4: Add Actions

Actions are the steps that happen after the trigger fires. Click the **"+"** below the trigger (or below the previous action) to add each action.

**Available actions you'll use most often:**

| Action                      | What It Does                                                                   |
|-----------------------------|--------------------------------------------------------------------------------|
| **Send SMS**                | Sends a text message to the contact's phone number                            |
| **Send Email**              | Sends an email to the contact's email address                                 |
| **Wait**                    | Pauses the workflow for a specified amount of time (minutes, hours, days)      |
| **Add Tag**                 | Adds a tag to the contact                                                      |
| **Remove Tag**              | Removes a tag from the contact                                                 |
| **Update Opportunity**      | Moves an opportunity to a different pipeline stage                              |
| **Create Opportunity**      | Creates a new opportunity (card) in a pipeline                                 |
| **Webhook**                 | Sends an HTTP request to an external URL (used for ntfy notifications)         |
| **Internal Notification**   | Sends a notification inside GHL to a specific user                             |
| **If/Else**                 | Creates a branch — if a condition is true, go one path; if false, go another  |
| **Go To**                   | Jumps to another step in the workflow (for loops)                               |
| **Update Contact Field**    | Changes a custom field value on the contact                                    |
| **Assign User**             | Assigns a GHL user to the contact                                              |

**How to configure an action:**
1. Click **"+"** to add a new step.
2. Browse or search the action list.
3. Click the action you want.
4. A configuration panel opens on the right side. Fill in the details.
5. To insert contact data (name, email, phone, company, etc.) into any text field, click the **`{{ }}`** button or **"Custom Values"** dropdown. Select the field you want to insert (e.g., "Contact First Name" inserts `{{contact.first_name}}`).
6. Click **"Save Action."**

### Step 5: Test the Workflow

**Testing by manually adding a tag:**

1. Go to **"Contacts"** in the left sidebar (person icon).
2. Find a test contact (create one if you don't have one — use your own phone number and email).
3. Click on the test contact to open their profile.
4. In the contact profile, find the **"Tags"** section. It's usually on the right side or in a panel.
5. Click in the tags field and type the tag that triggers your workflow (e.g., `payment-confirmed`).
6. Press Enter or click the tag to add it.
7. The workflow should fire. Check your phone for SMS, check your email inbox, and check ntfy for push notifications.

**Checking if a workflow fired:**

1. Go to **"Automation"** (lightning bolt) in the left sidebar.
2. Find the workflow you want to check.
3. Click on the workflow name to open it.
4. Look for an **"Execution Logs"** or **"History"** tab at the top of the workflow builder. Click it.
5. You'll see a list of all contacts who entered this workflow, when they entered, and the status of each step (completed, pending, failed).

> **Tip:** If a workflow step fails, click on the failed step in the execution log to see the error message. Common issues: phone number format wrong, email address missing, tag name misspelled.

### Step 6: Activate / Deactivate Workflows

- **To turn a workflow ON:** Open the workflow, look at the top-right corner, and click the toggle switch so it turns **green** (or click "Publish"). An active workflow will fire whenever its trigger condition is met.
- **To turn a workflow OFF:** Click the same toggle so it turns **gray** (or click "Unpublish"). The workflow stops firing but all your steps are preserved — you can turn it back on anytime.
- **Quick toggle from the list view:** On the main Automations page, each workflow has a toggle switch in its row. Click it to turn the workflow on or off without opening it.

### Step 7: View Workflow Execution Logs

1. Go to **"Automation"** in the left sidebar.
2. Click on the workflow name.
3. Click the **"Execution Logs"** or **"History"** tab (at the top of the builder, next to the "Builder" tab).
4. You'll see:
   - **Contact name** — who entered the workflow
   - **Date/time** — when the workflow started for that contact
   - **Status** — Completed, In Progress, Failed, or Waiting
   - **Step details** — click a row to expand and see which step they're on
5. If something failed, the failed step will be highlighted in red. Click on it to see the error.

**Common errors and fixes:**

| Error                              | Fix                                                                             |
|------------------------------------|---------------------------------------------------------------------------------|
| SMS failed — no phone number       | Go to the contact, add a phone number in `+1XXXXXXXXXX` format                 |
| Email failed — no email address    | Go to the contact, add an email address                                        |
| Webhook failed — 403/404           | Check the URL is correct (for ntfy: `https://ntfy.sh/tct-xK9mW4vR7pLd`)       |
| Wait step stuck                    | It's just waiting — check back after the wait period (24 hours, 7 days, etc.)  |
| Pipeline stage not moving          | Make sure the contact has an existing opportunity in the Client Lifecycle pipeline. If they don't, the "Update Opportunity" action has nothing to update. Create an opportunity for them first. |
| Tag not triggering workflow        | Check that the workflow is toggled ON. Check the trigger tag name for typos.    |

---

## SECTION 4: Tags Reference

Tags are labels you attach to contacts in GHL. They're used to trigger workflows, segment contacts, and track where each client is in your process. Here's every tag used in The Call Taker system and what it means.

### Lifecycle Tags (Client Status)

These tags track where a client is in the journey from lead to active customer.

| Tag                    | What It Means                                                     | Who/What Adds It                                  |
|------------------------|-------------------------------------------------------------------|---------------------------------------------------|
| `payment-confirmed`    | Client just paid. Triggers the Welcome workflow.                  | You add it manually when payment comes through     |
| `intake-submitted`     | Client filled out the intake form with their business info.       | You add it after receiving the form, or auto via webhook |
| `setup-in-progress`    | You're currently building their AI receptionist.                  | Added automatically by the "Intake Received" workflow |
| `setup-complete`       | Their AI agent is built and ready for testing.                    | You add it manually after finishing the build      |
| `live`                 | Client is live — call forwarding is on, AI is answering.          | You add it manually after forwarding is set up     |
| `active-client`        | Currently paying, active customer.                                | Added automatically by the "Go Live" workflow      |
| `monthly-review-due`   | Time for their monthly performance review.                        | You add it manually each month                     |
| `at-risk`              | Client might churn — low usage, complaints, unhappy.              | You add it manually when you spot warning signs    |
| `churned`              | Client cancelled their subscription.                              | You add it manually when they cancel               |
| `referral-source`      | This client referred another client to you.                       | You add it manually to track referral sources      |

### Plan Tags (What They're Paying For)

Each client should have exactly ONE plan tag.

| Tag            | What It Means                                                          |
|----------------|------------------------------------------------------------------------|
| `after-hours`  | After-Hours plan — $297/mo (AI answers only after business hours)      |
| `starter`      | Starter plan — $497/mo (HVAC, Plumbing, Electrical)                   |
| `pro`          | Pro plan — $997/mo (all other industries including Restoration)       |

### Industry Tags (What Kind of Business They Are)

Each client should have exactly ONE industry tag.

| Tag                    | Industry             |
|------------------------|----------------------|
| `hvac`                 | HVAC                 |
| `plumbing`             | Plumbing             |
| `electrical`           | Electrical           |
| `roofing`              | Roofing              |
| `locksmith`            | Locksmith            |
| `dental`               | Dental               |
| `medspa`               | Med Spa              |
| `legal`                | Legal                |
| `property-management`  | Property Management  |
| `veterinary`           | Veterinary           |
| `towing`               | Towing               |
| `garage-door`          | Garage Door          |
| `funeral`              | Funeral              |

### Other Tags You May See

These tags are used by the automated outreach systems (lead finders, blast engines, etc.) and are less relevant to client onboarding, but you may see them on contacts.

| Tag                   | What It Means                                                    |
|-----------------------|------------------------------------------------------------------|
| `prospect`            | Someone who showed interest but hasn't paid                      |
| `demo-booked`         | Booked a demo call                                               |
| `demo-completed`      | Demo call happened                                               |
| `cold-outreach`       | Found by the lead scraper, never contacted us first              |
| `water-damage`        | Water damage / restoration vertical contact                     |
| `customer`            | General customer tag (used with `water-damage` for WD clients)  |
| `website-visitor`     | Came in through the website                                      |
| `calculator-lead`     | Used the ROI calculator on the website                           |
| `pilot-requested`     | Requested the 14-day free pilot                                  |
| `pilot-active`        | Currently in their 14-day pilot                                  |
| `pilot-expired`       | Pilot ended, didn't convert                                      |
| `pilot-converted`     | Pilot ended, converted to paying client                          |
| `tests-passed`        | All 3 internal test calls passed QA                              |

### How to Add a Tag to a Contact

1. Go to **"Contacts"** in the left sidebar.
2. Find the contact (use the search bar at the top).
3. Click on their name to open their profile.
4. On the right side of the profile (or in a panel/tab labeled "Details"), find the **"Tags"** section.
5. Click in the tags field. Type the tag name exactly as shown above (lowercase, with hyphens).
6. If the tag already exists, it will appear in a dropdown — click it.
7. If it's a new tag, type it out and press Enter to create it.
8. The tag is added immediately. If a workflow is triggered by that tag, the workflow starts running right away.

### How to Remove a Tag from a Contact

1. Open the contact's profile (same as above).
2. Find the **"Tags"** section.
3. Click the **"X"** next to the tag you want to remove.
4. The tag is removed immediately.

---

## Quick Reference: What Fires When

Here's the complete chain of events when a new client comes in, from payment to 14-day review:

```
CLIENT PAYS
  └─ You add tag: payment-confirmed
       └─ WORKFLOW: Welcome — New Client
            ├─ SMS: Welcome message (instant)
            ├─ Email: Welcome + intake form link (5 min)
            └─ SMS: Intake form reminder (15 min)

CLIENT SUBMITS INTAKE FORM
  └─ You add tag: intake-submitted
       └─ WORKFLOW: Intake Received — Start Setup
            ├─ SMS: "We're building it now" (instant)
            ├─ Pipeline: → Intake Form Submitted
            ├─ Tag added: setup-in-progress
            └─ ntfy: "Start setup"

YOU FINISH BUILDING THEIR AI
  └─ You add tag: setup-complete
       └─ WORKFLOW: Setup Complete — Test Calls
            ├─ SMS: "Call your AI and test it" (instant)
            ├─ Pipeline: → Testing
            └─ ntfy: "Run test calls"

CLIENT APPROVES, FORWARDING IS SET UP
  └─ You add tag: live
       └─ WORKFLOW: Go Live — Client Active
       │    ├─ SMS: "You're LIVE!" (instant)
       │    ├─ Email: Full go-live details (5 min)
       │    ├─ Pipeline: → Live / Active
       │    ├─ Tag added: active-client
       │    └─ ntfy: "Client is LIVE!"
       │
       └─ WORKFLOW: 24hr Check-in
       │    └─ Wait 24 hours → SMS: "How's it going?"
       │
       └─ WORKFLOW: 1-Week Check-in
       │    └─ Wait 7 days → Email: "First week check-in"
       │
       └─ WORKFLOW: Review Request — Day 14
            └─ Wait 14 days → SMS: "Leave us a review?"
```

> **Note:** Workflows 4, 5, 6, and 7 all share the same trigger (`live` tag added), so they all start at the same time. The Wait steps in workflows 5, 6, and 7 ensure the messages go out at the right intervals (24 hours, 7 days, 14 days) even though all four workflows started simultaneously.

---

## Troubleshooting

**"I added a tag but nothing happened"**
- Is the workflow turned ON? Check the toggle at the top right of the workflow builder.
- Did you spell the tag exactly right? Tags are case-sensitive. Use all lowercase with hyphens.
- Open the workflow's Execution Logs tab to see if the workflow started but failed at a specific step.

**"The SMS didn't send"**
- Does the contact have a phone number? Open their profile and check.
- Is the phone number in the right format? It should be `+1XXXXXXXXXX` (with country code).
- Check Execution Logs for error messages.

**"The email didn't send"**
- Does the contact have an email address?
- Is your sending email/domain configured in GHL? Go to Settings (gear icon) > Email Services.

**"The pipeline stage didn't update"**
- Does the contact have an opportunity in the Client Lifecycle pipeline? The "Update Opportunity" action can only move existing opportunities — it can't create one from scratch. If they don't have an opportunity yet, add one manually first (go to Opportunities, click "+ Add" in the appropriate stage).

**"I need to stop a workflow for one contact"**
- Open the workflow, go to Execution Logs, find the contact, and click **"Cancel"** or **"Remove from Workflow"** next to their entry.

**"I need to re-run a workflow for a contact"**
- Remove the trigger tag from the contact, wait a few seconds, then add it back. This re-fires the trigger and starts the workflow again from the beginning.
