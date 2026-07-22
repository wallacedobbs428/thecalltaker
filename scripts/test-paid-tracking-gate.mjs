import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
function pages(dir, result = []) {
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) pages(full, result);
    else if (entry.isFile() && entry.name.endsWith('.html')) result.push(full);
  }
  return result;
}
const blocked = /connect\.facebook\.net|tracking\.thecalltaker\.com|AW-17970510102|fbq\(['"]track|gtag\(['"]event['"],\s*['"]conversion/i;
for (const page of pages('website')) assert.doesNotMatch(fs.readFileSync(page, 'utf8'), blocked, `${page} must not emit paid conversion tracking`);
console.log('paid tracking gate: PASS');
