/* ============================================
   THE CALL TAKER — 2350 Premium Interactions
   AmbientField canvas, 3-variant reveal system,
   animated counters, staggered grids, parallax,
   pricing glow, direction-aware shadows.
   Zero dependencies. Layers on existing scripts.
   ============================================ */
(function() {
  'use strict';

  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduced) return;

  // === 1. AMBIENTFIELD — Deferred until user interaction ===
  var ambientStarted = false;
  function startAmbient() {
    if (ambientStarted) return;
    ambientStarted = true;

    var canvas = document.createElement('canvas');
    canvas.id = 'ambientCanvas';
    document.body.insertBefore(canvas, document.body.firstChild);
    var ctx = canvas.getContext('2d');
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w, h;

    function resizeAmbient() {
      w = window.innerWidth;
      canvas.width = w * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = window.innerHeight + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resizeAmbient();
    window.addEventListener('resize', resizeAmbient);

    var orbs = [];
    var orbCount = w < 768 ? 3 : 5;
    var orbColors = [
      { r: 234, g: 88, b: 12 },
      { r: 37, g: 99, b: 235 },
      { r: 5, g: 150, b: 105 },
      { r: 234, g: 88, b: 12 },
      { r: 37, g: 99, b: 235 }
    ];
    for (var i = 0; i < orbCount; i++) {
      orbs.push({
        x: Math.random() * w,
        y: Math.random() * window.innerHeight,
        radius: 200 + Math.random() * 300,
        vx: (Math.random() - 0.5) * 0.15,
        vy: (Math.random() - 0.5) * 0.1,
        color: orbColors[i % orbColors.length],
        opacity: 0.025 + Math.random() * 0.015,
        phase: Math.random() * Math.PI * 2
      });
    }

    var ambientRunning = true;
    var ambientFrames = 0;
    var ambientLastCheck = performance.now();

    function drawAmbient(now) {
      if (!ambientRunning) return;
      ambientFrames++;
      if (ambientFrames >= 120) {
        var fps = ambientFrames / ((now - ambientLastCheck) / 1000);
        ambientFrames = 0;
        ambientLastCheck = now;
        if (fps < 25) { ambientRunning = false; canvas.style.display = 'none'; return; }
      }
      ctx.clearRect(0, 0, w, window.innerHeight);
      for (var i = 0; i < orbs.length; i++) {
        var orb = orbs[i];
        orb.phase += 0.003;
        orb.x += orb.vx + Math.sin(orb.phase) * 0.2;
        orb.y += orb.vy + Math.cos(orb.phase * 0.7) * 0.15;
        if (orb.x < -orb.radius) orb.x = w + orb.radius;
        if (orb.x > w + orb.radius) orb.x = -orb.radius;
        if (orb.y < -orb.radius) orb.y = window.innerHeight + orb.radius;
        if (orb.y > window.innerHeight + orb.radius) orb.y = -orb.radius;
        var grad = ctx.createRadialGradient(orb.x, orb.y, 0, orb.x, orb.y, orb.radius);
        var c = orb.color;
        grad.addColorStop(0, 'rgba(' + c.r + ',' + c.g + ',' + c.b + ',' + (orb.opacity * 1.5) + ')');
        grad.addColorStop(0.5, 'rgba(' + c.r + ',' + c.g + ',' + c.b + ',' + (orb.opacity * 0.5) + ')');
        grad.addColorStop(1, 'rgba(' + c.r + ',' + c.g + ',' + c.b + ',0)');
        ctx.fillStyle = grad;
        ctx.fillRect(orb.x - orb.radius, orb.y - orb.radius, orb.radius * 2, orb.radius * 2);
      }
      requestAnimationFrame(drawAmbient);
    }
    requestAnimationFrame(drawAmbient);
  }

  // Defer AmbientField until first user interaction + idle
  var idle = window.requestIdleCallback || function(cb) { setTimeout(cb, 300); };
  function triggerAmbient() {
    document.removeEventListener('scroll', triggerAmbient);
    document.removeEventListener('mousemove', triggerAmbient);
    document.removeEventListener('touchstart', triggerAmbient);
    idle(startAmbient);
  }
  document.addEventListener('scroll', triggerAmbient, { once: true, passive: true });
  document.addEventListener('mousemove', triggerAmbient, { once: true, passive: true });
  document.addEventListener('touchstart', triggerAmbient, { once: true, passive: true });
  // Fallback: start after 4s regardless
  setTimeout(function() { idle(startAmbient); }, 4000);

  // === 2. 3-VARIANT REVEAL SYSTEM ===
  var revealEls = document.querySelectorAll('.reveal, .reveal-blur, .reveal-scale, .fade-up');
  if (revealEls.length) {
    var revealObs = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          revealObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function(el) { revealObs.observe(el); });
  }

  // === 3. ANIMATED STAT COUNTERS ===
  function animateCounter(el) {
    var text = el.textContent.trim();
    var prefix = text.match(/^[^0-9]*/)[0] || '';
    var suffix = text.match(/[^0-9]*$/)[0] || '';
    var numStr = text.replace(prefix, '').replace(suffix, '').replace(/,/g, '');
    var target = parseFloat(numStr);
    if (isNaN(target)) return;

    var isFloat = numStr.includes('.');
    var duration = 1400;
    var start = performance.now();
    el.classList.add('stat-animated');

    function step(now) {
      var elapsed = now - start;
      var progress = Math.min(elapsed / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 4);
      var current = eased * target;

      if (isFloat) {
        el.textContent = prefix + current.toFixed(1) + suffix;
      } else {
        el.textContent = prefix + Math.round(current).toLocaleString() + suffix;
      }
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // Counter targets: problem stats + proof aggregate + hero proof
  var counterEls = document.querySelectorAll('.problem-stat .num, .proof-agg-val, .hero-proof-val, .proof-strip-value');
  if (counterEls.length) {
    var counterObs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) { animateCounter(e.target); counterObs.unobserve(e.target); }
      });
    }, { threshold: 0.3 });
    counterEls.forEach(function(el) { counterObs.observe(el); });
  }

  // === 4. STAGGERED REVEAL FOR GRID CHILDREN ===
  var grids = document.querySelectorAll('.steps-grid, .pricing-grid, .faq-list');
  var gridObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (!entry.isIntersecting) return;
      var children = entry.target.querySelectorAll('.step-card, .pricing-card, .faq-item');
      children.forEach(function(child, i) {
        child.style.opacity = '0';
        child.style.transform = 'translateY(32px)';
        child.style.transition = 'opacity .8s cubic-bezier(.16,1,.3,1), transform .8s cubic-bezier(.16,1,.3,1)';
        child.style.transitionDelay = (i * 0.12) + 's';
        requestAnimationFrame(function() {
          requestAnimationFrame(function() {
            child.style.opacity = '1';
            child.style.transform = 'translateY(0)';
          });
        });
      });
      gridObs.unobserve(entry.target);
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });
  grids.forEach(function(el) { gridObs.observe(el); });

  // === 5. HERO PHONE PARALLAX ===
  var heroEl = document.querySelector('.hero');
  var heroPhone = document.querySelector('.hero-phone');
  if (heroEl && heroPhone) {
    var pTicking = false;
    window.addEventListener('scroll', function() {
      if (pTicking) return;
      pTicking = true;
      requestAnimationFrame(function() {
        var y = window.scrollY;
        var hh = heroEl.offsetHeight;
        if (y < hh) {
          heroPhone.style.transform = 'translateY(' + (y * 0.06) + 'px)';
        }
        pTicking = false;
      });
    }, { passive: true });
  }

  // === 6. PRICING FEATURED GRADIENT BORDER ===
  var featured = document.querySelector('.pricing-card.featured');
  if (featured) featured.classList.add('gradient-border');

  // === 7. DIRECTION-AWARE HEADER SHADOW ===
  var header = document.querySelector('.site-header');
  if (header) {
    var lastScrollY = 0;
    window.addEventListener('scroll', function() {
      var y = window.scrollY;
      if (y > 100) {
        var dir = y > lastScrollY ? 'down' : 'up';
        header.style.boxShadow = dir === 'down'
          ? '0 2px 0 rgba(0,0,0,.02), 0 8px 32px rgba(0,0,0,.04)'
          : '0 1px 0 rgba(0,0,0,.02), 0 4px 16px rgba(0,0,0,.03)';
      }
      lastScrollY = y;
    }, { passive: true });
  }

  // === 8. SMOOTH SECTION ENTRY ===
  var sectionHeaders = document.querySelectorAll('.section-header');
  var secObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (!entry.isIntersecting) return;
      var label = entry.target.querySelector('.section-label');
      var title = entry.target.querySelector('.section-title');
      var subtitle = entry.target.querySelector('.section-subtitle');
      [label, title, subtitle].forEach(function(el, i) {
        if (!el) return;
        el.style.opacity = '0';
        el.style.transform = 'translateY(24px)';
        el.style.transition = 'opacity .7s cubic-bezier(.16,1,.3,1), transform .7s cubic-bezier(.16,1,.3,1)';
        el.style.transitionDelay = (i * 0.12) + 's';
        requestAnimationFrame(function() {
          requestAnimationFrame(function() {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
          });
        });
      });
      secObs.unobserve(entry.target);
    });
  }, { threshold: 0.15 });
  sectionHeaders.forEach(function(el) { secObs.observe(el); });

  // === 9. PRICING CARD HOVER GLOW ===
  document.querySelectorAll('.pricing-card').forEach(function(card) {
    card.addEventListener('mousemove', function(e) {
      var rect = card.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;
      card.style.setProperty('--glow-x', x + 'px');
      card.style.setProperty('--glow-y', y + 'px');
    });
  });

  // === 10. TESTIMONIAL CARD DEPTH ON HOVER ===
  document.querySelectorAll('.testimonial-card').forEach(function(card) {
    card.addEventListener('mousemove', function(e) {
      var rect = card.getBoundingClientRect();
      var x = (e.clientX - rect.left) / rect.width;
      var y = (e.clientY - rect.top) / rect.height;
      var rotateX = (0.5 - y) * 4;
      var rotateY = (x - 0.5) * 4;
      card.style.transform = 'translateY(-8px) perspective(800px) rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg)';
    });
    card.addEventListener('mouseleave', function() {
      card.style.transform = '';
    });
  });

  // === 11. STEP CARD 3D TILT ===
  document.querySelectorAll('.step-card').forEach(function(card) {
    card.addEventListener('mousemove', function(e) {
      var rect = card.getBoundingClientRect();
      var x = (e.clientX - rect.left) / rect.width;
      var y = (e.clientY - rect.top) / rect.height;
      var rotateX = (0.5 - y) * 6;
      var rotateY = (x - 0.5) * 6;
      card.style.transform = 'translateY(-10px) scale(1.01) perspective(600px) rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg)';
    });
    card.addEventListener('mouseleave', function() {
      card.style.transform = '';
    });
  });

  // === 12. AI CALL WORKFLOW VISUALIZER ===
  var wfSection = document.getElementById('call-workflow');
  var wfTrack = document.getElementById('wfTrack');
  if (wfSection && wfTrack) {
    var wfNodes = wfTrack.querySelectorAll('.wf-node');
    var wfSvg = document.getElementById('wfLines');
    var wfLineEls = wfSvg ? wfSvg.querySelectorAll('.wf-line') : [];
    var wfPulse = wfSvg ? wfSvg.querySelector('.wf-pulse') : null;

    function positionWfLines() {
      if (!wfSvg || wfNodes.length < 2) return;
      var trackRect = wfTrack.getBoundingClientRect();
      var centers = [];
      wfNodes.forEach(function(node) {
        var r = node.getBoundingClientRect();
        centers.push({
          x: r.left + r.width / 2 - trackRect.left,
          y: r.top + r.height / 2 - trackRect.top
        });
      });
      for (var i = 0; i < wfLineEls.length && i < centers.length - 1; i++) {
        wfLineEls[i].setAttribute('x1', centers[i].x);
        wfLineEls[i].setAttribute('y1', centers[i].y);
        wfLineEls[i].setAttribute('x2', centers[i + 1].x);
        wfLineEls[i].setAttribute('y2', centers[i + 1].y);
      }
      wfSvg.setAttribute('viewBox', '0 0 ' + trackRect.width + ' ' + trackRect.height);
    }

    positionWfLines();
    window.addEventListener('resize', positionWfLines);

    function animateWfPulse(lineEl) {
      if (!wfPulse) return;
      var x1 = parseFloat(lineEl.getAttribute('x1'));
      var y1 = parseFloat(lineEl.getAttribute('y1'));
      var x2 = parseFloat(lineEl.getAttribute('x2'));
      var y2 = parseFloat(lineEl.getAttribute('y2'));
      wfPulse.setAttribute('cx', x1);
      wfPulse.setAttribute('cy', y1);
      wfPulse.setAttribute('opacity', '1');
      var startT = performance.now();
      var dur = 300;
      function step(now) {
        var t = Math.min((now - startT) / dur, 1);
        var ease = t * (2 - t);
        wfPulse.setAttribute('cx', x1 + (x2 - x1) * ease);
        wfPulse.setAttribute('cy', y1 + (y2 - y1) * ease);
        if (t < 1) { requestAnimationFrame(step); }
        else { wfPulse.setAttribute('opacity', '0'); }
      }
      requestAnimationFrame(step);
    }

    var wfDone = false;
    var wfObs = new IntersectionObserver(function(entries) {
      if (wfDone) return;
      entries.forEach(function(entry) {
        if (!entry.isIntersecting) return;
        wfDone = true;
        wfObs.unobserve(wfSection);
        positionWfLines();
        var stepDelay = 400;
        wfNodes.forEach(function(node, i) {
          setTimeout(function() {
            node.classList.add('active');
            if (i > 0 && wfLineEls[i - 1]) {
              wfLineEls[i - 1].classList.add('active');
              animateWfPulse(wfLineEls[i - 1]);
            }
          }, i * stepDelay);
        });
      });
    }, { threshold: 0.15 });
    wfObs.observe(wfSection);

    // === 12b. TOGGLE: Workflow ↔ Outputs ===
    var wfTabW = document.getElementById('wfTabWorkflow');
    var wfTabO = document.getElementById('wfTabOutputs');
    var wfOutputs = document.getElementById('wfOutputs');

    function switchWfView(view) {
      var isWorkflow = view === 'workflow';
      if (wfTabW) { wfTabW.classList.toggle('active', isWorkflow); wfTabW.setAttribute('aria-selected', isWorkflow); }
      if (wfTabO) { wfTabO.classList.toggle('active', !isWorkflow); wfTabO.setAttribute('aria-selected', !isWorkflow); }
      if (wfTrack) wfTrack.hidden = !isWorkflow;
      if (wfOutputs) wfOutputs.hidden = isWorkflow;
      if (isWorkflow) positionWfLines();
    }

    if (wfTabW) wfTabW.addEventListener('click', function() { switchWfView('workflow'); });
    if (wfTabO) wfTabO.addEventListener('click', function() { switchWfView('outputs'); });

    // Keyboard: arrow keys between tabs
    [wfTabW, wfTabO].forEach(function(tab) {
      if (!tab) return;
      tab.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          e.preventDefault();
          var other = tab === wfTabW ? wfTabO : wfTabW;
          if (other) { other.focus(); other.click(); }
        }
      });
    });

    // === 12c. NODE → OUTPUT LINKING ===
    var wfNodeMap = { '2': 'summary', '3': 'booking', '4': 'text' };
    var wfOutputMap = { 'summary': '2', 'booking': '3', 'text': '4' };
    var wfHighlightTimer = null;

    function highlightOutput(outputId) {
      if (!wfOutputs) return;
      var card = wfOutputs.querySelector('[data-wf-output="' + outputId + '"]');
      if (!card) return;
      switchWfView('outputs');
      // Clear any previous highlight
      wfOutputs.querySelectorAll('.wf-highlight').forEach(function(c) { c.classList.remove('wf-highlight'); });
      card.classList.add('wf-highlight');
      if (wfHighlightTimer) clearTimeout(wfHighlightTimer);
      wfHighlightTimer = setTimeout(function() { card.classList.remove('wf-highlight'); }, 1200);
    }

    wfNodes.forEach(function(node) {
      var link = node.getAttribute('data-wf-link');
      if (!link) return;
      node.addEventListener('click', function() { highlightOutput(link); });
    });

    // Output card hover → highlight matching workflow node
    if (wfOutputs) {
      wfOutputs.querySelectorAll('.wf-output-card').forEach(function(card) {
        var outputId = card.getAttribute('data-wf-output');
        var nodeIdx = wfOutputMap[outputId];
        if (!nodeIdx) return;
        var matchNode = wfTrack.querySelector('[data-wf="' + nodeIdx + '"]');
        if (!matchNode) return;
        card.addEventListener('mouseenter', function() { matchNode.classList.add('wf-linked'); });
        card.addEventListener('mouseleave', function() { matchNode.classList.remove('wf-linked'); });
      });
    }

    // === 12d. CONSOLE SYNC (optional — only if demo-console dispatches events) ===
    var consoleSyncDone = false;
    var consoleTimes = [
      { t: 0, node: 0 },
      { t: 2, node: 1 },
      { t: 5, node: 2 },
      { t: 9, node: 3 },
      { t: 12, node: 4 },
      { t: 15, node: 5 }
    ];
    document.addEventListener('tct:console-time', function(e) {
      if (consoleSyncDone) return;
      var time = e.detail && e.detail.time;
      if (typeof time !== 'number') return;
      consoleTimes.forEach(function(step) {
        var node = wfTrack.querySelector('[data-wf="' + step.node + '"]');
        if (!node) return;
        if (time >= step.t && !node.classList.contains('active')) {
          node.classList.add('active');
          if (step.node > 0 && wfLineEls[step.node - 1]) {
            wfLineEls[step.node - 1].classList.add('active');
            animateWfPulse(wfLineEls[step.node - 1]);
          }
        }
      });
      if (time >= 15) consoleSyncDone = true;
    });
    document.addEventListener('tct:console-play', function() {
      // Reset nodes for a fresh sync run
      consoleSyncDone = false;
      switchWfView('workflow');
      wfNodes.forEach(function(n) { n.classList.remove('active'); });
      wfLineEls.forEach(function(l) { l.classList.remove('active'); });
    });
  }

})();
