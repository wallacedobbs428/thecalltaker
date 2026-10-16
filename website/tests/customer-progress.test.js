const test = require('node:test');
const assert = require('node:assert/strict');
const {customerProgress} = require('../onboarding/configuration-review');
test('verified trial and paid progression remain separate from payment receipt and current service permission', () => {
  const trial = customerProgress({customer_stage:'ENROLLMENT_VERIFIED',service_basis:'verified_trial',trial_end:'2026-11-01T07:00:00Z',current_service_permitted:false});
  assert.equal(trial.title,'Enrollment verified');assert.match(trial.basis,/not a payment receipt/);
  assert.match(trial.trial,/Setup or activation does not restart/);assert.ok(!trial.trial.includes('Invalid Date'));
  const paid=customerProgress({customer_stage:'CUSTOMER_DECISION',service_basis:'paid',current_service_permitted:false});
  assert.equal(paid.title,'Your service decisions');assert.equal(paid.basis,'Verified paid service basis.');
});
test('all customer stages use readable language without turning preparation into activation', () => {
  const stages={ENROLLMENT_RECEIVED:'Enrollment received',SETUP_NEEDED:'Setup needed',CONFIGURATION_REVIEW:'Configuration review',CUSTOMER_DECISION:'Your service decisions',READY_FOR_TESTS:'Ready for controlled tests',READY_FOR_LAUNCH:'Ready for launch review',BILLING_EXCEPTION:'Billing needs review'};
  for(const [customer_stage,title] of Object.entries(stages)) assert.equal(customerProgress({customer_stage,current_service_permitted:false}).title,title);
  assert.equal(customerProgress({customer_stage:'ACTIVE',activation_state:'ACTIVATED',current_service_permitted:false}).title,'Service status not verified');
  assert.equal(customerProgress({customer_stage:'ACTIVE',current_service_permitted:true}).title,'Service active');
  assert.equal(customerProgress({customer_stage:'future_unknown',trial_end:'bad'}).trial,null);
  assert.equal(customerProgress({customer_stage:'future_unknown'}).basis,'Service basis is not verified.');
});
