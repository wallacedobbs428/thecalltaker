#!/usr/bin/env python3
"""
SEO Quick Wins Audit Script — The Call Taker
Crawls all HTML files in website/ and checks:
  1. H1 tags against target keywords for 13 vertical pages
  2. Missing meta description tags
  3. Missing/wrong schema markup (Service, LocalBusiness)
  4. Missing internal links
Outputs prioritized fix list to docs/seo-audit-results.md
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
WEBSITE_DIR = REPO_ROOT / "website"
OUTPUT_FILE = REPO_ROOT / "docs" / "seo-audit-results.md"

# Target H1s for the 13 core verticals (industries/ directory)
TARGET_H1S = {
    "hvac": "AI Receptionist for HVAC Companies",
    "plumbing": "AI Answering Service for Plumbers",
    "roofing": "Virtual Receptionist for Roofing Contractors",
    "pest-control": "AI Receptionist for Pest Control Companies",
    "dental": "AI Receptionist for Dental Offices",
    "electrical": "AI Receptionist for Electricians",
    "locksmith": "AI Receptionist for Locksmiths",
    "auto-repair": "AI Receptionist for Auto Repair Shops",
    "property-management": "AI Receptionist for Property Managers",
    "veterinary": "AI Receptionist for Veterinary Clinics",
    "medspa": "AI Receptionist for Med Spas",
    "legal": "AI Receptionist for Law Firms",
    "towing": "AI Receptionist for Towing Companies",
}

# Extended verticals (not in the core 13 but exist on site)
EXTENDED_VERTICALS = {
    "funeral": "AI Receptionist for Funeral Homes",
    "garage-door": "AI Receptionist for Garage Door Companies",
    "insurance": "AI Receptionist for Insurance Agencies",
    "real-estate": "AI Receptionist for Real Estate Agents",
    "restaurant": "AI Receptionist for Restaurants",
}


def extract_h1(html):
    match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    if match:
        text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    return None


def extract_meta_description(html):
    match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', html, re.IGNORECASE)
    if not match:
        match = re.search(r'<meta\s+content=["\']([^"\']*?)["\']\s+name=["\']description["\']', html, re.IGNORECASE)
    return match.group(1) if match else None


def extract_schema(html):
    schemas = []
    for match in re.finditer(r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE):
        try:
            data = json.loads(match.group(1))
            schemas.append(data)
        except json.JSONDecodeError:
            schemas.append({"_error": "Invalid JSON-LD"})
    return schemas


def check_internal_links(html, filename):
    issues = []
    has_home_link = bool(re.search(r'href=["\']/?["\']|href=["\']https?://thecalltaker\.com/?["\']', html))
    has_blog_link = bool(re.search(r'href=["\'][^"\']*blog[^"\']*["\']', html))
    has_pilot_link = bool(re.search(r'href=["\'][^"\']*pilot[^"\']*["\']', html))
    if not has_home_link:
        issues.append("No link back to homepage")
    if not has_blog_link:
        issues.append("No links to blog posts")
    if not has_pilot_link:
        issues.append("No link to /pilot/ CTA")
    return issues


def audit_file(filepath):
    issues = []
    rel_path = filepath.relative_to(REPO_ROOT)
    html = filepath.read_text(errors='ignore')

    # Check meta description
    meta_desc = extract_meta_description(html)
    if not meta_desc:
        issues.append(("HIGH", "Missing meta description tag"))
    elif len(meta_desc) < 50:
        issues.append(("MEDIUM", f"Meta description too short ({len(meta_desc)} chars): \"{meta_desc}\""))
    elif len(meta_desc) > 160:
        issues.append(("LOW", f"Meta description too long ({len(meta_desc)} chars)"))

    # Check H1
    h1 = extract_h1(html)
    if not h1:
        issues.append(("HIGH", "Missing H1 tag"))

    # Check schema
    schemas = extract_schema(html)
    if not schemas:
        issues.append(("MEDIUM", "No JSON-LD schema markup found"))
    else:
        schema_types = [s.get("@type", "unknown") for s in schemas if isinstance(s, dict)]
        if "Service" not in schema_types and "LocalBusiness" not in schema_types:
            issues.append(("MEDIUM", f"Schema type is {schema_types} — should include Service or LocalBusiness"))
        for s in schemas:
            offers = s.get("offers", {}) if isinstance(s, dict) else {}
            if isinstance(offers, dict) and offers.get("price") == "297":
                issues.append(("HIGH", "Schema price is $297 — should be $497"))
            elif isinstance(offers, list):
                for o in offers:
                    if isinstance(o, dict) and o.get("price") == "297":
                        issues.append(("HIGH", "Schema price is $297 — should be $497"))

    return {
        "path": str(rel_path),
        "h1": h1,
        "meta_desc": meta_desc,
        "schemas": schemas,
        "issues": issues,
    }


def audit_vertical(filepath, target_h1):
    result = audit_file(filepath)
    h1 = result["h1"]
    if h1 and h1 != target_h1:
        result["issues"].insert(0, ("HIGH", f"H1 mismatch: \"{h1}\" → should be \"{target_h1}\""))

    html = filepath.read_text(errors='ignore')
    link_issues = check_internal_links(html, filepath.name)
    for issue in link_issues:
        result["issues"].append(("LOW", issue))

    return result


def run_audit():
    results = {"verticals": [], "other_pages": [], "stats": {}}

    # Audit vertical pages
    industries_dir = WEBSITE_DIR / "industries"
    all_targets = {**TARGET_H1S, **EXTENDED_VERTICALS}

    for slug, target_h1 in sorted(all_targets.items()):
        filepath = industries_dir / f"{slug}.html"
        if filepath.exists():
            r = audit_vertical(filepath, target_h1)
            r["target_h1"] = target_h1
            r["slug"] = slug
            r["is_core"] = slug in TARGET_H1S
            results["verticals"].append(r)

    # Audit ai-answering-service pages
    seo_dir = WEBSITE_DIR / "ai-answering-service"
    if seo_dir.exists():
        for f in sorted(seo_dir.glob("*.html")):
            if f.name == "index.html":
                continue
            r = audit_file(f)
            results["other_pages"].append(r)

    # Audit core pages
    core_pages = ["index.html", "pricing.html", "book.html", "signup.html",
                  "calculator.html", "compare.html", "services.html"]
    for page in core_pages:
        filepath = WEBSITE_DIR / page
        if filepath.exists():
            r = audit_file(filepath)
            results["other_pages"].append(r)

    # Count all HTML files
    all_html = list(WEBSITE_DIR.rglob("*.html"))
    results["stats"]["total_pages"] = len(all_html)

    total_issues = sum(len(r["issues"]) for r in results["verticals"]) + \
                   sum(len(r["issues"]) for r in results["other_pages"])
    results["stats"]["total_issues"] = total_issues

    high = sum(1 for r in results["verticals"] + results["other_pages"]
               for p, _ in r["issues"] if p == "HIGH")
    medium = sum(1 for r in results["verticals"] + results["other_pages"]
                 for p, _ in r["issues"] if p == "MEDIUM")
    low = sum(1 for r in results["verticals"] + results["other_pages"]
              for p, _ in r["issues"] if p == "LOW")
    results["stats"]["high"] = high
    results["stats"]["medium"] = medium
    results["stats"]["low"] = low

    return results


def write_report(results):
    lines = []
    lines.append(f"# SEO Audit Results — The Call Taker")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"")
    lines.append(f"## Summary")
    lines.append(f"- **Total pages scanned:** {results['stats']['total_pages']}")
    lines.append(f"- **Total issues found:** {results['stats']['total_issues']}")
    lines.append(f"- HIGH: {results['stats']['high']} | MEDIUM: {results['stats']['medium']} | LOW: {results['stats']['low']}")
    lines.append(f"")

    # Vertical pages
    lines.append(f"## Vertical Pages (industries/)")
    lines.append(f"")

    for r in results["verticals"]:
        core_tag = " [CORE]" if r.get("is_core") else ""
        lines.append(f"### {r['slug']}{core_tag}")
        lines.append(f"- **File:** `{r['path']}`")
        lines.append(f"- **Current H1:** {r['h1'] or '(none)'}")
        lines.append(f"- **Target H1:** {r.get('target_h1', 'N/A')}")
        if r["issues"]:
            for priority, msg in r["issues"]:
                lines.append(f"- **[{priority}]** {msg}")
        else:
            lines.append(f"- No issues found")
        lines.append(f"")

    # Other pages
    lines.append(f"## Other Pages")
    lines.append(f"")
    for r in results["other_pages"]:
        if r["issues"]:
            lines.append(f"### `{r['path']}`")
            lines.append(f"- **H1:** {r['h1'] or '(none)'}")
            for priority, msg in r["issues"]:
                lines.append(f"- **[{priority}]** {msg}")
            lines.append(f"")

    # Priority fix list
    lines.append(f"## Priority Fix List")
    lines.append(f"")
    lines.append(f"### Tonight (HIGH priority)")
    fix_num = 1
    for r in results["verticals"]:
        for priority, msg in r["issues"]:
            if priority == "HIGH":
                lines.append(f"{fix_num}. `{r['path']}` — {msg}")
                fix_num += 1
    for r in results["other_pages"]:
        for priority, msg in r["issues"]:
            if priority == "HIGH":
                lines.append(f"{fix_num}. `{r['path']}` — {msg}")
                fix_num += 1

    lines.append(f"")
    lines.append(f"### This Week (MEDIUM priority)")
    fix_num = 1
    for r in results["verticals"] + results["other_pages"]:
        for priority, msg in r["issues"]:
            if priority == "MEDIUM":
                lines.append(f"{fix_num}. `{r['path']}` — {msg}")
                fix_num += 1

    lines.append(f"")
    lines.append(f"### Later (LOW priority)")
    fix_num = 1
    for r in results["verticals"] + results["other_pages"]:
        for priority, msg in r["issues"]:
            if priority == "LOW":
                lines.append(f"{fix_num}. `{r['path']}` — {msg}")
                fix_num += 1

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Audit report written to {OUTPUT_FILE}")
    return OUTPUT_FILE


if __name__ == "__main__":
    import sys
    results = run_audit()
    report = write_report(results)

    print(f"\n{'='*50}")
    print(f"SEO AUDIT COMPLETE")
    print(f"{'='*50}")
    print(f"Pages scanned: {results['stats']['total_pages']}")
    print(f"Issues found:  {results['stats']['total_issues']}")
    print(f"  HIGH:   {results['stats']['high']}")
    print(f"  MEDIUM: {results['stats']['medium']}")
    print(f"  LOW:    {results['stats']['low']}")
    print(f"\nReport: {report}")
