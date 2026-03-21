#!/usr/bin/env node
/**
 * gen-close-links.js — Generate personalized close URLs for oracle-hot contacts
 *
 * Usage:
 *   node gen-close-links.js                    # Uses closer-data.json
 *   node gen-close-links.js oracle-hot.json    # Uses custom JSON input
 *
 * Input JSON format (array of contacts):
 *   [{ "name": "Greg", "company": "Carolina Locksmith", "industry": "locksmith", "phone": "+19196083694", "score": 8, "id": "ghl-contact-id" }]
 *
 * Output:
 *   - Prints personalized URLs + SMS copy to stdout
 *   - Writes oracle-hot-enrollment.csv for GHL bulk import
 */

const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://thecalltaker.com/close/';

// Load contacts
const inputFile = process.argv[2] || path.join(__dirname, 'website', 'closer-data.json');
let contacts;

try {
  const raw = fs.readFileSync(inputFile, 'utf8');
  const data = JSON.parse(raw);
  contacts = data.leads || data;
  if (!Array.isArray(contacts)) {
    console.error('Error: Input must be an array of contacts or have a "leads" key');
    process.exit(1);
  }
} catch (err) {
  console.error('Error reading input file:', err.message);
  process.exit(1);
}

// Sort by score descending
contacts.sort((a, b) => (b.score || 0) - (a.score || 0));

// CSV-safe: prevent formula injection in spreadsheet apps
function csvSafe(str) {
  str = String(str || '');
  if (/^[=+\-@\t\r]/.test(str)) str = "'" + str;
  return str.replace(/"/g, '""');
}

// Generate URLs
const results = contacts.map(c => {
  const firstName = (c.name || c.first_name || '').split(' ')[0];
  const company = c.company || c.company_name || '';
  const vertical = c.industry || c.vertical || c.custom_vertical || 'general';
  const phone = c.phone || '';
  const score = c.score || 0;
  const id = c.id || c.contactId || '';

  const params = new URLSearchParams({
    name: firstName,
    biz: company,
    vertical: vertical
  });

  const url = BASE_URL + '?' + params.toString();

  return { firstName, company, vertical, phone, score, id, url };
});

// Print top contacts with copy-paste ready SMS
console.log('');
console.log('═══════════════════════════════════════════════════════');
console.log(' ORACLE-HOT CLOSE LINKS — ' + results.length + ' contacts');
console.log('═══════════════════════════════════════════════════════');
console.log('');

results.forEach((r, i) => {
  console.log(`${i + 1}. ${r.firstName} — ${r.company} (${r.vertical})`);
  console.log(`   Phone: ${r.phone}`);
  console.log(`   Score: ${r.score}`);
  console.log(`   URL:   ${r.url}`);
  console.log('');

  if (i < 5) {
    // Print SMS copy for top 5
    console.log('   ── MSG 1 (send now) ──');
    console.log(`   Hey ${r.firstName} — this is Wallace from The Call Taker. I built a demo of Jessica answering your phones as ${r.company}. Takes 10 seconds to hear: ${r.url}`);
    console.log('   Want to grab one of the last 7 founding spots? Reply STOP to opt out.');
    console.log('');
    console.log('   ── MSG 2 (24hr, no reply) ──');
    console.log(`   ${r.firstName} — sent you a demo yesterday of Jessica answering as ${r.company}. Missed calls cost you real jobs. She never misses one. Link still works: ${r.url} Reply STOP to opt out.`);
    console.log('');
    console.log('   ── MSG 3 (48hr, no reply) ──');
    console.log(`   Last one from me, ${r.firstName}. Founding rate locks in at $264/mo — goes to $497 after we fill the last spots. Your demo: ${r.url}. Reply STOP to opt out.`);
    console.log('');
  }
  console.log('───────────────────────────────────────────────────────');
});

// Write CSV for GHL bulk enrollment
const csvHeader = 'contact_id,first_name,company,vertical,phone,score,close_url';
const csvRows = results.map(r =>
  `${csvSafe(r.id)},"${csvSafe(r.firstName)}","${csvSafe(r.company)}","${csvSafe(r.vertical)}","${csvSafe(r.phone)}",${r.score},"${csvSafe(r.url)}"`
);
const csvContent = [csvHeader, ...csvRows].join('\n');
const csvPath = path.join(__dirname, 'oracle-hot-enrollment.csv');
fs.writeFileSync(csvPath, csvContent);
console.log('');
console.log(`Enrollment CSV written to: ${csvPath}`);
console.log(`Total contacts: ${results.length}`);
