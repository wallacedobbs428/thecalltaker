# Square Handoff Test Plan - 2026-06-07

## Safety Boundary

This test plan does not require entering a payment card, charging a card, creating invoices, sending emails, sending SMS, triggering calls, or changing provider settings.

## Test 1 - $97 Pricing Button

1. Open `https://thecalltaker.com/pricing.html`.
2. Click the $97 After-Hours Capture `Start Free Trial` button.
3. Confirm the Square page opens.
4. Confirm no old AI-call-within-2-minutes copy is visible.
5. Confirm whether buyer-facing setup text is visible.
6. Confirm whether public/static proof shows `redirectUrl:null`.
7. Do not enter card information.

Expected current status: Square opens, old AI-call wording is not visible in static HTML, setup instruction is not visible in static Square HTML, and `redirectUrl:null` is present.

## Test 2 - $497 Pricing Button

1. Open `https://thecalltaker.com/pricing.html`.
2. Click the $497 24/7 Call Coverage `Start Free Trial` button.
3. Confirm the Square page opens.
4. Confirm no old AI-call-within-2-minutes copy is visible.
5. Confirm whether buyer-facing setup text is visible.
6. Confirm whether public/static proof shows `redirectUrl:null`.
7. Do not enter card information.

Expected current status: Square opens, old AI-call wording is not visible in static HTML, setup instruction is not visible in static Square HTML, and `redirectUrl:null` is present.

## Test 3 - $997+ Pricing Button

1. Open `https://thecalltaker.com/pricing.html`.
2. Click the $997+ Custom Call Coverage `Start Free Trial` button.
3. Confirm the Square page opens.
4. Confirm no old AI-call-within-2-minutes copy is visible.
5. Confirm whether buyer-facing setup text is visible.
6. Confirm whether public/static proof shows `redirectUrl:null`.
7. Do not enter card information.

Expected current status: Square opens, old AI-call wording is not visible in static HTML, setup instruction is not visible in static Square HTML, and `redirectUrl:null` is present.

## Test 4 - Website Fallback Route

1. Open `https://thecalltaker.com/checkout.html?plan=afterhours`.
2. Confirm it redirects toward the current $97 Square link.
3. If redirect is blocked or page text is visible, confirm it says: `After payment, return to the setup form so we can configure your AI receptionist.`
4. Click `I already checked out - start setup form`.
5. Confirm `/setup.html` loads.

## Test 5 - Direct Pay Fallback Route

1. Open `https://thecalltaker.com/pay.html`.
2. Confirm it redirects toward the current $97 Square link.
3. If redirect is blocked or page text is visible, confirm it says: `After payment, return to the setup form so we can configure your AI receptionist.`
4. Click `I already checked out - start setup form`.
5. Confirm `/setup.html?plan=afterhours` loads.

## Test 6 - Setup Form Staged Submit

1. Open `https://thecalltaker.com/setup.html?source=square-test&plan=full247`.
2. Confirm the top copy says: `Use this form after checkout so we can configure your AI receptionist`.
3. Fill staged/test business details only.
4. Submit the form.
5. Confirm `/setup-confirmation.html` loads.
6. Confirm the confirmation page says the setup form was received and does not claim live phone routing is active.

## Test 7 - No-Provider Safety

1. Confirm no card was entered.
2. Confirm no payment was made.
3. Confirm no invoice was created.
4. Confirm no email/SMS/call/provider webhook was triggered by RIGHT.
5. Confirm paid ads remain blocked until Square redirect or checkout copy is clean.
