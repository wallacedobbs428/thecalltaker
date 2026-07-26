const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");

const cardRoutes = {
  afterhours: "/card-checkout.html?plan=afterhours",
  full247: "/card-checkout.html?plan=full247",
  custom: "/card-checkout.html?plan=custom",
};

const directCheckoutPages = [
  "website/index.html",
  "website/pricing.html",
  "website/demo.html",
  "website/paid.html",
  "website/faq.html",
];

assert.strictEqual(
  fs.existsSync(path.join(root, "website/pre-checkout.html")),
  false,
  "the intermediate pre-checkout handoff must remain deleted"
);

for (const [plan, route] of Object.entries(cardRoutes)) {
  assert.ok(read("website/index.html").includes(route), `homepage must send ${plan} directly to card checkout`);
  assert.ok(read("website/pricing.html").includes(route), `pricing must send ${plan} directly to card checkout`);
}

assert.ok(read("website/faq.html").includes(cardRoutes.full247), "FAQ must send the recommended plan directly to card checkout");
directCheckoutPages.forEach((page) => {
  assert.strictEqual(read(page).includes("/pre-checkout.html"), false, `${page} must not retain the deleted handoff`);
  assert.strictEqual(read(page).includes("buy.stripe.com"), false, `${page} must not route trials to Stripe`);
  assert.strictEqual(/https:\/\/square\.link\/u\//.test(read(page)), false, `${page} must not use legacy Square links`);
});

const checkout = read("website/card-checkout.html");
for (const plan of Object.keys(cardRoutes)) {
  assert.ok(checkout.includes(`${plan}: {`), `card checkout must define ${plan}`);
}
assert.ok(checkout.includes("$0.00"), "checkout must disclose the amount due today");
assert.ok(checkout.includes("14-day trial"), "checkout must disclose the trial term");
assert.ok(checkout.includes("consentToStoreCard:true"), "checkout must collect reusable-card consent");
assert.ok(checkout.includes("result.setupToken"), "checkout must require a signed setup token");
assert.ok(checkout.includes("result.receipt"), "checkout must require the enrollment receipt");
assert.ok(
  checkout.includes("window.location.replace('/setup.html?plan='") &&
    checkout.includes("&trial=started&receipt=") &&
    checkout.includes("#binding="),
  "successful enrollment must automatically open receipt-bound setup"
);

const setup = read("website/setup.html");
const setupScript = read("website/setup-form.js");
[
  "business_name",
  "owner_name",
  "business_phone",
  "owner_cell",
  "summary_email",
  "gideon_answer_mode",
  "business_hours",
  "business_timezone",
  "services_offered",
  "service_area",
  "emergency_rules",
  "urgent_action_preference",
  "summary_destination",
  "phone_provider",
  "current_forwarding_status",
  "forwarding_ability",
  "what_ai_should_never_say",
].forEach((field) => {
  assert.ok(setup.includes(`name="${field}"`), `setup must collect critical field ${field}`);
});

assert.ok(setupScript.includes('"phone_provider"'), "phone provider must be part of the setup payload contract");
assert.ok(setupScript.includes('"current_forwarding_status"'), "forwarding status must be part of the setup payload contract");
assert.ok(
  setupScript.includes('payload.urgent_action_preference === "transfer"') &&
    setupScript.includes('field: "transfer_number"'),
  "urgent transfer selection must require a destination number"
);
assert.ok(setupScript.includes("setupBindingToken"), "setup must verify its signed enrollment binding");
assert.ok(setupScript.includes("trialReceiptFromQuery"), "setup must verify its enrollment receipt");
assert.ok(setupScript.includes("https://call-taker-os.vercel.app/api/public/setup-intake"), "setup must submit to protected intake");

console.log("website direct trial-to-setup funnel tests passed");
