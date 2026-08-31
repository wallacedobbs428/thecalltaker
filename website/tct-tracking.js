/*
 * Canonical public attribution entrypoint.
 *
 * This file deliberately owns no second event vocabulary or persistence path:
 * it loads the single PII-free CTOS producer in tct-funnel-events.js.  Keeping
 * this stable URL means legacy templates cannot silently fall back to a
 * retired/no-op tracker while the actual producer remains one implementation.
 */
(function (root, document) {
  "use strict";
  if (root.__TCT_ATTRIBUTION_ENTRYPOINT_LOADED__) return;
  root.__TCT_ATTRIBUTION_ENTRYPOINT_LOADED__ = true;
  root.TCTLeadCapture = { open: function () { return false; } };

  if (root.__TCT_FUNNEL_EVENTS_INITIALIZED__ || document.querySelector('script[data-tct-funnel-producer]')) return;
  var script = document.createElement('script');
  script.src = '/tct-funnel-events.js';
  script.defer = true;
  script.setAttribute('data-tct-funnel-producer', 'true');
  (document.head || document.documentElement).appendChild(script);
}(window, document));
