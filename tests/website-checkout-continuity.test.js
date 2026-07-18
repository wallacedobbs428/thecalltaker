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
];
const squareLinks = [
  "https://square.link/u/2Rsp3ELj",
  "https://square.link/u/27lLm9JP",
  "https://square.link/u/BfQxAAG4",
];

assert.strictEqual(new Set(squareLinks).size, 3, "each public plan must use a distinct Square checkout");
assert.notStrictEqual(squareLinks[0], squareLinks[1], "$97 must never collapse into the $497 checkout");
assert.notStrictEqual(squareLinks[2], squareLinks[1], "$997+ must never collapse into the $497 checkout");

pages.forEach((page) => {
  const html = read(page);
  assert.strictEqual(html.includes("window.location.replace"), false, `${page} must not replace the TCT page with Square`);
  assert.strictEqual(/http-equiv=["']refresh["'][^>]+square\.link/i.test(html), false, `${page} must not meta-refresh to Square`);
  assert.ok(html.includes('target="_blank"'), `${page} must open Square separately`);
  assert.ok(html.includes('rel="noopener"'), `${page} must isolate the Square tab`);
  assert.ok(html.includes("Payment complete — continue setup"), `${page} must preserve the visible setup continuation`);
  assert.ok(html.includes("does not verify or claim payment"), `${page} must not infer payment from the buyer click`);
  assert.ok(html.includes('params.get("orderId")'), `${page} must carry a returned orderId when present`);
  assert.ok(html.includes("setupUrl.searchParams.set(\"plan\""), `${page} must bind setup to the selected plan`);
});

squareLinks.forEach((link) => {
  assert.ok(read("website/pre-checkout.html").includes(link), `pre-checkout must preserve ${link}`);
  assert.ok(read("website/checkout.html").includes(link), `checkout must preserve ${link}`);
});
assert.ok(read("website/pay.html").includes(squareLinks[0]), "legacy $97 pay entrypoint must preserve its Square link");
assert.strictEqual(read("website/pay.html").includes(squareLinks[1]), false, "legacy $97 pay entrypoint must remain plan-bound");
assert.strictEqual(read("website/pay.html").includes(squareLinks[2]), false, "legacy $97 pay entrypoint must remain plan-bound");
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
assert.deepStrictEqual(authoritative.links.map((row) => row.url), squareLinks, "source links must match the provider-verified Square URLs exactly");

console.log("website checkout continuity tests passed");
