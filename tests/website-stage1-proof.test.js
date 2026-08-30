const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const cardRoutes = [
  "/card-checkout.html?plan=afterhours",
  "/card-checkout.html?plan=full247",
  "/card-checkout.html?plan=custom",
];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

const pages = {
  "website/index.html": read("website/index.html"),
  "website/pricing.html": read("website/pricing.html"),
  "website/paid.html": read("website/paid.html"),
  "website/faq.html": read("website/faq.html"),
  "website/setup.html": read("website/setup.html"),
  "website/setup-confirmation.html": read("website/setup-confirmation.html"),
  "website/checkout.html": read("website/checkout.html"),
  "website/pay.html": read("website/pay.html"),
};

const faviconSvg = read("website/favicon.svg");
const ogSvg = read("website/og-image.svg");
const manifest = JSON.parse(read("website/site.webmanifest"));

[
  "TCT",
  "role=\"img\"",
  "The Call Taker",
].forEach((marker) => {
  assert.ok(faviconSvg.includes(marker), `favicon SVG should include premium brand marker: ${marker}`);
});

[
  "Phone handset",
  "M22 16.92",
  "AI signal waves",
].forEach((phoneMarker) => {
  assert.strictEqual(
    faviconSvg.includes(phoneMarker),
    false,
    `favicon SVG should not keep the generic phone mark: ${phoneMarker}`
  );
});

assert.ok(
  fs.existsSync(path.join(root, "website/favicon.ico")) &&
    fs.existsSync(path.join(root, "website/apple-touch-icon.png")) &&
    fs.existsSync(path.join(root, "website/og-image.png")),
  "favicon, apple touch icon, and OG image files should exist"
);

assert.strictEqual(manifest.short_name, "TCT", "manifest should use the TCT short name");
assert.ok(
  manifest.icons.some((icon) => icon.src === "/favicon-192x192.png") &&
    manifest.icons.some((icon) => icon.src === "/favicon-512x512.png"),
  "manifest should reference generated brand icons"
);

[
  "The Call Taker - AI Call Answering For Missed Calls",
  "Gideon answers calls, collects caller details, and sends clean summaries after your setup questions are in.",
  "summary_large_image",
  "site.webmanifest",
].forEach((marker) => {
  assert.ok(pages["website/index.html"].includes(marker), `homepage social preview should include: ${marker}`);
});

[
  "0%",
  "MISSED CALLS",
  "LIVE AI COVERAGE",
  "Phone icon",
].forEach((unsafeOgMarker) => {
  assert.strictEqual(
    ogSvg.includes(unsafeOgMarker),
    false,
    `OG SVG should avoid unsupported or phone-icon marker: ${unsafeOgMarker}`
  );
});

const multilingualSection = pages["website/index.html"].match(
  /<!-- ═══ SECTION 5: MULTILINGUAL COVERAGE ═══ -->[\s\S]*?<!-- ═══ LIVE COUNTER BAR ═══ -->/
);

assert.ok(multilingualSection, "homepage should keep the multilingual coverage section");

[
  "Gideon can help capture caller details across common languages.",
  "Language support depends on the call flow and configuration.",
  "Caller language detected",
  "Spanish",
  "Caller understood",
  "Details captured",
  "Team summary ready",
  "WHAT YOUR TEAM SEES",
  "Clean handoff",
  "Name, phone number, job need, urgency, preferred language, and next step captured in one clean summary.",
  'href="/pricing.html"',
  'href="tel:+16292699697"',
  'data-tct-destination="live_demo_phone"',
].forEach((marker) => {
  assert.ok(multilingualSection[0].includes(marker), `multilingual section should include trust marker: ${marker}`);
});

[
  "all languages",
  "every language",
  "fluent in every language",
  "fluent in all languages",
  "perfect translation",
  "certified translation",
  "medical-grade translation",
  "legal-grade translation",
  "guaranteed translation",
].forEach((unsupportedClaim) => {
  assert.strictEqual(
    pages["website/index.html"].toLowerCase().includes(unsupportedClaim),
    false,
    `homepage should avoid unsupported multilingual claim: ${unsupportedClaim}`
  );
});

[
  "checkout.square.site",
  'rel="preload"',
  'rel="prefetch"',
  'rel="prerender"',
].forEach((speedRisk) => {
  assert.strictEqual(
    multilingualSection[0].includes(speedRisk),
    false,
    `multilingual section should not add Square or speculative load marker: ${speedRisk}`
  );
});

[
  "Simple setup before launch.",
  "06 / SETUP TRUST",
  "Reviewed before your calls go live.",
  "SAFE LAUNCH CHECKPOINTS",
  "Setup questions",
  "Test calls first",
  "Private summaries",
  "You approve flow",
  "Actual results depend on call volume, caller intent, follow-up speed, and the setup rules you approve.",
  "SAMPLE CALL FLOW: HVAC EMERGENCY",
].forEach((marker) => {
  assert.ok(pages["website/index.html"].includes(marker), `homepage should include safe setup trust marker: ${marker}`);
});

Object.entries(pages).forEach(([page, html]) => {
  [
    "within 2 minutes",
    "AI setup call",
    "AI will call",
    "Our AI will call you",
    "Setup complete",
    "setup is live",
    "Most of our customers stay",
    "American Surgical",
    "HVAC portfolio",
    "booked jobs",
    "Three steps. Five minutes.",
    "Verified production handoff",
    "Redacted client proof",
    "CALL RECORDING:",
    "CALLS EVALUATED",
    "TEAM-WORTHY",
    "LOW-VALUE SUPPRESSED",
    "TEAM HANDOFF",
    "CALLS REVIEWED",
    "square.link/u/POTLUBKa",
    "https://sendblue",
    "api.sendblue",
    "sendblue.com",
  ].forEach((blocked) => {
    assert.strictEqual(
      html.toLowerCase().includes(blocked.toLowerCase()),
      false,
      `${page} should not include unsafe Stage 1 marker: ${blocked}`
    );
  });
});

Object.entries(pages).forEach(([page, html]) => {
  assert.doesNotMatch(html, /href=["']sms:/i, `${page} must not expose an SMS CTA`);
  if (page !== "website/index.html") {
    assert.doesNotMatch(html, /href=["']tel:/i, `${page} must not expose the homepage-only live demo CTA`);
  }
});

assert.ok(
  pages["website/index.html"].includes('href="tel:+16292699697"') &&
    pages["website/index.html"].includes('data-tct-destination="live_demo_phone"') &&
    pages["website/index.html"].includes('data-text-channel-unverified="true"'),
  "homepage should expose only the verified live demo while text remains guarded"
);
assert.ok(
  pages["website/pricing.html"].includes("/demo.html?source=pricing#consented-demo-lead") &&
    pages["website/faq.html"].includes("/demo.html?source=faq#consented-demo-lead"),
  "pricing and FAQ should route human follow-up through the consented lead form"
);

cardRoutes.forEach((route) => {
  assert.ok(
    pages["website/pricing.html"].includes(route) && pages["website/index.html"].includes(route),
    `public buyer path should open card checkout directly: ${route}`
  );
});

assert.strictEqual(fs.existsSync(path.join(root, "website/pre-checkout.html")), false, "removed pre-checkout page should stay deleted");

[
  "Secure Square checkout remains pending until signed confirmation",
  "Only Square's validated signed event creates the internal payment and client records.",
  "setup questions",
  "forwarding/testing",
].forEach((marker) => {
  assert.ok(pages["website/pricing.html"].includes(marker), `pricing should explain the pending Square flow: ${marker}`);
});

assert.ok(
  !pages["website/checkout.html"].includes("Payment complete — continue setup") &&
    pages["website/checkout.html"].includes("checkout=select-plan"),
  "legacy checkout must not expose a buyer-controlled payment-complete bypass"
);

assert.ok(
  pages["website/setup.html"].includes("This public setup form is retired.") &&
    pages["website/setup.html"].includes("Nothing was activated by opening this page.") &&
    !pages["website/setup.html"].includes("<form"),
  "legacy setup must be an honest, non-activating compatibility page"
);

assert.ok(
  pages["website/setup-confirmation.html"].includes("This page is not a payment or setup receipt.") &&
    pages["website/setup-confirmation.html"].includes("Only a validated signed Square event") &&
    pages["website/setup-confirmation.html"].includes("Return to plans"),
  "legacy confirmation must not claim payment, setup, or activation"
);

console.log("website Stage 1 proof tests passed");
