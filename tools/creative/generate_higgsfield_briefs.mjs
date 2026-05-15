import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const HIGGSFIELD_BRIEF_NO_PROVIDER_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaults = {
  output: path.join(__dirname, "output", "higgsfield-briefs.sample.json"),
  markdown: path.join(__dirname, "output", "higgsfield-briefs.sample.md"),
};

const concepts = [
  {
    id: "after-hours-missed-call-office",
    title: "After-hours desk missed call",
    learning_purpose: "Test whether service owners understand the missed-call leak in the first two seconds.",
    scene: "a dim, real-looking small service business office after closing, one desk lamp on, a phone vibrating unanswered beside a notebook",
    motion: "slow handheld push toward the unanswered phone, then cut to an owner checking missed calls in the morning",
    overlay: "after close, the good leads still call",
    close: "see the demo preview",
  },
  {
    id: "owner-truck-still-working",
    title: "Owner still on the job",
    learning_purpose: "Test owner-operator pain when calls arrive while the owner is still working.",
    scene: "a tired local contractor sitting in a work truck at dusk after a job, phone lighting up on the passenger seat while tools are visible",
    motion: "native phone-shot framing, small camera shake, quick glance from owner to missed call notification without readable screen text",
    overlay: "still on the job. phone still ringing.",
    close: "hear the preview",
  },
  {
    id: "emergency-call-overnight",
    title: "Emergency call overnight",
    learning_purpose: "Test urgency for emergency-service categories without claiming live routing or guaranteed booked jobs.",
    scene: "a believable home-service dispatch desk at night with a wall clock, paperwork, and a phone buzzing while the office is empty",
    motion: "fast first shot on the buzzing phone, then a quiet empty-office wide shot",
    overlay: "emergency calls do not wait for business hours",
    close: "build a preview first",
  },
];

function usage() {
  return `The Call Taker Higgsfield brief generator

Usage:
  node tools/creative/generate_higgsfield_briefs.mjs

Creates local production briefs only. It does not call Higgsfield, Meta, or any provider.
`;
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--output") args.output = argv[++index];
    else if (arg === "--markdown") args.markdown = argv[++index];
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return { ...defaults, ...args };
}

function buildPrompt(concept) {
  return [
    "Realistic native vertical video for a local service-business ad.",
    concept.scene,
    concept.motion,
    "Looks like phone footage from a real small business, not a polished commercial.",
    "No readable phone number, no readable app UI, no fake dashboard, no futuristic AI graphics.",
    "No claim that calls are live, routed, activated, guaranteed, or answered for the business.",
    "Use natural lighting, believable hands, normal faces, simple motion, and a clear first two seconds.",
  ].join(" ");
}

function buildBrief(concept) {
  return {
    id: concept.id,
    title: concept.title,
    source: "higgsfield_brief_only",
    no_provider_call: HIGGSFIELD_BRIEF_NO_PROVIDER_MODE,
    learning_purpose: concept.learning_purpose,
    format: "vertical_reel",
    sound_plan: "caption-first; add controlled voiceover only after pronunciation review",
    prompt: buildPrompt(concept),
    negative_prompt: "fake UI, readable generated screen text, fake phone number, robot, hologram, corporate commercial, exaggerated acting, distorted hands, weird teeth, weird eyes, live activation claim, guaranteed results",
    caption_overlay: concept.overlay,
    closing_direction: concept.close,
    qa_gate: [
      "first two seconds clearly show missed-call pain",
      "works without sound",
      "no fake UI or readable generated text",
      "no fake phone numbers",
      "no live-routing, activation, or guaranteed-job claim",
      "does not look AI-generated before the problem is clear",
      "The Call Taker pronunciation verified if voice is used",
    ],
    next_action: "Generate candidate manually, then import it through tools/creative/import_asset.mjs for scoring.",
  };
}

export function generateHiggsfieldBriefs() {
  if (HIGGSFIELD_BRIEF_NO_PROVIDER_MODE !== true) {
    throw new Error("Higgsfield briefs must remain provider-call-free.");
  }
  return {
    generated_at: "2026-05-14T00:00:00.000Z",
    provider_calls_allowed: false,
    auto_generation_allowed: false,
    briefs: concepts.map(buildBrief),
  };
}

export function renderHiggsfieldBriefs(report) {
  const lines = [
    "# Higgsfield Production Briefs",
    "",
    "Status: local brief only. This file does not call Higgsfield, Meta, or any provider.",
    "",
  ];

  report.briefs.forEach((brief) => {
    lines.push(`## ${brief.id}`);
    lines.push("");
    lines.push(`- Title: ${brief.title}`);
    lines.push(`- Learning purpose: ${brief.learning_purpose}`);
    lines.push(`- Sound plan: ${brief.sound_plan}`);
    lines.push(`- Caption overlay: ${brief.caption_overlay}`);
    lines.push(`- Close: ${brief.closing_direction}`);
    lines.push("");
    lines.push("Prompt:");
    lines.push("");
    lines.push(brief.prompt);
    lines.push("");
    lines.push(`Negative prompt: ${brief.negative_prompt}`);
    lines.push("");
  });

  lines.push("## Boundary", "");
  lines.push("- Manual generation only; no provider call is made by this repo tool.");
  lines.push("- Generated candidates still need import, launch-gate scoring, post-readiness validation, and Wallace approval.");
  lines.push("");
  return lines.join("\n");
}

export function writeHiggsfieldBriefs({ outputPath = defaults.output, markdownPath = defaults.markdown } = {}) {
  const report = generateHiggsfieldBriefs();
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.mkdirSync(path.dirname(markdownPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(report, null, 2)}\n`);
  fs.writeFileSync(markdownPath, renderHiggsfieldBriefs(report));
  return {
    output: outputPath,
    markdown: markdownPath,
    briefs: report.briefs.length,
    provider_calls_allowed: false,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(JSON.stringify(writeHiggsfieldBriefs({ outputPath: args.output, markdownPath: args.markdown }), null, 2));
  }
}
