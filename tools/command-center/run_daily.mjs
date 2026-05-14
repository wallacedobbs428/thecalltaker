import path from "node:path";
import { fileURLToPath } from "node:url";
import { writeDailyQueue } from "../outreach/generate_daily_queue.mjs";
import { writeApprovalPacket } from "../outreach/generate_sms_approval_packet.mjs";
import { writeSmsPreview } from "../outreach/generate_sms_preview.mjs";
import { writeLaunchGate } from "../creative/launch_gate.mjs";
import { writeOrganicQueue } from "../creative/generate_organic_queue.mjs";
import { writeActionBoard } from "./wallace_action_board.mjs";

export const DAILY_RUNNER_NO_SEND_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../..");

const paths = {
  prospects: path.join(repoRoot, "tools/outreach/sample_prospects.json"),
  dailyQueue: path.join(repoRoot, "tools/outreach/output/daily-queue.sample.md"),
  smsApprovalPacket: path.join(repoRoot, "tools/outreach/output/sms-approval-packet.sample.md"),
  smsSampleProspect: path.join(repoRoot, "tools/outreach/sms_preview_sample.json"),
  smsWarmPreview: path.join(repoRoot, "tools/outreach/output/sms-preview.sample.md"),
  smsColdPreview: path.join(repoRoot, "tools/outreach/output/sms-preview-cold-blocked.sample.md"),
  creativeAssets: path.join(repoRoot, "tools/creative/creative_assets.sample.json"),
  launchGate: path.join(repoRoot, "tools/creative/output/launch-gate.sample.md"),
  organicQueue: path.join(repoRoot, "tools/creative/output/organic-content-queue.sample.md"),
  actionBoard: path.join(repoRoot, "tools/command-center/output/wallace-action-board.sample.md"),
};

function usage() {
  return `The Call Taker daily command center runner

Usage:
  node tools/command-center/run_daily.mjs

Regenerates local sample operating outputs. It does not send outreach, post content, call providers, deploy, or spend budget.
`;
}

export function runDailyCommandCenter() {
  if (DAILY_RUNNER_NO_SEND_MODE !== true) {
    throw new Error("Daily command runner must remain no-send/no-post.");
  }

  const dailyQueue = writeDailyQueue(paths.prospects, paths.dailyQueue, { generatedAt: "2026-05-14T00:00:00.000Z" });
  const smsApproval = writeApprovalPacket(paths.smsApprovalPacket);
  const smsWarm = writeSmsPreview({
    scenario: "after_demo",
    prospect: {
      first_name: "Sam",
      company: "Example HVAC",
      industry: "hvac",
      call_path_note: "after-hours calls appear to hit voicemail",
    },
    destination: paths.smsWarmPreview,
  });
  const smsCold = writeSmsPreview({
    scenario: "cold_candidate",
    prospect: {
      first_name: "Sam",
      company: "Example HVAC",
      industry: "hvac",
      call_path_note: "after-hours calls appear to hit voicemail",
    },
    destination: paths.smsColdPreview,
  });
  const launchGate = writeLaunchGate(paths.creativeAssets, paths.launchGate);
  const organicQueue = writeOrganicQueue(paths.creativeAssets, paths.organicQueue);
  const actionBoard = writeActionBoard({ output: paths.actionBoard });

  return {
    no_send_mode: DAILY_RUNNER_NO_SEND_MODE,
    outputs: {
      daily_queue: dailyQueue.outputPath,
      sms_approval_packet: smsApproval.output,
      sms_warm_preview: smsWarm.output,
      sms_cold_preview: smsCold.output,
      launch_gate: launchGate.output,
      organic_queue: organicQueue.output,
      action_board: actionBoard.output,
    },
    summary: {
      prospects_scored: dailyQueue.scored.length,
      sms_status: smsApproval.status,
      sms_cold_gate: smsCold.gate,
      organic_ready: launchGate.organic_ready,
      paid_ready: launchGate.paid_ready,
      posts_ready_for_manual_review: organicQueue.posts_ready_for_manual_review,
      a_prospects: actionBoard.a_prospects,
    },
  };
}

if (process.argv.includes("--help") || process.argv.includes("-h")) {
  console.log(usage());
} else if (process.argv[1] === fileURLToPath(import.meta.url)) {
  console.log(JSON.stringify(runDailyCommandCenter(), null, 2));
}
