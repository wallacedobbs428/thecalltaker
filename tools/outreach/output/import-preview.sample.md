# Outreach Import Preview

Status: dry run only. No email, SMS, calls, CRM writes, provider writes, scraping, or activation occurred.
Source: tools/outreach/example_import.json
Accepted: 3
Rejected: 1
Categories: A=1, B=0, C=1, D=1

## Scored Prospects

### Rapid Roof Example
- Score: 94 (A)
- Industry/category: roofing / emergency_service
- Recommended first touch: Wallace manual call with call sheet. Do not automate.
- Outreach angle: after-hours storm lead capture
- Review required: yes
- Next action: Review normalized intake, then choose manual no-send next action.

### City Dental Example
- Score: 49 (C)
- Industry/category: dental / appointment_service
- Recommended first touch: Nurture with education or re-research during a seasonal trigger.
- Outreach angle: missed appointment and callback cleanup
- Review required: yes
- Next action: Review normalized intake, then choose manual no-send next action.

### Neighborhood Books Example
- Score: 25 (D)
- Industry/category: business with phone line / business_with_phone_line
- Recommended first touch: Do not contact. Record bad-fit reason.
- Outreach angle: phone-line evaluation only
- Review required: yes
- Next action: Review normalized intake, then choose manual no-send next action.

## Rejected Records

### Broken Import Example
- Missing required field: phone

## Safety Boundary

- This importer is local-only and no-send.
- Manual compliance review is required before any outreach.
- Every business with a phone line may be evaluated, but only A/B/C/D scoring decides action priority.
- Generic phone-line businesses stay lower priority unless urgency, revenue risk, and answering-path weakness are proven.
