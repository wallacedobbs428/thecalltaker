import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { buildOrganicQueue, ORGANIC_QUEUE_NO_POST_MODE, renderOrganicQueue } from "../tools/creative/generate_organic_queue.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const sample = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/creative/creative_assets.sample.json"), "utf8"));

test("organic queue stays no-post", () => {
  assert.equal(ORGANIC_QUEUE_NO_POST_MODE, true);
});

test("builds queue from organic-ready assets only", () => {
  const queue = buildOrganicQueue(sample.assets);

  assert.ok(queue.length >= 2);
  assert.ok(queue.every((item) => item.organic_verdict === "organic-ready"));
  assert.ok(queue.every((item) => item.post_allowed_by_tool === false));
  assert.ok(!queue.some((item) => item.asset_id === "paid-live-routing-unsafe-example"));
});

test("captions preserve preview boundary", () => {
  const queue = buildOrganicQueue(sample.assets);
  const combined = queue.map((item) => item.caption).join("\n");

  assert.match(combined, /Nothing goes live without reviewed setup/);
  assert.doesNotMatch(combined, /guaranteed booked jobs/i);
  assert.doesNotMatch(combined, /provider routing is active/i);
});

test("rendered queue includes manual operator boundary", () => {
  const rendered = renderOrganicQueue(buildOrganicQueue(sample.assets));

  assert.match(rendered, /local no-post queue/);
  assert.match(rendered, /Operator action:/);
  assert.match(rendered, /Do not turn organic-ready into paid spend/);
});
