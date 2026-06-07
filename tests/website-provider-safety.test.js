const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

const tryLiveHtml = read("website/try-live.html");
const tryRedirectHtml = read("website/try.html");
const sitemapXml = read("website/sitemap.xml");

[
  "Live demo calling is temporarily disabled",
  "No call, SMS, email, or provider action will be triggered from this page",
  "No automated provider call from this page",
  'meta name="robots" content="noindex, nofollow"',
].forEach((expected) => {
  assert.ok(tryLiveHtml.includes(expected), `try-live page should show the paused safety state: ${expected}`);
});

[
  "api.bland.ai",
  "Authorization",
  "org_",
  "Call Me Now",
  "Calling you now",
  "Pick up your phone",
  "We call you",
  "under 30 seconds",
  "demo_call_initiated",
  "demo_call_success",
  "demo_call_error",
  "fetch(",
  "googletagmanager.com",
  'src="script.js"',
  "tct-tracking.js",
  "connect.facebook.net",
  "tracking.thecalltaker.com",
  "fbq(",
  "cbq(",
].forEach((blockedMarker) => {
  assert.strictEqual(
    tryLiveHtml.includes(blockedMarker),
    false,
    `try-live page must not contain live provider trigger marker: ${blockedMarker}`
  );
});

assert.ok(
  tryRedirectHtml.includes('meta name="robots" content="noindex, nofollow"') &&
    tryRedirectHtml.includes("/try-live.html"),
  "try helper should be noindex and redirect to the safety-gated try-live page"
);

assert.strictEqual(
  sitemapXml.includes("https://thecalltaker.com/try-live.html"),
  false,
  "sitemap should not advertise the paused try-live call flow"
);

console.log("website provider safety tests passed");
