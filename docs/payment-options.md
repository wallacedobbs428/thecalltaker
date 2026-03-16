# Payment Options — Internal Reference

> Wallace: use this to collect payment from new customers. Goal: send the link via text while on the close call so they complete it before hanging up.

---

## Option 1: Square Recurring Invoices (Recommended)

### Setup (one-time)
1. Go to squareup.com → sign up with your email
2. Dashboard → Invoices → Create Invoice
3. Add customer name + email
4. Line item: "The Call Taker — [Plan Name]" → $[amount]
5. Check "Make this a recurring invoice" → Monthly → Start date = Day 15 of trial
6. Send invoice → customer gets email + text with pay link

### How to send during a call
1. Open Square app on phone
2. Invoices → Create → enter their name + amount
3. Set recurring monthly, start Day 15
4. Send via text (enter their phone number)
5. They tap the link, enter card, done

### Trial structure
- Create the recurring invoice NOW with start date = Day 15
- Customer sees: "First charge: [date]" — no charge today
- Square auto-charges monthly after that

### Fees
- 2.9% + $0.30 per card transaction
- 3.5% + $0.15 for manually keyed cards
- No monthly fee

---

## Option 2: PayPal Subscriptions

### Setup (one-time)
1. Log into paypal.com → Pay & Get Paid → Subscriptions
2. Create Plan: name = "The Call Taker — Starter" (or Pro)
3. Set monthly price: $497 or $997
4. Trial period: 14 days, $0
5. Save → copy the subscription link

### How to send during a call
1. Open your saved subscription links (bookmark them):
   - Starter link: [save after creating]
   - Pro link: [save after creating]
2. Text the link to the customer
3. They tap → log into PayPal or enter card → subscribed

### Trial structure
- PayPal handles it natively: 14-day trial at $0, then auto-bills
- No manual work after setup

### Fees
- 2.99% + $0.49 per transaction
- No monthly fee

---

## Option 3: GoCardless ACH (Lowest Fees)

### Setup (one-time)
1. Go to gocardless.com → sign up
2. Dashboard → Create Payment → Subscription
3. Enter customer email + amount + monthly frequency
4. Start date = Day 15 of trial
5. Send mandate request — customer authorizes via bank account

### How to send during a call
1. GoCardless dashboard → quick create subscription
2. Enter customer email
3. They get an email to authorize bank debit
4. Slightly slower than Square/PayPal (bank auth takes 1-2 min)

### Trial structure
- Set first payment date to Day 15
- No charge during trial
- ACH pulls directly from bank account monthly

### Fees
- 1% + $0.25 per transaction (capped at $5)
- Significantly cheaper than card processing
- Downside: bank-only, no credit card option

---

## Quick Comparison

| Option | Fee on $497 | Fee on $997 | Speed | Trial Support |
|--------|-------------|-------------|-------|---------------|
| **Square** | ~$14.71 | ~$29.21 | Instant (card) | Yes — delayed start |
| **PayPal** | ~$15.35 | ~$30.30 | Instant (card/PayPal) | Yes — native trial |
| **GoCardless** | ~$5.00 | ~$5.00 | 1-2 min (bank auth) | Yes — delayed start |

---

## Sending a Payment Link in Under 60 Seconds

### The move (do this while on the close call):

1. Have your Square/PayPal subscription links saved as phone shortcuts or bookmarks
2. Say: "Let me lock in your trial right now — I'm texting you a link, takes 30 seconds"
3. Open your pre-saved link → text it to their number
4. Stay on the phone: "Got it? Just tap that and put in your card. No charge for 14 days."
5. Wait for them to complete it: "See the confirmation? Perfect. You're all set."

### Pro tip: Save these as text shortcuts on your iPhone
- Settings → General → Keyboard → Text Replacement
- Shortcut: `ppstarter` → expands to full PayPal Starter subscription link
- Shortcut: `pppro` → expands to full PayPal Pro subscription link
- Shortcut: `sqstarter` → expands to full Square Starter invoice link
- Shortcut: `sqpro` → expands to full Square Pro invoice link

Now you type 9 characters and the full link is ready to text.

---

## Recommended Setup Order

1. **Start with PayPal** — easiest trial setup, Wallace already has an account
2. **Add Square** — for customers who don't want PayPal
3. **Add GoCardless later** — when volume justifies the lower fees (10+ customers)

## Notes
- Stripe requires 18+ or parent/guardian — not available yet
- Venmo is fine for one-offs but doesn't do recurring subscriptions
- Always capture payment method DURING the close call — conversion drops 80% if you "send it later"
