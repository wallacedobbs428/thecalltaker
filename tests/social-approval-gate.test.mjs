import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { applySocialApproval, SOCIAL_APPROVAL_NO_POST_MODE } from "../tools/creative/apply_social_approval.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const handoff = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/creative/output/social-agent-handoff.sample.json"), "utf8"));
const approval = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/creative/social_approval.sample.json"), "utf8"));

test("social approval gate stays no-post", () => {
  assert.equal(SOCIAL_APPROVAL_NO_POST_MODE, true);
});

test("approval manifest flips only matching candidate to manual post allowed", () => {
  const result = applySocialApproval(handoff, approval);
  const approved = result.candidates.filter((candidate) => candidate.post_allowed === true);

  assert.equal(result.no_post_mode, true);
  assert.equal(approved.length, 4);
  assert.ok(approved.some((candidate) => candidate.platform === "facebook" && candidate.asset_id === "organic-missed-call-office-001"));
  assert.ok(approved.every((candidate) => candidate.approval_status === "approved_for_manual_post"));
});

test("unreviewed candidates stay blocked", () => {
  const result = applySocialApproval(handoff, approval);

  assert.ok(!result.candidates.some((candidate) => candidate.approval_status === "not_reviewed"));
});

test("approved handoff still forbids auto publish and paid spend", () => {
  const result = applySocialApproval(handoff, approval);

  assert.equal(result.blocked_policy.auto_publish_allowed, false);
  assert.equal(result.blocked_policy.provider_calls_allowed, false);
  assert.equal(result.blocked_policy.paid_spend_allowed, false);
});
