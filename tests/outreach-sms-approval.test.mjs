import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const approvalPath = path.join(repoRoot, "docs/outreach-sms-approval-packet.md");
const copyPath = path.join(repoRoot, "docs/outreach-sms-copy-bank.md");

function read(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

test("SMS approval packet keeps live sending blocked", () => {
  const packet = read(approvalPath).toLowerCase();

  assert.match(packet, /no sms sending is enabled/);
  assert.match(packet, /cold sms remains blocked/);
  assert.match(packet, /not approved for live sms/);
});

test("SMS packet includes identity, opt-out, and help handling", () => {
  const packet = read(approvalPath);

  assert.match(packet, /Wallace with The Call Taker/);
  assert.match(packet, /reply stop/i);
  assert.match(packet, /HELP/);
  assert.match(packet, /STOP/);
});

test("SMS docs reject fake-live and unsupported claims", () => {
  const combined = `${read(approvalPath)}\n${read(copyPath)}`;
  const forbiddenClaims = [
    "Your AI receptionist is live.",
    "Call forwarding is active.",
    "We guarantee more booked jobs.",
    "Calling you now.",
  ];

  forbiddenClaims.forEach((claim) => {
    assert.match(combined, new RegExp(claim.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  });

  assert.match(combined, /Do not use/i);
  assert.match(combined, /Not allowed/i);
});

test("human SMS style is documented without enabling sends", () => {
  const copy = read(copyPath);

  assert.match(copy, /less polished than email/);
  assert.match(copy, /hey \[First Name\]/);
  assert.match(copy, /not live call routing yet/);
});
