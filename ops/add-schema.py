#!/usr/bin/env python3
"""
Schema Markup Generator — The Call Taker
Adds/replaces JSON-LD Service schema on all vertical pages.
Usage: python3 ops/add-schema.py [--dry-run]
"""

import os
import re
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WEBSITE_DIR = REPO_ROOT / "website"

DRY_RUN = "--dry-run" in sys.argv

VERTICALS = {
    "hvac": {
        "name": "AI Receptionist for HVAC Companies",
        "description": "24/7 AI receptionist for HVAC companies. Answers emergency furnace and AC calls, books appointments, and texts you summaries — nights, weekends, holidays. Starting at $497/mo.",
    },
    "plumbing": {
        "name": "AI Answering Service for Plumbers",
        "description": "24/7 AI answering service for plumbing businesses. Captures emergency leak calls, books service appointments, and texts you summaries. Starting at $497/mo.",
    },
    "roofing": {
        "name": "Virtual Receptionist for Roofing Contractors",
        "description": "24/7 virtual receptionist for roofing contractors. Captures storm damage calls, books estimates, and texts you summaries. Starting at $497/mo.",
    },
    "pest-control": {
        "name": "AI Receptionist for Pest Control Companies",
        "description": "24/7 AI receptionist for pest control companies. Answers emergency calls, books treatments, and texts you summaries. Starting at $497/mo.",
    },
    "dental": {
        "name": "AI Receptionist for Dental Offices",
        "description": "24/7 AI receptionist for dental offices. Answers patient calls, books appointments, handles insurance questions, and texts you summaries. Starting at $497/mo.",
    },
    "electrical": {
        "name": "AI Receptionist for Electricians",
        "description": "24/7 AI receptionist for electrical contractors. Captures emergency calls, books service appointments, and texts you summaries. Starting at $497/mo.",
    },
    "locksmith": {
        "name": "AI Receptionist for Locksmiths",
        "description": "24/7 AI receptionist for locksmiths. Captures emergency lockout calls, dispatches jobs, and texts you summaries. Starting at $497/mo.",
    },
    "auto-repair": {
        "name": "AI Receptionist for Auto Repair Shops",
        "description": "24/7 AI receptionist for auto repair shops. Answers service calls, books appointments, and texts you summaries. Starting at $497/mo.",
    },
    "property-management": {
        "name": "AI Receptionist for Property Managers",
        "description": "24/7 AI receptionist for property management companies. Handles tenant calls, maintenance requests, and emergency dispatching. Starting at $497/mo.",
    },
    "veterinary": {
        "name": "AI Receptionist for Veterinary Clinics",
        "description": "24/7 AI receptionist for veterinary clinics. Answers pet emergency calls, books appointments, and texts you summaries. Starting at $497/mo.",
    },
    "medspa": {
        "name": "AI Receptionist for Med Spas",
        "description": "24/7 AI receptionist for med spas. Books consultations, answers treatment questions, and texts you summaries. Starting at $497/mo.",
    },
    "legal": {
        "name": "AI Receptionist for Law Firms",
        "description": "24/7 AI receptionist for law firms. Captures client intake calls, books consultations, and texts you summaries. Starting at $497/mo.",
    },
    "towing": {
        "name": "AI Receptionist for Towing Companies",
        "description": "24/7 AI receptionist for towing companies. Captures roadside assistance calls, dispatches jobs, and texts you summaries. Starting at $497/mo.",
    },
    "funeral": {
        "name": "AI Receptionist for Funeral Homes",
        "description": "24/7 AI receptionist for funeral homes. Answers family calls with compassion, books arrangements, and texts you summaries. Starting at $497/mo.",
    },
    "garage-door": {
        "name": "AI Receptionist for Garage Door Companies",
        "description": "24/7 AI receptionist for garage door companies. Captures repair and installation calls, books appointments, and texts you summaries. Starting at $497/mo.",
    },
    "insurance": {
        "name": "AI Receptionist for Insurance Agencies",
        "description": "24/7 AI receptionist for insurance agencies. Answers quote requests, captures claims information, and texts you summaries. Starting at $497/mo.",
    },
    "real-estate": {
        "name": "AI Receptionist for Real Estate Agents",
        "description": "24/7 AI receptionist for real estate agents. Captures buyer and seller leads, books showings, and texts you summaries. Starting at $497/mo.",
    },
    "restaurant": {
        "name": "AI Receptionist for Restaurants",
        "description": "24/7 AI receptionist for restaurants. Takes reservations, answers menu questions, handles catering inquiries, and texts you summaries. Starting at $497/mo.",
    },
}


def build_service_schema(slug, vertical):
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": vertical["name"],
        "description": vertical["description"],
        "url": f"https://thecalltaker.com/industries/{slug}",
        "provider": {
            "@type": "Organization",
            "name": "The Call Taker",
            "url": "https://thecalltaker.com",
            "telephone": "+16157845747",
            "founder": {
                "@type": "Person",
                "name": "Wallace Dobbs"
            }
        },
        "offers": {
            "@type": "Offer",
            "price": "497",
            "priceCurrency": "USD",
            "description": "14-day free pilot, then $497/mo. No contract."
        },
        "serviceType": "AI Receptionist",
        "areaServed": {
            "@type": "Country",
            "name": "United States"
        }
    }


def replace_schema(html, new_schema):
    schema_json = json.dumps(new_schema, indent=2)
    tag = f'<script type="application/ld+json">\n{schema_json}\n</script>'

    # Replace existing JSON-LD
    pattern = r'<script\s+type=["\']application/ld\+json["\'][^>]*>.*?</script>'
    match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    if match:
        html = html[:match.start()] + tag + html[match.end():]
        # Remove any additional JSON-LD blocks (duplicates)
        while True:
            m = re.search(pattern, html[html.index(tag) + len(tag):], re.DOTALL | re.IGNORECASE)
            if not m:
                break
            offset = html.index(tag) + len(tag) + m.start()
            html = html[:offset] + html[offset + m.end() - m.start():]
    else:
        # Insert before </head>
        html = html.replace('</head>', f'{tag}\n</head>')

    return html


def process_verticals():
    industries_dir = WEBSITE_DIR / "industries"
    updated = 0
    skipped = 0

    for slug, vertical in sorted(VERTICALS.items()):
        filepath = industries_dir / f"{slug}.html"
        if not filepath.exists():
            print(f"  SKIP {slug} — file not found")
            skipped += 1
            continue

        html = filepath.read_text(errors='ignore')
        schema = build_service_schema(slug, vertical)
        new_html = replace_schema(html, schema)

        if html != new_html:
            if DRY_RUN:
                print(f"  [DRY RUN] Would update {slug}")
            else:
                filepath.write_text(new_html)
                print(f"  UPDATED {slug}")
            updated += 1
        else:
            print(f"  OK {slug} — no changes needed")

    return updated, skipped


if __name__ == "__main__":
    print("Schema Markup Generator — The Call Taker")
    print("=" * 50)
    if DRY_RUN:
        print("MODE: Dry run (no files modified)")
    print()

    print("Processing vertical pages...")
    updated, skipped = process_verticals()

    print()
    print(f"Done. Updated: {updated}, Skipped: {skipped}")
    if DRY_RUN:
        print("(Dry run — no files were modified. Remove --dry-run to apply changes.)")
