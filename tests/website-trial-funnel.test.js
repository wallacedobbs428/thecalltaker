"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const pricing = read("website/pricing.html");
const checkout = read("website/card-checkout.html");
const demo = read("website/demo.html");

for (const [plan, label, amount] of [["afterhours","After-Hours Capture","$97"],["full247","Revenue Recovery System","$497"],["custom","Operational Infrastructure","$997"]]) {
  assert.ok(pricing.includes(`/card-checkout.html?plan=${plan}`), `${label} opens its exact checkout`);
  assert.ok(checkout.includes(`${plan}: { name:'${label}'`), `${label} is mapped in checkout`);
  assert.ok(pricing.includes(amount), `${label} discloses ${amount}`);
}

assert.ok(checkout.includes("SETUP_ELIGIBLE_STATES.indexOf(result.status) < 0"), "browser requires a setup-eligible backend receipt");
assert.ok(checkout.includes("result.checkoutAttemptId") && checkout.includes("result.correlationId"), "pending receipt is correlated");
assert.ok(checkout.includes("result.correlationId !== requestIdentity.correlationId"), "pending receipt must match the persisted submitted correlation");
assert.ok(checkout.includes("correlation_id="), "status read is scoped by correlation");
assert.ok(checkout.includes("tct_pending_checkout_v1"), "pending continuation survives refresh");
assert.ok(checkout.includes("sessionId:requestIdentity.sessionId"), "persisted anonymous session is propagated outside attribution");
assert.ok(checkout.includes("businessName:fields[0]") && checkout.includes("preferredContactMethod:fields[5]"), "checkout creates an actionable business contact receipt");
assert.ok(checkout.includes("consentToFollowUp:true"), "checkout requires explicit human-onboarding follow-up consent");
assert.ok(checkout.includes("subscription_scheduled_pending_human_review"), "signed scheduled-subscription evidence remains pending human review");
assert.ok(checkout.includes("intent:'STORE'") && checkout.includes("customerInitiated:true") && checkout.includes("sellerKeyedIn:false"), "Square tokenization explicitly requests card-on-file verification");
assert.ok(checkout.includes("token.details.billing.postalCode") && checkout.includes("billingPostalCode:billingPostalCode"), "the secure Square postal result reaches CreateCard without local persistence");
assert.ok(checkout.includes('http-equiv="Content-Security-Policy"') && checkout.includes("pci-connect.squareupsandbox.com") && checkout.includes("pci-connect.squareup.com"), "Square checkout has an explicit sandbox and production CSP");
assert.equal(/setupToken|tct_setup_binding|\/setup\.html/.test(checkout), false, "checkout cannot mint a legacy setup binding or paid browser result");
assert.ok(checkout.includes("result.setupContinuation") && checkout.includes("tct_setup_continuation_v1"), "checkout carries only the server-issued setup continuation into session storage");
assert.equal(/payment_confirmed|payment_succeeded/.test(checkout), false, "browser cannot emit or infer provider payment truth");

assert.ok(demo.includes('name="follow_up_consent"') && demo.includes("required"), "follow-up needs explicit consent");
assert.ok(demo.includes("body.request_id") && demo.includes("body.correlation_id !== correlationId"), "success requires the durable correlated server receipt");
assert.ok(demo.includes("session_id:sessionId"), "consented lead reuses the anonymous session correlation");
assert.equal(demo.includes('data-tct-event="lead_form_submitted"'), false, "form interaction cannot pretend submission");
assert.ok(demo.includes("<title>Build a Revenue Recovery Preview | The Call Taker</title>"), "demo title describes the available preview without advertising an unverified phone line");
assert.ok(demo.includes('<link rel="canonical" href="https://thecalltaker.com/demo.html">'), "demo canonical points to the deployed Pages route");
assert.equal(/Call \(\d{3}\) \d{3}-\d{4}/.test(demo), false, "demo cannot advertise an unverified public call number");

console.log("website trial funnel regression passed");
