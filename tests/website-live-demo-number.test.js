"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

test("homepage exposes the public live-call CTA without allowing a text channel", () => {
  const homepage = read("website/index.html");

  assert.match(homepage, /href=["']tel:\+16292699697/i);
  assert.match(homepage, /Call the live demo/);
  assert.match(homepage, /data-tct-event="homepage_cta_click"/);
  assert.match(homepage, /data-tct-destination="live_demo_phone"/);
  assert.match(homepage, /data-tct-learning-tag="demo_call_intent"/);
  const funnelClient = read("website/tct-funnel-events.js");
  assert.match(funnelClient, /destination_type === "live_demo_phone"\) return "demo_live_phone_cta_intent"/);
  assert.match(funnelClient, /receipt_role: destinationType === "live_demo_phone" \? "live_demo_phone_browser_cta" : ""/);
  assert.match(funnelClient, /receipt_role: payload\.receipt_role \|\| ""/);
  assert.match(funnelClient, /new URL\(doc\.referrer \|\| ""\)\.hostname/);
  assert.match(funnelClient, /referrer_host: payload\.referrer_host \|\| null/);
  assert.doesNotMatch(funnelClient, /referrer_host:\s*doc\.referrer/);
  assert.doesNotMatch(homepage, /data-gideon-demo-unverified/);
  assert.doesNotMatch(homepage, /Live Gideon demo and text-channel verification/);
  assert.match(homepage, /data-text-channel-unverified="true"/);
  assert.doesNotMatch(homepage, /href=["']sms:/i);
});
