/* ============================================
   THE CALL TAKER — A/B Split (v1)
   Lightweight 50/50 traffic splitter.
   Runs sync in <head> — no flicker.

   Console:
     TCT.variant()          → current variant
     TCT.setVariant('B')    → force variant (reload)
     TCT.resetVariant()     → clear + re-randomize (reload)
   ============================================ */
(function () {
  'use strict';

  var KEY = 'tct_variant';
  var TTL = 7 * 24 * 60 * 60 * 1000; // 7 days
  var variant = 'A';

  // ── 1. Read or assign variant ──
  try {
    var raw = localStorage.getItem(KEY);
    if (raw) {
      var data = JSON.parse(raw);
      if (data.v && data.t && (Date.now() - data.t < TTL)) {
        variant = data.v;
      } else {
        variant = Math.random() < 0.5 ? 'A' : 'B';
        localStorage.setItem(KEY, JSON.stringify({ v: variant, t: Date.now() }));
      }
    } else {
      variant = Math.random() < 0.5 ? 'A' : 'B';
      localStorage.setItem(KEY, JSON.stringify({ v: variant, t: Date.now() }));
    }
  } catch (e) {
    // Private browsing / storage quota — fall back to A
    variant = 'A';
  }

  // ── 2. Set global before any other JS reads it ──
  window.TCT_UI_VARIANT = variant;

  // ── 3. Pre-apply variant B class to <html> (prevents flash) ──
  if (variant === 'B') {
    document.documentElement.classList.add('tct-variant-b');
  }

  // ── 4. Console helpers ──
  window.TCT = {
    variant: function () {
      console.log('Current variant: ' + window.TCT_UI_VARIANT);
      return window.TCT_UI_VARIANT;
    },
    setVariant: function (v) {
      if (v !== 'A' && v !== 'B') {
        console.error('Variant must be "A" or "B"');
        return;
      }
      try {
        localStorage.setItem(KEY, JSON.stringify({ v: v, t: Date.now() }));
      } catch (e) { /* noop */ }
      window.TCT_UI_VARIANT = v;
      console.log('Variant set to ' + v + '. Reload to see changes.');
    },
    resetVariant: function () {
      try {
        localStorage.removeItem(KEY);
      } catch (e) { /* noop */ }
      console.log('Variant cleared. Reload to re-randomize.');
    }
  };

  // ── 5. Intent tracking (runs after DOM ready) ──
  //    tct_call_intent = tel: link clicks
  //    tct_text_intent = sms: link clicks
  //    Works on ALL pages (Pattern A, B, or standalone)
  document.addEventListener('DOMContentLoaded', function () {
    var V = window.TCT_UI_VARIANT || 'A';

    function track(event, params) {
      params = params || {};
      params.variant = V;
      params.page = location.pathname;
      if (typeof gtag === 'function') {
        gtag('event', event, params);
      }
    }

    // ── Call intent: every tel: link ──
    document.querySelectorAll('a[href^="tel:"]').forEach(function (el) {
      el.addEventListener('click', function () {
        var source = 'inline';
        if (this.closest('.mobile-call-bar')) source = 'call_bar';
        else if (this.closest('.demo-phone')) source = 'demo_phone';
        else if (this.closest('.mobile-menu-inner')) source = 'mobile_menu';
        else if (this.closest('.site-footer, .footer')) source = 'footer';
        track('tct_call_intent', {
          phone: this.getAttribute('href'),
          source: source
        });
      });
    });

    // ── Text intent: every sms: link (PILOT texts, exit toast, etc) ──
    document.querySelectorAll('a[href^="sms:"]').forEach(function (el) {
      el.addEventListener('click', function () {
        var source = 'inline';
        if (this.closest('.mobile-exit-toast')) source = 'exit_toast';
        else if (this.closest('.mobile-call-bar')) source = 'call_bar_fallback';
        track('tct_text_intent', {
          target: this.getAttribute('href'),
          source: source
        });
      });
    });

    // ── CTA intent: pilot/signup/checkout links (deduped with ui.js via event name) ──
    // ui.js fires tct_cta_click for its managed CTAs.
    // This catches CTAs on Pattern B pages where ui.js doesn't run.
    if (!window.__tctUILoaded || !document.querySelector('.site-header')) {
      // Only on pages WITHOUT ui.js managing CTAs
      document.querySelectorAll(
        'a[href*="pilot"], a[href*="signup"], a[href*="checkout"], .btn-primary'
      ).forEach(function (el) {
        el.addEventListener('click', function () {
          track('tct_cta_click', {
            text: (this.textContent || '').trim().substring(0, 60),
            href: this.href || '',
            source: this.className || 'unknown'
          });
        });
      });
    }
  });
})();
