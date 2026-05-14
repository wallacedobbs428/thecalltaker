# SMS Approval Packet Render

Status: Not approved for live SMS
Last reviewed: 2026-05-14
Owner: Wallace
No-send mode: true

## Business Use Case

The Call Taker helps local service businesses recover missed-call revenue by capturing missed or after-hours callers, qualifying what the caller needs, and preparing a reviewed handoff for the business owner or team.

SMS is intended for reviewed outreach and follow-up only. Cold SMS, bulk SMS, and automated sequences stay blocked until provider approval is verified.

## Provider Submission State

- A2P/10DLC: not_submitted
- Provider approval verified: false
- Campaign use case ready: true
- Sample messages ready: true
- Opt-out language ready: true
- Help language ready: true

## Allowed Sources After Approval

- inbound_demo_request
- inbound_call_or_text
- explicit_written_permission
- existing_customer_relationship
- manual_wallace_review

## Blocked Until Approved

- cold_sms
- bulk_sms
- automated_sms_sequences
- crm_provider_writes
- uploaded_scraped_phone_lists

## Required Boundaries

- Identify Wallace or The Call Taker in the first message.
- Honor STOP, unsubscribe, remove me, and equivalent opt-outs immediately.
- Pause on any human reply until Wallace reviews it.
- Do not claim live routing, call forwarding, backend sync, or guaranteed jobs.
- Use human text style, not polished email grammar.

## Sample Messages

### permission_preview

Gate: review-only warm lead
Source: inbound_demo_request

  - hey {first_name}, Wallace with The Call Taker. saw your demo request - want me to send the preview for {company}?
  - yep i can send it. just to be clear, its a preview - not live call routing yet
  - want the short version or should i call and walk you through it?

### after_demo

Gate: review-only warm lead
Source: inbound_demo_request

  - hey {first_name}, Wallace here. looks like you checked out The Call Taker demo. want me to show what Gideon would say for {company}?
  - quick note - nothing goes live from the demo. its just the caller experience preview
  - if missed calls arent an issue, all good. if they are, i can send the preview

### after_call

Gate: review-only warm lead
Source: manual_wallace_review

  - good talking earlier. i wrote down the main issue as: {call_path_note}. that right?
  - next step would be a reviewed setup preview. no routing gets turned on from this
  - i can send the preview here if thats easiest

### cold_candidate

Gate: provider approval required
Source: cold_sms_provider_approval

  - hey {first_name}, Wallace with The Call Taker. quick question - what happens when calls hit after hours at {company}? reply stop and i wont text again
  - not trying to spam you. i help businesses catch missed calls and prep cleaner handoffs. worth sending the preview?
  - last text from me - if missed calls arent a problem, no worries. if they are, i can show the preview

### hvac_variant

Gate: provider approval required
Source: cold_sms_provider_approval

  - hey {first_name}, quick question - when someone calls about AC after hours, does it hit a person or voicemail?
  - Wallace with The Call Taker btw. i help HVAC shops catch missed calls and prep cleaner handoffs. want the preview?
  - last one from me. if after-hours calls are handled, all good. if not, i can show what the preview sounds like
