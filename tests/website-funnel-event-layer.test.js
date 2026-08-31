"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const client = read("website/tct-funnel-events.js");
const checkout = read("website/card-checkout.html");
const demo = read("website/demo.html");
for (const page of ["index.html","pricing.html","demo.html","meet-gideon.html","paid.html","card-checkout.html","setup.html","setup-confirmation.html","faq.html"]) {
  const html = read(`website/${page}`);
  assert.ok(html.includes("tct-tracking.js"), `${page} loads the canonical attribution entrypoint`);
  assert.equal(html.includes("tct-funnel-events.js"), false, `${page} does not bypass the canonical entrypoint`);
}
for (const event of [
  "page_view", "cta_intent", "demo_preview_intent", "demo_preview_rendered_ui", "pricing_viewed",
  "checkout_intent_opened", "checkout_intent_submitted", "checkout_request_accepted_ui",
  "checkout_request_error_ui", "checkout_waiting_ui_shown", "lead_form_started",
  "follow_up_consent_selected_ui", "lead_request_submitted_ui", "lead_request_accepted_ui", "lead_request_error_ui",
]) {
  assert.ok(client.includes(`"${event}"`) || client.includes(`return "${event}"`) || client.includes(`${event}: true`), `client maps ${event}`);
}
for (const forbiddenBrowserTruth of [
  "cta_clicked", "demo_started", "demo_completed", "demo_call_tap", "demo_text_tap", "text_us_tap",
  "checkout_started", "checkout_pending", "checkout_failed", "checkout_confirmed",
  "payment_confirmed", "payment_succeeded", "client_record_created", "onboarding_task_created",
  "lead_form_submitted", "follow_up_consent_granted",
]) {
  assert.equal(client.includes(forbiddenBrowserTruth), false, `browser cannot emit ${forbiddenBrowserTruth}`);
}
for (const event of ["checkout_intent_submitted", "checkout_request_accepted_ui", "checkout_request_error_ui", "checkout_waiting_ui_shown"]) assert.ok(checkout.includes(`record('${event}'`), `checkout records ${event}`);
for (const forbiddenCall of ["checkout_started", "checkout_pending", "checkout_failed", "checkout_confirmed"]) assert.equal(checkout.includes(`record('${forbiddenCall}'`), false, `checkout does not record ${forbiddenCall}`);
for (const event of ["demo_preview_rendered_ui", "follow_up_consent_selected_ui", "lead_request_submitted_ui", "lead_request_accepted_ui", "lead_request_error_ui"]) assert.ok(demo.includes(`'${event}'`), `demo records ${event}`);
assert.equal(read("website/after-hours-call-checklist.html").includes("demo_call_tap"), false);
assert.equal(read("website/shared/tct-intent.js").includes("demo_completed"), false);
assert.equal(read("website/shared/tct-convert.js").includes("demo_completed"), false);
assert.equal(read("tests/fixtures/funnel-event-layer/simulation-events.json").includes("demo_call_tap"), false);
assert.equal(read("tests/fixtures/funnel-event-layer/simulation-events.csv").includes("text_us_tap"), false);
assert.match(client, /fetch\(endpoint/);
assert.match(client, /credentials:\s*"omit"/);
assert.match(client, /keepalive:\s*true/);
assert.match(client, /tct_buyer_session_v1/);
assert.match(client, /tct_correlation_id_v1/);
for (const key of ["tct_item_id", "tct_asset_sha256", "tct_publication_seed_sha256"]) assert.match(client, new RegExp(key));
for (const pii of ["business_name","owner_name","business_phone","owner_cell","summary_email","FormData","document.cookie","localStorage"]) assert.equal(client.includes(pii), false, `event client excludes ${pii}`);
console.log("website funnel event layer tests passed");
