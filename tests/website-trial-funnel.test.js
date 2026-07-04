const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function listFiles(relativeDir) {
  const absoluteDir = path.join(root, relativeDir);
  return fs.readdirSync(absoluteDir, { withFileTypes: true }).flatMap((entry) => {
    const relativePath = path.join(relativeDir, entry.name);
    if (entry.isDirectory()) return listFiles(relativePath);
    return relativePath;
  });
}

const publicCheckoutPages = [
  "website/index.html",
  "website/pricing.html",
  "website/paid.html",
  "website/pre-checkout.html",
  "website/checkout.html",
  "website/pay.html",
  "website/demo.html",
  "website/faq.html",
  "website/signup.html",
  "website/pilot/index.html",
  "website/go.html",
  "website/try-funnel/checkout.html",
];

const publicCheckoutHtml = publicCheckoutPages.map(read).join("\n");
const publicWebsiteCodeFiles = listFiles("website").filter((file) => /\.(html|js)$/.test(file));
const squareCheckout = {
  afterhours: "https://square.link/u/cSiXiuLx",
  full247: "https://square.link/u/TQseWnAY",
  custom: "https://square.link/u/RSjzTrCn"
};
const preCheckoutRoutes = {
  afterhours: "/pre-checkout.html?plan=afterhours",
  full247: "/pre-checkout.html?plan=full247",
  custom: "/pre-checkout.html?plan=custom"
};

assert.strictEqual(
  publicCheckoutHtml.includes("buy.stripe.com"),
  false,
  "public checkout funnel should not send buyers to Stripe checkout links"
);

assert.strictEqual(
  publicCheckoutHtml.includes("Stripe"),
  false,
  "public checkout funnel copy should not imply Stripe checkout"
);

[
  ["website/index.html", preCheckoutRoutes.afterhours],
  ["website/index.html", preCheckoutRoutes.full247],
  ["website/index.html", preCheckoutRoutes.custom],
  ["website/pricing.html", preCheckoutRoutes.afterhours],
  ["website/pricing.html", preCheckoutRoutes.full247],
  ["website/pricing.html", preCheckoutRoutes.custom],
  ["website/demo.html", preCheckoutRoutes.afterhours],
  ["website/demo.html", preCheckoutRoutes.full247],
  ["website/demo.html", preCheckoutRoutes.custom],
  ["website/paid.html", preCheckoutRoutes.afterhours],
  ["website/paid.html", preCheckoutRoutes.full247],
  ["website/paid.html", preCheckoutRoutes.custom],
  ["website/faq.html", preCheckoutRoutes.full247],
].forEach(([page, expectedRoute]) => {
  assert.ok(
    read(page).includes(expectedRoute),
    `${page} should route checkout CTA through pre-checkout handoff: ${expectedRoute}`
  );
});

const checkoutHtml = read("website/checkout.html");
const preCheckoutHtml = read("website/pre-checkout.html");
const intakeHtml = read("website/onboarding/intake.html");
const customerBuyerPathPages = [
  "website/index.html",
  "website/pricing.html",
  "website/paid.html",
  "website/pre-checkout.html",
  "website/checkout.html",
  "website/pay.html",
  "website/demo.html",
  "website/faq.html",
  "website/signup.html",
];

[
  "within 2 minutes",
  "AI setup call",
  "same-day setup questions",
  "AI will call",
  "calls you after checkout",
  "instant call",
  "2 minute setup",
  "Takes 2 minutes",
  "automatic post-payment call",
].forEach((unsafeSetupPromise) => {
  customerBuyerPathPages.forEach((page) => {
    assert.strictEqual(
      read(page).toLowerCase().includes(unsafeSetupPromise.toLowerCase()),
      false,
      `${page} should not imply the old post-payment AI setup-call flow: ${unsafeSetupPromise}`
    );
  });
});

[
  "within 2 minutes",
  "AI setup call",
  "same-day setup questions",
  "AI will call",
  "calls you after checkout",
  "instant call",
  "2 minute setup",
  "Takes 2 minutes",
  "automatic post-payment call",
  "Our AI will call you",
].forEach((unsafePublicPhrase) => {
  publicWebsiteCodeFiles.forEach((page) => {
    assert.strictEqual(
      read(page).toLowerCase().includes(unsafePublicPhrase.toLowerCase()),
      false,
      `${page} should not contain superseded setup-call or instant-callback language: ${unsafePublicPhrase}`
    );
  });
});

[
  [/Gideon.{0,80}setup call/i, "Gideon should not be positioned as the post-payment setup caller"],
  [/Gideon.{0,80}after checkout/i, "Gideon should not be promised immediately after checkout"],
  [/Gideon.{0,80}payment/i, "Gideon should not be tied to payment completion"],
  [/setup.{0,80}before Gideon goes live/i, "setup copy should describe questions, internal build, forwarding, and testing instead of a vague Gideon-goes-live review"],
].forEach(([unsafeRegex, message]) => {
  customerBuyerPathPages.forEach((page) => {
    assert.strictEqual(
      unsafeRegex.test(read(page)),
      false,
      `${page} has unsafe setup wording: ${message}`
    );
  });
});

[
  ["website/index.html", "60-second setup questions after payment"],
  ["website/index.html", "Choose a plan, pay through secure Square checkout"],
  ["website/pricing.html", "After payment, answer the 60-second setup questions"],
  ["website/pricing.html", "thecalltaker.com/setup.html"],
  ["website/pricing.html", "If Square does not send you back"],
  ["website/pricing.html", "the internal build can start"],
  ["website/pre-checkout.html", "Checkout, then 60-second setup."],
  ["website/pre-checkout.html", "After payment, you’ll answer the short setup questions"],
  ["website/pre-checkout.html", "After payment, setup questions take about 60 seconds"],
  ["website/faq.html", "After payment, answer the 60-second setup questions"],
  ["website/faq.html", "What happens after I pay?"],
  ["website/faq.html", "If Square does not automatically send you back"],
  ["website/faq.html", "Do not change your phone system during checkout"],
  ["website/checkout.html", "After payment, answer the 60-second setup questions"],
  ["website/checkout.html", "I already paid"],
  ["website/pay.html", "After payment, answer the 60-second setup questions"],
  ["website/pay.html", "I already paid"],
].forEach(([page, expected]) => {
  assert.ok(read(page).includes(expected), `${page} should explain the payment-to-setup path: ${expected}`);
});

assert.strictEqual(
  checkoutHtml.includes("paypal.me") || checkoutHtml.includes("venmo.com"),
  false,
  "public checkout should use Square links instead of manual PayPal or Venmo payment links"
);

assert.ok(
  checkoutHtml.includes(squareCheckout.afterhours),
  "legacy checkout redirect should use the configured Square checkout URL for the public $97 path"
);

[
  squareCheckout.afterhours,
  squareCheckout.full247,
  squareCheckout.custom,
].forEach((expectedSquareLink) => {
  assert.ok(
    preCheckoutHtml.includes(expectedSquareLink),
    `pre-checkout should preserve the approved Square destination: ${expectedSquareLink}`
  );
});

[
  "website/index.html",
  "website/pricing.html",
  "website/demo.html",
  "website/faq.html",
].forEach((page) => {
  Object.values(squareCheckout).forEach((squareLink) => {
    assert.strictEqual(
      read(page).includes(squareLink),
      false,
      `${page} should not bypass the pre-checkout handoff with direct Square CTA: ${squareLink}`
    );
  });
});

assert.ok(
  checkoutHtml.includes(squareCheckout.full247) &&
    checkoutHtml.includes(squareCheckout.custom),
  "legacy checkout redirect should use the configured Square checkout URLs for the public $497 and $997 paths"
);

assert.strictEqual(
  publicCheckoutHtml.includes("https://square.link/u/POTLUBKa"),
  false,
  "public funnel pages should not use the deprecated single-plan Square link"
);

assert.ok(
  checkoutHtml.includes("window.location.replace") &&
    checkoutHtml.includes("Taking you to Square checkout"),
  "legacy checkout should redirect immediately instead of showing an intermediate checkout page"
);

[
  "prefetch",
  "preload",
  "prerender",
  "preconnect",
  "dns-prefetch",
].forEach((rel) => {
  ["website/index.html", "website/pricing.html", "website/faq.html", "website/pre-checkout.html"].forEach((page) => {
    assert.strictEqual(
      new RegExp(`<link[^>]+rel=["']${rel}["'][^>]+(?:href=["'](?:https:)?//checkout\\.square\\.site|href=["']https://checkout\\.square\\.site)`, "i").test(read(page)),
      false,
      `${page} should not ${rel} Square checkout before buyer intent`
    );
  });
});

assert.ok(Buffer.byteLength(preCheckoutHtml, "utf8") < 15000, "pre-checkout should stay under 15 KB");
[
  "<script src=",
  "fetch(",
  "gtag",
  "fbq",
  "cbq",
  "googletagmanager",
  "connect.facebook.net",
  "tracking.thecalltaker.com",
  "script.js",
  "<img",
  "<picture",
  "<source",
  "background-image",
  "gideon-service-homepage-hero",
  "247-call-coverage-v3",
].forEach((heavyMarker) => {
  assert.strictEqual(
    preCheckoutHtml.toLowerCase().includes(heavyMarker.toLowerCase()),
    false,
    `pre-checkout should stay lightweight and avoid heavy marker: ${heavyMarker}`
  );
});

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
  "after-hours-capture-v3.webp",
  "247-call-coverage-v3.webp",
  "custom-call-coverage-v3.webp",
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
    demoHtml.includes("Square handles checkout") &&
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

console.log("website payment setup funnel regression tests passed");
