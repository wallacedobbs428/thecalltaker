const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const siblingRoot = path.resolve(root, "..", "thecalltaker");
const pages = [
  "website/pre-checkout.html",
  "website/checkout.html",
  "website/pay.html",
  "website/card-checkout.html",
];
const cardRoutes = [
  "/card-checkout.html?plan=afterhours",
  "/card-checkout.html?plan=full247",
  "/card-checkout.html?plan=custom",
];

assert.strictEqual(new Set(cardRoutes).size, 3, "each public plan must use a distinct card checkout route");

pages.forEach((page) => {
  const html = read(page);
  assert.strictEqual(html.includes("window.location.replace"), false, `${page} must not replace the TCT page with Square`);
  assert.strictEqual(/http-equiv=["']refresh["'][^>]+square\.link/i.test(html), false, `${page} must not meta-refresh to Square`);
  assert.strictEqual(/https:\/\/square\.link\/u\//.test(html), false, `${page} must not use the broken hosted free-trial links`);
});

cardRoutes.forEach((link) => {
  assert.ok(read("website/pre-checkout.html").includes(link), `pre-checkout must preserve ${link}`);
  assert.ok(read("website/checkout.html").includes(link), `checkout must preserve ${link}`);
});
assert.ok(read("website/pay.html").includes(cardRoutes[0]), "legacy $97 pay entrypoint must remain plan-bound");
assert.ok(read("website/card-checkout.html").includes("https://web.squarecdn.com/v1/square.js"), "card checkout must load Square's production SDK");
assert.ok(read("website/card-checkout.html").includes("intent:'STORE'"), "card checkout must explicitly tokenize for card storage");
assert.ok(read("website/card-checkout.html").includes("consentToStoreCard"), "card checkout must require stored-card consent");
assert.ok(read("website/card-checkout.html").includes("Accepted credit and debit cards"), "card checkout must identify eligible recurring payment methods");
for (const brand of ["Visa", "Mastercard", "American Express", "Discover", "JCB", "UnionPay"]) {
  assert.ok(read("website/card-checkout.html").includes(`<span>${brand}</span>`), `card checkout must display ${brand}`);
}
assert.ok(read("website/card-checkout.html").includes("enabled for one-time purchases"), "wallet availability must be explained without implying recurring support");
assert.ok(read(".github/workflows/deploy.yml").includes("checkout.html card-checkout.html signup.html"), "Pages artifact must include card checkout");
assert.strictEqual(
  fs.readFileSync(path.join(siblingRoot, "website/checkout.html"), "utf8"),
  read("website/checkout.html"),
  "split marketing-site checkout source must match the deploy source",
);
assert.strictEqual(
  fs.readFileSync(path.join(siblingRoot, "website/pay.html"), "utf8"),
  read("website/pay.html"),
  "split marketing-site pay source must match the deploy source",
);

const authoritativePath = path.join(root, "ctos/product/square-links.json");
const authoritative = JSON.parse(fs.readFileSync(authoritativePath, "utf8"));
assert.ok(authoritative.links.every((row) => row.checkout_redirect_url === "https://thecalltaker.com/setup.html"), "all provider links must return to secure setup");

console.log("website checkout continuity tests passed");
