import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { buildSocialCalendar, renderCalendarMarkdown, SOCIAL_CALENDAR_NO_POST_MODE } from "../tools/social/generate_calendar.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const approved = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/creative/output/social-agent-approved.sample.json"), "utf8"));

test("social calendar stays no-post", () => {
  assert.equal(SOCIAL_CALENDAR_NO_POST_MODE, true);
});

test("calendar schedules only approved candidates", () => {
  const calendar = buildSocialCalendar(approved, { days: 7 });

  assert.equal(calendar.no_post_mode, true);
  assert.equal(calendar.source_candidates, 4);
  assert.equal(calendar.scheduled_posts.length, 7);
  assert.ok(calendar.scheduled_posts.every((item) => item.ready_for_manual_post === true));
  assert.ok(calendar.scheduled_posts.every((item) => item.post_allowed === true));
  assert.ok(calendar.scheduled_posts.every((item) => item.calendar_executes_post === false));
  assert.ok(new Set(calendar.scheduled_posts.map((item) => `${item.platform}:${item.asset_id}`)).size > 1);
});

test("calendar preserves no-provider and no-paid boundary", () => {
  const calendar = buildSocialCalendar(approved, { days: 7 });

  assert.equal(calendar.blocked_policy.auto_publish_allowed, false);
  assert.equal(calendar.blocked_policy.paid_spend_allowed, false);
  assert.equal(calendar.blocked_policy.provider_calls_allowed, false);
});

test("markdown output is operator-readable", () => {
  const markdown = renderCalendarMarkdown(buildSocialCalendar(approved, { days: 2 }));

  assert.match(markdown, /Social Content Calendar/);
  assert.match(markdown, /Ready for manual post: yes/);
  assert.match(markdown, /Calendar executes post: no/);
  assert.match(markdown, /This calendar does not post/);
});
