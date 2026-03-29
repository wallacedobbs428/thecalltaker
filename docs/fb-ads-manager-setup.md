# Facebook Lead Ads — Ads Manager Setup Guide
**For Wallace — Follow these steps click-by-click in Meta Ads Manager**
**Target: Live by 9AM tomorrow**

---

## STEP 1: Create Campaign

1. Go to **ads.facebook.com** → click **+ Create**
2. Choose objective: **Leads**
3. Campaign name: `Call Taker – Lead Ads – US Small Business`
4. Turn ON **Campaign Budget Optimization (CBO)**
5. Set daily budget: **$50/day**
6. Bid strategy: **Lowest cost** (default)
7. Click **Next**

---

## STEP 2: Create Ad Set

1. Ad set name: `US – Service Business Owners – 25-65+`
2. **Lead method:** Instant Forms (on Facebook/Instagram)
3. **Location:** United States
4. **Age:** 25–65+
5. **Detailed targeting — Interests (add ALL of these):**
   - Small business owner
   - Entrepreneur
   - HVAC
   - Plumbing
   - Roofing
   - Pest control
   - Dentist
   - Electrician
   - Locksmith
   - Home services
   - Service business
6. **Placements:** Manual placements → select ONLY:
   - Facebook Feed
   - Instagram Feed
   - (UNCHECK everything else — no Audience Network, no Stories, no Reels)
7. **Optimization:** Leads
8. Click **Next**

---

## STEP 3: Create 3 Ads

Create all 3 ads inside the same ad set.

### Ad 1: Missed Revenue
- Ad name: `Ad 1 – Missed Revenue`
- Use copy from `docs/fb-ads-final-copy.md` → Variant 1
- CTA button: **Sign Up**
- Image: Use a photo of a phone ringing with no one answering, or a frustrated business owner

### Ad 2: After-Hours Lifeline
- Ad name: `Ad 2 – After-Hours`
- Use copy from `docs/fb-ads-final-copy.md` → Variant 2
- CTA button: **Learn More**
- Image: Use a nighttime/after-hours service scene

### Ad 3: Hiring Headache Relief
- Ad name: `Ad 3 – Hiring Relief`
- Use copy from `docs/fb-ads-final-copy.md` → Variant 3
- CTA button: **Get Offer**
- Image: Use a busy office/receptionist desk scene

---

## STEP 4: Lead Form Setup (same form for all 3 ads)

1. Click **Create Form**
2. Form name: `The Call Taker — Free Pilot Signup`
3. Form type: **More Volume** (instant form)
4. **Intro section:**
   - Headline: "Your Calls, Answered 24/7"
   - Description: "Get a smart receptionist for your business — free for 14 days. No credit card needed."
5. **Questions — add these fields:**
   - Full Name (prefilled from Facebook)
   - Mobile Number (prefilled)
   - Business Name (short answer)
   - City/State (short answer)
   - "What's your biggest phone issue?" (multiple choice):
     - Missing calls after hours
     - Can't afford a full-time receptionist
     - Calls go to voicemail too often
     - Want to capture more leads from calls
     - Other
6. **Privacy policy:** Link to `https://thecalltaker.com/privacy`
7. **Thank you screen:**
   - Headline: "Jessica will text you in 30 seconds"
   - Description: "Our team is setting up your free pilot right now. You'll get a text at the number you provided."
   - CTA button: **Book Your Demo**
   - Link: `https://thecalltaker.com/book`
8. Click **Publish Form**

---

## STEP 5: Pre-Publish Checks

Before clicking Publish on the campaign:

- [ ] Go to **Events Manager** → verify Meta Pixel is firing on thecalltaker.com
- [ ] Submit a test lead through Facebook's **Lead Ads Testing Tool**
- [ ] Check GHL → new contact appeared with `fb-lead` tag
- [ ] Verify Wallace got SMS notification for test lead
- [ ] Review ALL ad copy — make sure NONE of these words appear:
  - "AI" (use "smart receptionist" or "virtual receptionist")
  - "guaranteed" (remove entirely)
  - "never miss" (use "catch more calls")
  - Specific income claims like "$10K/month" (use "thousands")
- [ ] All images/videos uploaded and not rejected
- [ ] Set campaign schedule: **Start 9AM ET tomorrow**
- [ ] Click **Publish**

---

## STEP 6: Post-Launch (First 2 Hours After 9AM)

1. **Events Manager:** Watch for Lead events firing (each form submit = 1 Lead event)
2. **GHL:** Check Contacts for new entries with `fb-lead` tag
3. **SMS:** Verify auto-SMS fires within 60 seconds of each lead
4. **ntfy:** Check `tct-urgent` for Wallace alert on each new lead
5. **If no leads after 1 hour:** Check ad delivery status — may be in "Learning" phase (normal)
6. **If leads come in but no SMS:** Check `ops/fb-lead-ads-engine.py status`

---

## Quick Reference

| Item | Value |
|------|-------|
| Campaign name | Call Taker – Lead Ads – US Small Business |
| Budget | $50/day CBO |
| Audience | US, 25-65+, service business interests |
| Placements | FB Feed + IG Feed only |
| Pixel ID | 2129562004253413 (replace in Events Manager) |
| Lead form | More Volume, 5 fields |
| Thank you link | thecalltaker.com/book |
| Privacy link | thecalltaker.com/privacy |
| Start time | 9AM ET tomorrow |
