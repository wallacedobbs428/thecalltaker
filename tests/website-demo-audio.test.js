"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const demo = fs.readFileSync(path.join(root, "website/demo.html"), "utf8");
const eventClient = fs.readFileSync(path.join(root, "website/tct-funnel-events.js"), "utf8");
const audio = path.join(root, "website/assets/demo/demo-call-15s.mp3");

assert.match(demo, /id="gideon-browser-audio"/);
assert.match(demo, /<source src="assets\/demo\/demo-call-15s\.mp3" type="audio\/mpeg">/);
assert.match(demo, /controls preload="metadata"/);
assert.match(demo, /record\('demo_preview_intent', submit\)/);
assert.match(demo, /record\('demo_preview_rendered_ui', submit\)/);
assert.match(demo, /record\('cta_intent', audioSample\)/);
assert.match(demo, /data-tct-cta="listen_recorded_ai_sample"/);
assert.match(demo, /recorded_ai_sample_played/);
assert.match(demo, /recorded_ai_sample_completed/);
assert.match(demo, /recorded_ai_sample_load_error/);
assert.match(demo, /This is a recorded sample, not a live call\./);
assert.doesNotMatch(demo, /href=["'](?:tel:|sms:)/i);
assert.match(eventClient, /cta_intent: true/);
assert.ok(fs.statSync(audio).size > 10_000, "the deployed audio asset is non-empty");

console.log("website demo audio contract passed");
