import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SOCIAL_APPROVAL_NO_POST_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaults = {
  handoff: path.join(__dirname, "output", "social-agent-handoff.sample.json"),
  approval: path.join(__dirname, "social_approval.sample.json"),
  output: path.join(__dirname, "output", "social-agent-approved.sample.json"),
};

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--handoff") args.handoff = argv[++index];
    else if (arg === "--approval") args.approval = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return { ...defaults, ...args };
}

function usage() {
  return `The Call Taker social approval gate

Usage:
  node tools/creative/apply_social_approval.mjs

Applies a local approval manifest to the social-agent handoff. It still does not post.
`;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function approvalKey(item) {
  return `${item.platform}::${item.asset_id}`;
}

export function applySocialApproval(handoff, approval) {
  if (SOCIAL_APPROVAL_NO_POST_MODE !== true || handoff.no_post_mode !== true) {
    throw new Error("Social approval gate must remain no-post.");
  }

  const approved = new Map((approval.approved_candidates || []).map((item) => [approvalKey(item), item]));
  const blocked = new Map((approval.blocked_candidates || []).map((item) => [approvalKey(item), item]));

  const candidates = handoff.candidates.map((candidate) => {
    const key = approvalKey(candidate);
    const blockedItem = blocked.get(key);
    const approvedItem = approved.get(key);

    if (blockedItem) {
      return {
        ...candidate,
        approval_status: "blocked",
        post_allowed: false,
        approval_notes: blockedItem.notes || "Blocked by approval manifest.",
      };
    }

    if (approvedItem) {
      return {
        ...candidate,
        approval_status: "approved_for_manual_post",
        post_allowed: true,
        approval_notes: approvedItem.notes || "Approved for manual post only.",
      };
    }

    return {
      ...candidate,
      approval_status: "not_reviewed",
      post_allowed: false,
      approval_notes: "No approval manifest entry.",
    };
  });

  return {
    generated_at: approval.approved_at || handoff.generated_at,
    no_post_mode: SOCIAL_APPROVAL_NO_POST_MODE,
    approval_mode: approval.approval_mode || "local",
    approved_by: approval.approved_by || "unknown",
    posting_window: approval.posting_window || "manual-review-only",
    posting_agent_instruction:
      "Only candidates with post_allowed true may be considered by a separate posting agent. This file itself does not post.",
    candidates,
    blocked_policy: {
      auto_publish_allowed: false,
      provider_calls_allowed: false,
      paid_spend_allowed: false,
      requires_separate_posting_agent: true,
    },
  };
}

export function writeApprovedSocialHandoff({ handoffPath = defaults.handoff, approvalPath = defaults.approval, outputPath = defaults.output } = {}) {
  const approved = applySocialApproval(readJson(handoffPath), readJson(approvalPath));
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(approved, null, 2)}\n`);
  return {
    output: outputPath,
    approved_candidates: approved.candidates.filter((item) => item.post_allowed === true).length,
    blocked_candidates: approved.candidates.filter((item) => item.approval_status === "blocked").length,
    no_post_mode: SOCIAL_APPROVAL_NO_POST_MODE,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(
      JSON.stringify(
        writeApprovedSocialHandoff({
          handoffPath: args.handoff,
          approvalPath: args.approval,
          outputPath: args.output,
        }),
        null,
        2,
      ),
    );
  }
}
