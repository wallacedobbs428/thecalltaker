"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..", "..");
const entrypoint = fs.readFileSync(path.join(root, "website/tct-tracking.js"), "utf8");
const canonical = fs.readFileSync(path.join(root, "website/tct-funnel-events.js"), "utf8");
assert.match(entrypoint, /Canonical public attribution entrypoint/);
assert.match(entrypoint, /TCT_ATTRIBUTION_ENTRYPOINT_VERSION = "tct-tracking-entrypoint-v1"/);
assert.match(entrypoint, /tct-funnel-events\.js/);
assert.match(entrypoint, /__TCT_ATTRIBUTION_ENTRYPOINT_LOADED__/);
assert.match(canonical, /api\/public\/buyer-event/);
assert.match(canonical, /credentials:\s*"omit"/);
assert.match(canonical, /2129562004253413/);
assert.doesNotMatch(canonical, /XXXXXXXXXX/);
assert.match(canonical, /__TCT_FUNNEL_EVENTS_INITIALIZED__/);
assert.match(canonical, /tct_attribution_test/);
assert.match(canonical, /traffic_kind = "controlled_test"/);
for (const page of [
  "404.html", "after-hours-answering-service/index.html", "after-hours-call-checklist.html",
  "ai-receptionist/index.html", "card-checkout.html", "checkout.html", "demo.html",
  "demo/carolina-locksmith/index.html", "demos/houston-hvac.html", "faq.html", "index.html",
  "meet-gideon.html", "paid.html", "pay.html", "pricing.html", "privacy.html",
  "setup-confirmation.html", "setup.html", "terms.html",
]) {
  const html = fs.readFileSync(path.join(root, "website", page), "utf8");
  assert.match(html, /tct-tracking\.js/, `${page} uses the stable attribution entrypoint`);
  assert.doesNotMatch(html, /tct-funnel-events\.js/, `${page} does not bypass the stable entrypoint`);
}
console.log("privacy-safe conversion tracking release tests passed");
