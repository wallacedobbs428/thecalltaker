const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

const publicTrialPages = [
  "website/index.html",
  "website/pricing.html",
  "website/checkout.html",
  "website/pay.html",
  "website/demo.html",
  "website/pilot/index.html",
  "website/go.html",
  "website/try-funnel/checkout.html",
];

const publicTrialHtml = publicTrialPages.map(read).join("\n");

assert.strictEqual(
  publicTrialHtml.includes("buy.stripe.com"),
  false,
  "public trial funnel should not send buyers to Stripe checkout links"
);

assert.strictEqual(
  publicTrialHtml.includes("Stripe"),
  false,
  "public trial funnel copy should not imply Stripe checkout"
);

[
  ["website/index.html", "/checkout.html?plan=afterhours"],
  ["website/index.html", "/checkout.html?plan=full247"],
  ["website/index.html", "/checkout.html?plan=premium"],
  ["website/pricing.html", "/checkout.html?plan=afterhours"],
  ["website/pricing.html", "/checkout.html?plan=full247"],
  ["website/pricing.html", "/checkout.html?plan=premium"],
].forEach(([page, expectedHref]) => {
  assert.ok(
    read(page).includes(expectedHref),
    `${page} should route its pricing card to ${expectedHref}`
  );
});

const checkoutHtml = read("website/checkout.html");
const intakeHtml = read("website/onboarding/intake.html");

[
  ["After-Hours Capture", 97],
  ["Revenue Recovery System", 497],
  ["Operational Infrastructure", 997],
].forEach(([planName, price]) => {
  assert.ok(checkoutHtml.includes(planName), `checkout should display ${planName}`);
  assert.ok(checkoutHtml.includes(`price: ${price}`), `checkout should configure ${planName} at $${price}/mo`);
});

assert.ok(
  checkoutHtml.includes("https://square.link/u/POTLUBKa"),
  "checkout should use the configured Square link for the public $97 trial path"
);

assert.ok(
  checkoutHtml.includes("Request $497 Square Trial Setup") &&
    checkoutHtml.includes("Request $997+ Square Trial Setup"),
  "checkout should not send higher tiers to a generic or wrong payment link"
);

assert.ok(
  checkoutHtml.includes('href="#plans" class="header-cta"'),
  "checkout header trial CTA should scroll to plan selection before provider checkout"
);

assert.ok(
  checkoutHtml.includes("Selected plan: ") && checkoutHtml.includes("14 days free, then $"),
  "checkout should show selected plan and post-trial monthly billing copy"
);

[
  ["afterhours", "After-Hours Capture ($97/mo)"],
  ["full247", "Revenue Recovery System ($497/mo)"],
  ["premium", "Operational Infrastructure ($997+/mo)"],
].forEach(([planKey, label]) => {
  assert.ok(intakeHtml.includes(`data-plan="${planKey}"`), `intake should use current plan key ${planKey}`);
  assert.ok(intakeHtml.includes(label), `intake should use current plan label ${label}`);
});

["starter: 'full247'", "pro: 'premium'", "'after-hours': 'afterhours'"].forEach((alias) => {
  assert.ok(intakeHtml.includes(alias), `intake should preserve legacy plan alias ${alias}`);
});

assert.ok(
  intakeHtml.includes("new URLSearchParams(window.location.search).get('plan')"),
  "intake should be able to preselect a plan from the checkout success URL"
);

console.log("website trial funnel regression tests passed");
