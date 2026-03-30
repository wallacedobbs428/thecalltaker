/* ============================================
   THE CALL TAKER — Shared UI Module v2
   Scroll bar, glassmorphism header, mobile
   overlay, fade-ups, FAQ, CTA escalation,
   smart call bar, behavioral tracking, A/B.
   Zero dependencies.
   ============================================ */
(function () {
  'use strict';
  if (window.__tctUILoaded) return;
  window.__tctUILoaded = true;

  var header = document.querySelector('.site-header');
  if (!header) return;

  // ── Config ──
  var VARIANT = window.TCT_UI_VARIANT || 'A';
  var CTA_ORIGINAL_TEXT = '';
  var CTA_ESCALATED_TEXT = 'Start Free Pilot \u2014 3 Spots Left';
  var VARIANT_B_ESCALATED_TEXT = 'Claim Your Spot \u2014 Only 3 Left';

  // ── State ──
  var ctaClicked = false;
  var pulseFired = false;
  var escalated = false;
  var callBarAttentionFired = false;
  var depth90Tracked = false;
  var heroHeightCached = 0;

  // ── Tracking helper ──
  function track(event, params) {
    if (typeof gtag === 'function') {
      gtag('event', event, params || {});
    }
  }

  // ── Variant B: apply body class ──
  if (VARIANT === 'B') {
    document.documentElement.classList.add('tct-variant-b');
  }

  // ── 1. Inject scroll progress bar ──
  var progressBar = document.querySelector('.tct-scroll-progress');
  if (!progressBar) {
    progressBar = document.createElement('div');
    progressBar.className = 'tct-scroll-progress';
    document.body.insertBefore(progressBar, document.body.firstChild);
  }

  // ── 2. Inject mobile overlay if missing ──
  var overlay = document.querySelector('.mobile-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'mobile-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Navigation menu');

    var navLinks = header.querySelector('.nav-links');
    var _headerCta = header.querySelector('.header-cta');
    var ul = document.createElement('ul');
    ul.className = 'mobile-menu-inner';

    if (navLinks) {
      var items = navLinks.querySelectorAll('li');
      for (var i = 0; i < items.length; i++) {
        var a = items[i].querySelector('a');
        if (!a) continue;
        if (a.classList.contains('btn')) continue;
        var li = document.createElement('li');
        var link = document.createElement('a');
        link.href = a.href;
        link.textContent = a.textContent;
        if (a.classList.contains('nav-demo')) {
          link.textContent = 'Call Us: ' + a.textContent.replace('Demo: ', '');
        }
        li.appendChild(link);
        ul.appendChild(li);
      }
    }

    var ctaHref = '/pilot/';
    var ctaText = 'Start Free Pilot \u2192';
    if (_headerCta) {
      ctaHref = _headerCta.href || ctaHref;
      ctaText = _headerCta.textContent.trim() || ctaText;
      if (ctaText.indexOf('\u2192') === -1) ctaText += ' \u2192';
    } else {
      var navCta = navLinks ? navLinks.querySelector('.btn') : null;
      if (navCta) {
        ctaHref = navCta.href || ctaHref;
        ctaText = navCta.textContent.trim() || ctaText;
        if (ctaText.indexOf('\u2192') === -1) ctaText += ' \u2192';
      }
    }
    var ctaLi = document.createElement('li');
    var ctaLink = document.createElement('a');
    ctaLink.href = ctaHref;
    ctaLink.className = 'mobile-menu-cta';
    ctaLink.textContent = ctaText;
    ctaLi.appendChild(ctaLink);
    ul.appendChild(ctaLi);

    overlay.appendChild(ul);
    header.parentNode.insertBefore(overlay, header.nextSibling);
  }

  // ── 3. Inject mobile call bar if missing ──
  var callBar = document.querySelector('.mobile-call-bar');
  if (!callBar) {
    callBar = document.createElement('a');
    callBar.className = 'mobile-call-bar';
    callBar.href = 'tel:+16157845747';
    callBar.innerHTML =
      '<div class="call-bar-main">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
          '<path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>' +
        '</svg>' +
        'Call Our AI Demo' +
      '</div>' +
      '<span style="font-size:.75rem;font-weight:500;opacity:.85">(615) 784-5747 \u2014 Hear it live</span>';
    document.body.appendChild(callBar);
  }

  // ── 4. Inject header CTA if missing ──
  var headerCta = header.querySelector('.header-cta');
  if (!headerCta) {
    var navCtaBtn = header.querySelector('.nav-links .btn');
    if (navCtaBtn) {
      headerCta = document.createElement('a');
      headerCta.className = 'header-cta';
      headerCta.href = navCtaBtn.href;
      headerCta.textContent = navCtaBtn.textContent.trim();
      var toggle = header.querySelector('.mobile-toggle');
      if (toggle) {
        toggle.parentNode.insertBefore(headerCta, toggle);
      } else {
        header.querySelector('.header-inner').appendChild(headerCta);
      }
      var ctaParentLi = navCtaBtn.closest('li');
      if (ctaParentLi) ctaParentLi.remove();
    }
  }

  // Save original CTA text
  if (headerCta) {
    CTA_ORIGINAL_TEXT = headerCta.textContent.trim();
  }

  // ── Variant B: modify CTA text ──
  if (VARIANT === 'B' && headerCta) {
    headerCta.textContent = 'Claim Your Free Pilot';
    CTA_ORIGINAL_TEXT = headerCta.textContent.trim();
    CTA_ESCALATED_TEXT = VARIANT_B_ESCALATED_TEXT;
  }

  // ── 5. Scroll handler — rAF throttled, no layout thrashing ──
  var menuBtn = header.querySelector('.mobile-toggle');
  var heroSection = document.querySelector('.hero, section:first-of-type, main > :first-child');

  // Cache hero height — only re-read on resize
  function updateHeroHeight() {
    if (heroSection) {
      heroHeightCached = heroSection.offsetHeight;
    }
  }
  updateHeroHeight();

  // Debounced resize to recache hero height
  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(updateHeroHeight, 200);
  }, { passive: true });

  function onScroll() {
    var y = window.scrollY;
    var docH = document.documentElement.scrollHeight - window.innerHeight;
    var pct = docH > 0 ? y / docH : 0;

    // Progress bar — transform instead of width for GPU compositing
    if (progressBar && docH > 0) {
      progressBar.style.width = (pct * 100) + '%';
    }

    // Header glassmorphism
    header.classList.toggle('scrolled', y > 40);

    // CTA fill after hero (uses cached height — no forced reflow)
    if (headerCta) {
      var threshold = heroHeightCached > 0 ? heroHeightCached - 100 : 300;
      headerCta.classList.toggle('filled', y > threshold);
    }

    // ── CTA Escalation ──
    if (headerCta && !ctaClicked) {
      // 50% scroll — one-shot pulse
      if (pct >= 0.5 && !pulseFired) {
        pulseFired = true;
        headerCta.classList.add('tct-pulse');
        headerCta.addEventListener('animationend', function () {
          headerCta.classList.remove('tct-pulse');
        }, { once: true });
      }

      // 75% scroll — change text + escalate
      if (pct >= 0.75 && !escalated) {
        escalated = true;
        headerCta.textContent = CTA_ESCALATED_TEXT;
        headerCta.classList.add('tct-escalated');
        track('tct_cta_escalated', {
          variant: VARIANT,
          scroll_pct: Math.round(pct * 100)
        });
      }
    }

    // ── 90% scroll depth tracking ──
    if (pct >= 0.9 && !depth90Tracked) {
      depth90Tracked = true;
      track('tct_scroll_depth_90', { variant: VARIANT });
    }
  }

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(function () {
        onScroll();
        ticking = false;
      });
    }
  }, { passive: true });
  onScroll();

  // ── 6. CTA click tracking ──
  function onCtaClick() {
    ctaClicked = true;
    track('tct_cta_click', {
      variant: VARIANT,
      text: this.textContent.trim(),
      escalated: escalated
    });
    // Smart call bar: reduce intensity after any CTA click
    if (callBar) {
      callBar.classList.add('tct-reduced');
    }
  }

  // Track all CTA links (header, mobile overlay, inline)
  if (headerCta) headerCta.addEventListener('click', onCtaClick);
  document.querySelectorAll('.mobile-menu-cta, .btn-primary[href*="pilot"], a[href*="pilot"]').forEach(function (el) {
    el.addEventListener('click', onCtaClick);
  });

  // ── 7. Smart call bar — attention after 20s of no interaction ──
  if (callBar) {
    var interacted = false;

    function markInteraction() {
      interacted = true;
    }

    // Any click or CTA click counts as interaction
    document.addEventListener('click', markInteraction, { once: true, passive: true });

    setTimeout(function () {
      if (!interacted && !callBarAttentionFired) {
        callBarAttentionFired = true;
        callBar.classList.add('tct-attention');
        callBar.addEventListener('animationend', function () {
          callBar.classList.remove('tct-attention');
        }, { once: true });
        track('tct_call_bar_attention_triggered', { variant: VARIANT });
      }
    }, 20000);
  }

  // ── 8. Mobile menu toggle + tracking ──
  if (menuBtn && overlay) {
    var isOpen = false;

    function openMenu() {
      isOpen = true;
      overlay.classList.add('open');
      menuBtn.classList.add('active');
      menuBtn.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
      track('tct_menu_open', { variant: VARIANT });
    }

    function closeMenu() {
      isOpen = false;
      overlay.classList.remove('open');
      menuBtn.classList.remove('active');
      menuBtn.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }

    menuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      isOpen ? closeMenu() : openMenu();
    });

    // Track and close on link click
    overlay.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        track('tct_menu_click', {
          link_target: this.href,
          link_text: this.textContent.trim(),
          variant: VARIANT
        });
        closeMenu();
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen) closeMenu();
    });

    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeMenu();
    });
  }

  // ── 9. Smooth scroll for anchor links ──
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = this.getAttribute('href');
      if (id === '#') return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      var top = target.getBoundingClientRect().top + window.scrollY - 90;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });

  // ── 10. Fade-up reveal (IntersectionObserver) ──
  var fadeEls = document.querySelectorAll('.fade-up');
  if (fadeEls.length > 0) {
    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add('visible');
            obs.unobserve(en.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
      fadeEls.forEach(function (el) { obs.observe(el); });
    } else {
      fadeEls.forEach(function (el) { el.classList.add('visible'); });
    }
  }

  // ── 11. FAQ accordion ──
  document.querySelectorAll('.faq-question').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = this.parentElement;
      var wasOpen = item.classList.contains('open');
      item.parentElement.querySelectorAll('.faq-item.open').forEach(function (el) {
        el.classList.remove('open');
        var inner = el.querySelector('.faq-answer-inner, .faq-answer');
        if (inner) inner.style.maxHeight = null;
      });
      if (!wasOpen) {
        item.classList.add('open');
        var inner = item.querySelector('.faq-answer-inner, .faq-answer');
        if (inner) inner.style.maxHeight = inner.scrollHeight + 'px';
      }
    });
  });

  // ── 12. Variant B: inject revenue framing under hero ──
  if (VARIANT === 'B') {
    var heroEl = document.querySelector('.hero');
    if (heroEl) {
      var badge = document.createElement('div');
      badge.style.cssText = 'text-align:center;padding:12px 20px;background:var(--orange-light);color:var(--orange);font-size:.85rem;font-weight:700;letter-spacing:-.01em;';
      badge.textContent = 'Service businesses using The Call Taker recover $2K\u2013$10K/month in missed calls';
      heroEl.parentNode.insertBefore(badge, heroEl.nextSibling);
    }
  }

})();
