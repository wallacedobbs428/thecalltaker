#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const websiteDir = path.join(root, 'website');
const reportPath = path.join(root, 'reports', 'websiteaudit-report.json');

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

const expectedSquareLinks = {
  after_hours_capture: 'https://square.link/u/2hfmRPY7',
  revenue_recovery_system: 'https://square.link/u/S305ewBr',
  operational_infrastructure: 'https://square.link/u/OpwWF9Sa'
};

function read(rel) {
  return fs.readFileSync(path.join(websiteDir, rel), 'utf8');
}

function exists(rel) {
  return fs.existsSync(path.join(websiteDir, rel));
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
    if (!href || href.startsWith('#') || href.startsWith('tel:') || href.startsWith('mailto:')) continue;
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

function audit() {
  const issues = [];
  const checks = [];
  const pageTexts = {};

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

  const navPages = ['index.html', 'pricing.html', 'faq.html', 'demo.html'];
  const navLabels = ['Features', 'Pricing', 'FAQ', 'Call Gideon'];
  for (const page of navPages) {
    const html = pageTexts[page] || '';
    for (const label of navLabels) {
      if (!html.includes(label)) {
        addIssue(issues, 'warn', 'nav_label', page, `Expected nav label missing: ${label}`);
      }
    }
  }

  const pricing = pageTexts['pricing.html'] || '';
  if (!pricing.includes('class="logo-text"')) {
    addIssue(issues, 'fail', 'pricing_logo', 'pricing.html', 'Pricing logo is not grouped as one wordmark; mobile can split Call/Taker.');
  }
  if (!pricing.includes('matrix-mobile-cards')) {
    addIssue(issues, 'fail', 'pricing_mobile_compare', 'pricing.html', 'Mobile comparison cards are missing; phone users may lose plan context.');
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

  const styles = exists('styles.css') ? read('styles.css') : '';
  if (!styles.includes('.exit-overlay') || !styles.includes('.exit-overlay.show')) {
    addIssue(issues, 'fail', 'exit_modal', 'styles.css', 'Exit popup overlay CSS is missing; modal may render as broken bottom-page content.');
  }
  if (!styles.includes('width: min(420px, calc(100vw - 32px))')) {
    addIssue(issues, 'warn', 'exit_modal', 'styles.css', 'Exit modal width is not visibly mobile-contained.');
  }

  const checkout = pageTexts['checkout.html'] || '';
  for (const [plan, url] of Object.entries(expectedSquareLinks)) {
    if (!checkout.includes(url)) {
      addIssue(issues, 'fail', 'square_mapping', 'checkout.html', `Expected Square URL missing for ${plan}.`, url);
    }
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

  const summary = {
    generated_at: new Date().toISOString(),
    pages_checked: publicPages,
    fail_count: issues.filter(i => i.severity === 'fail').length,
    warn_count: issues.filter(i => i.severity === 'warn').length,
    pass_count: checks.length,
    current_verdict: null,
    issues
  };
  summary.current_verdict = summary.fail_count === 0 ? 'pass_with_warnings_allowed' : 'fail';

  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(summary, null, 2) + '\n');
  return summary;
}

const report = audit();
console.log(`websiteaudit: ${report.current_verdict}`);
console.log(`pages checked: ${report.pages_checked.length}`);
console.log(`failures: ${report.fail_count}`);
console.log(`warnings: ${report.warn_count}`);
if (report.issues.length) {
  for (const issue of report.issues) {
    console.log(`${issue.severity.toUpperCase()} ${issue.file} ${issue.category}: ${issue.message}`);
  }
}
console.log(`report: ${path.relative(root, reportPath)}`);
process.exit(report.fail_count ? 1 : 0);
