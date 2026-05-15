import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { buildSocialHandoff, SOCIAL_HANDOFF_NO_POST_MODE } from "../tools/creative/generate_social_handoff.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const sample = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/creative/creative_assets.sample.json"), "utf8"));

test("social handoff stays no-post", () => {
  assert.equal(SOCIAL_HANDOFF_NO_POST_MODE, true);
});

test("builds platform-specific candidates from organic-ready assets", () => {
  const handoff = buildSocialHandoff(sample.assets);

  assert.equal(handoff.no_post_mode, true);
  assert.ok(handoff.candidates.length >= 4);
  assert.ok(handoff.candidates.some((item) => item.platform === "facebook"));
  assert.ok(handoff.candidates.some((item) => item.platform === "instagram"));
  assert.ok(!handoff.candidates.some((item) => item.asset_id === "paid-live-routing-unsafe-example"));
});

test("posting is blocked by default for every candidate", () => {
  const handoff = buildSocialHandoff(sample.assets);

  assert.equal(handoff.blocked_policy.auto_publish_allowed, false);
  assert.equal(handoff.blocked_policy.paid_spend_allowed, false);
  assert.ok(handoff.candidates.every((item) => item.post_allowed === false));
  assert.ok(handoff.candidates.every((item) => item.required_manual_checks.length >= 4));
});

test("candidate captions preserve truth boundaries", () => {
  const handoff = buildSocialHandoff(sample.assets);
  const combined = handoff.candidates.map((item) => item.caption).join("\n");

  assert.match(combined, /Nothing goes live without reviewed setup/);
  assert.doesNotMatch(combined, /guaranteed booked jobs/i);
  assert.doesNotMatch(combined, /provider routing is active/i);
  assert.doesNotMatch(combined, /Your AI is live/i);
});
