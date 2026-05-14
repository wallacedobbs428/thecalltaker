const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

const onboardingPages = [
  "website/onboarding/live.html",
  "website/onboarding/next-steps.html",
  "website/onboarding/intake.html",
  "website/onboarding/checklist.html",
  "website/client/onboarding.html",
  "website/client/dashboard.html",
];

const forbiddenPhrases = [
  "You're Live",
  "You\u2019re Live",
  "AI receptionist is live",
  "is live and answering",
  "answering calls right now",
  "answering calls for your business 24/7",
  "answering every call",
  "calls are being handled",
  "provider routing active",
  "live activation complete",
  "GIDEON is now answering",
  "24/7 answering",
  "go live",
  "start catching every call",
  "have you live",
  "flip the switch",
  "Every call to your business gets answered",
  "Call forwarding activated",
  "\"Live\" tag applied",
  "Hear AI Live",
  "Our AI will call you",
  "Call Me Now",
  "Calling you now",
  "hear the AI right now",
];

onboardingPages.forEach((page) => {
  const html = read(page);

  forbiddenPhrases.forEach((phrase) => {
    assert.strictEqual(
      html.includes(phrase),
      false,
      `${phrase} should not appear in ${page}`
    );
  });
});

console.log("website onboarding safety tests passed");
