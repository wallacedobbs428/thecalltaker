import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { scoreAssets } from "./launch_gate.mjs";

export const ORGANIC_QUEUE_NO_POST_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaults = {
  input: path.join(__dirname, "creative_assets.sample.json"),
  output: path.join(__dirname, "output", "organic-content-queue.sample.md"),
};

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--input") args.input = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return { ...defaults, ...args };
}

function usage() {
  return `The Call Taker organic content queue generator

Usage:
  node tools/creative/generate_organic_queue.mjs

Creates a local Facebook/Instagram content queue from organic-ready creative assets. It never posts or calls social APIs.
`;
}

function loadAssets(filePath) {
  const parsed = JSON.parse(fs.readFileSync(filePath, "utf8"));
  return parsed.assets || [];
}

function captionFor(asset) {
  const hook = asset.hook.endsWith(".") ? asset.hook : `${asset.hook}.`;
  return `${hook}\n\nMost service businesses do not need more noise. They need a cleaner way to catch missed and after-hours calls before the caller moves on.\n\nThe Call Taker shows the caller experience first. Nothing goes live without reviewed setup.\n\n${asset.cta}`;
}

function storyFrameFor(asset) {
  return [
    asset.hook,
    "missed calls do not wait",
    "preview the caller experience before anything goes live",
    asset.cta,
  ];
}

export function buildOrganicQueue(assets) {
  if (ORGANIC_QUEUE_NO_POST_MODE !== true) {
    throw new Error("Organic queue must remain no-post.");
  }
  return scoreAssets(assets)
    .filter((asset) => asset.organic_verdict === "organic-ready")
    .map((asset, index) => ({
      day: index + 1,
      asset_id: asset.id,
      platforms: asset.platform,
      format: asset.format,
      organic_verdict: asset.organic_verdict,
      paid_verdict: asset.paid_verdict,
      score: asset.score,
      hook: asset.hook,
      caption: captionFor(asset),
      story_frames: storyFrameFor(asset),
      cta: asset.cta,
      landing_path: asset.landing_path,
      post_allowed_by_tool: false,
      operator_action: "Wallace review, then post manually only if asset file passes visual QA.",
    }));
}

export function renderOrganicQueue(queue) {
  const lines = [
    "# Organic Facebook/Instagram Content Queue",
    "",
    "Status: local no-post queue. This file does not publish to Facebook, Instagram, Meta, Higgsfield, or any provider.",
    "",
  ];

  if (queue.length === 0) {
    lines.push("No organic-ready assets.");
  } else {
    queue.forEach((item) => {
      lines.push(`## Day ${item.day}: ${item.asset_id}`);
      lines.push("");
      lines.push(`- Platforms: ${item.platforms.join(", ")}`);
      lines.push(`- Format: ${item.format}`);
      lines.push(`- Score: ${item.score}/100`);
      lines.push(`- Organic verdict: ${item.organic_verdict}`);
      lines.push(`- Paid verdict: ${item.paid_verdict}`);
      lines.push(`- Landing: ${item.landing_path}`);
      lines.push(`- Post allowed by tool: ${item.post_allowed_by_tool ? "yes" : "no"}`);
      lines.push(`- Operator action: ${item.operator_action}`);
      lines.push("");
      lines.push("### Caption");
      lines.push("");
      lines.push(item.caption);
      lines.push("");
      lines.push("### Story Frames");
      lines.push("");
      item.story_frames.forEach((frame, index) => lines.push(`${index + 1}. ${frame}`));
      lines.push("");
    });
  }

  lines.push("## Posting Boundary", "");
  lines.push("- This queue prepares manual post candidates only.");
  lines.push("- Do not post assets that fail visual QA, brand pronunciation, or claim safety.");
  lines.push("- Do not turn organic-ready into paid spend without launch-gate review and Wallace approval.");
  lines.push("");
  return lines.join("\n");
}

export function writeOrganicQueue(inputPath = defaults.input, outputPath = defaults.output) {
  const queue = buildOrganicQueue(loadAssets(inputPath));
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, renderOrganicQueue(queue));
  return {
    output: outputPath,
    posts_ready_for_manual_review: queue.length,
    post_allowed_by_tool: false,
    no_post_mode: ORGANIC_QUEUE_NO_POST_MODE,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(JSON.stringify(writeOrganicQueue(args.input, args.output), null, 2));
  }
}
