import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SMS_APPROVAL_NO_SEND_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const statusPath = path.join(__dirname, "sms_approval_status.json");
const templatesPath = path.join(__dirname, "sms_templates.json");
const outputPath = path.join(__dirname, "output", "sms-approval-packet.sample.md");

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function renderList(items) {
  return items.map((item) => `- ${item}`).join("\n");
}

export function renderApprovalPacket(status, templates) {
  if (SMS_APPROVAL_NO_SEND_MODE !== true || status.no_send_mode !== true) {
    throw new Error("SMS approval tooling must remain no-send.");
  }

  const sampleMessages = Object.entries(templates)
    .map(([key, template]) => {
      const gate = template.approval_required ? "provider approval required" : "review-only warm lead";
      const messages = template.messages.map((message) => `  - ${message}`).join("\n");
      return `### ${key}\n\nGate: ${gate}\nSource: ${template.source_required}\n\n${messages}`;
    })
    .join("\n\n");

  return `# SMS Approval Packet Render

Status: ${status.status_label}
Last reviewed: ${status.last_reviewed}
Owner: ${status.owner}
No-send mode: ${status.no_send_mode ? "true" : "false"}

## Business Use Case

The Call Taker helps local service businesses recover missed-call revenue by capturing missed or after-hours callers, qualifying what the caller needs, and preparing a reviewed handoff for the business owner or team.

SMS is intended for reviewed outreach and follow-up only. Cold SMS, bulk SMS, and automated sequences stay blocked until provider approval is verified.

## Provider Submission State

- A2P/10DLC: ${status.provider_submission.a2p_10dlc_status}
- Provider approval verified: ${status.provider_submission.provider_approval_verified}
- Campaign use case ready: ${status.provider_submission.campaign_use_case_ready}
- Sample messages ready: ${status.provider_submission.sample_messages_ready}
- Opt-out language ready: ${status.provider_submission.opt_out_language_ready}
- Help language ready: ${status.provider_submission.help_language_ready}

## Allowed Sources After Approval

${renderList(status.allowed_sources_after_approval)}

## Blocked Until Approved

${renderList(status.blocked_until_approved)}

## Required Boundaries

${renderList(status.required_boundaries)}

## Sample Messages

${sampleMessages}
`;
}

export function writeApprovalPacket(destination = outputPath) {
  const status = loadJson(statusPath);
  const templates = loadJson(templatesPath);
  const rendered = renderApprovalPacket(status, templates);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, rendered);
  return { output: destination, status: status.status, no_send_mode: SMS_APPROVAL_NO_SEND_MODE };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const result = writeApprovalPacket(process.argv[2] || outputPath);
  console.log(JSON.stringify(result, null, 2));
}
