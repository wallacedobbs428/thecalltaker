import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { buildOrganicQueue } from "./generate_organic_queue.mjs";

export const SOCIAL_HANDOFF_NO_POST_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaults = {
  input: path.join(__dirname, "creative_assets.sample.json"),
  output: path.join(__dirname, "output", "social-agent-handoff.sample.json"),
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
  return `The Call Taker social-agent handoff generator

Usage:
  node tools/creative/generate_social_handoff.mjs

Creates machine-readable Facebook/Instagram post candidates for a separate posting agent. This tool never posts.
`;
}

function loadAssets(filePath) {
  const parsed = JSON.parse(fs.readFileSync(filePath, "utf8"));
  return parsed.assets || [];
}

function hashtagsFor(item) {
  const base = ["#TheCallTaker", "#MissedCalls", "#LocalBusiness", "#ServiceBusiness"];
  if (item.caption.toLowerCase().includes("after-hours") || item.caption.toLowerCase().includes("after hours")) {
    base.push("#AfterHours");
  }
  return base;
}

function platformPayload(item, platform) {
  return {
    platform,
    asset_id: item.asset_id,
    format: item.format,
    caption: item.caption,
    story_frames: item.story_frames,
    cta: item.cta,
    landing_path: item.landing_path,
    hashtags: hashtagsFor(item),
    post_allowed: false,
    required_manual_checks: [
      "asset file exists and plays cleanly",
      "no fake UI or unreadable generated screen text",
      "brand pronunciation verified if voice is present",
      "claim still matches landing page",
      "Wallace or approved operator gives final post approval",
    ],
  };
}

export function buildSocialHandoff(assets) {
  if (SOCIAL_HANDOFF_NO_POST_MODE !== true) {
    throw new Error("Social handoff must remain no-post.");
  }

  const queue = buildOrganicQueue(assets);
  return {
    generated_at: "2026-05-14T00:00:00.000Z",
    no_post_mode: SOCIAL_HANDOFF_NO_POST_MODE,
    posting_agent_instruction:
      "Use this as candidate input only. Do not post unless a separate approval system marks the item approved.",
    candidates: queue.flatMap((item) => item.platforms.map((platform) => platformPayload(item, platform))),
    blocked_policy: {
      post_allowed_default: false,
      paid_spend_allowed: false,
      provider_calls_allowed: false,
      auto_publish_allowed: false,
    },
  };
}

export function writeSocialHandoff(inputPath = defaults.input, outputPath = defaults.output) {
  const handoff = buildSocialHandoff(loadAssets(inputPath));
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(handoff, null, 2)}\n`);
  return {
    output: outputPath,
    candidates: handoff.candidates.length,
    post_allowed_default: false,
    no_post_mode: SOCIAL_HANDOFF_NO_POST_MODE,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(JSON.stringify(writeSocialHandoff(args.input, args.output), null, 2));
  }
}
