import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { ACTION_BOARD_NO_SEND_MODE, buildActionBoard, renderActionBoard } from "../tools/command-center/wallace_action_board.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");

const paths = {
  prospectsPath: path.join(repoRoot, "tools/outreach/sample_prospects.json"),
  smsStatusPath: path.join(repoRoot, "tools/outreach/sms_approval_status.json"),
  smsTemplatesPath: path.join(repoRoot, "tools/outreach/sms_templates.json"),
  creativeAssetsPath: path.join(repoRoot, "tools/creative/creative_assets.sample.json"),
};

test("Wallace action board stays no-send and no-post", () => {
  assert.equal(ACTION_BOARD_NO_SEND_MODE, true);
});

test("builds combined prospect, SMS, and creative board", () => {
  const board = buildActionBoard(paths);

  assert.ok(board.scoredProspects.length > 0);
  assert.ok((board.prospectCounts.A || 0) > 0);
  assert.equal(board.smsStatus.status, "blocked");
  assert.ok(board.scoredCreatives.length > 0);
  assert.ok(board.organicReady.length > 0);
});

test("renders SMS gates without allowing sends", () => {
  const board = buildActionBoard(paths);
  const rendered = renderActionBoard(board);

  assert.match(rendered, /SMS status: Not approved for live SMS/);
  assert.match(rendered, /SMS draft allowed to send: no/);
  assert.match(rendered, /Status: local no-send\/no-post command output/);
});

test("renders creative verdicts", () => {
  const rendered = renderActionBoard(buildActionBoard(paths));

  assert.match(rendered, /Organic:/);
  assert.match(rendered, /Paid:/);
  assert.match(rendered, /Hard fails:/);
});

test("sample board contains no real private prospect domains", () => {
  const sample = fs.readFileSync(paths.prospectsPath, "utf8");
  const domains = Array.from(sample.matchAll(/[a-z0-9.-]+\.[a-z]{2,}/gi)).map((match) => match[0].toLowerCase());
  domains.forEach((domain) => {
    assert.ok(domain === "example.invalid" || domain.endsWith(".example.invalid"), `${domain} should be fake`);
  });
});
