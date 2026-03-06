/**
 * TheCallTaker.com - Unified Tracking & Lead Capture
 * Includes: GA4, Meta Pixel, Lead Popup, Event Tracking
 * Include on every page via: <script src="/tct-tracking.js"></script>
 */

(function() {
  'use strict';

  // =========================================================================
  // A. Google Analytics 4 (gtag.js) — skip if already loaded by page
  // =========================================================================
  window.dataLayer = window.dataLayer || [];
  if (typeof window.gtag !== 'function' && !document.querySelector('script[src*="gtag/js?id=G-29LL5GPBQV"]')) {
    window.gtag = function(){dataLayer.push(arguments);};
    var gtagScript = document.createElement('script');
    gtagScript.async = true;
    gtagScript.src = 'https://www.googletagmanager.com/gtag/js?id=G-29LL5GPBQV';
    document.head.appendChild(gtagScript);
    window.gtag('js', new Date());
    window.gtag('config', 'G-29LL5GPBQV');
  }

  // =========================================================================
  // B. Meta Pixel — deferred to idle to avoid blocking render
  // =========================================================================
  var _idleCb = window.requestIdleCallback || function(cb) { setTimeout(cb, 200); };
  _idleCb(function() {
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
    document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', 'XXXXXXXXXX'); // TODO: Replace with actual Meta Pixel ID
    fbq('track', 'PageView');
  });

  // =========================================================================
  // B2. Attribution Tracking (UTM, gclid, fbclid, referrer, landing page)
  // =========================================================================
  (function initAttribution() {
    // First-touch only — don't overwrite if already captured this session
    if (sessionStorage.getItem('tct_attribution')) return;

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
      landing_page: window.location.pathname || '/'
    };

    sessionStorage.setItem('tct_attribution', JSON.stringify(attribution));
  })();

  /**
   * Returns GHL-compatible tag array from attribution data.
   * e.g. ['source-google', 'medium-cpc', 'campaign-spring25', 'gclid']
   */
  window.getTctAttributionTags = function() {
    var tags = [];
    try {
      var attr = JSON.parse(sessionStorage.getItem('tct_attribution') || '{}');
      if (attr.utm_source) tags.push('source-' + attr.utm_source.toLowerCase());
      if (attr.utm_medium) tags.push('medium-' + attr.utm_medium.toLowerCase());
      if (attr.utm_campaign) tags.push('campaign-' + attr.utm_campaign.toLowerCase());
      if (attr.utm_content) tags.push('content-' + attr.utm_content.toLowerCase());
      if (attr.utm_term) tags.push('term-' + attr.utm_term.toLowerCase());
      if (attr.gclid) tags.push('gclid', 'google-ads');
      if (attr.fbclid) tags.push('fbclid', 'meta-ads');
      if (attr.landing_page && attr.landing_page !== '/') {
        var slug = attr.landing_page.replace(/^\//, '').replace(/\.html$/, '').replace(/\//g, '-');
        if (slug) tags.push('landing-page-' + slug);
      }
    } catch (e) {}
    return tags;
  };

  /**
   * Returns a full attribution string for GHL contact notes.
   */
  window.getTctAttributionNotes = function() {
    try {
      var attr = JSON.parse(sessionStorage.getItem('tct_attribution') || '{}');
      var parts = [];
      parts.push('--- Attribution ---');
      if (attr.utm_source) parts.push('Source: ' + attr.utm_source);
      if (attr.utm_medium) parts.push('Medium: ' + attr.utm_medium);
      if (attr.utm_campaign) parts.push('Campaign: ' + attr.utm_campaign);
      if (attr.utm_content) parts.push('Content: ' + attr.utm_content);
      if (attr.utm_term) parts.push('Term: ' + attr.utm_term);
      if (attr.gclid) parts.push('Google Click ID: ' + attr.gclid);
      if (attr.fbclid) parts.push('Meta Click ID: ' + attr.fbclid);
      if (attr.referrer) parts.push('Referrer: ' + attr.referrer);
      if (attr.landing_page) parts.push('Landing Page: ' + attr.landing_page);
      parts.push('Captured: ' + new Date().toISOString());
      return parts.length > 1 ? parts.join('\n') : '';
    } catch (e) { return ''; }
  };

  // =========================================================================
  // C. Lead Capture Popup
  // =========================================================================
  var POPUP_DELAY = 15000; // 15 seconds
  var GHL_API_BASE = 'https://services.leadconnectorhq.com';
  var GHL_API_KEY = 'pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35';
  var GHL_LOCATION_ID = 'tQb9YmrGDrdVUJYPKrsY';

  var INDUSTRIES = [
    { value: 'hvac', label: 'HVAC' },
    { value: 'roofing', label: 'Roofing' },
    { value: 'plumbing', label: 'Plumbing' },
    { value: 'electrical', label: 'Electrical' },
    { value: 'dental', label: 'Dental' },
    { value: 'medspa', label: 'MedSpa' },
    { value: 'legal', label: 'Legal' },
    { value: 'property-management', label: 'Property Management' },
    { value: 'veterinary', label: 'Veterinary' },
    { value: 'locksmith', label: 'Locksmith' },
    { value: 'garage-door', label: 'Garage Door' },
    { value: 'towing', label: 'Towing' },
    { value: 'funeral', label: 'Funeral Homes' }
  ];

  function buildPopup() {
    // Inject CSS
    var style = document.createElement('style');
    style.textContent = '' +
      '#tct-popup-overlay {' +
      '  display: none;' +
      '  position: fixed;' +
      '  top: 0; left: 0; width: 100%; height: 100%;' +
      '  background: rgba(0,0,0,0.5);' +
      '  z-index: 999999;' +
      '  justify-content: center;' +
      '  align-items: center;' +
      '  opacity: 0;' +
      '  transition: opacity 0.4s ease;' +
      '}' +
      '#tct-popup-overlay.tct-visible {' +
      '  display: flex;' +
      '  opacity: 1;' +
      '}' +
      '#tct-popup-overlay.tct-fade-in {' +
      '  display: flex;' +
      '}' +
      '#tct-popup-modal {' +
      '  background: #ffffff;' +
      '  border-radius: 16px;' +
      '  padding: 40px 36px;' +
      '  max-width: 520px;' +
      '  width: 90%;' +
      '  position: relative;' +
      '  box-shadow: 0 25px 60px rgba(0,0,0,0.15);' +
      '  border: 1px solid rgba(0,0,0,0.08);' +
      '  transform: translateY(20px);' +
      '  transition: transform 0.4s ease;' +
      '  max-height: 90vh;' +
      '  overflow-y: auto;' +
      '}' +
      '#tct-popup-overlay.tct-visible #tct-popup-modal {' +
      '  transform: translateY(0);' +
      '}' +
      '#tct-popup-close {' +
      '  position: absolute;' +
      '  top: 14px; right: 18px;' +
      '  background: none; border: none;' +
      '  color: #9ca3af; font-size: 28px;' +
      '  cursor: pointer; line-height: 1;' +
      '  padding: 4px 8px;' +
      '  transition: color 0.2s;' +
      '}' +
      '#tct-popup-close:hover { color: #111827; }' +
      '#tct-popup-modal h2 {' +
      '  color: #111827;' +
      '  font-size: 24px;' +
      '  margin: 0 0 12px 0;' +
      '  line-height: 1.3;' +
      '  font-family: inherit;' +
      '}' +
      '#tct-popup-modal p.tct-subhead {' +
      '  color: #4b5563;' +
      '  font-size: 15px;' +
      '  margin: 0 0 24px 0;' +
      '  line-height: 1.6;' +
      '}' +
      '#tct-popup-form input,' +
      '#tct-popup-form select {' +
      '  width: 100%;' +
      '  padding: 12px 16px;' +
      '  margin-bottom: 14px;' +
      '  background: #f9fafb;' +
      '  border: 1px solid rgba(0,0,0,0.08);' +
      '  border-radius: 8px;' +
      '  color: #111827;' +
      '  font-size: 15px;' +
      '  outline: none;' +
      '  box-sizing: border-box;' +
      '  font-family: inherit;' +
      '  transition: border-color 0.2s;' +
      '  -webkit-appearance: none;' +
      '  appearance: none;' +
      '}' +
      '#tct-popup-form input::placeholder { color: #9ca3af; }' +
      '#tct-popup-form input:focus,' +
      '#tct-popup-form select:focus {' +
      '  border-color: #ea580c;' +
      '}' +
      '#tct-popup-form select {' +
      '  color: #9ca3af;' +
      '  cursor: pointer;' +
      '  background-image: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'12\' height=\'8\' viewBox=\'0 0 12 8\'%3E%3Cpath d=\'M1 1l5 5 5-5\' stroke=\'%239ca3af\' stroke-width=\'2\' fill=\'none\'/%3E%3C/svg%3E");' +
      '  background-repeat: no-repeat;' +
      '  background-position: right 16px center;' +
      '  padding-right: 40px;' +
      '}' +
      '#tct-popup-form select.tct-selected { color: #111827; }' +
      '#tct-popup-submit {' +
      '  width: 100%;' +
      '  padding: 14px 24px;' +
      '  background: #ea580c;' +
      '  color: #fff;' +
      '  border: none;' +
      '  border-radius: 8px;' +
      '  font-size: 17px;' +
      '  font-weight: 700;' +
      '  cursor: pointer;' +
      '  transition: background 0.2s, transform 0.1s;' +
      '  font-family: inherit;' +
      '  margin-top: 4px;' +
      '}' +
      '#tct-popup-submit:hover { background: #c2410c; }' +
      '#tct-popup-submit:active { transform: scale(0.98); }' +
      '#tct-popup-submit:disabled {' +
      '  background: #d1d5db;' +
      '  cursor: not-allowed;' +
      '}' +
      '#tct-popup-success {' +
      '  display: none;' +
      '  text-align: center;' +
      '  padding: 40px 20px;' +
      '}' +
      '#tct-popup-success .tct-check {' +
      '  font-size: 48px;' +
      '  color: #059669;' +
      '  margin-bottom: 16px;' +
      '}' +
      '#tct-popup-success h3 {' +
      '  color: #111827;' +
      '  font-size: 20px;' +
      '  margin: 0 0 8px 0;' +
      '}' +
      '#tct-popup-success p {' +
      '  color: #4b5563;' +
      '  font-size: 15px;' +
      '  margin: 0;' +
      '}' +
      '#tct-popup-error {' +
      '  color: #ef4444;' +
      '  font-size: 13px;' +
      '  margin: 8px 0 0 0;' +
      '  display: none;' +
      '}' +
      '@media (max-width: 600px) {' +
      '  #tct-popup-modal {' +
      '    padding: 28px 20px;' +
      '    margin: 10px;' +
      '    width: calc(100% - 20px);' +
      '  }' +
      '  #tct-popup-modal h2 { font-size: 20px; }' +
      '  #tct-popup-modal p.tct-subhead { font-size: 14px; }' +
      '}';
    document.head.appendChild(style);

    // Build HTML
    var overlay = document.createElement('div');
    overlay.id = 'tct-popup-overlay';

    var industryOptions = '<option value="">Select Your Industry</option>';
    for (var i = 0; i < INDUSTRIES.length; i++) {
      industryOptions += '<option value="' + INDUSTRIES[i].value + '">' + INDUSTRIES[i].label + '</option>';
    }

    overlay.innerHTML = '' +
      '<div id="tct-popup-modal">' +
        '<button id="tct-popup-close" aria-label="Close">&times;</button>' +
        '<div id="tct-popup-form-wrap">' +
          '<h2>How Much Is Your Business Losing to Missed Calls?</h2>' +
          '<p class="tct-subhead">Get a free Missed Call Revenue Report customized for your business. We\'ll show you exactly how many calls you\'re missing and what they\'re costing you.</p>' +
          '<form id="tct-popup-form" novalidate>' +
            '<input type="text" name="firstName" placeholder="First Name" required>' +
            '<input type="email" name="email" placeholder="Email Address" required>' +
            '<input type="tel" name="phone" placeholder="Phone Number" required>' +
            '<input type="text" name="companyName" placeholder="Company Name" required>' +
            '<select name="industry" required>' + industryOptions + '</select>' +
            '<button type="submit" id="tct-popup-submit">Get My Free Report</button>' +
            '<p id="tct-popup-error">Please fill in all fields correctly.</p>' +
          '</form>' +
        '</div>' +
        '<div id="tct-popup-success">' +
          '<div class="tct-check">&#10003;</div>' +
          '<h3>Check your email!</h3>' +
          '<p>Your report is on the way.</p>' +
        '</div>' +
      '</div>';

    document.body.appendChild(overlay);

    // Select color change on selection
    var selectEl = overlay.querySelector('select[name="industry"]');
    selectEl.addEventListener('change', function() {
      if (this.value) {
        this.classList.add('tct-selected');
      } else {
        this.classList.remove('tct-selected');
      }
    });

    return overlay;
  }

  function showPopup(overlay) {
    if (sessionStorage.getItem('tct_popup_shown')) return;
    sessionStorage.setItem('tct_popup_shown', '1');

    overlay.style.display = 'flex';
    // Trigger reflow for animation
    overlay.offsetHeight;
    overlay.classList.add('tct-visible');

    // Track popup impression
    if (typeof gtag === 'function') {
      gtag('event', 'popup_shown', { event_category: 'lead_capture' });
    }
  }

  function hidePopup(overlay) {
    overlay.classList.remove('tct-visible');
    setTimeout(function() {
      overlay.style.display = 'none';
    }, 400);
  }

  function initPopup() {
    var overlay = buildPopup();
    var modal = document.getElementById('tct-popup-modal');
    var closeBtn = document.getElementById('tct-popup-close');
    var form = document.getElementById('tct-popup-form');
    var errorMsg = document.getElementById('tct-popup-error');
    var submitBtn = document.getElementById('tct-popup-submit');
    var formWrap = document.getElementById('tct-popup-form-wrap');
    var successMsg = document.getElementById('tct-popup-success');

    // Close handlers
    closeBtn.addEventListener('click', function() { hidePopup(overlay); });
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) hidePopup(overlay);
    });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') hidePopup(overlay);
    });

    // Timer trigger (15 seconds)
    var timer = setTimeout(function() {
      showPopup(overlay);
    }, POPUP_DELAY);

    // Exit intent trigger (mouse leaves viewport top)
    var exitTriggered = false;
    document.addEventListener('mouseout', function(e) {
      if (exitTriggered) return;
      if (e.clientY <= 0) {
        exitTriggered = true;
        clearTimeout(timer);
        showPopup(overlay);
      }
    });

    // Form submission
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      errorMsg.style.display = 'none';

      var firstName = form.firstName.value.trim();
      var email = form.email.value.trim();
      var phone = form.phone.value.trim();
      var companyName = form.companyName.value.trim();
      var industry = form.industry.value;

      // Basic validation
      if (!firstName || !email || !phone || !companyName || !industry) {
        errorMsg.textContent = 'Please fill in all fields.';
        errorMsg.style.display = 'block';
        return;
      }

      // Simple email check
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        errorMsg.textContent = 'Please enter a valid email address.';
        errorMsg.style.display = 'block';
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Submitting...';

      var baseTags = ['website-popup', 'missed-call-report', 'industry-' + industry];
      var attrTags = typeof getTctAttributionTags === 'function' ? getTctAttributionTags() : [];
      var payload = {
        firstName: firstName,
        email: email,
        phone: phone,
        companyName: companyName,
        locationId: GHL_LOCATION_ID,
        tags: baseTags.concat(attrTags),
        source: 'Website Popup - Missed Call Report'
      };

      fetch(GHL_API_BASE + '/contacts/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + GHL_API_KEY,
          'Version': '2021-07-28'
        },
        body: JSON.stringify(payload)
      })
      .then(function(response) {
        if (!response.ok) throw new Error('Request failed');
        return response.json();
      })
      .then(function(data) {
        // Post attribution notes to contact
        var contactId = data.contact ? data.contact.id : null;
        if (contactId && typeof getTctAttributionNotes === 'function') {
          var notes = getTctAttributionNotes();
          if (notes) {
            fetch(GHL_API_BASE + '/contacts/' + contactId + '/notes', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + GHL_API_KEY,
                'Version': '2021-07-28'
              },
              body: JSON.stringify({ body: notes })
            }).catch(function(){});
          }
        }
        // Track conversion
        if (typeof gtag === 'function') {
          gtag('event', 'lead_form_submit', {
            event_category: 'conversion',
            event_label: 'popup_missed_call_report',
            industry: industry
          });
        }
        if (typeof fbq !== 'undefined') {
          fbq('track', 'Lead', { content_name: 'Missed Call Report', industry: industry });
        }

        // Show success
        formWrap.style.display = 'none';
        successMsg.style.display = 'block';

        // Auto-close after 3 seconds
        setTimeout(function() {
          hidePopup(overlay);
        }, 3000);
      })
      .catch(function() {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Get My Free Report';
        errorMsg.textContent = 'Something went wrong. Please try again.';
        errorMsg.style.display = 'block';
      });
    });
  }

  // =========================================================================
  // D1. UTM Forwarding — append stored UTMs to outbound conversion links
  // =========================================================================
  function appendUtmsToLink(href) {
    try {
      var attr = JSON.parse(sessionStorage.getItem('tct_attribution') || '{}');
      var keys = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid','fbclid'];
      var sep = href.indexOf('?') !== -1 ? '&' : '?';
      keys.forEach(function(k) {
        if (attr[k]) { href += sep + k + '=' + encodeURIComponent(attr[k]); sep = '&'; }
      });
    } catch(e) {}
    return href;
  }

  // Decorate outbound links on click (pilot, book, checkout, signup, stripe)
  document.addEventListener('click', function(e) {
    var a = e.target.closest('a[href*="/pilot"], a[href*="/book"], a[href*="/checkout"], a[href*="/signup"], a[href*="stripe.com"]');
    if (a && a.href && !a.hasAttribute('data-utm-done')) {
      a.href = appendUtmsToLink(a.href);
      a.setAttribute('data-utm-done', '1');
    }
  }, true);

  // =========================================================================
  // D. Track Key Events (skips pages with inline tracking to avoid double-fire)
  // =========================================================================
  var pageHasInlineTracking = typeof window.tctTrack === 'function' || typeof window.__tctVariant !== 'undefined';
  document.addEventListener('click', function(e) {
    // Track phone call clicks (tel: links, call bar, demo phone)
    var telLink = e.target.closest('a[href*="tel:"]');
    var callBar = e.target.closest('.mobile-call-bar');
    var demoPhone = e.target.closest('.demo-phone');
    if (telLink || callBar || demoPhone) {
      if (!pageHasInlineTracking) {
        var src = callBar ? 'call_bar' : demoPhone ? 'demo_phone' : 'tel_link';
        window.gtag('event', 'tct_call_click', { event_category: 'conversion', source: src });
      }
      if (typeof fbq !== 'undefined') fbq('track', 'Contact');
    }

    // Track CTA / pricing button clicks
    var ctaBtn = e.target.closest('.btn-primary, .btn-outline, .header-cta, .mobile-menu-cta, .rf-cta');
    if (ctaBtn) {
      if (!pageHasInlineTracking) {
        window.gtag('event', 'tct_cta_click', { event_category: 'conversion', event_label: ctaBtn.getAttribute('href') || '' });
      }
      if (typeof fbq !== 'undefined') fbq('track', 'InitiateCheckout');
    }
  });

  // =========================================================================
  // Initialize popup when DOM is ready
  // =========================================================================
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPopup);
  } else {
    initPopup();
  }

})();
