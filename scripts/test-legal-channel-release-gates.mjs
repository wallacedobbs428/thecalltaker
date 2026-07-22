import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = (path) => JSON.parse(fs.readFileSync(path, 'utf8'));
const gates = read('ctos/policies/legal-channel-release-gates.json');
const outbound = read('ctos/policies/autonomous-outbound-policy.json');
const limits = read('ctos/policies/channel-safety-limits.json');
const lanes = read('ctos/policies/lane6-operating-controls.json');

assert.equal(gates.default, 'do_not_send_or_activate');
assert.equal(gates.channels.manual_b2b_email.status, 'ALLOW_WITH_CONTROLS');
assert.equal(gates.channels.transactional_setup_service_sms.status, 'SAFE_INTERIM_PATH');
for (const channel of ['marketing_sms_mms', 'outbound_ai_or_prerecorded_voice', 'outbound_live_agent_calls', 'paid_conversion_tracking', 'healthcare_phi_recording_transcription_summary_email_crm']) assert.equal(gates.channels[channel].status, 'HOLD_UNTIL_EXACT_FACT', `${channel} must remain gated`);
assert.equal(gates.channels.american_surgical_no_phi_routing.status, 'SAFE_INTERIM_PATH');
assert.equal(outbound.send_gate.default, 'do_not_send_or_activate');
assert.equal(outbound.autonomous_actions_allowed.some((item) => /send messages|send low-risk replies|schedule follow-ups/.test(item)), false);
const instantly = limits.daily_limits.find((item) => item.channel === 'Instantly email');
assert.equal(instantly.max_per_campaign_per_day, 0);
assert.equal(instantly.autonomous_sending_allowed, false);
for (const lane of ['lane2_acquisition', 'lane3_buyer_path', 'lane4_growth', 'lane5_healthcare']) assert.ok(lanes.lanes[lane], `missing ${lane} control`);
assert.equal(lanes.lanes.lane2_acquisition.safe_path, 'manual_b2b_email');
assert.equal(lanes.lanes.lane3_buyer_path.safe_path, 'card_trial_checkout');
assert.equal(lanes.lanes.lane4_growth.safe_path, 'factual_organic_content');
assert.equal(lanes.lanes.lane5_healthcare.safe_path, 'american_surgical_no_phi_routing');
console.log('legal channel release gates: PASS');
