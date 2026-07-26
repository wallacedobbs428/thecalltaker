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
for (const plan of ["afterhours", "full247", "custom"]) {
  assert.ok(card.includes(`${plan}: {`), `checkout must define ${plan}`);
}
assert.ok(card.includes("checkout=select-plan"), "an invalid plan must return to pricing");
assert.ok(card.includes("call-taker-os.vercel.app/api/public/square-trial"), "checkout must use the protected Square card-on-file endpoint");
assert.ok(card.includes("consentToStoreCard:true"), "checkout must collect explicit card-storage consent");
assert.ok(card.includes("<button id=\"submit\" type=\"submit\" disabled>"), "checkout must start disabled until required details are complete");

console.log("website checkout continuity tests passed");
