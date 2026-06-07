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
  "The Call Taker - AI receptionist setup for service businesses",
  "Missed-call capture, clean summaries, and a setup packet reviewed before launch.",
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
  assert.ok(pages["website/pricing.html"].includes(link), `pricing should keep current Square link: ${link}`);
  assert.ok(pages["website/index.html"].includes(link), `homepage should keep current Square link: ${link}`);
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
  "Submit setup packet",
].forEach((marker) => {
  assert.ok(pages["website/setup.html"].includes(marker), `setup should include proof marker: ${marker}`);
});

[
  "Your setup packet is now in review",
  "Return Home",
  "View Pricing",
  "Review FAQ",
].forEach((marker) => {
  assert.ok(pages["website/setup-confirmation.html"].includes(marker), `confirmation should include proof marker: ${marker}`);
});

console.log("website Stage 1 proof tests passed");
