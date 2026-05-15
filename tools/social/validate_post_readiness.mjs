import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const POST_READINESS_NO_POST_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../..");
const defaults = {
  calendar: path.join(repoRoot, "tools/social/output/social-calendar.sample.json"),
  registry: path.join(repoRoot, "tools/creative/creative_assets.sample.json"),
  output: path.join(repoRoot, "tools/social/output/post-readiness.sample.json"),
  markdown: path.join(repoRoot, "tools/social/output/post-readiness.sample.md"),
};

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--calendar") args.calendar = argv[++index];
    else if (arg === "--registry") args.registry = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else if (arg === "--markdown") args.markdown = argv[++index];
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return { ...defaults, ...args };
}

function usage() {
  return `The Call Taker social post readiness validator

Usage:
  node tools/social/validate_post_readiness.mjs

Checks approved calendar items against local asset files. It never posts or calls social APIs.
`;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function assetMap(registry) {
  return new Map((registry.assets || []).map((asset) => [asset.id, asset]));
}

function resolveAssetPath(asset) {
  if (!asset?.asset_path || asset.asset_path === "local-review-only") return null;
  if (path.isAbsolute(asset.asset_path)) return asset.asset_path;
  return path.join(repoRoot, asset.asset_path);
}

function validateItem(item, asset) {
  const missing = [];
  const assetPath = resolveAssetPath(asset);

  if (!asset) missing.push("missing creative registry asset");
  if (!assetPath) missing.push("missing local asset_path");
  if (assetPath && !fs.existsSync(assetPath)) missing.push("local asset file not found");
  if (item.post_allowed !== true) missing.push("calendar item is not approved for posting agent consideration");
  if (item.ready_for_manual_post !== true) missing.push("calendar item is not marked ready for manual post");

  return {
    date: item.date,
    platform: item.platform,
    asset_id: item.asset_id,
    asset_path: assetPath || "missing",
    ready_for_posting_agent: missing.length === 0,
    missing,
    caption: item.caption,
  };
}

export function validatePostReadiness(calendar, registry) {
  if (POST_READINESS_NO_POST_MODE !== true || calendar.no_post_mode !== true) {
    throw new Error("Post readiness validator must remain no-post.");
  }
  const assets = assetMap(registry);
  const items = (calendar.scheduled_posts || []).map((item) => validateItem(item, assets.get(item.asset_id)));
  return {
    generated_at: "2026-05-14T00:00:00.000Z",
    no_post_mode: POST_READINESS_NO_POST_MODE,
    ready_count: items.filter((item) => item.ready_for_posting_agent).length,
    blocked_count: items.filter((item) => !item.ready_for_posting_agent).length,
    items,
    blocked_policy: {
      auto_publish_allowed: false,
      provider_calls_allowed: false,
      paid_spend_allowed: false,
    },
  };
}

export function renderReadinessMarkdown(report) {
  const lines = [
    "# Social Post Readiness",
    "",
    "Status: local no-post validation. This file does not publish to Facebook, Instagram, Meta, or any provider.",
    "",
    `Ready for posting agent: ${report.ready_count}`,
    `Blocked: ${report.blocked_count}`,
    "",
  ];

  report.items.forEach((item) => {
    lines.push(`## ${item.date} - ${item.platform} - ${item.asset_id}`);
    lines.push("");
    lines.push(`- Ready: ${item.ready_for_posting_agent ? "yes" : "no"}`);
    lines.push(`- Asset path: ${item.asset_path}`);
    lines.push(`- Missing: ${item.missing.length ? item.missing.join("; ") : "none"}`);
    lines.push("");
  });

  lines.push("## Boundary", "");
  lines.push("- This validator does not post.");
  lines.push("- Missing local asset files must be fixed before a posting agent can use the item.");
  lines.push("- Paid spend is still blocked unless the paid launch gate and Wallace approval pass.");
  lines.push("");
  return lines.join("\n");
}

export function writePostReadiness({ calendarPath = defaults.calendar, registryPath = defaults.registry, outputPath = defaults.output, markdownPath = defaults.markdown } = {}) {
  const report = validatePostReadiness(readJson(calendarPath), readJson(registryPath));
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.mkdirSync(path.dirname(markdownPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(report, null, 2)}\n`);
  fs.writeFileSync(markdownPath, renderReadinessMarkdown(report));
  return {
    output: outputPath,
    markdown: markdownPath,
    ready_count: report.ready_count,
    blocked_count: report.blocked_count,
    no_post_mode: POST_READINESS_NO_POST_MODE,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(
      JSON.stringify(
        writePostReadiness({
          calendarPath: args.calendar,
          registryPath: args.registry,
          outputPath: args.output,
          markdownPath: args.markdown,
        }),
        null,
        2,
      ),
    );
  }
}
