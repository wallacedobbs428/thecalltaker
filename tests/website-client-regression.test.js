const assert = require("assert");
const fs = require("fs");
const path = require("path");
const CallFlow = require("../website/client/call-flow.js");

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

const websiteClientDir = path.join(__dirname, "../website/client");
const onboardingHtml = fs.readFileSync(path.join(websiteClientDir, "onboarding.html"), "utf8");
const dashboardHtml = fs.readFileSync(path.join(websiteClientDir, "dashboard.html"), "utf8");
const clientPages = onboardingHtml + "\n" + dashboardHtml;

[
  "GIDEON IS LIVE",
  "You're Live",
  "You\u2019re Live",
  "answering calls right now",
  "answering calls for your business 24/7",
  "AI receptionist goes live",
  "Calls Answered",
  "Transferred",
  "Messages Taken",
].forEach((phrase) => {
  assert.strictEqual(clientPages.includes(phrase), false, `${phrase} should not appear in website/client pages`);
});

const invalidForward = CallFlow.validateStep(4, {
  greeting: "Thank you for calling.",
  forwardNumber: "555",
});
assert.strictEqual(invalidForward.forwardNumber, "Enter a 10 digit US number or leave it blank.");

const storage = memoryStorage();
const store = CallFlow.createLocalSetupStore(storage);
storage.setItem("unrelated_key", "keep-me");

const result = store.save({
  businessName: "Thompson Plumbing",
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
assert.strictEqual(result.setup.meta.storage, "local-only");
assert.strictEqual(result.setup.activation.providerStatus, "not-configured");
assert.strictEqual(result.setup.activation.liveProviderConfigured, false);

const completeState = CallFlow.dashboardState(store.load());
assert.strictEqual(completeState.complete, true);
assert.strictEqual(completeState.statusLabel, "SETUP COMPLETE");
assert.strictEqual(completeState.providerStatus, "not-configured");
assert.strictEqual(completeState.liveProviderConfigured, false);
assert.deepStrictEqual(completeState.missingItems, []);

const incompleteState = CallFlow.dashboardState(CallFlow.buildSetup({
  businessName: "Thompson Plumbing",
  industry: "Plumbing",
  location: "",
  weekdayHours: "8 AM - 6 PM",
  saturdayHours: "Closed",
  sundayHours: "Closed",
  services: "Drain cleaning",
  serviceArea: "Nashville metro",
  greeting: "Thank you for calling.",
}));

assert.strictEqual(incompleteState.complete, false);
assert.strictEqual(incompleteState.statusLabel, "SETUP NEEDS ATTENTION");
assert.deepStrictEqual(incompleteState.missingItems.map((item) => item.key), ["location"]);

store.reset();
assert.strictEqual(store.load(), null);
assert.strictEqual(storage.getItem("unrelated_key"), "keep-me");

console.log("website client regression tests passed");
