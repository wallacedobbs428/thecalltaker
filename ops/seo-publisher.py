#!/usr/bin/env python3
"""
SEO Publisher — The Call Taker
Generates state+vertical location pages from template.
Usage: python3 ops/seo-publisher.py [--dry-run]
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_FILE = REPO_ROOT / "docs" / "templates" / "location-page.html"
OUTPUT_DIR = REPO_ROOT / "website" / "pages" / "locations"

DRY_RUN = "--dry-run" in sys.argv

STATES = {
    "TX": {"name": "Texas", "slug": "texas"},
    "FL": {"name": "Florida", "slug": "florida"},
    "CA": {"name": "California", "slug": "california"},
    "GA": {"name": "Georgia", "slug": "georgia"},
    "NC": {"name": "North Carolina", "slug": "north-carolina"},
    "AZ": {"name": "Arizona", "slug": "arizona"},
    "OH": {"name": "Ohio", "slug": "ohio"},
    "PA": {"name": "Pennsylvania", "slug": "pennsylvania"},
    "IL": {"name": "Illinois", "slug": "illinois"},
    "MI": {"name": "Michigan", "slug": "michigan"},
}

VERTICALS = {
    "hvac": {
        "name": "HVAC",
        "lower": "HVAC",
        "slug": "hvac",
        "job_word": "service call",
        "avg_job_value": "350",
    },
    "plumbing": {
        "name": "Plumbing",
        "lower": "plumbing",
        "slug": "plumbing",
        "job_word": "service call",
        "avg_job_value": "300",
    },
    "roofing": {
        "name": "Roofing",
        "lower": "roofing",
        "slug": "roofing",
        "job_word": "estimate",
        "avg_job_value": "8500",
    },
}


def generate_page(template, state, vertical):
    html = template
    replacements = {
        "[STATE]": state["name"],
        "[STATE_SLUG]": state["slug"],
        "[VERTICAL]": vertical["name"],
        "[VERTICAL_LOWER]": vertical["lower"],
        "[VERTICAL_SLUG]": vertical["slug"],
        "[JOB_WORD]": vertical["job_word"],
        "[AVG_JOB_VALUE]": vertical["avg_job_value"],
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    return html


def run():
    if not TEMPLATE_FILE.exists():
        print(f"ERROR: Template not found at {TEMPLATE_FILE}")
        sys.exit(1)

    template = TEMPLATE_FILE.read_text()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    generated = 0
    for state_code, state in sorted(STATES.items()):
        for vert_key, vertical in sorted(VERTICALS.items()):
            filename = f"{state['slug']}-{vertical['slug']}-ai-receptionist.html"
            filepath = OUTPUT_DIR / filename

            html = generate_page(template, state, vertical)

            if DRY_RUN:
                print(f"  [DRY RUN] Would create: {filename}")
            else:
                filepath.write_text(html)
                print(f"  CREATED: {filename}")
            generated += 1

    print(f"\nGenerated {generated} pages in {OUTPUT_DIR}")
    if DRY_RUN:
        print("(Dry run — no files written. Remove --dry-run to generate.)")


if __name__ == "__main__":
    print("SEO Publisher — The Call Taker")
    print("=" * 50)
    run()
