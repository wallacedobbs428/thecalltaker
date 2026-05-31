# Sunday Revenue Execution Plan

Date: Sunday 2026-05-31
Owner: Middle Revenue Execution Agent
Mode: policy-based autonomy; Wallace handles exceptions only

## Purpose

Make CTOS operate The Call Taker's revenue system today by preparing real lead research, outbound queues, inbound capture, follow-up movement, and ad-response conversion without sending messages or inventing leads.

## What AI Agents Can Execute Today

- Middle Revenue Agent can run the Instagram lead research queue for roofing, plumbing, HVAC, electrical, landscaping, towing, locksmith, med spa, dentist, veterinary, and local business owner segments.
- Middle Revenue Agent can create source-backed lead records after real research and keep placeholders out of the lead pipeline.
- Middle Revenue Agent can generate founder/advice DMs from approved segment playbooks and policy-check them.
- Inbound Agent can classify first-ad comments and DMs into CTOS categories as soon as they exist.
- Follow-Up Agent can classify due follow-ups, draft next touches, and send future non-sensitive follow-ups only when provider/channel/context pass.
- Revenue Ops Agent can update the money scoreboard with real AI movement: researched, drafted, sent, replied, moved, escalated, or blocked.

## Outbound Campaigns That Can Run Today

- Instagram Local Founder campaign: research and message generation can run now; sending is gated by real source-backed leads and Instagram runtime proof.
- Warm Follow-Up campaign: policy logic is ready; current known warm leads do not auto-send because they are sensitive, relationship-driven, current-customer, or missing context.
- Facebook advice-post campaign: drafting and classification can run; posting waits for adapter/platform confirmation.
- Instantly email campaign: list/source/suppression prep can run; sending waits for provider setup.

## Inbound System That Needs To Be Proven

- Netlify Instagram webhook GET proof works and returns test123.
- Instagram inbound POST proof is still not confirmed.
- Autonomous replies are ready in CTOS but cannot be treated as connected until inbound POST plus reply/send runtime are proven.
- When proof arrives, inbound events should create or update lead records, classify intent, draft/send low-risk replies, and schedule follow-ups.

## Warm Leads Needing Movement

- Franklin medical meeting: AI prepares meeting context and safe questions; escalation required due healthcare-adjacent meeting sensitivity.
- Jay Grosman: AI prepares reminder packet only after exact last-touch date is sourced.
- Chuck McDowell: AI prepares scheduling nudge and call prep; high-trust relationship stays escalated.
- Orthodontist DM lead: AI holds draft until exact channel/provider and relationship context are clear.
- Ad-growth lead: AI prepares partner/referral framing; escalation required due strategic context uncertainty.
- Freedom Diagnostics: AI keeps implementation packet ready; no live setup or outbound until Sydney/Kris answers and authority exist.
- American Surgical: protected client context only; no Middle sales outreach or proof claim without client-ops authorization.

## Follow-Ups AI Can Send Autonomously Under Policy

Current known warm leads: none are autonomous-sendable today.

Future follow-ups can be sent autonomously when:

- the lead is source-backed
- last-touch date and spacing are known
- the lead is not personal, sensitive, current-customer, or strategic
- the message uses recorded context only
- provider/channel is connected
- no custom pricing, proof, legal, payment, or meeting-with-Wallace request appears

## Revenue Actions Connected To Right Lane's First Ad

- Middle provides comment and DM classification behind Right's ad.
- Middle creates lead records from real comments/DMs with source links and timestamps.
- Middle drafts or sends low-risk replies based on provider runtime status.
- Middle routes pricing, website, demo, vertical-fit, advice, and not-interested replies through CTOS rules.
- Middle escalates proof requests, custom pricing, angry/sensitive replies, known relationships, investor interest, and meeting requests.

## CTOS Data To Create From Ad Comments, Replies, And DMs

- lead_id
- source_post_or_ad_id
- platform
- comment_or_dm_permalink if available
- business_name if source-backed
- contact_name if source-backed
- category or vertical
- intent classification
- generated reply
- policy check result
- provider status
- next AI action
- escalation required true/false
- follow-up date if applicable

## Provider Blocks

- Instagram inbound POST proof not confirmed.
- Instagram outbound/reply runtime not proven in this run.
- Instantly provider setup not verified.
- Facebook group posting adapter/platform confirmation missing.
- Square/payment/checkout provider repair belongs to Left lane.

## Safe Operating Rule

Middle does not send DMs, emails, calls, public posts, provider writes, checkout edits, or deployments unless the provider adapter is actually connected, campaign policy allows it, and the action is inside approved limits.
