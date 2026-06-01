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

function indexById(items, key) {
  return new Map(asArray(items).map((item) => [item[key], item]));
}

function taskById(tasks, taskId) {
  return indexById(tasks, "task_id").get(taskId);
}

function shortText(value, fallback = "None recorded.") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function firstStep(task) {
  return asArray(task.exact_execution_steps)[0] || task.next_action || "Review CTOS context and produce the next safe artifact.";
}

function lineStatus(task) {
  const autonomy = task.autonomous_now ? "AI can work" : "manual";
  const provider = task.provider_required ? `provider: ${shortText(task.provider_tool_needed)}` : "no provider";
  return `${task.task_id}: ${task.task_name} (${task.owner_agent}; ${task.priority}; ${task.status}; ${autonomy}; ${provider})`;
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

function taskLine(task) {
  const blocker = task.blocker && task.blocker !== "None." ? ` Blocker: ${task.blocker}` : "";
  return `${lineStatus(task)}. Next: ${firstStep(task)}${blocker}`;
}

function campaignLine(campaign) {
  return `${campaign.owner_agent || "agent"} can operate ${campaign.name || campaign.campaign_id} [${campaign.autonomy_status || campaign.current_status || campaign.status}] - ${campaign.ai_next_action || campaign.next_agent_action}`;
}

function queueLine(item) {
  return `${item.queue_id}: ${item.channel} / ${item.campaign_id} [${item.status}] - send_allowed=${item.send_allowed}; provider=${item.provider_status}; next=${item.next_action}`;
}

function includesAny(value, terms) {
  const text = String(value || "").toLowerCase();
  return terms.some((term) => text.includes(term));
}

function categoryText(task) {
  return [
    task.task_id,
    task.task_name,
    task.category,
    task.owner_agent
  ].join(" ");
}

function orderedTasks(board, orderKey) {
  const tasks = asArray(board.tasks);
  const ids = asArray(board.execution_order && board.execution_order[orderKey]);
  return ids.map((taskId) => taskById(tasks, taskId)).filter(Boolean);
}

function topReadyTasks(tasks, limit = 8) {
  return asArray(tasks)
    .filter((task) => task.autonomous_now && !task.provider_required && task.status !== "provider_blocked")
    .slice(0, limit);
}

function categoryNextTasks(tasks, terms, limit = 3) {
  return asArray(tasks)
    .filter((task) => includesAny(categoryText(task), terms))
    .slice(0, limit)
    .map((task) => `${task.task_id}: ${task.task_name} (${task.owner_agent}) - ${firstStep(task)}`);
}

function wallaceApprovalLine(item, tasks) {
  const related = asArray(item.related_tasks)
    .map((taskId) => {
      const task = taskById(tasks, taskId);
      return task ? `${taskId} ${task.task_name}` : taskId;
    })
    .join("; ");
  return `${item.reason}: ${related}`;
}

function providerBoundaryLine(line) {
  return line.endsWith(".") ? line.slice(0, -1) : line;
}

function buildBrief() {
  const middleBoard = readJson("boards/middle-next-50-task-board.json", {
    execution_order: {},
    tasks: [],
    tasks_blocked_only_by_provider_access: [],
    tasks_that_truly_require_wallace: []
  });
  const middleMap = readJson("ai-execution/middle-agent-execution-map.json", {
    first_actions_for_agents: [],
    provider_boundaries: []
  });
  const money = readJson("revenue/money-scoreboard.json");
  const nextActions = asArray(readJson("ai-execution/ai-next-actions.json").next_actions);
  const campaignBoard = asArray(readJson("boards/master-campaign-board.json").campaigns);
  const sendQueue = asArray(readJson("outbound/autonomous-send-queue.json").items);
  const dmBatches = asArray(readJson("outbound/dm-draft-queue.json").draft_batches);
  const emailQueue = asArray(readJson("outbound/email-send-queue.json").items);
  const followUpSendQueue = asArray(readJson("outbound/follow-up-send-queue.json").items);
  const inboundQueue = asArray(readJson("inbound/inbound-response-queue.json").items);
  const escalations = asArray(readJson("communications/wallace-approval-queue.json").approval_items);
  const webhook = readJson("product/webhook-status.json", { tracked_webhooks: [] });
  const checkout = readJson("product/checkout-status.json", { known_blockers: [] });
  const revenueOpps = asArray(readJson("revenue/revenue-opportunities.json").opportunities);
  const leadPipeline = readJson("leads/unified-lead-pipeline.json", { leads: [] });
  const followUpQueue = readJson("leads/follow-up-queue.json", { items: [] });

  const allMiddleTasks = asArray(middleBoard.tasks);
  const todaysTasks = orderedTasks(middleBoard, "next_10_tasks");
  const sprintTasks = orderedTasks(middleBoard, "todays_20_task_sprint");
  const readyToday = topReadyTasks(todaysTasks, 10);
  const nextClientTask = readyToday[0] || topReadyTasks(allMiddleTasks, 1)[0];

  const autonomousReady = nextActions.filter((item) => item.action_mode === "autonomous_now");
  const integrationBlocked = [
    ...campaignBoard.filter((item) => String(item.autonomy_status || item.status).includes("blocked")),
    ...sendQueue.filter((item) => item.status === "failed_provider_block"),
    ...emailQueue.filter((item) => item.status === "failed_provider_block")
  ];
  const allowedCampaigns = campaignBoard.filter((item) =>
    ["active", "generation_allowed"].includes(item.status) ||
    ["allowed_after_real_lead_and_provider_check", "partially_autonomous", "autonomous_for_non_sensitive_followups", "generation_allowed"].includes(item.autonomy_status)
  );
  const pausedCampaigns = campaignBoard.filter((item) => ["blocked", "critical"].includes(item.status) || String(item.autonomy_status || "").includes("blocked"));
  const leadsMoveable = sendQueue.filter((item) => item.status === "ready_for_agent_research" || item.status === "ready_to_generate");
  const inboundAuto = inboundQueue.filter((item) => item.autonomous_reply_allowed && item.policy_check_result !== "escalate");
  const followupsAuto = followUpSendQueue.filter((item) => item.send_allowed && !item.escalation_required);
  const warmFollowups = asArray(followUpQueue.items).filter((item) => item.status !== "archived");
  const activePipeline = asArray(leadPipeline.leads).filter((item) => item.stage !== "lost");
  const systemProof = asArray(money.system_proof);

  return {
    middleBoard,
    middleMap,
    money,
    todaysTasks,
    sprintTasks,
    readyToday,
    nextClientTask,
    autonomousReady,
    integrationBlocked,
    allowedCampaigns,
    pausedCampaigns,
    leadsMoveable,
    inboundAuto,
    followupsAuto,
    warmFollowups,
    activePipeline,
    escalations,
    revenueOpps,
    sendQueue,
    dmBatches,
    webhook,
    checkout,
    allMiddleTasks,
    systemProof
  };
}

function printBrief(brief) {
  const {
    middleBoard,
    middleMap,
    money,
    todaysTasks,
    sprintTasks,
    readyToday,
    nextClientTask,
    autonomousReady,
    integrationBlocked,
    allowedCampaigns,
    pausedCampaigns,
    leadsMoveable,
    inboundAuto,
    followupsAuto,
    warmFollowups,
    activePipeline,
    escalations,
    revenueOpps,
    sendQueue,
    dmBatches,
    webhook,
    checkout,
    allMiddleTasks,
    systemProof
  } = brief;

  console.log("CTOS Daily Revenue Execution Brief");
  console.log("==================================");
  console.log("Operating question: What can AI agents do next for Wallace to get clients, revenue, meetings, content, follow-ups, and proof?");
  console.log(`Execution model: ${middleBoard.principle || "AI-agent revenue execution map"}`);
  console.log(`Target MRR: $${money.target_mrr ?? 10000}`);
  console.log(`Confirmed MRR: $${money.current_confirmed_mrr ?? 0}`);
  console.log(`Expected pipeline MRR: $${money.expected_pipeline_mrr ?? 0}`);
  console.log(`Active pipeline records: ${activePipeline.length}`);
  console.log(`Warm follow-up records: ${warmFollowups.length}`);
  console.log(`Top AI money action: ${money.top_ai_action_likely_to_create_money_next || "None recorded."}`);

  printSection(
    "1. Highest-priority revenue tasks today",
    todaysTasks.slice(0, 10).map(taskLine)
  );

  printSection(
    "2. AI can do this without Wallace manually working",
    readyToday.map((task) => `${lineStatus(task)}. Produce/update: ${asArray(task.output_files).join(", ") || "local CTOS artifact"}`)
  );

  printSection(
    "3. Wallace approval or human judgment needed",
    [
      ...asArray(middleBoard.tasks_that_truly_require_wallace).map((item) => wallaceApprovalLine(item, allMiddleTasks)),
      ...escalations.map((item) => `${item.approval_id}: ${item.target_lead_or_business} - ${item.why_policy_cannot_handle_it}`)
    ]
  );

  printSection(
    "4. Follow-up, outreach, content, and pipeline actions next",
    [
      ...categoryNextTasks(sprintTasks, ["instagram", "dm", "outbound", "lead research", "call-list", "email", "facebook"], 5).map((line) => `Outreach: ${line}`),
      ...categoryNextTasks(sprintTasks, ["follow-up", "warm", "referral", "jay", "chuck"], 4).map((line) => `Follow-up: ${line}`),
      ...categoryNextTasks(sprintTasks, ["content", "facebook advice", "caption", "post"], 3).map((line) => `Content: ${line}`),
      ...categoryNextTasks(sprintTasks, ["inbound", "lead stage", "scoreboard", "demo", "checkout", "pipeline"], 5).map((line) => `Pipeline: ${line}`)
    ]
  );

  printSection(
    "5. Blocked or waiting",
    [
      ...asArray(middleBoard.tasks_blocked_only_by_provider_access).map((item) => `${item.task_id}: ${item.task_name} - ${item.provider_tool_needed}; ${item.blocker}`),
      ...integrationBlocked.map((item) => item.queue_id ? queueLine(item) : campaignLine(item)),
      ...asArray(middleMap.provider_boundaries).map((line) => `Boundary: ${providerBoundaryLine(line)}`)
    ]
  );

  printSection(
    "6. Agent-specific first actions",
    asArray(middleMap.first_actions_for_agents).map((item) => `${item.owner_agent}: ${item.task_id} ${item.task_name} [${item.status}]`)
  );

  printSection(
    "7. Next best action to get a client",
    nextClientTask ? [
      `${nextClientTask.task_id}: ${nextClientTask.task_name} (${nextClientTask.owner_agent})`,
      `Why it matters: ${shortText(nextClientTask.revenue_connection)}`,
      `Do next: ${firstStep(nextClientTask)}`
    ] : []
  );

  printSection(
    "8. Existing autonomous actions agents can execute now",
    autonomousReady.slice(0, 10).map((item) => `${item.owner_agent}: ${item.next_ai_action} [escalation only if: ${item.escalation_only_if || "policy exception"}]`)
  );

  printSection(
    "9. Campaigns currently allowed to run",
    allowedCampaigns.map(campaignLine)
  );

  printSection(
    "10. Campaigns paused by policy, provider, or rate limit",
    pausedCampaigns.map(campaignLine)
  );

  printSection(
    "11. Leads agents can move forward without Wallace",
    leadsMoveable.map(queueLine)
  );

  printSection(
    "12. Inbound replies agents can answer automatically",
    inboundAuto.map((item) => `${item.queue_id}: ${item.business_name} / ${item.intent} - ${item.next_best_ai_action}`)
  );

  printSection(
    "13. Follow-ups agents can send automatically",
    followupsAuto.map(queueLine)
  );

  printSection(
    "14. Revenue opportunities closest to money",
    revenueOpps.map((item) => `${item.owner_agent}: ${item.title} [${item.action_mode}] - ${item.next_ai_action}`)
  );

  printSection(
    "15. System proof: what AI handled without Wallace",
    [
      ...systemProof,
      `${todaysTasks.length} board-ranked daily revenue tasks loaded from the Middle 50 board.`,
      `${readyToday.length} top daily tasks are AI-workable without Wallace or provider mutation.`,
      `${sendQueue.length} outbound queue items policy-modeled without sends.`,
      `${dmBatches.reduce((sum, batch) => sum + asArray(batch.drafts).length, 0)} DM seed drafts are blocked from send until real leads exist.`,
      `${asArray(webhook.tracked_webhooks).filter((item) => item.autonomous_allowed).length} webhook/provider paths are marked autonomous-capable in CTOS state.`,
      `${asArray(checkout.known_blockers).length} checkout blocker(s) tracked without touching pricing/checkout files.`
    ]
  );
}

function main() {
  printBrief(buildBrief());
}

if (require.main === module) {
  main();
}

module.exports = {
  buildBrief,
  printBrief
};
