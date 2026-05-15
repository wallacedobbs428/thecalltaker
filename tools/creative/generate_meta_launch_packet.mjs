import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { scoreAssets } from "./launch_gate.mjs";

export const META_PACKET_NO_SPEND_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../..");
const defaults = {
  input: path.join(__dirname, "creative_assets.sample.json"),
  output: path.join(__dirname, "output", "meta-launch-packet.sample.json"),
  markdown: path.join(__dirname, "output", "meta-launch-packet.sample.md"),
};

function usage() {
  return `The Call Taker Meta launch packet generator

Usage:
  node tools/creative/generate_meta_launch_packet.mjs

Creates a local manual setup packet for Wallace review. It does not post, launch ads, call Meta, or spend budget.
`;
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--input") args.input = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else if (arg === "--markdown") args.markdown = argv[++index];
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return { ...defaults, ...args };
}

function readAssets(filePath) {
  const parsed = JSON.parse(fs.readFileSync(filePath, "utf8"));
  if (!Array.isArray(parsed.assets)) throw new Error("Creative asset file must include an assets array.");
  return parsed.assets;
}

function resolveAssetPath(asset) {
  if (!asset.asset_path || asset.asset_path === "local-review-only") return null;
  if (path.isAbsolute(asset.asset_path)) return asset.asset_path;
  return path.join(repoRoot, asset.asset_path);
}

function missingLaunchRequirements(asset) {
  const missing = [];
  const assetPath = resolveAssetPath(asset);

  if (asset.paid_verdict !== "paid-ready") missing.push("paid launch gate not passed");
  if (asset.hard_fails.length > 0) missing.push("creative hard fail exists");
  if (!assetPath) missing.push("local asset file missing from registry");
  if (assetPath && !fs.existsSync(assetPath)) missing.push("registered local asset file not found");

  missing.push("Wallace paid-spend approval not recorded in this packet");
  missing.push("Meta account/manual setup not confirmed by this tool");

  return missing;
}

function buildAdDraft(asset, platform) {
  const missing = missingLaunchRequirements(asset);
  return {
    asset_id: asset.id,
    platform,
    campaign_name: `TCT | ${asset.offer} | ${asset.id}`,
    objective: "lead_or_demo_preview",
    funnel_path: asset.landing_path,
    hook: asset.hook,
    primary_text: asset.hook,
    headline: "Missed calls cost real money",
    description: "Preview how The Call Taker handles missed-call capture before anything goes live.",
    cta: asset.cta,
    audience_notes: [
      "Local service business owners/operators",
      "Prioritize emergency and appointment-based services",
      "Do not use private prospect lists in this sample packet",
    ],
    proof_boundary: asset.claim_notes,
    launch_allowed: false,
    missing_launch_requirements: missing,
  };
}

export function buildMetaLaunchPacket(assets) {
  if (META_PACKET_NO_SPEND_MODE !== true) {
    throw new Error("Meta launch packet must remain no-spend/no-post.");
  }

  const scored = scoreAssets(assets);
  const drafts = scored
    .filter((asset) => asset.organic_verdict === "organic-ready" || asset.paid_verdict === "paid-ready")
    .flatMap((asset) => asset.platform.map((platform) => buildAdDraft(asset, platform)));

  return {
    generated_at: "2026-05-14T00:00:00.000Z",
    no_spend_mode: META_PACKET_NO_SPEND_MODE,
    provider_calls_allowed: false,
    auto_publish_allowed: false,
    launch_allowed: false,
    drafts,
    blocked_count: drafts.filter((draft) => draft.launch_allowed !== true).length,
    manual_next_step: "Attach real local asset files, review in Meta manually, confirm Wallace paid-spend approval, then run the launch gate again.",
  };
}

export function renderMetaLaunchPacket(packet) {
  const lines = [
    "# Meta Launch Packet",
    "",
    "Status: local no-spend setup brief. This file does not post, launch ads, call Meta, upload audiences, or spend budget.",
    "",
    `Draft ads: ${packet.drafts.length}`,
    `Launch allowed by tool: ${packet.launch_allowed ? "yes" : "no"}`,
    `Blocked drafts: ${packet.blocked_count}`,
    "",
  ];

  packet.drafts.forEach((draft) => {
    lines.push(`## ${draft.platform} - ${draft.asset_id}`);
    lines.push("");
    lines.push(`- Campaign: ${draft.campaign_name}`);
    lines.push(`- Objective: ${draft.objective}`);
    lines.push(`- Funnel path: ${draft.funnel_path}`);
    lines.push(`- Hook: ${draft.hook}`);
    lines.push(`- Primary text: ${draft.primary_text}`);
    lines.push(`- Headline: ${draft.headline}`);
    lines.push(`- CTA: ${draft.cta}`);
    lines.push(`- Launch allowed: ${draft.launch_allowed ? "yes" : "no"}`);
    lines.push(`- Missing launch requirements: ${draft.missing_launch_requirements.join("; ")}`);
    lines.push("");
  });

  lines.push("## Operator Boundary", "");
  lines.push("- This packet is for manual setup planning only.");
  lines.push("- Do not launch paid spend from this file.");
  lines.push("- Do not upload private prospect lists or customer data from this repo.");
  lines.push("- No provider/API write is performed by this tool.");
  lines.push("");
  return lines.join("\n");
}

export function writeMetaLaunchPacket({ inputPath = defaults.input, outputPath = defaults.output, markdownPath = defaults.markdown } = {}) {
  const packet = buildMetaLaunchPacket(readAssets(inputPath));
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.mkdirSync(path.dirname(markdownPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(packet, null, 2)}\n`);
  fs.writeFileSync(markdownPath, renderMetaLaunchPacket(packet));
  return {
    output: outputPath,
    markdown: markdownPath,
    drafts: packet.drafts.length,
    launch_allowed: packet.launch_allowed,
    no_spend_mode: META_PACKET_NO_SPEND_MODE,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(
      JSON.stringify(
        writeMetaLaunchPacket({
          inputPath: args.input,
          outputPath: args.output,
          markdownPath: args.markdown,
        }),
        null,
        2,
      ),
    );
  }
}
