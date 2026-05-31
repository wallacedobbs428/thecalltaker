# First Ad Inbound Capture Loop

Date: Sunday 2026-05-31
Owner: Middle Revenue Execution Agent
Right lane partner: Right Video/Content Agent

## Purpose

Make sure Right lane's first ad and Instagram post create revenue movement instead of loose attention.

## If Someone Comments

- Inbound Agent classifies the comment.
- If it is advice, AI thanks them, summarizes the advice, asks one useful follow-up, and logs the advice.
- If it asks what The Call Taker does, AI drafts or sends the approved short explanation.
- If it asks whether it works for a vertical, AI answers with category-specific use case and asks what call type they miss most.
- If it asks pricing, AI uses standard public pricing facts only and escalates custom pricing or payment terms.
- If it is spam/irrelevant, AI archives or suppresses.
- If it is angry/sensitive, AI stops automation and escalates.

## If Someone DMs

- Create or update a lead record only from real source-backed DM data.
- Classify intent.
- Draft or send low-risk replies if provider runtime is connected.
- Move stage to replied, interested, demo_sent, meeting_suggested, follow_up_later, lost, or escalated.
- Queue follow-up when appropriate.

## If Someone Asks Pricing

- AI can answer standard pricing only: $97, $497, and $997+.
- AI does not offer discounts, custom terms, payment changes, or contracts.
- Custom pricing/payment/contract questions escalate.

## If Someone Asks Whether It Works For Roofers, Plumbers, Or Another Vertical

- AI explains the relevant missed-call or after-hours capture use case.
- AI does not guarantee revenue or emergency dispatch outcomes.
- AI asks which call scenario matters most.
- Regulated, medical, emergency, legal, or safety-sensitive claims escalate.

## If A Business Owner Gives Advice

- AI thanks them.
- AI summarizes the advice into CTOS as market language.
- AI asks one follow-up if useful.
- If fit signal appears, AI marks the lead warm and queues follow-up.

## If A Lead Wants A Demo

- AI sends demo context only if provider runtime is connected and no escalation trigger exists.
- AI asks which scenario to test.
- AI moves stage to demo_sent and schedules follow-up.
- Requests for a meeting with Wallace escalate.

## Data Created In CTOS

- lead_id
- source_post_or_ad_id
- platform
- business_name if source-backed
- contact_name if source-backed
- vertical/category
- source URL or permalink if available
- intent
- generated reply
- policy_check_result
- provider_status
- pipeline stage update
- next_follow_up_at
- escalation_required

## Escalation Rules

Escalate if:

- known personal or high-trust relationship
- asks for Wallace or a meeting
- custom pricing, contract, payment, legal, or financial terms
- asks for unverified proof, ROI, or case study
- angry/sensitive reply
- regulated/emergency/medical claims
- provider block or platform warning

## Current Blocker

Instagram inbound POST proof is not confirmed, so CTOS is ready to classify and draft locally, but autonomous replies remain provider-runtime gated.
