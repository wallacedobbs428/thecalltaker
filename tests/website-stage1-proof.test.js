const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const smsHref = "sms:+17073208712?body=Hi!%20I%20would%20love%20to%20learn%20more%20about%20your%20service";
const demoTel = "tel:+16292699697";
const squareLinks = [
  "https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/HywRLQ4aYHQ0ojpIbsnBPnrelqAZY",
  "https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/RFxESyTjwZQuIS2xceV8983Pvj8YY",
  "https://checkout.square.site/merchant/MLETJ9R4Z5KQ1/order/PCGvURHQSoL8LnXbmQ3olB0imFBZY",
];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

const pages = {
  "website/index.html": read("website/index.html"),
  "website/pricing.html": read("website/pricing.html"),
  "website/paid.html": read("website/paid.html"),
  "website/pre-checkout.html": read("website/pre-checkout.html"),
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
  "Gideon answers calls, collects caller details, and sends clean summaries after your setup is reviewed.",
  "summary_large_image",
  "https://thecalltaker.com/og-image.png",
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
  "Setup reviewed",
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

[
  "website/index.html",
  "website/pricing.html",
  "website/faq.html",
].forEach((page) => {
  assert.ok(pages[page].includes(demoTel), `${page} should label Call Gideon Live with the demo number`);
  assert.ok(pages[page].includes("Call Gideon"), `${page} should keep the demo CTA label clear`);
});

[
  "website/index.html",
  "website/pricing.html",
  "website/faq.html",
  "website/setup.html",
  "website/setup-confirmation.html",
].forEach((page) => {
  assert.ok(pages[page].includes(smsHref), `${page} should use the approved SMS Text Us number`);
  assert.strictEqual(pages[page].includes("tel:+17073208712"), false, `${page} should not call the Text Us number`);
  assert.strictEqual(pages[page].includes("sms:+16292699697"), false, `${page} should not text the Gideon demo number`);
});

squareLinks.forEach((link) => {
  assert.ok(pages["website/pre-checkout.html"].includes(link), `pre-checkout should keep current Square link: ${link}`);
  assert.strictEqual(pages["website/pricing.html"].includes(link), false, `pricing should route to pre-checkout before Square: ${link}`);
  assert.strictEqual(pages["website/paid.html"].includes(link), false, `paid landing should route to pre-checkout before Square: ${link}`);
  assert.strictEqual(pages["website/index.html"].includes(link), false, `homepage should route to pre-checkout before Square: ${link}`);
});

[
  "/pre-checkout.html?plan=afterhours",
  "/pre-checkout.html?plan=full247",
  "/pre-checkout.html?plan=custom",
].forEach((route) => {
  assert.ok(
    pages["website/pricing.html"].includes(route) || pages["website/index.html"].includes(route),
    `public buyer path should include pre-checkout route: ${route}`
  );
});

[
  "You’re almost set up",
  "After checkout, you’ll be directed or guided to answer a few setup questions",
  "Continue to secure checkout",
  "No setup starts until we have your business details",
].forEach((marker) => {
  assert.ok(pages["website/pre-checkout.html"].includes(marker), `pre-checkout should include trust marker: ${marker}`);
});

[
  "After checkout, complete your setup form at thecalltaker.com/setup.html",
  "If Square does not automatically send you back",
  "setup packet",
  "forwarding/testing",
].forEach((marker) => {
  assert.ok(pages["website/pricing.html"].includes(marker), `pricing should explain the Square fallback: ${marker}`);
});

assert.ok(
  pages["website/checkout.html"].includes("After checkout, complete your setup form at") &&
    pages["website/pay.html"].includes("After checkout, complete your setup form at"),
  "checkout fallback pages should send buyers to setup after Square"
);

[
  "Setup progress",
  "Already checked out?",
  "Before we review your setup",
  "Mobile number to text your setup/forwarding guide",
  "Submit setup packet",
].forEach((marker) => {
  assert.ok(pages["website/setup.html"].includes(marker), `setup should include proof marker: ${marker}`);
});

[
  "Your setup packet is now in review",
  "We received your setup details. Next, we'll text the phone number you provided with a setup guide for forwarding your calls and testing your AI answering system.",
  "Return Home",
  "View Pricing",
  "Review FAQ",
].forEach((marker) => {
  assert.ok(pages["website/setup-confirmation.html"].includes(marker), `confirmation should include proof marker: ${marker}`);
});

console.log("website Stage 1 proof tests passed");
