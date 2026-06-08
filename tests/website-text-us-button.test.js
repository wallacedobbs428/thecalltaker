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
const preCheckoutRoutes = [
  "/pre-checkout.html?plan=afterhours",
  "/pre-checkout.html?plan=full247",
  "/pre-checkout.html?plan=custom",
];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function hrefs(html) {
  return [...html.matchAll(/href="([^"]+)"/g)].map((match) => match[1]);
}

function textUsButtonCount(html) {
  return (html.match(/class="[^"]*\btext-us-button\b/g) || []).length;
}

function sliceBetween(html, startMarker, endMarker) {
  const start = html.indexOf(startMarker);
  assert.ok(start >= 0, `missing start marker: ${startMarker}`);
  const end = html.indexOf(endMarker, start);
  assert.ok(end > start, `missing end marker after ${startMarker}: ${endMarker}`);
  return html.slice(start, end);
}

const pages = {
  "website/index.html": read("website/index.html"),
  "website/pricing.html": read("website/pricing.html"),
  "website/faq.html": read("website/faq.html"),
  "website/setup.html": read("website/setup.html"),
  "website/setup-confirmation.html": read("website/setup-confirmation.html"),
  "website/services.html": read("website/services.html"),
};

assert.ok(
  read("website/text-us.css").includes("#0A93F6") &&
    read("website/text-us.css").includes("#0880D9") &&
    read("website/text-us.css").includes(".text-us-button") &&
    read("website/text-us.css").includes(".text-us-button--support"),
  "Text Us button should use the reusable blue button stylesheet"
);

[
  "website/index.html",
  "website/pricing.html",
  "website/faq.html",
  "website/setup.html",
  "website/setup-confirmation.html",
  "website/services.html",
].forEach((page) => {
  assert.ok(pages[page].includes('href="text-us.css"'), `${page} should load the shared Text Us stylesheet`);
  assert.ok(pages[page].includes("text-us-button"), `${page} should include a Text Us button`);
  assert.ok(pages[page].includes('aria-label="Text The Call Taker"'), `${page} should label the SMS CTA accessibly`);
  assert.ok(hrefs(pages[page]).includes(smsHref), `${page} should use the approved Sendblue SMS destination`);
});

[
  ["website/index.html", 4],
  ["website/pricing.html", 3],
  ["website/faq.html", 3],
  ["website/setup.html", 3],
  ["website/setup-confirmation.html", 1],
].forEach(([page, maxCount]) => {
  assert.ok(
    textUsButtonCount(pages[page]) <= maxCount,
    `${page} should keep Text Us under the target max placement count`
  );
});

assert.ok(
  decodeURIComponent(smsHref).includes("Hi! I would love to learn more about your service"),
  "SMS body should be URL encoded and decode to the approved prospect message"
);

[
  "website/index.html",
  "website/pricing.html",
  "website/faq.html",
  "website/services.html",
].forEach((page) => {
  assert.ok(pages[page].includes(demoTel), `${page} should keep the existing Gideon demo phone CTA`);
});

preCheckoutRoutes.forEach((route) => {
  assert.ok(pages["website/index.html"].includes(route), `homepage should route checkout CTA through pre-checkout: ${route}`);
  assert.ok(pages["website/pricing.html"].includes(route), `pricing should route checkout CTA through pre-checkout: ${route}`);
});

assert.ok(
  pages["website/faq.html"].includes(preCheckoutRoutes[1]),
  "FAQ should route the recommended checkout CTA through pre-checkout"
);

Object.entries(pages).forEach(([page, html]) => {
  [
    "https://sendblue",
    "api.sendblue",
    "sendblue.com",
    "fetch(\"sms:",
    "fetch('sms:",
    "Text Wallace directly",
    "iMessage us",
    "Blue text us",
    "within 2 minutes",
    "AI setup call",
    "AI will call",
    "Our AI will call you",
    "automatic post-payment call",
    "phone-circle",
    "callback-widget",
    "floating-phone",
  ].forEach((blockedMarker) => {
    assert.strictEqual(
      html.toLowerCase().includes(blockedMarker.toLowerCase()),
      false,
      `${page} should not include unsafe Text Us/provider/floating-phone marker: ${blockedMarker}`
    );
  });
});

assert.ok(
  pages["website/pricing.html"].indexOf("Questions before checkout?") >
    pages["website/pricing.html"].indexOf(preCheckoutRoutes[1]),
  "pricing Text Us support should appear after the main plan checkout CTAs, not above them"
);

assert.ok(
  pages["website/pricing.html"].includes("Questions before checkout? Text us") &&
    pages["website/faq.html"].includes("Prefer texting? Send us a quick message") &&
    pages["website/setup.html"].includes("Need help with setup?") &&
    pages["website/setup-confirmation.html"].includes("Need to update something? Text us."),
  "support pages should use approved Text Us support copy"
);

assert.strictEqual(
  sliceBetween(
    pages["website/index.html"],
    "<!-- ═══ SECTION 9: FINAL CTA",
    "<!-- ═══ FOOTER"
  ).includes("text-us-button"),
  false,
  "homepage final CTA should stay focused on See Plans and Call Gideon Live"
);

assert.strictEqual(
  sliceBetween(
    pages["website/index.html"],
    '<section id="faq"',
    "<!-- ═══ REVIEWED SETUP CTA"
  ).includes("text-us-button"),
  false,
  "homepage FAQ preview should not duplicate Text Us close to the footer"
);

assert.strictEqual(
  sliceBetween(
    pages["website/pricing.html"],
    "<!-- FINAL CTA -->",
    "<!-- FOOTER -->"
  ).includes("text-us-button"),
  false,
  "pricing final CTA should not let Text Us compete with Choose Plan and Call Gideon Live"
);

assert.strictEqual(
  sliceBetween(
    pages["website/setup.html"],
    '<form class="setup-form"',
    "</form>"
  ).includes("text-us-button"),
  false,
  "setup form itself should keep Submit setup packet as the only form CTA"
);

const homepageHeroCta = pages["website/index.html"].slice(
  pages["website/index.html"].indexOf('<div class="gideon-cta"'),
  pages["website/index.html"].indexOf("</div>", pages["website/index.html"].indexOf('<div class="gideon-cta"'))
);
assert.ok(
  homepageHeroCta.indexOf("See Plans &amp; Setup Options") >= 0 &&
    homepageHeroCta.indexOf("Call Gideon Live") > homepageHeroCta.indexOf("See Plans &amp; Setup Options") &&
    homepageHeroCta.indexOf("Text Us") > homepageHeroCta.indexOf("Call Gideon Live") &&
    homepageHeroCta.includes("text-us-button--support"),
  "homepage hero CTA order should remain See Plans, Call Gideon Live, then support Text Us"
);

assert.strictEqual(
  pages["website/index.html"].includes(".gideon-hero.service-selling .btn-gideon-ghost {\n    display: none;"),
  false,
  "mobile homepage hero should not hide Call Gideon Live when Text Us is added"
);

assert.ok(
  pages["website/setup.html"].includes("Submit setup packet") &&
    pages["website/setup.html"].includes("class=\"setup-submit-row\""),
  "setup form submit CTA should remain primary"
);

assert.ok(
  read("website/text-us.css").includes("max-width: calc(100vw - 36px)") &&
    read("website/text-us.css").includes(".mobile-nav .text-us-button"),
  "Text Us support controls should keep mobile width constrained"
);

console.log("website Text Us button tests passed");
