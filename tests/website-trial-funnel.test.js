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

assert.strictEqual(
  checkoutHtml.includes("paypal.me") || checkoutHtml.includes("venmo.com"),
  false,
  "public checkout should use Square links instead of manual PayPal or Venmo payment links"
);

[
  ["After-Hours Capture", 97],
  ["Revenue Recovery System", 497],
  ["Operational Infrastructure", 997],
].forEach(([planName, price]) => {
  assert.ok(checkoutHtml.includes(planName), `checkout should display ${planName}`);
  assert.ok(checkoutHtml.includes(`price: ${price}`), `checkout should configure ${planName} at $${price}/mo`);
});

assert.ok(
  checkoutHtml.includes("https://square.link/u/2hfmRPY7"),
  "checkout should use the configured Square link for the public $97 trial path"
);

assert.ok(
  checkoutHtml.includes("full247: 'https://square.link/u/S305ewBr'") &&
    checkoutHtml.includes("premium: 'https://square.link/u/OpwWF9Sa'"),
  "checkout should use the configured Square links for the public $497 and $997 trial paths"
);

assert.ok(
  checkoutHtml.includes("Revenue Recovery System: 14 days free, then $497/mo") &&
    checkoutHtml.includes("Operational Infrastructure: 14 days free, then $997/mo"),
  "checkout should state post-trial monthly billing terms before Square opens"
);

assert.ok(
  checkoutHtml.includes("Choose the plan before the trial starts.") &&
    checkoutHtml.includes("Payment details are entered on Square-hosted checkout."),
  "checkout should present a focused premium plan-selection experience"
);

assert.ok(
  checkoutHtml.includes('id="plans"'),
  "checkout should keep a plan-selection anchor before provider checkout"
);

assert.ok(
  checkoutHtml.includes("Trial summary") && checkoutHtml.includes("unless canceled before renewal"),
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
