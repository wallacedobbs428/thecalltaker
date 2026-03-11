/* === ENHANCE.JS — Clean, cinematic scroll animations === */
/* Apple-inspired: slow, purposeful reveals. No gimmicks. */
/* Loaded AFTER GSAP + ScrollTrigger + Lenis CDNs */

(function() {
  'use strict';

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    function waitForGsap(cb) {
      if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        cb();
      } else {
        var attempts = 0;
        var check = setInterval(function() {
          attempts++;
          if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
            clearInterval(check);
            cb();
          } else if (attempts > 50) {
            clearInterval(check);
          }
        }, 100);
      }
    }

    waitForGsap(function() {
      gsap.registerPlugin(ScrollTrigger);
      run();
    });
  }

  function run() {

    // === LENIS SMOOTH SCROLL ===
    if (typeof Lenis !== 'undefined') {
      var lenis = new Lenis({
        duration: 1.1,
        easing: function(t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
        touchMultiplier: 2,
        infinite: false,
      });
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function(time) { lenis.raf(time * 1000); });
      gsap.ticker.lagSmoothing(0);
      document.documentElement.classList.add('lenis', 'lenis-smooth');
    }

    document.body.classList.add('gsap-enhanced');

    // === HERO — slow, confident entrance ===
    var heroFades = document.querySelectorAll('#hero-section .fade-up');
    if (heroFades.length) {
      gsap.fromTo(heroFades, {
        opacity: 0,
        y: 30,
      }, {
        opacity: 1,
        y: 0,
        duration: 1.2,
        stagger: 0.15,
        ease: 'power2.out',
        delay: 0.15,
        onComplete: function() {
          heroFades.forEach(function(el) { el.classList.add('visible'); });
        }
      });
    }

    // === SCROLL REVEALS — smooth fade + subtle rise ===
    // Replace IntersectionObserver .fade-up with GSAP for smoother timing
    var fadeUps = document.querySelectorAll('.fade-up:not(.visible)');
    fadeUps.forEach(function(el) {
      if (el.closest('.hero') || el.closest('#hero-section')) return;

      gsap.fromTo(el, {
        opacity: 0,
        y: 24,
      }, {
        opacity: 1,
        y: 0,
        duration: 1,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: el,
          start: 'top 88%',
          once: true,
        },
        onComplete: function() {
          el.classList.add('visible');
        }
      });
    });

    // === TEXT SPLIT — clean word reveals on section titles ===
    function splitText(el) {
      if (el.querySelectorAll('span[class], a, button, svg, br').length > 0) return false;
      var text = el.textContent.trim();
      if (!text) return false;

      var words = text.split(/\s+/);
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

    var splitEls = [];
    document.querySelectorAll('.section-title').forEach(function(el) {
      if (el.closest('#hero-section') || el.closest('.hero')) return;
      if (splitText(el)) {
        splitEls.push(el);
      }
    });

    splitEls.forEach(function(el) {
      var words = el.querySelectorAll('.split-word');
      gsap.fromTo(words, {
        y: '100%',
        opacity: 0,
      }, {
        y: '0%',
        opacity: 1,
        duration: 0.9,
        stagger: 0.035,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: el,
          start: 'top 88%',
          once: true,
        },
      });
    });

    // === STAGGERED GRIDS — gentle cascade ===
    var grids = ['.features-grid', '.steps-grid', '.po-grid', '.pricing-cards'];
    grids.forEach(function(selector) {
      var grid = document.querySelector(selector);
      if (!grid) return;
      var items = grid.children;
      gsap.fromTo(items, {
        opacity: 0,
        y: 40,
      }, {
        opacity: 1,
        y: 0,
        duration: 0.9,
        stagger: 0.12,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: grid,
          start: 'top 82%',
          once: true,
        },
        onComplete: function() {
          Array.from(items).forEach(function(el) { el.classList.add('visible'); });
        }
      });
    });

    // === COUNTER ANIMATIONS — proof strip numbers count up ===
    var counters = document.querySelectorAll('.proof-strip-value, [data-metric]');
    counters.forEach(function(counter) {
      var text = counter.textContent.trim();
      var match = text.match(/^([<>\$]?\s?)([\d,]+\.?\d*)(.*)/);
      if (!match) return;

      var prefix = match[1];
      var numStr = match[2].replace(/,/g, '');
      var suffix = match[3];
      var target = parseFloat(numStr);
      if (isNaN(target) || target === 0) return;
      var hasDecimal = numStr.includes('.');

      counter.classList.add('counter-animate');

      ScrollTrigger.create({
        trigger: counter,
        start: 'top 90%',
        once: true,
        onEnter: function() {
          var obj = { val: 0 };
          gsap.to(obj, {
            val: target,
            duration: 2.2,
            ease: 'power2.out',
            onUpdate: function() {
              var v = hasDecimal ? obj.val.toFixed(1) : Math.round(obj.val);
              v = v.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
              counter.textContent = prefix + v + suffix;
            },
          });
        },
      });
    });

    // === PROBLEM STATS — stagger in ===
    var problemStats = document.querySelectorAll('.problem-stat');
    if (problemStats.length) {
      gsap.fromTo(problemStats, {
        opacity: 0,
        y: 24,
      }, {
        opacity: 1,
        y: 0,
        duration: 0.8,
        stagger: 0.1,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: problemStats[0].parentElement,
          start: 'top 82%',
          once: true,
        },
        onComplete: function() {
          problemStats.forEach(function(el) { el.classList.add('visible'); });
        }
      });
    }

    // === BEFORE/AFTER — slide from sides ===
    var baCompare = document.querySelector('.ba-compare');
    if (baCompare) {
      var baColumns = baCompare.children;
      if (baColumns.length >= 2) {
        gsap.fromTo(baColumns[0], { opacity: 0, x: -40 }, {
          opacity: 1, x: 0, duration: 1, ease: 'power2.out',
          scrollTrigger: { trigger: baCompare, start: 'top 82%', once: true }
        });
        gsap.fromTo(baColumns[1], { opacity: 0, x: 40 }, {
          opacity: 1, x: 0, duration: 1, ease: 'power2.out', delay: 0.1,
          scrollTrigger: { trigger: baCompare, start: 'top 82%', once: true }
        });
      }
    }

    // === REVIEW CARDS — clean stagger ===
    var reviewCards = document.querySelectorAll('.review-card');
    if (reviewCards.length) {
      gsap.fromTo(reviewCards, {
        opacity: 0,
        y: 30,
      }, {
        opacity: 1,
        y: 0,
        duration: 0.85,
        stagger: 0.1,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: reviewCards[0].parentElement,
          start: 'top 82%',
          once: true,
        },
      });
    }

    // === PRICING CARDS — sequential reveal ===
    var pricingCards = document.querySelectorAll('.pricing-card');
    if (pricingCards.length) {
      pricingCards.forEach(function(card, i) {
        gsap.fromTo(card, {
          opacity: 0,
          y: 40,
        }, {
          opacity: 1,
          y: 0,
          duration: 1,
          delay: i * 0.1,
          ease: 'power2.out',
          scrollTrigger: { trigger: card.parentElement, start: 'top 82%', once: true }
        });
      });
    }

    // === CALL FLOW STEPS ===
    var flowSteps = document.querySelectorAll('.flow-step');
    if (flowSteps.length) {
      gsap.fromTo(flowSteps, {
        opacity: 0,
        y: 20,
      }, {
        opacity: 1,
        y: 0,
        duration: 0.7,
        stagger: 0.08,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: flowSteps[0].parentElement,
          start: 'top 82%',
          once: true,
        },
      });
    }

    // === FAQ ITEMS ===
    var faqItems = document.querySelectorAll('.faq-item');
    if (faqItems.length) {
      gsap.fromTo(faqItems, {
        opacity: 0,
        y: 16,
      }, {
        opacity: 1,
        y: 0,
        duration: 0.6,
        stagger: 0.06,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: faqItems[0].parentElement,
          start: 'top 82%',
          once: true,
        },
      });
    }

    // === SECTION LINE DRAWS ===
    var sectionLines = document.querySelectorAll('.section-line');
    sectionLines.forEach(function(line) {
      gsap.to(line, {
        scaleX: 1,
        duration: 1.4,
        ease: 'power2.inOut',
        scrollTrigger: {
          trigger: line,
          start: 'top 90%',
          once: true,
        },
      });
    });

    // === PARALLAX — subtle depth on key sections ===
    document.querySelectorAll('.section').forEach(function(section) {
      var img = section.querySelector('.hero-phone, .ba-compare img, .case-study-img');
      if (!img) return;
      gsap.fromTo(img, {
        y: 30,
      }, {
        y: -30,
        ease: 'none',
        scrollTrigger: {
          trigger: section,
          start: 'top bottom',
          end: 'bottom top',
          scrub: 1.5,
        },
      });
    });

    console.log('[enhance] Clean animation layer loaded');
  }

})();
