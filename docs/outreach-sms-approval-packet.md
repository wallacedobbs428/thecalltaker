# The Call Taker SMS Approval Packet

Status: approval prep only. No SMS sending is enabled by this document.

This is the working packet for SMS/A2P review. It is written so Wallace can copy the business-use-case language into the provider review process after the legal/provider details are confirmed.

## Business Use Case

The Call Taker helps local service businesses recover missed-call revenue by capturing missed or after-hours callers, qualifying what the caller needs, and preparing a reviewed handoff for the business owner or team.

SMS would be used only for reviewed outreach and follow-up, such as:

- replying to prospects who requested a preview
- following up after a prospect asked for information
- coordinating a Wallace call
- confirming a manual setup-review next step

Cold SMS remains blocked until compliance approval is confirmed.

## Sender Identity

Business name: The Call Taker

Representative: Wallace

Required first-message identity:

> hey [First Name], Wallace with The Call Taker here

Do not hide the sender. Do not impersonate a customer, competitor, vendor, Google, Meta, or any phone provider.

## Consent Position

Current status:

- No blanket cold-SMS approval exists.
- No live sending workflow is approved.
- No provider approval has been verified in this repo.
- SMS must remain manual-review-only until approval is confirmed.

Approved future SMS sources should be limited to:

- direct opt-in form submission
- inbound demo request
- inbound call/text from the prospect
- explicit written permission
- existing customer/service relationship where SMS is appropriate

Do not upload scraped phone lists for automated texting.

## Required Opt-Out Handling

Every outbound SMS sequence must honor these rules:

- `STOP`, `Stop`, `stop`, `unsubscribe`, `remove me`, or equivalent means stop all SMS.
- Opt-out must be honored immediately before any future touch.
- No argument after an opt-out.
- No re-adding the number without explicit new permission.
- Manual replies pause automation until Wallace reviews the conversation.

Short opt-out language for first message:

> reply stop and i wont text again

Formal opt-out language when needed:

> Reply STOP to opt out.

## Required Help Handling

If a contact replies `HELP`, respond only with support/identity information after approval:

> The Call Taker helps businesses review missed-call capture. Wallace: [approved business phone]. Reply STOP to opt out.

No provider or automation should send this until the SMS lane is approved.

## Claim Boundaries

Allowed:

- missed-call capture
- after-hours call capture
- preview
- reviewed setup
- handoff summary
- provider routing not active until reviewed

Not allowed:

- "we answer every call for you"
- "your AI is live"
- "calling you now"
- "call forwarding is active"
- "guaranteed booked jobs"
- "provider routing is already connected"
- "backend sync is automatic"
- fake proof or unsubstantiated revenue claims

## Human SMS Style

Wallace's SMS should not read like an email.

Use:

- short sentences
- normal lowercase where natural
- simple punctuation
- one idea per text
- direct wording

Avoid:

- perfect corporate grammar
- long paragraphs
- hype
- legal-heavy wording in every line
- fake urgency
- polished ad copy

Good tone:

> hey John, Wallace with The Call Taker. quick question - what happens when calls hit after hours at Smith Plumbing?

Too polished:

> Hello John, I hope this message finds you well. I am reaching out to discuss your after-hours call management strategy.

## Approval-Ready Sample Messages

These are samples for review, not sending instructions.

### Opt-In / Requested Preview

> hey [First Name], Wallace with The Call Taker. heres the preview you asked for: [preview link]. its not live routing, just the setup preview. reply stop and i wont text again

### After Demo Request

> hey [First Name], Wallace here. i saw you checked the demo - want me to send what Gideon would say for [Company]?

### Manual Follow-Up

> quick follow up - if missed calls arent a thing for [Company], no worries. if they are, i can send the preview

### Wallace Call Prep

> cool, i can walk you through it. nothing goes live from the preview. want me to call you today or tomorrow?

### Cold SMS Candidate, Blocked Until Approval

> hey [First Name], Wallace with The Call Taker. quick question - what happens when calls hit after hours at [Company]? reply stop and i wont text again

Use this only after cold-SMS compliance and provider approval are confirmed.

## Approval Status

Current practical status: not approved for live SMS.

The repo now has the language needed for a provider/compliance packet. The missing piece is external approval and a verified, reviewed sending workflow.
