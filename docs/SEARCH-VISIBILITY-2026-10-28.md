# Search and AI visibility improvements

Scope: general website content and search visibility. No industry-specific pages are created or changed.

## Website changes

- Responsive WebP versions of the approved hero image: 640px (17,666 bytes), 960px (30,386), 1440px (50,000), 1920px (70,862), retaining the original PNG fallback (2,511,920 bytes).
- Search-focused homepage metadata and descriptive headings on the existing service pages.
- Shared navigation and contextual links to general resources.
- General About/Contact page with one public support inbox and accurate Organization markup. Existing service markup is retained; incomplete logo data and the misleading homepage maximum-price aggregate are removed.
- Coverage comparison, reusable intake script, escalation checklist, contribution worksheet, and explicitly fictional written call/summary illustration.
- New FAQ answers covering existing numbers, appointment requests, escalation and plan scope.
- Existing homepage estimator describes hypothetical gross value and exclusions rather than money saved.
- General resource pages are added to the sitemap and explicit GitHub Pages publication allowlist. No generated industry/location pages are released.
- Known AI UTM sources map to the existing allowed referral category. The canonical producer continues to send only a normalized referrer hostname, which the existing server hashes. Conversation paths and query strings are not emitted.
- Resource page views use the existing event contract. No additional analytics provider, server endpoint or competing tracker is introduced.

## Verification

- `node --test tests/website*.test.js website/tests/*.test.js`
- `python3 tests/search-visibility-report.test.py`
- `npm ci --ignore-scripts --prefix tools/demo-evaluation-sdk`
- `npm run build --prefix tools/demo-evaluation-sdk`
- Exact Pages artifact preparation, followed by a local file-target audit of all 13 sitemap pages.
- Desktop/mobile browser inspection, image selection, calculator zero-conversion behavior and keyboard menu dismissal.

## Local measurement

`scripts/search-visibility-report.py` accepts bounded CSV/JSON exports. It summarizes positions 8–20, classifies known AI referrers (including the existing server's SHA-256 representation), excludes controlled test events and never includes raw queries, conversation URLs, visitor identifiers or event bodies in its output. Missing input is reported as missing, never as zero traffic.

Example:

```sh
python3 scripts/search-visibility-report.py --search-export search-export.csv --events-export events-export.json --output search-summary.json
```

Reports count observations rather than unique visitors, recommendations, calls, sales or revenue. Referrer information can be absent; the source aliases intentionally use the existing `referral` category rather than changing server enums.

## Remaining external prerequisites

- The owner approved Google and Bing verification for thecalltakerservice@gmail.com on October 28, 2026. The corresponding public verification tags are included; verification and sitemap results must be independently read back after publication.
- Authenticated search reports are unavailable before verification. Rankings, indexing, AI citations and subsequent change in traffic are not yet established.
- Publication clearance and a defined cohort are required before publishing real customer results or recordings. The new written example is explicitly fictional.
- Earned editorial coverage, customer reviews and backlinks require real independent participation. No coverage or recommendation is promised or represented as secured.
- No automatic recurring schedule is installed. The owner can rerun the reporting tool when new exports are available.

## Provider boundary

This change does not alter payments, phone routing, voice agents, database schema, billing or scheduled services. No email/SMS/call is initiated by the implementation. Website publication remains the existing GitHub Pages workflow.
