/* ============================================
   THE CALL TAKER — Shared UI Module (JS, Dark)
   Scroll bar, glassmorphism header, mobile
   overlay upgrade, fade-ups, FAQ.
   For Pattern B dark-theme pages.
   Zero dependencies.
   ============================================ */
(function () {
  'use strict';
  if (window.__tctUILoaded) return;
  window.__tctUILoaded = true;

  var isAdmin = document.body.hasAttribute('data-app') &&
                document.body.getAttribute('data-app') === 'admin';

  var header = document.querySelector('.header');
  if (!header && !isAdmin) return;

  // ── 1. Inject scroll progress bar ──
  var progressBar = document.querySelector('.tct-scroll-progress');
  if (!progressBar) {
    progressBar = document.createElement('div');
    progressBar.className = 'tct-scroll-progress';
    document.body.insertBefore(progressBar, document.body.firstChild);
  }

  // Admin pages: only scroll progress + fade-ups, skip nav mods
  if (isAdmin) {
    initFadeUps();
    initScrollProgress();
    return;
  }

  // ── 2. Upgrade mobile-nav to fullscreen overlay ──
  var mobileNav = document.querySelector('.mobile-nav');
  var menuBtn = document.querySelector('.menu-toggle');

  if (mobileNav && !mobileNav.classList.contains('tct-upgraded')) {
    mobileNav.classList.add('tct-upgraded');
    // Reset any inline transform from the old slide-in
    mobileNav.style.transform = '';
  }

  // ── 3. Inject mobile call bar if missing ──
  var callBar = document.querySelector('.tct-call-bar');
  var stickyBar = document.querySelector('.sticky-mobile-bar');
  if (!callBar && !stickyBar) {
    callBar = document.createElement('a');
    callBar.className = 'tct-call-bar';
    callBar.href = 'tel:+16292699697';
    callBar.innerHTML =
      '<div class="tct-call-bar-main">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
          '<path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>' +
        '</svg>' +
        'Call Our AI Demo' +
      '</div>' +
      '<span style="font-size:.75rem;font-weight:500;opacity:.85">(629) 269-9697 \u2014 Hear it live</span>';
    document.body.appendChild(callBar);
  }

  // ── 4. Scroll handler ──
  var headerCta = header ? header.querySelector('.header-cta') : null;
  var heroSection = document.querySelector('.hero, section:first-of-type, main > :first-child');

  function onScroll() {
    var y = window.scrollY;
    var docH = document.documentElement.scrollHeight - window.innerHeight;

    // Progress bar
    if (progressBar && docH > 0) {
      progressBar.style.width = (y / docH * 100) + '%';
    }

    // Header glassmorphism
    if (header) {
      header.classList.toggle('scrolled', y > 40);
    }

    // CTA fill after hero
    if (headerCta) {
      var threshold = heroSection ? heroSection.offsetHeight - 100 : 300;
      var wasFilled = headerCta.classList.contains('filled');
      headerCta.classList.toggle('filled', y > threshold);
      if (!wasFilled && y > threshold) {
        try { window.dispatchEvent(new CustomEvent('tct:cta:filled')); } catch(e) {}
      }
    }
  }

  function initScrollProgress() {
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(function () {
          var y = window.scrollY;
          var docH = document.documentElement.scrollHeight - window.innerHeight;
          if (progressBar && docH > 0) {
            progressBar.style.width = (y / docH * 100) + '%';
          }
          ticking = false;
        });
      }
    }, { passive: true });
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
  onScroll(); // initial state

  // ── 5. Mobile menu toggle (upgraded) ──
  if (menuBtn && mobileNav) {
    var isOpen = false;

    function openMenu() {
      isOpen = true;
      mobileNav.classList.add('open');
      menuBtn.classList.add('active');
      menuBtn.classList.add('open');
      menuBtn.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
      try { window.dispatchEvent(new CustomEvent('tct:menu:open')); } catch(e) {}
    }

    function closeMenu() {
      isOpen = false;
      mobileNav.classList.remove('open');
      menuBtn.classList.remove('active');
      menuBtn.classList.remove('open');
      menuBtn.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      // Reset stagger delays for next open
      var links = mobileNav.querySelectorAll('a');
      for (var i = 0; i < links.length; i++) {
        links[i].style.transitionDelay = '';
      }
    }

    menuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      isOpen ? closeMenu() : openMenu();
    });

    // Close on link click
    mobileNav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeMenu);
    });

    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen) closeMenu();
    });

    // Close on outside click (clicking the overlay backdrop)
    mobileNav.addEventListener('click', function (e) {
      if (e.target === mobileNav) closeMenu();
    });
  }

  // ── 6. Smooth scroll for anchor links ──
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = this.getAttribute('href');
      if (id === '#') return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      var top = target.getBoundingClientRect().top + window.scrollY - 72;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });

  // ── 7. Fade-up reveal (IntersectionObserver) ──
  function initFadeUps() {
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
  }
  initFadeUps();

  // ── 8. FAQ accordion ──
  document.querySelectorAll('.faq-question').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = this.parentElement;
      var wasOpen = item.classList.contains('open');
      // Close all siblings
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

})();
