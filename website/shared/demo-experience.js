/* ============================================
   DEMO EXPERIENCE ENGINE v1 — 10/10
   Phone UI, Web Audio waveform, personalization,
   conversion overlay, analytics.
   ============================================ */
(function() {
  'use strict';

  // === CONFIG ===
  var AUDIO_SRC = '/assets/demo/jessica-demo.wav';
  var PILOT_URL = '/pilot/';
  var DEFAULT_BIZ = 'Your Business';
  var GHL_LOCATION = 'tQb9YmrGDrdVUJYPKrsY';

  // === TRANSCRIPT (dynamic — {BIZ} replaced at runtime) ===
  function getTranscript(biz) {
    return [
      { speaker: 'AI', text: 'Thank you for calling ' + biz + ', this is Jessica speaking\u2014how can I help you today?', start: 0.5, end: 4.0 },
      { speaker: 'Caller', text: 'Hey, my AC just quit on me and it\u2019s gotta be close to a hundred degrees in here. I\u2019ve got two little kids.', start: 5.0, end: 8.5 },
      { speaker: 'AI', text: 'Oh no, I\u2019m so sorry. Let\u2019s get someone out to you right away. Can I grab your address?', start: 8.5, end: 11.5 },
      { speaker: 'Caller', text: 'Yeah, it\u2019s 142 Oak Street in Nashville. It\u2019s a Trane unit, about eight years old.', start: 11.5, end: 14.5 },
      { speaker: 'AI', text: 'Got it\u2014142 Oak Street, Trane system. I have a certified tech available this afternoon between 2 and 4. Sound good?', start: 14.5, end: 18.0 }
    ];
  }

  // === STATE ===
  var bizName = DEFAULT_BIZ;
  var audioCtx = null;
  var analyser = null;
  var audioSource = null;
  var audioEl = null;
  var animFrame = null;
  var bars = [];
  var playing = false;
  var done = false;
  var callTimer = null;
  var callSeconds = 0;
  var overlayShown = false;

  // === INIT ===
  function init() {
    var section = document.getElementById('demo-10');
    if (!section) return;

    // Business name input
    var input = document.getElementById('demoBizInput');
    if (input) {
      input.addEventListener('input', function() {
        bizName = this.value.trim() || DEFAULT_BIZ;
        updateBizName();
        track('demo_form_input', { business_name: bizName });
      });
      input.addEventListener('focus', function() {
        track('demo_form_focus');
      });
    }

    // Build audio
    audioEl = document.getElementById('demoAudio');
    if (!audioEl) {
      audioEl = document.createElement('audio');
      audioEl.id = 'demoAudio';
      audioEl.preload = 'auto';
      audioEl.src = AUDIO_SRC;
      section.appendChild(audioEl);
    }

    // Build waveform bars
    var waveformEl = document.getElementById('demoWaveform');
    if (waveformEl) {
      bars = [];
      for (var i = 0; i < 48; i++) {
        var bar = document.createElement('div');
        bar.className = 'dc-bar';
        var h = 20 + Math.random() * 75;
        var pos = i / 48;
        if (pos < 0.06 || pos > 0.94) h *= 0.3;
        else if (pos > 0.15 && pos < 0.35) h *= 1.2;
        else if (pos > 0.55 && pos < 0.72) h *= 1.3;
        bar.style.height = Math.min(100, Math.max(8, h)) + '%';
        waveformEl.appendChild(bar);
        bars.push(bar);
      }
    }

    // Play button
    var playBtn = document.getElementById('demoPlayBtn');
    if (playBtn) {
      playBtn.addEventListener('click', function() {
        if (done) { resetDemo(); done = false; }
        togglePlay();
      });
    }

    // Waveform click to seek
    if (waveformEl) {
      waveformEl.addEventListener('click', function(e) {
        if (!audioEl || !audioEl.duration) return;
        var rect = waveformEl.getBoundingClientRect();
        var pct = (e.clientX - rect.left) / rect.width;
        audioEl.currentTime = pct * audioEl.duration;
        if (!playing) togglePlay();
      });
    }

    // Audio events
    if (audioEl) {
      audioEl.addEventListener('timeupdate', onTimeUpdate);
      audioEl.addEventListener('ended', onComplete);
      audioEl.addEventListener('loadedmetadata', function() {
        var durEl = document.getElementById('demoDuration');
        if (durEl) durEl.textContent = '0:00 / ' + fmt(audioEl.duration);
      });
    }

    // Overlay close
    var closeBtn = document.getElementById('demoOverlayClose');
    if (closeBtn) {
      closeBtn.addEventListener('click', hideOverlay);
    }

    // Text me capture
    var textBtn = document.getElementById('demoTextBtn');
    if (textBtn) {
      textBtn.addEventListener('click', capturePhone);
    }

    // Overlay CTA
    var ctaBtn = document.getElementById('demoOverlayCta');
    if (ctaBtn) {
      ctaBtn.addEventListener('click', function() {
        track('demo_cta_clicked', { business_name: bizName });
        trackMeta('Lead', { content_name: 'demo_cta', value: 97 });
      });
    }

    // Escape key closes overlay
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') hideOverlay();
    });

    // Set initial business name
    updateBizName();
  }

  // === WEB AUDIO API ===
  function initAudioContext() {
    if (audioCtx) return;
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 128;
      analyser.smoothingTimeConstant = 0.75;
      audioSource = audioCtx.createMediaElementSource(audioEl);
      audioSource.connect(analyser);
      analyser.connect(audioCtx.destination);
    } catch(e) {
      // Fallback — no Web Audio API
      audioCtx = null;
    }
  }

  function animateWaveform() {
    if (!playing) return;
    animFrame = requestAnimationFrame(animateWaveform);

    if (analyser) {
      var data = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(data);

      for (var i = 0; i < bars.length; i++) {
        var dataIdx = Math.floor(i * data.length / bars.length);
        var val = data[dataIdx] / 255;
        var minH = 8;
        var maxH = 95;
        var h = minH + val * (maxH - minH);
        bars[i].style.height = h + '%';
        bars[i].style.transition = 'height 0.08s ease';

        // Color based on progress
        var pct = audioEl ? audioEl.currentTime / audioEl.duration : 0;
        var barPos = i / bars.length;
        if (barPos < pct) {
          bars[i].className = 'dc-bar played';
        } else if (Math.abs(barPos - pct) < 0.03) {
          bars[i].className = 'dc-bar active';
        } else {
          bars[i].className = 'dc-bar';
        }
      }
    } else {
      // Fallback animation without Web Audio
      var pct = audioEl ? audioEl.currentTime / audioEl.duration : 0;
      for (var j = 0; j < bars.length; j++) {
        var barPos = j / bars.length;
        if (barPos < pct) bars[j].className = 'dc-bar played';
        else if (Math.abs(barPos - pct) < 0.03) bars[j].className = 'dc-bar active';
        else bars[j].className = 'dc-bar';

        // Simulated bounce
        var baseH = parseFloat(bars[j].getAttribute('data-h') || bars[j].style.height);
        if (!bars[j].getAttribute('data-h')) bars[j].setAttribute('data-h', bars[j].style.height);
        var bounce = barPos < pct ? (0.6 + 0.4 * Math.sin(Date.now() / 200 + j)) : 1;
        bars[j].style.height = (parseFloat(baseH) * bounce) + '%';
      }
    }
  }

  // === PLAYBACK ===
  function togglePlay() {
    if (playing) {
      pauseDemo();
    } else {
      playDemo();
    }
  }

  function playDemo() {
    if (!audioEl) return;
    // Lazy load audio on first play
    if (audioEl.preload === 'none') {
      audioEl.preload = 'auto';
      audioEl.load();
    }
    initAudioContext();
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }

    audioEl.play().then(function() {
      playing = true;
      setPlayIcon('pause');
      startCallTimer();
      animateWaveform();
      updateCallBar('active');
      track('demo_play', { business_name: bizName });
      trackMeta('ViewContent', { content_name: 'demo_play' });
    }).catch(function() {
      // Autoplay blocked — show visual-only
      playing = true;
      setPlayIcon('pause');
      startCallTimer();
      updateCallBar('active');
    });
  }

  function pauseDemo() {
    playing = false;
    if (audioEl) audioEl.pause();
    if (animFrame) cancelAnimationFrame(animFrame);
    setPlayIcon('play');
    stopCallTimer();
  }

  function resetDemo() {
    playing = false;
    done = false;
    callSeconds = 0;
    if (audioEl) { audioEl.pause(); audioEl.currentTime = 0; }
    if (animFrame) cancelAnimationFrame(animFrame);
    setPlayIcon('play');
    stopCallTimer();
    updateCallBar('ringing');

    var timerEl = document.getElementById('phoneCallTimer');
    if (timerEl) timerEl.textContent = '0:00';

    var durEl = document.getElementById('demoDuration');
    if (durEl && audioEl) durEl.textContent = '0:00 / ' + fmt(audioEl.duration || 18);

    bars.forEach(function(b) {
      b.className = 'dc-bar';
      if (b.getAttribute('data-h')) b.style.height = b.getAttribute('data-h');
    });

    // Reset transcript
    var lines = document.querySelectorAll('#demoTranscript .dc-line');
    lines.forEach(function(l) { l.classList.remove('highlight', 'spoken'); });

    // Reset progress
    var progEl = document.getElementById('demoProgressFill');
    if (progEl) progEl.style.width = '0%';
  }

  function onTimeUpdate() {
    if (!audioEl) return;
    var t = audioEl.currentTime;
    var dur = audioEl.duration || 18;
    var pct = t / dur;

    // Duration display
    var durEl = document.getElementById('demoDuration');
    if (durEl) durEl.textContent = fmt(t) + ' / ' + fmt(dur);

    // Progress bar
    var progEl = document.getElementById('demoProgressFill');
    if (progEl) progEl.style.width = (pct * 100) + '%';

    // Transcript sync
    syncTranscript(t);
  }

  function onComplete() {
    playing = false;
    done = true;
    if (animFrame) cancelAnimationFrame(animFrame);
    setPlayIcon('check');
    stopCallTimer();
    bars.forEach(function(b) { b.className = 'dc-bar played'; });

    var progEl = document.getElementById('demoProgressFill');
    if (progEl) progEl.style.width = '100%';

    track('demo_complete', { business_name: bizName, duration: callSeconds });
    trackMeta('CompleteRegistration', { content_name: 'demo_complete' });

    // Show conversion overlay after 1.5s
    setTimeout(showOverlay, 1500);
  }

  // === TRANSCRIPT ===
  function syncTranscript(t) {
    var lines = document.querySelectorAll('#demoTranscript .dc-line');
    lines.forEach(function(line) {
      var s = parseFloat(line.getAttribute('data-start') || 0);
      var e = parseFloat(line.getAttribute('data-end') || 999);
      if (t >= s && t < e) { line.classList.add('highlight'); line.classList.remove('spoken'); }
      else if (t >= e) { line.classList.remove('highlight'); line.classList.add('spoken'); }
      else { line.classList.remove('highlight', 'spoken'); }
    });
  }

  function buildTranscript() {
    var el = document.getElementById('demoTranscript');
    if (!el) return;
    var transcript = getTranscript(bizName);
    var html = '';
    transcript.forEach(function(l) {
      var cls = l.speaker === 'Caller' ? 'dc-caller' : 'dc-ai';
      html += '<div class="dc-line" data-start="' + l.start + '" data-end="' + l.end + '">';
      html += '<span class="dc-speaker ' + cls + '">' + l.speaker + '</span>';
      html += '<span class="dc-text">\u201c' + l.text + '\u201d</span>';
      html += '</div>';
    });
    el.innerHTML = html;
  }

  // === BUSINESS NAME ===
  function updateBizName() {
    // Phone caller name
    var callerName = document.getElementById('phoneCallerName');
    if (callerName) callerName.textContent = bizName;

    // Rebuild transcript with new name
    buildTranscript();

    // Overlay text
    var overlayBiz = document.querySelectorAll('.biz-name-inject');
    overlayBiz.forEach(function(el) {
      el.textContent = bizName;
    });
  }

  // === CALL TIMER ===
  function startCallTimer() {
    stopCallTimer();
    callTimer = setInterval(function() {
      callSeconds++;
      var timerEl = document.getElementById('phoneCallTimer');
      if (timerEl) timerEl.textContent = fmt(callSeconds);
    }, 1000);
  }

  function stopCallTimer() {
    if (callTimer) { clearInterval(callTimer); callTimer = null; }
  }

  function updateCallBar(state) {
    var bar = document.getElementById('phoneCallBar');
    if (!bar) return;
    bar.classList.remove('ringing', 'active');
    bar.classList.add(state);
    var statusEl = document.getElementById('phoneCallStatus');
    if (statusEl) {
      statusEl.textContent = state === 'active' ? 'CONNECTED' : 'INCOMING CALL';
    }
  }

  // === CONVERSION OVERLAY ===
  function showOverlay() {
    if (overlayShown) return;
    overlayShown = true;
    var overlay = document.getElementById('demoOverlay');
    if (overlay) overlay.classList.add('show');
    track('demo_overlay_shown', { business_name: bizName });
  }

  function hideOverlay() {
    overlayShown = false;
    var overlay = document.getElementById('demoOverlay');
    if (overlay) overlay.classList.remove('show');
  }

  // === TEXT ME CAPTURE ===
  function capturePhone() {
    var phoneInput = document.getElementById('demoTextPhone');
    var phone = phoneInput ? phoneInput.value.trim() : '';
    if (!phone || phone.length < 10) {
      if (phoneInput) phoneInput.style.borderColor = '#ef4444';
      setTimeout(function() { if (phoneInput) phoneInput.style.borderColor = ''; }, 2000);
      return;
    }

    // Format phone
    var cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 10) cleaned = '1' + cleaned;
    if (cleaned.length === 11 && cleaned[0] === '1') cleaned = '+' + cleaned;

    track('demo_text_me_clicked', { phone: cleaned, business_name: bizName });
    trackMeta('Lead', { content_name: 'demo_text_me', value: 0 });

    // Send to GHL via API (create/update contact)
    try {
      var ghlData = {
        phone: cleaned,
        tags: ['demo-text-me', 'website-demo'],
        source: 'website-demo',
        customField: []
      };
      if (bizName !== DEFAULT_BIZ) {
        ghlData.companyName = bizName;
      }
      // Fire and forget — GHL contact creation
      fetch('/api/ghl/contacts/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + TCT_PROXY_SECRET,
          'Version': '2021-07-28'
        },
        body: JSON.stringify(Object.assign({ locationId: GHL_LOCATION }, ghlData))
      }).catch(function() {});
    } catch(e) {}

    // UI feedback
    var captureForm = document.getElementById('demoTextCapture');
    var sentMsg = document.getElementById('demoTextSent');
    if (captureForm) captureForm.style.display = 'none';
    if (sentMsg) sentMsg.classList.add('show');
  }

  // === HELPERS ===
  function fmt(s) {
    if (!s || !isFinite(s)) return '0:00';
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
  }

  function setPlayIcon(type) {
    var btn = document.getElementById('demoPlayBtn');
    if (!btn) return;
    if (type === 'pause') btn.innerHTML = '<svg viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16" fill="currentColor"/><rect x="14" y="4" width="4" height="16" fill="currentColor"/></svg>';
    else if (type === 'check') btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
    else btn.innerHTML = '<svg viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21" fill="currentColor"/></svg>';
  }

  // === ANALYTICS ===
  function track(name, data) {
    data = data || {};
    try {
      if (typeof gtag === 'function') gtag('event', name, data);
    } catch(e) {}
    try {
      if (typeof tctTrack === 'function') tctTrack(name, data);
    } catch(e) {}
  }

  function trackMeta(event, data) {
    data = data || {};
    try {
      if (typeof fbq === 'function') fbq('track', event, data);
    } catch(e) {}
  }

  // === BOOT ===
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
