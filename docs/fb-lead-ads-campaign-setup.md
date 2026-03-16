# Facebook Lead Ads Campaign Setup — Step-by-Step Checklist

> Campaign: Call Taker – Lead Ads – US Home Services
> Budget: $30/day CBO | 3 ad sets | 3 ad variants each
> Goal: Lead form submissions → GHL contact → SMS follow-up → demo booked

---

## PHASE 1: PRE-WORK (Before Opening Ads Manager)

### 1.1 Meta Business Suite Setup
- [ ] Log in to business.facebook.com
- [ ] Confirm your Facebook Page ("The Call Taker") is connected to your Business Suite
- [ ] Go to **Business Settings → Pages** — verify page is listed
- [ ] Go to **Business Settings → Ad Accounts** — verify your ad account is listed (ID: 25895456013410801)

### 1.2 Facebook Pixel (if not already installed)
- [ ] Go to **Events Manager → Data Sources → Pixels**
- [ ] Pixel should already exist from website install — verify it's firing on thecalltaker.com
- [ ] If not: create pixel, add to `<head>` of index.html via tct-tracking.js

### 1.3 Lead Forms Prep
You'll create 3 lead forms (one per ad variant). All share the same fields but different intro copy.

### 1.4 Env Vars Needed for GHL Integration
```
FB_VERIFY_TOKEN=<your-chosen-string>
FB_APP_SECRET=<from-meta-app-settings>
FB_PAGE_ACCESS_TOKEN=<long-lived-page-token>
```
- Get these from developers.facebook.com → Your App → Settings → Basic
- Page Access Token: developers.facebook.com → Your App → Tools → Graph API Explorer → select page → generate token → exchange for long-lived

---

## PHASE 2: CREATE THE CAMPAIGN

### 2.1 Open Ads Manager
- [ ] Go to adsmanager.facebook.com
- [ ] Click **+ Create**

### 2.2 Campaign Level
- [ ] **Campaign Objective:** Select **Leads**
- [ ] **Campaign Name:** `Call Taker – Lead Ads – US Home Services`
- [ ] **Special Ad Categories:** Leave blank (not housing/credit/employment/politics)
- [ ] **Campaign Budget Optimization (CBO):** Toggle **ON**
- [ ] **Daily Budget:** `$30.00`
- [ ] **Bid Strategy:** Lowest cost (leave default — do NOT set a bid cap)
- [ ] Click **Next**

---

## PHASE 3: CREATE AD SET 1 — HVAC

### 3.1 Ad Set Settings
- [ ] **Ad Set Name:** `HVAC Owners`
- [ ] **Conversion Location:** Instant Forms
- [ ] **Facebook Page:** The Call Taker
- [ ] **Performance Goal:** Maximize number of leads

### 3.2 Audience
- [ ] **Location:** United States
- [ ] **Age:** 25 – 65+
- [ ] **Gender:** All

### 3.3 Detailed Targeting
- [ ] Click **Browse → Interests**
- [ ] Add these interests (type each one and select from dropdown):
  - `HVAC`
  - `HVACR`
  - `Air conditioning`
  - `Heating, ventilation, and air conditioning`
  - `Mechanical contractor`
  - `Field service management software`
- [ ] Click **Narrow Further** (this means people must match BOTH groups)
- [ ] Add:
  - `Small business owner`
  - `Entrepreneur`
  - `Business owner`
  - `Contractor`
- [ ] Click **Exclude People**
- [ ] Add:
  - `Student`
  - `Intern`

### 3.4 Placements
- [ ] Select **Advantage+ Placements** (let Meta optimize)
- [ ] OR manually select: Facebook Feed, Instagram Feed, Facebook Marketplace, Instagram Stories (skip Audience Network for lead ads)

### 3.5 Budget & Schedule
- [ ] Leave as CBO-managed (no ad set budget override)
- [ ] Start date: Today
- [ ] End date: Leave open (you'll pause manually)

---

## PHASE 4: CREATE AD SET 2 — PLUMBING

### 4.1 Duplicate Ad Set 1
- [ ] In Ads Manager, select Ad Set 1 → **Duplicate**
- [ ] **Ad Set Name:** `Plumbing Owners`

### 4.2 Change Targeting
- [ ] Remove all HVAC interests
- [ ] Add interests:
  - `Plumbing`
  - `Plumber`
  - `Drain cleaning`
  - `Home improvement`
  - `Field service software`
- [ ] **Narrow Further** (keep same):
  - `Small business owner`
  - `Entrepreneur`
  - `Business owner`
  - `Contractor`
- [ ] **Exclude** (keep same): `Student`, `Intern`
- [ ] Everything else stays the same

---

## PHASE 5: CREATE AD SET 3 — DENTAL

### 5.1 Duplicate Ad Set 1
- [ ] Select Ad Set 1 → **Duplicate**
- [ ] **Ad Set Name:** `Dental Owners`

### 5.2 Change Targeting
- [ ] Remove all HVAC interests
- [ ] Add interests:
  - `Dentist`
  - `Dental practice`
  - `Dental clinic`
  - `Dental software`
- [ ] **Narrow Further**:
  - `Small business owner`
  - `Entrepreneur`
  - `Practice Owner`
- [ ] **Exclude**: `Student`, `Intern`

---

## PHASE 6: CREATE LEAD FORMS (3 Forms)

Go to **Publishing Tools → Forms Library** (or create inline when building ads).

### Form 1: Missed Revenue
- [ ] **Form Name:** `TCT – Missed Revenue Form`
- [ ] **Form Type:** More Volume (Instant Form)
- [ ] **Intro Section:**
  - Headline: `Stop Losing $2K-$10K/Month in Missed Calls`
  - Description: `Fill this out to get a 14-day free trial, no setup fee, flat monthly rate, cancel anytime.`
- [ ] **Questions:**
  1. Full Name (prefilled)
  2. Phone Number → change to **Mobile Number** (prefilled)
  3. Business Name (short answer, custom question)
  4. City/State (short answer, custom question)
  5. What's your biggest phone issue right now? (multiple choice, custom question):
     - `Missed calls during the day`
     - `After-hours and weekend calls`
     - `Hiring/keeping a receptionist`
- [ ] **Privacy Policy URL:** `https://thecalltaker.com/privacy.html`
- [ ] **Thank You Screen:**
  - Headline: `You're In — We'll Be in Touch`
  - Description: `Check your phone for a text from us in the next 60 seconds. We'll get your free trial set up today.`
  - Button: `Call Our Demo Line` → link to `tel:+16157845747`
- [ ] Click **Publish**

### Form 2: After-Hours Lifeline
- [ ] **Form Name:** `TCT – After-Hours Lifeline Form`
- [ ] Same fields as Form 1
- [ ] **Intro Headline:** `Who's Answering Your Phones at 9 PM?`
- [ ] **Intro Description:** `Fill this out to get a 14-day free trial, no setup fee, flat monthly rate, cancel anytime.`
- [ ] Same thank you screen
- [ ] Click **Publish**

### Form 3: Hiring Headache Relief
- [ ] **Form Name:** `TCT – Hiring Headache Form`
- [ ] Same fields as Form 1
- [ ] **Intro Headline:** `Stop Hiring Receptionists. Start Answering Every Call.`
- [ ] **Intro Description:** `Fill this out to get a 14-day free trial, no setup fee, flat monthly rate, cancel anytime.`
- [ ] Same thank you screen
- [ ] Click **Publish**

---

## PHASE 7: CREATE ADS (3 per Ad Set = 9 Total)

### For EACH ad set, create 3 ads:

#### Ad 1: Missed Revenue
- [ ] **Ad Name:** `Missed Revenue – [VERTICAL]` (e.g., `Missed Revenue – HVAC`)
- [ ] **Primary Text:**
```
Last weekend, your phone rang at 9:47 PM. Nobody picked up.

That customer called your competitor. $500 job — gone.

We built a smart receptionist that answers every call in 2 rings, 24/7. Books the appointment. Texts you the details.

14-day free trial. No setup fee. No contracts.
```
- [ ] **Headline:** `Stop Losing $2K-$10K/Month in Missed Calls`
- [ ] **Description:** `Smart 24/7 answering. Setup in 24 hours. Cancel anytime.`
- [ ] **CTA Button:** Sign Up
- [ ] **Instant Form:** Select `TCT – Missed Revenue Form`
- [ ] **Tracking:**
  - URL Parameters: `utm_source=facebook&utm_medium=paid&utm_campaign=lead-ads-home-services&utm_content=missed-revenue-[vertical]`

#### Ad 2: After-Hours Lifeline
- [ ] **Ad Name:** `After-Hours Lifeline – [VERTICAL]`
- [ ] **Primary Text:**
```
Saturday morning. You're finally off. Then your phone rings.

A customer needs help NOW. But you're at your kid's soccer game.

What if someone professional answered that call? Got the details. Booked the appointment. Texted you a summary.

That's what we do. 24/7 answering that sounds like a real person.

14-day free trial. See how many calls you're missing.
```
- [ ] **Headline:** `Who's Answering Your Phones at 9 PM?`
- [ ] **Description:** `24/7 smart answering. No contracts. Free 14-day trial.`
- [ ] **CTA Button:** Learn More
- [ ] **Instant Form:** Select `TCT – After-Hours Lifeline Form`
- [ ] **Tracking:**
  - URL Parameters: `utm_source=facebook&utm_medium=paid&utm_campaign=lead-ads-home-services&utm_content=after-hours-[vertical]`

#### Ad 3: Hiring Headache Relief
- [ ] **Ad Name:** `Hiring Headache – [VERTICAL]`
- [ ] **Primary Text:**
```
Hiring a receptionist: $2,500/month + benefits + sick days + turnover.

Or: a smart receptionist that answers every call, 24/7, never takes a day off, and costs less than $10/day.

Books appointments. Handles FAQs. Texts you when it's urgent.

Your customers can't tell the difference. Your bank account can.

14-day free trial. $97/month after that.
```
- [ ] **Headline:** `Stop Hiring Receptionists. Start Answering Every Call.`
- [ ] **Description:** `$97/mo vs $2,500/mo for a receptionist. Free 14-day trial.`
- [ ] **CTA Button:** Get Offer
- [ ] **Instant Form:** Select `TCT – Hiring Headache Form`
- [ ] **Tracking:**
  - URL Parameters: `utm_source=facebook&utm_medium=paid&utm_campaign=lead-ads-home-services&utm_content=hiring-headache-[vertical]`

### Repeat for all 3 ad sets
- [ ] HVAC ad set: 3 ads created
- [ ] Plumbing ad set: 3 ads created
- [ ] Dental ad set: 3 ads created

---

## PHASE 8: CONNECT GHL INTEGRATION

### Option A: Facebook-GHL Native Integration (Recommended — Fastest)
- [ ] In GHL: Go to **Settings → Integrations → Facebook**
- [ ] Connect your Facebook account
- [ ] Select your Facebook Page
- [ ] Map each lead form to GHL:
  - Map `full_name` → Contact Name
  - Map `phone_number` → Phone
  - Map `business_name` → Company Name
  - Map `city_state` → Address
  - Map `phone_issue` → Custom Field (create if needed)
- [ ] Enable auto-tagging: `facebook-lead`
- [ ] This gives you instant leads in GHL without a webhook server

### Option B: Custom Webhook (Already Built)
- [ ] Deploy `ops/facebook-lead-webhook.py` (already in repo — port 5091)
- [ ] Set environment variables: `FB_VERIFY_TOKEN`, `FB_APP_SECRET`, `FB_PAGE_ACCESS_TOKEN`
- [ ] Expose port 5091 via ngrok or Cloudflare Tunnel
- [ ] In Meta App → Webhooks → subscribe `leadgen` field to your page

### Deploy the Follow-Up Engine
- [ ] Deploy `ops/fb-lead-ads-engine.py` (new script in this commit)
- [ ] Install launchd plists:
```bash
cp ops/com.thecalltaker.fb-leads.scan.plist ~/Library/LaunchAgents/
cp ops/com.thecalltaker.fb-leads.followup.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.thecalltaker.fb-leads.scan.plist
launchctl load ~/Library/LaunchAgents/com.thecalltaker.fb-leads.followup.plist
```

---

## PHASE 9: PRE-PUBLISH CHECKLIST

- [ ] All 3 ad sets have correct targeting (verify interests match spec)
- [ ] All 9 ads have correct form linked
- [ ] All 3 forms have correct fields (Full Name, Mobile Number, Business Name, City/State, Phone Issue dropdown)
- [ ] Privacy policy URL works: thecalltaker.com/privacy.html
- [ ] Thank you screen CTA calls demo line
- [ ] UTM parameters are set on all 9 ads
- [ ] GHL integration is connected (Option A or B)
- [ ] `fb-lead-ads-engine.py` is deployed and running
- [ ] Test: Submit a test lead through each form → verify it appears in GHL with correct tags
- [ ] Budget confirmed: $30/day CBO

---

## PHASE 10: PUBLISH

- [ ] Click **Publish** in Ads Manager
- [ ] Ads go into review (usually 15 minutes to 24 hours)
- [ ] Once approved: verify first real lead comes through correctly
- [ ] Start the Day 1-7 playbook (see `docs/fb-lead-ads-playbook.md`)

---

## NAMING CONVENTION REFERENCE

| Item | Naming Pattern |
|------|---------------|
| Campaign | `Call Taker – Lead Ads – US Home Services` |
| Ad Set | `[Vertical] Owners` (e.g., HVAC Owners) |
| Ad | `[Variant] – [Vertical]` (e.g., Missed Revenue – HVAC) |
| Form | `TCT – [Variant] Form` |
| GHL Tags | `facebook-lead`, `fb-[variant]`, `[vertical]` |
| UTM Content | `[variant]-[vertical]` (e.g., missed-revenue-hvac) |

## AD COPY RULES
- NEVER use "AI" or "artificial intelligence"
- NEVER use "bot" or "automated"
- DO use: "smart receptionist", "24/7 answering", "never miss a call"
- Focus on MISSED REVENUE, not technology
