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

  // === TTS VOICE SETTINGS ===
  var TTS_VOICES = {
    jessica: { pitch: -0.1, rate: 0.85 },
    caller:  { pitch: 0, rate: 1.0 }
  };

  // === INDUSTRY DATASETS ===
  var INDUSTRIES = {
    hvac: {
      label: 'HVAC',
      transcript: [
        { speaker: 'Caller', text: 'Hey, my AC just quit on me and it\u2019s gotta be close to a hundred degrees in the house. I\u2019ve got two little kids here.', start: 0, end: 4 },
        { speaker: 'AI', text: 'Oh no, I\u2019m so sorry. Let\u2019s get someone out to you right away. Can I grab your address?', start: 4, end: 7 },
        { speaker: 'Caller', text: 'Yeah, it\u2019s 142 Oak Street in Nashville. It\u2019s a Trane unit, probably about eight years old.', start: 7, end: 10.5 },
        { speaker: 'AI', text: 'Got it \u2014 142 Oak Street, Trane system. I have a certified tech available this afternoon between 2 and 4. He\u2019ll check your refrigerant levels and the compressor. Sound good?', start: 10.5, end: 15 },
        { speaker: 'Caller', text: 'Yes, please. We\u2019re dying in here. Thank you so much.', start: 15, end: 17 }
      ],
      summary: { name: 'Sarah M.', issue: 'AC not cooling \u2014 Trane unit, 8 yrs old', location: '142 Oak St, Nashville', urgency: 'High \u2014 emergency, kids at home' },
      booking: { service: 'AC Diagnostic + Repair', time: 'Today 2\u20134 PM', tech: 'Certified HVAC tech', address: '142 Oak St, Nashville' },
      textMsg: 'New lead from The Call Taker:\nSarah M. \u2014 AC out, Trane unit ~8 yrs.\n142 Oak St, Nashville. Kids at home.\nBooked today 2\u20134 PM.\nCall back: (615) 555-0142',
      result: 'Job booked. Text sent. $800 saved.'
    },
    plumbing: {
      label: 'Plumbing',
      transcript: [
        { speaker: 'Caller', text: 'I\u2019ve got water spraying out from under my kitchen sink \u2014 it looks like the supply line burst. There\u2019s water everywhere!', start: 0, end: 4 },
        { speaker: 'AI', text: 'Okay, first thing \u2014 can you reach the shut-off valve under the sink? Turn it clockwise to stop the flow. I\u2019m getting a plumber headed your way right now.', start: 4, end: 8.5 },
        { speaker: 'Caller', text: 'Yeah, I got it turned off. I\u2019m at 88 Elm Drive, apartment 4B. It\u2019s soaking through the floor already.', start: 8.5, end: 12 },
        { speaker: 'AI', text: 'Good, you stopped it. I\u2019m dispatching our nearest plumber \u2014 he\u2019ll be there within 45 minutes with a replacement supply line. I\u2019ll text you his name and ETA.', start: 12, end: 16 },
        { speaker: 'Caller', text: 'Thank you. I\u2019ll start getting towels down. Please hurry.', start: 16, end: 18 }
      ],
      summary: { name: 'Mike R.', issue: 'Burst supply line \u2014 kitchen flooding', location: '88 Elm Dr, Apt 4B', urgency: 'Critical \u2014 active water damage' },
      booking: { service: 'Emergency Pipe Repair', time: 'Within 45 min', tech: 'Nearest available', address: '88 Elm Dr, Apt 4B' },
      textMsg: 'URGENT lead from The Call Taker:\nMike R. \u2014 burst supply line, kitchen flooding.\n88 Elm Dr, Apt 4B. Shut-off closed.\nDispatched within 45 min.\nCall back: (615) 555-0288',
      result: 'Emergency dispatch. $1,200 job saved.'
    },
    dental: {
      label: 'Dental',
      transcript: [
        { speaker: 'Caller', text: 'Hi, I\u2019m a new patient and I need to schedule a cleaning and a checkup. Do you accept Delta Dental insurance?', start: 0, end: 4 },
        { speaker: 'AI', text: 'Welcome! Yes, we do accept Delta Dental. Let me find you a time. Are mornings or afternoons better for you?', start: 4, end: 8 },
        { speaker: 'Caller', text: 'Mornings work best. I\u2019d love something this week if you have it. I haven\u2019t been to a dentist in about two years.', start: 8, end: 12 },
        { speaker: 'AI', text: 'No worries at all. I have Thursday at 9 AM open with Dr. Williams. Since it\u2019s been a while, we\u2019ll do full X-rays along with the cleaning. I\u2019ll text you the new patient forms to fill out ahead of time.', start: 12, end: 17 },
        { speaker: 'Caller', text: 'Thursday at 9 is perfect. Thank you so much!', start: 17, end: 19 }
      ],
      summary: { name: 'Lisa K.', issue: 'New patient cleaning + checkup', location: 'New patient \u2014 Delta Dental', urgency: 'Normal \u2014 routine' },
      booking: { service: 'Cleaning + Full X-rays', time: 'Thursday 9:00 AM', tech: 'Dr. Williams', address: 'New patient \u2014 forms sent' },
      textMsg: 'New patient from The Call Taker:\nLisa K. \u2014 cleaning + checkup, new patient.\nInsurance: Delta Dental.\nThursday 9 AM w/ Dr. Williams.\nForms link sent.\nCall back: (615) 555-0311',
      result: 'New patient booked. Forms sent. Revenue captured.'
    },
    legal: {
      label: 'Legal',
      transcript: [
        { speaker: 'Caller', text: 'I was rear-ended on I-65 about an hour ago. The other driver\u2019s insurance is already calling me. Do I need a lawyer?', start: 0, end: 4 },
        { speaker: 'AI', text: 'I\u2019m glad you\u2019re safe. Yes, I\u2019d strongly recommend speaking with an attorney before talking to their insurance. Can I get your name so I can have someone call you back right away?', start: 4, end: 9 },
        { speaker: 'Caller', text: 'It\u2019s James Torres. My neck is really sore and the bumper is completely smashed in. I took photos at the scene.', start: 9, end: 13 },
        { speaker: 'AI', text: 'Thank you, James. Keep those photos safe \u2014 they\u2019re important evidence. An attorney will call you within the hour for a free consultation. Don\u2019t give any recorded statements to the other driver\u2019s insurance until then.', start: 13, end: 18 },
        { speaker: 'Caller', text: 'Okay, I won\u2019t talk to them. Thank you.', start: 18, end: 20 }
      ],
      summary: { name: 'James T.', issue: 'Rear-end collision \u2014 I-65, neck pain', location: 'Nashville area', urgency: 'High \u2014 insurance already contacting' },
      booking: { service: 'Free Consultation', time: 'Callback within 1 hour', tech: 'Personal injury attorney', address: 'Phone consultation' },
      textMsg: 'HOT LEAD from The Call Taker:\nJames T. \u2014 rear-end collision on I-65.\nNeck pain, has photos. Insurance calling.\nCallback within 1 hour.\nCall back: (615) 555-0477',
      result: 'Client intake captured. Case secured.'
    },
    medspa: {
      label: 'Med Spa',
      transcript: [
        { speaker: 'Caller', text: 'Hi, I\u2019m interested in getting Botox for the first time. How many units do most people need for the forehead?', start: 0, end: 4 },
        { speaker: 'AI', text: 'Great question! Most patients use between 10 and 20 units for the forehead, but our injector will customize it during your consultation. Would you like to schedule one?', start: 4, end: 9 },
        { speaker: 'Caller', text: 'Yeah, do you have anything this week? Also, what\u2019s the cost per unit?', start: 9, end: 12 },
        { speaker: 'AI', text: 'We\u2019re running $12 per unit this month. I have Wednesday at 2 PM or Friday at 11. We\u2019ll send you intake paperwork and pre-treatment instructions ahead of time.', start: 12, end: 16.5 },
        { speaker: 'Caller', text: 'Wednesday at 2 sounds great. I\u2019m excited!', start: 16.5, end: 18 }
      ],
      summary: { name: 'Amanda P.', issue: 'First-time Botox \u2014 forehead', location: 'New patient', urgency: 'Normal' },
      booking: { service: 'Botox Consultation + Treatment', time: 'Wednesday 2:00 PM', tech: 'Licensed injector', address: 'New patient \u2014 intake sent' },
      textMsg: 'New booking from The Call Taker:\nAmanda P. \u2014 first-time Botox, forehead.\nWednesday 2:00 PM.\nIntake + pre-treatment info sent.\nCall back: (615) 555-0533',
      result: 'Appointment booked. Intake sent.'
    },
    roofing: {
      label: 'Roofing',
      transcript: [
        { speaker: 'Caller', text: 'We had that bad storm last night and now I\u2019ve got water coming through the ceiling in my living room. I can see shingles in the yard.', start: 0, end: 4.5 },
        { speaker: 'AI', text: 'That sounds like storm damage. Let me get an inspector out to you as soon as possible. Are you seeing active dripping right now?', start: 4.5, end: 8.5 },
        { speaker: 'Caller', text: 'Yeah, I\u2019ve got a bucket under it. We\u2019re at 305 Maple Lane in Murfreesboro. The roof is about 15 years old.', start: 8.5, end: 12.5 },
        { speaker: 'AI', text: 'Got it. I\u2019m scheduling a free storm damage inspection for tomorrow morning. We\u2019ll document everything for your insurance claim and tarp the affected area. Do you have your homeowner\u2019s policy number handy?', start: 12.5, end: 17 },
        { speaker: 'Caller', text: 'I can grab it. Tomorrow morning works. Thank you.', start: 17, end: 19 }
      ],
      summary: { name: 'Kevin B.', issue: 'Storm damage \u2014 ceiling leak, missing shingles', location: '305 Maple Ln, Murfreesboro', urgency: 'High \u2014 active leak' },
      booking: { service: 'Storm Damage Inspection', time: 'Tomorrow AM', tech: 'Roof inspector', address: '305 Maple Ln, Murfreesboro' },
      textMsg: 'URGENT lead from The Call Taker:\nKevin B. \u2014 storm damage, ceiling leak.\n305 Maple Ln, Murfreesboro. Roof ~15 yrs.\nInspection booked tomorrow AM.\nCall back: (615) 555-0305',
      result: 'Inspection booked. Insurance claim started. $8,500 job.'
    },
    electrical: {
      label: 'Electrical',
      transcript: [
        { speaker: 'Caller', text: 'Half the outlets in my kitchen stopped working and the breaker keeps tripping every time I reset it. I\u2019m worried something\u2019s wrong with the wiring.', start: 0, end: 4.5 },
        { speaker: 'AI', text: 'That does sound like it could be a short or an overloaded circuit. I\u2019d recommend not forcing the breaker back on. Let me get a licensed electrician out to diagnose it. What\u2019s your address?', start: 4.5, end: 9.5 },
        { speaker: 'Caller', text: '712 Cedar Court in Franklin. The house was built in the \u201970s so the wiring might be original.', start: 9.5, end: 13 },
        { speaker: 'AI', text: 'Good to know \u2014 older wiring is definitely something we\u2019ll want to check. I have an electrician available tomorrow between 8 and 10 AM. He\u2019ll inspect the panel and trace the circuit. I\u2019ll text you the confirmation.', start: 13, end: 18 },
        { speaker: 'Caller', text: 'That works. I just want to make sure it\u2019s safe. Thank you.', start: 18, end: 20 }
      ],
      summary: { name: 'Tom H.', issue: 'Tripping breaker \u2014 kitchen outlets dead', location: '712 Cedar Ct, Franklin', urgency: 'High \u2014 possible wiring fault' },
      booking: { service: 'Electrical Diagnostic', time: 'Tomorrow 8\u201310 AM', tech: 'Licensed electrician', address: '712 Cedar Ct, Franklin' },
      textMsg: 'New lead from The Call Taker:\nTom H. \u2014 breaker tripping, kitchen outlets out.\n712 Cedar Ct, Franklin. 1970s wiring.\nBooked tomorrow 8\u201310 AM.\nCall back: (615) 555-0712',
      result: 'Diagnostic booked. Text sent. $650 job saved.'
    },
    locksmith: {
      label: 'Locksmith',
      transcript: [
        { speaker: 'Caller', text: 'I\u2019m locked out of my car at the Kroger parking lot on West End. My keys are sitting right on the seat. Can someone come pop the lock?', start: 0, end: 4.5 },
        { speaker: 'AI', text: 'Absolutely, I can get a locksmith to you fast. What\u2019s the year, make, and model of the vehicle?', start: 4.5, end: 8 },
        { speaker: 'Caller', text: 'It\u2019s a 2019 Honda Civic. I\u2019m standing right next to it in the parking lot.', start: 8, end: 11 },
        { speaker: 'AI', text: 'Got it \u2014 2019 Civic at the West End Kroger. I\u2019m sending our nearest tech now, he should be there in about 20 minutes. I\u2019ll text you his name and ETA so you know who to look for.', start: 11, end: 16 },
        { speaker: 'Caller', text: 'Twenty minutes? That\u2019s great. I was worried it\u2019d be an hour. Thanks!', start: 16, end: 18 }
      ],
      summary: { name: 'Rachel S.', issue: 'Car lockout \u2014 keys on seat', location: 'Kroger, West End Ave', urgency: 'Medium \u2014 stranded' },
      booking: { service: 'Car Lockout', time: 'Within 20 min', tech: 'Nearest mobile locksmith', address: 'Kroger, West End Ave' },
      textMsg: 'New lead from The Call Taker:\nRachel S. \u2014 locked out, 2019 Honda Civic.\nKroger parking lot, West End Ave.\nETA 20 min.\nCall back: (615) 555-0199',
      result: 'Locksmith dispatched. $150 job saved.'
    },
    towing: {
      label: 'Towing',
      transcript: [
        { speaker: 'Caller', text: 'My car broke down on the shoulder of I-24 near exit 57. The engine overheated and it won\u2019t start back up. I need a tow.', start: 0, end: 4.5 },
        { speaker: 'AI', text: 'I\u2019m sorry to hear that. Are you in a safe spot off the road? Let me get a tow truck headed to you right away. What kind of vehicle is it?', start: 4.5, end: 9 },
        { speaker: 'Caller', text: 'Yeah, I\u2019m on the shoulder with my hazards on. It\u2019s a 2017 Ford F-150. I need it towed to my mechanic on Nolensville Pike.', start: 9, end: 13 },
        { speaker: 'AI', text: 'Got it \u2014 F-150 on I-24 at exit 57, towing to Nolensville Pike. Our nearest driver can be there in about 30 minutes. I\u2019ll text you his info and a live ETA tracker.', start: 13, end: 17.5 },
        { speaker: 'Caller', text: 'Perfect, 30 minutes is fine. I appreciate the fast response.', start: 17.5, end: 19 }
      ],
      summary: { name: 'Marcus J.', issue: 'Breakdown \u2014 engine overheated, I-24', location: 'I-24 shoulder, exit 57', urgency: 'High \u2014 roadside' },
      booking: { service: 'Flatbed Tow', time: 'Within 30 min', tech: 'Nearest tow driver', address: 'I-24 exit 57 \u2192 Nolensville Pike' },
      textMsg: 'URGENT lead from The Call Taker:\nMarcus J. \u2014 breakdown, 2017 F-150.\nI-24 shoulder at exit 57.\nTow to Nolensville Pike mechanic.\nETA 30 min.\nCall back: (615) 555-0824',
      result: 'Tow dispatched. $250 job saved.'
    },
    veterinary: {
      label: 'Veterinary',
      transcript: [
        { speaker: 'Caller', text: 'My dog just ate a whole bar of dark chocolate. He\u2019s a 30-pound beagle and he\u2019s already starting to shake. What should I do?', start: 0, end: 4.5 },
        { speaker: 'AI', text: 'Dark chocolate is toxic for dogs, especially at that size. Don\u2019t try to induce vomiting at home. How long ago did he eat it?', start: 4.5, end: 9 },
        { speaker: 'Caller', text: 'Maybe 20 minutes ago. He got into my purse while I was in the other room. I\u2019m at 460 Belmont Avenue.', start: 9, end: 13 },
        { speaker: 'AI', text: 'Okay, bring him in right away. I\u2019m flagging the vet team now so they\u2019ll be ready when you arrive. Drive safely \u2014 we\u2019re expecting you in the next 15 minutes.', start: 13, end: 17.5 },
        { speaker: 'Caller', text: 'We\u2019re leaving right now. Thank you so much.', start: 17.5, end: 19 }
      ],
      summary: { name: 'Nicole D.', issue: 'Chocolate toxicity \u2014 30lb beagle', location: '460 Belmont Ave', urgency: 'Critical \u2014 emergency' },
      booking: { service: 'Emergency Exam', time: 'Arriving in 15 min', tech: 'Vet team on standby', address: '460 Belmont Ave' },
      textMsg: 'EMERGENCY from The Call Taker:\nNicole D. \u2014 dog ate dark chocolate.\n30lb beagle, shaking, 20 min ago.\nArriving in 15 min.\nCall back: (615) 555-0460',
      result: 'Emergency flagged. Vet team ready. Life saved.'
    },
    property: {
      label: 'Property Mgmt',
      transcript: [
        { speaker: 'Caller', text: 'This is the tenant in unit 12B at Riverside Commons. My hot water heater is leaking all over the utility closet and the carpet is soaked.', start: 0, end: 4.5 },
        { speaker: 'AI', text: 'I\u2019m sorry about that. Can you see where the leak is coming from \u2014 is it the tank itself or one of the pipes at the top?', start: 4.5, end: 8.5 },
        { speaker: 'Caller', text: 'It looks like it\u2019s coming from the bottom of the tank. There\u2019s a puddle forming pretty fast.', start: 8.5, end: 12 },
        { speaker: 'AI', text: 'That\u2019s likely a tank failure. I\u2019m sending a maintenance request to the property manager right now and dispatching a plumber for tomorrow morning. In the meantime, turn the water supply valve above the heater to the off position.', start: 12, end: 17.5 },
        { speaker: 'Caller', text: 'Okay, I\u2019ll do that. Thanks for taking care of this so fast.', start: 17.5, end: 19 }
      ],
      summary: { name: 'Tenant 12B', issue: 'Water heater leak \u2014 tank failure', location: 'Riverside Commons, Unit 12B', urgency: 'High \u2014 active leak' },
      booking: { service: 'Water Heater Replacement', time: 'Tomorrow AM', tech: 'Maintenance + plumber', address: 'Riverside Commons, 12B' },
      textMsg: 'Maintenance request from The Call Taker:\nTenant 12B \u2014 water heater leaking from tank.\nRiverside Commons. Carpet soaked.\nPlumber booked tomorrow AM.\nCall back: (615) 555-0912',
      result: 'Work order filed. Plumber booked. Tenant handled.'
    },
    garage: {
      label: 'Garage Door',
      transcript: [
        { speaker: 'Caller', text: 'My garage door went off the track this morning and it\u2019s stuck about two feet up. I can\u2019t close it and my car is inside.', start: 0, end: 4 },
        { speaker: 'AI', text: 'That sounds like a cable or roller issue. Don\u2019t try to force it \u2014 the spring tension can be dangerous. What\u2019s your address so I can send a technician?', start: 4, end: 8.5 },
        { speaker: 'Caller', text: '215 Bridle Path in Brentwood. It\u2019s a two-car garage, and the left side is the one that\u2019s stuck.', start: 8.5, end: 12 },
        { speaker: 'AI', text: 'Got it \u2014 215 Bridle Path, left bay off-track. I have a tech available this afternoon between 1 and 3 PM. He\u2019ll re-track the door and inspect the cables, rollers, and springs. I\u2019ll text you confirmation.', start: 12, end: 17 },
        { speaker: 'Caller', text: 'This afternoon is great. I just need to get my car out. Thanks.', start: 17, end: 19 }
      ],
      summary: { name: 'David W.', issue: 'Door off track \u2014 stuck open 2 ft', location: '215 Bridle Path, Brentwood', urgency: 'Medium \u2014 car trapped' },
      booking: { service: 'Off-Track Repair + Inspection', time: 'Today 1\u20133 PM', tech: 'Garage door tech', address: '215 Bridle Path, Brentwood' },
      textMsg: 'New lead from The Call Taker:\nDavid W. \u2014 garage door off track, left bay.\n215 Bridle Path, Brentwood. Car inside.\nBooked today 1\u20133 PM.\nCall back: (615) 555-0215',
      result: 'Service call booked. $350 job saved.'
    },
    funeral: {
      label: 'Funeral',
      transcript: [
        { speaker: 'Caller', text: 'My mother passed away this morning at Vanderbilt hospital. We need to make arrangements. I don\u2019t really know where to start.', start: 0, end: 4.5 },
        { speaker: 'AI', text: 'I\u2019m so sorry for your loss. Please take your time. We\u2019re here to walk you through everything. Can I get your name and the best number to reach you?', start: 4.5, end: 9.5 },
        { speaker: 'Caller', text: 'It\u2019s Patricia Collins. You can reach me at this number. She\u2019s still at the hospital right now.', start: 9.5, end: 13 },
        { speaker: 'AI', text: 'Thank you, Patricia. I\u2019ll have our funeral director call you within the next 30 minutes. We\u2019ll coordinate the transfer from Vanderbilt and help you plan everything at your pace. You don\u2019t need to worry about the details right now.', start: 13, end: 18 },
        { speaker: 'Caller', text: 'Thank you. That means a lot right now.', start: 18, end: 20 }
      ],
      summary: { name: 'Patricia C.', issue: 'Arrangements needed \u2014 mother passed', location: 'Vanderbilt Hospital', urgency: 'High \u2014 immediate coordination' },
      booking: { service: 'Funeral Arrangement Consultation', time: 'Callback within 30 min', tech: 'Funeral director', address: 'Transfer from Vanderbilt' },
      textMsg: 'Sensitive lead from The Call Taker:\nPatricia C. \u2014 mother passed at Vanderbilt.\nNeeds arrangements + hospital transfer.\nCallback within 30 min.\nCall back: (615) 555-0741',
      result: 'Family contacted. Transfer arranged. Compassionate care.'
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

    // State
    var playing = false;
    var audioDuration = 15;
    var currentTime = 0;
    var simInterval = null;
    var done = false;
    var currentIndustry = industry;
    var hasRealAudio = false;
    var bars = [];
    var barCount = 44;

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
            // Placeholder file — too short to be a real demo recording
            hasRealAudio = false;
            if (simLabel) {
              simLabel.textContent = 'Simulated demo (real recording coming soon)';
              simLabel.classList.remove('dc-audio-loaded');
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
          simLabel.textContent = simLabel.getAttribute('data-sim');
          simLabel.classList.remove('dc-audio-loaded');
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
      // Rebuild panels content
      root.querySelector('[data-panel="transcript"]').innerHTML = buildTranscriptPanel(data.transcript);
      root.querySelector('[data-panel="summary"]').innerHTML = buildSummaryPanel(data.summary);
      root.querySelector('[data-panel="booking"]').innerHTML = buildBookingPanel(data.booking);
      root.querySelector('[data-panel="text"]').innerHTML = buildTextPanel(data.textMsg);
      // Reset refs
      completeEl = root.querySelector('.dc-complete');
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
      // Stop any TTS speech
      if ('speechSynthesis' in window) {
        try { speechSynthesis.cancel(); } catch(e) {}
      }
    }

    // === TTS for simulated playback ===
    var ttsSpoken = {};
    var ttsAvailable = 'speechSynthesis' in window;

    function speakLine(text, speaker) {
      if (!ttsAvailable) return;
      try {
        var utter = new SpeechSynthesisUtterance(text);
        var voices = speechSynthesis.getVoices();
        if (speaker === 'AI') {
          // Try to find a female voice for AI
          var femaleVoice = voices.find(function(v) { return /samantha|karen|victoria|zira|female/i.test(v.name); });
          if (femaleVoice) utter.voice = femaleVoice;
          utter.pitch = 1.05;
          utter.rate = 0.9;
        } else {
          // Try to find a male voice for callers
          var maleVoice = voices.find(function(v) { return /daniel|alex|david|mark|male/i.test(v.name) && !/female/i.test(v.name); });
          if (maleVoice) utter.voice = maleVoice;
          utter.pitch = 0.95;
          utter.rate = 1.0;
        }
        utter.volume = 0.8;
        speechSynthesis.speak(utter);
      } catch(e) {}
    }

    function startSimulated() {
      ttsSpoken = {};
      // Pre-load voices
      if (ttsAvailable) {
        try { speechSynthesis.getVoices(); } catch(e) {}
      }
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
        // Speak transcript lines via TTS
        if (ttsAvailable) {
          var data = INDUSTRIES[currentIndustry];
          if (data && data.transcript) {
            data.transcript.forEach(function(line) {
              var key = line.start + ':' + line.speaker;
              if (currentTime >= line.start && !ttsSpoken[key]) {
                ttsSpoken[key] = true;
                speakLine(line.text, line.speaker);
              }
            });
          }
        }
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
      // Transcript sync
      try { document.dispatchEvent(new CustomEvent('tct:console-time', { detail: { time: currentTime } })); } catch(e) {}
      syncTranscript(currentTime);
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
      ttsSpoken = {};
      if (ttsAvailable) { try { speechSynthesis.cancel(); } catch(e) {} }
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
    html += '<span class="dc-duration">0:00 / 0:15</span>';
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
