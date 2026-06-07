/* ============================================
   SITE DATA — Single source of truth for
   industry content across all pages.
   Console transcripts live in demo-console.js.
   ============================================ */
window.TCT_DATA = {
  industries: {
    hvac: {
      label: 'HVAC',
      pain: "It\u2019s 95\u00b0 and a homeowner\u2019s AC just died. They call you \u2014 but you\u2019re on another job. That $800 repair goes to your competitor.",
      bullets: [
        '62% of HVAC calls come after hours \u2014 when you can\u2019t answer',
        'Emergency AC/heat jobs average $400\u2013$1,200 each'
      ],
      sample: '\u201COur AC stopped working and it\u2019s 95 degrees in here. Can someone come out today?\u201D',
      link: '/industries/hvac.html',
      linkText: 'See How It Works for HVAC',
      avgJobValue: 800,
      whoLine: 'HVAC contractors losing after-hours emergency calls'
    },
    plumbing: {
      label: 'Plumbing',
      pain: "A burst pipe at 2 AM. The homeowner is panicking. They call you \u2014 voicemail. They call the next plumber. That\u2019s an $800 emergency job, gone.",
      bullets: [
        'Plumbing emergencies don\u2019t wait for business hours',
        'Average emergency plumbing job: $500\u2013$1,500'
      ],
      sample: '\u201CI have a burst pipe flooding my basement. Can someone come right now?\u201D',
      link: '/industries/plumbing.html',
      linkText: 'See How It Works for Plumbing',
      avgJobValue: 700,
      whoLine: 'Plumbers who miss emergency calls on nights and weekends'
    },
    dental: {
      label: 'Dental',
      pain: "A patient calls to book a cleaning. Your front desk is already on another line. They hang up and book with the dentist down the street.",
      bullets: [
        'The average dental patient is worth $600\u2013$1,200/year in recurring revenue',
        '67% of patients who can\u2019t get through won\u2019t call back'
      ],
      sample: '\u201CHi, I need to schedule a teeth cleaning. Do you have any openings this week?\u201D',
      link: '/industries/dental.html',
      linkText: 'See How It Works for Dental',
      avgJobValue: 400,
      whoLine: 'Dental offices with front desk overflow and hold-time drop-offs'
    },
    legal: {
      label: 'Legal',
      pain: "A potential client calls about a personal injury case \u2014 worth $10K+ in fees. Your office is closed. They call the next firm on Google.",
      bullets: [
        'Legal intake calls are time-sensitive \u2014 the first firm to respond often wins the case',
        'Average case value: $3,000\u2013$15,000 in legal fees'
      ],
      sample: '\u201CI was in a car accident and I need to talk to a lawyer as soon as possible.\u201D',
      link: '/industries/legal.html',
      linkText: 'See How It Works for Legal',
      avgJobValue: 5000,
      whoLine: 'Law firms losing intake calls to faster-answering competitors'
    },
    medspa: {
      label: 'Med Spa',
      pain: "A new client calls to book Botox. Your receptionist is helping someone at the front desk. The call goes unanswered. That\u2019s a $500+ appointment \u2014 and a lifetime customer \u2014 lost.",
      bullets: [
        'Med spa clients expect instant booking \u2014 they won\u2019t leave voicemails',
        'Average med spa appointment: $300\u2013$800'
      ],
      sample: '\u201CHi, I\u2019d like to book a Botox consultation. What\u2019s your earliest availability?\u201D',
      link: '/industries/medspa.html',
      linkText: 'See How It Works for Med Spa',
      avgJobValue: 500,
      whoLine: 'Med spas where front desk can\u2019t keep up with booking calls'
    },
    locksmith: {
      label: 'Locksmith',
      pain: "Someone\u2019s locked out at midnight. They need help NOW. Your phone goes to voicemail. They call the next locksmith. That\u2019s a $175 job in 15 minutes, gone.",
      bullets: [
        'Locksmith calls are 100% emergencies \u2014 every missed call is a missed job',
        'Average lockout job: $150\u2013$300, done in under an hour'
      ],
      sample: '\u201CI\u2019m locked out of my car at the Walmart parking lot. Can someone come right now?\u201D',
      link: '/industries/locksmith.html',
      linkText: 'See How It Works for Locksmith',
      avgJobValue: 200,
      whoLine: 'Locksmiths who can\u2019t answer when they\u2019re on a job'
    },
    roofing: {
      label: 'Roofing',
      pain: "A storm just hit. Homeowners are calling every roofer in town. You\u2019re on a job site. The ones who answer first book $5K\u2013$15K roof replacements.",
      bullets: [
        'Storm season creates massive call volume you can\u2019t handle alone',
        'Average roof repair: $500\u2013$2,000. Replacement: $8,000\u2013$15,000'
      ],
      sample: '\u201CWe had a big storm last night and I think my roof is damaged. Can someone come look at it?\u201D',
      link: '/industries/roofing.html',
      linkText: 'See How It Works for Roofing',
      avgJobValue: 3000,
      whoLine: 'Roofers overwhelmed during storm season call surges'
    },
    other: {
      label: 'Other',
      pain: "Every service business has the same problem: when you\u2019re busy doing the work, you can\u2019t answer the phone. And every missed call is money walking out the door.",
      bullets: [
        'We serve 17+ industries \u2014 from towing to veterinary to property management',
        'If your business answers phones, The Call Taker works for you'
      ],
      sample: '\u201CHi, I need to schedule a service appointment. What\u2019s your availability this week?\u201D',
      link: '/industries/',
      linkText: 'See All Industries',
      avgJobValue: 500,
      whoLine: 'Any service business that answers phones'
    }
  },

  // Week 1 setup timeline (used on pricing page)
  timeline: [
    { day: 0, title: 'Connect Your Number', desc: 'Forward your line after your setup packet is ready. Keep your existing number.', detail: 'You get a dedicated AI number. Set up call forwarding from your existing line \u2014 after hours, when busy, or 24/7. Works with any carrier.' },
    { day: 1, title: 'Industry Tuning', desc: 'We configure the AI for your exact business \u2014 services, pricing, hours, scripts.', detail: 'Tell us your services, pricing, business hours, and how you want calls handled. The AI learns your business in minutes.' },
    { day: 2, title: 'Go Live + Summaries', desc: 'AI starts taking real calls. You get a text summary after every call.', detail: 'Every call: caller name, number, what they need, and whether an appointment was booked. Sent to your phone instantly.' },
    { day: 7, title: 'Review Results', desc: 'Check how many calls were caught, jobs booked, and revenue recovered.', detail: 'Most businesses catch 5\u201315 calls in the first week they would have missed. That\u2019s real money that was walking out the door.' }
  ]
};
