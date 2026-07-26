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
    setup_guide_sms_recipient: "(615) 555-2202",
    gideon_answer_mode: "overflow",
    business_hours: "Monday-Friday 8:00 AM-5:00 PM",
    after_hours_rules: "Answer after hours and collect caller name, number, door issue, and urgency.",
    services_offered: "Garage door repair, spring replacement, opener repair, new door estimates.",
    service_area: "Brentwood, Franklin, Nashville.",
    emergency_rules: "If the door is stuck open or the customer cannot secure the home, mark urgent.",
    transfer_number: "(615) 555-2202",
    urgent_action_preference: "text/call the owner",
    callback_rules: "Urgent calls get same-day callback. Routine calls get next-business-day callback.",
    summary_destination: "Email garage-owner@example.com and text the owner.",
    forwarding_ability: "yes",
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
    gideon_answer_mode: "after-hours",
    business_hours: "Monday-Friday 8:00 AM-5:00 PM",
    after_hours_rules: "Answer after hours and collect caller details.",
    services_offered: "Primary service, repair service, estimate requests.",
    service_area: "Brentwood, Franklin, Nashville.",
    emergency_rules: "If urgent or unsafe, request immediate callback.",
    transfer_number: "(615) 555-3002",
    urgent_action_preference: "summarize only",
    callback_rules: "Urgent calls get same-day callback. Non-urgent calls get next-business-day callback.",
    summary_destination: "Email owner@example.com.",
    phone_provider: "Not sure",
    current_forwarding_status: "not sure",
    forwarding_ability: "yes",
    ai_greeting_preference: "Thanks for calling Minimum Sample Co. How can I help?",
    what_ai_should_never_say: "None.",
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
    gideon_answer_mode: "not sure",
    business_hours: "Monday-Friday 8:00 AM-5:00 PM",
    after_hours_rules: "Answer after hours and collect caller details.",
    services_offered: "Repair, maintenance, estimates.",
    service_area: "Nashville and surrounding areas.",
    emergency_rules: "If urgent, request immediate callback.",
    transfer_number: "(615) 555-3102",
    urgent_action_preference: "text/call the owner",
    callback_rules: "Urgent same-day callback. Routine next-business-day callback.",
    summary_destination: "Email owner@example.com.",
    forwarding_ability: "not sure",
    ai_greeting_preference: "Thanks for calling Unknown Provider Sample Co. How can I help?",
    phone_provider: "not sure",
    current_forwarding_status: "Not sure",
    what_ai_should_never_say: "None.",
    authorized_to_configure_forwarding: true,
  },
  "missing-required-fields-payload.json": {
    plan_purchased: "$497 Revenue Recovery System",
    business_name: "Missing Required Sample Co.",
    owner_name: "Jordan Owner",
    owner_cell: "(615) 555-3202",
    summary_email: "owner@example.com",
    gideon_answer_mode: "after-hours",
    business_hours: "Monday-Friday 8:00 AM-5:00 PM",
    after_hours_rules: "Answer after hours.",
    services_offered: "Repair and estimates.",
    service_area: "Nashville.",
    emergency_rules: "If urgent, request immediate callback.",
    transfer_number: "(615) 555-3202",
    urgent_action_preference: "text/call the owner",
    callback_rules: "Urgent same-day callback.",
    summary_destination: "Email owner@example.com.",
    forwarding_ability: "yes",
    ai_greeting_preference: "Thanks for calling Missing Required Sample Co.",
    what_ai_should_never_say: "None.",
    authorized_to_configure_forwarding: true,
  },
};

Object.values(fallbackFixtures).forEach((payload) => {
  if (payload.business_hours) {
    payload.business_default_open_time = "08:00";
    payload.business_default_close_time = "17:00";
    payload.business_timezone = "America/Chicago";
  }
});

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function readJson(fileName) {
  const fixturePath = handoffRoot ? path.join(handoffRoot, fileName) : "";
  let payload;
  if (fixturePath && fs.existsSync(fixturePath)) {
    payload = JSON.parse(fs.readFileSync(fixturePath, "utf8"));
  } else {
    payload = fallbackFixtures[fileName];
  }
  return payload && payload.business_hours
    ? {
        ...payload,
        business_default_open_time: payload.business_default_open_time || "08:00",
        business_default_close_time: payload.business_default_close_time || "17:00",
        business_timezone: payload.business_timezone || "America/Chicago",
      }
    : payload;
}

const setupHtml = read("website/setup.html");
const confirmationHtml = read("website/setup-confirmation.html");
const setupFormJs = read("website/setup-form.js");
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
  "business_name",
  "business_phone",
  "owner_name",
  "summary_email",
  "owner_cell",
  "gideon_answer_mode",
  "business_hours",
  "business_default_open_time",
  "business_default_close_time",
  "business_timezone",
  "service_area",
  "services_offered",
  "emergency_rules",
  "summary_destination",
  "urgent_action_preference",
  "what_ai_should_never_say",
  "forwarding_ability",
].forEach((field) => {
  assert.ok(
    setupForm.REQUIRED_FIELDS.includes(field),
    `${field} should be required to launch`
  );
});

[
  "after_hours_rules",
  "callback_rules",
  "ai_greeting_preference",
  "appointment_booking_rules",
  "preferred_go_live_time",
  "special_notes",
].forEach((field) => {
  assert.strictEqual(
    setupHtml.includes(`name="${field}"`),
    false,
    `${field} should not be asked on the 60-second setup form`
  );
});

["phone_provider", "current_forwarding_status"].forEach((field) => {
  assert.ok(setupHtml.includes(`name="${field}"`), `${field} should be collected on the critical setup form`);
  assert.ok(setupForm.REQUIRED_FIELDS.includes(field), `${field} should be required before launch setup is accepted`);
});

assert.ok(
  setupHtml.includes("Your selected plan is locked to this setup") &&
    setupHtml.includes("The plan comes from confirmed checkout and cannot be changed here."),
  "setup form should be clear that a signed, locked checkout plan is required"
);

assert.ok(
  setupHtml.includes('name="business_default_open_time"') &&
    setupHtml.includes('value="08:00"') &&
    setupHtml.includes('name="business_default_close_time"') &&
    setupHtml.includes('value="17:00"') &&
    setupHtml.includes('name="business_timezone"') &&
    setupHtml.includes('value="America/Chicago" selected'),
  "setup form should collect structured default hours and an IANA timezone while preserving free-text business_hours"
);

assert.ok(
  setupHtml.includes("Set up your call handling") &&
    setupHtml.includes("Four focused steps") &&
    setupHtml.includes("Continue to coverage"),
  "setup form should give paid buyers a clear post-checkout handoff"
);

assert.strictEqual(
  (setupHtml.match(/<fieldset class="setup-section" data-setup-step="/g) || []).length,
  4,
  "setup form should keep the four short setup sections"
);

[
  "Setup progress",
  "Business basics",
  "Calls and hours",
  "Phone setup and handoff",
  "Confirm",
  "setup-progress-card",
  "setup-step-badge",
  "setup-step-title",
  "Best mobile for urgent setup issues",
  "When should Gideon answer?",
  "Who provides your business phone service?",
  "This answer determines the forwarding instructions we prepare first.",
  "For urgent calls, what should Gideon do?",
  "Can you access your phone settings or provider account?",
  "Before we build",
  "We use these answers to configure your call taker.",
  "Do not change your phone system yet.",
  "Live routing starts only after forwarding/testing is confirmed.",
  "Submit setup questions",
  "Continue to phone setup",
  "Review setup",
].forEach((marker) => {
  assert.ok(
    setupHtml.includes(marker),
    `setup form should include V2 setup marker: ${marker}`
  );
});

assert.ok(
  setupFormJs.includes('setup-confirmation.html?status=') &&
    setupFormJs.includes("root.location.assign(next)") &&
    setupFormJs.includes("deriveSetupResponse(payload)"),
  "setup form submit should still stage receipt data and route to setup-confirmation"
);

[
  "Setup questions submitted",
  "Your setup questions were received",
  "The internal build starts from these basics",
  "We have the basics needed to start the internal build",
  "Next, The Call Taker builds from these answers and sends forwarding instructions or walks you through setup if needed",
  "Setup Questions",
  "Received",
  "Checkout reference",
  "May still need verification",
  "Build status",
  "Core details received",
  "After build + testing",
  "Your AI receptionist goes live after test confirmation",
  "Do not change your phone system yet unless instructed",
  "Review the setup guide first. The Call Taker will help verify forwarding and test calls before go-live.",
  "Return Home",
  "View Pricing",
  "Review FAQ",
  "What we're preparing",
  "First call path",
  "Urgent-call rules",
  "Summary delivery rules",
  "Manual review is only for $997+ custom builds",
  "Checkout",
  "Internal Build",
  "Forwarding/Test",
  "Live",
  "AI receptionist setup for service businesses.",
  'href="/">Home</a>',
  'href="/pricing.html">Pricing</a>',
  'href="/faq.html">FAQ</a>',
  'class="setup-shell setup-review-shell"',
  'class="setup-note"',
  'class="setup-status-grid"',
  'class="setup-progress"',
  'class="setup-section setup-review-section"',
].forEach((marker) => {
  assert.ok(
    confirmationHtml.includes(marker),
    `confirmation page should include V2 setup marker: ${marker}`
  );
});

const confirmationActionsStart = confirmationHtml.indexOf('<div class="receipt-actions"');
const confirmationActionsEnd = confirmationHtml.indexOf("</div>", confirmationActionsStart);
assert.ok(
  confirmationActionsStart >= 0 && confirmationActionsEnd > confirmationActionsStart,
  "confirmation page should include a CTA row"
);
const confirmationActions = confirmationHtml.slice(confirmationActionsStart, confirmationActionsEnd);
assert.strictEqual(
  /<a\b[^>]*class="[^"]*\bbtn\b[^"]*"[^>]*>\s*<\/a>/.test(confirmationActions),
  false,
  "confirmation page should not include blank CTA buttons"
);
assert.ok(
  confirmationHtml.includes(".setup-confirmation-page .receipt-actions .btn-secondary") &&
    confirmationHtml.includes("color: #061610") &&
    confirmationHtml.includes("Return Home") &&
    confirmationHtml.includes("View Pricing") &&
    confirmationHtml.includes("Review FAQ"),
  "confirmation page CTA buttons should be clearly labeled and readable in light mode"
);

[
  "Setup complete",
  "setup is live",
  "Your AI is live",
  "Checkout verified",
  "payment verification complete",
  "AI setup call",
  "AI will call",
  "Our AI will call you",
  "within 2 minutes",
].forEach((unsafeMarker) => {
  assert.strictEqual(
    confirmationHtml.includes(unsafeMarker),
    false,
    `confirmation page should not include unsafe setup claim: ${unsafeMarker}`
  );
});

assert.ok(
  confirmationHtml.includes('<span class="logo-text">The Call<span>Taker</span></span>') &&
    setupHtml.includes('<span class="logo-text">The Call<span>Taker</span></span>') &&
    !confirmationHtml.includes("The Call <span>Taker</span>") &&
    !setupHtml.includes("The Call <span>Taker</span>"),
  "setup flow footers should use the unbroken brand logo text"
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
  "setup_help_needed",
  "unknown forwarding ability should produce setup_help_needed status"
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
  gideon_answer_mode: "not sure",
  business_hours: "Monday-Friday 8am-5pm",
  business_default_open_time: "08:00",
  business_default_close_time: "17:00",
  business_timezone: "America/Chicago",
  services_offered: "HVAC repair",
  service_area: "Nashville",
  emergency_rules: "No heat and no AC are urgent",
  transfer_number: "(629) 555-0103",
  setup_guide_sms_recipient: "(629) 555-0102",
  urgent_action_preference: "text/call the owner",
  summary_destination: "Email owner@example.com",
  forwarding_ability: "not sure",
  what_ai_should_never_say: "Do not promise exact arrival times.",
  authorized_to_configure_forwarding: "on",
  phone_provider: "Not sure",
  current_forwarding_status: "not sure",
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
assert.strictEqual(browserPayload.business_default_open_time, "08:00");
assert.strictEqual(browserPayload.business_default_close_time, "17:00");
assert.strictEqual(browserPayload.business_timezone, "America/Chicago");
assert.ok(setupForm.BUSINESS_TIMEZONE_OPTIONS.includes(browserPayload.business_timezone));

const invalidStructuredHours = {
  ...browserPayload,
  business_default_open_time: "8am",
  business_default_close_time: "25:00",
  business_timezone: "Central Time",
};
const invalidStructuredHoursResult = setupForm.validatePayload(invalidStructuredHours);
assert.strictEqual(invalidStructuredHoursResult.valid, false);
assert.deepStrictEqual(
  invalidStructuredHoursResult.errors.map((error) => error.field).sort(),
  ["business_default_close_time", "business_default_open_time", "business_timezone"].sort(),
  "setup packet should fail closed on non-24-hour times or a non-IANA timezone"
);

const equalStructuredHoursResult = setupForm.validatePayload({
  ...browserPayload,
  business_default_open_time: "09:00",
  business_default_close_time: "09:00",
});
assert.strictEqual(equalStructuredHoursResult.valid, false);
assert.ok(
  equalStructuredHoursResult.errors.some(
    (error) => error.field === "business_default_close_time" && /must be different/.test(error.message)
  ),
  "setup packet should reject equal default opening and closing times"
);
assert.strictEqual(
  browserPayload.setup_guide_sms_recipient,
  "(629) 555-0102",
  "browser form payload should preserve the setup guide SMS recipient for LEFT's guide workflow"
);
assert.strictEqual(
  setupForm.deriveSetupResponse(browserPayload).status,
  "setup_help_needed",
  "browser form payload with unknown forwarding ability should be staged for setup help"
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
  assert.strictEqual(
    html.includes('href="/setup.html'),
    false,
    `${page} must not expose an unsigned direct setup bypass`
  );
});
assert.ok(
  read("website/card-checkout.html").includes("#binding=' + encodeURIComponent(result.setupToken)") &&
    read("website/card-checkout.html").includes("&trial=started&receipt=' + encodeURIComponent(result.receipt)"),
  "confirmed checkout must be the only public source of the signed setup route"
);

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
