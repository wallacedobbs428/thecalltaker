"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const legacy = read("website/checkout.html");
const card = read("website/card-checkout.html");
assert.match(legacy, /utm_source/);
assert.match(legacy, /correlation_id/);
for (const key of ["tct_item_id","tct_asset_sha256","tct_publication_seed_sha256"]) {
  assert.match(legacy, new RegExp(key));
  assert.match(card, new RegExp(key));
}
assert.match(card, /API_ORIGIN = window\.location\.hostname === SANDBOX_CHECKOUT_HOST/);
assert.match(card, /call-taker-square-sandbox\.vercel\.app/);
assert.match(card, /call-taker-os\.vercel\.app/);
assert.match(card, /API_ORIGIN \+ '\/api\/public\/square-trial'/);
assert.match(card, /square-checkout-status/);
assert.match(card, /payment_pending/);
assert.match(card, /intent:'STORE'/);
assert.match(card, /token\.details\.billing\.postalCode/);
assert.match(card, /billingPostalCode:billingPostalCode/);
assert.match(card, /http-equiv="Content-Security-Policy"/);
assert.match(card, /pci-connect\.squareupsandbox\.com/);
assert.match(card, /requiresHumanReview|human will review onboarding|human-reviewed/);
assert.doesNotMatch(card, /setupToken|\/setup\.html|clientActive:\s*true/);
assert.match(card, /setupContinuation/);
assert.match(card, /sessionStorage\.setItem\(SETUP_CONTINUATION_KEY/);
assert.doesNotMatch(card, /[?&](?:continuationToken|setupToken)=/);

// A server may durably accept the POST and return 202 while the browser loses
// the response. The next submission must reuse the identity persisted before
// the request instead of manufacturing a second Square idempotency chain.
const identityBlock = card.match(/\/\/ BEGIN checkout request identity([\s\S]*?)\/\/ END checkout request identity/);
assert.ok(identityBlock, "checkout identity helper is present");
const storage = new Map();
const issued = [
  "10000000-1000-4000-8000-100000000001",
  "10000000-1000-4000-8000-100000000002",
  "10000000-1000-4000-8000-100000000003",
  "10000000-1000-4000-8000-100000000004",
];
let issuedCount = 0;
const context = vm.createContext({
  PENDING_CHECKOUT_KEY: "tct_pending_checkout_v1",
  key: "full247",
  sessionStorage: {
    getItem(name) { return storage.has(name) ? storage.get(name) : null; },
    setItem(name, value) { storage.set(name, String(value)); },
  },
  window: { crypto: { randomUUID() { return issued[issuedCount++]; } } },
});
vm.runInContext(identityBlock[1], context);
const firstAttempt = vm.runInContext("checkoutRequestIdentity()", context);
const persistedBeforeResponse = JSON.parse(storage.get("tct_pending_checkout_v1"));
assert.equal(persistedBeforeResponse.idempotencyKey, firstAttempt.idempotencyKey);
assert.equal(persistedBeforeResponse.state, "checkout_request_pending");

// Simulate a dropped 202 by never recording checkoutAttemptId, then retry.
const retryAfterDroppedResponse = vm.runInContext("checkoutRequestIdentity()", context);
assert.equal(retryAfterDroppedResponse.idempotencyKey, firstAttempt.idempotencyKey);
assert.equal(retryAfterDroppedResponse.correlationId, firstAttempt.correlationId);
assert.equal(retryAfterDroppedResponse.sessionId, firstAttempt.sessionId);
assert.equal(issuedCount, 3, "retry does not mint another checkout identity");
const persistenceIndex = card.indexOf("var requestIdentity = checkoutRequestIdentity();");
const postIndex = card.indexOf("var response = await fetch(API, { method:'POST'");
assert.ok(persistenceIndex >= 0 && postIndex > persistenceIndex, "pending identity is persisted before the checkout POST");
assert.match(card, /idempotencyKey:requestIdentity\.idempotencyKey/);
assert.doesNotMatch(card, /idempotencyKey:crypto\.randomUUID\(\)/);
console.log("website checkout continuity tests passed");
