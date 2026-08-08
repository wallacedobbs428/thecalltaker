/* ============================================
   THE CALL TAKER — Conversion Engine (v1)
   Phase 2: Adaptive CTAs based on intent score
   Phase 3: Demo→Pilot bridge after completion
   Depends on: tct-intent.js (TCT_Intent global)
   ============================================ */
(function() {
  'use strict';

  // === Phase 2: Adaptive CTAs ===

  var CTA_TIERS = {
    early: {
      text: 'Hear the AI in Action',
      href: '#demo',
      className: 'btn btn-outline'
    },
    mid: {
      text: 'See Pricing & Plans',
      href: '#pricing',
      className: 'btn btn-primary'
    },
    high: {
      text: 'Request Setup Review',
      href: '/pilot/',
      className: 'btn btn-primary btn-glow'
    }
  };

  function updateAdaptiveCTAs() {
    if (!window.TCT_Intent) return;
    var tier = TCT_Intent.tier();
    var cta = CTA_TIERS[tier];
    if (!cta) return;

    var adaptiveEls = document.querySelectorAll('[data-adaptive-cta]');
    adaptiveEls.forEach(function(el) {
      // Don't override if user already clicked a higher-tier CTA
      if (el.getAttribute('data-cta-locked') === 'true') return;

      if (el.tagName === 'A') {
        el.href = cta.href;
        el.textContent = cta.text;
        el.className = cta.className;
      } else if (el.tagName === 'BUTTON') {
        el.textContent = cta.text;
        el.className = cta.className;
      }
    });

    // Fire GA4 event for CTA tier change
    if (typeof gtag === 'function') {
      gtag('event', 'tct_cta_tier', {
        tier: tier,
        score: TCT_Intent.score()
      });
    }
  }

  // Listen for intent updates
  document.addEventListener('tct:intent_update', updateAdaptiveCTAs);

  // === Phase 3: Demo→Pilot Bridge ===

  var bridgeShown = false;

  function showPilotBridge() {
    if (bridgeShown) return;
    if (sessionStorage.getItem('tct_bridge_dismissed')) return;
    bridgeShown = true;

    // Inject bridge CSS
    var style = document.createElement('style');
    style.textContent =
      '#tct-pilot-bridge { display:none; position:fixed; bottom:0; left:0; right:0; z-index:99998; ' +
      'background:linear-gradient(135deg, #1e3a5f 0%, #0f2440 100%); color:#fff; ' +
      'padding:28px 24px 24px; box-shadow:0 -8px 40px rgba(0,0,0,.25); ' +
      'transform:translateY(100%); transition:transform .5s cubic-bezier(.34,1.56,.64,1); }' +
      '#tct-pilot-bridge.visible { display:block; transform:translateY(0); }' +
      '#tct-pilot-bridge.slide-up { display:block; }' +
      '.tpb-inner { max-width:720px; margin:0 auto; text-align:center; }' +
      '.tpb-close { position:absolute; top:10px; right:16px; background:none; border:none; ' +
      'color:rgba(255,255,255,.5); font-size:24px; cursor:pointer; padding:4px 8px; }' +
      '.tpb-close:hover { color:#fff; }' +
      '.tpb-title { font-size:1.25rem; font-weight:800; margin:0 0 10px; line-height:1.3; }' +
      '.tpb-bullets { list-style:none; padding:0; margin:0 0 16px; display:flex; ' +
      'justify-content:center; gap:20px; flex-wrap:wrap; font-size:.85rem; color:rgba(255,255,255,.85); }' +
      '.tpb-bullets li::before { content:"\\2713 "; color:#22c55e; font-weight:700; margin-right:4px; }' +
      '.tpb-actions { display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }' +
      '.tpb-btn { display:inline-block; padding:12px 28px; border-radius:8px; font-weight:700; ' +
      'font-size:.95rem; text-decoration:none; transition:all .2s; cursor:pointer; border:none; }' +
      '.tpb-btn-primary { background:#ea580c; color:#fff; }' +
      '.tpb-btn-primary:hover { background:#c2410c; transform:scale(1.03); }' +
      '.tpb-btn-secondary { background:rgba(255,255,255,.12); color:#fff; border:1px solid rgba(255,255,255,.2); }' +
      '.tpb-btn-secondary:hover { background:rgba(255,255,255,.2); }' +
      '@media(max-width:600px) { .tpb-bullets { flex-direction:column; gap:6px; align-items:center; } ' +
      '.tpb-actions { flex-direction:column; } .tpb-btn { width:100%; text-align:center; } }';
    document.head.appendChild(style);

    // Build bridge HTML
    var bridge = document.createElement('div');
    bridge.id = 'tct-pilot-bridge';
    bridge.innerHTML =
      '<button class="tpb-close" aria-label="Close">&times;</button>' +
      '<div class="tpb-inner">' +
        '<div class="tpb-title">Want This Answering Your Calls Tonight?</div>' +
        '<ul class="tpb-bullets">' +
          '<li>Free setup-review pilot, no payment collected before review</li>' +
          '<li>Works with your existing phone number</li>' +
          '<li>Live in under 10 minutes</li>' +
        '</ul>' +
        '<div class="tpb-actions">' +
          '<a href="/start" class="tpb-btn tpb-btn-primary">Request Setup Review</a>' +
          '<a href="#pricing" class="tpb-btn tpb-btn-secondary">See Plans & Pricing</a>' +
        '</div>' +
      '</div>';

    document.body.appendChild(bridge);

    // Animate in after repaint
    requestAnimationFrame(function() {
      bridge.classList.add('slide-up');
      requestAnimationFrame(function() {
        bridge.classList.add('visible');
      });
    });

    // Close handler
    bridge.querySelector('.tpb-close').addEventListener('click', function() {
      bridge.classList.remove('visible');
      sessionStorage.setItem('tct_bridge_dismissed', '1');
      setTimeout(function() { bridge.remove(); }, 500);
    });

    // Track clicks
    bridge.querySelectorAll('.tpb-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var action = this.classList.contains('tpb-btn-primary') ? 'pilot_click' : 'pricing_click';
        if (typeof gtag === 'function') {
          gtag('event', 'tct_bridge_' + action, { source: 'demo_bridge' });
        }
      });
    });

    // Track bridge impression
    if (typeof gtag === 'function') {
      gtag('event', 'tct_bridge_shown', {
        trigger: 'demo_preview_playback_end_ui',
        intent_score: window.TCT_Intent ? TCT_Intent.score() : 0
      });
    }
  }

  // === Bridge Triggers ===

  // Trigger 1: Demo console completion
  document.addEventListener('tct:intent_update', function(e) {
    if (e.detail && e.detail.signal === 'demo_preview_playback_end_ui') {
      // Delay slightly so user sees completion state first
      setTimeout(showPilotBridge, 1500);
    }
  });

  // Trigger 2: High intent score (60+) on any page with demo
  document.addEventListener('tct:intent_update', function(e) {
    if (e.detail && e.detail.score >= 60) {
      // Only show if there's a demo console on the page
      if (document.querySelector('.dc') || document.querySelector('.demo-section')) {
        setTimeout(showPilotBridge, 2000);
      }
    }
  });

  // === Init adaptive CTAs on DOM ready ===
  function init() {
    // Initial CTA update
    if (window.TCT_Intent && TCT_Intent.score() > 0) {
      updateAdaptiveCTAs();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
