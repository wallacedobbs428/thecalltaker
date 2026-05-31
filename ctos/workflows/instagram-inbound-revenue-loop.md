# Instagram Inbound Revenue Loop

Date: Sunday 2026-05-31
Owner: Middle Revenue Execution Agent
Status: ready locally; provider runtime gated

## Current Truth

- Netlify Instagram webhook GET works and returns test123.
- Instagram inbound POST proof is not confirmed.
- CTOS can classify and prepare responses locally.
- CTOS cannot assume autonomous reply sending until provider runtime proves inbound POST and reply/send access.

## Loop

1. Receive Instagram comment or DM event.
2. Record raw event metadata without secrets.
3. Match existing lead by platform handle or source URL.
4. If no match exists, create a source-backed lead record only when business/contact evidence exists.
5. Classify intent with ctos/inbound/inbound-classification-rules.json.
6. Draft response using ctos/inbound/autonomous-reply-policy.json.
7. Send autonomously only if category, provider, limits, source, and escalation gates pass.
8. Log inbound event and reply result.
9. Move lead stage.
10. Queue follow-up if appropriate.

## Categories

- asks_what_it_does
- asks_website
- asks_pricing
- sounds_interesting
- gives_advice
- referral_opportunity
- wants_demo
- wants_call
- asks_for_proof
- vertical_fit_question
- not_interested
- angry_sensitive
- spam_irrelevant

## Escalate

Escalate if the lead asks for Wallace, a meeting, custom pricing, legal/contract/payment terms, proof we cannot verify, investor discussion, emergency/medical claims, or if the relationship is known/sensitive.

## Outputs

- Updated lead record
- Inbound classification
- Draft or sent reply status
- Follow-up queue item
- Revenue scoreboard update
- Message history entry
