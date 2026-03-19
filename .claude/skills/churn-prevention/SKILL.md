---
name: churn-prevention
description: "Analyze and reduce SaaS customer churn. Use when discussing retention strategies, analyzing why customers cancel, building re-engagement campaigns, designing onboarding improvements, or creating loyalty/reward systems. Covers churn prediction, cohort analysis, win-back sequences, NPS-driven interventions, and pricing retention tactics."
category: marketing
---

# Churn Prevention — SaaS Retention Playbook

Reduce churn through data-driven retention strategies, proactive health monitoring, and automated intervention sequences.

---

## Framework: The 5 Churn Vectors

Every SaaS churn event traces to one of these root causes. Diagnose FIRST, then intervene.

### 1. Onboarding Failure (Days 1-14)
- **Signal:** No key action within 72 hours
- **Fix:** Reduce time-to-value. Guided setup, milestone emails, human check-in at Day 3
- **Metric:** Activation rate (% completing core action within 7 days)

### 2. Value Gap (Days 14-60)
- **Signal:** Login frequency drops, support tickets increase
- **Fix:** Usage-triggered education emails, feature discovery nudges, "Did you know?" campaigns
- **Metric:** Feature adoption breadth (% of key features used)

### 3. Support Failure
- **Signal:** Unresolved tickets, negative NPS, repeated same-issue tickets
- **Fix:** Priority queue for at-risk accounts, proactive outreach after bad experience, service recovery offers
- **Metric:** Time to resolution, CSAT per interaction

### 4. Price Sensitivity
- **Signal:** Downgrade requests, "too expensive" in cancellation surveys, competitor mentions
- **Fix:** ROI reports showing value delivered, usage-based pricing tiers, annual discount offers, pause option instead of cancel
- **Metric:** Revenue per user vs. perceived value

### 5. Natural Lifecycle
- **Signal:** Business closed, changed industries, outgrew product
- **Fix:** Graceful exit (referral program), alumni community, "come back" offers for seasonal businesses
- **Metric:** Reason codes in exit surveys

---

## Churn Prediction Model

### Health Score (0-100)
Calculate weekly for each customer:

```
Login frequency (last 14 days)     → 0-25 pts
Feature usage breadth               → 0-20 pts
Support ticket sentiment            → 0-15 pts
NPS/CSAT score                      → 0-15 pts
Payment history (failed charges)    → 0-10 pts
Engagement with emails/comms        → 0-10 pts
Contract remaining                  → 0-5 pts
```

### Risk Tiers
- **Green (70-100):** Healthy. Upsell/referral candidates
- **Yellow (40-69):** At risk. Trigger proactive check-in within 48 hours
- **Red (0-39):** Churn imminent. War room alert. Personal outreach from founder

---

## Intervention Sequences

### Red Alert Sequence (Health < 40)
1. **Immediate:** Personal email from founder acknowledging the issue
2. **Day 1:** Phone call or video message offering dedicated support
3. **Day 3:** Concrete fix/improvement based on their specific pain point
4. **Day 7:** Check-in + exclusive offer (free month, plan upgrade, custom feature)
5. **Day 14:** If no response, "We miss you" with easy reactivation path

### Yellow Alert Sequence (Health 40-69)
1. **Day 0:** Automated "How's it going?" email with usage insights
2. **Day 3:** Feature tip based on what they're NOT using
3. **Day 7:** Case study from similar business showing ROI
4. **Day 14:** Personal check-in from success team

### Win-Back Sequence (Already Churned)
1. **Day 1 post-churn:** "We're sorry to see you go" + feedback survey
2. **Day 14:** "Here's what we've improved since you left"
3. **Day 30:** Special comeback offer (50% off first month back)
4. **Day 60:** Final "Door is always open" with one-click reactivation
5. **Day 90:** Remove from active sequences, move to quarterly newsletter

---

## Cancellation Flow Best Practices

### Never Let Them Cancel in One Click
1. **Step 1:** "What's not working?" (multiple choice + free text)
2. **Step 2:** Offer targeted save based on reason:
   - "Too expensive" → Show ROI, offer discount or pause
   - "Not using it" → Offer setup help or training call
   - "Missing feature" → Show roadmap, offer workaround
   - "Switching to competitor" → Competitive comparison + match offer
3. **Step 3:** Offer pause (1-3 months) instead of cancel
4. **Step 4:** If they still cancel, make it easy (don't be hostile)

### Pause Feature
- 1-month or 3-month pause options
- Keeps data intact, reduces friction to reactivate
- Converts 15-30% of would-be cancellations to pauses
- 40-60% of paused accounts reactivate

---

## Metrics Dashboard

Track weekly:
- **Gross churn rate:** Customers lost / starting customers
- **Net churn rate:** (Lost - gained) / starting customers
- **Revenue churn:** MRR lost / starting MRR (weight by plan tier)
- **Churn by cohort:** Which signup month has highest churn?
- **Churn by plan:** Which tier churns most?
- **Churn by source:** Which acquisition channel has stickiest customers?
- **Save rate:** % of cancellation attempts saved by intervention
- **Reactivation rate:** % of churned customers who come back

---

## Retention Tactics Quick Reference

| Tactic | Impact | Effort | When to Use |
|--------|--------|--------|-------------|
| Onboarding email sequence | High | Low | Always |
| Monthly ROI report | High | Medium | After Day 30 |
| NPS survey + follow-up | High | Low | Day 30, then quarterly |
| Usage milestone celebrations | Medium | Low | Ongoing |
| Annual plan discount | High | Low | At renewal |
| Founder personal outreach | Very High | High | Red alerts only |
| Feature request follow-up | Medium | Low | When shipped |
| Customer advisory board | Medium | Medium | Top 10% customers |
| Referral program | Medium | Medium | Green health only |
| Pause instead of cancel | High | Medium | Cancellation flow |
