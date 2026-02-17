# STRIPE SETUP GUIDE FOR THE CALL TAKER
**Complete Payment System Setup — $497/Month Recurring Billing**

Wallace, this guide will take you from zero to collecting payments in under 30 minutes. Follow every step in order. Don't skip anything.

---

## PART 1: CREATE YOUR STRIPE ACCOUNT

### Step 1: Sign Up for Stripe
1. Go to https://stripe.com
2. Click **"Start now"** (top right)
3. Enter your email: **wallacemdobbs@icloud.com**
4. Create a strong password (write it down somewhere secure)
5. Agree to terms and click **"Create account"**

### Step 2: Verify Your Email
1. Check your email inbox for "Verify your email address for Stripe"
2. Click the verification link
3. You'll be redirected back to Stripe

### Step 3: Choose Your Country and Business Type
1. **Country:** United States
2. **Business type:** Individual (if just you) OR Sole proprietorship (if you have an LLC/DBA registered)
3. Click **"Continue"**

**NOTE:** At 19, you're legally eligible for Stripe. If they ask for additional verification, you may need to provide:
- Social Security Number (SSN)
- Date of birth
- Home address
- Bank account for payouts

### Step 4: Complete Business Profile
You'll need to fill out the Stripe onboarding form. Here's what to enter:

**Business Information:**
- **Business name:** The Call Taker
- **Business website:** https://thecalltaker.com
- **Industry:** Business Services (or Software as a Service)
- **Product description:** "AI phone receptionist service for HVAC companies"
- **Your name:** Wallace Dobbs
- **Phone number:** [Your phone number]

**Personal Information (for sole prop/individual):**
- **SSN:** [Your social security number]
- **Date of birth:** [Your DOB]
- **Home address:** [Your current residential address]

**Bank Account for Payouts:**
- You'll need to connect a bank account where Stripe will deposit your money
- **Routing number:** [Your bank's routing number]
- **Account number:** [Your checking account number]
- Stripe will make 2 small deposits (under $1) to verify — check your bank in 1-2 days and enter the amounts

### Step 5: Enable Payment Methods
1. Once your profile is submitted, go to **Settings** (gear icon, top right)
2. Click **"Payment methods"** in the left sidebar
3. Make sure **"Card"** is enabled (should be on by default)
4. You can also enable:
   - **ACH Direct Debit** (bank transfers — good for clients who prefer this)
   - **Link** (Stripe's 1-click payment method)
5. Click **"Save"** if you made changes

**Your Stripe account is now ACTIVE.** You can start accepting payments immediately, even while your bank account verification is pending (funds will just be held until verification completes).

---

## PART 2: CREATE YOUR $497/MONTH PRODUCT

### Step 6: Create a Recurring Product
1. In your Stripe Dashboard, click **"Products"** in the left sidebar
2. Click **"Add product"** (top right)
3. Fill out the product details:

**Product Information:**
- **Name:** The Call Taker — AI Receptionist Service
- **Description:** 24/7 AI phone receptionist for HVAC companies. Answers every call, books appointments, captures leads. No contracts, cancel anytime.
- **Image:** (Optional — skip for now, add later if you want)

**Pricing:**
- **Pricing model:** Select **"Standard pricing"**
- **Price:** $497.00
- **Billing period:** Monthly (Recurring)
- **Currency:** USD

**Additional Options:**
- **Trial period:** Leave blank (no free trial)
- **Usage is metered:** Leave unchecked

4. Click **"Add product"**

### Step 7: Copy Your Price ID
1. After creating the product, you'll see it listed under **Products**
2. Click on **"The Call Taker — AI Receptionist Service"**
3. In the Pricing section, you'll see your price (e.g., "$497.00 / month")
4. Click on the price
5. You'll see a **Price ID** that looks like `price_1Abc123XYZ...`
6. **COPY THIS PRICE ID** — you'll need it in a minute

---

## PART 3: CREATE A PAYMENT LINK

### Step 8: Create a Payment Link for Clients
1. In Stripe Dashboard, click **"Payment links"** in the left sidebar
2. Click **"New"** (top right)
3. Select **"The Call Taker — AI Receptionist Service"** from the dropdown
4. Configure the link:

**Product details:**
- Product: The Call Taker — AI Receptionist Service (already selected)
- Quantity: 1 (fixed)

**Collect customer information:**
- Check **"Name"**
- Check **"Email"**
- Check **"Phone number"**
- Check **"Billing address"**

**Payment page:**
- **Custom message:** (Optional) "Welcome to The Call Taker! Your AI receptionist will be live within 48 hours of payment. You'll receive an email with next steps."
- **After payment:** Select **"Show a confirmation page"**
- **Custom thank you page:** (Optional — leave blank for now, or enter https://thecalltaker.com/thank-you if you build one later)

**Advanced settings:**
- **Allow promotion codes:** (Optional — check this if you want to offer discount codes later)
- **Require billing address:** Checked (helps prevent fraud)

5. Click **"Create link"**

### Step 9: Copy Your Payment Link
1. After creating the link, you'll see a shareable URL like: `https://buy.stripe.com/abc123xyz`
2. **COPY THIS URL** — this is what you'll send to clients
3. Test it yourself:
   - Open the link in a private/incognito browser window
   - You should see a clean payment page with your product, price, and Stripe branding
   - **DO NOT complete a real payment yet — we'll test with a test card in a minute**

---

## PART 4: CONNECT STRIPE TO GOHIGHLEVEL

### Step 10: Get Your Stripe API Keys
1. In Stripe Dashboard, click **Settings** (gear icon, top right)
2. Click **"API keys"** in the left sidebar under Developers
3. You'll see two keys:
   - **Publishable key** (starts with `pk_live_...`)
   - **Secret key** (starts with `sk_live_...` — click "Reveal live key token" to see it)
4. **COPY BOTH KEYS** — you'll paste them into GHL in a second

**SECURITY WARNING:** Your secret key is like a password. NEVER share it publicly, commit it to GitHub, or paste it in Slack/Discord. Only paste it into GHL.

### Step 11: Connect Stripe to GoHighLevel
1. Log into your GoHighLevel account
2. Click **Settings** (gear icon, bottom left)
3. Click **"Integrations"** in the left sidebar
4. Scroll down and find **"Stripe"**
5. Click **"Connect"** or **"Configure"**
6. You'll see two fields:
   - **Publishable Key:** Paste your `pk_live_...` key
   - **Secret Key:** Paste your `sk_live_...` key
7. Click **"Save"** or **"Connect"**

**Test the connection:**
- GHL should show "Connected" with a green checkmark
- If you get an error, double-check you copied the full keys (no extra spaces)

### Step 12: Enable Stripe Payments in Your GHL Location
1. Go to **Settings > Business Profile** (or "My Business")
2. Scroll down to **"Payment Integrations"**
3. Make sure **Stripe** is listed as **"Active"**
4. If not, click **"Manage"** and enable it

---

## PART 5: SET UP AUTOMATIC INVOICING IN GHL

### Step 13: Create an Invoice Template (Optional but Recommended)
1. In GHL, go to **Payments > Invoices**
2. Click **"Templates"** at the top
3. Click **"Create Template"**
4. Fill out:
   - **Template Name:** The Call Taker — Monthly Service
   - **Product/Service:** AI Receptionist Service
   - **Description:** 24/7 AI phone receptionist for [Client Company Name]
   - **Amount:** $497.00
   - **Recurring:** Monthly
5. Save the template

**You can now use this template to quickly generate invoices for new clients.**

### Step 14: Send an Invoice (When a Client Says Yes)
1. Go to **Payments > Invoices**
2. Click **"Create Invoice"**
3. Select the client's contact record (or create one if it doesn't exist)
4. Use the template you just created OR enter:
   - **Product/Service:** AI Receptionist Service
   - **Amount:** $497.00
   - **Recurring:** Monthly (on the anniversary of first payment)
5. Click **"Send Invoice"**
6. The client will receive an email with a link to pay via Stripe

---

## PART 6: CREATE A "DEAL WON" PAYMENT FLOW

This is the workflow that fires automatically when you close a deal in GHL.

### Step 15: Build the "Deal Won → Payment" Workflow
1. In GHL, go to **Automation > Workflows**
2. Click **"Create Workflow"**
3. Name it: **"TC - Sales - Deal Won Payment"**
4. Set the trigger:
   - **Trigger Type:** Opportunity Status Changed
   - **Pipeline:** [Your sales pipeline name, e.g., "Lead Pipeline"]
   - **Status:** Closed Won (or whatever you named your "client signed" stage)

5. Add actions:

**ACTION 1: Send Payment Link Email**
- **Action Type:** Send Email
- **From Name:** Wallace Dobbs
- **From Email:** wallacemdobbs@icloud.com
- **Subject:** Let's Get You Started — Payment & Next Steps
- **Body:**
```
Hi {{contact.first_name}},

Excited to get your AI receptionist up and running!

Here's what happens next:

1. Complete your payment using the secure link below ($497/month, billed monthly, cancel anytime)
2. Fill out the onboarding form I'll send in the next email
3. Your AI receptionist will be LIVE within 48 hours

PAYMENT LINK: [Paste your Stripe payment link here]

Questions? Just reply to this email or call me at [your phone number].

Let's do this,
Wallace Dobbs
The Call Taker
wallacemdobbs@icloud.com
(615) 784-5747
```

**ACTION 2: Send Onboarding Form**
- **Action Type:** Send Email (or SMS, depending on your preference)
- **Subject:** Onboarding Form — We Need a Few Details
- **Body:**
```
Hi {{contact.first_name}},

To build your custom AI receptionist, I need a few details about your business.

Please fill out this quick form (takes 5 minutes): [Link to your GHL onboarding form]

Once you've paid and submitted this form, we'll have you live within 48 hours.

Thanks,
Wallace
```

**ACTION 3: Internal Notification to You**
- **Action Type:** Send Internal Notification (or Email to wallacemdobbs@icloud.com)
- **Message:**
```
NEW CLIENT ALERT!

{{contact.first_name}} {{contact.last_name}} just moved to Closed Won.

Payment link and onboarding form sent automatically.

NEXT STEPS:
1. Wait for payment confirmation
2. Wait for onboarding form submission
3. Build their AI agent in GHL
4. Go live within 48 hours

Contact: {{contact.phone}}
Company: {{contact.company_name}}
```

6. Click **"Save"** and **"Publish"**

**Now, every time you move a deal to "Closed Won" in your pipeline, this workflow fires automatically.**

---

## PART 7: TEST WITH STRIPE TEST CARDS

Before you send payment links to real clients, TEST EVERYTHING.

### Step 16: Switch to Test Mode (Optional — Recommended for First-Time Testing)
1. In Stripe Dashboard, you'll see a toggle at the top: **"Test mode"**
2. Switch it ON (it should say "Viewing test data")
3. Repeat Steps 6-9 to create a test product and test payment link (in test mode)
4. Copy the test payment link

### Step 17: Test a Payment
1. Open your test payment link in a private/incognito browser
2. Enter test customer info:
   - **Email:** test@example.com
   - **Name:** Test Customer
   - **Phone:** 555-123-4567
3. For the card details, use Stripe's test card numbers:

**Successful Payment:**
- **Card Number:** 4242 4242 4242 4242
- **Expiration:** Any future date (e.g., 12/28)
- **CVC:** Any 3 digits (e.g., 123)
- **ZIP:** Any 5 digits (e.g., 12345)

**Declined Payment (to test errors):**
- **Card Number:** 4000 0000 0000 0002
- **Expiration:** Any future date
- **CVC:** Any 3 digits
- **ZIP:** Any 5 digits

4. Click **"Subscribe"**
5. If successful, you should see a confirmation page
6. Go to your Stripe Dashboard > **Customers** — you should see "Test Customer" listed
7. Go to **Payments** — you should see a $497.00 payment

### Step 18: Test the GHL Workflow
1. In GHL, create a test contact (e.g., "Test HVAC Company")
2. Add them to your sales pipeline as a new opportunity
3. Move them to **"Closed Won"**
4. Check your email — you should receive the internal notification
5. Check the test contact's activity — they should have received the payment link email

**If everything works, you're ready to go LIVE.**

### Step 19: Switch Back to Live Mode
1. In Stripe Dashboard, toggle **"Test mode"** OFF
2. You'll now be viewing live data
3. Your live payment link (from Step 9) is ready to send to real clients

---

## PART 8: WHAT CLIENTS SEE WHEN THEY PAY

When you send a client your Stripe payment link, here's their experience:

1. They click the link
2. They see a clean Stripe-hosted payment page with:
   - **Product name:** The Call Taker — AI Receptionist Service
   - **Price:** $497.00 / month
   - **Description:** (if you added one)
   - Fields to enter: Name, Email, Phone, Billing Address, Card Info
3. They enter their payment details and click **"Subscribe"**
4. Stripe processes the payment instantly
5. They see a confirmation page: "Payment successful!"
6. They receive an email receipt from Stripe
7. **You receive:**
   - Email notification from Stripe (payment successful)
   - Notification in your GHL workflow (if set up)
   - The payment shows in your Stripe Dashboard under **Payments**
   - The customer is added to your Stripe **Customers** list with a recurring subscription

**Recurring billing:**
- Stripe will automatically charge them $497 every month on the anniversary of their first payment
- If the payment fails (expired card, insufficient funds), Stripe will retry automatically and email the customer
- You'll get an email notification if a payment fails

---

## PART 9: HOW TO HANDLE CANCELLATIONS

When a client wants to cancel, here's what to do:

### Step 20: Cancel a Subscription in Stripe
1. Log into Stripe Dashboard
2. Go to **Customers**
3. Find the client you need to cancel
4. Click on their name
5. Under **"Subscriptions"**, you'll see their active $497/month subscription
6. Click on the subscription
7. Click **"Cancel subscription"** (top right)
8. Choose one of two options:
   - **Cancel immediately:** They lose access now, no refund
   - **Cancel at period end:** They keep access until the end of their current billing cycle (most common — use this)
9. Add a cancellation reason (optional, but helpful for tracking): "Client requested cancellation" or "Churn — not satisfied" or "Churn — too expensive"
10. Click **"Cancel subscription"**

**What happens after cancellation:**
- The client will NOT be charged again
- They'll receive an email from Stripe confirming the cancellation
- You'll receive an email notification
- You should also:
  - Mark them as "Churned" or "Cancelled" in your GHL pipeline
  - Send a goodbye email (optional): "Sorry to see you go! If you ever need us again, we're here."
  - Forward their AI agent's phone number to their direct line OR turn it off

### Step 21: Track Churn in GHL
1. In GHL, go to your sales pipeline
2. Add a new stage called **"Churned"** or **"Cancelled"**
3. When a client cancels, move their deal to this stage
4. This lets you track churn rate over time

**Monthly churn goal:** Under 10% (if you have 10 clients, lose fewer than 1/month)

---

## PART 10: STRIPE DASHBOARD TOUR — WHERE TO FIND THINGS

Here's what you'll use most often:

**Home:**
- Quick overview of payments, customers, disputes

**Payments:**
- Every payment that comes in (successful, failed, refunded)
- Click on a payment to see details, issue refunds, send receipts

**Customers:**
- Full list of every customer
- Click on a customer to see their payment history, subscriptions, contact info

**Subscriptions:**
- All active, past due, and canceled subscriptions
- Filter by status

**Products:**
- Your service offerings (you should only have one: The Call Taker — AI Receptionist Service)

**Payment links:**
- The shareable links you send to clients
- Track clicks, conversions

**Disputes:**
- If a client files a chargeback (rare but happens)
- You'll need to respond with proof of service (emails, call logs, contracts)

**Payouts:**
- Money Stripe transfers to your bank account
- Default schedule: every 2 business days (you can change this to daily or weekly in Settings > Payouts)

**Reports:**
- Revenue reports, tax reports, reconciliation

**Settings:**
- API keys, webhooks, payment methods, branding, notifications

---

## QUICK REFERENCE: DEAL WON TO GO-LIVE CHECKLIST

When a client says YES, here's your exact workflow:

### THE 48-HOUR CLIENT ONBOARDING PROCESS

**HOUR 0 (Immediately after "Closed Won"):**
- [ ] GHL workflow auto-sends payment link + onboarding form
- [ ] You receive internal notification

**HOUR 0-12 (Wait for client action):**
- [ ] Client pays via Stripe (you get email confirmation)
- [ ] Client fills out onboarding form (you get GHL notification)

**HOUR 12-24 (Build their AI agent):**
- [ ] Create new sub-account in GHL (if you're using sub-accounts per client)
- [ ] Set up their AI voice agent:
   - Business name, hours, services, pricing, emergency protocol
   - Use their onboarding form answers
- [ ] Configure call forwarding number
- [ ] Test the AI agent (call it 3 times, score it)

**HOUR 24-36 (Send go-live instructions):**
- [ ] Email client with:
   - AI agent phone number
   - Call forwarding setup instructions
   - "Your AI is LIVE — test it yourself by calling [number]"
   - "Forward your business line to [AI number] when you're ready"

**HOUR 36-48 (Go live + first check-in):**
- [ ] Client forwards their calls
- [ ] Monitor first 10 calls closely
- [ ] Email or call client: "How's it going? Any issues?"

**DAY 7 (First week check-in):**
- [ ] Email: "Your AI answered [X] calls this week. Everything working smoothly?"
- [ ] Ask for testimonial if they're happy

**DAY 30 (First month check-in):**
- [ ] Send first monthly report (calls answered, appointments booked, duration)
- [ ] Ask: "Anything we can improve?"

---

## TROUBLESHOOTING

**"Stripe won't verify my bank account"**
- It takes 1-2 business days for the micro-deposits to show up
- Check your bank's transaction history for two small deposits under $1 from Stripe
- Enter the exact amounts in Stripe Dashboard > Settings > Bank accounts

**"GHL says my Stripe keys are invalid"**
- Make sure you copied the FULL key (they're long — 80+ characters)
- Make sure you're using LIVE keys, not test keys (live keys start with `pk_live_` and `sk_live_`)
- Try disconnecting and reconnecting in GHL > Integrations

**"A client's card was declined"**
- Stripe will automatically retry the payment 3 times over 2 weeks
- The client will receive an email asking them to update their card
- If payment fails after all retries, the subscription is canceled automatically
- You'll get an email notification — reach out to the client and ask them to update their card

**"I need to issue a refund"**
- Go to Stripe Dashboard > Payments
- Find the payment you want to refund
- Click on it, then click "Refund payment" (top right)
- Enter the refund amount ($497.00 for full refund, or partial)
- Click "Refund"
- The client will see the refund in 5-10 business days
- NOTE: Stripe does NOT refund their fee (2.9% + $0.30), so you'll lose ~$15 on a full refund

**"How do I change my pricing?"**
- Go to Products > The Call Taker — AI Receptionist Service > Add price
- Create a new price (e.g., $597/month)
- All NEW customers will use the new price
- Existing customers stay at their original price UNLESS you manually migrate them
- To migrate existing customers: go to their subscription > Update plan > select new price

**"How do I offer a discount?"**
- Go to Products > The Call Taker — AI Receptionist Service
- Click "Add coupon"
- Create a coupon code (e.g., "LAUNCH50" for $50 off first month)
- When creating a payment link, enable "Allow promotion codes"
- Give the coupon code to clients manually (they enter it at checkout)

**"Stripe is holding my money / payouts are paused"**
- This can happen if:
  - Your account is brand new (Stripe holds funds for 7 days for new accounts as fraud protection)
  - You received a chargeback or dispute
  - Stripe detected unusual activity
- Solution: Go to Dashboard > Payouts and see if there's a message. If unclear, contact Stripe support (they're very responsive)

**"A client filed a chargeback / dispute"**
- Go to Stripe Dashboard > Disputes
- Click on the dispute
- You have 7-14 days to respond (depending on card network)
- Submit evidence:
  - Emails showing the client agreed to the service
  - Call logs showing the AI agent was working
  - GHL activity logs showing the client was using the service
- Stripe will review and make a decision
- If you win, you get the money back. If you lose, Stripe takes the $497 + a $15 dispute fee.

---

## STRIPE FEES (Know Your Costs)

**Per transaction:**
- 2.9% + $0.30 per successful charge
- On a $497 payment, you pay: ($497 × 0.029) + $0.30 = **$14.71 per payment**
- You keep: $497 - $14.71 = **$482.29**

**Monthly revenue math:**
- 1 client = $482.29/month profit (after Stripe fees)
- 5 clients = $2,411.45/month
- 10 clients = $4,822.90/month
- 20 clients = $9,645.80/month

**Chargeback fee:**
- $15 per dispute (even if you win)

**No monthly fees, no setup fees, no hidden costs.**

---

## FINAL CHECKLIST — BEFORE YOU SEND YOUR FIRST PAYMENT LINK

- [ ] Stripe account created and verified
- [ ] Bank account connected and verified (or pending verification — ok to proceed)
- [ ] Product created: "The Call Taker — AI Receptionist Service" at $497/month recurring
- [ ] Payment link created and tested with test card (4242 4242 4242 4242)
- [ ] Stripe connected to GHL (green checkmark in Integrations)
- [ ] "Deal Won → Payment" workflow created and tested
- [ ] Invoice template created (optional but recommended)
- [ ] You've tested the full flow: move deal to Closed Won → workflow fires → email sent → test payment → confirmation

**When all boxes are checked, you're ready to send payment links to real clients.**

---

## SUPPORT RESOURCES

**Stripe Support:**
- Dashboard: Click "?" icon (bottom right) > "Contact support"
- Email: support@stripe.com
- Phone: +1 888-926-2289
- Response time: Usually within 4-8 hours

**GHL Support:**
- Help Desk: support.gohighlevel.com
- Live Chat: Click "?" icon in GHL dashboard
- Facebook Group: GoHighLevel Marketers & Entrepreneurs (very active)

**Stripe Documentation:**
- https://stripe.com/docs/billing/subscriptions/overview
- https://stripe.com/docs/payments/payment-links

**This guide last updated:** February 16, 2026

---

Wallace, you now have a complete payment system. When your first client says yes:

1. Move them to Closed Won in GHL
2. Workflow auto-sends payment link
3. They pay via Stripe
4. You get notified
5. You build their AI agent
6. They go live within 48 hours
7. Stripe auto-bills them every month
8. You get paid every 2 days to your bank account

That's it. Now go close some deals.

— Your Command Center
