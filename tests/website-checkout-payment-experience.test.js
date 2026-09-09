"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const checkout = fs.readFileSync(path.join(root, "website/card-checkout.html"), "utf8");

assert.match(checkout, /Start my 14-day free trial/, "primary action states the offer, not a vague submit action");
assert.match(checkout, /Nothing is charged today/, "checkout discloses the immediate amount beside the form");
assert.match(checkout, /Cancel before renewal/, "checkout surfaces the cancellation boundary before submission");
assert.match(checkout, /Credit or debit card/, "eligible recurring payment method is named clearly");
assert.match(checkout, /not for this recurring subscription trial/, "wallet limitation is explained in buyer language");
assert.match(checkout, /We do not show payment buttons that cannot complete this plan/, "page cannot fake an incompatible wallet path");
assert.match(checkout, /Secured by Square/, "payment processor trust is visible at the decision point");
assert.match(checkout, /1 · Checkout[\s\S]*2 · Setup[\s\S]*3 · Go live/, "post-checkout path is visible before payment details");
assert.match(checkout, /id="business"[^>]*autocomplete="organization"/, "business identity keeps autofill support");
assert.match(checkout, /id="email"[^>]*inputmode="email"[^>]*autocomplete="email"/, "email field uses mobile keyboard and autofill hints");
assert.match(checkout, /id="phone"[^>]*inputmode="tel"[^>]*autocomplete="tel"/, "phone field uses mobile keyboard and autofill hints");
assert.match(checkout, /id="card"[^>]*hidden/, "Square field stays hidden until it is ready");
assert.match(checkout, /document\.getElementById\('cardLoading'\)\.hidden = true/, "secure-field loading state resolves after attach");
assert.doesNotMatch(checkout, /applePay\(|googlePay\(|cashAppPay\(|afterpayClearpay\(/, "incompatible payment methods are not simulated");

for (const amount of ["97", "497", "997"]) {
  const request = JSON.parse(fs.readFileSync(path.join(root, `ctos/integrations/square-${amount}-create-payment-link-request.json`), "utf8"));
  assert.equal(typeof request.checkout_options.subscription_plan_id, "string", `${amount} request binds the variation in checkout_options`);
  assert.equal("subscription_plan_id" in request.quick_pay, false, `${amount} request cannot silently degrade into a one-time quick pay order`);
  assert.equal(request.quick_pay.price_money.amount, request._ctos_metadata.expected_monthly_amount_cents, `${amount} request cannot override the paid phase to zero`);
  assert.equal(request._ctos_metadata.initial_trial_amount_cents, 0, `${amount} variation still owns the free trial phase`);
}

console.log("website checkout payment experience tests passed");
