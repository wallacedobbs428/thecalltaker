#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const repoRoot = path.join(__dirname, "..");
const ctosRoot = path.join(repoRoot, "ctos");

const files = {
  dailyOutput: "revenue/daily-revenue-execution-output.json",
  approvalPackets: "revenue/warm-lead-approval-packets.json",
  leadActionQueue: "revenue/lead-action-queue.json",
  firstAdWorkflow: "revenue/first-ad-inbound-capture-workflow.json"
};

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(ctosRoot, relativePath), "utf8"));
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertNoRawContactFields(item, context) {
  for (const field of ["phone", "email"]) {
    assert(!(field in item), `${context} must not expose raw ${field}`);
  }
}

function validate() {
  const dailyOutput = readJson(files.dailyOutput);
  const approvalPackets = readJson(files.approvalPackets);
  const leadActionQueue = readJson(files.leadActionQueue);
  const firstAdWorkflow = readJson(files.firstAdWorkflow);

  assert(dailyOutput.no_send_mode.status === "active", "daily output no-send mode must be active");
  assert(approvalPackets.no_send_mode.status === "active", "approval packets no-send mode must be active");
  assert(leadActionQueue.no_send_mode.status === "active", "lead action queue no-send mode must be active");
  assert(firstAdWorkflow.no_send_mode.status === "active", "first-ad workflow no-send mode must be active");

  assert(Array.isArray(dailyOutput.top_5_revenue_actions), "daily output must include top_5_revenue_actions");
  assert(dailyOutput.top_5_revenue_actions.length === 5, "daily output must include exactly 5 top revenue actions");
  assert(dailyOutput.next_best_client_getting_action, "daily output must include next_best_client_getting_action");
  assert(Array.isArray(dailyOutput.blocked_actions), "daily output must include blocked_actions");
  assert(Array.isArray(dailyOutput.wallace_only_actions), "daily output must include wallace_only_actions");
  assert(Array.isArray(dailyOutput.ai_agent_owned_actions), "daily output must include ai_agent_owned_actions");

  assert(Array.isArray(approvalPackets.packets), "approval packets file must include packets");
  assert(approvalPackets.packets.length >= 5, "approval packets must include at least the warm lead packet set");
  for (const packet of approvalPackets.packets) {
    for (const field of [
      "lead_name",
      "business_type",
      "source",
      "pain_or_opportunity",
      "recommended_next_action",
      "draft_message_or_call_angle",
      "wallace_approval_needed",
      "status",
      "next_follow_up_date"
    ]) {
      assert(field in packet, `approval packet ${packet.packet_id || "unknown"} missing ${field}`);
    }
    assert(packet.send_allowed === false, `approval packet ${packet.packet_id} must not be sendable`);
    assertNoRawContactFields(packet, `approval packet ${packet.packet_id}`);
  }

  assert(Array.isArray(leadActionQueue.items), "lead action queue must include items");
  assert(leadActionQueue.items.length >= 8, "lead action queue must include source-backed demo/result prospects");
  assert(leadActionQueue.summary.sends_allowed === 0, "lead action queue must allow zero sends");
  assert(leadActionQueue.items.some((item) => item.lead_name === "Huntsville Roofing Company"), "lead action queue must include Huntsville Roofing Company");
  for (const item of leadActionQueue.items) {
    assert(item.send_allowed === false, `lead action ${item.action_id} must not be sendable`);
    assertNoRawContactFields(item, `lead action ${item.action_id}`);
  }

  assert(Array.isArray(firstAdWorkflow.reply_classification_flow), "first-ad workflow must include reply_classification_flow");
  assert(firstAdWorkflow.reply_classification_flow.length >= 6, "first-ad workflow must cover the expected reply categories");
  assert(firstAdWorkflow.after_booking_interest.create_approval_packet === true, "booking interest must create approval packets");

  return {
    files_validated: Object.values(files).length,
    approval_packets: approvalPackets.packets.length,
    lead_actions: leadActionQueue.items.length,
    first_ad_reply_categories: firstAdWorkflow.reply_classification_flow.length,
    sends_allowed: leadActionQueue.summary.sends_allowed
  };
}

if (require.main === module) {
  const result = validate();
  console.log(`CTOS revenue execution engine valid: ${JSON.stringify(result)}`);
}

module.exports = { validate };
