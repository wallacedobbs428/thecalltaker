"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const pages = ["index.html","meet-gideon.html","demo.html","pricing.html","paid.html","pay.html","checkout.html","card-checkout.html","book.html","setup.html","setup-confirmation.html","confirmation.html","faq.html"];
const deployedVoiceSurfaces = pages.concat(["404.html","ai-receptionist/index.html","after-hours-answering-service/index.html","demo/carolina-locksmith/index.html","demos/houston-hvac.html"]);

test("the Pages artifact contains the repaired routes and is gated by this regression", () => {
  const workflow = read(".github/workflows/deploy.yml");
  assert.match(workflow, /Verify buyer and consent funnel contract/);
  for (const page of pages) {
    assert.ok(fs.existsSync(path.join(root, "website", page)), `${page} exists`);
    assert.match(workflow, new RegExp(`(?:^|\\s)${page.replace(".", "\\.")}(?:\\s|$)`), `${page} is allowlisted`);
  }
  assert.doesNotMatch(workflow, /setup-form\.js/);
  assert.doesNotMatch(workflow, /tct-first-party-attribution\.js/);
});

test("all deployed buyer pages use one durable, PII-free browser event client", () => {
  const client = read("website/tct-funnel-events.js");
  assert.match(client, /call-taker-os\.vercel\.app\/api\/public\/buyer-event/);
  assert.match(client, /method:\s*"POST"/);
  assert.match(client, /session_sha256|session_id/);
  assert.match(client, /correlation_id/);
  assert.match(client, /utm_content/);
  assert.match(client, /utm_term/);
  for (const marker of ["email_address","phone_number","business_name","owner_name","FormData","document.cookie","localStorage"]) {
    assert.equal(client.includes(marker), false, `event client excludes ${marker}`);
  }
  assert.equal(read("website/index.html").includes("tct-first-party-attribution.js"), false);
});

test("Meet Gideon and the legacy booking path keep only public attribution", () => {
  const meet = read("website/meet-gideon.html");
  const book = read("website/book.html");
  assert.match(book, /\/demo\.html/);
  assert.match(book, /consented-demo-lead/);
  assert.doesNotMatch(meet, /lead_id|"session_id"/);
  for (const key of ["source","utm_source","utm_medium","utm_campaign","utm_content","utm_term","correlation_id","tct_item_id","tct_asset_sha256","tct_publication_seed_sha256"]) {
    assert.ok(meet.includes(`"${key}"`) || book.includes(`'${key}'`), `public attribution includes ${key}`);
  }
});

test("the optional Gideon follow-up is explicit, durable, and never anonymous outreach", () => {
  const demo = read("website/demo.html");
  assert.match(demo, /data-tct-form="consented-lead"/);
  assert.match(demo, /name="follow_up_consent"[^>]*required/);
  assert.match(demo, /name="preferred_contact_method"/);
  assert.match(demo, /name="phone"[^>]*required/);
  assert.match(demo, /follow_up_consent:data\.get\('follow_up_consent'\) === 'on'/);
  assert.doesNotMatch(demo, /body\.id/);
  assert.match(demo, /body\.request_id/);
  assert.match(demo, /body\.correlation_id !== correlationId/);
  assert.match(demo, /session_id:sessionId/);
  for (const key of ["content_key","source_asset_sha256","source_publication_seed_sha256"]) assert.match(demo, new RegExp(`${key}:`));
  for (const event of ["follow_up_consent_selected_ui","lead_request_submitted_ui","lead_request_accepted_ui","lead_request_error_ui"]) assert.match(demo, new RegExp(event));
  assert.doesNotMatch(demo, /data-tct-event="lead_form_submitted"/);
  assert.doesNotMatch(read("website/tct-tracking.js"), /^\s*initPopup\(\);/m);
});

test("checkout remains correlated and pending until signed provider truth", () => {
  const checkout = read("website/card-checkout.html");
  assert.match(checkout, /status !== 'payment_pending'/);
  assert.match(checkout, /tct_pending_checkout_v1/);
  assert.match(checkout, /checkout_attempt_id=/);
  assert.match(checkout, /correlation_id=/);
  assert.match(checkout, /sessionId:sessionId/);
  for (const key of ["tct_item_id","tct_asset_sha256","tct_publication_seed_sha256"]) assert.match(checkout, new RegExp(key));
  assert.match(checkout, /webPaymentsSdkUrl/);
  assert.match(checkout, /sandbox\\\.web|sandbox\\\./);
  assert.match(checkout, /human-reviewed setup handoff|human will review onboarding/);
  assert.doesNotMatch(checkout, /setupToken|receipt|tct_setup_binding|\/setup\.html/);
  assert.match(checkout, /trial_active_pending_human_review/);
  assert.doesNotMatch(checkout, /payment_confirmed|payment_succeeded/);
  assert.doesNotMatch(checkout, /<script src="https:\/\/web\.squarecdn\.com/);
});

test("unverified Gideon voice paths fail closed and still offer a consented next step", () => {
  const combined = deployedVoiceSurfaces.map((page) => read(`website/${page}`)).join("\n");
  assert.doesNotMatch(combined, /href=["']tel:\+16292699697/i);
  assert.doesNotMatch(combined, />\s*Call Gideon Live\s*</i);
  assert.match(read("website/demo.html"), /consented-demo-lead/);
  assert.match(read("website/index.html"), /Build the preview or request a human demo/);
  assert.match(read("website/meet-gideon.html"), /Request a human demo/);
});

test("the Pages build does not secretly rewrite the canonical booking route", () => {
  const workflow = read(".github/workflows/deploy.yml");
  assert.doesNotMatch(workflow, /perl -0pi/);
  assert.match(read("website/book.html"), /legacy-book-route/);
});

test("plan CTAs map exactly and no legacy setup page can activate a buyer", () => {
  const combined = pages.map((page) => read(`website/${page}`)).join("\n");
  const pricing = read("website/pricing.html");
  assert.match(pricing, /card-checkout\.html\?plan=afterhours/);
  assert.match(pricing, /card-checkout\.html\?plan=full247/);
  assert.match(pricing, /card-checkout\.html\?plan=custom/);
  assert.match(combined, /\$97/);
  assert.match(combined, /\$497/);
  assert.match(combined, /\$997/);
  assert.doesNotMatch(combined, /setupToken|tct_setup_binding|trial=started|receipt=/);
  assert.doesNotMatch(combined, /setup opens automatically|confirmed checkout opens setup automatically/i);
  assert.match(read("website/setup.html"), /Nothing was activated by opening this page/);
  assert.match(read("website/setup-confirmation.html"), /not a payment or setup receipt/);
  assert.equal(read("website/setup.html").includes("<form"), false);
});

test("deployed source contains no stale backend alias or Stripe buyer path", () => {
  const deployedText = pages.concat(["script.js","tct-tracking.js","tct-funnel-events.js"]).map((file) => read(`website/${file}`)).join("\n");
  assert.doesNotMatch(deployedText, /https:\/\/thecalltaker\.vercel\.app/);
  assert.doesNotMatch(deployedText, /stripe/i);
});
