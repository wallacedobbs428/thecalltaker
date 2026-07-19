const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const buyerPages = [
  "website/index.html",
  "website/pricing.html",
  "website/demo.html",
  "website/faq.html",
  "website/start.html",
  "website/signup.html",
  "website/pre-checkout.html",
  "website/checkout.html",
  "website/pay.html",
];

const home = read("website/index.html");
assert.ok(home.includes("--gideon-card-bg: #fff"), "light mode must give Meet Gideon a light card");
assert.ok(home.includes("background: var(--gideon-card-bg)"), "Meet Gideon card must use its theme token");
assert.ok(home.includes("color: var(--gideon-copy)"), "Meet Gideon copy must use its theme token");
for (const unsupportedClaim of [
  "TEAM ALERT SENT",
  "&lt; 2s",
  "Let me get an emergency tech out to you",
  "Any phone system",
  "$2,800",
]) {
  assert.strictEqual(home.includes(unsupportedClaim), false, `homepage must not publish unsupported claim: ${unsupportedClaim}`);
}

for (const page of buyerPages) {
  const html = read(page);
  assert.strictEqual(html.includes('href="/setup.html'), false, `${page} must not expose unsigned setup`);
  assert.strictEqual(html.includes("Payment complete — continue setup"), false, `${page} must not expose a buyer-controlled payment bypass`);
}

for (const route of ["website/pre-checkout.html", "website/checkout.html", "website/card-checkout.html"]) {
  const html = read(route);
  assert.strictEqual(/params\.get\(['"]plan['"]\)\s*\|\|\s*['"]full247['"]/.test(html), false, `${route} must not silently default to $497`);
  assert.ok(html.includes("checkout=select-plan"), `${route} must send a missing or invalid plan back to pricing`);
}

const card = read("website/card-checkout.html");
assert.ok(card.includes("enrollmentConfirmed=true"), "checkout must distinguish confirmed enrollment from pre-enrollment failure");
assert.ok(card.includes("Do not submit again"), "confirmed enrollment handoff failure must prevent duplicate enrollment");
assert.ok(card.includes("button.disabled=true"), "confirmed enrollment handoff failure must leave submit disabled");
assert.ok(card.includes("result.setupToken"), "checkout must require a signed setup token");

const setup = read("website/setup.html");
const setupScript = read("website/setup-form.js");
assert.ok(setup.includes('type="hidden" id="plan_purchased"'), "setup plan must be locked, not buyer-selectable");
assert.strictEqual(setup.includes('<select id="plan_purchased"'), false, "setup must not allow plan substitution");
assert.ok(setupScript.includes("setup_binding_token"), "setup payload must carry the signed binding token");
assert.ok(setupScript.includes("https://call-taker-os.vercel.app/api/public/setup-intake"), "setup must use the protected intake endpoint");
assert.ok(setupScript.includes('if (!intake.ok) throw new Error'), "setup must not confirm an intake the backend did not accept");
assert.ok(setupScript.includes("Do not start another checkout"), "setup intake failure must prevent a duplicate checkout attempt");
assert.ok(setupScript.includes('removeItem("tct_setup_binding")'), "accepted setup must clear its browser-stored binding token");

const legal = `${read("website/terms.html")}\n${read("website/privacy.html")}`;
for (const contradiction of [
  "GoHighLevel",
  "do not currently use cookies",
  "99.9%",
  "fully live within 48",
  "full refund",
]) {
  assert.strictEqual(legal.toLowerCase().includes(contradiction.toLowerCase()), false, `legal copy must not contain stale claim: ${contradiction}`);
}

const faq = read("website/faq.html");
assert.ok(faq.includes("@media(max-width:380px)"), "FAQ footer must collapse at narrow-mobile width");
assert.ok(faq.includes("overflow-wrap: anywhere"), "FAQ contact links must not force horizontal overflow");

const workflow = read(".github/workflows/deploy.yml");
assert.ok(workflow.includes('website/pilot/index.html'), "Pages artifact must include the retired pilot redirect");

console.log("website release candidate v1 tests passed");
