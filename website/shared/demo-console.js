/* ============================================
   CALL SESSION VIEWER — Reusable Component v2
   initDemoConsole(el, options) API.
   Tabs, industry datasets, live field-fill,
   transcript sync, completion state.
   Zero external deps.
   ============================================ */
(function() {
  'use strict';

  var REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // === INDUSTRY DATASETS ===
  var INDUSTRIES = {
    hvac: {
      label: 'HVAC',
      transcript: [
        { speaker: 'Caller', text: 'My AC stopped working and it\u2019s 95 degrees in here. Can someone come out today?', start: 0, end: 5 },
        { speaker: 'AI', text: 'I\u2019m sorry to hear that \u2014 I can get a technician out to you right away. What\u2019s your address?', start: 5, end: 11 },
        { speaker: 'Caller', text: '142 Oak Street, Nashville.', start: 11, end: 14 },
        { speaker: 'AI', text: 'Got it. I have a tech available this afternoon between 2 and 4 PM. I\u2019ll text you a confirmation with all the details.', start: 14, end: 22 },
        { speaker: 'Caller', text: 'That\u2019s perfect, thank you.', start: 22, end: 25 }
      ],
      summary: { name: 'Sarah M.', issue: 'AC not cooling \u2014 95\u00b0 inside', location: '142 Oak St, Nashville', urgency: 'High \u2014 emergency' },
      booking: { service: 'AC Repair', time: 'Today 2\u20134 PM', tech: 'Next available', address: '142 Oak St, Nashville' },
      textMsg: 'New lead from The Call Taker:\nSarah M. needs AC repair ASAP.\n142 Oak St, Nashville.\nBooked today 2\u20134 PM.\nCall back: (615) 555-0142',
      result: 'Job booked. Text sent. $800 saved.'
    },
    plumbing: {
      label: 'Plumbing',
      transcript: [
        { speaker: 'Caller', text: 'I have a burst pipe flooding my kitchen! I need someone now!', start: 0, end: 4 },
        { speaker: 'AI', text: 'I\u2019m dispatching an emergency plumber right away. What\u2019s your address so I can send the closest tech?', start: 4, end: 10 },
        { speaker: 'Caller', text: '88 Elm Drive, apartment 4B.', start: 10, end: 13 },
        { speaker: 'AI', text: 'Got it. Turn off the main water valve under your sink if you can. A plumber will be there within 45 minutes.', start: 13, end: 21 },
        { speaker: 'Caller', text: 'Okay, I\u2019ll do that. Thank you so much.', start: 21, end: 25 }
      ],
      summary: { name: 'Mike R.', issue: 'Burst pipe \u2014 kitchen flooding', location: '88 Elm Dr, Apt 4B', urgency: 'Critical \u2014 water damage' },
      booking: { service: 'Emergency Pipe Repair', time: 'Within 45 min', tech: 'Nearest available', address: '88 Elm Dr, Apt 4B' },
      textMsg: 'URGENT lead from The Call Taker:\nMike R. \u2014 burst pipe flooding kitchen.\n88 Elm Dr, Apt 4B.\nDispatched within 45 min.\nCall back: (615) 555-0288',
      result: 'Emergency dispatch. $1,200 job saved.'
    },
    dental: {
      label: 'Dental',
      transcript: [
        { speaker: 'Caller', text: 'I need to reschedule my cleaning appointment. I can\u2019t make it Thursday.', start: 0, end: 5 },
        { speaker: 'AI', text: 'No problem at all. Let me check available times. How does next Tuesday at 10 AM work?', start: 5, end: 11 },
        { speaker: 'Caller', text: 'Tuesday works great.', start: 11, end: 13 },
        { speaker: 'AI', text: 'Perfect. I\u2019ve rescheduled you for Tuesday at 10 AM. You\u2019ll get a text confirmation shortly. Anything else?', start: 13, end: 21 },
        { speaker: 'Caller', text: 'That\u2019s it, thank you!', start: 21, end: 24 }
      ],
      summary: { name: 'Lisa K.', issue: 'Reschedule cleaning', location: 'Existing patient', urgency: 'Low \u2014 routine' },
      booking: { service: 'Dental Cleaning', time: 'Tuesday 10:00 AM', tech: 'Dr. Williams', address: 'On file' },
      textMsg: 'Appointment update:\nLisa K. rescheduled cleaning.\nOld: Thursday \u2192 New: Tuesday 10 AM.\nDr. Williams.\nCall back: (615) 555-0311',
      result: 'Rescheduled. No missed appointment.'
    },
    legal: {
      label: 'Legal',
      transcript: [
        { speaker: 'Caller', text: 'I was just in a car accident and I need to talk to an attorney.', start: 0, end: 4 },
        { speaker: 'AI', text: 'I\u2019m sorry to hear that. Are you safe right now? Let me get your information so an attorney can call you back as soon as possible.', start: 4, end: 12 },
        { speaker: 'Caller', text: 'Yes, I\u2019m okay. My name is James and the accident happened on I-65.', start: 12, end: 17 },
        { speaker: 'AI', text: 'Thank you, James. I have your number. An attorney will call you within the hour. Don\u2019t speak to any insurance adjusters until then.', start: 17, end: 25 }
      ],
      summary: { name: 'James T.', issue: 'Car accident \u2014 I-65', location: 'Nashville area', urgency: 'High \u2014 time-sensitive' },
      booking: { service: 'Free Consultation', time: 'Callback within 1 hour', tech: 'Next available attorney', address: 'Phone consultation' },
      textMsg: 'HOT LEAD from The Call Taker:\nJames T. \u2014 car accident on I-65.\nNeeds attorney ASAP.\nCallback within 1 hour.\nCall back: (615) 555-0477',
      result: 'Client intake captured. Case secured.'
    },
    medspa: {
      label: 'Med Spa',
      transcript: [
        { speaker: 'Caller', text: 'Hi, I\u2019d like to book a Botox appointment. Do you have anything this week?', start: 0, end: 5 },
        { speaker: 'AI', text: 'Absolutely! We have openings on Wednesday at 2 PM and Friday at 11 AM. Which works better for you?', start: 5, end: 11 },
        { speaker: 'Caller', text: 'Wednesday at 2 sounds great.', start: 11, end: 14 },
        { speaker: 'AI', text: 'You\u2019re all set for Wednesday at 2 PM. Is this your first visit? I\u2019ll text you a link to fill out your intake form.', start: 14, end: 22 },
        { speaker: 'Caller', text: 'Yes, first time. Thanks!', start: 22, end: 25 }
      ],
      summary: { name: 'Amanda P.', issue: 'Botox appointment', location: 'New patient', urgency: 'Normal' },
      booking: { service: 'Botox Treatment', time: 'Wednesday 2:00 PM', tech: 'First available', address: 'New patient \u2014 intake sent' },
      textMsg: 'New booking from The Call Taker:\nAmanda P. \u2014 Botox, new patient.\nWednesday 2:00 PM.\nIntake form link sent.\nCall back: (615) 555-0533',
      result: 'Appointment booked. Intake sent.'
    },
    other: {
      label: 'Other',
      transcript: [
        { speaker: 'Caller', text: 'I need someone to come look at my garage door. It won\u2019t close all the way.', start: 0, end: 5 },
        { speaker: 'AI', text: 'I can help with that. Is the door stuck open right now, or does it go partway down and come back up?', start: 5, end: 12 },
        { speaker: 'Caller', text: 'It goes about halfway and then reverses.', start: 12, end: 15 },
        { speaker: 'AI', text: 'That\u2019s usually a sensor or spring issue. I have a tech available tomorrow morning between 9 and 11. Should I book that?', start: 15, end: 24 }
      ],
      summary: { name: 'David W.', issue: 'Garage door won\u2019t close', location: 'Residential', urgency: 'Medium' },
      booking: { service: 'Garage Door Repair', time: 'Tomorrow 9\u201311 AM', tech: 'Next available', address: 'Pending address' },
      textMsg: 'New lead from The Call Taker:\nDavid W. \u2014 garage door issue.\nDoor reverses halfway.\nBooked tomorrow 9\u201311 AM.\nCall back: (615) 555-0621',
      result: 'Service call booked. $350 job saved.'
    }
  };

  function track(name, data) {
    data = data || {};
    if (typeof tctTrack === 'function') tctTrack(name, data);
    else if (typeof gtag === 'function') gtag('event', name, data);
  }

  function fmt(s) {
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
  }

  // ===========================
  // initDemoConsole(el, options)
  // ===========================
  function initDemoConsole(root, opts) {
    opts = opts || {};
    var industry = opts.industry || 'hvac';
    var dark = opts.dark !== undefined ? opts.dark : false;
    var large = opts.large || false;
    var showIndustries = opts.industries !== false;
    var audioSrc = opts.audioSrc || '/assets/demo/demo-call-15s.mp3';

    if (dark) root.classList.add('dc-dark');
    if (large) root.classList.add('dc-large');

    // Build HTML
    root.innerHTML = buildHTML(industry, showIndustries, audioSrc);

    // Refs
    var playBtn = root.querySelector('.dc-play');
    var waveform = root.querySelector('.dc-waveform');
    var durationEl = root.querySelector('.dc-duration');
    var progressFill = root.querySelector('.dc-progress-fill');
    var completeEl = root.querySelector('.dc-complete');
    var audioEl = root.querySelector('audio');
    var tabs = root.querySelectorAll('.dc-tab');
    var panels = root.querySelectorAll('.dc-panel');
    var indBtns = root.querySelectorAll('.dc-ind');

    // State — auto-calculate duration from transcript
    var playing = false;
    var initData = INDUSTRIES[industry];
    var lastLine = initData && initData.transcript ? initData.transcript[initData.transcript.length - 1] : null;
    var audioDuration = lastLine ? lastLine.end : 25;
    var currentTime = 0;
    var simInterval = null;
    var done = false;
    var currentIndustry = industry;
    var hasRealAudio = false;
    var bars = [];
    var barCount = 44;

    // === TTS (text-to-speech) for simulated playback ===
    var ttsSupported = 'speechSynthesis' in window;
    var ttsSpokenLines = {};  // track which lines have been spoken by start time
    var ttsCallerVoice = null;
    var ttsAIVoice = null;

    function ttsPickVoices() {
      if (!ttsSupported) return;
      var voices = speechSynthesis.getVoices();
      if (!voices.length) return;
      // Prefer English voices; use different ones for Caller vs AI
      var en = voices.filter(function(v) { return v.lang && v.lang.startsWith('en'); });
      if (!en.length) en = voices;
      // Try to pick a male-sounding for caller and female-sounding for AI
      var female = en.filter(function(v) { return /samantha|victoria|karen|fiona|allison|susan|zira|female/i.test(v.name); });
      var male = en.filter(function(v) { return /daniel|alex|thomas|david|james|male|guy/i.test(v.name); });
      ttsCallerVoice = (male.length ? male[0] : en[0]) || null;
      ttsAIVoice = (female.length ? female[0] : (en.length > 1 ? en[1] : en[0])) || null;
    }
    if (ttsSupported) {
      ttsPickVoices();
      if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = ttsPickVoices;
      }
    }

    function ttsSpeak(text, isCaller) {
      if (!ttsSupported || REDUCED) return;
      var utter = new SpeechSynthesisUtterance(text);
      utter.rate = isCaller ? 1.05 : 0.95;
      utter.pitch = isCaller ? 1.1 : 0.9;
      utter.volume = 1;
      var voice = isCaller ? ttsCallerVoice : ttsAIVoice;
      if (voice) utter.voice = voice;
      speechSynthesis.speak(utter);
    }

    function ttsCancel() {
      if (ttsSupported) {
        speechSynthesis.cancel();
      }
      ttsSpokenLines = {};
    }

    function ttsSyncLine(t) {
      if (!ttsSupported || hasRealAudio || REDUCED) return;
      var data = INDUSTRIES[currentIndustry];
      if (!data || !data.transcript) return;
      data.transcript.forEach(function(line) {
        var key = line.start + ':' + line.speaker;
        if (t >= line.start && !ttsSpokenLines[key]) {
          ttsSpokenLines[key] = true;
          ttsSpeak(line.text, line.speaker === 'Caller');
        }
      });
    }

    // Generate waveform
    for (var i = 0; i < barCount; i++) {
      var bar = document.createElement('div');
      bar.className = 'dc-bar';
      var h = 20 + Math.random() * 75;
      var pos = i / barCount;
      if (pos < 0.06 || pos > 0.94) h *= 0.3;
      else if (pos > 0.15 && pos < 0.35) h *= 1.2;
      else if (pos > 0.55 && pos < 0.72) h *= 1.3;
      bar.style.height = Math.min(100, Math.max(8, h)) + '%';
      waveform.appendChild(bar);
      bars.push(bar);
    }

    // Audio detection
    if (audioEl) {
      audioEl.addEventListener('loadedmetadata', function() {
        if (audioEl.duration > 0 && isFinite(audioEl.duration)) {
          var simLabel = root.querySelector('.dc-sim-label');
          if (audioEl.duration < 5) {
            // Placeholder file — use TTS-voiced playback
            hasRealAudio = false;
            if (simLabel) {
              simLabel.textContent = ttsSupported ? 'AI-voiced demo' : 'Simulated demo';
              simLabel.classList.toggle('dc-audio-loaded', ttsSupported);
            }
          } else {
            audioDuration = audioEl.duration;
            hasRealAudio = true;
            if (durationEl) durationEl.textContent = '0:00 / ' + fmt(audioDuration);
            if (simLabel) {
              simLabel.textContent = simLabel.getAttribute('data-loaded');
              simLabel.classList.add('dc-audio-loaded');
            }
          }
        }
      });
      audioEl.addEventListener('timeupdate', function() {
        if (!hasRealAudio) return;
        currentTime = audioEl.currentTime;
        tick(currentTime / audioDuration);
      });
      audioEl.addEventListener('ended', onComplete);
      audioEl.addEventListener('error', function() {
        var simLabel = root.querySelector('.dc-sim-label');
        if (simLabel) {
          simLabel.textContent = ttsSupported ? 'AI-voiced demo' : simLabel.getAttribute('data-sim');
          simLabel.classList.toggle('dc-audio-loaded', ttsSupported);
        }
      });
    }

    // Init display
    if (durationEl) durationEl.textContent = '0:00 / ' + fmt(audioDuration);
    if (REDUCED) revealAllOutputs();

    // === Tab navigation ===
    tabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        switchTab(this.getAttribute('data-tab'));
        track('tab_switch', { tab: this.getAttribute('data-tab') });
      });
      // Keyboard: arrow left/right
      tab.addEventListener('keydown', function(e) {
        var idx = Array.prototype.indexOf.call(tabs, this);
        if (e.key === 'ArrowRight' && idx < tabs.length - 1) { e.preventDefault(); tabs[idx + 1].focus(); tabs[idx + 1].click(); }
        if (e.key === 'ArrowLeft' && idx > 0) { e.preventDefault(); tabs[idx - 1].focus(); tabs[idx - 1].click(); }
      });
    });

    function switchTab(name) {
      tabs.forEach(function(t) { t.classList.toggle('active', t.getAttribute('data-tab') === name); });
      panels.forEach(function(p) { p.classList.toggle('active', p.getAttribute('data-panel') === name); });
    }

    // === Industry pills ===
    indBtns.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var ind = this.getAttribute('data-ind');
        if (ind === currentIndustry) return;
        currentIndustry = ind;
        indBtns.forEach(function(b) { b.classList.toggle('active', b.getAttribute('data-ind') === ind); });
        stopPlayback();
        resetState();
        loadIndustry(ind);
        track('industry_switch', { industry: ind });
      });
    });

    function loadIndustry(ind) {
      var data = INDUSTRIES[ind];
      if (!data) return;
      // Recalculate duration from transcript
      var last = data.transcript[data.transcript.length - 1];
      if (last && !hasRealAudio) audioDuration = last.end;
      // Rebuild panels content
      root.querySelector('[data-panel="transcript"]').innerHTML = buildTranscriptPanel(data.transcript);
      root.querySelector('[data-panel="summary"]').innerHTML = buildSummaryPanel(data.summary);
      root.querySelector('[data-panel="booking"]').innerHTML = buildBookingPanel(data.booking);
      root.querySelector('[data-panel="text"]').innerHTML = buildTextPanel(data.textMsg);
      // Reset refs
      completeEl = root.querySelector('.dc-complete');
      if (durationEl) durationEl.textContent = '0:00 / ' + fmt(audioDuration);
    }

    // === Playback ===
    playBtn.addEventListener('click', function() {
      if (done) { resetState(); done = false; }
      togglePlay();
    });

    waveform.addEventListener('click', function(e) {
      var rect = waveform.getBoundingClientRect();
      var pct = (e.clientX - rect.left) / rect.width;
      if (hasRealAudio && audioEl.readyState >= 1) {
        audioEl.currentTime = pct * audioDuration;
        if (!playing) togglePlay();
      }
    });

    function togglePlay() {
      if (playing) {
        stopPlayback();
      } else {
        playing = true;
        setPlayIcon('pause');
        track('audio_play', { section: 'demo_console', industry: currentIndustry });
        try { document.dispatchEvent(new CustomEvent('tct:console-play')); } catch(e) {}
        if (hasRealAudio) {
          audioEl.play().catch(function() { startSimulated(); });
        } else {
          startSimulated();
        }
      }
    }

    function stopPlayback() {
      playing = false;
      setPlayIcon('play');
      if (hasRealAudio) audioEl.pause();
      if (simInterval) { clearInterval(simInterval); simInterval = null; }
      ttsCancel();
    }

    function startSimulated() {
      var startMs = Date.now() - (currentTime * 1000);
      simInterval = setInterval(function() {
        currentTime = (Date.now() - startMs) / 1000;
        if (currentTime >= audioDuration) {
          clearInterval(simInterval);
          simInterval = null;
          currentTime = audioDuration;
          onComplete();
          return;
        }
        tick(currentTime / audioDuration);
      }, 80);
    }

    function tick(pct) {
      // Waveform bars
      var active = Math.floor(pct * barCount);
      for (var i = 0; i < bars.length; i++) {
        if (i < active) bars[i].className = 'dc-bar played';
        else if (i === active) bars[i].className = 'dc-bar active';
        else bars[i].className = 'dc-bar';
      }
      // Duration
      if (durationEl) durationEl.textContent = fmt(currentTime) + ' / ' + fmt(audioDuration);
      // Progress
      if (progressFill) progressFill.style.width = (pct * 100) + '%';
      // Transcript sync + TTS
      try { document.dispatchEvent(new CustomEvent('tct:console-time', { detail: { time: currentTime } })); } catch(e) {}
      syncTranscript(currentTime);
      ttsSyncLine(currentTime);
      // Summary live-fill
      fillSummary(pct);
      // Booking lock
      if (pct >= 0.85) lockBooking();
      // Text reveal
      if (pct >= 0.9) revealText();
    }

    function onComplete() {
      playing = false;
      done = true;
      root.classList.add('dc-done');
      setPlayIcon('check');
      playBtn.classList.add('dc-done');
      bars.forEach(function(b) { b.className = 'dc-bar played'; });
      if (progressFill) progressFill.style.width = '100%';
      if (completeEl) completeEl.classList.add('show');
      revealAllOutputs();
      track('audio_complete', { section: 'demo_console', industry: currentIndustry });
    }

    function resetState() {
      root.classList.remove('dc-done');
      playBtn.classList.remove('dc-done');
      setPlayIcon('play');
      currentTime = 0;
      bars.forEach(function(b) { b.className = 'dc-bar'; });
      if (progressFill) progressFill.style.width = '0%';
      if (durationEl) durationEl.textContent = '0:00 / ' + fmt(audioDuration);
      if (completeEl) completeEl.classList.remove('show');
      // Reset field fills
      root.querySelectorAll('.dc-field').forEach(function(f) { f.classList.remove('filled'); });
      root.querySelectorAll('.dc-field-value').forEach(function(v) { v.textContent = ''; });
      root.querySelector('.dc-booking') && root.querySelector('.dc-booking').classList.remove('locked');
      var typeEl = root.querySelector('.dc-text-type');
      if (typeEl) typeEl.classList.remove('revealed');
      // Reset transcript + TTS
      root.querySelectorAll('.dc-line').forEach(function(l) { l.classList.remove('highlight', 'spoken'); });
      ttsCancel();
      if (hasRealAudio) audioEl.currentTime = 0;
    }

    function revealAllOutputs() {
      fillSummary(1);
      lockBooking();
      revealText();
    }

    // === Sync functions ===
    function syncTranscript(t) {
      var lines = root.querySelectorAll('[data-panel="transcript"] .dc-line');
      lines.forEach(function(line) {
        var s = parseFloat(line.getAttribute('data-start') || 0);
        var e = parseFloat(line.getAttribute('data-end') || 999);
        if (t >= s && t < e) { line.classList.add('highlight'); line.classList.remove('spoken'); }
        else if (t >= e) { line.classList.remove('highlight'); line.classList.add('spoken'); }
        else { line.classList.remove('highlight', 'spoken'); }
      });
    }

    var summaryFilled = {};
    function fillSummary(pct) {
      var data = INDUSTRIES[currentIndustry];
      if (!data) return;
      var fields = root.querySelectorAll('[data-panel="summary"] .dc-field');
      var keys = Object.keys(data.summary);
      keys.forEach(function(key, i) {
        var threshold = (i + 1) / (keys.length + 1);
        if (pct >= threshold && !summaryFilled[key]) {
          summaryFilled[key] = true;
          if (fields[i]) {
            fields[i].classList.add('filled');
            var valEl = fields[i].querySelector('.dc-field-value');
            if (valEl) valEl.textContent = data.summary[key];
          }
        }
      });
      if (pct < 0.05) summaryFilled = {};
    }

    function lockBooking() {
      var el = root.querySelector('.dc-booking');
      if (el && !el.classList.contains('locked')) {
        el.classList.add('locked');
        // Fill booking vals
        var data = INDUSTRIES[currentIndustry];
        if (!data) return;
        var vals = root.querySelectorAll('.dc-booking-val');
        var bookKeys = Object.keys(data.booking);
        vals.forEach(function(v, i) {
          if (bookKeys[i]) v.textContent = data.booking[bookKeys[i]];
        });
      }
    }

    function revealText() {
      var el = root.querySelector('.dc-text-type');
      if (el && !el.classList.contains('revealed')) {
        el.classList.add('revealed');
      }
    }

    function setPlayIcon(type) {
      if (type === 'pause') playBtn.innerHTML = '<svg viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16" fill="currentColor"/><rect x="14" y="4" width="4" height="16" fill="currentColor"/></svg>';
      else if (type === 'check') playBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
      else playBtn.innerHTML = '<svg viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21" fill="currentColor"/></svg>';
    }
  }

  // === HTML Builders ===
  function buildHTML(industry, showIndustries, audioSrc) {
    var data = INDUSTRIES[industry];
    var html = '';
    // Header
    html += '<div class="dc-header">';
    html += '<span class="dc-badge"><span class="dc-live-dot"></span>Call Session Viewer</span>';
    html += '<span class="dc-sim-label" data-loaded="Demo audio loaded" data-sim="Using simulated demo">Using simulated demo</span>';
    html += '<span class="dc-time">Real call \u2014 11:47 PM</span>';
    html += '</div>';
    // Industry pills
    if (showIndustries) {
      html += '<div class="dc-industries">';
      Object.keys(INDUSTRIES).forEach(function(key) {
        html += '<button class="dc-ind' + (key === industry ? ' active' : '') + '" data-ind="' + key + '">' + INDUSTRIES[key].label + '</button>';
      });
      html += '</div>';
    }
    // Player
    html += '<div class="dc-player">';
    html += '<button class="dc-play" aria-label="Play demo call"><svg viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21" fill="currentColor"/></svg></button>';
    html += '<div class="dc-waveform"></div>';
    html += '<span class="dc-duration">0:00 / 0:25</span>';
    html += '</div>';
    html += '<div class="dc-progress"><div class="dc-progress-fill"></div></div>';
    // Tabs
    html += '<div class="dc-tabs" role="tablist">';
    html += '<button class="dc-tab active" data-tab="transcript" role="tab" tabindex="0">Transcript</button>';
    html += '<button class="dc-tab" data-tab="summary" role="tab" tabindex="-1">Summary</button>';
    html += '<button class="dc-tab" data-tab="booking" role="tab" tabindex="-1">Booking</button>';
    html += '<button class="dc-tab" data-tab="text" role="tab" tabindex="-1">Text Sent</button>';
    html += '</div>';
    // Panels
    html += '<div class="dc-panels">';
    html += '<div class="dc-panel active" data-panel="transcript">' + buildTranscriptPanel(data.transcript) + '</div>';
    html += '<div class="dc-panel" data-panel="summary">' + buildSummaryPanel(data.summary) + '</div>';
    html += '<div class="dc-panel" data-panel="booking">' + buildBookingPanel(data.booking) + '</div>';
    html += '<div class="dc-panel" data-panel="text">' + buildTextPanel(data.textMsg) + '</div>';
    html += '</div>';
    // Complete
    html += '<div class="dc-complete"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> Call handled. Job booked. Summary sent.</div>';
    // Audio
    html += '<audio preload="metadata" src="' + audioSrc + '"></audio>';
    return html;
  }

  function buildTranscriptPanel(lines) {
    var html = '';
    lines.forEach(function(l) {
      var cls = l.speaker === 'Caller' ? 'dc-caller' : 'dc-ai';
      html += '<div class="dc-line" data-start="' + l.start + '" data-end="' + l.end + '">';
      html += '<span class="dc-speaker ' + cls + '">' + l.speaker + '</span>';
      html += '<span class="dc-text">\u201c' + l.text + '\u201d</span>';
      html += '</div>';
    });
    return html;
  }

  function buildSummaryPanel(summary) {
    var html = '<div class="dc-summary-grid">';
    var labels = { name: 'Name', issue: 'Issue', location: 'Location', urgency: 'Urgency' };
    Object.keys(labels).forEach(function(key) {
      html += '<div class="dc-field">';
      html += '<div class="dc-field-label">' + labels[key] + '</div>';
      html += '<div class="dc-field-value"></div>';
      html += '</div>';
    });
    html += '</div>';
    return html;
  }

  function buildBookingPanel(booking) {
    var html = '<div class="dc-booking">';
    html += '<div class="dc-booking-header">';
    html += '<div class="dc-booking-title">Appointment Confirmation</div>';
    html += '<div class="dc-booking-check"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div>';
    html += '</div>';
    html += '<div class="dc-booking-rows">';
    var labels = { service: 'Service', time: 'Time', tech: 'Technician', address: 'Address' };
    Object.keys(labels).forEach(function(key) {
      html += '<div class="dc-booking-row"><span class="dc-booking-label">' + labels[key] + '</span><span class="dc-booking-val">\u2014</span></div>';
    });
    html += '</div></div>';
    return html;
  }

  function buildTextPanel(textMsg) {
    var escaped = textMsg.replace(/\n/g, '<br>');
    return '<div class="dc-text-preview"><div class="dc-text-type"><strong>New lead from The Call Taker:</strong><br>' + escaped + '</div></div>';
  }

  // === Auto-init all .dc elements on page ===
  document.querySelectorAll('.dc').forEach(function(el) {
    var opts = {
      dark: el.classList.contains('dc-dark'),
      large: el.classList.contains('dc-large'),
      industry: el.getAttribute('data-industry') || 'hvac',
      industries: el.getAttribute('data-industries') !== 'false',
      audioSrc: el.getAttribute('data-audio') || '/assets/demo/demo-call-15s.mp3'
    };
    initDemoConsole(el, opts);
  });

  // === Proof Dock ===
  var dock = document.querySelector('.proof-dock');
  if (dock && window.innerWidth > 768) {
    var hero = document.querySelector('.hero, .pilot-hero, .demo-hero, .pricing-hero');
    if (hero) {
      var dockShown = false;
      window.addEventListener('scroll', function() {
        var bottom = hero.offsetTop + hero.offsetHeight;
        var show = window.scrollY > bottom + 200;
        if (show && !dockShown) { dock.classList.add('visible'); dockShown = true; }
        else if (!show && dockShown) { dock.classList.remove('visible'); dockShown = false; }
      }, { passive: true });
    }
  }

  // Export for manual init + command palette
  window.initDemoConsole = initDemoConsole;
  window.TCT_Console = {
    play: function() {
      var btn = document.querySelector('.dc .dc-play');
      if (btn) btn.click();
    }
  };
})();
