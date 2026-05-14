import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {
  NO_SEND_MODE,
  STORAGE_MODE,
  loadProspects,
  scoreProspects,
  validateProspect,
} from "../tools/outreach/score_prospects.mjs";
import { renderDailyQueue } from "../tools/outreach/generate_daily_queue.mjs";

const samplePath = path.join(process.cwd(), "tools/outreach/sample_prospects.json");
const sampleText = fs.readFileSync(samplePath, "utf8");
const prospects = loadProspects(samplePath);
const scored = scoreProspects(prospects);
const categories = new Set(scored.map((prospect) => prospect.score_category));

assert.equal(NO_SEND_MODE, true);
assert.equal(STORAGE_MODE, "local-files-only");

assert.equal(prospects.length >= 12, true);
assert.deepEqual([...categories].sort(), ["A", "B", "C", "D"]);

const invalid = { ...prospects[0] };
delete invalid.business_name;
assert.match(validateProspect(invalid).join("\n"), /Missing required field: business_name/);

const aLead = scored.find((prospect) => prospect.score_category === "A");
const bLead = scored.find((prospect) => prospect.score_category === "B");
const cLead = scored.find((prospect) => prospect.score_category === "C");
const dLead = scored.find((prospect) => prospect.score_category === "D");

assert.ok(aLead);
assert.equal(aLead.recommended_first_touch.includes("Wallace"), true);
assert.ok(bLead);
assert.equal(bLead.recommended_first_touch.includes("Manual email"), true);
assert.ok(cLead);
assert.equal(cLead.recommended_first_touch.includes("Nurture"), true);
assert.ok(dLead);
assert.equal(dLead.recommended_first_touch.includes("Do not contact"), true);

const report = renderDailyQueue(scored, { generatedAt: "2026-05-14T00:00:00.000Z" });
assert.match(report, /Wallace Daily Outreach Queue/);
assert.match(report, /A Leads: Call Wallace Now/);
assert.match(report, /What Not To Send Yet/);
assert.match(report, /Provider writes: disabled/);

assert.equal(sampleText.includes("@gmail.com"), false);
assert.equal(sampleText.includes("@yahoo.com"), false);
assert.equal(sampleText.includes("@icloud.com"), false);
assert.equal(sampleText.includes("https://example.invalid"), true);

console.log("outreach command center tests passed");
