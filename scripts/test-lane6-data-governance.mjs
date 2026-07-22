import assert from 'node:assert/strict';
import fs from 'node:fs';
const policy = JSON.parse(fs.readFileSync('ctos/policies/lane6-data-governance.json', 'utf8'));
for (const name of ['Square', 'Supabase', 'Vercel', 'Retell', 'Resend', 'Meta', 'Instantly', 'Bland', 'SendBlue', 'Clay', 'Apollo', 'Higgsfield']) assert.ok(policy.subprocessors.some((item) => item.name === name), `missing subprocessor: ${name}`);
assert.ok(policy.retention.every((item) => item.days > 0 && item.deletion));
for (const field of ['deletion ID', 'completion timestamp', 'backup expiry', 'exception/hold']) assert.ok(policy.deletion_verification.includes(field), `missing deletion evidence: ${field}`);
assert.equal(policy.subprocessors.find((item) => item.name === 'Retell').healthcare_gate, 'executed BAA before PHI');
console.log('Lane 6 data governance: PASS');
