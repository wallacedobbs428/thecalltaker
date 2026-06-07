const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const handoffRoot = process.env.TCT_LEFT_HANDOFF_ROOT || "";
const setupForm = require("../website/setup-form.js");

const fallbackFixtures = {
  "complete-497-customer-payload.json": {
    plan_purchased: "$497 Revenue Recovery System",
    square_checkout_reference: "sq_fake_checkout_ref_497",
    square_order_id: "sq_fake_order_497",
    square_payment_id: null,
    payment_verification_status: "paid_verified",
    business_name: "Harpeth Garage Door Sample Co.",
    owner_name: "Alex Carter",
    business_phone: "(615) 555-2201",
    owner_cell: "(615) 555-2202",
    summary_email: "garage-owner@example.com",
    summary_sms_number: "(615) 555-2202",
    business_hours: "Monday-Friday 8:00 AM-5:00 PM",
    after_hours_rules: "Answer after hours and collect caller name, number, door issue, and urgency.",
    services_offered: "Garage door repair, spring replacement, opener repair, new door estimates.",
    service_area: "Brentwood, Franklin, Nashville.",
    emergency_rules: "If the door is stuck open or the customer cannot secure the home, mark urgent.",
    transfer_number: "(615) 555-2202",
    callback_rules: "Urgent calls get same-day callback. Routine calls get next-business-day callback.",
    appointment_booking_rules: "Collect preferred day and time but do not confirm.",
    phone_provider: "Comcast Business",
    current_forwarding_status: "No",
    preferred_go_live_time: "Today after 2:00 PM Central",
    ai_greeting_preference: "Thanks for calling Harpeth Garage Door. How can I help?",
    what_ai_should_never_say: "Never quote exact spring replacement prices.",
    special_notes: "Ask whether the vehicle is trapped inside the garage.",
    authorized_to_configure_forwarding: true,
    source_url: "https://thecalltaker.com/setup?plan=revenue-recovery",
    submitted_at: "2026-06-07T16:00:00-05:00",
  },
  "minimum-valid-customer-payload.json": {
    plan_purchased: "$497 Revenue Recovery System",
    business_name: "Minimum Sample Co.",
    owner_name: "Sam Owner",
    business_phone: "(615) 555-3001",
    owner_cell: "(615) 555-3002",
    summary_email: "owner@example.com",
    business_hours: "Monday-Friday 8:00 AM-5:00 PM",
    after_hours_rules: "Answer after hours and collect caller details.",
    services_offered: "Primary service, repair service, estimate requests.",
    service_area: "Brentwood, Franklin, Nashville.",
    emergency_rules: "If urgent or unsafe, request immediate callback.",
    transfer_number: "(615) 555-3002",
    callback_rules: "Urgent calls get same-day callback. Non-urgent calls get next-business-day callback.",
    ai_greeting_preference: "Thanks for calling Minimum Sample Co. How can I help?",
    authorized_to_configure_forwarding: true,
  },
  "unknown-phone-provider-payload.json": {
    plan_purchased: "$497 Revenue Recovery System",
    square_checkout_reference: "sq_fake_checkout_ref_unknown_provider",
    payment_verification_status: "paid_unverified",
    business_name: "Unknown Provider Sample Co.",
    owner_name: "Taylor Owner",
    business_phone: "(615) 555-3101",
    owner_cell: "(615) 555-3102",
    summary_email: "owner@example.com",
    business_hours: "Monday-Friday 8:00 AM-5:00 PM",
    after_hours_rules: "Answer after hours and collect caller details.",
    services_offered: "Repair, maintenance, estimates.",
    service_area: "Nashville and surrounding areas.",
    emergency_rules: "If urgent, request immediate callback.",
    transfer_number: "(615) 555-3102",
    callback_rules: "Urgent same-day callback. Routine next-business-day callback.",
    ai_greeting_preference: "Thanks for calling Unknown Provider Sample Co. How can I help?",
    phone_provider: "not sure",
    current_forwarding_status: "Not sure",
    authorized_to_configure_forwarding: true,
  },
  "missing-required-fields-payload.json": {
    plan_purchased: "$497 Revenue Recovery System",
    business_name: "Missing Required Sample Co.",
    owner_name: "Jordan Owner",
    owner_cell: "(615) 555-3202",
    summary_email: "owner@example.com",
    business_hours: "Monday-Friday 8:00 AM-5:00 PM",
    after_hours_rules: "Answer after hours.",
    services_offered: "Repair and estimates.",
    service_area: "Nashville.",
    emergency_rules: "If urgent, request immediate callback.",
    transfer_number: "(615) 555-3202",
    callback_rules: "Urgent same-day callback.",
    ai_greeting_preference: "Thanks for calling Missing Required Sample Co.",
    authorized_to_configure_forwarding: true,
  },
};

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function readJson(fileName) {
  const fixturePath = handoffRoot ? path.join(handoffRoot, fileName) : "";
  if (fixturePath && fs.existsSync(fixturePath)) {
    return JSON.parse(fs.readFileSync(fixturePath, "utf8"));
  }
  return fallbackFixtures[fileName];
}

const setupHtml = read("website/setup.html");
const confirmationHtml = read("website/setup-confirmation.html");
const pricingHtml = read("website/pricing.html");
const indexHtml = read("website/index.html");
const faqHtml = read("website/faq.html");

setupForm.REQUIRED_FIELDS.forEach((field) => {
  assert.ok(
    setupHtml.includes(`name="${field}"`),
    `setup.html should collect required setup field: ${field}`
  );
});

[
  "square_checkout_reference",
  "summary_sms_number",
  "appointment_booking_rules",
  "phone_provider",
  "current_forwarding_status",
  "preferred_go_live_time",
  "what_ai_should_never_say",
  "special_notes",
  "payment_verification_status",
].forEach((field) => {
  assert.ok(
    setupHtml.includes(`name="${field}"`),
    `setup.html should collect or preserve optional setup field: ${field}`
  );
});

assert.ok(
  setupHtml.includes("This form starts the setup packet") &&
    setupHtml.includes("We may still need to verify your checkout reference"),
  "setup form should be clear that checkout verification may still happen before configuration"
);

assert.ok(
  confirmationHtml.includes("Setup form received") &&
    confirmationHtml.includes("Your setup form has been received") &&
    confirmationHtml.includes("Do not change your phone system yet unless instructed"),
  "confirmation page should use the approved setup receipt and phone-system boundary copy"
);

[
  "/Users/",
  "ctos-revenue-outbound-automation",
  "handoff-json",
  "schemas/website-setup-form-submit.schema.json",
].forEach((internalMarker) => {
  assert.strictEqual(
    setupHtml.includes(internalMarker) || confirmationHtml.includes(internalMarker),
    false,
    `public setup pages should not expose internal path marker: ${internalMarker}`
  );
});

const completePayload = readJson("complete-497-customer-payload.json");
const minimumPayload = readJson("minimum-valid-customer-payload.json");
const unknownProviderPayload = readJson("unknown-phone-provider-payload.json");
const missingRequiredPayload = readJson("missing-required-fields-payload.json");

assert.strictEqual(
  setupForm.validatePayload(completePayload).valid,
  true,
  "complete fixture payload should validate"
);

assert.strictEqual(
  setupForm.validatePayload(minimumPayload).valid,
  true,
  "minimum valid fixture payload should validate"
);

const unknownProviderResponse = setupForm.deriveSetupResponse(unknownProviderPayload);
assert.strictEqual(
  unknownProviderResponse.success,
  true,
  "unknown phone provider should still submit successfully"
);
assert.strictEqual(
  unknownProviderResponse.status,
  "forwarding_instructions_needed",
  "unknown phone provider should produce forwarding_instructions_needed status"
);

const missingRequiredValidation = setupForm.validatePayload(missingRequiredPayload);
assert.strictEqual(
  missingRequiredValidation.valid,
  false,
  "missing required fixture payload should fail validation"
);
assert.ok(
  missingRequiredValidation.missing_fields.length > 0,
  "missing required fixture payload should identify missing fields"
);

const browserPayload = setupForm.buildPayloadFromObject({
  plan_purchased: "full247",
  business_name: "Acme HVAC",
  owner_name: "Wallace Dobbs",
  business_phone: "(629) 555-0101",
  owner_cell: "(629) 555-0102",
  summary_email: "owner@example.com",
  business_hours: "Monday-Friday 8am-5pm",
  after_hours_rules: "Answer all calls after 5pm",
  services_offered: "HVAC repair",
  service_area: "Nashville",
  emergency_rules: "No heat and no AC are urgent",
  transfer_number: "(629) 555-0103",
  callback_rules: "Text owner for urgent leads",
  ai_greeting_preference: "Thanks for calling Acme.",
  authorized_to_configure_forwarding: "on",
  phone_provider: "Not sure",
}, "https://thecalltaker.com/setup.html?plan=full247", "2026-06-07T12:00:00.000Z");

assert.strictEqual(
  browserPayload.plan_purchased,
  "$497 Revenue Recovery System",
  "plan query and alias should map to the LEFT-approved $497 plan label"
);
assert.strictEqual(
  browserPayload.payment_verification_status,
  "paid_unverified",
  "public browser payload should not claim payment is verified by default"
);
assert.strictEqual(
  setupForm.deriveSetupResponse(browserPayload).status,
  "forwarding_instructions_needed",
  "browser form payload with unknown phone provider should be staged for forwarding instructions"
);

[
  ["website/index.html", indexHtml],
  ["website/pricing.html", pricingHtml],
  ["website/faq.html", faqHtml],
  ["website/start.html", read("website/start.html")],
  ["website/signup.html", read("website/signup.html")],
  ["website/checkout.html", read("website/checkout.html")],
  ["website/pay.html", read("website/pay.html")],
].forEach(([page, html]) => {
  assert.ok(
    html.includes("setup.html"),
    `${page} should include the public setup form path`
  );
});

assert.ok(
  pricingHtml.includes("Do I need to know how to set up call forwarding?") &&
    faqHtml.includes("Do I need to know how to set up call forwarding?"),
  "pricing and FAQ should answer the forwarding uncertainty objection"
);

[
  "AI will call",
  "within 2 minutes",
  "payment verification complete",
  "setup instantly live",
  "backend sync is complete",
].forEach((unsafePhrase) => {
  const haystack = [setupHtml, confirmationHtml, pricingHtml, indexHtml, faqHtml].join("\n").toLowerCase();
  assert.strictEqual(
    haystack.includes(unsafePhrase.toLowerCase()),
    false,
    `public setup path should not include unsafe promise: ${unsafePhrase}`
  );
});
