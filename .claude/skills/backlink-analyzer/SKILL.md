---
name: backlink-analyzer
description: "SEO backlink analysis tool that evaluates link profiles, detects toxic links, discovers opportunities, and generates link-building strategy recommendations. Triggers: analyze backlinks, check link profile, find toxic links, link building strategy."
version: 3.0.0
---

# Backlink Analyzer

An SEO monitoring skill designed to evaluate link profiles and identify link-building opportunities.

## Core Functions

1. **Profile Overview** — Metrics like total backlinks, referring domains, and authority distribution
2. **Link Quality Assessment** — Evaluates authority and relevance of incoming links
3. **Toxic Link Detection** — Identifies harmful or spammy links requiring disavowal
4. **Competitor Comparison** — Benchmarks your profile against competitors
5. **Opportunity Discovery** — Finds potential link sources competitors use
6. **Change Tracking** — Monitors new/lost links over time
7. **Report Generation** — Comprehensive backlink strategy recommendations

## Requirements

- `AHREFS_API_KEY` for automated data collection (can operate with user-provided backlink CSV exports if API access is unavailable)

## Integration

Backlink data feeds directly into CITE scoring when paired with the domain-authority-auditor skill, mapping metrics like referring domain count, link velocity, and toxic link analysis into broader domain authority evaluation.

## References

- `references/analysis-templates.md` — Analysis report templates
- `references/link-quality-rubric.md` — Link quality scoring rubric
- `references/outreach-templates.md` — Link building outreach templates
