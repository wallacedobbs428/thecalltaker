const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const pages = ["website/pre-checkout.html", "website/checkout.html", "website/pay.html"];
const cardRoutes = [
  "/card-checkout.html?plan=afterhours",
  "/card-checkout.html?plan=full247",
  "/card-checkout.html?plan=custom",
];
const card = read("website/card-checkout.html");
const expectedLinks = {
  afterhours: "https://square.link/u/nAgP58ki",
  full247: "https://square.link/u/EslC0nAq",
  custom: "https://square.link/u/J9Fpp46N",
};

assert.strictEqual(new Set(cardRoutes).size, 3, "each public plan must use a distinct checkout route");
pages.forEach((page) => {
  const html = read(page);
  assert.strictEqual(/https:\/\/square\.link\/u\//.test(html), false, `${page} must preserve plan selection before Square`);
});
cardRoutes.forEach((link) => {
  assert.ok(read("website/pre-checkout.html").includes(link), `pre-checkout must preserve ${link}`);
  assert.ok(read("website/checkout.html").includes(link), `checkout must preserve ${link}`);
});
assert.ok(read("website/pay.html").includes(cardRoutes[0]), "legacy $97 pay entrypoint must remain plan-bound");
for (const [plan, url] of Object.entries(expectedLinks)) {
  assert.ok(card.includes(`${plan}: {`), `checkout must define ${plan}`);
  assert.ok(card.includes(url), `checkout must use the verified ${plan} Square link`);
}
assert.ok(card.includes("window.location.assign(plan.url)"), "a valid selected plan must hand off to Square");
assert.ok(card.includes("checkout=select-plan"), "an invalid plan must return to pricing");
assert.strictEqual(card.includes("call-taker-os.vercel.app/api/public/square-trial"), false, "retired custom card capture must not remain public");
assert.strictEqual(card.includes("intent:'STORE'"), false, "retired card-storage flow must not remain public");

console.log("website checkout continuity tests passed");
