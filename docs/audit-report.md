# THE CALL TAKER — Project Audit
**Date:** February 13, 2026
**GHL Location:** tQb9YmrGDrdVUJYPKrsY
**Business:** Demo HVAC Services, Brentwood, TN
**Account:** wallacemdobbs@icloud.com

---

## 1. CONNECTIONS

| Service | Status | Details |
|---------|--------|---------|
| GoHighLevel API | CONNECTED | Key: pit-771d...4b35, full read/write access |
| GHL Phone Number | ACTIVE | +16156539004 (SMS only, no voice AI) |
| GitHub Pages | CONNECTED | Website deployed at thecalltaker.com (wallacedobbs428/thecalltaker) |
| Custom Domain | CONNECTED | thecalltaker.com — via Wallace's GitHub repo |
| Stripe/Payments | NOT CONNECTED | No billing system |
| Instagram/Social | NOT CONNECTED | No social integrations found |

---

## 2. WHAT'S IN GOHIGHLEVEL

### Funnels/Websites: 2
**HVAC (website)** — 6 pages (Home, About Us, Services, Contact Us, Thank You, Link in Bio)
- NO custom domain connected
- Only accessible via GHL preview links
- GHL API is read-only for pages — cannot create/edit page content via API

**HVAC Offer (funnel)** — 3 pages (Offer, Consultation Appointment, Thank You)
- No domain connected

### Calendars: 5 (only 1 active)
| Calendar | Active |
|----------|--------|
| Schedule an Appointment | YES |
| Installation | NO |
| Repair | NO |
| Air Quality Solutions | NO |
| Maintenance | NO |

### Pipelines: 2
1. **Marketing Pipeline** — 11 stages (New Lead → Review Request)
2. **New Leads - HVAC** — 6 stages (New Lead → Lost)

### Workflows: 10
| Workflow | Status |
|----------|--------|
| 1. New Lead Nurture (Fast 5) - Claim Offer | DRAFT |
| 2. Appointment Confirmation + Reminders | PUBLISHED |
| 3. Appt No Show | PUBLISHED |
| 4. New Sale - Send Review Request | DRAFT |
| 5. Long-Term Nurture | PUBLISHED |
| 6. Stale Leads | PUBLISHED |
| AI Agent Trigger | PUBLISHED |
| New Workflow : 1767294037970 | PUBLISHED (unnamed) |
| New Workflow : 1767457230352 | DRAFT (unnamed) |
| New Workflow : 1770958676732 | PUBLISHED (unnamed) |

### Contacts: 7
- 1 active AI conversation (James, tagged ai-qualifying)
- 6 others (tests and follow-ups, mostly unnamed)

### Tags: 5
ai-disabled, ai-qualifying, follow-up, high priority, warm lead

### Custom Fields: 1
- Message (contact.message)

### Forms: 3
1. Contact Us
2. Newsletter Subscriptions
3. Marketing Form - Claim Offer

**Form submissions: 0**

---

## 3. AI VOICE AGENT: CONFIGURED AND LIVE
- Agent ID: 695947c64b9ed67d8f1077ad on +16157845747
- Full 7-step call flow (greeting → urgency → info collection → appointment → FAQs → guardrails → conclusion)
- Emergency triage: gas leak, CO alarm, no heat <40°, flooding, burning smell, elderly/infant/medical
- patienceLevel=medium, maxCallDuration=900 (15 min)
- 6 test agents should be deleted via GHL dashboard

---

## 4. LOCAL FILES (~/Desktop/wallace-hvac/)

See CLAUDE.md for current file structure. Website is a 2-page site (index.html + demo.html) deployed on GitHub Pages with dark green premium theme.

---

## 5. WHAT'S WORKING / BROKEN / MISSING

### WORKING
- GHL API connection (live, valid)
- SMS sending/receiving
- 4 published workflows (appointment reminders, no-show, long-term nurture, stale leads)
- 2 sales pipelines built
- 1 calendar active (Schedule an Appointment)
- Tag-based lead tracking

### BROKEN / INCOMPLETE
- 3 unnamed workflows (unknown purpose)
- 2 draft workflows never activated (Lead Nurture, Review Request)
- 4 inactive calendars
- GHL funnels have no domain — not publicly accessible
- Contact data is sparse (most contacts unnamed)

### MISSING (as of Feb 14, 2026)
- Custom domain DNS (CNAME configured, Wallace must point DNS)
- Payment collection (no Stripe, no invoicing)
- Email template content in GHL (shells exist, need copy pasted)
- Real testimonials (placeholder testimonials on site)

---

## 6. PRIORITY ORDER TO GET 10 PAYING CLIENTS

1. ✅ **Build and deploy the website** — DONE (2-page dark+green GitHub Pages site)
2. ✅ **Set up GHL automations** — DONE (tags, templates, workflows, pipelines)
3. ✅ **Create sales materials** — DONE (cold emails, cold call script, proposal, secret shopper, demo script)
4. ✅ **Create onboarding docs** — DONE (intake form, onboarding steps, welcome emails, client agreement)
5. ✅ **Configure AI voice agent** — DONE (live on +16157845747)
6. ☐ **Wallace: Connect custom domain** (manual — point DNS to GitHub Pages)
7. ☐ **Wallace: Set up Stripe** for billing (manual — skip until first client)
8. ☐ **Wallace: Start calling HVAC companies** with sales materials
