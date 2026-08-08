"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
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
assert.match(card, /call-taker-os\.vercel\.app\/api\/public\/square-trial/);
assert.match(card, /square-checkout-status/);
assert.match(card, /payment_pending/);
assert.match(card, /requiresHumanReview|human will review onboarding|human-reviewed/);
assert.doesNotMatch(card, /setupToken|\/setup\.html|clientActive:\s*true/);
console.log("website checkout continuity tests passed");
