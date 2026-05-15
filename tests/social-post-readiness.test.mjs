import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { POST_READINESS_NO_POST_MODE, renderReadinessMarkdown, validatePostReadiness } from "../tools/social/validate_post_readiness.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const calendar = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/social/output/social-calendar.sample.json"), "utf8"));
const registry = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/creative/creative_assets.sample.json"), "utf8"));

test("post readiness validator stays no-post", () => {
  assert.equal(POST_READINESS_NO_POST_MODE, true);
});

test("sample calendar is blocked until local asset files exist", () => {
  const report = validatePostReadiness(calendar, registry);

  assert.equal(report.no_post_mode, true);
  assert.equal(report.ready_count, 0);
  assert.ok(report.blocked_count > 0);
  assert.ok(report.items.every((item) => item.missing.includes("missing local asset_path")));
});

test("readiness passes when registry points to an existing local file", () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "tct-social-asset-"));
  const assetPath = path.join(tempDir, "asset.mp4");
  fs.writeFileSync(assetPath, "fake local video placeholder");
  const localRegistry = {
    assets: registry.assets.map((asset) => ({
      ...asset,
      asset_path: asset.id === "organic-missed-call-office-001" ? assetPath : asset.asset_path,
    })),
  };

  const report = validatePostReadiness(calendar, localRegistry);

  assert.ok(report.ready_count > 0);
  assert.ok(report.items.some((item) => item.ready_for_posting_agent === true));
});

test("markdown reports missing asset reason", () => {
  const markdown = renderReadinessMarkdown(validatePostReadiness(calendar, registry));

  assert.match(markdown, /Social Post Readiness/);
  assert.match(markdown, /missing local asset_path/);
  assert.match(markdown, /This validator does not post/);
});
