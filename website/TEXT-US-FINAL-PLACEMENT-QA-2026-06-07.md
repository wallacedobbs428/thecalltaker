# Text Us Final Placement QA - 2026-06-07

## Rule

- Text Us = support CTA.
- Checkout/setup = primary CTA.
- Call Gideon Live = demo CTA.

## Result

PASS

## Findings

- Text Us uses `sms:+17073208712`.
- SMS body is URL encoded.
- No Sendblue API script added.
- No Sendblue provider endpoint added.
- Text Us does not appear inside the setup form body.
- Pricing Text Us appears after primary plan checkout CTAs.
- Confirmation Text Us appears as support after the main receipt CTAs.
- Call Gideon Live remains tied to `tel:+16292699697`.

## Notes

Homepage has Text Us in nav/hero/footer support positions. This is acceptable for support, but future ad landing pages should keep Text Us lower than the primary checkout/setup CTA.
