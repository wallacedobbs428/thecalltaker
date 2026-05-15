import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { DAILY_RUNNER_NO_SEND_MODE, runDailyCommandCenter } from "../tools/command-center/run_daily.mjs";

test("daily runner stays no-send/no-post", () => {
  assert.equal(DAILY_RUNNER_NO_SEND_MODE, true);
});

test("daily runner regenerates all operating outputs", () => {
  const result = runDailyCommandCenter();

  assert.equal(result.no_send_mode, true);
  assert.ok(result.summary.prospects_scored > 0);
  assert.equal(result.summary.sms_status, "blocked");
  assert.equal(result.summary.sms_cold_gate, "blocked_provider_approval_required");
  assert.ok(result.summary.organic_ready > 0);
  assert.ok(result.summary.posts_ready_for_manual_review > 0);
  assert.ok(result.summary.social_agent_candidates > 0);
  assert.ok(result.summary.social_approved_candidates > 0);
  assert.equal(result.summary.social_calendar_posts, 7);
  assert.equal(result.summary.social_post_ready, 0);
  assert.ok(result.summary.social_post_blocked > 0);
  Object.values(result.outputs).forEach((filePath) => {
    assert.ok(fs.existsSync(filePath), `${filePath} should exist`);
  });
});

test("generated outputs preserve operating boundaries", () => {
  const result = runDailyCommandCenter();
  const combined = Object.values(result.outputs).map((filePath) => fs.readFileSync(filePath, "utf8")).join("\n");

  assert.match(combined, /No-send mode: on|no-send review only|local no-post queue|local no-send\/no-post/);
  assert.match(combined, /Cold SMS|blocked_provider_approval_required|SMS remains draft-only/);
  assert.doesNotMatch(combined, /Send allowed: yes/);
  assert.doesNotMatch(combined, /Post allowed by tool: yes/);
  assert.match(combined, /post_allowed_default|post_allowed/);
  assert.match(combined, /approved_for_manual_post/);
  assert.match(combined, /Social Post Readiness|missing local asset_path/);
});
