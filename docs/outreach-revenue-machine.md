# The Call Taker Outreach Revenue Machine

## Purpose

Build a CTOS-native outreach system that turns cold local service prospects into either self-educated buyers or hot inbound calls with Wallace. This is an implementation plan, not a sending engine.

The system must stay aligned with the current product truth: The Call Taker helps local service businesses recover missed-call revenue by capturing after-hours or missed-call opportunities, qualifying callers, preparing handoffs, and giving the business a reviewed setup path before live activation. Outreach must not claim live phone routing, provider activation, guaranteed booked jobs, automatic backend sync, or active SMS/email/call workflows unless those systems are configured and verified.

## Current Status

- Website homepage/demo/pricing release is live.
- `website/client/` is now a safe local-only setup preview.
- `website/onboarding/` no longer claims fake live activation.
- GHL/LeadConnector should be treated as deprecated legacy unless Wallace explicitly re-approves it.
- No outreach sending is enabled by this doc.
- No provider, CRM, SMS, email, call, webhook, payment, or deployment behavior is changed by this doc.

## Existing Repo Assets Audited

### Reuse

- `docs/call-setup-contract.md`: source of truth for local-only setup boundaries.
- `website/demo.html`: current demo path and safe preview concept.
- `website/client/`: deployed local setup preview and dashboard.
- `sales/secret-shopper-template.md`: useful raw process, but must be softened to avoid creepy framing and claims.
- `sales/objection-handling-playbook.md`: useful objections, but pricing/live/demo claims need safety review before reuse.
- `sales/cold-call-script.md`: useful call structure, but must remove live-routing claims and unverified proof.
- `outreach/cold-sequences-v2.md`: useful industry segmentation, but old copy claims live 24/7 answering and setup outcomes.
- `outreach/hot-lead-sequence-v1.md`: useful channel timing and variable map, but GHL-first, pricing-first, and live-demo claims are stale.
- `agents/agent-04-lead-intel/CLAUDE.md`: strong research template and scoring ideas.
- `agents/agent-08-demo-closer/CLAUDE.md`: useful call-flow and objection structure, but close language must reflect reviewed activation.
- `website/blog/*missed-call*`, `website/ai-receptionist-*`, and industry pages: useful SEO/proof education surfaces.

### Stale Or Risky

- GHL/LeadConnector as the default CRM and automation hub.
- Launchd/outbound scripts under `ops/`, `max/`, and `water-damage/` that imply blast sending, SMS sending, hot-lead follow-up, provider mutation, or stateful automation.
- Any state/log files in `max/` or `water-damage/` that contain historical outreach state.
- Old templates claiming "answer every call," "go live," "missing zero," "booked $X," "under 2 seconds," "free pilot," or specific pricing without current approval.
- `website/shared/proof-metrics.json` contains public proof-style metrics but needs substantiation review before outreach uses any number.

### Missing

- A CTOS-native prospect schema.
- A no-send command center.
- A clear lead scoring model tied to action categories.
- Safe outreach sequences that match the current product truth.
- A compliant secret-shopper SOP.
- A Wallace call sheet template.
- A proof governance process.
- Regression checks that prevent outreach docs from reintroducing fake-live claims.

## Revenue Machine Map

### 1. Prospect Sourcing

Target prospects are owner-operated local service businesses where a missed call is urgent, expensive, or emotionally charged.

Primary industries:

| Rank | Industry | Why It Fits | Main Pain | First Angle | Recommended First Channel |
| --- | --- | --- | --- | --- | --- |
| 1 | HVAC | Seasonal spikes, emergency jobs, owner often in the field | Calls after hours or during jobs | "What happens when AC breaks after 6pm?" | Secret-shopper email or phone |
| 2 | Plumbing | Emergency demand, high intent, first answer often wins | Burst pipe or leak calls go unanswered | "After-hours emergency calls are high intent." | Phone plus email |
| 3 | Roofing | Storm spikes, high-ticket inspections, call floods | Storm leads decay fast | "Storm calls need fast capture and handoff." | Email plus phone |
| 4 | Water damage | Severe urgency, high-ticket jobs, immediate response expectations | Caller needs help now | "Flood calls cannot wait for voicemail." | Phone-first |
| 5 | Locksmith | Emergency nights/weekends, fast decision | Locked-out caller calls until someone answers | "Emergency lockouts are first-answer wins." | Phone/SMS only where compliant |
| 6 | Towing | Roadside urgency, caller shops by response speed | Stranded caller needs immediate intake | "First clear response earns the tow." | Phone |
| 7 | Electrical | Safety-sensitive emergencies and after-hours concerns | Panel/sparking issue needs triage | "Capture urgent electrical calls safely." | Email plus phone |
| 8 | Garage door | Security-sensitive urgent jobs, evening demand | Door stuck open at night | "Security issue calls need fast capture." | Email |
| 9 | Medical/surgical supply | Operational handoffs and qualified calls matter | Missed qualified calls and slow handoff | "Reviewed call handoffs reduce leakage." | Warm email/call |
| 10 | Dental/med spa/clinic | High lifetime value, front desk overload | New patient or consultation calls missed | "Front desk overflow and after-hours capture." | Email |

Geography strategy:

- Start with reachable service markets where Wallace can credibly follow up by phone.
- Prioritize cities with high home-service demand, visible Google Maps density, active ads, and emergency service language.
- Build market batches by industry and city, not random national lists.
- Use public sources only: business websites, Google Business Profiles, public review themes, social profiles, industry directories, and manual call-path checks where lawful and appropriate.

Qualification filters:

- Owner-operated or clear local decision maker.
- Visible service phone number.
- Emergency, after-hours, same-day, storm, dispatch, or urgent service language.
- Enough reviews or web presence to show inbound demand.
- Website/contact path has friction or no clear after-hours handling.
- The business appears active and service-area driven.

Bad-fit filters:

- National franchise where local owner cannot decide.
- Existing sophisticated call center or AI reception system with good reviews.
- No visible phone demand or low urgency category.
- Very new business with no reviews and no proof of demand.
- Businesses whose customers should not be secret-shopped due to sensitive context.
- Any prospect where outreach would require private data, scraping behind login, or terms-violating collection.

### 2. Pre-Outreach Intelligence

For each prospect, collect:

- Business name
- Owner/manager if publicly available
- Main phone number
- Website
- City/service area
- Industry and sub-specialty
- Hours and after-hours language
- Emergency service language
- Website contact friction: buried phone, forms only, slow booking path, unclear after-hours path
- Public review signals: communication, responsiveness, missed calls, slow callbacks
- Ad spend signals: sponsored listings, LSAs, active PPC landing pages, heavy SEO footprint
- Current answering clues: voicemail language, answering service, live receptionist, AI, unknown
- Secret-shopper result when appropriate: date/time window, result code, neutral notes
- Proof angle to use
- Best channel
- Compliance constraints

Do not collect private personal data beyond what is publicly and lawfully available for business outreach. Do not store unredacted call recordings without explicit lawful basis and approval.

### 3. Outreach Angles

Use angles that educate without pretending a prospect has already lost specific customers.

- Missed-call revenue recovery: "If high-intent calls hit voicemail, some of them will call the next company."
- After-hours lead capture: "Your best jobs may happen outside office hours."
- Secret-shopper call path: "We checked the public call path and saw the call route to voicemail/no answer at [time]."
- Competitor speed: "In urgent service categories, the business that responds clearly first often wins." Avoid naming competitors unless directly substantiated and fair.
- Emergency handling: "Urgent callers need fast intake and a clear next step."
- Handoff cleanup: "The goal is a clean lead summary for the operator, not blind automation."
- Proof-driven: "We use reviewed call handoffs and setup boundaries from prior client work." Do not use American Surgical numbers without approval/redaction.
- Gideon demo preview: "Want to hear what Gideon would say in a preview?" Do not imply their phone is live or routed.

### 4. Multi-Channel System

Cold email:

- Primary scalable channel.
- Must be short, personalized, problem-first, and honest.
- Include real sender identity and required unsubscribe/compliance path where applicable.
- CTA: "Want me to send the preview?" or "Want to hear what Gideon would say?"

Phone:

- Best for A leads and secret-shopper findings.
- Goal is discovery and Wallace call/demo, not pressure.
- Script should use safe wording: "your after-hours path may be leaking calls."

Voicemail:

- 20 seconds or less.
- Mention one observation and one easy next step.
- No urgency theater or fake scarcity.

SMS/DM:

- Use only where compliant, consented, relationship-based, or otherwise approved.
- Keep short and conversational.
- No automated SMS until compliance and provider plan are approved.

Website/demo retargeting path:

- Send to `https://thecalltaker.com/demo.html` for preview education.
- Send to `https://thecalltaker.com/client/` only when explaining local setup preview boundaries.
- Do not send users into provider-sensitive intake unless the path is approved for that campaign.

Wallace call:

- Use when lead score is A or the prospect replies with urgency.
- Wallace should receive a call sheet with pain, proof angle, exact outreach history, likely objection, and next-step recommendation.

### 5. Self-Close Path

The self-close path should educate and qualify before any provider activation.

1. Prospect receives problem-first outreach.
2. Prospect opens demo page or preview.
3. Prospect understands that the preview is not live routing.
4. Prospect completes safe setup review only if ready.
5. Payment/trial path uses the currently approved live website path.
6. Setup is saved/reviewed.
7. Operator verifies backend sync, provider routing, notifications, and activation before live calls are routed.

Self-close copy must say:

- "Setup details saved for review."
- "Backend sync and provider routing are not automatic."
- "Do not route live calls until activation is verified."

Self-close copy must not say:

- "You're live."
- "Your AI is answering calls now."
- "Calls are routed automatically."
- "Guaranteed booked jobs."

### 6. Wallace Call-Ready Path

Before the call, the prospect should understand:

- Missed calls can become lost revenue.
- The Call Taker captures and qualifies caller intent.
- Gideon/demo preview shows the experience but does not activate their phone line.
- Setup requires review before provider activation.
- Wallace is there to map their current call path and next safe step.

Wallace should ask:

- "What happens when someone calls after hours?"
- "Who answers when your team is on jobs?"
- "Do callers leave voicemails, or do they call the next business?"
- "What is one qualified call worth in your business?"
- "Do you want capture only, dispatch handoff, appointment request, or review-first intake?"
- "Who needs to approve call routing before anything goes live?"

Common objections:

- "We answer our own calls." Ask about nights, weekends, job-site overlap.
- "We have voicemail." Ask whether urgent callers wait.
- "AI makes mistakes." Explain reviewed setup, handoff boundaries, and human approval.
- "We have an answering service." Compare consistency, handoff quality, and cost only if substantiated.
- "Send info." Send demo preview and one-line recap, then schedule a specific follow-up.

Close next step:

- A lead: book Wallace review call or setup review.
- B lead: send preview and sequence.
- C lead: nurture with missed-call education.
- D lead: mark bad fit.

### 7. Proof Engine

Proof can be used only when it is substantiated, permissioned, and safe.

Allowed:

- Anonymized proof where client identity and numbers are approved.
- Process proof: "reviewed setup," "local-only setup contract," "handoff summary," "operator verification before activation."
- Public website proof that has been audited and approved.
- Qualitative client feedback if redacted and permissioned.

Needs approval before use:

- American Surgical details.
- Call logs.
- Revenue lift numbers.
- Claims about response time, calls answered, booked jobs, or ROI.
- Screenshots with client names, phone numbers, emails, or patient/customer details.

Never use:

- Fake proof.
- Unsourced benchmark stats.
- "100%" or "missing zero" claims.
- Protected health, customer, or caller details.
- Provider logs or unredacted notifications.

Proof should become:

- Outreach snippets: one safe line tied to the prospect pain.
- Website/trust assets: redacted case-study cards.
- Call scripts: discovery prompts, not brag claims.
- Internal call sheets: proof angle with evidence status.

### 8. CTOS-Native Command Center

The command center should be local-first and provider-neutral until sending is approved.

Track:

- Prospect identity and public source URLs
- Industry, geography, services, service area
- Call-path observations
- Outreach status
- Channel history
- Last touch
- Next action
- Lead score
- Proof angle
- Objections
- Demo status
- Wallace call status
- Payment/setup status
- Follow-up reminders
- Won/lost reason
- Compliance notes

Recommended status model:

- `researched`
- `qualified`
- `sequence-ready`
- `touched`
- `replied`
- `hot-call-needed`
- `demo-sent`
- `wallace-call-booked`
- `setup-review-started`
- `won`
- `lost`
- `nurture`
- `bad-fit`

GHL/LeadConnector should not be the system of record unless re-approved. If later integrated, CTOS should remain the canonical source and write to CRM through explicit reviewed adapters.

## Implementation Phases

### Phase 1: Manual Outreach Command Center

Likely files:

- `ops/outreach/README.md`
- `ops/outreach/schema.md`
- `ops/outreach/prospects.example.csv`
- `tools/outreach/validate-prospects.js`

Data model:

- Prospect record, channel touch record, score record, call sheet record.

Checks:

- No real private data in examples.
- No provider writes.
- Schema validates required fields.

Success criteria:

- Wallace can review A/B/C/D leads and next actions without opening GHL.

Do not automate:

- Sending.
- Scraping.
- CRM sync.
- SMS.

### Phase 2: Prospect Research/Import

Likely files:

- `tools/outreach/import-prospects.js`
- `tools/outreach/score-prospects.js`
- `data/prospects/.gitkeep`
- `data/prospects/README.md`

Data model:

- CSV or JSONL with public business fields only.

Checks:

- Required source URL for every record.
- No personal/private sensitive data fields.
- No credentials.

Success criteria:

- A researcher can import safe public prospects and produce a scored queue.

Do not automate:

- Terms-violating scraping.
- Login-required collection.
- Calling.

### Phase 3: Sequences and Templates

Likely files:

- `docs/outreach-sequences.md`
- `tools/outreach/render-template.js`

Data model:

- Template ID, channel, industry, angle, required variables, compliance flags.

Checks:

- Forbidden claim scan.
- Unsubscribe/compliance placeholder for email.
- SMS marked consent/compliance required.

Success criteria:

- Wallace can generate safe drafts but nothing sends.

Do not automate:

- Bulk sends.
- Auto-DMs.
- Auto-SMS.

### Phase 4: Proof-Driven Personalization

Likely files:

- `docs/proof-governance.md`
- `data/proof/proof-registry.example.json`

Data model:

- Proof item, source, approved language, substantiation status, redaction status.

Checks:

- No client identifiers unless explicitly approved.
- No unsubstantiated metrics.

Success criteria:

- Templates can include only approved proof snippets.

Do not automate:

- Pulling provider logs.
- Publishing proof to website.

### Phase 5: Self-Close Flow

Likely files:

- Later website copy QA docs only.
- No website change in this lane.

Data model:

- Funnel stage events and setup review status.

Checks:

- No fake live activation copy.
- Demo page and client preview stay local-only where applicable.

Success criteria:

- Prospect can understand next step without Wallace, but activation remains reviewed.

Do not automate:

- Provider activation.
- Payment/pricing changes.

### Phase 6: CTOS Automation

Likely files:

- `ops/outreach/queue.md`
- `tools/outreach/next-action.js`
- `tools/outreach/export-drafts.js`

Data model:

- Next-action queue, owner, due date, channel, manual approval required.

Checks:

- Dry-run only by default.
- Preview output before any provider write.

Success criteria:

- CTOS can prepare Wallace's daily call list and draft messages.

Do not automate:

- Live sending.
- Provider writes.
- Launchd schedules.

### Phase 7: Reporting Dashboard

Likely files:

- `ops/outreach/report-schema.md`
- `tools/outreach/report.js`
- Future local HTML dashboard.

Data model:

- Prospects by status, touches by channel, reply rate, demo status, win/loss reason.

Checks:

- No PII leaks in committed examples.
- Reports can run on sanitized data.

Success criteria:

- Wallace knows daily: who to call, who to follow up, what angle to use, and what changed.

Do not automate:

- Publishing reports publicly.
- Provider dashboards.

## Safety And Compliance Boundaries

- No spam engine.
- No illegal scraping.
- No deceptive impersonation.
- No fake proof.
- No guaranteed outcomes.
- No claim that phone routing, backend sync, SMS/email, or live activation exists unless verified.
- SMS only where compliant, consented, relationship-based, or explicitly approved.
- Email must use honest sender identity and include unsubscribe/compliance path when required.
- No provider or CRM writes without approval.
- No live sending without Wallace approval.
- No payment/Square changes in outreach lanes.
- No private prospect data committed to the repo.

## Next Safe Action

Build Phase 1 as a no-send command center:

1. Define prospect schema.
2. Add safe example prospect data only.
3. Add forbidden-claim checks for outreach docs.
4. Add manual daily queue generation.
5. Keep all provider adapters as dry-run stubs until Wallace approves sending.
