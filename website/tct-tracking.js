/**
 * TheCallTaker.com — Unified Tracking & Attribution
 * Include on every page: <script src="/tct-tracking.js"></script>
 *
 * Exposes window.tctData for any form to merge: {...formData, ...window.tctData}
 * No API keys client-side — all submissions go to GHL widget/form endpoint (public-safe).
 */
(function() {
  'use strict';

  // =========================================================================
  // A. Attribution Tracking (first-touch, persisted in localStorage)
  // =========================================================================
  var SESSION_KEY = 'tct_session_id';
  var ATTR_KEY = 'tct_attribution';
  var FIRST_VISIT_KEY = 'tct_first_visit';

  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0;
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
  }

  function getDeviceType() {
    var ua = navigator.userAgent || '';
    if (/tablet|ipad|playbook|silk/i.test(ua)) return 'tablet';
    if (/mobile|iphone|ipod|android.*mobile|windows phone|blackberry/i.test(ua)) return 'mobile';
    return 'desktop';
  }

  // Session ID — persists per browser tab session
  if (!sessionStorage.getItem(SESSION_KEY)) {
    sessionStorage.setItem(SESSION_KEY, generateUUID());
  }

  // First visit timestamp — persists across sessions
  if (!localStorage.getItem(FIRST_VISIT_KEY)) {
    localStorage.setItem(FIRST_VISIT_KEY, new Date().toISOString());
  }

  // Attribution — first-touch only (don't overwrite)
  if (!sessionStorage.getItem(ATTR_KEY)) {
    var params = new URLSearchParams(window.location.search);
    var attribution = {
      utm_source: params.get('utm_source') || '',
      utm_medium: params.get('utm_medium') || '',
      utm_campaign: params.get('utm_campaign') || '',
      utm_content: params.get('utm_content') || '',
      utm_term: params.get('utm_term') || '',
      gclid: params.get('gclid') || '',
      fbclid: params.get('fbclid') || '',
      referrer: document.referrer || '',
      landing_page: window.location.href
    };
    sessionStorage.setItem(ATTR_KEY, JSON.stringify(attribution));
  }

  // =========================================================================
  // B. Global tctData object — merge into any form payload
  // =========================================================================
  function buildTctData() {
    var attr = {};
    try { attr = JSON.parse(sessionStorage.getItem(ATTR_KEY) || '{}'); } catch(e) {}
    return {
      utm_source: attr.utm_source || '',
      utm_medium: attr.utm_medium || '',
      utm_campaign: attr.utm_campaign || '',
      utm_content: attr.utm_content || '',
      utm_term: attr.utm_term || '',
      gclid: attr.gclid || '',
      fbclid: attr.fbclid || '',
      referrer: attr.referrer || '',
      landing_page: attr.landing_page || '',
      session_id: sessionStorage.getItem(SESSION_KEY) || '',
      device_type: getDeviceType(),
      timestamp_first_visit: localStorage.getItem(FIRST_VISIT_KEY) || '',
      timestamp_current: new Date().toISOString()
    };
  }

  Object.defineProperty(window, 'tctData', { get: buildTctData });

  // =========================================================================
  // C. Helper exports for GHL tag/notes generation
  // =========================================================================
  window.getTctAttributionTags = function() {
    var tags = [];
    try {
      var attr = JSON.parse(sessionStorage.getItem(ATTR_KEY) || '{}');
      if (attr.utm_source) tags.push('source-' + attr.utm_source.toLowerCase());
      if (attr.utm_medium) tags.push('medium-' + attr.utm_medium.toLowerCase());
      if (attr.utm_campaign) tags.push('campaign-' + attr.utm_campaign.toLowerCase());
      if (attr.utm_content) tags.push('content-' + attr.utm_content.toLowerCase());
      if (attr.utm_term) tags.push('term-' + attr.utm_term.toLowerCase());
      if (attr.gclid) tags.push('gclid', 'google-ads');
      if (attr.fbclid) tags.push('fbclid', 'meta-ads');
      var pg = attr.landing_page || '';
      if (pg && pg !== '/') {
        try { pg = new URL(pg).pathname; } catch(e) {}
        var slug = pg.replace(/^\//, '').replace(/\.html$/, '').replace(/\//g, '-');
        if (slug) tags.push('landing-' + slug);
      }
    } catch (e) {}
    return tags;
  };

  window.getTctAttributionNotes = function() {
    try {
      var d = window.tctData;
      var parts = ['--- Attribution ---'];
      if (d.utm_source) parts.push('Source: ' + d.utm_source);
      if (d.utm_medium) parts.push('Medium: ' + d.utm_medium);
      if (d.utm_campaign) parts.push('Campaign: ' + d.utm_campaign);
      if (d.utm_content) parts.push('Content: ' + d.utm_content);
      if (d.gclid) parts.push('Google Click ID: ' + d.gclid);
      if (d.fbclid) parts.push('Meta Click ID: ' + d.fbclid);
      if (d.referrer) parts.push('Referrer: ' + d.referrer);
      if (d.landing_page) parts.push('Landing Page: ' + d.landing_page);
      parts.push('Device: ' + d.device_type);
      parts.push('Session: ' + d.session_id);
      parts.push('First Visit: ' + d.timestamp_first_visit);
      parts.push('Captured: ' + d.timestamp_current);
      return parts.length > 1 ? parts.join('\n') : '';
    } catch (e) { return ''; }
  };

  // =========================================================================
  // D. UTM forwarding — decorate outbound conversion links
  // =========================================================================
  function appendUtmsToLink(href) {
    try {
      var attr = JSON.parse(sessionStorage.getItem(ATTR_KEY) || '{}');
      var keys = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid','fbclid'];
      var sep = href.indexOf('?') !== -1 ? '&' : '?';
      keys.forEach(function(k) {
        if (attr[k]) { href += sep + k + '=' + encodeURIComponent(attr[k]); sep = '&'; }
      });
    } catch(e) {}
    return href;
  }

  document.addEventListener('click', function(e) {
    var a = e.target.closest('a[href*="/pilot"], a[href*="/book"], a[href*="/checkout"], a[href*="/signup"], a[href*="stripe.com"]');
    if (a && a.href && !a.hasAttribute('data-utm-done')) {
      a.href = appendUtmsToLink(a.href);
      a.setAttribute('data-utm-done', '1');
    }
  }, true);

  // =========================================================================
  // E. GA4 — deferred, skip if already loaded
  // =========================================================================
  window.dataLayer = window.dataLayer || [];
  if (!document.querySelector('script[src*="gtag/js?id=G-29LL5GPBQV"]')) {
    if (typeof window.gtag !== 'function') {
      window.gtag = function(){dataLayer.push(arguments);};
      var _ga = document.createElement('script');
      _ga.async = true;
      _ga.src = 'https://www.googletagmanager.com/gtag/js?id=G-29LL5GPBQV';
      document.head.appendChild(_ga);
      window.gtag('js', new Date());
    }
    window.gtag('config', 'G-29LL5GPBQV');
    window.gtag('config', 'AW-17970510102');
  }

  // =========================================================================
  // F. Meta Pixel — deferred to idle
  // =========================================================================
  var _idle = window.requestIdleCallback || function(cb) { setTimeout(cb, 200); };
  _idle(function() {
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
    document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', 'XXXXXXXXXX');
    fbq('track', 'PageView');
  });

  // =========================================================================
  // G. Event Tracking — phone clicks, CTA clicks
  // =========================================================================
  document.addEventListener('click', function(e) {
    var telLink = e.target.closest('a[href*="tel:"]');
    if (telLink) {
      if (typeof gtag === 'function') gtag('event', 'tct_call_click', { event_category: 'conversion', source: 'tel_link' });
      if (typeof fbq !== 'undefined') fbq('track', 'Contact');
    }
    var ctaBtn = e.target.closest('.btn-primary, .btn-outline, .nav-cta');
    if (ctaBtn) {
      if (typeof gtag === 'function') gtag('event', 'tct_cta_click', { event_category: 'conversion', event_label: ctaBtn.getAttribute('href') || '' });
      if (typeof fbq !== 'undefined') fbq('track', 'InitiateCheckout');
    }
  });

})();
