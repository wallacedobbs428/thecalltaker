(function (root) {
  'use strict';
  function calculate(values) {
    var limits = {missed:1000000,answered:100,qualified:100,closed:100,contribution:10000000,cost:1000000};
    for (var key in limits) {
      if (typeof values[key] !== 'number' || !Number.isFinite(values[key]) || values[key] < 0 || values[key] > limits[key]) return null;
    }
    var jobs = values.missed * values.answered / 100 * values.qualified / 100 * values.closed / 100;
    return {jobs:jobs, beforeCost:jobs * values.contribution, afterCost:jobs * values.contribution - values.cost};
  }
  if (typeof module === 'object' && module.exports) module.exports = {calculate:calculate};
  if (!root.document) return;
  var doc = root.document, form = doc.getElementById('missed-call-worksheet'), output = doc.getElementById('worksheet-output');
  if (!form || !output) return;
  function update() {
    var values = {};
    ['missed','answered','qualified','closed','contribution','cost'].forEach(function (key) {
      var input = doc.getElementById(key);
      values[key] = input.value.trim() === '' ? NaN : Number(input.value);
    });
    var result = calculate(values);
    if (!result) { output.textContent = 'Enter a valid number in every field. Percentages must be between 0 and 100.'; return; }
    var dollars = new Intl.NumberFormat('en-US', {style:'currency',currency:'USD',maximumFractionDigits:2});
    output.textContent = result.jobs.toFixed(2) + ' estimated jobs in this scenario; ' + dollars.format(result.beforeCost) + ' contribution before coverage; ' + dollars.format(result.afterCost) + ' after coverage cost. This is an illustration, not a forecast.';
  }
  form.addEventListener('input', update);
  update();
}(typeof window === 'undefined' ? {} : window));
