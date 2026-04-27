# Wallace's To-Do List — Tonight
**Date:** February 14, 2026
**Goal:** 45 paying clients by May 31, 2026 — $33,000 MRR ($100K by May 2026)

---

## CRITICAL (Must do to accept clients)

### ☐ 1. Create Stripe Account & Connect to legacy CRM
📍 stripe.com → Sign up
👆 Create account, verify identity (needs SSN or EIN + bank account), then go to legacy CRM Settings → Payments → Connect Stripe
⏱ 30-45 minutes (verification can take 1-2 business days)
🔑 Bank account info, SSN or EIN, business address

### ☐ 2. Create Stripe Products for Each Plan
📍 Stripe Dashboard → Products → Add Product
👆 Create 3 recurring products:
  - "Starter" — $297/month
  - "Professional" — $497/month
  - "Enterprise" — custom (create as quote-based)
Generate a Payment Link for each product
⏱ 10 minutes
🔑 Stripe dashboard access

### ☐ 3. Add Stripe Payment Links to Home Page Pricing Section
📍 /Users/millsthaverner/Desktop/wallace-hvac/website/index.html (pricing section near bottom)
👆 Replace the 3 "Get Started" / "Contact Us" button href="demo.html" values with your Stripe Payment Link URLs, then push to GitHub
⏱ 5 minutes
🔑 The Stripe Payment Link URLs from step 2

### ✅ 4. Custom Domain — DONE
Website live at https://thecalltaker.com/ via Wallace's GitHub repo (wallacedobbs428/thecalltaker).

### ☐ 5. Paste Welcome Email Content into legacy CRM Templates
📍 legacy CRM → Marketing → Emails → Templates
👆 Open each of the 5 "The Call Taker - Welcome" email template shells and paste the content from /Users/millsthaverner/Desktop/wallace-hvac/onboarding/welcome-email-sequence.md
⏱ 20 minutes
🔑 legacy CRM dashboard access

---

## IMPORTANT (Should do this week)

### ☐ 6. Delete Test Voice Agents
📍 legacy CRM → Settings → Conversation AI → Voice AI
👆 Delete the 6 test agents (keep only "The Call Taker - HVAC AI Receptionist" on +16292699697)
⏱ 5 minutes
🔑 legacy CRM dashboard access

### ☐ 7. Activate "New Lead Nurture" Workflow
📍 legacy CRM → Automation → Workflows → "1. New Lead Nurture (Fast 5)"
👆 Review the workflow steps, then change status from Draft to Published
⏱ 5 minutes
🔑 legacy CRM dashboard access

### ☐ 8. Review & Rename Unnamed Workflows
📍 legacy CRM → Automation → Workflows
👆 Find the 3 workflows with timestamp names (1767294037970, 1767457230352, 1770958676732). Review what each does — rename with descriptive names or delete if they're test workflows
⏱ 10 minutes
🔑 legacy CRM dashboard access

### ☐ 9. Test the Admin Setup Wizard
📍 Open /Users/millsthaverner/Desktop/wallace-hvac/website/admin-setup.html in your browser
👆 Password is: calltaker2026. Fill in a test client, submit, verify agent appears in legacy CRM, then delete the test agent
⏱ 10 minutes
🔑 Browser + legacy CRM dashboard to verify

---

## NICE TO HAVE (When you get a chance)

### ☐ 10. Fix Inactive Service Calendars
📍 legacy CRM → Calendars
👆 Either activate the 4 HVAC service calendars (Installation, Repair, Air Quality, Maintenance) with correct hours, or delete them if not needed
⏱ 10 minutes
🔑 legacy CRM dashboard access

### ☐ 11. Clean Up Duplicate Tags
📍 legacy CRM → Settings → Tags
👆 Merge "follow-up" and "follow-up-needed" into one tag
⏱ 2 minutes
🔑 legacy CRM dashboard access

### ✅ 12. Push Website Updates to GitHub — DONE
Website redesigned (2-page dark+green theme), committed, and pushed to GitHub Pages.

---

## Total Estimated Time: ~2 hours
## Items that block scaling to 10 clients: #1-#5
