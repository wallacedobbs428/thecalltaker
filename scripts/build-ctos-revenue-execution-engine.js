#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");

const repoRoot = path.join(__dirname, "..");
const ctosRoot = path.join(repoRoot, "ctos");
const middleRefreshRoot = path.join(
  os.homedir(),
  "Developer",
  "business-brain",
  "outreach-system",
  "revenue-command-center",
  "middle-command-refresh"
);

const noSendMode = {
  status: "active",
  allowed: [
    "draft",
    "classify",
    "prioritize",
    "prepare_approval_packets",
    "prepare_local_ctos_outputs",
    "recommend_lead_stage_updates"
  ],
  forbidden: [
    "send_dm",
    "send_email",
    "send_sms",
    "place_call",
    "send_webhook",
    "post_publicly",
    "mutate_provider",
    "deploy",
    "read_env"
  ],
  rule: "CTOS may prepare revenue actions locally, but no external communication or provider mutation is allowed from this engine."
};

function readJson(relativePath, fallback = {}) {
  try {
    return JSON.parse(fs.readFileSync(path.join(ctosRoot, relativePath), "utf8"));
  } catch (error) {
    return fallback;
  }
}

function readText(filePath, fallback = "") {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch (error) {
    return fallback;
  }
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function slug(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

function cleanMarkdown(value) {
  return String(value || "")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .trim();
}

function cleanTableCell(value) {
  return String(value || "")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .trim();
}

function stripInlineContact(value) {
  return String(value || "").replace(/\s*`[^`]+`\s*/g, " ").replace(/\s+/g, " ").trim();
}

function parseMarkdownTableAfter(markdown, heading) {
  const start = markdown.indexOf(heading);
  if (start === -1) return [];
  const lines = markdown.slice(start).split(/\r?\n/);
  const tableLines = [];
  let foundTable = false;
  for (const line of lines) {
    if (line.trim().startsWith("|")) {
      foundTable = true;
      tableLines.push(line.trim());
      continue;
    }
    if (foundTable && tableLines.length) break;
  }
  if (tableLines.length < 2) return [];

  const headers = tableLines[0]
    .split("|")
    .slice(1, -1)
    .map((header) => cleanMarkdown(header).toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, ""));

  return tableLines.slice(2).map((line) => {
    const cells = line.split("|").slice(1, -1).map(cleanTableCell);
    return headers.reduce((record, header, index) => {
      record[header] = cells[index] || "";
      return record;
    }, {});
  }).filter((record) => Object.values(record).some(Boolean));
}

function taskById(tasks, taskId) {
  return asArray(tasks).find((task) => task.task_id === taskId);
}

function firstStep(task) {
  return asArray(task && task.exact_execution_steps)[0] || "Prepare the next local CTOS artifact.";
}

function m50LinksForFollowup(leadId) {
  if (leadId === "lead-chuck-mcdowell") return ["M50-006", "M50-007", "M50-014"];
  if (leadId === "lead-jay-grosman") return ["M50-006", "M50-008", "M50-014"];
  if (leadId === "lead-freedom-diagnostics") return ["M50-006", "M50-014"];
  return ["M50-006", "M50-014"];
}

function buildApprovalPackets(followUpQueue, pipeline, hotLeads) {
  const pipelineById = new Map(asArray(pipeline.leads).map((lead) => [lead.lead_id, lead]));
  const hotById = new Map(asArray(hotLeads.items).map((lead) => [lead.lead_id, lead]));

  return asArray(followUpQueue.items).map((item) => {
    const lead = pipelineById.get(item.lead_id) || {};
    const hot = hotById.get(item.lead_id) || {};
    const approvalNeeded = Boolean(item.approval_required || lead.approval_needed || item.status === "escalated");
    return {
      packet_id: `approval-${slug(item.lead_id || item.business_name)}`,
      lead_id: item.lead_id,
      lead_name: item.business_name,
      business_type: lead.category || "needs_review",
      source: item.source || lead.source || hot.source || "needs_review",
      pain_or_opportunity: item.evidence || hot.reason_hot || lead.notes || "needs_review",
      recommended_next_action: item.ai_next_action || lead.next_ai_action || hot.next_ai_action || "Prepare sourced review packet.",
      draft_message_or_call_angle: item.draft_next_touch || "No draft queued until source context is complete.",
      wallace_approval_needed: approvalNeeded,
      wallace_approval_reason: approvalNeeded ? (lead.next_wallace_decision || hot.wallace_needed_for || "Relationship-sensitive or incomplete-context follow-up.") : "No Wallace approval needed if policy and provider gates pass.",
      status: item.status || lead.stage || "needs_review",
      next_follow_up_date: item.next_touch_date || "needs_review",
      next_stage_if_approved: item.stage_if_approved || item.stage_if_policy_or_escalation_clears || lead.stage || "needs_review",
      no_send_mode: noSendMode.status,
      send_allowed: false,
      m50_task_links: m50LinksForFollowup(item.lead_id)
    };
  });
}

function buildDemoProspects() {
  const demoPath = path.join(middleRefreshRoot, "DEMO-RESULT-PROSPECT-CALL-READY-SHEETS-2026-06-01.md");
  const hotPath = path.join(middleRefreshRoot, "HOT-CTOS-LEADS-TOP-5-2026-06-01.md");
  const demoMarkdown = readText(demoPath);
  const hotMarkdown = readText(hotPath);
  const demoRows = parseMarkdownTableAfter(demoMarkdown, "## Queue Snapshot");
  const hotRows = parseMarkdownTableAfter(hotMarkdown, "## Ranked Queue");

  const queue = demoRows.map((row) => {
    const rawProspect = row.prospect || "";
    const businessName = stripInlineContact(rawProspect);
    return {
      action_id: `demo-result-rank-${row.rank}-${slug(businessName)}`,
      lead_name: businessName,
      business_type: inferBusinessType(businessName),
      source_groups: ["demo_result_prospect"],
      source: demoPath,
      source_rank: Number(row.rank),
      source_contact_available: true,
      source_contact_policy: "Contact detail exists only in the source sheet; this CTOS queue keeps contact execution manual and no-send.",
      stage: row.stage || "needs_review",
      close_step: row.close_step || "needs_review",
      market: inferMarket(businessName, row),
      payment_status: row.payment || "needs_review",
      recommended_next_action: row.middle_next_action || "Prepare no-send follow-up packet.",
      draft_message_or_call_angle: noSendDraftFor(row, businessName),
      wallace_approval_needed: true,
      status: row.close_step === "demo_called" ? "wallace_personal_follow_up_ready" : "no_send_draft_ready",
      next_follow_up_date: row.close_step === "demo_called" ? "today_or_next_available_wallace_slot" : "needs_wallace_approval",
      send_allowed: false,
      no_send_mode: noSendMode.status,
      m50_task_links: ["M50-004", "M50-006", "M50-014"]
    };
  });

  for (const hotRow of hotRows) {
    const hotName = stripInlineContact(hotRow.prospect || "");
    const match = queue.find((item) => item.lead_name === hotName && !item.hot_ctos_rank);
    if (match) {
      match.source_groups.push("hot_ctos_top_5");
      match.hot_ctos_rank = Number(hotRow.rank);
      match.ctos_probability = Number(hotRow.ctos_probability) || null;
      match.tier_fit = hotRow.tier_fit || "needs_review";
      match.hot_next_safe_step = hotRow.next_safe_step || match.recommended_next_action;
      match.recommended_next_action = hotRow.next_safe_step || match.recommended_next_action;
    }
  }

  return queue;
}

function inferBusinessType(name) {
  const text = String(name || "").toLowerCase();
  if (text.includes("roof")) return "roofing";
  if (text.includes("water")) return "water_damage";
  if (text.includes("lock")) return "locksmith";
  if (text.includes("tow")) return "towing";
  return "needs_review";
}

function inferMarket(name, row) {
  const text = `${name} ${JSON.stringify(row)}`.toLowerCase();
  if (text.includes("huntsville")) return "Huntsville, AL";
  if (text.includes("san antonio")) return "San Antonio, TX";
  if (text.includes("jacksonville")) return "Jacksonville, FL";
  if (text.includes("memphis")) return "Memphis, TN";
  if (text.includes("austin")) return "Austin, TX";
  if (text.includes("tow pro")) return "Nashville, TN";
  return "needs_review";
}

function noSendDraftFor(row, businessName) {
  if (row.close_step === "demo_called") {
    return "Ask what happened when they tried Gideon, what felt useful or failed, and whether one captured missed job would cover month one.";
  }
  const type = inferBusinessType(businessName);
  if (type === "roofing") return "No-send draft angle: ask whether they called Gideon with a roof leak scenario and whether the handoff would catch a missed roofing job.";
  if (type === "water_damage") return "No-send draft angle: ask whether they tested Gideon with an urgent water-damage scenario and whether the handoff captured the emergency clearly.";
  if (type === "locksmith") return "No-send draft angle: ask whether they tested Gideon with a lockout scenario and whether the handoff captured the job cleanly.";
  if (type === "towing") return "No-send draft angle: ask whether they tested Gideon with a roadside breakdown scenario and whether the handoff captured location and need.";
  return "No-send draft angle: ask whether they tested Gideon and what outcome should be logged.";
}

function buildLeadActionQueue(demoProspects, approvalPackets) {
  const approvalActions = approvalPackets.map((packet) => ({
    action_id: `warm-packet-${slug(packet.lead_id)}`,
    lead_name: packet.lead_name,
    business_type: packet.business_type,
    source_groups: ["ctos_warm_follow_up"],
    source: packet.source,
    source_rank: null,
    source_contact_available: false,
    source_contact_policy: "Use existing relationship context only; no external send from CTOS.",
    stage: packet.status,
    close_step: packet.next_stage_if_approved,
    market: "needs_review",
    payment_status: "not_sent",
    recommended_next_action: packet.recommended_next_action,
    draft_message_or_call_angle: packet.draft_message_or_call_angle,
    wallace_approval_needed: packet.wallace_approval_needed,
    status: "approval_packet_ready",
    next_follow_up_date: packet.next_follow_up_date,
    send_allowed: false,
    no_send_mode: noSendMode.status,
    m50_task_links: packet.m50_task_links,
    approval_packet_id: packet.packet_id
  }));

  return {
    queue_id: "ctos-local-lead-action-queue-2026-06-01",
    generated_at: "2026-06-01",
    mode: "local_no_send",
    no_send_mode: noSendMode,
    source_policy: "Only source-backed records from CTOS and MIDDLE command files are included. Contact details stay in source sheets; this queue does not authorize sends or calls.",
    summary: {
      demo_result_prospects: demoProspects.length,
      hot_ctos_top_5_overlaps: demoProspects.filter((item) => item.source_groups.includes("hot_ctos_top_5")).length,
      warm_approval_packets: approvalActions.length,
      sends_allowed: 0
    },
    items: [...demoProspects, ...approvalActions]
  };
}

function buildFirstAdWorkflow(board) {
  return {
    workflow_id: "first-ad-inbound-capture-workflow-2026-06-01",
    generated_at: "2026-06-01",
    mode: "local_no_send",
    no_send_mode: noSendMode,
    owner_agent: "Ad Capture Agent",
    m50_task_links: ["M50-001", "M50-005", "M50-009", "M50-013", "M50-023", "M50-035"],
    required_right_handoff_fields: [
      "final_caption",
      "cta_wording",
      "post_or_ad_url",
      "target_segment",
      "expected_comment_prompts",
      "launch_status"
    ],
    reply_classification_flow: [
      {
        inbound_signal: "asks_what_it_does",
        classification: "education_request",
        lane_owner: "Inbound Agent",
        ai_next_action: "Draft simple explanation and offer Gideon demo path locally.",
        wallace_approval_required: false,
        next_pipeline_stage: "AI_reply_drafted"
      },
      {
        inbound_signal: "asks_for_website_or_demo",
        classification: "demo_interest",
        lane_owner: "Inbound Agent",
        ai_next_action: "Prepare demo link/Call Gideon Live reply draft; do not send.",
        wallace_approval_required: false,
        next_pipeline_stage: "demo_sent"
      },
      {
        inbound_signal: "basic_pricing_question",
        classification: "pricing_interest",
        lane_owner: "Revenue Scoreboard Agent",
        ai_next_action: "Prepare sourced $97/$497/$997 pricing explanation draft; escalate custom pricing.",
        wallace_approval_required: false,
        next_pipeline_stage: "interested"
      },
      {
        inbound_signal: "booking_or_setup_interest",
        classification: "meeting_or_setup_review",
        lane_owner: "Follow-Up Agent",
        ai_next_action: "Create approval packet with context, recommended setup-review next step, and outcome log slot.",
        wallace_approval_required: true,
        next_pipeline_stage: "meeting_suggested"
      },
      {
        inbound_signal: "proof_request",
        classification: "proof_needed",
        lane_owner: "CTOS Data Agent",
        ai_next_action: "Prepare proof-safe response draft using only approved public/source-backed proof.",
        wallace_approval_required: true,
        next_pipeline_stage: "interested"
      },
      {
        inbound_signal: "angry_sensitive_legal_contract_payment",
        classification: "sensitive_exception",
        lane_owner: "LEFT / Wallace escalation",
        ai_next_action: "Hold and escalate; no reply draft leaves CTOS.",
        wallace_approval_required: true,
        next_pipeline_stage: "escalated"
      },
      {
        inbound_signal: "not_interested",
        classification: "polite_closeout",
        lane_owner: "Inbound Agent",
        ai_next_action: "Draft polite close-out and mark follow_up_later or lost after approval rules pass.",
        wallace_approval_required: false,
        next_pipeline_stage: "follow_up_later"
      },
      {
        inbound_signal: "spam_or_irrelevant",
        classification: "archive",
        lane_owner: "Inbound Agent",
        ai_next_action: "Mark spam/irrelevant in local queue.",
        wallace_approval_required: false,
        next_pipeline_stage: "lost"
      }
    ],
    after_booking_interest: {
      create_approval_packet: true,
      required_fields: [
        "lead_name",
        "source",
        "reply_summary",
        "requested_next_step",
        "recommended_offer_tier",
        "risk_flags",
        "suggested_follow_up_date"
      ],
      next_safe_action: "Wallace reviews setup-review or meeting request before any external send, call, payment link, or provider action."
    },
    board_task_context: ["M50-001", "M50-005", "M50-009"].map((taskId) => {
      const task = taskById(board.tasks, taskId);
      return {
        task_id: taskId,
        task_name: task ? task.task_name : "missing",
        owner_agent: task ? task.owner_agent : "unknown",
        output_files: task ? asArray(task.output_files) : []
      };
    })
  };
}

function buildDailyOutput({ board, executionMap, approvalPackets, leadActionQueue, firstAdWorkflow }) {
  const tasks = asArray(board.tasks);
  const top5 = asArray(board.execution_order && board.execution_order.next_5_tasks).map((taskId) => {
    const task = taskById(tasks, taskId);
    return {
      task_id: taskId,
      task_name: task ? task.task_name : "missing",
      owner_agent: task ? task.owner_agent : "unknown",
      status: task ? task.status : "unknown",
      ai_agent_owned: Boolean(task && task.autonomous_now),
      provider_required: Boolean(task && task.provider_required),
      no_send_mode: noSendMode.status,
      engine_output: engineOutputForTask(taskId),
      next_action: task ? firstStep(task) : "Review task source."
    };
  });

  return {
    brief_id: "ctos-daily-revenue-execution-output-2026-06-01",
    generated_at: "2026-06-01",
    mode: "local_no_send",
    no_send_mode: noSendMode,
    operating_question: "What can AI agents do next for Wallace to get clients, revenue, meetings, follow-ups, content, and proof?",
    data_gaps_preventing_full_action_system: [
      "No source-backed Instagram/local leads are confirmed in CTOS for M50-003; current send queues contain placeholders.",
      "Instagram inbound POST and outbound DM runtime proof are not confirmed.",
      "RIGHT final first-ad CTA/caption handoff is not yet attached to the Middle capture loop.",
      "Warm lead exact dates and relationship context remain incomplete for some packets.",
      "Huntsville Roofing outcome is not logged yet; CTOS cannot move the close path until Wallace records the real result.",
      "Instantly and Facebook posting remain provider/platform blocked.",
      "Square/payment changes are tracked only; CTOS does not mutate provider dashboards."
    ],
    persistent_outputs: [
      "ctos/revenue/daily-revenue-execution-output.json",
      "ctos/revenue/warm-lead-approval-packets.json",
      "ctos/revenue/lead-action-queue.json",
      "ctos/revenue/first-ad-inbound-capture-workflow.json"
    ],
    top_5_revenue_actions: top5,
    approval_packets_ready: {
      count: approvalPackets.length,
      packet_ids: approvalPackets.map((packet) => packet.packet_id),
      wallace_required_count: approvalPackets.filter((packet) => packet.wallace_approval_needed).length
    },
    blocked_actions: [
      ...asArray(board.tasks_blocked_only_by_provider_access).map((item) => ({
        id: item.task_id,
        name: item.task_name,
        blocker: item.blocker,
        provider_tool_needed: item.provider_tool_needed
      })),
      ...asArray(executionMap.provider_boundaries).map((boundary, index) => ({
        id: `provider-boundary-${index + 1}`,
        name: "Provider boundary",
        blocker: boundary,
        provider_tool_needed: "do_not_mutate_provider"
      }))
    ],
    wallace_only_actions: [
      {
        action_id: "wallace-huntsville-roofing-follow-up",
        lead_name: "Huntsville Roofing Company",
        why_wallace: "Only demo/result prospect marked demo_called; founder trust moment, not an automation send.",
        next_action: "Ask what happened when they tried Gideon, what worked/failed, and whether one captured missed roofing job covers month one.",
        source: path.join(middleRefreshRoot, "WALLACE-FIRST-PERSONAL-FOLLOW-UP-CARD-2026-06-01.md"),
        send_allowed_from_ctos: false
      },
      ...approvalPackets.filter((packet) => packet.wallace_approval_needed).map((packet) => ({
        action_id: packet.packet_id,
        lead_name: packet.lead_name,
        why_wallace: packet.wallace_approval_reason,
        next_action: packet.recommended_next_action,
        source: packet.source,
        send_allowed_from_ctos: false
      }))
    ],
    ai_agent_owned_actions: top5
      .filter((task) => task.ai_agent_owned)
      .map((task) => ({
        task_id: task.task_id,
        owner_agent: task.owner_agent,
        next_action: task.next_action,
        output: task.engine_output
      })),
    next_best_client_getting_action: {
      action_id: "wallace-huntsville-roofing-follow-up",
      owner: "Wallace with Follow-Up Agent support",
      ai_support_owner: "Follow-Up Agent",
      lead_name: "Huntsville Roofing Company",
      reason: "Strongest near-money record because the MIDDLE command sheet marks it demo_sent with close_step demo_called.",
      next_action: "Wallace personally asks what happened when they tried Gideon and logs the outcome before any setup, payment link, or provider action.",
      ctOS_local_support: [
        "approval packet ready",
        "lead action queue entry ready",
        "no-send outcome logging next step identified"
      ],
      send_allowed_from_ctos: false
    },
    lead_action_queue_summary: leadActionQueue.summary,
    first_ad_capture_summary: {
      workflow_id: firstAdWorkflow.workflow_id,
      reply_categories: firstAdWorkflow.reply_classification_flow.length,
      booking_interest_creates_approval_packet: firstAdWorkflow.after_booking_interest.create_approval_packet
    }
  };
}

function engineOutputForTask(taskId) {
  const outputs = {
    "M50-001": "ctos/revenue/first-ad-inbound-capture-workflow.json",
    "M50-002": "ctos/revenue/lead-action-queue.json",
    "M50-003": "ctos/revenue/lead-action-queue.json",
    "M50-004": "ctos/revenue/warm-lead-approval-packets.json",
    "M50-005": "ctos/revenue/first-ad-inbound-capture-workflow.json"
  };
  return outputs[taskId] || "ctos/revenue/daily-revenue-execution-output.json";
}

function writeJson(relativePath, value) {
  const filePath = path.join(ctosRoot, relativePath);
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
  return filePath;
}

function main() {
  const board = readJson("boards/middle-next-50-task-board.json", { tasks: [], execution_order: {} });
  const executionMap = readJson("ai-execution/middle-agent-execution-map.json", { provider_boundaries: [] });
  const followUpQueue = readJson("leads/follow-up-queue.json", { items: [] });
  const pipeline = readJson("leads/unified-lead-pipeline.json", { leads: [] });
  const hotLeads = readJson("leads/hot-leads.json", { items: [] });

  const approvalPackets = buildApprovalPackets(followUpQueue, pipeline, hotLeads);
  const demoProspects = buildDemoProspects();
  const leadActionQueue = buildLeadActionQueue(demoProspects, approvalPackets);
  const firstAdWorkflow = buildFirstAdWorkflow(board);
  const dailyOutput = buildDailyOutput({ board, executionMap, approvalPackets, leadActionQueue, firstAdWorkflow });

  const written = [
    writeJson("revenue/warm-lead-approval-packets.json", {
      packet_set_id: "warm-lead-approval-packets-2026-06-01",
      generated_at: "2026-06-01",
      mode: "local_no_send",
      no_send_mode: noSendMode,
      packets: approvalPackets
    }),
    writeJson("revenue/lead-action-queue.json", leadActionQueue),
    writeJson("revenue/first-ad-inbound-capture-workflow.json", firstAdWorkflow),
    writeJson("revenue/daily-revenue-execution-output.json", dailyOutput)
  ];

  console.log("CTOS revenue execution engine built:");
  written.forEach((filePath) => console.log(`- ${path.relative(repoRoot, filePath)}`));
}

if (require.main === module) {
  main();
}

module.exports = {
  buildApprovalPackets,
  buildDailyOutput,
  buildDemoProspects,
  buildFirstAdWorkflow,
  buildLeadActionQueue,
  noSendMode,
  parseMarkdownTableAfter
};
