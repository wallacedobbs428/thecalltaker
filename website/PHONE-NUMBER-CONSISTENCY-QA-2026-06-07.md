# Phone Number Consistency QA - 2026-06-07

## Known Numbers

- Gideon/demo call number: `(629) 269-9697` / `tel:+16292699697`
- Text Us SMS number: `+1 707 320 8712` / `sms:+17073208712`

## Result

PASS_WITH_NOTES

## Buyer-Path Findings

| Page | Gideon demo number | Text Us SMS number | Result |
| --- | --- | --- | --- |
| `index.html` | Present and labeled Call Gideon | Present as SMS-only Text Us | Pass |
| `pricing.html` | Present and labeled Call Gideon/Talk Through Setup | Present as SMS-only Text Us | Pass |
| `faq.html` | Present and labeled Call Gideon | Present as SMS-only Text Us | Pass |
| `setup.html` | Not used as primary setup CTA | Present as SMS-only support | Pass |
| `setup-confirmation.html` | Not used as primary CTA | Present as SMS-only support | Pass |

## Safety Checks

- Text Us number is not used as a `tel:` CTA.
- Gideon demo number is not used as an `sms:` CTA.
- No old 615 public phone number found in the primary buyer-path pages.
- Wallace personal phone number was not introduced.

## Notes

Some footer email/contact language still references Wallace email on pricing. That is not a phone-number mismatch, but a future public-contact policy can decide whether to keep or replace it.
