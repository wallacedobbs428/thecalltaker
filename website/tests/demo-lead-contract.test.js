"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const demo = fs.readFileSync(path.resolve(__dirname, "..", "demo.html"), "utf8");

test("demo credits a lead only after the canonical CTOS receipt ID", () => {
  assert.match(demo, /body\.ok !== true \|\| !body\.id/);
  assert.doesNotMatch(demo, /!body\.request_id/);
  assert.match(demo, /recordLeadUi\('lead_request_accepted_ui'\)/);
});
