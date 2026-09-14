const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const pricing = read("website/pricing.html");
const sharedScript = read("website/site-menu.js");
const homepage = read("website/index.html");

assert.ok(pricing.includes('<details id="tctSiteMenu">'), "pricing menu must use the shared native disclosure");
assert.ok(pricing.includes('aria-label="Main navigation"'), "pricing navigation must have an accessible name");
assert.strictEqual(pricing.includes("var menuToggle = document.querySelector('.pricing-page .menu-toggle')"), false, "pricing must not install a second menu click handler");
assert.ok(sharedScript.includes("menu.open = false"), "shared menu must close the native disclosure deterministically");
assert.ok(pricing.includes('<summary aria-label="Menu">'), "native summary must expose its accessible disclosure state");
assert.ok(sharedScript.includes("event.key === 'Escape'"), "shared menu must close with Escape");

[
  "/assets/images/plan-visuals/after-hours-capture-v3.webp",
  "/assets/images/plan-visuals/247-call-coverage-v3.webp",
  "/assets/images/plan-visuals/custom-call-coverage-v3.webp",
].forEach((source) => assert.ok(pricing.includes(source), `pricing must restore ${source}`));
assert.ok(pricing.includes("image.src = plan.image"), "plan selection must update the visible image");
assert.ok(pricing.includes("other.setAttribute('aria-pressed', 'false')"), "plan selector must expose selection state");
assert.ok(pricing.includes("Start Free Trial"), "pricing plan CTAs must say Start Free Trial");
assert.strictEqual(pricing.includes(">Continue to Checkout<"), false, "pricing must not retain stale checkout CTA copy");

assert.ok(homepage.includes('/assets/images/gideon-service-homepage-hero.png'), "homepage must show the approved Gideon visual");
assert.ok(homepage.includes('aria-labelledby="callSculptureCaption"'), "Gideon visual must have a labelled figure");
assert.ok(homepage.includes("text-align: center;\n    align-items: center;"), "mobile homepage hero card must be centered");

console.log("website mobile pricing regression tests passed");
