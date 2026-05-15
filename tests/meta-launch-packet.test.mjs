import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { buildMetaLaunchPacket, META_PACKET_NO_SPEND_MODE, renderMetaLaunchPacket } from "../tools/creative/generate_meta_launch_packet.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const sample = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/creative/creative_assets.sample.json"), "utf8"));

test("Meta launch packet stays no-spend/no-post", () => {
  const packet = buildMetaLaunchPacket(sample.assets);

  assert.equal(META_PACKET_NO_SPEND_MODE, true);
  assert.equal(packet.no_spend_mode, true);
  assert.equal(packet.provider_calls_allowed, false);
  assert.equal(packet.auto_publish_allowed, false);
  assert.equal(packet.launch_allowed, false);
});

test("packet creates manual drafts from safe launch-gate assets", () => {
  const packet = buildMetaLaunchPacket(sample.assets);

  assert.equal(packet.drafts.length, 4);
  assert.ok(packet.drafts.every((draft) => draft.funnel_path === "https://thecalltaker.com/demo.html"));
  assert.ok(packet.drafts.every((draft) => draft.launch_allowed === false));
});

test("packet blocks spend until local assets and Wallace approval exist", () => {
  const packet = buildMetaLaunchPacket(sample.assets);
  const combinedMissing = packet.drafts.flatMap((draft) => draft.missing_launch_requirements).join(" ");

  assert.match(combinedMissing, /local asset file missing/);
  assert.match(combinedMissing, /Wallace paid-spend approval/);
  assert.match(combinedMissing, /Meta account\/manual setup not confirmed/);
});

test("packet excludes unsafe live-routing sample", () => {
  const packet = buildMetaLaunchPacket(sample.assets);

  assert.ok(!packet.drafts.some((draft) => draft.asset_id === "paid-live-routing-unsafe-example"));
});

test("markdown keeps operator boundary visible", () => {
  const markdown = renderMetaLaunchPacket(buildMetaLaunchPacket(sample.assets));

  assert.match(markdown, /Meta Launch Packet/);
  assert.match(markdown, /does not post, launch ads, call Meta/);
  assert.match(markdown, /Do not launch paid spend/);
});
