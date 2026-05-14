import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const CREATIVE_GATE_NO_POST_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaultInput = path.join(__dirname, "creative_assets.sample.json");
const defaultOutput = path.join(__dirname, "output", "launch-gate.sample.md");

const HARD_FAIL_CHECKS = {
  uses_fake_phone_ui: "fake phone UI",
  uses_readable_generated_screen_text: "readable generated screen text",
  uses_fake_phone_number: "fake phone number",
  has_unsupported_guarantee: "unsupported guarantee",
  claims_live_activation: "fake live activation claim",
  claims_provider_routing: "provider routing claim",
  claims_every_call_answered: "every-call claim",
  has_price_mismatch: "price or offer mismatch",
  looks_ai_generated_first: "looks AI-generated before offer is clear",
};

const REQUIRED_CRITERIA = [
  "first_two_second_clarity",
  "native_feed_fit",
  "offer_truth",
  "cta_alignment",
  "landing_match",
  "sound_off_understandable",
  "visual_quality",
  "learning_purpose",
  "distinct_test_value",
  "proof_safety",
];

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--input") args.input = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return args;
}

function usage() {
  return `The Call Taker Meta/Higgsfield launch gate

Usage:
  node tools/creative/launch_gate.mjs
  node tools/creative/launch_gate.mjs --input tools/creative/creative_assets.sample.json

This tool scores creative assets for organic and paid readiness. It does not post, deploy, spend, call providers, or touch Meta/Higgsfield APIs.
`;
}

function loadAssets(filePath) {
  const parsed = JSON.parse(fs.readFileSync(filePath, "utf8"));
  if (!Array.isArray(parsed.assets)) throw new Error("Creative asset file must include an assets array.");
  return parsed.assets;
}

function validateAsset(asset) {
  const errors = [];
  ["id", "title", "platform", "format", "source", "learning_purpose", "hook", "cta", "landing_path", "offer", "criteria", "checks"].forEach((field) => {
    if (!Object.prototype.hasOwnProperty.call(asset, field)) errors.push(`Missing required field: ${field}`);
  });
  if (asset.criteria) {
    REQUIRED_CRITERIA.forEach((field) => {
      if (typeof asset.criteria[field] !== "number") errors.push(`Missing numeric criterion: ${field}`);
    });
  }
  return errors;
}

function scoreAsset(asset) {
  const validationErrors = validateAsset(asset);
  const score = REQUIRED_CRITERIA.reduce((total, field) => total + Math.max(0, Math.min(10, asset.criteria?.[field] || 0)), 0);
  const hardFails = Object.entries(HARD_FAIL_CHECKS)
    .filter(([field]) => asset.checks?.[field] === true)
    .map(([, label]) => label);

  if (asset.checks?.brand_pronunciation_verified !== true) {
    hardFails.push("brand pronunciation not verified");
  }
  if (asset.checks?.has_clear_close !== true) {
    hardFails.push("missing clear close");
  }
  validationErrors.forEach((error) => hardFails.push(error));

  const organicVerdict =
    hardFails.length === 0 && score >= 70
      ? "organic-ready"
      : hardFails.length === 0 && score >= 55
        ? "organic-revise"
        : "hold";
  const paidVerdict = hardFails.length === 0 && score >= 85 ? "paid-ready" : "paid-hold";

  const smallestFix =
    hardFails[0] ||
    (score < 70 ? "raise first-two-second clarity and CTA alignment" : score < 85 ? "improve paid-spend score before launch" : "ready for controlled test");

  return {
    ...asset,
    score,
    hard_fails: hardFails,
    organic_verdict: organicVerdict,
    paid_verdict: paidVerdict,
    smallest_fix: smallestFix,
    next_test:
      paidVerdict === "paid-ready"
        ? "controlled paid test after Wallace approval"
        : organicVerdict === "organic-ready"
          ? "post organic first and watch comments/saves/profile clicks"
          : "revise asset before posting",
  };
}

export function scoreAssets(assets) {
  if (CREATIVE_GATE_NO_POST_MODE !== true) {
    throw new Error("Creative launch gate must remain no-post/no-spend.");
  }
  return assets.map(scoreAsset).sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
}

export function renderLaunchGate(scored) {
  const lines = [
    "# Meta/Higgsfield Launch Gate",
    "",
    "Status: no-post/no-spend review output. This file does not post organic content, launch ads, call providers, or spend budget.",
    "",
    "## Verdicts",
    "",
  ];

  scored.forEach((asset) => {
    lines.push(`### ${asset.id}`);
    lines.push(`- Score: ${asset.score}/100`);
    lines.push(`- Organic verdict: ${asset.organic_verdict}`);
    lines.push(`- Paid verdict: ${asset.paid_verdict}`);
    lines.push(`- Hook: ${asset.hook}`);
    lines.push(`- CTA: ${asset.cta}`);
    lines.push(`- Landing path: ${asset.landing_path}`);
    lines.push(`- Hard fails: ${asset.hard_fails.length ? asset.hard_fails.join("; ") : "none"}`);
    lines.push(`- Smallest fix: ${asset.smallest_fix}`);
    lines.push(`- Next test: ${asset.next_test}`);
    lines.push("");
  });

  lines.push("## Rules");
  lines.push("");
  lines.push("- Organic can move faster than paid, but hard fails still block posting.");
  lines.push("- Paid requires score 85+ and zero hard fails.");
  lines.push("- Higgsfield assets must not rely on fake UI, readable generated screen text, fake numbers, or unverified pronunciation.");
  lines.push("- Every ad needs one learning purpose, a safe claim, and a CTA that matches the landing path.");
  lines.push("");
  return `${lines.join("\n")}`;
}

export function writeLaunchGate(inputPath = defaultInput, outputPath = defaultOutput) {
  const scored = scoreAssets(loadAssets(inputPath));
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, renderLaunchGate(scored));
  return {
    output: outputPath,
    total: scored.length,
    organic_ready: scored.filter((asset) => asset.organic_verdict === "organic-ready").length,
    paid_ready: scored.filter((asset) => asset.paid_verdict === "paid-ready").length,
    held: scored.filter((asset) => asset.organic_verdict === "hold").length,
    no_post_mode: CREATIVE_GATE_NO_POST_MODE,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(JSON.stringify(writeLaunchGate(args.input || defaultInput, args.output || defaultOutput), null, 2));
  }
}
