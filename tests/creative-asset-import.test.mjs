import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { CREATIVE_IMPORT_NO_POST_MODE, importCreativeAsset } from "../tools/creative/import_asset.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const sampleInput = path.join(repoRoot, "tools/creative/incoming_asset.sample.json");
const sampleRegistry = path.join(repoRoot, "tools/creative/creative_assets.sample.json");

function tempFile(name) {
  return path.join(os.tmpdir(), `tct-${name}-${Date.now()}-${Math.random().toString(16).slice(2)}.json`);
}

test("creative importer stays no-post/no-spend", () => {
  assert.equal(CREATIVE_IMPORT_NO_POST_MODE, true);
});

test("dry-run import scores incoming Higgsfield asset", () => {
  const output = tempFile("asset-preview").replace(/\.json$/, ".md");
  const result = importCreativeAsset({ inputPath: sampleInput, registryPath: sampleRegistry, outputPath: output });
  const rendered = fs.readFileSync(output, "utf8");

  assert.equal(result.accepted, true);
  assert.equal(result.write_registry, false);
  assert.equal(result.organic_verdict, "organic-ready");
  assert.match(rendered, /After-hours office missed call/);
  assert.match(rendered, /This command does not post to Facebook or Instagram/);
});

test("write-registry updates only the local registry file", () => {
  const registryCopy = tempFile("asset-registry");
  const output = tempFile("asset-preview").replace(/\.json$/, ".md");
  fs.copyFileSync(sampleRegistry, registryCopy);

  const result = importCreativeAsset({ inputPath: sampleInput, registryPath: registryCopy, outputPath: output, writeRegistry: true });
  const registry = JSON.parse(fs.readFileSync(registryCopy, "utf8"));

  assert.equal(result.accepted, true);
  assert.ok(registry.assets.some((asset) => asset.id === "higgsfield-after-hours-office-003"));
});

test("rejects remote asset URLs and off-domain landing pages", () => {
  const badInput = tempFile("bad-asset");
  const output = tempFile("bad-preview").replace(/\.json$/, ".md");
  const sample = JSON.parse(fs.readFileSync(sampleInput, "utf8"));
  fs.writeFileSync(
    badInput,
    JSON.stringify(
      {
        ...sample,
        id: "bad-remote-asset",
        asset_path: "https://example.invalid/video.mp4",
        landing_path: "https://not-thecalltaker.example.invalid/",
      },
      null,
      2,
    ),
  );

  const result = importCreativeAsset({ inputPath: badInput, registryPath: sampleRegistry, outputPath: output });
  const rendered = fs.readFileSync(output, "utf8");

  assert.equal(result.accepted, false);
  assert.match(rendered, /Landing path must stay on thecalltaker.com/);
  assert.match(rendered, /Asset path should be a local review path/);
});
