import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadProspects, scoreProspects } from "../outreach/score_prospects.mjs";
import { generateSmsPreview } from "../outreach/generate_sms_preview.mjs";
import { scoreAssets } from "../creative/launch_gate.mjs";

export const ACTION_BOARD_NO_SEND_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../..");
const defaults = {
  prospects: path.join(repoRoot, "tools/outreach/sample_prospects.json"),
  smsStatus: path.join(repoRoot, "tools/outreach/sms_approval_status.json"),
  smsTemplates: path.join(repoRoot, "tools/outreach/sms_templates.json"),
  creativeAssets: path.join(repoRoot, "tools/creative/creative_assets.sample.json"),
  output: path.join(repoRoot, "tools/command-center/output/wallace-action-board.sample.md"),
};

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--prospects") args.prospects = argv[++index];
    else if (arg === "--sms-status") args.smsStatus = argv[++index];
    else if (arg === "--sms-templates") args.smsTemplates = argv[++index];
    else if (arg === "--creative-assets") args.creativeAssets = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return { ...defaults, ...args };
}

function usage() {
  return `The Call Taker Wallace action board

Usage:
  node tools/command-center/wallace_action_board.mjs

This command writes a local no-send/no-post daily board combining prospects, SMS gates, and creative launch-gate verdicts.
`;
}

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function countBy(items, key) {
  return items.reduce((counts, item) => {
    const value = item[key] || "unknown";
    counts[value] = (counts[value] || 0) + 1;
    return counts;
  }, {});
}

function topProspects(scored) {
  return scored.filter((prospect) => prospect.score_category === "A").slice(0, 5);
}

function smsPreviewForProspect(prospect, status, templates) {
  const scenario = "cold_candidate";
  return generateSmsPreview({
    scenario,
    status,
    templates,
    prospect: {
      first_name: prospect.contact_person === "unknown" ? "there" : prospect.contact_person.split(/\s+/)[0],
      company: prospect.business_name,
      industry: prospect.industry,
      call_path_note: prospect.current_answering_path,
    },
  });
}

function renderCounts(counts) {
  return Object.entries(counts)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => `- ${key}: ${value}`)
    .join("\n");
}

function renderProspectAction(prospect, index, smsPreview) {
  const asset = prospect.asset_selector;
  return [
    `### ${index + 1}. ${prospect.business_name}`,
    "",
    `- Score: ${prospect.score} (${prospect.score_category})`,
    `- Industry: ${prospect.industry}`,
    `- Reason: ${prospect.missed_call_risk_notes}`,
    `- First touch: ${prospect.recommended_first_touch}`,
    `- Wallace opener: ${asset.phone_opener}`,
    `- Email opener: ${asset.email_opener}`,
    `- SMS gate: ${smsPreview.gate}`,
    `- SMS draft allowed to send: ${smsPreview.send_allowed ? "yes" : "no"}`,
    `- SMS draft preview: ${smsPreview.messages[0]}`,
    `- Next action: ${prospect.next_action}`,
    "",
  ].join("\n");
}

function renderCreativeAction(asset, index) {
  return [
    `### ${index + 1}. ${asset.id}`,
    "",
    `- Score: ${asset.score}/100`,
    `- Organic: ${asset.organic_verdict}`,
    `- Paid: ${asset.paid_verdict}`,
    `- Hook: ${asset.hook}`,
    `- CTA: ${asset.cta}`,
    `- Hard fails: ${asset.hard_fails.length ? asset.hard_fails.join("; ") : "none"}`,
    `- Next test: ${asset.next_test}`,
    "",
  ].join("\n");
}

export function buildActionBoard({ prospectsPath, smsStatusPath, smsTemplatesPath, creativeAssetsPath }) {
  if (ACTION_BOARD_NO_SEND_MODE !== true) {
    throw new Error("Wallace action board must remain no-send/no-post.");
  }

  const scoredProspects = scoreProspects(loadProspects(prospectsPath));
  const smsStatus = loadJson(smsStatusPath);
  const smsTemplates = loadJson(smsTemplatesPath);
  const scoredCreatives = scoreAssets(loadJson(creativeAssetsPath).assets);
  const aProspects = topProspects(scoredProspects);
  const organicReady = scoredCreatives.filter((asset) => asset.organic_verdict === "organic-ready");
  const paidReady = scoredCreatives.filter((asset) => asset.paid_verdict === "paid-ready");
  const heldCreatives = scoredCreatives.filter((asset) => asset.organic_verdict === "hold");

  return {
    no_send_mode: ACTION_BOARD_NO_SEND_MODE,
    scoredProspects,
    prospectCounts: countBy(scoredProspects, "score_category"),
    smsStatus,
    aProspects,
    prospectActions: aProspects.map((prospect) => ({
      prospect,
      smsPreview: smsPreviewForProspect(prospect, smsStatus, smsTemplates),
    })),
    scoredCreatives,
    organicReady,
    paidReady,
    heldCreatives,
  };
}

export function renderActionBoard(board) {
  const lines = [
    "# Wallace Daily Action Board",
    "",
    "Status: local no-send/no-post command output. No outreach, SMS, calls, webhooks, provider writes, posting, ad launch, or spend occurred.",
    "",
    "## Today",
    "",
    `- A prospects for Wallace review: ${board.prospectCounts.A || 0}`,
    `- B prospects for manual sequence review: ${board.prospectCounts.B || 0}`,
    `- C prospects for nurture: ${board.prospectCounts.C || 0}`,
    `- D prospects suppressed: ${board.prospectCounts.D || 0}`,
    `- SMS status: ${board.smsStatus.status_label}`,
    `- SMS provider approval verified: ${board.smsStatus.provider_submission.provider_approval_verified ? "yes" : "no"}`,
    `- Organic-ready creative assets: ${board.organicReady.length}`,
    `- Paid-ready creative assets: ${board.paidReady.length}`,
    `- Held creative assets: ${board.heldCreatives.length}`,
    "",
    "## Prospect Mix",
    "",
    renderCounts(board.prospectCounts),
    "",
    "## Wallace Prospect Actions",
    "",
    ...(board.prospectActions.length
      ? board.prospectActions.map(({ prospect, smsPreview }, index) => renderProspectAction(prospect, index, smsPreview))
      : ["No A prospects in this sample.\n"]),
    "## Creative Actions",
    "",
    ...(board.scoredCreatives.length ? board.scoredCreatives.slice(0, 5).map(renderCreativeAction) : ["No creative assets registered.\n"]),
    "## Hard Gates",
    "",
    "- SMS remains draft-only until approval status is updated and provider approval is verified.",
    "- Cold SMS is blocked when the SMS gate says provider approval is required.",
    "- Organic posting is not performed by this command.",
    "- Paid Meta launch is not performed by this command.",
    "- Provider writes, CRM writes, emails, SMS, calls, DMs, webhooks, and payment changes are outside this command.",
    "",
  ];

  return lines.join("\n");
}

export function writeActionBoard(options = {}) {
  const board = buildActionBoard({
    prospectsPath: options.prospects || defaults.prospects,
    smsStatusPath: options.smsStatus || defaults.smsStatus,
    smsTemplatesPath: options.smsTemplates || defaults.smsTemplates,
    creativeAssetsPath: options.creativeAssets || defaults.creativeAssets,
  });
  const outputPath = options.output || defaults.output;
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, renderActionBoard(board));
  return {
    output: outputPath,
    no_send_mode: ACTION_BOARD_NO_SEND_MODE,
    a_prospects: board.prospectCounts.A || 0,
    organic_ready: board.organicReady.length,
    paid_ready: board.paidReady.length,
    sms_status: board.smsStatus.status,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(JSON.stringify(writeActionBoard(args), null, 2));
  }
}
