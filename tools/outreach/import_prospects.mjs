import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { normalizeProspectInput } from "./normalize_prospect.mjs";

export const IMPORT_NO_SEND_MODE = true;

function usage() {
  return `The Call Taker outreach prospect importer

No-send local utility. It validates, normalizes, scores, and previews prospects only.

Usage:
  node tools/outreach/import_prospects.mjs --input tools/outreach/example_import.csv --dry-run
  node tools/outreach/import_prospects.mjs --input tools/outreach/example_import.json --dry-run
  node tools/outreach/import_prospects.mjs --single '{"business_name":"Example HVAC","industry":"hvac",...}' --dry-run

Options:
  --input <path>      Manual CSV or JSON import file.
  --single <json>     One prospect JSON object.
  --dry-run           Required. Writes a local preview only; never sends.
  --output <path>     Preview markdown path. Defaults to tools/outreach/output/import-preview.sample.md.
  --help              Show this help text.
`;
}

function parseArgs(argv) {
  const args = { dryRun: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") args.help = true;
    else if (arg === "--dry-run") args.dryRun = true;
    else if (arg === "--input") args.input = argv[++index];
    else if (arg === "--single") args.single = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else throw new Error(`Unknown option: ${arg}`);
  }
  return args;
}

function splitCsvLine(line) {
  const cells = [];
  let current = "";
  let inQuotes = false;

  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const next = line[index + 1];
    if (char === '"' && next === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      cells.push(current.trim());
      current = "";
    } else {
      current += char;
    }
  }
  cells.push(current.trim());
  return cells;
}

export function parseCsv(content) {
  const lines = content
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  if (lines.length === 0) return [];

  const headers = splitCsvLine(lines[0]).map((header) => header.trim());
  return lines.slice(1).map((line) => {
    const cells = splitCsvLine(line);
    return headers.reduce((row, header, index) => {
      row[header] = cells[index] ?? "";
      return row;
    }, {});
  });
}

function loadInput(filePath) {
  const content = fs.readFileSync(filePath, "utf8");
  if (filePath.endsWith(".csv")) return parseCsv(content);
  const parsed = JSON.parse(content);
  return Array.isArray(parsed) ? parsed : [parsed];
}

function defaultOutputPath() {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  return path.join(__dirname, "output", "import-preview.sample.md");
}

function summarize(results) {
  const accepted = results.filter((result) => result.accepted).map((result) => result.record);
  const rejected = results.filter((result) => !result.accepted);
  const counts = { A: 0, B: 0, C: 0, D: 0 };
  accepted.forEach((record) => {
    counts[record.score_category] += 1;
  });
  return { accepted, rejected, counts };
}

function renderPreview({ sourceLabel, accepted, rejected, counts }) {
  const lines = [
    "# Outreach Import Preview",
    "",
    "Status: dry run only. No email, SMS, calls, CRM writes, provider writes, scraping, or activation occurred.",
    `Source: ${sourceLabel}`,
    `Accepted: ${accepted.length}`,
    `Rejected: ${rejected.length}`,
    `Categories: A=${counts.A}, B=${counts.B}, C=${counts.C}, D=${counts.D}`,
    "",
    "## Scored Prospects",
    "",
  ];

  if (accepted.length === 0) {
    lines.push("No accepted prospects.");
  } else {
    accepted
      .sort((a, b) => b.score - a.score || a.business_name.localeCompare(b.business_name))
      .forEach((prospect) => {
        lines.push(`### ${prospect.business_name}`);
        lines.push(`- Score: ${prospect.score} (${prospect.score_category})`);
        lines.push(`- Industry/category: ${prospect.industry} / ${prospect.category}`);
        lines.push(`- Recommended first touch: ${prospect.recommended_first_touch}`);
        lines.push(`- Outreach angle: ${prospect.outreach_angle}`);
        lines.push(`- Review required: ${prospect.review_required ? "yes" : "no"}`);
        lines.push(`- Next action: ${prospect.next_action}`);
        lines.push("");
      });
  }

  lines.push("## Rejected Records", "");
  if (rejected.length === 0) {
    lines.push("No rejected records.");
  } else {
    rejected.forEach((result, index) => {
      const name = result.record.business_name || `row-${index + 1}`;
      lines.push(`### ${name}`);
      result.errors.forEach((error) => lines.push(`- ${error}`));
      lines.push("");
    });
  }

  lines.push("## Safety Boundary", "");
  lines.push("- This importer is local-only and no-send.");
  lines.push("- Manual compliance review is required before any outreach.");
  lines.push("- Every business with a phone line may be evaluated, but only A/B/C/D scoring decides action priority.");
  lines.push("- Generic phone-line businesses stay lower priority unless urgency, revenue risk, and answering-path weakness are proven.");
  return `${lines.join("\n")}\n`;
}

export function importProspects(records, options = {}) {
  if (IMPORT_NO_SEND_MODE !== true) {
    throw new Error("Outreach import must remain no-send.");
  }
  return records.map((record) => normalizeProspectInput(record, options));
}

function runCli() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    return;
  }
  if (!args.dryRun) {
    throw new Error("--dry-run is required. This importer never performs live sending or provider writes.");
  }
  if (!args.input && !args.single) {
    throw new Error("Provide --input <path> or --single '<json>'.");
  }

  const sourceLabel = args.input || "single-json";
  const records = args.single ? [JSON.parse(args.single)] : loadInput(args.input);
  const results = importProspects(records, { dataSource: sourceLabel, sampleMode: true });
  const summary = summarize(results);
  const outputPath = args.output || defaultOutputPath();
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, renderPreview({ sourceLabel, ...summary }));
  console.log(
    JSON.stringify(
      {
        no_send_mode: IMPORT_NO_SEND_MODE,
        dry_run: true,
        source: sourceLabel,
        accepted: summary.accepted.length,
        rejected: summary.rejected.length,
        categories: summary.counts,
        output: outputPath,
      },
      null,
      2,
    ),
  );
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  runCli();
}
