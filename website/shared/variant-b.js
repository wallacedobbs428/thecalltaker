/* ============================================
   THE CALL TAKER — Variant B Flag + Intent Tracker
   Loaded ONLY on money pages: /, /signup, /calculator, /pilot
   Sets variant flag and tracks CTA/call/SMS clicks.
   Browser-side ntfy activity beacons were removed because they created
   low-signal notification spam without adding operational leverage.
   ============================================ */
(function () {
  'use strict';

  window.__tctVariant = 'B';

  var PAGE = (window.location.pathname.split('/').pop() || 'index.html').replace('.html', '') || 'index';
  var isMobile = /Mobi|Android/i.test(navigator.userAgent);
  var dayKey = new Date().toISOString().slice(0, 10);

  // ── Lightweight tracking ──
  function fire(eventName, detail) {
    detail = detail || {};
    detail.page = PAGE;
    detail.variant = 'B';
    detail.ts = Date.now();

    // gtag (single call — tctTrack also calls gtag, so skip it to avoid double-fire)
    if (typeof gtag === 'function') {
      gtag('event', eventName, detail);
    }
    // Custom DOM event
    try {
      window.dispatchEvent(new CustomEvent('tct:' + eventName, { detail: detail }));
    } catch (e) {}

    // Daily activity noise was removed from phone alerts. Keep analytics only.
  }

  // ── CTA click tracking ──
  document.addEventListener('click', function (e) {
    var link = e.target.closest('a, button');
    if (!link) return;
    var href = (link.getAttribute('href') || '').toLowerCase();
    var text = link.textContent.trim().substring(0, 40);

    // tel: links = call intent
    if (href.indexOf('tel:') === 0) {
      fire('tct_call_click', { label: text, channel: 'phone' });
      return;
    }

    // sms: links = SMS intent
    if (href.indexOf('sms:') === 0) {
      fire('tct_call_click', { label: text, channel: 'sms' });
      return;
    }

    // CTA buttons (book, pilot, signup, checkout, start)
    var cls = (link.className || '').toLowerCase();
    if (cls.indexOf('header-cta') !== -1 || cls.indexOf('btn-primary') !== -1 ||
        cls.indexOf('mobile-menu-cta') !== -1 || cls.indexOf('mobile-call-bar') !== -1 ||
        href.indexOf('book.html') !== -1 || href.indexOf('/pilot') !== -1 ||
        href.indexOf('signup') !== -1 || href.indexOf('checkout') !== -1) {
      fire('tct_cta_click', { label: text, href: href });
    }
  }, true);

  // ── Scarcity toast click (delegated — toast injected later by carousel.js) ──
  document.addEventListener('click', function (e) {
    var toast = e.target.closest('.tct-scarcity-toast');
    if (toast) {
      fire('tct_exit_toast_click', { label: toast.textContent.trim().substring(0, 60) });
    }
  }, true);

})();
