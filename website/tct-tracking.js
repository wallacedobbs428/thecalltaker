/*
 * Retired compatibility shim.
 * Anonymous visitors are measured only by the PII-free first-party
 * tct-funnel-events.js contract. Lead capture is explicit on /demo.html.
 */
(function () {
  "use strict";
  window.TCTLeadCapture = { open: function () { return false; } };
}());
