/* ============================================
   THE CALL TAKER — Visitor Intent Scoring (v1)
   Tracks behavioral signals, maintains running
   score in sessionStorage, fires GA4 events,
   exposes score for adaptive CTAs + bridge.
   ============================================ */
(function() {
  'use strict';

  var STORAGE_KEY = 'tct_intent';
  var SCORE_EVENT = 'tct:intent_update';

  // === Scoring weights ===
  var WEIGHTS = {
    demo_played:      30,
    demo_completed:   20,  // bonus on top of demo_played
    pricing_viewed:   20,
    calculator_used:  20,
    scroll_deep:      10,  // >60% page scroll
    pilot_cta_click:  15,
    call_click:       25,
    time_on_site:     5,   // >90 seconds
    return_visit:     10,
    popup_submit:     30
  };

  // === State ===
  var state = loadState();
  var scrollTracked = false;
  var timeTracked = false;

  function loadState() {
    try {
      var raw = sessionStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch(e) {}
    return { score: 0, signals: {}, ts: Date.now() };
  }

  function saveState() {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch(e) {}
  }

  function addSignal(name, points) {
    if (state.signals[name]) return; // already counted
    state.signals[name] = { pts: points, t: Date.now() };
    state.score += points;
    saveState();

    // Fire GA4 event
    if (typeof gtag === 'function') {
      gtag('event', 'tct_intent_signal', {
        signal: name,
        points: points,
        total_score: state.score
      });
    }

    // Dispatch custom event for adaptive CTAs
    try {
      document.dispatchEvent(new CustomEvent(SCORE_EVENT, {
        detail: { signal: name, points: points, score: state.score, signals: state.signals }
      }));
    } catch(e) {}
  }

  // === Return visit detection ===
  (function checkReturnVisit() {
    try {
      var visited = localStorage.getItem('tct_visited');
      if (visited) {
        addSignal('return_visit', WEIGHTS.return_visit);
      }
      localStorage.setItem('tct_visited', Date.now().toString());
    } catch(e) {}
  })();

  // === Scroll depth tracking (>60%) ===
  function trackScroll() {
    if (scrollTracked) return;
    var docHeight = Math.max(
      document.body.scrollHeight,
      document.documentElement.scrollHeight
    );
    var viewHeight = window.innerHeight;
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var scrollPct = (scrollTop + viewHeight) / docHeight;

    if (scrollPct > 0.6) {
      scrollTracked = true;
      addSignal('scroll_deep', WEIGHTS.scroll_deep);
    }
  }

  window.addEventListener('scroll', trackScroll, { passive: true });

  // === Time on site (>90s) ===
  setTimeout(function() {
    if (!timeTracked) {
      timeTracked = true;
      addSignal('time_on_site', WEIGHTS.time_on_site);
    }
  }, 90000);

  // === Pricing section viewed ===
  function trackPricingView() {
    var pricingEl = document.getElementById('pricing') ||
                    document.querySelector('.pricing-grid, .pricing-section, [data-section="pricing"]');
    if (!pricingEl || !('IntersectionObserver' in window)) return;

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          addSignal('pricing_viewed', WEIGHTS.pricing_viewed);
          observer.disconnect();
        }
      });
    }, { threshold: 0.3 });
    observer.observe(pricingEl);
  }

  // === Calculator interaction ===
  function trackCalculator() {
    var calcEl = document.getElementById('roiCalls') ||
                 document.querySelector('.calculator-form, [data-section="calculator"]');
    if (!calcEl) return;
    calcEl.addEventListener('input', function handler() {
      addSignal('calculator_used', WEIGHTS.calculator_used);
      calcEl.removeEventListener('input', handler);
    });
  }

  // === Demo console events ===
  function trackDemoConsole() {
    document.addEventListener('tct:console-play', function() {
      addSignal('demo_played', WEIGHTS.demo_played);
    });

    // Listen for demo completion via class change
    var checkComplete = function() {
      var doneEls = document.querySelectorAll('.dc-done');
      if (doneEls.length > 0) {
        addSignal('demo_completed', WEIGHTS.demo_completed);
      }
    };
    // demo-console.js fires audio_complete which adds .dc-done
    // We also listen for the custom event from demo-console
    document.addEventListener('tct:console-time', function(e) {
      if (e.detail && e.detail.time >= 14) {
        addSignal('demo_completed', WEIGHTS.demo_completed);
      }
    });
  }

  // === CTA + call clicks ===
  function trackClicks() {
    document.addEventListener('click', function(e) {
      // Pilot/signup CTA clicks
      var pilotLink = e.target.closest('a[href*="/pilot"], a[href*="/signup"], .pilot-cta, .start-pilot-btn');
      if (pilotLink) {
        addSignal('pilot_cta_click', WEIGHTS.pilot_cta_click);
      }

      // Phone call clicks
      var telLink = e.target.closest('a[href^="tel:"]');
      if (telLink) {
        addSignal('call_click', WEIGHTS.call_click);
      }
    });
  }

  // === Popup form submit ===
  function trackPopupSubmit() {
    // Listen for the popup success (tct-tracking.js shows #tct-popup-success)
    var observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(m) {
        if (m.target.id === 'tct-popup-success' && m.target.style.display === 'block') {
          addSignal('popup_submit', WEIGHTS.popup_submit);
          observer.disconnect();
        }
      });
    });
    // Observe after a short delay to let popup build
    setTimeout(function() {
      var successEl = document.getElementById('tct-popup-success');
      if (successEl) {
        observer.observe(successEl, { attributes: true, attributeFilter: ['style'] });
      }
    }, 2000);
  }

  // === Initialize all trackers on DOM ready ===
  function init() {
    trackPricingView();
    trackCalculator();
    trackDemoConsole();
    trackClicks();
    trackPopupSubmit();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // === Public API ===
  window.TCT_Intent = {
    score: function() { return state.score; },
    signals: function() { return state.signals; },
    tier: function() {
      if (state.score >= 60) return 'high';
      if (state.score >= 30) return 'mid';
      return 'early';
    },
    // Manual signal injection (for custom integrations)
    signal: function(name, points) {
      addSignal(name, points || 10);
    }
  };
})();
