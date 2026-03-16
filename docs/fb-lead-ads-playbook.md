# Facebook Lead Ads — Day 1-7 Daily Check Playbook

> Campaign: Call Taker – Lead Ads – US Home Services
> Budget: $30/day CBO | 3 ad sets | 3 variants each = 9 ads total
> Started: __________ (fill in launch date)

---

## Key Metrics to Track

| Metric | Where to Find It | Good | Warning | Kill |
|--------|-------------------|------|---------|------|
| CPL (Cost Per Lead) | Ads Manager → Results column | < $10 | $10-20 | > $25 |
| CTR (Click-Through Rate) | Ads Manager → CTR column | > 2% | 1-2% | < 1% |
| Form Completion Rate | Ads Manager → Results / Clicks | > 30% | 15-30% | < 15% |
| Reply Rate (YES) | `fb-lead-ads-engine.py status` | > 20% | 10-20% | < 5% |
| Cost Per Reply | Manual: Spend / Replies | < $30 | $30-50 | > $50 |
| Demo Booked Rate | Manual: Demos / Leads | > 10% | 5-10% | < 5% |

---

## DAY 1 — Launch Day

### Morning (after ads approved)
- [ ] Verify all 9 ads are **Active** in Ads Manager (not in review, not rejected)
- [ ] If any ad rejected: read rejection reason, edit copy, resubmit
- [ ] Confirm `fb-lead-ads-engine.py` is running: `python3 ops/fb-lead-ads-engine.py status`
- [ ] Submit a test lead through each of the 3 forms
- [ ] Verify test leads appear in GHL with correct tags:
  - `facebook-lead`
  - `fb-lead-enrolled`
  - Variant tag (e.g., `fb-missed-revenue`)
  - Vertical tag (e.g., `hvac`)
- [ ] Verify you received the initial SMS on your test phone
- [ ] Delete test leads from GHL after verification

### Evening
- [ ] Check Ads Manager: How much spent? Any leads?
- [ ] Check GHL: Any new contacts with `facebook-lead` tag?
- [ ] If 0 leads and $10+ spent: check audiences aren't too narrow (aim 50K-500K)
- [ ] Note: Day 1 data is meaningless for optimization — DO NOT change anything

### Day 1 Numbers
```
Spend: $____
Impressions: ____
Clicks: ____
Leads: ____
CPL: $____
Replies: ____
```

---

## DAY 2 — First Data Check

### Check (evening)
- [ ] Open Ads Manager → Breakdown → By Ad
- [ ] Record CPL for each of the 9 ads
- [ ] Check which ad set (vertical) is getting the most spend from CBO
- [ ] Check GHL for replies: any `fb-lead-replied` or `fb-lead-interested` contacts?
- [ ] Run `python3 ops/fb-lead-ads-engine.py status` for automated stats
- [ ] If a lead replied YES: did Wallace follow up? Check tasks in GHL

### Day 2 Numbers
```
Spend: $____  (cumulative: $____)
Leads: ____   (cumulative: ____)
CPL: $____
Best ad: ____________________
Worst ad: ____________________
Replies: ____
```

### DO NOT
- Do not pause any ads yet (not enough data)
- Do not increase budget
- Do not change targeting

---

## DAY 3 — Trend Spotting

### Check
- [ ] Ads Manager → last 3 days → sort by CPL
- [ ] Identify: Which vertical is cheapest? (HVAC vs Plumbing vs Dental)
- [ ] Identify: Which variant is cheapest? (Missed Revenue vs After-Hours vs Hiring)
- [ ] Check form completion rates: Ads Manager → customize columns → add "Form Completion Rate"
- [ ] If any ad has 0 leads after $15+ spend → **flag it** (potential kill on Day 5)
- [ ] Check 24hr escalations: `python3 ops/fb-lead-ads-engine.py status` → "No Response" count
- [ ] If high no-response rate (>80%): review SMS copy, check phone numbers are real

### Day 3 Numbers
```
Spend: $____  (cumulative: $____)
Leads: ____   (cumulative: ____)
Avg CPL: $____
Best vertical CPL: ____ at $____
Worst vertical CPL: ____ at $____
Best variant CPL: ____ at $____
YES replies: ____
Demos booked: ____
```

---

## DAY 4 — Quality Check

### Check
- [ ] Review ALL leads in GHL → are they real businesses?
- [ ] Check phone numbers: are they real mobile numbers? (fake = bad targeting)
- [ ] Check business names: real companies or spam?
- [ ] If >30% fake/junk leads: tighten targeting (add more "narrow further" criteria)
- [ ] Check reply quality: are replies from decision-makers or random people?
- [ ] Call or text any leads that replied but didn't book a demo

### Lead Quality Score
```
Total leads so far: ____
Real businesses: ____
Fake/junk: ____
Quality rate: ____%
Replied: ____
Demos booked: ____
```

### If Quality is Bad (>30% junk)
1. Add more "Narrow Further" interests: `Business administration`, `Small and medium-sized enterprises`
2. Switch form type from "More Volume" to "Higher Intent" (adds a review step)
3. Add a qualifying question: "Do you own or manage a [HVAC/plumbing/dental] business? Yes / No"

---

## DAY 5 — First Optimization

### KILL DECISION: Pause any ad that meets ALL of these:
- Spent >$20
- CPL >$25
- 0 replies from its leads

### KEEP any ad that:
- CPL <$15
- At least 1 reply

### Actions
- [ ] Pause underperforming ads (mark which ones below)
- [ ] If an entire ad set (vertical) is bad: pause the ad set, don't just pause one ad
- [ ] DO NOT reallocate budget — CBO will auto-shift to winners

### Day 5 Report Card

| Ad | Vertical | Variant | Spend | Leads | CPL | Replies | Status |
|----|----------|---------|-------|-------|-----|---------|--------|
| 1 | HVAC | Missed Revenue | $__ | __ | $__ | __ | KEEP / PAUSE |
| 2 | HVAC | After-Hours | $__ | __ | $__ | __ | KEEP / PAUSE |
| 3 | HVAC | Hiring Headache | $__ | __ | $__ | __ | KEEP / PAUSE |
| 4 | Plumbing | Missed Revenue | $__ | __ | $__ | __ | KEEP / PAUSE |
| 5 | Plumbing | After-Hours | $__ | __ | $__ | __ | KEEP / PAUSE |
| 6 | Plumbing | Hiring Headache | $__ | __ | $__ | __ | KEEP / PAUSE |
| 7 | Dental | Missed Revenue | $__ | __ | $__ | __ | KEEP / PAUSE |
| 8 | Dental | After-Hours | $__ | __ | $__ | __ | KEEP / PAUSE |
| 9 | Dental | Hiring Headache | $__ | __ | $__ | __ | KEEP / PAUSE |

---

## DAY 6 — Double Down or Cut

### Check
- [ ] Did pausing bad ads improve CPL for remaining ads? (CBO should shift budget)
- [ ] Are the remaining ads getting cheaper or more expensive?
- [ ] How many total demos booked from Facebook leads?
- [ ] Cost per demo booked: Total spend / Demos booked

### If Things Are Working (CPL <$15, demos booked)
- [ ] Consider increasing budget from $30 → $50/day
- [ ] Only increase if you can handle the lead volume (Wallace has bandwidth to call)

### If Things Are NOT Working (CPL >$20, 0 demos)
- [ ] Don't increase budget
- [ ] Consider: Is the follow-up sequence working? Are leads getting SMS?
- [ ] Review `fb-lead-ads-engine.py status` — are SMS being sent? Are emails going out?
- [ ] Common fix: Change form type to "Higher Intent" (fewer but better leads)

---

## DAY 7 — DECLARE WINNERS

### Final Analysis
- [ ] Export all lead data to tracking CSV
- [ ] Calculate final metrics:

```
CAMPAIGN TOTALS (7 days):
  Total spend: $____
  Total leads: ____
  Avg CPL: $____
  Total replies: ____
  YES replies: ____
  Demos booked: ____
  Cost per demo: $____
  Conversion rate (lead → demo): ____%

WINNER — Best Vertical: _____________ (CPL: $____)
WINNER — Best Variant:  _____________ (CPL: $____)
LOSER — Worst Vertical: _____________ (CPL: $____)
LOSER — Worst Variant:  _____________ (CPL: $____)
```

### Day 7 Decision Tree

**IF cost per demo < $50 AND at least 2 demos booked:**
→ SCALE: Increase budget to $50-100/day on winning combinations only
→ Pause all losing ad sets
→ Create lookalike audience from leads who replied YES

**IF cost per demo $50-100 AND at least 1 demo booked:**
→ OPTIMIZE: Keep budget at $30, pause losers, test new copy on winners
→ Try "Higher Intent" form type
→ Add a follow-up call from Wallace within 5 minutes of lead (speed-to-lead)

**IF cost per demo > $100 OR 0 demos booked:**
→ PAUSE: Stop the campaign
→ Diagnose: Is the problem CPL (ads) or conversion (follow-up)?
  - High CPL (>$25) = targeting or copy problem → test different audiences
  - Low CPL (<$15) but 0 demos = follow-up problem → fix SMS/email/call sequence
→ Relaunch with fixes in 3-5 days

**IF 0 leads after 7 days ($210 spent):**
→ KILL: Campaign structure is broken
→ Check: Were ads approved? Were audiences >10K? Did forms work?
→ Rebuild from scratch with different approach

---

## Ongoing (After Day 7)

### Weekly Checks
- [ ] Monday: Review last week's CPL, reply rate, demo rate
- [ ] Wednesday: Check for ad fatigue (CPL rising 20%+ week over week)
- [ ] Friday: Review lead quality, clean up junk contacts in GHL

### Monthly
- [ ] Refresh ad creative (new primary text, keep what works)
- [ ] Test 1 new vertical (e.g., add Roofing or Legal ad set)
- [ ] Review total ROI: (Revenue from FB leads) - (Total ad spend) = Profit

### Ad Fatigue Signs
- CPL increases 20%+ over 2 weeks
- CTR drops below 1%
- Frequency >3 (same people seeing your ad 3+ times)
- Fix: New creative, new primary text, or expand audience
