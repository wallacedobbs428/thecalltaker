/* === ENHANCE.JS — Award-winning animation layer === */
/* Loaded AFTER GSAP, ScrollTrigger & Lenis CDNs */
/* Does NOT replace existing script.js — adds on top */

(function() {
  'use strict';

  // Bail on reduced motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    // Register GSAP plugins
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
      console.warn('[enhance] GSAP or ScrollTrigger not loaded');
      return;
    }
    gsap.registerPlugin(ScrollTrigger);

    // === LENIS SMOOTH SCROLL ===
    let lenis;
    if (typeof Lenis !== 'undefined') {
      lenis = new Lenis({
        duration: 1.2,
        easing: function(t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
        touchMultiplier: 2,
        infinite: false,
      });
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function(time) { lenis.raf(time * 1000); });
      gsap.ticker.lagSmoothing(0);
      document.documentElement.classList.add('lenis', 'lenis-smooth');
    }

    // === SCROLL PROGRESS BAR ===
    var progressBar = document.querySelector('.scroll-progress');
    if (progressBar) {
      gsap.to(progressBar, {
        scaleX: 1,
        ease: 'none',
        scrollTrigger: {
          trigger: document.body,
          start: 'top top',
          end: 'bottom bottom',
          scrub: 0.3,
        },
      });
    }

    // === DISABLE OLD REVEAL SYSTEM, USE GSAP ===
    // The old script.js uses IntersectionObserver to add .visible to .reveal
    // We override those elements and let GSAP handle the animation
    var reveals = document.querySelectorAll('.reveal');
    reveals.forEach(function(el) {
      // Force visible so old system doesn't interfere
      el.classList.add('visible');
      // Add GSAP class for our animations
      el.classList.add('gsap-reveal');
    });

    // === TEXT SPLIT — split headings into animated words ===
    function splitText(el) {
      var text = el.textContent;
      var html = el.innerHTML;
      // Don't split if it has complex HTML children (spans with classes, etc.)
      if (el.querySelectorAll('span[class], a, button, svg').length > 0) return false;

      var words = text.trim().split(/\s+/);
      el.innerHTML = '';
      el.classList.add('split-line');

      words.forEach(function(word, i) {
        var span = document.createElement('span');
        span.classList.add('split-word');
        span.textContent = word;
        el.appendChild(span);
        if (i < words.length - 1) {
          el.appendChild(document.createTextNode(' '));
        }
      });
      return true;
    }

    // Split hero headline and section titles
    var heroH1 = document.querySelector('.hero h1');
    var splitTargets = document.querySelectorAll('.section-title, .bento h2, .callout h2');
    var allSplitEls = [];

    // Only split simple text headings — skip ones with gradient spans etc.
    splitTargets.forEach(function(el) {
      if (splitText(el)) {
        allSplitEls.push(el);
      }
    });

    // === GSAP REVEAL ANIMATIONS ===

    // Hero entrance — staggered fade
    var heroElements = document.querySelectorAll('.hero .reveal');
    if (heroElements.length > 0) {
      gsap.fromTo(heroElements, {
        opacity: 0,
        y: 60,
      }, {
        opacity: 1,
        y: 0,
        duration: 1,
        stagger: 0.15,
        ease: 'power3.out',
        delay: 0.3,
      });
    }

    // Split word reveals
    allSplitEls.forEach(function(el) {
      var words = el.querySelectorAll('.split-word');
      gsap.fromTo(words, {
        y: '110%',
      }, {
        y: '0%',
        duration: 0.8,
        stagger: 0.05,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: el,
          start: 'top 85%',
          once: true,
        },
      });
    });

    // General section reveals
    var gsapReveals = document.querySelectorAll('.gsap-reveal');
    gsapReveals.forEach(function(el) {
      // Skip hero ones — those are handled above
      if (el.closest('.hero')) return;

      gsap.fromTo(el, {
        opacity: 0,
        y: 40,
      }, {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: el,
          start: 'top 85%',
          once: true,
        },
      });
    });

    // === STAGGERED GRID ITEMS ===
    var grids = document.querySelectorAll('.bento-grid, .pricing-grid, .features-grid');
    grids.forEach(function(grid) {
      var items = grid.children;
      gsap.fromTo(items, {
        opacity: 0,
        y: 50,
        scale: 0.96,
      }, {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.7,
        stagger: 0.1,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: grid,
          start: 'top 80%',
          once: true,
        },
      });
    });

    // === PARALLAX ON SECTIONS ===
    var sections = document.querySelectorAll('section');
    sections.forEach(function(section) {
      var decos = section.querySelectorAll('.section-deco');
      decos.forEach(function(deco, i) {
        gsap.to(deco, {
          y: (i % 2 === 0) ? -60 : 60,
          ease: 'none',
          scrollTrigger: {
            trigger: section,
            start: 'top bottom',
            end: 'bottom top',
            scrub: 1,
          },
        });
      });
    });

    // === SECTION LINE DRAWS ===
    var sectionLines = document.querySelectorAll('.section-line');
    sectionLines.forEach(function(line) {
      gsap.to(line, {
        scaleX: 1,
        duration: 1.2,
        ease: 'power2.inOut',
        scrollTrigger: {
          trigger: line,
          start: 'top 90%',
          once: true,
        },
      });
    });

    // === COUNTER ANIMATIONS ===
    var counters = document.querySelectorAll('.stat-val-home, .stat-val');
    counters.forEach(function(counter) {
      var text = counter.textContent.trim();
      // Extract numeric value — handle formats like "$2,847", "1.7s", "24/7", "98%"
      var match = text.match(/^([\$]?)([\d,]+\.?\d*)(.*)/);
      if (!match) return;

      var prefix = match[1];
      var numStr = match[2].replace(/,/g, '');
      var suffix = match[3];
      var target = parseFloat(numStr);
      if (isNaN(target)) return;
      var hasDecimal = numStr.includes('.');

      counter.classList.add('counter-animate');

      ScrollTrigger.create({
        trigger: counter,
        start: 'top 85%',
        once: true,
        onEnter: function() {
          var obj = { val: 0 };
          gsap.to(obj, {
            val: target,
            duration: 1.8,
            ease: 'power2.out',
            onUpdate: function() {
              var v = hasDecimal ? obj.val.toFixed(1) : Math.round(obj.val);
              // Re-add commas
              v = v.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
              counter.textContent = prefix + v + suffix;
            },
          });
          // Add glow
          counter.classList.add('stat-glow');
        },
      });
    });

    // === CARD HOVER TILT (desktop only) ===
    if (window.matchMedia('(pointer: fine)').matches) {
      var tiltCards = document.querySelectorAll('.bento-item, .pricing-card, .review-card');
      tiltCards.forEach(function(card) {
        card.addEventListener('mousemove', function(e) {
          var rect = card.getBoundingClientRect();
          var x = (e.clientX - rect.left) / rect.width;
          var y = (e.clientY - rect.top) / rect.height;
          var rotateX = (y - 0.5) * -8;
          var rotateY = (x - 0.5) * 8;
          gsap.to(card, {
            rotateX: rotateX,
            rotateY: rotateY,
            duration: 0.4,
            ease: 'power2.out',
            transformPerspective: 800,
          });
        });
        card.addEventListener('mouseleave', function() {
          gsap.to(card, {
            rotateX: 0,
            rotateY: 0,
            duration: 0.6,
            ease: 'elastic.out(1, 0.5)',
          });
        });
      });
    }

    // === MAGNETIC BUTTONS ===
    if (window.matchMedia('(pointer: fine)').matches) {
      var magneticEls = document.querySelectorAll('.btn, .callback-btn, .industry-pill');
      magneticEls.forEach(function(el) {
        el.addEventListener('mousemove', function(e) {
          var rect = el.getBoundingClientRect();
          var cx = rect.left + rect.width / 2;
          var cy = rect.top + rect.height / 2;
          var dx = (e.clientX - cx) * 0.2;
          var dy = (e.clientY - cy) * 0.2;
          gsap.to(el, { x: dx, y: dy, duration: 0.3, ease: 'power2.out' });
        });
        el.addEventListener('mouseleave', function() {
          gsap.to(el, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.4)' });
        });
      });
    }

    // === CUSTOM CURSOR ===
    if (window.matchMedia('(pointer: fine) and (hover: hover)').matches) {
      var dot = document.querySelector('.cursor-dot');
      var ring = document.querySelector('.cursor-ring');
      if (dot && ring) {
        var mouseX = 0, mouseY = 0;
        var dotX = 0, dotY = 0;
        var ringX = 0, ringY = 0;

        document.addEventListener('mousemove', function(e) {
          mouseX = e.clientX;
          mouseY = e.clientY;
        });

        gsap.ticker.add(function() {
          dotX += (mouseX - dotX) * 0.2;
          dotY += (mouseY - dotY) * 0.2;
          ringX += (mouseX - ringX) * 0.08;
          ringY += (mouseY - ringY) * 0.08;
          dot.style.left = dotX + 'px';
          dot.style.top = dotY + 'px';
          ring.style.left = ringX + 'px';
          ring.style.top = ringY + 'px';
        });

        // Hover state on interactive elements
        var hovers = document.querySelectorAll('a, button, .btn, .industry-pill, .bento-item, .pricing-card, input, textarea');
        hovers.forEach(function(el) {
          el.addEventListener('mouseenter', function() {
            dot.classList.add('hover');
            ring.classList.add('hover');
          });
          el.addEventListener('mouseleave', function() {
            dot.classList.remove('hover');
            ring.classList.remove('hover');
          });
        });
      }
    }

    // === GRADIENT MESH PARALLAX ===
    var mesh = document.querySelector('.gradient-mesh');
    if (mesh) {
      gsap.to(mesh, {
        y: -100,
        ease: 'none',
        scrollTrigger: {
          trigger: document.body,
          start: 'top top',
          end: 'bottom bottom',
          scrub: 1,
        },
      });
    }

    // === MARQUEE — duplicate content for seamless loop ===
    var marqueeInner = document.querySelector('.marquee-inner');
    if (marqueeInner) {
      marqueeInner.innerHTML += marqueeInner.innerHTML;
    }

    // === FAQ ACCORDION ENHANCED ===
    var faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(function(item) {
      var answer = item.querySelector('.faq-answer');
      if (answer) {
        answer.style.overflow = 'hidden';
      }
    });

    // === URGENCY STRIP ENTRANCE ===
    var urgencyStrip = document.querySelector('.urgency-strip');
    if (urgencyStrip) {
      gsap.from(urgencyStrip, {
        y: -100,
        opacity: 0,
        duration: 0.8,
        ease: 'power3.out',
        delay: 0.1,
      });
    }

    // === STATS BAR COUNT-UP ON ENTER ===
    var statsBar = document.querySelector('.stats-bar, .proof-strip');
    if (statsBar) {
      gsap.from(statsBar.children, {
        opacity: 0,
        y: 20,
        stagger: 0.15,
        duration: 0.6,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: statsBar,
          start: 'top 90%',
          once: true,
        },
      });
    }

    // === BEFORE/AFTER SECTION ===
    var baCards = document.querySelectorAll('.ba-card');
    if (baCards.length > 0) {
      gsap.from(baCards, {
        opacity: 0,
        x: function(i) { return i === 0 ? -60 : 60; },
        duration: 0.9,
        stagger: 0.2,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: baCards[0].parentElement,
          start: 'top 80%',
          once: true,
        },
      });
    }

    // === TESTIMONIAL CARDS STAGGER ===
    var reviewCards = document.querySelectorAll('.review-card');
    if (reviewCards.length > 0) {
      gsap.from(reviewCards, {
        opacity: 0,
        y: 40,
        stagger: 0.12,
        duration: 0.7,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: reviewCards[0].parentElement,
          start: 'top 80%',
          once: true,
        },
      });
    }

    // === PRICING CARDS ENTRANCE ===
    var pricingCards = document.querySelectorAll('.pricing-card');
    if (pricingCards.length > 0) {
      pricingCards.forEach(function(card, i) {
        gsap.from(card, {
          opacity: 0,
          y: 60,
          scale: 0.95,
          duration: 0.8,
          delay: i * 0.15,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: card.parentElement,
            start: 'top 80%',
            once: true,
          },
        });
      });
    }

    // === FLOATING ELEMENTS GENTLE BOB ===
    var floatingEls = document.querySelectorAll('.section-deco');
    floatingEls.forEach(function(el, i) {
      gsap.to(el, {
        y: '+=15',
        duration: 2 + (i * 0.5),
        ease: 'sine.inOut',
        repeat: -1,
        yoyo: true,
      });
      gsap.to(el, {
        rotation: (i % 2 === 0) ? 15 : -15,
        duration: 3 + (i * 0.7),
        ease: 'sine.inOut',
        repeat: -1,
        yoyo: true,
      });
    });

    // === HERO LABEL SHIMMER ===
    var heroLabel = document.querySelector('.hero-label');
    if (heroLabel) {
      heroLabel.style.backgroundSize = '200% auto';
      heroLabel.style.backgroundImage = 'linear-gradient(90deg, var(--green), #00a8ff, var(--green))';
      heroLabel.style.webkitBackgroundClip = 'text';
      heroLabel.style.backgroundClip = 'text';
      heroLabel.style.webkitTextFillColor = 'transparent';
      gsap.to(heroLabel, {
        backgroundPosition: '200% center',
        duration: 3,
        ease: 'none',
        repeat: -1,
      });
    }

    console.log('[enhance] Animation layer loaded');
  }

})();
