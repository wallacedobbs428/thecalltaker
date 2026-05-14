const assert = require("assert");
const fs = require("fs");
const path = require("path");
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
    _data: data,
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
const store = CallFlow.createLocalSetupStore(storage);
storage.setItem("unrelated_key", "keep-me");

const result = store.save({
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
assert.strictEqual(result.setup.meta.storage, "local-only");
assert.strictEqual(result.setup.activation.providerStatus, "not-configured");
assert.strictEqual(result.setup.activation.liveProviderConfigured, false);
assert.strictEqual(result.setup.business.name, "Thompson Plumbing");
assert.strictEqual(result.setup.services.offered.length, 2);
assert.strictEqual(result.setup.callHandling.emergencyForwardNumber, "+16155550199");

const serialized = CallFlow.serializeSetup(result.setup);
assert.strictEqual(serialized.schemaVersion, 2);
assert.strictEqual(serialized.meta.storage, "local-only");
assert.strictEqual(serialized.activation.liveProviderConfigured, false);

const loaded = store.load();
const dashboardState = CallFlow.dashboardState(loaded);
assert.strictEqual(dashboardState.complete, true);
assert.strictEqual(dashboardState.statusLabel, "SETUP COMPLETE");
assert.strictEqual(dashboardState.statusTone, "complete");
assert.strictEqual(dashboardState.afterHours, "Preference: forward urgent calls to +16155550199");
assert.strictEqual(dashboardState.liveProviderConfigured, false);
assert.strictEqual(dashboardState.providerStatus, "not-configured");
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
assert.strictEqual(incompleteState.setup.setupCompletion, "incomplete");
assert.deepStrictEqual(incompleteState.missingItems.map((item) => item.key), ["location"]);
assert.strictEqual(incompleteState.liveProviderConfigured, false);

const missingSetupState = CallFlow.dashboardState(null);
assert.strictEqual(missingSetupState.complete, false);
assert.strictEqual(missingSetupState.statusLabel, "SETUP NEEDS ATTENTION");
assert.strictEqual(missingSetupState.afterHours, "Not configured until setup is complete");
assert.strictEqual(missingSetupState.providerStatus, "not-configured");
assert.strictEqual(
  missingSetupState.greeting,
  "Complete onboarding before this account has a custom greeting ready for provider setup."
);

const backendAdapter = CallFlow.createBackendPersistenceAdapter();
const backendResult = backendAdapter.persist(loaded);
assert.strictEqual(backendResult.ok, false);
assert.strictEqual(backendResult.skipped, true);
assert.strictEqual(backendResult.providerStatus, "not-configured");
assert.strictEqual(backendResult.liveProviderConfigured, false);

store.reset();
assert.strictEqual(store.load(), null);
assert.strictEqual(storage.getItem("unrelated_key"), "keep-me");

const clientPages = [
  fs.readFileSync(path.join(__dirname, "../client/onboarding.html"), "utf8"),
  fs.readFileSync(path.join(__dirname, "../client/dashboard.html"), "utf8"),
].join("\n");
[
  "Hear AI Live",
  "Call Me Now",
  "Calling you now",
  "missed call audit",
  "view call stats",
  "GIDEON IS LIVE",
  "This Month",
  "Answer Rate",
  "Calls Answered",
  "Booked",
].forEach((phrase) => {
  assert.strictEqual(clientPages.includes(phrase), false, `${phrase} should not appear on setup pages`);
});

console.log("call-flow regression tests passed");
