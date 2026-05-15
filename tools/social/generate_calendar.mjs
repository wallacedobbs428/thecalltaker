import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SOCIAL_CALENDAR_NO_POST_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../..");
const defaults = {
  input: path.join(repoRoot, "tools/creative/output/social-agent-approved.sample.json"),
  output: path.join(repoRoot, "tools/social/output/social-calendar.sample.json"),
  markdown: path.join(repoRoot, "tools/social/output/social-calendar.sample.md"),
  days: 7,
};

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--input") args.input = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else if (arg === "--markdown") args.markdown = argv[++index];
    else if (arg === "--days") args.days = Number(argv[++index]);
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return { ...defaults, ...args };
}

function usage() {
  return `The Call Taker social calendar generator

Usage:
  node tools/social/generate_calendar.mjs

Builds a 7-day local calendar from approved social handoff candidates. It never posts.
`;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function addDays(date, days) {
  const next = new Date(date);
  next.setUTCDate(next.getUTCDate() + days);
  return next.toISOString().slice(0, 10);
}

function approvedCandidates(handoff) {
  return (handoff.candidates || []).filter((candidate) => candidate.post_allowed === true && candidate.approval_status === "approved_for_manual_post");
}

function calendarItem(candidate, index, startDate) {
  return {
    day: index + 1,
    date: addDays(startDate, index),
    platform: candidate.platform,
    asset_id: candidate.asset_id,
    format: candidate.format,
    caption: candidate.caption,
    story_frames: candidate.story_frames,
    cta: candidate.cta,
    landing_path: candidate.landing_path,
    hashtags: candidate.hashtags,
    approval_status: candidate.approval_status,
    post_allowed: candidate.post_allowed === true,
    calendar_executes_post: false,
    ready_for_manual_post: true,
    operator_action: "Final visual QA, then hand to approved posting agent. This calendar does not post.",
  };
}

export function buildSocialCalendar(handoff, options = {}) {
  if (SOCIAL_CALENDAR_NO_POST_MODE !== true || handoff.no_post_mode !== true) {
    throw new Error("Social calendar must remain no-post.");
  }
  const startDate = options.startDate || "2026-05-15T00:00:00.000Z";
  const days = options.days || 7;
  const approved = approvedCandidates(handoff);
  const schedule = [];

  for (let index = 0; index < days; index += 1) {
    const candidate = approved[index % approved.length];
    if (!candidate) break;
    schedule.push(calendarItem(candidate, index, startDate));
  }

  return {
    generated_at: "2026-05-14T00:00:00.000Z",
    no_post_mode: SOCIAL_CALENDAR_NO_POST_MODE,
    source_candidates: approved.length,
    days_requested: days,
    scheduled_posts: schedule,
    blocked_policy: {
      auto_publish_allowed: false,
      paid_spend_allowed: false,
      provider_calls_allowed: false,
      post_allowed_by_calendar: false,
    },
  };
}

export function renderCalendarMarkdown(calendar) {
  const lines = [
    "# Social Content Calendar",
    "",
    "Status: local no-post calendar. This file does not publish to Facebook, Instagram, Meta, or any provider.",
    "",
  ];

  if (calendar.scheduled_posts.length === 0) {
    lines.push("No approved candidates available.");
  } else {
    calendar.scheduled_posts.forEach((item) => {
      lines.push(`## Day ${item.day}: ${item.date} - ${item.platform}`);
      lines.push("");
      lines.push(`- Asset: ${item.asset_id}`);
      lines.push(`- Format: ${item.format}`);
      lines.push(`- CTA: ${item.cta}`);
      lines.push(`- Landing: ${item.landing_path}`);
      lines.push(`- Approved for posting agent consideration: ${item.post_allowed ? "yes" : "no"}`);
      lines.push(`- Calendar executes post: ${item.calendar_executes_post ? "yes" : "no"}`);
      lines.push(`- Ready for manual post: ${item.ready_for_manual_post ? "yes" : "no"}`);
      lines.push(`- Operator action: ${item.operator_action}`);
      lines.push("");
      lines.push("### Caption");
      lines.push("");
      lines.push(item.caption);
      lines.push("");
    });
  }

  lines.push("## Boundary", "");
  lines.push("- This calendar does not post.");
  lines.push("- A separate approved posting agent must perform any real post.");
  lines.push("- Do not turn organic calendar items into paid ads without paid launch-gate approval.");
  lines.push("");
  return lines.join("\n");
}

export function writeSocialCalendar({ inputPath = defaults.input, outputPath = defaults.output, markdownPath = defaults.markdown, days = defaults.days } = {}) {
  const calendar = buildSocialCalendar(readJson(inputPath), { days });
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.mkdirSync(path.dirname(markdownPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(calendar, null, 2)}\n`);
  fs.writeFileSync(markdownPath, renderCalendarMarkdown(calendar));
  return {
    output: outputPath,
    markdown: markdownPath,
    scheduled_posts: calendar.scheduled_posts.length,
    source_candidates: calendar.source_candidates,
    no_post_mode: SOCIAL_CALENDAR_NO_POST_MODE,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(
      JSON.stringify(
        writeSocialCalendar({
          inputPath: args.input,
          outputPath: args.output,
          markdownPath: args.markdown,
          days: args.days,
        }),
        null,
        2,
      ),
    );
  }
}
