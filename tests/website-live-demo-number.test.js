"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

test("homepage requests a consented human demo without claiming an observed live caller experience", () => {
  const homepage = read("website/index.html");

  const demoCtas = homepage.match(/<a\b[^>]*href="\/demo\.html\?source=homepage#consented-demo-lead"[^>]*>[\s\S]*?<\/a>/g) || [];
  assert.equal(demoCtas.length, 15, "all existing homepage demo placements keep a usable destination");
  for (const cta of demoCtas) {
    assert.match(cta, /aria-label="Request a human demo"/);
    assert.match(cta, /data-tct-event="homepage_cta_click"/);
    assert.match(cta, /data-tct-destination="consented_lead_queue"/);
    assert.match(cta, /data-tct-learning-tag="human_followup_intent"/);
    assert.match(cta, /Request a human demo/);
  }
  assert.doesNotMatch(homepage, /href=["']tel:|Call (?:the )?(?:live|public) (?:AI |The Call Taker )?demo|live_demo_phone|demo_call_intent|NO SIGNUP NEEDED/i);
  const structured = homepage.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1];
  assert.doesNotMatch(structured, /demo line/i, "structured data must not preserve the removed live-experience claim");
  assert.match(homepage, /data-tct-event="homepage_cta_click"/);
  // Keep receipt support for any independently governed future live-call CTA;
  // this copy correction must not rewrite the canonical event vocabulary.
  const funnelClient = read("website/tct-funnel-events.js");
  assert.match(funnelClient, /destination_type === "live_demo_phone"\) return "cta_intent"/);
  assert.match(funnelClient, /receipt_role: destinationType === "live_demo_phone" \? "live_demo_phone_browser_cta" : ""/);
  assert.match(funnelClient, /receipt_role: payload\.receipt_role \|\| ""/);
  assert.match(funnelClient, /new URL\(doc\.referrer \|\| ""\)\.hostname/);
  assert.match(funnelClient, /referrer_host: payload\.referrer_host \|\| null/);
  assert.doesNotMatch(funnelClient, /referrer_host:\s*doc\.referrer/);
  assert.doesNotMatch(homepage, /data-gideon-demo-unverified/);
  assert.doesNotMatch(homepage, /Live Gideon demo and text-channel verification/);
  assert.match(homepage, /data-text-channel-unverified="true"/);
  assert.doesNotMatch(homepage, /href=["']sms:/i);
  assert.doesNotMatch(homepage, /Text messaging is not available from this site\./);
  assert.doesNotMatch(homepage, /homepage-text-status/);
  assert.doesNotMatch(homepage, /document\.body\.insertBefore\(status/);
  const demo = read("website/demo.html");
  assert.match(demo, /id="consented-demo-lead"/);
  assert.match(demo, /name="follow_up_consent"[^>]*required/);
  assert.match(demo, /body\.correlation_id !== correlationId/);
});
