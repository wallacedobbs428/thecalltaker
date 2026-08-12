#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const websiteDir = path.join(root, 'website');
const reportPath = path.join(root, 'reports', 'websiteaudit-report.json');
const websiteOpportunitiesPath = path.join(root, 'reports', 'websiteaudit-opportunities.json');

const publicPages = [
  'index.html',
  'pricing.html',
  'faq.html',
  'demo.html',
  'checkout.html',
  'pay.html',
  'start.html',
  'pilot/index.html'
];

// Only the homepage has the shared sitewide navigation. The conversion pages
// intentionally use focused layouts, so auditing them against homepage labels
// creates false alarms and hides meaningful funnel regressions.
const coreNavPages = ['index.html'];

const outerPagePatterns = [
  /^ai-receptionist-/,
  /^ai-answering-service\//,
  /^vs\//,
  /^demo\//,
  /^agency-program\//,
  /^industries\//
];

const riskyTerms = [
  'POTLUBKa',
  'Stripe',
  'PayPal',
  'Venmo',
  'no card',
  'no credit card',
  'instant live',
  'live tonight',
  'guaranteed ROI',
  'books appointments',
  '615-784-5747',
  '(615) 784-5747'
];

const staleCtaTerms = [
  'Book Demo',
  'Book a Demo'
];

const legacyPositioningTerms = [
  'generic AI receptionist',
  'fully automated',
  'never misses a lead',
  'answers every call, books every job',
  'most callers can',
  'Average ROI',
  '10-30x'
];

const expectedCheckoutRoutes = {
  afterhours: '/card-checkout.html?plan=afterhours',
  full247: '/card-checkout.html?plan=full247',
  custom: '/card-checkout.html?plan=custom'
};

function read(rel) {
  return fs.readFileSync(path.join(websiteDir, rel), 'utf8');
}

function exists(rel) {
  return fs.existsSync(path.join(websiteDir, rel));
}

function walkHtml(dir, base = '') {
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const abs = path.join(dir, entry.name);
    const rel = path.join(base, entry.name).replace(/\\/g, '/');
    if (entry.isDirectory()) {
      files.push(...walkHtml(abs, rel));
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      files.push(rel);
    }
  }
  return files.sort();
}

function addIssue(list, severity, category, file, message, evidence) {
  list.push({ severity, category, file, message, evidence: evidence || null });
}

function extractInternalLinks(html) {
  const links = [];
  const re = /\bhref=["']([^"']+)["']/gi;
  let match;
  while ((match = re.exec(html))) {
    const href = match[1].trim();
    if (!href || href.startsWith('#') || href.startsWith('tel:') || href.startsWith('mailto:') || href.startsWith('sms:')) continue;
    if (/^[a-z]+:\/\//i.test(href)) continue;
    links.push(href);
  }
  return links;
}

function normalizeLinkTarget(href) {
  const clean = href.split('#')[0].split('?')[0];
  if (!clean || clean === '/') return 'index.html';
  const withoutSlash = clean.replace(/^\//, '');
  if (withoutSlash.endsWith('/')) return withoutSlash + 'index.html';
  if (path.extname(withoutSlash)) return withoutSlash;
  return withoutSlash + '.html';
}

function isOuterGeneratedPage(page) {
  return outerPagePatterns.some((pattern) => pattern.test(page));
}

function countMatches(text, term) {
  const re = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
  return (text.match(re) || []).length;
}

function audit() {
  const issues = [];
  const checks = [];
  const pageTexts = {};
  const allHtmlPages = walkHtml(websiteDir);
  const opportunityIssues = [];

  for (const page of publicPages) {
    if (!exists(page)) {
      addIssue(issues, 'fail', 'page_exists', page, 'Public funnel page is missing.');
      continue;
    }
    pageTexts[page] = read(page);
    checks.push({ check: 'page_exists', page, status: 'pass' });
  }

  for (const [page, html] of Object.entries(pageTexts)) {
    for (const term of riskyTerms) {
      if (html.toLowerCase().includes(term.toLowerCase())) {
        addIssue(issues, 'fail', 'risky_term', page, `Risky/stale term found: ${term}`, term);
      }
    }
    for (const term of staleCtaTerms) {
      if (html.toLowerCase().includes(term.toLowerCase())) {
        addIssue(issues, 'warn', 'stale_cta_wording', page, `Old demo CTA wording found: ${term}`, term);
      }
    }
  }

  // A live-call CTA must stay unavailable until its verified path exists.
  // The production site deliberately renders the safe status label instead
  // of advertising an unverified phone demo.
  const navLabels = ['Features', 'Pricing', 'FAQ', 'Demo verification in progress'];
  for (const page of coreNavPages) {
    const html = pageTexts[page] || '';
    for (const label of navLabels) {
      if (!html.includes(label)) {
        addIssue(issues, page === 'index.html' ? 'fail' : 'warn', 'nav_label', page, `Expected nav label missing: ${label}`);
      }
    }
  }

  const home = pageTexts['index.html'] || '';
  if (!home.includes('id="navMenuToggle"') || !home.includes('.mobile-nav')) {
    addIssue(issues, 'fail', 'mobile_home_nav', 'index.html', 'Homepage is missing its mobile navigation control or menu.');
  }
  if (!home.includes('.mobile-bar {\n    display: none !important;')) {
    addIssue(issues, 'fail', 'mobile_home_cta', 'index.html', 'Homepage does not explicitly disable the retired mobile call bar.');
  }

  const pricing = pageTexts['pricing.html'] || '';
  if (!pricing.includes('class="logo-text"')) {
    addIssue(issues, 'fail', 'pricing_logo', 'pricing.html', 'Pricing logo is not grouped as one wordmark; mobile can split Call/Taker.');
  }
  if (!pricing.includes('@media (max-width: 640px)') || !pricing.includes('.matrix-table {\n        width: 100% !important;\n        min-width: 0;')) {
    addIssue(issues, 'fail', 'pricing_mobile_compare', 'pricing.html', 'Pricing comparison is not constrained to the phone viewport.');
  }
  if (!pricing.includes('After-Hours') || !pricing.includes('Recovery') || !pricing.includes('Infrastructure')) {
    addIssue(issues, 'fail', 'pricing_mobile_compare', 'pricing.html', 'Pricing comparison does not expose all plan labels.');
  }

  const faq = pageTexts['faq.html'] || '';
  if (!faq.includes('--bg: #f7f5ef')) {
    addIssue(issues, 'warn', 'faq_theme', 'faq.html', 'FAQ page does not appear to use the updated light theme token.');
  }
  if (faq.includes('Book a Demo') || faq.includes('Book Demo')) {
    addIssue(issues, 'warn', 'faq_cta', 'faq.html', 'FAQ still contains old Book Demo wording.');
  }

  const checkout = pageTexts['checkout.html'] || '';
  for (const [plan, route] of Object.entries(expectedCheckoutRoutes)) {
    if (!checkout.includes(route)) {
      addIssue(issues, 'fail', 'checkout_mapping', 'checkout.html', `Plan-preserving card checkout route missing for ${plan}.`, route);
    }
  }
  const cardCheckout = exists('card-checkout.html') ? read('card-checkout.html') : '';
  const hasSquareSdk = cardCheckout.includes('webPaymentsSdkUrl')
    && cardCheckout.includes('sandbox.web.squarecdn.com')
    && cardCheckout.includes('web.squarecdn.com');
  const hasProtectedTrialEndpoint = cardCheckout.includes("API_ORIGIN + '/api/public/square-trial'")
    && cardCheckout.includes("'https://call-taker-os.vercel.app'");
  if (!hasSquareSdk || !hasProtectedTrialEndpoint) {
    addIssue(issues, 'fail', 'card_checkout_provider', 'card-checkout.html', 'Card checkout is missing Square Web Payments or the protected trial endpoint.');
  }

  const selectedLinkPages = ['index.html', 'pricing.html', 'faq.html', 'demo.html'];
  for (const page of selectedLinkPages) {
    const html = pageTexts[page] || '';
    const links = extractInternalLinks(html);
    for (const href of links) {
      const target = normalizeLinkTarget(href);
      if (!exists(target)) {
        addIssue(issues, 'warn', 'internal_link', page, `Internal link target may be missing: ${href}`, target);
      }
    }
  }

  for (const page of allHtmlPages) {
    const html = read(page);
    if (publicPages.includes(page)) continue;
    const foundRisk = [];
    for (const term of riskyTerms.concat(staleCtaTerms, legacyPositioningTerms)) {
      const hits = countMatches(html, term);
      if (hits) foundRisk.push({ term, hits });
    }
    const generated = isOuterGeneratedPage(page);
    if (foundRisk.length) {
      opportunityIssues.push({
        severity: generated ? 'warn' : 'manual_review',
        category: generated ? 'generated_outer_page_risk' : 'outer_page_risk',
        file: page,
        generated_or_outer_page: generated,
        findings: foundRisk
      });
    }
  }

  const summary = {
    generated_at: new Date().toISOString(),
    pages_checked: publicPages,
    all_html_pages_count: allHtmlPages.length,
    core_nav_pages_checked: coreNavPages,
    fail_count: issues.filter(i => i.severity === 'fail').length,
    warn_count: issues.filter(i => i.severity === 'warn').length,
    pass_count: checks.length,
    current_verdict: null,
    issues
  };
  summary.current_verdict = summary.fail_count === 0 ? 'pass_with_warnings_allowed' : 'fail';

  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(summary, null, 2) + '\n');
  fs.writeFileSync(websiteOpportunitiesPath, JSON.stringify({
    generated_at: summary.generated_at,
    all_html_pages_count: allHtmlPages.length,
    core_funnel_pages_checked: publicPages,
    outer_pages_with_risk_count: opportunityIssues.length,
    note: 'These are wider website cleanup opportunities. Core public funnel failures are reported in websiteaudit-report.json.',
    issues: opportunityIssues
  }, null, 2) + '\n');
  return summary;
}

const report = audit();
console.log(`websiteaudit: ${report.current_verdict}`);
console.log(`pages checked: ${report.pages_checked.length}`);
console.log(`failures: ${report.fail_count}`);
console.log(`warnings: ${report.warn_count}`);
console.log(`all html pages seen: ${report.all_html_pages_count}`);
if (report.issues.length) {
  for (const issue of report.issues) {
    console.log(`${issue.severity.toUpperCase()} ${issue.file} ${issue.category}: ${issue.message}`);
  }
}
console.log(`report: ${path.relative(root, reportPath)}`);
console.log(`outer-page opportunities: ${path.relative(root, websiteOpportunitiesPath)}`);
process.exit(report.fail_count ? 1 : 0);
