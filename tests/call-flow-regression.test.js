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
    removeItem(key) {
      delete data[key];
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

const invalidSave = CallFlow.saveSetup(memoryStorage(), {
  businessName: "Thompson Plumbing",
  industry: "Plumbing",
  location: "Nashville, TN",
  weekdayHours: "8 AM - 6 PM",
  saturdayHours: "Closed",
  sundayHours: "Closed",
  services: "Drain cleaning",
  serviceArea: "Nashville metro",
  greeting: "Thank you for calling Thompson Plumbing.",
  forwardNumber: "555",
});
assert.strictEqual(invalidSave.ok, false);
assert.strictEqual(invalidSave.setup.setupCompletion, "incomplete");
assert.strictEqual(invalidSave.errors.forwardNumber, "Enter a 10 digit US number or leave it blank.");

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
assert.strictEqual(result.setup.schemaVersion, 2);
assert.strictEqual(result.setup.setupCompletion, "complete");
assert.strictEqual(result.setup.business.name, "Thompson Plumbing");
assert.strictEqual(result.setup.services.offered.length, 2);
assert.strictEqual(result.setup.callHandling.emergencyForwardNumber, "+16155550199");

const loaded = CallFlow.loadSetup(storage);
const dashboardState = CallFlow.dashboardState(loaded);
assert.strictEqual(dashboardState.complete, true);
assert.strictEqual(dashboardState.statusLabel, "GIDEON IS READY");
assert.strictEqual(dashboardState.afterHours, "Forward urgent calls to +16155550199");
assert.deepStrictEqual(dashboardState.missingItems, []);

const incompleteSetup = CallFlow.buildSetup({
  businessName: "Thompson Plumbing",
  industry: "Plumbing",
  location: "",
  weekdayHours: "8 AM - 6 PM",
  saturdayHours: "Closed",
  sundayHours: "Closed",
  services: "Drain cleaning",
  serviceArea: "Nashville metro",
  greeting: "Thank you for calling.",
});
const incompleteState = CallFlow.dashboardState(incompleteSetup);
assert.strictEqual(incompleteState.complete, false);
assert.strictEqual(incompleteState.statusLabel, "SETUP NEEDS ATTENTION");
assert.strictEqual(incompleteState.setupCompletion, "incomplete");
assert.deepStrictEqual(incompleteState.missingItems.map((item) => item.key), ["location"]);

const missingSetupState = CallFlow.dashboardState(null);
assert.strictEqual(missingSetupState.complete, false);
assert.strictEqual(missingSetupState.statusLabel, "SETUP NEEDS ATTENTION");
assert.strictEqual(missingSetupState.afterHours, "Blocked until setup is complete");

CallFlow.resetSetup(storage);
assert.strictEqual(CallFlow.loadSetup(storage), null);

console.log("call-flow regression tests passed");
