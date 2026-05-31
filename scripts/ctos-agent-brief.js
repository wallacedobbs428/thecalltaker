#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..", "ctos");

function readJson(relativePath, fallback = {}) {
  try {
    return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
  } catch (error) {
    return fallback;
  }
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function printSection(title, lines) {
  console.log(`\n${title}`);
  console.log("-".repeat(title.length));
  const clean = asArray(lines).filter(Boolean);
  if (!clean.length) {
    console.log("None recorded.");
    return;
  }
  clean.forEach((line) => console.log(`- ${line}`));
}

function campaignLine(campaign) {
  return `${campaign.owner_agent || "agent"} can operate ${campaign.name || campaign.campaign_id} [${campaign.autonomy_status || campaign.current_status || campaign.status}] - ${campaign.ai_next_action || campaign.next_agent_action}`;
}

function queueLine(item) {
  return `${item.queue_id}: ${item.channel} / ${item.campaign_id} [${item.status}] - send_allowed=${item.send_allowed}; provider=${item.provider_status}; next=${item.next_action}`;
}

const money = readJson("revenue/money-scoreboard.json");
const nextActions = asArray(readJson("ai-execution/ai-next-actions.json").next_actions);
const campaigns = asArray(readJson("campaigns/autonomous-campaigns.json").campaigns);
const campaignBoard = asArray(readJson("boards/master-campaign-board.json").campaigns);
const researchQueue = readJson("outbound/instagram-lead-research-queue.json", { tasks: [] });
const sendQueue = asArray(readJson("outbound/autonomous-send-queue.json").items);
const dmBatches = asArray(readJson("outbound/dm-draft-queue.json").draft_batches);
const emailQueue = asArray(readJson("outbound/email-send-queue.json").items);
const followUpSendQueue = asArray(readJson("outbound/follow-up-send-queue.json").items);
const inboundQueue = asArray(readJson("inbound/inbound-response-queue.json").items);
const escalations = asArray(readJson("communications/wallace-approval-queue.json").approval_items);
const webhook = readJson("product/webhook-status.json", { tracked_webhooks: [] });
const checkout = readJson("product/checkout-status.json", { known_blockers: [] });
const revenueOpps = asArray(readJson("revenue/revenue-opportunities.json").opportunities);
const laneOwnership = money.lane_ownership || {};

const autonomousReady = nextActions.filter((item) => String(item.action_mode || "").includes("autonomous_now"));
const integrationBlocked = [
  ...campaignBoard.filter((item) => String(item.autonomy_status || item.status).includes("blocked") || String(item.autonomy_status || "").includes("provider_gated")),
  ...sendQueue.filter((item) => item.status === "failed_provider_block"),
  ...emailQueue.filter((item) => item.status === "failed_provider_block")
];
const allowedCampaigns = campaignBoard.filter((item) =>
  ["active", "generation_allowed"].includes(item.status) ||
  ["allowed_after_real_lead_and_provider_check", "partially_autonomous", "autonomous_for_non_sensitive_followups", "generation_allowed", "research_autonomous_send_provider_gated", "classification_ready_reply_provider_gated", "right_lane_owned_middle_capture_ready"].includes(item.autonomy_status)
);
const pausedCampaigns = campaignBoard.filter((item) => ["blocked", "critical"].includes(item.status) || String(item.autonomy_status || "").includes("blocked"));
const leadsMoveable = sendQueue.filter((item) => item.status === "ready_for_agent_research" || item.status === "ready_to_generate");
const inboundAuto = inboundQueue.filter((item) => item.autonomous_reply_allowed && item.policy_check_result !== "escalate");
const followupsAuto = followUpSendQueue.filter((item) => item.send_allowed && !item.escalation_required);
const systemProof = asArray(money.system_proof);

console.log("CTOS Agent Brief");
console.log("================");
console.log(`Execution model: policy-based autonomy`);
console.log(`Target MRR: $${money.target_mrr ?? 10000}`);
console.log(`Confirmed MRR: $${money.current_confirmed_mrr ?? 0}`);
console.log(`Expected pipeline MRR: $${money.expected_pipeline_mrr ?? 0}`);
console.log(`Top AI money action: ${money.top_ai_action_likely_to_create_money_next || "None recorded."}`);

printSection(
  "Lane ownership today",
  [
    laneOwnership.left && `${laneOwnership.left.lane}: ${laneOwnership.left.owns}`,
    laneOwnership.middle && `${laneOwnership.middle.lane}: ${laneOwnership.middle.owns}`,
    laneOwnership.right && `${laneOwnership.right.lane}: ${laneOwnership.right.owns}`
  ]
);

printSection(
  "1. Autonomous actions agents can execute now",
  autonomousReady.slice(0, 10).map((item) => `${item.owner_agent}: ${item.next_ai_action} [escalation only if: ${item.escalation_only_if || "policy exception"}]`)
);

printSection(
  "2. Actions blocked by missing integrations",
  integrationBlocked.map((item) => item.queue_id ? queueLine(item) : campaignLine(item))
);

printSection(
  "3. Actions escalated to Wallace",
  escalations.map((item) => `${item.approval_id}: ${item.target_lead_or_business} - ${item.why_policy_cannot_handle_it}`)
);

printSection(
  "4. Campaigns currently allowed to run",
  allowedCampaigns.map(campaignLine)
);

printSection(
  "5. Campaigns paused by policy, provider, or rate limit",
  pausedCampaigns.map(campaignLine)
);

printSection(
  "6. Leads agents can move forward without Wallace",
  leadsMoveable.map(queueLine)
);

printSection(
  "7. Instagram lead research tasks ready",
  asArray(researchQueue.tasks).map((item) => `${item.task_id}: ${item.target_segment} in ${item.target_market} [${item.status}] - ${item.autonomous_next_action}`)
);

printSection(
  "8. Inbound replies agents can answer automatically",
  inboundAuto.map((item) => `${item.queue_id}: ${item.business_name} / ${item.intent} - ${item.next_best_ai_action}`)
);

printSection(
  "9. Follow-ups agents can send automatically",
  followupsAuto.map(queueLine)
);

printSection(
  "10. Revenue opportunities closest to money",
  revenueOpps.map((item) => `${item.owner_agent}: ${item.title} [${item.action_mode}] - ${item.next_ai_action}`)
);

printSection(
  "11. Provider/runtime blocks",
  asArray(money.provider_blocks)
);

printSection(
  "12. System proof: what AI handled without Wallace",
  [
    ...systemProof,
    `${sendQueue.length} outbound queue items policy-modeled without sends.`,
    `${dmBatches.reduce((sum, batch) => sum + asArray(batch.drafts).length, 0)} DM seed drafts are blocked from send until real leads exist.`,
    `${asArray(webhook.tracked_webhooks).filter((item) => item.autonomous_allowed).length} webhook/provider paths are marked autonomous-capable in CTOS state.`,
    `${asArray(checkout.known_blockers).length} checkout blocker(s) tracked without touching pricing/checkout files.`
  ]
);
