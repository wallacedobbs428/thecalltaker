/* ============================================
   THE CALL TAKER — Carousel Module v2 (JS)
   Revenue-driving ticker + GSAP parallax.
   Clickable items, tracking, scarcity toasts,
   CTA reinforcement, performance guards.
   ============================================ */
var TCTCarousel = (function () {
  'use strict';

  var PAGE = (window.location.pathname.split('/').pop() || 'index.html').replace('.html', '');
  var PATH = window.location.pathname;
  var REDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var isMobile = /Mobi|Android/i.test(navigator.userAgent);
  var DEMO_HREF = '/book.html';
  var allTracks = [];
  var interacted = false;
  var ctaClicked = false;
  var reinforceFired = false;
  var urgencyFired = false;
  var proofFired = false;
  var scrollDepth = 0;

  // ── Industry detection ──
  var INDUSTRY_MAP = {
    hvac: 'HVAC', plumbing: 'Plumbing', electrical: 'Electrical',
    roofing: 'Roofing', dental: 'Dental', medspa: 'Med Spa',
    'med-spa': 'Med Spa', legal: 'Legal', locksmith: 'Locksmith',
    towing: 'Towing', pest: 'Pest Control', veterinary: 'Veterinary',
    vet: 'Veterinary', property: 'Property Mgmt', auto: 'Auto Repair',
    cleaning: 'Cleaning', landscaping: 'Landscaping', funeral: 'Funeral',
    garage: 'Garage Door', water: 'Water Damage', contractor: 'General Contractor'
  };

  function detectIndustry() {
    // 1. Check data-industry on carousel or body
    var di = document.querySelector('[data-industry]');
    if (di) return di.getAttribute('data-industry');
    // 2. Check page path
    for (var key in INDUSTRY_MAP) {
      if (PATH.indexOf(key) !== -1) return INDUSTRY_MAP[key];
    }
    // 3. Check page title / meta description
    var title = (document.title + ' ' + (document.querySelector('meta[name="description"]') || {}).content).toLowerCase();
    for (var k in INDUSTRY_MAP) {
      if (title.indexOf(k) !== -1) return INDUSTRY_MAP[k];
    }
    return '';
  }

  var detectedIndustry = detectIndustry();

  // ── Dynamic SMS deep link ──
  function buildSMSHref() {
    var body = 'PILOT';
    if (detectedIndustry) {
      body = 'PILOT \u2014 ' + detectedIndustry + '. Interested in after-hours coverage.';
    } else {
      body = 'PILOT \u2014 Business: ____ Industry: ____ Best callback time: ____';
    }
    return 'sms:+16157845747?body=' + encodeURIComponent(body);
  }

  var PILOT_SMS = buildSMSHref();

  // ── Scroll depth tracker ──
  window.addEventListener('scroll', function () {
    var docH = document.documentElement.scrollHeight - window.innerHeight;
    if (docH > 0) scrollDepth = window.scrollY / docH;
  }, { passive: true });

  // ── Tracking helper ──
  function track(eventName, params) {
    params = params || {};
    params.page = PAGE;
    // gtag
    if (typeof gtag === 'function') {
      gtag('event', eventName, params);
    }
    // tctTrack (attribution system)
    if (typeof tctTrack === 'function') {
      tctTrack(eventName, params);
    }
    // Custom event for other listeners
    try {
      window.dispatchEvent(new CustomEvent('tct:carousel:' + eventName, { detail: params }));
    } catch (e) {}
  }

  // ── Detect CTA click anywhere on page ──
  document.addEventListener('click', function (e) {
    var link = e.target.closest('a, button');
    if (!link) return;
    var href = link.getAttribute('href') || '';
    var cls = link.className || '';
    if (cls.indexOf('header-cta') !== -1 || cls.indexOf('btn-primary') !== -1 ||
        href.indexOf('book.html') !== -1 || href.indexOf('pilot') !== -1 ||
        href.indexOf('PILOT') !== -1 || href.indexOf('signup') !== -1) {
      ctaClicked = true;
    }
  }, true);

  // ── Performance: pause on hidden tab ──
  function setupVisibilityGuard() {
    document.addEventListener('visibilitychange', function () {
      var hidden = document.hidden;
      for (var i = 0; i < allTracks.length; i++) {
        if (hidden) {
          allTracks[i].classList.add('tct-tab-hidden');
        } else {
          allTracks[i].classList.remove('tct-tab-hidden');
        }
      }
    });
  }

  // ── Clickable item wrapper ──
  function wrapClickable(track) {
    var items = track.querySelectorAll('.tct-ticker-item, .tct-ticker-testimonial, .tct-ticker-badge');
    for (var i = 0; i < items.length; i++) {
      var el = items[i];
      // Skip if already wrapped
      if (el.tagName === 'A') continue;
      // Determine link target
      var href = isMobile ? PILOT_SMS : DEMO_HREF;
      // Check for page-specific CTA section
      var ctaSection = document.querySelector('#cta, .cta-section, #demo');
      if (ctaSection && !isMobile) {
        href = '#' + (ctaSection.id || 'cta');
      }
      // Create anchor wrapper
      var a = document.createElement('a');
      a.href = href;
      a.className = el.className;
      a.innerHTML = el.innerHTML;
      // Preserve data attributes
      for (var j = 0; j < el.attributes.length; j++) {
        var attr = el.attributes[j];
        if (attr.name !== 'class' && attr.name !== 'style') {
          a.setAttribute(attr.name, attr.value);
        }
      }
      if (el.getAttribute('style')) {
        a.setAttribute('style', el.getAttribute('style'));
      }
      // Click tracking + proof injection
      (function (anchor) {
        anchor.addEventListener('click', function (e) {
          var text = this.textContent.trim().substring(0, 60);
          track('tct_carousel_click', {
            item_text: text,
            variant: this.closest('.tct-carousel-ticker') ?
              (this.closest('.tct-carousel-ticker').getAttribute('data-variant') || 'default') : 'default'
          });
          // If it's a hash link, smooth scroll + inject proof
          var h = this.getAttribute('href');
          if (h && h.charAt(0) === '#') {
            var target = document.querySelector(h);
            if (target) {
              e.preventDefault();
              target.scrollIntoView({ behavior: 'smooth', block: 'start' });
              injectProofLine(target);
            }
          }
          // Mark CTA as clicked
          ctaClicked = true;
        });
      })(a);
      el.parentNode.replaceChild(a, el);
    }
  }

  // ── Viewport tracking (IntersectionObserver) ──
  function setupViewTracking(el) {
    if (!('IntersectionObserver' in window)) return;
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          track('tct_carousel_viewed', {
            variant: el.getAttribute('data-variant') || 'default'
          });
          obs.unobserve(el);
        }
      });
    }, { threshold: 0.3 });
    obs.observe(el);
  }

  // ── Interaction tracking ──
  function setupInteractionTracking(el) {
    var fired = false;
    function onInteract() {
      if (fired) return;
      fired = true;
      interacted = true;
      track('tct_carousel_interacted', {
        variant: el.getAttribute('data-variant') || 'default'
      });
      // Schedule CTA reinforcement
      scheduleCTAReinforcement();
    }
    el.addEventListener('mouseenter', onInteract, { passive: true });
    el.addEventListener('touchstart', onInteract, { passive: true });
  }

  // ── CTA reinforcement (5s after interaction, if CTA not clicked) ──
  function scheduleCTAReinforcement() {
    if (reinforceFired || ctaClicked || REDUCED) return;
    reinforceFired = true;
    setTimeout(function () {
      if (ctaClicked) return;
      var cta = document.querySelector('.header-cta, .btn-primary, a[href*="book.html"], a[href*="pilot"]');
      if (cta) {
        cta.classList.add('tct-cta-reinforce');
        track('tct_carousel_cta_reinforce', {});
        setTimeout(function () {
          cta.classList.remove('tct-cta-reinforce');
        }, 800);
      }
    }, 5000);
    // Also schedule urgency layer (8s, needs scroll > 50%) — Variant B only
    if (window.__tctVariant === 'B') scheduleUrgencyBanner();
  }

  // ── Micro urgency banner (8s after interaction, scroll > 50%, no CTA) ──
  function scheduleUrgencyBanner() {
    if (urgencyFired || REDUCED) return;
    if (sessionStorage.getItem('tct_urgency_shown')) return;
    urgencyFired = true;
    setTimeout(function () {
      if (ctaClicked) return;
      if (scrollDepth < 0.5) return;
      sessionStorage.setItem('tct_urgency_shown', '1');
      showUrgencyBanner();
    }, 8000);
  }

  function showUrgencyBanner() {
    if (document.querySelector('.tct-urgency-banner')) return;
    // Find CTA to place banner under
    var ctaSection = document.querySelector('#cta, .cta-section');
    var ctaBtn = ctaSection ?
      ctaSection.querySelector('.btn-primary, .btn, a[href*="book.html"]') :
      document.querySelector('.btn-primary, a[href*="book.html"]');
    if (!ctaBtn) return;
    var anchor = ctaBtn.closest('div, p, section') || ctaBtn.parentNode;

    var isDark = document.querySelector('.tct-ticker-item--dark, [data-variant]');
    var cls = isDark ? 'tct-urgency-banner--dark' : 'tct-urgency-banner--light';
    var banner = document.createElement('div');
    banner.className = 'tct-urgency-banner ' + cls;
    banner.innerHTML = 'Most businesses decide in 1 call. <a href="/book.html">Want to test it?</a>';

    // Use rAF to avoid reflow during scroll
    requestAnimationFrame(function () {
      anchor.parentNode.insertBefore(banner, anchor.nextSibling);
      requestAnimationFrame(function () {
        banner.classList.add('visible');
      });
    });

    track('tct_revenue_decision_prompt', {});
  }

  // ── Proof injection after carousel click (desktop) — Variant B only ──
  function injectProofLine(ctaSection) {
    if (proofFired || isMobile || REDUCED) return;
    if (window.__tctVariant !== 'B') return;
    proofFired = true;
    var ctaBtn = ctaSection.querySelector('.btn-primary, .btn, a[href*="book.html"]');
    if (!ctaBtn) return;
    var anchor = ctaBtn.closest('div, p, section') || ctaBtn.parentNode;

    var isDark = document.querySelector('.tct-ticker-item--dark, [data-variant]');
    var cls = isDark ? 'tct-proof-line--dark' : 'tct-proof-line--light';
    var proof = document.createElement('div');
    proof.className = 'tct-proof-line ' + cls;
    proof.textContent = '73% of customers book with the first business to answer.';

    requestAnimationFrame(function () {
      anchor.parentNode.insertBefore(proof, anchor.nextSibling);
      requestAnimationFrame(function () {
        proof.classList.add('visible');
      });
    });

    track('tct_proof_injection_shown', {});

    // Fade out after 6s
    setTimeout(function () {
      proof.classList.remove('visible');
      setTimeout(function () {
        if (proof.parentNode) proof.parentNode.removeChild(proof);
      }, 400);
    }, 6000);
  }

  // ── Scarcity toast (pilot + calculator pages only) ──
  function setupScarcityToast(el) {
    var isScarcityPage = PAGE === 'index' || PAGE === 'calculator';
    // Check parent path for pilot
    if (window.location.pathname.indexOf('pilot') !== -1) isScarcityPage = true;
    if (!isScarcityPage) return;
    // Only fire once per session
    if (sessionStorage.getItem('tct_scarcity_shown')) return;

    var track_el = el.querySelector('.tct-carousel-ticker-track');
    if (!track_el) return;

    // Listen for one full animation cycle via animationiteration
    track_el.addEventListener('animationiteration', function onCycle() {
      track_el.removeEventListener('animationiteration', onCycle);
      if (sessionStorage.getItem('tct_scarcity_shown')) return;
      sessionStorage.setItem('tct_scarcity_shown', '1');
      showScarcityToast();
    });
  }

  function showScarcityToast() {
    // Don't double-inject
    if (document.querySelector('.tct-scarcity-toast')) return;

    var toast = document.createElement('a');
    toast.href = '/pilot/';
    toast.className = 'tct-scarcity-toast';
    toast.style.textDecoration = 'none';
    toast.style.color = '#fff';
    toast.innerHTML = '<span class="tct-toast-dot"></span>Only 3 beta spots left this month.';
    document.body.appendChild(toast);

    // Show after brief delay
    setTimeout(function () {
      toast.classList.add('visible');
      track('tct_scarcity_toast_shown', {});
    }, 200);

    // Auto-dismiss after 5s
    setTimeout(function () {
      toast.classList.remove('visible');
      setTimeout(function () {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 500);
    }, 5200);
  }

  // ── Revenue microcopy injection ──
  function injectMicrocopy(el) {
    // Skip if already has microcopy
    if (el.nextElementSibling && el.nextElementSibling.classList.contains('tct-carousel-microcopy')) return;

    var isDark = el.querySelector('.tct-ticker-item--dark, .tct-ticker-testimonial--dark, .tct-ticker-badge--dark');
    var themeClass = isDark ? 'tct-carousel-microcopy--dark' : 'tct-carousel-microcopy--light';

    // Page-specific microcopy
    var copy = 'Every missed call = $300\u2013$1,000 gone.';
    var path = window.location.pathname;
    if (path.indexOf('calculator') !== -1) {
      copy = 'The average missed call costs a service business $300\u2013$1,000.';
    } else if (path.indexOf('industries') !== -1) {
      copy = 'Service businesses lose $35,000+/year to missed calls.';
    } else if (path.indexOf('services') !== -1) {
      copy = 'Your competitors answer every call. Do you?';
    } else if (path.indexOf('compare') !== -1) {
      copy = 'Traditional answering services miss 23% of calls. AI misses zero.';
    } else if (path.indexOf('agency') !== -1) {
      copy = 'Your clients are losing revenue every night. You could fix that.';
    } else if (path.indexOf('blog') !== -1) {
      copy = 'Missing calls while you read? <a href="/book.html">Fix that in 2 minutes.</a>';
    } else if (path.indexOf('pilot') !== -1) {
      copy = '14 days. Zero missed calls. No credit card.';
    }

    var div = document.createElement('div');
    div.className = 'tct-carousel-microcopy ' + themeClass;
    div.innerHTML = copy;
    el.parentNode.insertBefore(div, el.nextSibling);
  }

  /**
   * CSS-only infinite ticker.
   * Auto-duplicates innerHTML, wraps items as clickable links.
   */
  function ticker(el, opts) {
    if (!el) return;
    opts = opts || {};

    var trackEl = el.querySelector('.tct-carousel-ticker-track');
    if (!trackEl) return;

    if (REDUCED) {
      // Still show content, just no animation
      trackEl.style.animation = 'none';
      wrapClickable(trackEl);
      injectMicrocopy(el);
      return;
    }

    // Auto-duplicate content for seamless loop
    if (!trackEl.hasAttribute('data-tct-duped')) {
      var original = trackEl.innerHTML;
      trackEl.innerHTML = original + original;
      trackEl.setAttribute('data-tct-duped', 'true');
    }

    // Apply options
    if (opts.speed) {
      trackEl.style.animationDuration = opts.speed;
    }
    if (opts.direction === 'reverse') {
      trackEl.classList.add('reverse');
    }
    if (opts.pauseOnHover === false) {
      trackEl.style.animationPlayState = 'running';
      el.addEventListener('mouseenter', function () {
        trackEl.style.animationPlayState = 'running';
      });
    }

    // Register for visibility guard
    allTracks.push(trackEl);

    // Wrap items as clickable links
    wrapClickable(trackEl);

    // Revenue microcopy
    injectMicrocopy(el);

    // Tracking
    setupViewTracking(el);
    setupInteractionTracking(el);

    // Scarcity toast (pilot + calculator only)
    setupScarcityToast(el);
  }

  /**
   * GSAP-powered parallax carousel.
   * Falls back to CSS ticker if GSAP is missing.
   */
  function parallax(el, opts) {
    if (!el) return;
    opts = opts || {};

    var trackEl = el.querySelector('.tct-carousel-track');
    if (!trackEl) return;

    if (REDUCED) {
      trackEl.style.animation = 'none';
      wrapClickable(trackEl);
      injectMicrocopy(el);
      return;
    }

    // Graceful fallback if GSAP missing
    if (typeof gsap === 'undefined') {
      el.classList.add('tct-carousel-ticker');
      trackEl.classList.add('tct-carousel-ticker-track');
      el.classList.remove('tct-carousel-scroll');
      trackEl.classList.remove('tct-carousel-track');
      ticker(el, { speed: (opts.speed ? (30 / opts.speed) + 's' : '30s') });
      return;
    }

    // Duplicate content
    if (!trackEl.hasAttribute('data-tct-duped')) {
      var original = trackEl.innerHTML;
      trackEl.innerHTML = original + original;
      trackEl.setAttribute('data-tct-duped', 'true');
    }

    var items = trackEl.children;
    var totalWidth = 0;
    for (var i = 0; i < items.length / 2; i++) {
      totalWidth += items[i].offsetWidth + parseInt(getComputedStyle(trackEl).gap || 40);
    }

    var speed = opts.speed || 1;
    var duration = totalWidth / (50 * speed);

    var tl = gsap.timeline({ repeat: -1 });
    tl.to(trackEl, {
      x: -totalWidth,
      duration: duration,
      ease: 'none'
    });

    // Hover pause
    if (opts.pauseOnHover !== false) {
      el.addEventListener('mouseenter', function () {
        gsap.to(tl, { timeScale: 0, duration: 0.5 });
      });
      el.addEventListener('mouseleave', function () {
        gsap.to(tl, { timeScale: 1, duration: 0.5 });
      });
    }

    // Tab visibility — pause GSAP timeline
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        tl.pause();
      } else {
        tl.resume();
      }
    });

    // Touch/swipe support
    var startX = 0;
    var currentX = 0;
    el.addEventListener('touchstart', function (e) {
      startX = e.touches[0].clientX;
      tl.pause();
    }, { passive: true });
    el.addEventListener('touchmove', function (e) {
      currentX = e.touches[0].clientX;
      var diff = currentX - startX;
      var current = gsap.getProperty(trackEl, 'x');
      gsap.set(trackEl, { x: current + diff * 0.5 });
      startX = currentX;
    }, { passive: true });
    el.addEventListener('touchend', function () {
      tl.resume();
    }, { passive: true });

    // Wrap items as clickable links
    wrapClickable(trackEl);

    // Revenue microcopy
    injectMicrocopy(el);

    // Tracking
    setupViewTracking(el);
    setupInteractionTracking(el);

    // Scarcity toast
    setupScarcityToast(el);
  }

  /**
   * Auto-discover and init all carousels on the page.
   */
  function init() {
    // CSS tickers
    var tickers = document.querySelectorAll('.tct-carousel-ticker');
    for (var i = 0; i < tickers.length; i++) {
      var el = tickers[i];
      var speed = el.getAttribute('data-speed') || null;
      var dir = el.getAttribute('data-direction') || 'normal';
      ticker(el, { speed: speed, direction: dir });
    }

    // GSAP parallax
    var scrollers = document.querySelectorAll('.tct-carousel-scroll[data-parallax]');
    for (var j = 0; j < scrollers.length; j++) {
      var sel = scrollers[j];
      var sp = parseFloat(sel.getAttribute('data-speed')) || 1;
      parallax(sel, { speed: sp });
    }

    // Performance: visibility guard
    setupVisibilityGuard();

    try { window.dispatchEvent(new CustomEvent('tct:carousel:init')); } catch (e) {}
  }

  // Auto-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  return { ticker: ticker, parallax: parallax, init: init };
})();
