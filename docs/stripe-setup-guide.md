# Stripe + GoHighLevel Setup Guide

**For:** Wallace Dobbs / The Call Taker

This guide walks you through every step to connect Stripe so you can take payments.

---

## Part 1: Create Your Stripe Account (10 min)

1. Go to **https://stripe.com**
2. Click **"Start now"**
3. Enter your email, full name, and a strong password
4. Click **"Create account"**
5. Check your inbox and click the verification link

## Part 2: Activate Your Stripe Account

Once logged in, click the **"Activate your account"** banner at the top.

You'll go through these screens:

**Business type:**
- Select **"Sole proprietorship"** (or "LLC" if you have one)

**Business details:**
- Legal business name: **The Call Taker**
- DBA: **The Call Taker**
- Website: `https://wallacedobbs428.github.io/thecalltaker/`
- Industry: **"Computer software"** or **"Telecommunications"**

**Personal details:**
- Your legal name, DOB, address, phone
- Last 4 of SSN (required by law for payment processors)

**Bank account:**
- Select **"Bank account"**
- Enter your routing number (9 digits, bottom-left of a check)
- Enter your account number

Click **"Submit"**. Stripe may take 1-2 days to verify.

---

## Part 3: Connect Stripe to GoHighLevel (5 min)

1. Log in to **https://app.gohighlevel.com**
2. Make sure you're in The Call Taker sub-account (top-left dropdown)
3. Click **"Payments"** in the left sidebar
4. Click **"Integrations"**
   - If you don't see "Payments", click **Settings** (gear icon) > **Payments** > **Integrations**
5. Find the **Stripe** card and click **"Connect"**
6. A popup opens — log in to Stripe if needed
7. Click **"Connect my Stripe account"**
8. You should see a green checkmark / "Connected" status

---

## Part 4: Create Your 3 Products (10 min)

### Product 1: Starter Plan — $297/mo

1. In GHL, click **Payments** > **Products** > **+ Add Product**
2. Product Name: `Starter Plan`
3. Description: `AI receptionist for HVAC companies with 1-5 trucks. 200 calls/month.`
4. Click **"Add Price"**
   - Price Name: `Starter Monthly`
   - Amount: `297`
   - Currency: `USD`
   - Type: **Recurring** > **Monthly**
5. Click **Save**

### Product 2: Professional Plan — $497/mo

1. Click **+ Add Product** again
2. Product Name: `Professional Plan`
3. Description: `AI receptionist for HVAC companies with 5-20 trucks. 500 calls/month.`
4. Click **"Add Price"**
   - Price Name: `Professional Monthly`
   - Amount: `497`
   - Type: **Recurring** > **Monthly**
5. Click **Save**

### Product 3: Enterprise Plan — Custom

1. Click **+ Add Product** again
2. Product Name: `Enterprise Plan`
3. Description: `Custom AI receptionist for 20+ truck operations. Contact us for pricing.`
4. Click **"Add Price"**
   - Price Name: `Enterprise Custom`
   - Amount: `0`
   - Type: **Recurring** > **Monthly**
5. Click **Save**
6. (You'll send custom invoices for Enterprise customers)

### Verify in Stripe

1. Go to **https://dashboard.stripe.com**
2. Click **"Product catalog"** in left sidebar
3. All 3 products should appear there

---

## Part 5: Test a Payment (5 min)

1. In Stripe dashboard, toggle **"Test mode"** ON (top-right)
2. In GHL, go to **Payments** > **Products** > click Starter Plan
3. Click **"Create Payment Link"** > select Starter Plan > Create > Copy link
4. Open a new browser tab, paste the link
5. Fill in test info:
   - Name: `Test Customer`
   - Email: `test@test.com`
   - Card: `4242 4242 4242 4242`
   - Exp: `12/28`
   - CVC: `123`
   - ZIP: `12345`
6. Click **Pay/Subscribe**
7. Check GHL **Payments > Transactions** — you should see $297.00
8. Check Stripe **Payments** — should show "Succeeded"

### GO LIVE

**When ready for real customers:**
1. Go to Stripe dashboard
2. Toggle **"Test mode" OFF**
3. Real cards will now be charged real money
4. Money hits your bank on a 2-day rolling basis

---

## Quick Reference

| Plan | Price | Trucks | Calls/Month |
|------|-------|--------|-------------|
| Starter | $297/mo | 1-5 | 200 |
| Professional | $497/mo | 5-20 | 500 |
| Enterprise | Custom | 20+ | Custom |

---

## Troubleshooting

- **Can't see Payments in GHL?** — Switch from Agency view to sub-account view (top-left dropdown)
- **Stripe Connect button not working?** — Allow pop-ups in your browser. Try Chrome.
- **Test payment failed?** — Use card `4242 4242 4242 4242` exactly. Make sure Test mode is ON.
- **Products not showing in Stripe?** — Wait 1-2 min and refresh. If still missing, disconnect and reconnect Stripe in GHL.
