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
  assert.match(meet, /utm_campaign[\s\S]*match\(\/\[0-9\]\/g\)/);
  assert.match(book, /sourceAliases/);
  assert.doesNotMatch(book, /set\('source', 'legacy-book-route'\)/);
});

test("the optional Gideon follow-up is explicit, durable, and never anonymous outreach", () => {
  const demo = read("website/demo.html");
  assert.match(demo, /data-tct-form="consented-lead"/);
  assert.match(demo, /name="follow_up_consent"[^>]*required/);
  assert.match(demo, /name="preferred_contact_method"/);
  assert.match(demo, /name="phone"[^>]*required/);
  assert.match(demo, /Required by the current human follow-up queue, even when email is your preferred contact method/);
  assert.match(demo, /follow_up_consent:data\.get\('follow_up_consent'\) === 'on'/);
  assert.match(demo, /body\.id/);
  assert.doesNotMatch(demo, /body\.request_id/);
  assert.match(demo, /body\.correlation_id !== correlationId/);
  assert.match(demo, /session_id:sessionId/);
  for (const key of ["content_key","source_asset_sha256","source_publication_seed_sha256"]) assert.match(demo, new RegExp(`${key}:`));
  for (const event of ["follow_up_consent_selected_ui","lead_request_submitted_ui","lead_request_accepted_ui","lead_request_error_ui"]) assert.match(demo, new RegExp(event));
  for (const normalizer of ["issuedUtmSource", "issuedUtmChannel", "issuedUtmSlug"]) assert.match(demo, new RegExp(normalizer));
  assert.doesNotMatch(demo, /data-tct-event="lead_form_submitted"/);
  assert.doesNotMatch(read("website/tct-tracking.js"), /^\s*initPopup\(\);/m);
});

test("the direct human-demo CTA reaches one visible intake without building a preview", () => {
  const demo = read("website/demo.html");
  const intake = demo.match(/<section class="human-demo-intake"[^>]*>([\s\S]*?)<\/section>/);
  assert.ok(intake, "the intake has its own visible section, independent of the optional preview");
  assert.match(intake[1], /<form id="consented-demo-lead"/);
  assert.equal((demo.match(/<form id="consented-demo-lead"/g) || []).length, 1);
  assert.doesNotMatch(intake[0], /<(?:section|div|form)\b[^>]*(?:\shidden\b|aria-hidden="true"|class="(?:demo-experience|bottom-cta))/);
  const preview = demo.slice(demo.indexOf('<section class="demo-experience"'), demo.indexOf('<!-- ===== BOTTOM CTA'));
  assert.doesNotMatch(preview, /<form id="consented-demo-lead"/);
  assert.match(demo, /\.demo-experience\s*\{\s*display:\s*none/);
  assert.match(demo, /\.human-demo-intake\s*\{[^}]*display:\s*block/);
  assert.ok(/\.human-demo-intake\s*\{[^}]*--text-1:\s*#18181b;[^}]*color:\s*var\(--text-1\)/.test(demo),
    "the white intake card has scoped readable text, not inherited white page text");
  assert.match(demo, /#consented-demo-lead\s*\{[^}]*scroll-margin-top:\s*\d+px/);
});

test("the visible human-demo intake keeps the canonical identity, consent, and submission binding", () => {
  const demo = read("website/demo.html");
  const form = demo.match(/<form id="consented-demo-lead"[^>]*>[\s\S]*?<\/form>/)[0];
  assert.match(form, /data-tct-form="consented-lead"/);
  assert.match(form, /data-tct-destination="consented_lead_queue"/);
  assert.deepEqual([...form.matchAll(/<(?:input|select)\b[^>]*\bname="([^"]+)"/g)].map((match) => match[1]),
    ["company", "name", "email", "phone", "preferred_contact_method", "follow_up_consent", "website"]);
  assert.match(form, /name="follow_up_consent" type="checkbox" required/);
  assert.equal((demo.match(/getElementById\('consented-demo-lead'\)/g) || []).length, 1);
  assert.equal((demo.match(/https:\/\/call-taker-os\.vercel\.app\/api\/public\/lead/g) || []).length, 1);
  assert.match(demo, /body\.correlation_id !== correlationId/);
});

test("checkout remains correlated and pending until signed provider truth", () => {
  const checkout = read("website/card-checkout.html");
  assert.match(checkout, /status !== 'payment_pending'/);
  assert.match(checkout, /tct_pending_checkout_v1/);
  assert.match(checkout, /state: 'checkout_request_pending'/);
  assert.match(checkout, /idempotencyKey:requestIdentity\.idempotencyKey/);
  assert.doesNotMatch(checkout, /idempotencyKey:crypto\.randomUUID\(\)/);
  assert.match(checkout, /checkout_attempt_id=/);
  assert.match(checkout, /correlation_id=/);
  assert.match(checkout, /sessionId:requestIdentity\.sessionId/);
  for (const key of ["tct_item_id","tct_asset_sha256","tct_publication_seed_sha256"]) assert.match(checkout, new RegExp(key));
  assert.match(checkout, /webPaymentsSdkUrl/);
  assert.match(checkout, /sandbox\\\.web|sandbox\\\./);
  assert.match(checkout, /human-reviewed setup handoff|human will review onboarding/);
  assert.match(checkout, /id="business"[^>]*required/);
  assert.match(checkout, /id="preferred"[^>]*required/);
  assert.match(checkout, /consentToFollowUp:true/);
  assert.match(checkout, /consent to a human from The Call Taker contacting me/);
  assert.doesNotMatch(checkout, /setupToken|receipt|tct_setup_binding|\/setup\.html/);
  assert.match(checkout, /subscription_scheduled_pending_human_review/);
  assert.match(checkout, /intent:'STORE'/);
  assert.match(checkout, /billingPostalCode:billingPostalCode/);
  assert.doesNotMatch(checkout, /payment_confirmed|payment_succeeded/);
  assert.doesNotMatch(checkout, /<script src="https:\/\/web\.squarecdn\.com/);
  assert.match(checkout, /\$997 base\/month/);
  assert.match(checkout, /custom scope above the \$997 base is quoted separately and is not authorized by this checkout/i);
});

test("homepage and other public surfaces keep demo requests consented while live-call proof is unobserved", () => {
  const homepage = read("website/index.html");
  const nonHomepageVoiceSurfaces = deployedVoiceSurfaces
    .filter((page) => page !== "index.html")
    .map((page) => read(`website/${page}`))
    .join("\n");
  assert.doesNotMatch(homepage, /href=["'](?:tel:|sms:)/i);
  assert.match(homepage, /href="\/demo\.html\?source=homepage#consented-demo-lead"/);
  assert.match(homepage, /data-tct-destination="consented_lead_queue"/);
  assert.doesNotMatch(homepage, /data-gideon-demo-unverified/);
  assert.match(homepage, /data-text-channel-unverified="true"/);
  assert.doesNotMatch(nonHomepageVoiceSurfaces, /href=["']tel:\+16292699697/i);
  assert.match(read("website/demo.html"), /consented-demo-lead/);
  assert.match(read("website/meet-gideon.html"), /Request a human demo/);
  assert.match(read("website/meet-gideon.html"), /\/assets\/images\/gideon-service-homepage-hero\.png/);
  assert.doesNotMatch(read("website/meet-gideon.html"), /gideon-service-homepage-hero\.webp/);
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
  assert.doesNotMatch(read("website/demo.html"), /60-second setup/i);
  assert.doesNotMatch(read("website/index.html"), /60-second setup/i);
  assert.match(read("website/demo.html"), /Signed payment &rarr; human review/);
  assert.match(read("website/index.html"), /SIGNED CONFIRMATION &middot; HUMAN REVIEW BEFORE LIVE CALLS/);
});

test("deployed source contains no stale backend alias or Stripe buyer path", () => {
  const deployedText = pages.concat(["script.js","tct-tracking.js","tct-funnel-events.js"]).map((file) => read(`website/${file}`)).join("\n");
  assert.doesNotMatch(deployedText, /https:\/\/thecalltaker\.vercel\.app/);
  assert.doesNotMatch(deployedText, /stripe/i);
});
