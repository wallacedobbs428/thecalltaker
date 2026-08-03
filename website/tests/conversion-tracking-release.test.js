"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const tracking = fs.readFileSync(path.resolve(__dirname, "..", "tct-tracking.js"), "utf8");

test("uses the production Meta Pixel and suppresses duplicate page initialization", () => {
  assert.doesNotMatch(tracking, /XXXXXXXXXX/);
  assert.match(tracking, /if \(typeof window\.fbq === 'function'\) return/);
  assert.match(tracking, /fbq\('init', '2129562004253413'\)/);
});

test("records a lead only after the CTOS response proves persistence", () => {
  const persistenceCheck = tracking.indexOf("body.ok !== true || !body.id");
  const googleLead = tracking.indexOf("gtag('event', 'lead_form_submit'");
  const metaLead = tracking.indexOf("fbq('track', 'Lead'");
  assert.ok(persistenceCheck >= 0, "persistence check is present");
  assert.ok(googleLead > persistenceCheck, "Google lead event follows persistence proof");
  assert.ok(metaLead > persistenceCheck, "Meta lead event follows persistence proof");
});

test("preserves attribution and recognizes demo plan checkout clicks", () => {
  assert.match(tracking, /a\[href\*="\/checkout"\]/);
  assert.match(tracking, /a\[href\*="card-checkout"\]/);
  assert.match(tracking, /a\[href\*="square\.link"\]/);
  assert.match(tracking, /\.post-demo-plan/);
  assert.match(tracking, /data-tct-event="pricing_plan_click"/);
  assert.match(tracking, /window\.fbq\('track', 'InitiateCheckout'\)/);
});
