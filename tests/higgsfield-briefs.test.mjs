import assert from "node:assert/strict";
import test from "node:test";
import { generateHiggsfieldBriefs, HIGGSFIELD_BRIEF_NO_PROVIDER_MODE, renderHiggsfieldBriefs } from "../tools/creative/generate_higgsfield_briefs.mjs";

test("Higgsfield brief generator stays provider-call-free", () => {
  const report = generateHiggsfieldBriefs();

  assert.equal(HIGGSFIELD_BRIEF_NO_PROVIDER_MODE, true);
  assert.equal(report.provider_calls_allowed, false);
  assert.equal(report.auto_generation_allowed, false);
});

test("briefs create multiple native service-business concepts", () => {
  const report = generateHiggsfieldBriefs();

  assert.equal(report.briefs.length, 3);
  assert.ok(report.briefs.every((brief) => brief.format === "vertical_reel"));
  assert.ok(report.briefs.every((brief) => brief.learning_purpose.includes("Test")));
});

test("briefs block fake UI, fake numbers, and live-activation claims", () => {
  const combined = JSON.stringify(generateHiggsfieldBriefs()).toLowerCase();

  assert.match(combined, /no readable phone number/);
  assert.match(combined, /no readable app ui/);
  assert.match(combined, /no fake dashboard/);
  assert.match(combined, /no claim that calls are live/);
  assert.match(combined, /guaranteed-job claim/);
});

test("briefs require review before import or launch", () => {
  const report = generateHiggsfieldBriefs();

  assert.ok(report.briefs.every((brief) => brief.next_action.includes("import")));
  assert.ok(report.briefs.every((brief) => brief.qa_gate.includes("The Call Taker pronunciation verified if voice is used")));
});

test("markdown keeps no-provider boundary visible", () => {
  const markdown = renderHiggsfieldBriefs(generateHiggsfieldBriefs());

  assert.match(markdown, /Higgsfield Production Briefs/);
  assert.match(markdown, /does not call Higgsfield/);
  assert.match(markdown, /Manual generation only/);
});
