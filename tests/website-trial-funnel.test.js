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
  "website/faq.html",
  "website/pilot/index.html",
  "website/go.html",
  "website/try-funnel/checkout.html",
];

const publicTrialHtml = publicTrialPages.map(read).join("\n");
const squareCheckout = {
  afterhours: "https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/HywRLQ4aYHQ0ojpIbsnBPnrelqAZY",
  full247: "https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/RFxESyTjwZQuIS2xceV8983Pvj8YY",
  premium: "https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/PCGvURHQSoL8LnXbmQ3olB0imFBZY"
};

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
  ["website/index.html", squareCheckout.afterhours],
  ["website/index.html", squareCheckout.full247],
  ["website/index.html", squareCheckout.premium],
  ["website/pricing.html", squareCheckout.afterhours],
  ["website/pricing.html", squareCheckout.full247],
  ["website/pricing.html", squareCheckout.premium],
  ["website/demo.html", squareCheckout.afterhours],
  ["website/demo.html", squareCheckout.full247],
  ["website/demo.html", squareCheckout.premium],
  ["website/faq.html", squareCheckout.full247],
].forEach(([page, expectedHref]) => {
  assert.ok(
    read(page).includes(expectedHref),
    `${page} should route trial CTA directly to Square checkout: ${expectedHref}`
  );
});

const checkoutHtml = read("website/checkout.html");
const intakeHtml = read("website/onboarding/intake.html");

assert.strictEqual(
  checkoutHtml.includes("paypal.me") || checkoutHtml.includes("venmo.com"),
  false,
  "public checkout should use Square links instead of manual PayPal or Venmo payment links"
);

assert.ok(
  checkoutHtml.includes(squareCheckout.afterhours),
  "legacy checkout redirect should use the configured Square checkout URL for the public $97 trial path"
);

assert.ok(
  checkoutHtml.includes(squareCheckout.full247) &&
    checkoutHtml.includes(squareCheckout.premium),
  "legacy checkout redirect should use the configured Square checkout URLs for the public $497 and $997 trial paths"
);

assert.strictEqual(
  publicTrialHtml.includes("https://square.link/u/POTLUBKa"),
  false,
  "public funnel pages should not use the deprecated single-plan Square trial link"
);

assert.ok(
  checkoutHtml.includes("window.location.replace") &&
    checkoutHtml.includes("Taking you to Square checkout"),
  "legacy checkout should redirect immediately instead of showing an intermediate checkout page"
);

[
  "/checkout.html?plan=afterhours",
  "/checkout.html?plan=full247",
  "/checkout.html?plan=premium",
].forEach((deprecatedLocalRoute) => {
  assert.strictEqual(
    read("website/index.html").includes(deprecatedLocalRoute) ||
      read("website/pricing.html").includes(deprecatedLocalRoute) ||
      read("website/demo.html").includes(deprecatedLocalRoute) ||
      read("website/faq.html").includes(deprecatedLocalRoute),
    false,
    `public CTAs should not stop on local checkout route: ${deprecatedLocalRoute}`
  );
});

const pricingHtml = read("website/pricing.html");

[
  "Compare the coverage level, follow-up support, and setup depth in each plan.",
  "Custom call paths for different jobs",
  "Approved follow-up setup",
  "Clear owner notifications",
  "Call review notes when available",
].forEach((expected) => {
  assert.ok(pricingHtml.includes(expected), `pricing should explain tier differences beyond checkmarks: ${expected}`);
});

assert.ok(
  read("website/index.html").includes('href="/pricing.html">Pricing') &&
    read("website/index.html").includes('href="#pricing" class="hero-ghost"'),
  "homepage nav should open the full pricing page while the hero keeps a quick scroll pricing CTA"
);

[
  "Calling you now",
  "Pick up your phone",
  "SMS, email, or scoped CRM routing",
  "You get every lead",
  "Takes 2 minutes",
].forEach((unsafeCopy) => {
  assert.strictEqual(
    read("website/index.html").includes(unsafeCopy),
    false,
    `homepage should avoid instant activation or live-provider copy: ${unsafeCopy}`
  );
});

assert.strictEqual(
  read("website/index.html").includes("fetch(") || read("website/index.html").includes("atob("),
  false,
  "homepage floating demo widget should not send webhook notifications from the public page"
);

[
  "after-hours-capture-v3.png",
  "247-call-coverage-v3.png",
  "custom-call-coverage-v3.png",
].forEach((expected) => {
  assert.ok(pricingHtml.includes(expected), `pricing should use the upgraded plan visual: ${expected}`);
});

const demoHtml = read("website/demo.html");

assert.strictEqual(
  demoHtml.includes("We'll text you shortly") ||
    demoHtml.includes("Text Me") ||
    demoHtml.includes("text-me"),
  false,
  "demo page should not imply SMS follow-up exists without a live provider path"
);

assert.ok(
  demoHtml.includes("Choose the setup path") &&
    demoHtml.includes("Square shows the post-trial price") &&
    demoHtml.includes("No SMS, provider routing, booking, or backend sync is implied"),
  "demo page should move preview users into a clear, provider-safe plan-selection follow-up"
);

[
  "48h",
  "<2s",
  "No delay",
  "notified immediately",
  "provider routing is reviewed",
  "CTOS-backed",
].forEach((unsafeCopy) => {
  assert.strictEqual(
    read("website/services.html").includes(unsafeCopy) ||
      read("website/checkout.html").includes(unsafeCopy) ||
      read("website/faq.html").includes(unsafeCopy),
    false,
    `services, checkout, and FAQ should avoid exact-speed, jargon, or provider-activation promises: ${unsafeCopy}`
  );
});

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
