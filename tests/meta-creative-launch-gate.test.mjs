import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { CREATIVE_GATE_NO_POST_MODE, renderLaunchGate, scoreAssets } from "../tools/creative/launch_gate.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const samplePath = path.join(repoRoot, "tools/creative/creative_assets.sample.json");
const sample = JSON.parse(fs.readFileSync(samplePath, "utf8"));

test("creative launch gate stays no-post/no-spend", () => {
  assert.equal(CREATIVE_GATE_NO_POST_MODE, true);
});

test("scores organic and paid readiness separately", () => {
  const scored = scoreAssets(sample.assets);
  const top = scored.find((asset) => asset.id === "organic-missed-call-office-001");

  assert.equal(top.organic_verdict, "organic-ready");
  assert.equal(top.paid_verdict, "paid-ready");
  assert.equal(top.hard_fails.length, 0);
  assert.ok(top.score >= 85);
});

test("blocks unsafe live-routing creative", () => {
  const scored = scoreAssets(sample.assets);
  const unsafe = scored.find((asset) => asset.id === "paid-live-routing-unsafe-example");

  assert.equal(unsafe.organic_verdict, "hold");
  assert.equal(unsafe.paid_verdict, "paid-hold");
  assert.ok(unsafe.hard_fails.includes("fake live activation claim"));
  assert.ok(unsafe.hard_fails.includes("provider routing claim"));
  assert.ok(unsafe.hard_fails.includes("looks AI-generated before offer is clear"));
});

test("rendered output includes required verdict fields", () => {
  const rendered = renderLaunchGate(scoreAssets(sample.assets));

  assert.match(rendered, /Organic verdict:/);
  assert.match(rendered, /Paid verdict:/);
  assert.match(rendered, /Hard fails:/);
  assert.match(rendered, /Paid requires score 85\+/);
});

test("missing required fields fail closed", () => {
  const broken = {
    ...sample.assets[0],
    id: "broken-asset",
  };
  delete broken.cta;

  const [scored] = scoreAssets([broken]);

  assert.equal(scored.organic_verdict, "hold");
  assert.equal(scored.paid_verdict, "paid-hold");
  assert.ok(scored.hard_fails.includes("Missing required field: cta"));
});
