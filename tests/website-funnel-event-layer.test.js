const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

const launchPages = [
  "website/index.html",
  "website/pricing.html",
  "website/setup.html",
  "website/setup-confirmation.html",
  "website/demo.html",
  "website/paid.html",
  "website/faq.html"
];
const cardCheckoutPage = "website/card-checkout.html";
const eventInventoryPages = launchPages.concat(cardCheckoutPage);

const eventScript = read("website/tct-funnel-events.js");

assert.ok(
  read(".github/workflows/deploy.yml").includes("tct-funnel-events.js"),
  "future deploy allowlist should include the privacy-safe funnel script"
);

launchPages.forEach((page) => {
  assert.ok(
    read(page).includes("tct-funnel-events.js"),
    `${page} should include the deploy-gated funnel event script`
  );
});
[
  ["website/index.html", "homepage_view"],
  ["website/pricing.html", "pricing_view"],
  ["website/card-checkout.html", "card_checkout_view"],
  ["website/setup.html", "setup_view"],
  ["website/setup-confirmation.html", "setup_confirmation_view"],
  ["website/demo.html", "demo_view"],
  ["website/paid.html", "paid_view"]
].forEach(([page, eventName]) => {
  assert.ok(read(page).includes(`data-tct-view="${eventName}"`), `${page} should mark page view ${eventName}`);
});

function tags(html, pattern) {
  return (html.match(pattern) || []);
}

launchPages.forEach((page) => {
  const html = read(page);
  tags(html, /<a\b[^>]*class="[^"]*\btext-us-button\b[^"]*"[^>]*>/g).forEach((tag) => {
    assert.ok(tag.includes('data-tct-event="text_us_tap"'), `${page} Text Us button missing text_us_tap`);
    assert.ok(tag.includes('data-tct-destination="sms"'), `${page} Text Us button should use SMS destination`);
  });
  tags(html, /<a\b[^>]*href=["']tel:[^"']+["'][^>]*>/g).forEach((tag) => {
    assert.ok(
      tag.includes('data-tct-event="demo_call_tap"') || tag.includes('data-tct-event="paid_demo_click"'),
      `${page} tel link missing demo event`
    );
    assert.ok(tag.includes('data-tct-destination="tel"'), `${page} tel link should use tel destination`);
  });
  tags(html, /<a\b[^>]*href=["'][^"']*card-checkout\.html\?plan=[^"']*["'][^>]*>/g).forEach((tag) => {
    assert.ok(
      tag.includes('data-tct-event="homepage_cta_click"') ||
        tag.includes('data-tct-event="pricing_plan_click"') ||
        tag.includes('data-tct-event="paid_cta_click"'),
      `${page} card-checkout CTA should have funnel event`
    );
    assert.ok(tag.includes('data-tct-destination="card_checkout"'), `${page} card-checkout CTA should identify destination`);
  });
});

[
  'data-tct-event="homepage_cta_click"',
  'data-tct-event="pricing_plan_click"',
  'data-tct-event="card_checkout_start"',
  'data-tct-form="setup"',
  'data-tct-event-start="setup_form_started"',
  'data-tct-event-submit="setup_form_submitted"',
  'data-tct-view="setup_confirmation_view"',
  'data-tct-event="demo_call_tap"',
  'data-tct-event="text_us_tap"',
  'data-tct-event="paid_cta_click"',
  'data-tct-event="paid_demo_click"'
].forEach((marker) => {
    assert.ok(
    eventInventoryPages.some((page) => read(page).includes(marker)),
    `funnel package should include marker ${marker}`
  );
});

const squareLinksOutsideCardCheckout = launchPages
  .filter((page) => read(page).includes("checkout.square.site"));
assert.deepStrictEqual(squareLinksOutsideCardCheckout, [], "hosted Square links should not bypass the card checkout");

[
  /fetch\s*\(/,
  /XMLHttpRequest/,
  /sendBeacon/,
  /navigator\.sendBeacon/,
  /https?:\/\//,
  /localStorage/,
  /sessionStorage/,
  /document\.cookie/,
  /checkout\.square\.site/,
  /api[_-]?key/i,
  /secret/i,
  /token/i,
  /password/i
].forEach((blocked) => {
  assert.ok(!blocked.test(eventScript), `event script should not include blocked marker: ${blocked}`);
});

[
  "business_name",
  "owner_name",
  "business_phone",
  "owner_cell",
  "summary_email",
  "summary_sms_number",
  "setup_guide_sms_recipient",
  "transfer_number",
  "callback_rules",
  "services_offered",
  "service_area",
  "emergency_rules",
  "special_notes",
  "formData",
  "FormData"
].forEach((piiMarker) => {
  assert.ok(!eventScript.includes(piiMarker), `event script should not capture setup form content marker: ${piiMarker}`);
});

[
  "event_name",
  "page",
  "plan",
  "cta",
  "destination_type",
  "source",
  "utm_source",
  "utm_campaign",
  "device_hint",
  "timestamp",
  "session_placeholder",
  "ctos_learning_tag"
].forEach((field) => {
  assert.ok(eventScript.includes(field), `event script should include payload field ${field}`);
});

const simulation = JSON.parse(read("tests/fixtures/funnel-event-layer/simulation-events.json"));
assert.strictEqual(simulation.real_user_data_collected, false, "simulation should not collect real user data");
assert.strictEqual(simulation.provider_calls_made, false, "simulation should not call providers");
[
  "homepage_cta_click",
  "pricing_plan_click",
  "card_checkout_view",
  "card_checkout_start",
  "setup_view",
  "setup_form_submitted",
  "setup_confirmation_view",
  "demo_call_tap",
  "text_us_tap",
  "paid_cta_click"
].forEach((eventName) => {
  assert.ok(simulation.events.some((event) => event.event_name === eventName), `simulation missing ${eventName}`);
});
assert.strictEqual(simulation.events.length, 10, "simulation should cover the ten required buyer-path events");

const csv = read("tests/fixtures/funnel-event-layer/simulation-events.csv");
[
  "event_name",
  "page",
  "plan",
  "cta",
  "destination_type",
  "source",
  "utm_source",
  "utm_campaign",
  "device_hint",
  "timestamp",
  "session_placeholder",
  "ctos_learning_tag"
].forEach((column) => {
  assert.ok(csv.split("\n")[0].split(",").includes(column), `simulation CSV missing column ${column}`);
});

console.log("website funnel event layer tests passed");
