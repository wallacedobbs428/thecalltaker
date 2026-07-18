const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const pricing = read("website/pricing.html");
const sharedScript = read("website/script.js");
const homepage = read("website/index.html");

assert.ok(pricing.includes('aria-controls="pricingMobileNav"'), "pricing menu must identify its mobile navigation");
assert.ok(pricing.includes('id="pricingMobileNav"'), "pricing mobile navigation must have a stable id");
assert.strictEqual(pricing.includes("var menuToggle = document.querySelector('.pricing-page .menu-toggle')"), false, "pricing must not install a second menu click handler");
assert.ok(sharedScript.includes("setMenuOpen(!mobileNav.classList.contains('open'))"), "shared menu must use one deterministic open/close controller");
assert.ok(sharedScript.includes("aria-expanded"), "shared menu must expose expanded state");
assert.ok(sharedScript.includes("event.key === 'Escape'"), "shared menu must close with Escape");

[
  "/assets/images/plan-visuals/after-hours-capture.jpg",
  "/assets/images/plan-visuals/revenue-recovery-system.jpg",
  "/assets/images/plan-visuals/operational-infrastructure.jpg",
].forEach((source) => assert.ok(pricing.includes(source), `pricing must restore ${source}`));
assert.ok(pricing.includes("image.src = plan.image"), "plan selection must update the visible image");
assert.ok(pricing.includes("other.setAttribute('aria-pressed', 'false')"), "plan selector must expose selection state");
assert.ok(pricing.includes("Start Free Trial"), "pricing plan CTAs must say Start Free Trial");
assert.strictEqual(pricing.includes(">Continue to Checkout<"), false, "pricing must not retain stale checkout CTA copy");

assert.ok(homepage.includes('/assets/images/gideon-service-homepage-hero.png'), "homepage must show the approved Gideon visual");
assert.ok(homepage.includes('id="meetGideonTitle"'), "Gideon visual must have a labelled section");
assert.ok(homepage.includes("text-align: center;\n    align-items: center;"), "mobile homepage hero card must be centered");

console.log("website mobile pricing regression tests passed");
