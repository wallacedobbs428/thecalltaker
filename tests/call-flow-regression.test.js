const assert = require("assert");
const CallFlow = require("../client/call-flow.js");

function memoryStorage() {
  const data = {};
  return {
    getItem(key) {
      return Object.prototype.hasOwnProperty.call(data, key) ? data[key] : null;
    },
    setItem(key, value) {
      data[key] = String(value);
    },
  };
}

const blankStepErrors = CallFlow.validateStep(1, {});
assert.deepStrictEqual(blankStepErrors, {
  businessName: "Business name is required.",
  industry: "Choose an industry.",
  location: "City and state are required.",
});

const invalidForward = CallFlow.validateStep(4, {
  greeting: "Thanks for calling.",
  forwardNumber: "555",
});
assert.strictEqual(invalidForward.forwardNumber, "Enter a 10 digit US number or leave it blank.");

const storage = memoryStorage();
const result = CallFlow.saveSetup(storage, {
  businessName: "  Thompson   Plumbing  ",
  industry: "Plumbing",
  location: "Nashville, TN",
  weekdayHours: "8 AM - 6 PM",
  saturdayHours: "Closed",
  sundayHours: "Closed",
  services: "Drain cleaning, emergency plumbing",
  serviceArea: "Nashville metro",
  greeting: "Thank you for calling Thompson Plumbing. How can I help?",
  forwardNumber: "(615) 555-0199",
});

assert.strictEqual(result.ok, true);
assert.strictEqual(result.setup.businessName, "Thompson Plumbing");
assert.strictEqual(result.setup.forwardNumber, "+16155550199");

const loaded = CallFlow.loadSetup(storage);
const dashboardState = CallFlow.dashboardState(loaded);
assert.strictEqual(dashboardState.complete, true);
assert.strictEqual(dashboardState.statusLabel, "GIDEON IS READY");
assert.strictEqual(dashboardState.afterHours, "Forward urgent calls to +16155550199");

const missingSetupState = CallFlow.dashboardState(null);
assert.strictEqual(missingSetupState.complete, false);
assert.strictEqual(missingSetupState.statusLabel, "SETUP NEEDS ATTENTION");
assert.strictEqual(missingSetupState.afterHours, "Blocked until setup is complete");

console.log("call-flow regression tests passed");
