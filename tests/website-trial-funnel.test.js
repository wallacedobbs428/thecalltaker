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
];

const publicTrialHtml = publicTrialPages.map(read).join("\n");

assert.strictEqual(
  publicTrialHtml.includes("square.link"),
  false,
  "public trial funnel should not send buyers to the old generic Square link"
);

assert.strictEqual(
  publicTrialHtml.includes("Secure Square"),
  false,
  "public trial funnel copy should not imply the old Square-only checkout path"
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

[
  ["After-Hours Capture", 97, "https://buy.stripe.com/4gM00j7HG816fbO6Y3b3q03"],
  ["Revenue Recovery System", 497, "https://buy.stripe.com/6oU8wP4vu3KQfbObejb3q04"],
  ["Operational Infrastructure", 997, "https://buy.stripe.com/4gM8wPbXWgxCaVy3LRb3q05"],
].forEach(([planName, price, trialLink]) => {
  assert.ok(checkoutHtml.includes(planName), `checkout should display ${planName}`);
  assert.ok(checkoutHtml.includes(`price: ${price}`), `checkout should configure ${planName} at $${price}/mo`);
  assert.ok(checkoutHtml.includes(trialLink), `checkout should configure a distinct trial link for ${planName}`);
});

assert.ok(
  checkoutHtml.includes('href="#plans" class="header-cta"'),
  "checkout header trial CTA should scroll to plan selection before provider checkout"
);

assert.ok(
  checkoutHtml.includes("Selected plan: ") && checkoutHtml.includes("14 days free, then $"),
  "checkout should show selected plan and post-trial monthly billing copy"
);

console.log("website trial funnel regression tests passed");
