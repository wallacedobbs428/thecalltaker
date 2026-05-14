import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { scoreAssets } from "./launch_gate.mjs";

export const CREATIVE_IMPORT_NO_POST_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaults = {
  input: path.join(__dirname, "incoming_asset.sample.json"),
  registry: path.join(__dirname, "creative_assets.sample.json"),
  output: path.join(__dirname, "output", "asset-import-preview.sample.md"),
};

const DEFAULT_CRITERIA = {
  first_two_second_clarity: 5,
  native_feed_fit: 5,
  offer_truth: 5,
  cta_alignment: 5,
  landing_match: 5,
  sound_off_understandable: 5,
  visual_quality: 5,
  learning_purpose: 5,
  distinct_test_value: 5,
  proof_safety: 5,
};

const DEFAULT_CHECKS = {
  has_clear_close: false,
  uses_fake_phone_ui: false,
  uses_readable_generated_screen_text: false,
  uses_fake_phone_number: false,
  has_unsupported_guarantee: false,
  claims_live_activation: false,
  claims_provider_routing: false,
  claims_every_call_answered: false,
  has_price_mismatch: false,
  looks_ai_generated_first: false,
  brand_pronunciation_verified: false,
};

function parseArgs(argv) {
  const args = { dryRun: true };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--input") args.input = argv[++index];
    else if (arg === "--registry") args.registry = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else if (arg === "--write-registry") args.writeRegistry = true;
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return { ...defaults, ...args };
}

function usage() {
  return `The Call Taker creative asset importer

Usage:
  node tools/creative/import_asset.mjs --input tools/creative/incoming_asset.sample.json
  node tools/creative/import_asset.mjs --input local/private-asset.json --write-registry

Default mode is dry-run preview. It never posts, spends, or calls Meta/Higgsfield APIs.
`;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function normalizeArray(value, fallback = []) {
  if (Array.isArray(value)) return value;
  if (typeof value === "string" && value.trim()) return value.split(",").map((item) => item.trim()).filter(Boolean);
  return fallback;
}

function normalizeAsset(input) {
  const asset = {
    id: input.id,
    title: input.title,
    platform: normalizeArray(input.platform, ["facebook", "instagram"]),
    format: input.format || "reel",
    source: input.source || "higgsfield",
    learning_purpose: input.learning_purpose,
    hook: input.hook,
    cta: input.cta,
    landing_path: input.landing_path,
    offer: input.offer,
    claim_notes: input.claim_notes || "Needs Wallace review before posting.",
    criteria: {
      ...DEFAULT_CRITERIA,
      ...(input.criteria || {}),
    },
    checks: {
      ...DEFAULT_CHECKS,
      ...(input.checks || {}),
    },
    asset_path: input.asset_path || "local-review-only",
    created_at: input.created_at || "2026-05-14",
    import_status: "previewed",
  };

  return asset;
}

function validateIncoming(input) {
  const errors = [];
  ["id", "title", "learning_purpose", "hook", "cta", "landing_path", "offer"].forEach((field) => {
    if (!input[field]) errors.push(`Missing required field: ${field}`);
  });
  if (input.landing_path && !String(input.landing_path).startsWith("https://thecalltaker.com/")) {
    errors.push("Landing path must stay on thecalltaker.com for launch-gate samples.");
  }
  if (input.asset_path && String(input.asset_path).match(/https?:\/\//i)) {
    errors.push("Asset path should be a local review path, not a remote URL.");
  }
  return errors;
}

function renderPreview({ asset, scored, errors, registryPath, writeRegistry }) {
  const lines = [
    "# Creative Asset Import Preview",
    "",
    "Status: local no-post/no-spend import preview.",
    `Registry: ${registryPath}`,
    `Write registry: ${writeRegistry ? "yes" : "no"}`,
    "",
  ];

  if (errors.length > 0) {
    lines.push("## Rejected", "");
    errors.forEach((error) => lines.push(`- ${error}`));
    lines.push("");
  } else {
    lines.push("## Normalized Asset", "");
    lines.push(`- ID: ${asset.id}`);
    lines.push(`- Title: ${asset.title}`);
    lines.push(`- Source: ${asset.source}`);
    lines.push(`- Hook: ${asset.hook}`);
    lines.push(`- CTA: ${asset.cta}`);
    lines.push(`- Landing: ${asset.landing_path}`);
    lines.push(`- Score: ${scored.score}/100`);
    lines.push(`- Organic verdict: ${scored.organic_verdict}`);
    lines.push(`- Paid verdict: ${scored.paid_verdict}`);
    lines.push(`- Hard fails: ${scored.hard_fails.length ? scored.hard_fails.join("; ") : "none"}`);
    lines.push(`- Smallest fix: ${scored.smallest_fix}`);
    lines.push("");
  }

  lines.push("## Boundary", "");
  lines.push("- This command does not post to Facebook or Instagram.");
  lines.push("- This command does not call Meta, Higgsfield, or any provider API.");
  lines.push("- This command does not spend budget.");
  lines.push("- Writing the registry is local-file only and still requires launch-gate review.");
  lines.push("");
  return lines.join("\n");
}

export function importCreativeAsset({ inputPath = defaults.input, registryPath = defaults.registry, outputPath = defaults.output, writeRegistry = false } = {}) {
  if (CREATIVE_IMPORT_NO_POST_MODE !== true) {
    throw new Error("Creative asset importer must remain no-post/no-spend.");
  }

  const incoming = readJson(inputPath);
  const errors = validateIncoming(incoming);
  const asset = normalizeAsset(incoming);
  const [scored] = errors.length ? [{ score: 0, organic_verdict: "hold", paid_verdict: "paid-hold", hard_fails: errors, smallest_fix: errors[0] }] : scoreAssets([asset]);

  if (writeRegistry && errors.length === 0) {
    const registry = readJson(registryPath);
    const existingIndex = registry.assets.findIndex((item) => item.id === asset.id);
    if (existingIndex >= 0) registry.assets[existingIndex] = asset;
    else registry.assets.push(asset);
    fs.writeFileSync(registryPath, `${JSON.stringify(registry, null, 2)}\n`);
  }

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, renderPreview({ asset, scored, errors, registryPath, writeRegistry }));

  return {
    output: outputPath,
    accepted: errors.length === 0,
    write_registry: writeRegistry,
    organic_verdict: scored.organic_verdict,
    paid_verdict: scored.paid_verdict,
    no_post_mode: CREATIVE_IMPORT_NO_POST_MODE,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(
      JSON.stringify(
        importCreativeAsset({
          inputPath: args.input,
          registryPath: args.registry,
          outputPath: args.output,
          writeRegistry: args.writeRegistry === true,
        }),
        null,
        2,
      ),
    );
  }
}
