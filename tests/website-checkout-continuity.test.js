const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const pages = ["website/index.html", "website/pricing.html", "website/faq.html", "website/checkout.html", "website/pay.html"];
const cardRoutes = [
  "/card-checkout.html?plan=afterhours",
  "/card-checkout.html?plan=full247",
  "/card-checkout.html?plan=custom",
];
const card = read("website/card-checkout.html");

assert.ok(fs.existsSync(path.join(root, "website/meet-gideon.html")), "Meet Gideon compatibility route must be published");
const meetGideon = read("website/meet-gideon.html");
assert.ok(meetGideon.includes("/demo.html?source=meet-gideon"), "Meet Gideon must route to the existing demo with source context");
assert.ok(!/setup\.html|paid\.html/.test(meetGideon), "Meet Gideon must not imply checkout or payment success");
assert.ok(read(".github/workflows/deploy.yml").includes("meet-gideon.html"), "GitHub Pages artifact must include Meet Gideon");
assert.ok(meetGideon.includes('href="tel:+16292699697"'), "Meet Gideon must expose the live demo line");
assert.ok(meetGideon.includes("correlation_id"), "Meet Gideon must preserve buyer correlation context");
assert.ok(meetGideon.includes("prefers-reduced-motion"), "Meet Gideon must respect reduced-motion preferences");

assert.strictEqual(new Set(cardRoutes).size, 3, "each public plan must use a distinct checkout route");
pages.forEach((page) => {
  const html = read(page);
  assert.strictEqual(/https:\/\/square\.link\/u\//.test(html), false, `${page} must preserve plan selection before Square`);
});
cardRoutes.forEach((link) => {
  assert.ok(read("website/pricing.html").includes(link), `pricing must route directly to ${link}`);
  assert.ok(read("website/checkout.html").includes(link), `checkout must preserve ${link}`);
});
assert.strictEqual(fs.existsSync(path.join(root, "website/pre-checkout.html")), false, "the removed pre-checkout handoff must not be published");
assert.ok(read("website/pay.html").includes(cardRoutes[0]), "legacy $97 pay entrypoint must remain plan-bound");
for (const plan of ["afterhours", "full247", "custom"]) {
  assert.ok(card.includes(`${plan}: {`), `checkout must define ${plan}`);
}
assert.ok(card.includes("checkout=select-plan"), "an invalid plan must return to pricing");
assert.ok(card.includes("call-taker-os.vercel.app/api/public/square-trial"), "checkout must use the protected Square card-on-file endpoint");
assert.ok(card.includes("consentToStoreCard:true"), "checkout must collect explicit card-storage consent");
assert.ok(card.includes("<button id=\"submit\" type=\"submit\" disabled>"), "checkout must start disabled until required details are complete");
assert.ok(card.includes("window.location.replace('/setup.html?plan='"), "successful enrollment must open setup automatically");
assert.ok(card.includes("result.receipt"), "setup redirect must carry Square's receipt binding");

console.log("website checkout continuity tests passed");
