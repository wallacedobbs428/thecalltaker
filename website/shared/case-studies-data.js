/* ============================================
   CASE STUDIES DATA — 6 Industries
   Used by index.html, demo-showcase.html,
   pricing.html for inline social proof.
   ============================================ */
window.TCT_CaseStudies = {
  hvac: {
    industry: 'HVAC',
    company: 'Palmetto Comfort Solutions',
    location: 'Charleston, SC',
    problem: 'Missing 41% of after-hours calls. Owner was answering the phone at dinner, on weekends, and losing emergency jobs to competitors who picked up first.',
    bullets: [
      'AI answers in under 2 seconds, 24/7 — no hold music, no voicemail',
      'Captures caller name, address, and issue before dispatching',
      'Sends confirmation text to homeowner with tech ETA'
    ],
    metrics: { missed: '41% \u2192 0%', revenue: '+$8,400/mo', roi: '29x', time: '2 weeks' },
    transcript: [
      { speaker: 'caller', text: '\u201cMy AC stopped working and it\u2019s 95 degrees in here.\u201d' },
      { speaker: 'ai', text: '\u201cI\u2019m sorry to hear that. I can get a technician out to you right away. What\u2019s your address?\u201d' }
    ],
    link: '/case-studies/palmetto-comfort.html'
  },
  plumbing: {
    industry: 'Plumbing',
    company: 'Reliable Rooter Co.',
    location: 'Tampa, FL',
    problem: 'Solo plumber losing emergency calls while on jobs. Couldn\u2019t answer the phone with his hands full under a sink, and voicemail meant the customer called the next plumber on Google.',
    bullets: [
      'AI handles calls while the plumber works — no missed emergencies',
      'Collects problem details so the plumber arrives prepared',
      'Texts the customer a booking confirmation instantly'
    ],
    metrics: { missed: '60% \u2192 3%', revenue: '+$6,200/mo', roi: '21x', time: '10 days' },
    transcript: [
      { speaker: 'caller', text: '\u201cI have a burst pipe flooding my kitchen!\u201d' },
      { speaker: 'ai', text: '\u201cI\u2019m dispatching an emergency plumber now. What\u2019s your address?\u201d' }
    ],
    link: '/case-studies/reliable-rooter.html'
  },
  dental: {
    industry: 'Dental',
    company: 'Bright Smile Family Dental',
    location: 'Austin, TX',
    problem: 'Front desk overwhelmed during peak hours. Patients calling to reschedule or ask about insurance were going to voicemail, and 1 in 4 never called back.',
    bullets: [
      'AI handles scheduling, rescheduling, and insurance questions',
      'Frees front desk to focus on in-office patients',
      'Sends appointment reminders via text automatically'
    ],
    metrics: { missed: '25% \u2192 2%', revenue: '+$4,800/mo', roi: '16x', time: '1 week' },
    transcript: [
      { speaker: 'caller', text: '\u201cI need to move my cleaning appointment to next week.\u201d' },
      { speaker: 'ai', text: '\u201cI can help with that. How does Thursday at 10 AM work for you?\u201d' }
    ],
    link: '/case-studies/'
  },
  legal: {
    industry: 'Legal',
    company: 'Carter & Associates Law',
    location: 'Nashville, TN',
    problem: 'Potential clients calling after a car accident or arrest don\u2019t leave voicemails \u2014 they call the next firm. Missing one intake call can mean losing a $15,000+ case.',
    bullets: [
      'AI captures full intake: name, incident type, timeline, urgency',
      'Flags high-value cases for immediate attorney callback',
      'Sends caller a text confirming the firm received their case'
    ],
    metrics: { missed: '35% \u2192 1%', revenue: '+$12,000/mo', roi: '40x', time: '3 days' },
    transcript: [
      { speaker: 'caller', text: '\u201cI was in a car accident and I need a lawyer.\u201d' },
      { speaker: 'ai', text: '\u201cI\u2019m sorry to hear that. Let me get your information so an attorney can call you first thing tomorrow.\u201d' }
    ],
    link: '/case-studies/'
  },
  medspa: {
    industry: 'Med Spa',
    company: 'Glow Aesthetics',
    location: 'Scottsdale, AZ',
    problem: 'Clients booking Botox and facials want to call and confirm availability \u2014 not fill out a form. After-hours calls were going unanswered, sending clients to competitors.',
    bullets: [
      'AI books consultations and answers treatment questions 24/7',
      'Handles pricing inquiries with pre-approved ranges',
      'Sends booking confirmation with prep instructions via text'
    ],
    metrics: { missed: '30% \u2192 0%', revenue: '+$5,600/mo', roi: '19x', time: '5 days' },
    transcript: [
      { speaker: 'caller', text: '\u201cDo you have availability for Botox this week?\u201d' },
      { speaker: 'ai', text: '\u201cWe do! I can get you in Thursday at 2 PM. Shall I book that for you?\u201d' }
    ],
    link: '/case-studies/'
  },
  locksmith: {
    industry: 'Locksmith',
    company: 'Rapid Key Locksmith',
    location: 'Nashville, TN',
    problem: 'Emergency lockouts happen at 2 AM. Owner was sleeping through calls, and every missed call was a $150\u2013$300 job walking to a competitor.',
    bullets: [
      'AI dispatches for emergencies 24/7 \u2014 even at 3 AM',
      'Captures location, vehicle/home type, and urgency level',
      'Texts customer with locksmith ETA within 60 seconds'
    ],
    metrics: { missed: '50% \u2192 0%', revenue: '+$7,200/mo', roi: '24x', time: '1 week' },
    transcript: [
      { speaker: 'caller', text: '\u201cI\u2019m locked out of my car. Can someone come now?\u201d' },
      { speaker: 'ai', text: '\u201cAbsolutely. I\u2019ll dispatch a locksmith to your location. What\u2019s the address?\u201d' }
    ],
    link: '/case-studies/rapid-key-locksmith.html'
  }
};
