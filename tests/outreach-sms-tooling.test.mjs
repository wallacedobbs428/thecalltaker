import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { renderApprovalPacket, SMS_APPROVAL_NO_SEND_MODE } from "../tools/outreach/generate_sms_approval_packet.mjs";
import { generateSmsPreview, renderSmsPreview, SMS_PREVIEW_NO_SEND_MODE } from "../tools/outreach/generate_sms_preview.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const status = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/outreach/sms_approval_status.json"), "utf8"));
const templates = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/outreach/sms_templates.json"), "utf8"));

const prospect = {
  first_name: "Sam",
  company: "Example HVAC",
  industry: "hvac",
  call_path_note: "after-hours calls appear to hit voicemail",
};

test("SMS tooling stays no-send", () => {
  assert.equal(SMS_APPROVAL_NO_SEND_MODE, true);
  assert.equal(SMS_PREVIEW_NO_SEND_MODE, true);
  assert.equal(status.no_send_mode, true);
});

test("approval packet renders operator-ready provider language", () => {
  const packet = renderApprovalPacket(status, templates);

  assert.match(packet, /Status: Not approved for live SMS/);
  assert.match(packet, /A2P\/10DLC: not_submitted/);
  assert.match(packet, /Cold SMS, bulk SMS, and automated sequences stay blocked/);
  assert.match(packet, /hey \{first_name\}/);
});

test("warm SMS preview renders drafts but never allows sending", () => {
  const preview = generateSmsPreview({ scenario: "after_demo", prospect, status, templates });
  const rendered = renderSmsPreview(preview);

  assert.equal(preview.gate, "review_only");
  assert.equal(preview.send_allowed, false);
  assert.match(rendered, /Send allowed: no/);
  assert.match(rendered, /Example HVAC/);
  assert.match(rendered, /nothing goes live from the demo/);
});

test("cold SMS preview is blocked until provider approval", () => {
  const preview = generateSmsPreview({ scenario: "cold_candidate", prospect, status, templates });

  assert.equal(preview.gate, "blocked_provider_approval_required");
  assert.equal(preview.send_allowed, false);
  assert.ok(preview.messages.some((message) => message.includes("reply stop")));
});

test("approved status still keeps generator no-send", () => {
  const approvedStatus = {
    ...status,
    status: "approved",
    provider_submission: {
      ...status.provider_submission,
      provider_approval_verified: true,
    },
  };
  const preview = generateSmsPreview({ scenario: "cold_candidate", prospect, status: approvedStatus, templates });

  assert.equal(preview.gate, "approved_review_required");
  assert.equal(preview.send_allowed, false);
});

test("templates avoid live-routing claims outside explicit blocked examples", () => {
  const templateText = JSON.stringify(templates);

  assert.doesNotMatch(templateText, /your AI is live/i);
  assert.doesNotMatch(templateText, /call forwarding is active/i);
  assert.doesNotMatch(templateText, /guaranteed booked jobs/i);
  assert.doesNotMatch(templateText, /calling you now/i);
});
