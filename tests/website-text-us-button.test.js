const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

const publicPages = {
  home: read("website/index.html"),
  pricing: read("website/pricing.html"),
  faq: read("website/faq.html"),
  setup: read("website/setup.html"),
  confirmation: read("website/setup-confirmation.html"),
};

const combined = Object.values(publicPages).join("\n");
const checkoutRoutes = [
  "/card-checkout.html?plan=afterhours",
  "/card-checkout.html?plan=full247",
  "/card-checkout.html?plan=custom",
];

// SMS remains off. The verified public demo number is intentionally homepage-only;
// anonymous callers remain separate from consented human follow-up.
assert.doesNotMatch(combined, /href=["']sms:/i);
assert.doesNotMatch(combined, /api\.sendblue|sendblue\.com/i);
const nonHomepage = [publicPages.pricing, publicPages.faq, publicPages.setup, publicPages.confirmation].join("\n");
assert.doesNotMatch(nonHomepage, /href=["']tel:/i);
assert.match(publicPages.home, /href=["']tel:\+16292699697/i);
assert.match(publicPages.home, /data-tct-destination="live_demo_phone"/);

[publicPages.pricing, publicPages.faq].forEach((html) => {
  assert.match(html, /href="\/demo\.html\?source=[^"]+#consented-demo-lead"/);
  assert.match(html, /aria-label="Request human follow-up"/);
  assert.match(html, /data-destination="consented_lead_queue"/);
});

assert.doesNotMatch(publicPages.home, /data-gideon-demo-unverified="true"/);
assert.match(publicPages.home, /Call the live demo/);
assert.match(publicPages.home, /data-text-channel-unverified="true"/);
assert.doesNotMatch(publicPages.home, /Text messaging is not available from this site\./);

checkoutRoutes.forEach((route) => {
  assert.ok(publicPages.home.includes(route), `homepage should preserve ${route}`);
  assert.ok(publicPages.pricing.includes(route), `pricing should preserve ${route}`);
});
assert.ok(publicPages.faq.includes(checkoutRoutes[1]));

assert.match(publicPages.setup, /public setup form is retired/i);
assert.match(publicPages.setup, /Nothing was activated by opening this page/);
assert.match(publicPages.confirmation, /not a payment or setup receipt/i);
assert.match(publicPages.setup, /retired-setup#consented-demo-lead/);
assert.match(publicPages.confirmation, /retired-confirmation#consented-demo-lead/);
assert.doesNotMatch(combined, /setupToken|tct_setup_binding|trial=started|receipt=/);

[
  "automatic post-payment call",
  "AI setup call within 2 minutes",
  "setup opens automatically",
  "confirmed checkout opens setup automatically",
].forEach((claim) => {
  assert.equal(combined.toLowerCase().includes(claim.toLowerCase()), false, `unsafe claim remains: ${claim}`);
});

console.log("website consented support CTA tests passed");
