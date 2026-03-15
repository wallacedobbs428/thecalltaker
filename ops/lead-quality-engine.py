#!/usr/bin/env python3
"""
LEAD QUALITY ENGINE — The Call Taker
=====================================
Deduplication + quality scoring pipeline that runs before any lead
touches the blast engines. Keeps reputation clean and email lists tight.

Scoring (1-10):
  +3  Has a valid email address
  +2  Has owner first name
  +1  Has a website URL
  +2  Has Google review data (count or rating mentioned)
  +2  Has been in business 2+ years (inferred from "established", "since YYYY",
      "founded YYYY", or review count >= 20)

Deduplication:
  1. Phone number exact match against GHL contacts
  2. Business name fuzzy match (>= 85% similarity) against GHL contacts
  If either hits → marked duplicate, skipped.

Only leads with quality_score >= 5 pass to blast engines.

Commands:
  score <csv>   — Score all leads in CSV, output scored CSV
  dedup <csv>   — Check CSV against GHL, flag duplicates
  process <csv> — Full pipeline: dedup + score + filter (5+) + clean CSV
  audit         — Scan existing GHL contacts for internal duplicates
  report        — Print daily scraper performance report
  status        — Show engine stats from state file

Output: ~/thecalltaker/ops/scored-leads-{YYYY-MM-DD}.csv
State:  ~/thecalltaker/ops/lead-quality-state.json
Report: ~/thecalltaker/ops/scraper-report.json
Log:    ~/thecalltaker/ops/lead-quality.log
"""

import sys
import os
import csv
import json
import re
import time
import logging
import requests
import tempfile
from datetime import datetime, date
from pathlib import Path
from difflib import SequenceMatcher

# ─── Paths ───────────────────────────────────────────────────────────────────

OPS_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(OPS_DIR, "lead-quality-state.json")
REPORT_FILE = os.path.join(OPS_DIR, "scraper-report.json")
LOG_FILE = os.path.join(OPS_DIR, "lead-quality.log")
TODAY = date.today().isoformat()

# ─── GHL Config ──────────────────────────────────────────────────────────────

GHL_API_KEY = os.environ.get("TCT_GHL_API_KEY", "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID = os.environ.get("TCT_GHL_LOCATION_ID", "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"

CONTACTS_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TheCallTaker-LeadQualityEngine/1.0",
}

# ─── ntfy Config ─────────────────────────────────────────────────────────────

NTFY_ACTIVITY = "tct-activity-cn1Aqa85"
NTFY_SYSTEM = "tct-system-vRsfXQRQ"

# ─── Quality Thresholds ───────────────────────────────────────────────────────

MIN_QUALITY_SCORE = 5
FUZZY_NAME_THRESHOLD = 0.85   # 85% similarity = duplicate

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("lead-quality")

# ─── Utility: State File (atomic write) ──────────────────────────────────────

def load_state() -> dict:
    """Load state file, return empty skeleton if missing or corrupt."""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "last_run": None,
            "total_processed": 0,
            "total_duplicates_caught": 0,
            "total_scored": 0,
            "total_passed": 0,
            "total_failed_quality": 0,
            "daily": {},
        }


def save_state(state: dict) -> None:
    """Atomically write state to disk."""
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def load_report() -> dict:
    """Load report file, return empty skeleton if missing."""
    try:
        with open(REPORT_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"days": {}}


def save_report(report: dict) -> None:
    tmp = REPORT_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(report, f, indent=2)
    os.replace(tmp, REPORT_FILE)

# ─── Utility: ntfy ───────────────────────────────────────────────────────────

def ntfy(topic: str, title: str, message: str, priority: str = "default") -> None:
    """Send a notification to ntfy.sh (best-effort, never crashes the engine)."""
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title": title[:250],
                "Priority": priority,
                "Tags": "chart_with_upwards_trend",
            },
            timeout=8,
        )
    except Exception as e:
        log.warning(f"ntfy failed: {e}")

# ─── Utility: Phone Normalizer ───────────────────────────────────────────────

def normalize_phone(raw: str) -> str:
    """Strip all non-digits, return 10-digit US number or empty string."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", str(raw))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return digits
    return ""


def phone_to_e164(digits: str) -> str:
    """Convert 10-digit to +1XXXXXXXXXX format."""
    if len(digits) == 10:
        return f"+1{digits}"
    return digits

# ─── Utility: Fuzzy Name Match ───────────────────────────────────────────────

def fuzzy_ratio(a: str, b: str) -> float:
    """Return similarity ratio 0.0-1.0 between two strings (case-insensitive)."""
    a = re.sub(r"\s+", " ", a.strip().lower())
    b = re.sub(r"\s+", " ", b.strip().lower())
    # Strip common suffixes that inflate false-negatives
    for suffix in [" llc", " inc", " corp", " co", " ltd", " lp", " hvac",
                   " services", " service", " solutions", " group", " company"]:
        a = a.replace(suffix, "")
        b = b.replace(suffix, "")
    return SequenceMatcher(None, a.strip(), b.strip()).ratio()

# ─── GHL API Helpers ─────────────────────────────────────────────────────────

def ghl_search_contacts(query: str, limit: int = 5) -> list:
    """
    Search GHL contacts by phone or business name.
    Returns list of contact dicts.
    """
    url = f"{GHL_BASE_URL}/contacts/"
    params = {
        "locationId": GHL_LOCATION_ID,
        "query": query,
        "limit": limit,
    }
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=CONTACTS_HEADERS, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("contacts", [])
            elif resp.status_code == 429:
                wait = 30 * (attempt + 1)
                log.warning(f"GHL rate limit hit, waiting {wait}s")
                time.sleep(wait)
            else:
                log.warning(f"GHL search returned {resp.status_code} for '{query}'")
                return []
        except Exception as e:
            log.warning(f"GHL search error (attempt {attempt+1}): {e}")
            time.sleep(5)
    return []


def ghl_list_all_contacts(page_size: int = 100) -> list:
    """
    Page through all GHL contacts for the audit command.
    Returns full list of contact dicts.
    """
    all_contacts = []
    page = 1
    while True:
        url = f"{GHL_BASE_URL}/contacts/"
        params = {
            "locationId": GHL_LOCATION_ID,
            "limit": page_size,
            "page": page,
        }
        try:
            resp = requests.get(url, headers=CONTACTS_HEADERS, params=params, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                batch = data.get("contacts", [])
                if not batch:
                    break
                all_contacts.extend(batch)
                log.info(f"  Fetched page {page}: {len(batch)} contacts (total {len(all_contacts)})")
                page += 1
                time.sleep(0.5)  # be gentle with the API
            elif resp.status_code == 429:
                log.warning("GHL rate limit during full scan, sleeping 30s")
                time.sleep(30)
            else:
                log.warning(f"GHL list returned {resp.status_code} on page {page}")
                break
        except Exception as e:
            log.warning(f"GHL list error on page {page}: {e}")
            break
    return all_contacts

# ─── Deduplication ───────────────────────────────────────────────────────────

def check_duplicate_against_ghl(phone: str, company_name: str) -> tuple[bool, str]:
    """
    Check if a lead already exists in GHL.
    Returns (is_duplicate, reason).
    Priority: phone match first, then fuzzy name match.
    """
    # 1. Phone check (exact, fast)
    norm_phone = normalize_phone(phone)
    if norm_phone:
        e164 = phone_to_e164(norm_phone)
        results = ghl_search_contacts(e164)
        if not results:
            # Try without country code
            results = ghl_search_contacts(norm_phone)
        for contact in results:
            existing_phone = normalize_phone(contact.get("phone", ""))
            if existing_phone and existing_phone == norm_phone:
                existing_name = contact.get("companyName") or contact.get("name", "?")
                return True, f"Phone match: {e164} exists as '{existing_name}' (GHL ID {contact.get('id', '?')})"
        time.sleep(0.3)  # small delay between searches

    # 2. Business name fuzzy match
    if company_name and company_name.strip():
        results = ghl_search_contacts(company_name.strip()[:50])
        for contact in results:
            existing_company = contact.get("companyName", "") or ""
            if not existing_company:
                # fall back to full name field
                existing_company = contact.get("name", "") or ""
            if existing_company:
                ratio = fuzzy_ratio(company_name, existing_company)
                if ratio >= FUZZY_NAME_THRESHOLD:
                    return True, (
                        f"Name fuzzy match ({ratio:.0%}): '{company_name}' ~ "
                        f"'{existing_company}' (GHL ID {contact.get('id', '?')})"
                    )
        time.sleep(0.3)

    return False, ""


def check_duplicate_in_batch(phone: str, company_name: str,
                              seen_phones: set, seen_names: list) -> tuple[bool, str]:
    """
    Fast in-memory dedup check within the current CSV batch.
    Prevents the same row appearing twice in one file.
    """
    norm = normalize_phone(phone)
    if norm and norm in seen_phones:
        return True, f"Duplicate phone in batch: {norm}"

    if company_name and company_name.strip():
        clean = company_name.strip().lower()
        for existing in seen_names:
            if fuzzy_ratio(clean, existing) >= FUZZY_NAME_THRESHOLD:
                return True, f"Duplicate name in batch: '{company_name}' ~ '{existing}'"

    return False, ""

# ─── Quality Scoring ─────────────────────────────────────────────────────────

# Year patterns: "since 2018", "est. 2015", "founded in 2010", "established 2019"
_YEAR_RE = re.compile(
    r"\b(since|est\.?|established|founded\s+in?|in\s+business\s+since)\s*(\d{4})\b",
    re.IGNORECASE,
)

# Review count patterns: "150 reviews", "23 Google reviews"
_REVIEW_COUNT_RE = re.compile(r"\b(\d+)\s*(?:google\s+)?reviews?\b", re.IGNORECASE)

# Star/rating patterns: "4.8 stars", "rated 4.9", "4.7/5"
_RATING_RE = re.compile(r"\b([1-5](?:\.\d)?)\s*(?:stars?|/\s*5|star\s+rating)\b", re.IGNORECASE)


def _has_email(row: dict) -> bool:
    email = (row.get("email") or row.get("Email") or "").strip()
    return bool(email) and "@" in email and "." in email.split("@")[-1]


def _has_owner_name(row: dict) -> bool:
    fname = (row.get("firstName") or row.get("first_name") or
             row.get("owner_name") or row.get("owner") or "").strip()
    return bool(fname) and len(fname) >= 2


def _has_website(row: dict) -> bool:
    site = (row.get("website") or row.get("Website") or
            row.get("url") or row.get("URL") or "").strip()
    return bool(site) and ("." in site) and len(site) > 4


def _has_reviews(row: dict) -> bool:
    """Return True if any field contains a review count or rating."""
    combined = " ".join(str(v) for v in row.values() if v)
    if _REVIEW_COUNT_RE.search(combined):
        return True
    if _RATING_RE.search(combined):
        return True
    # Check dedicated columns
    for key in ("google_reviews", "reviews", "rating", "review_count",
                "googleReviews", "reviewCount", "stars"):
        val = str(row.get(key) or "").strip()
        if val and val not in ("0", "none", "n/a", ""):
            return True
    return False


def _has_review_count_20plus(row: dict) -> bool:
    """Specifically check if review count >= 20 (used as longevity signal)."""
    combined = " ".join(str(v) for v in row.values() if v)
    match = _REVIEW_COUNT_RE.search(combined)
    if match:
        try:
            return int(match.group(1)) >= 20
        except ValueError:
            pass
    # Also check dedicated columns
    for key in ("google_reviews", "reviews", "review_count", "googleReviews", "reviewCount"):
        val = str(row.get(key) or "").strip()
        try:
            if int(val) >= 20:
                return True
        except (ValueError, TypeError):
            pass
    return False


def _established_2plus_years(row: dict) -> bool:
    """
    Return True if we can infer the business has been operating >= 2 years.
    Sources: year-founding strings, review count >= 20.
    """
    current_year = datetime.now().year
    combined = " ".join(str(v) for v in row.values() if v)

    # Check year strings
    for match in _YEAR_RE.finditer(combined):
        try:
            founded = int(match.group(2))
            if current_year - founded >= 2:
                return True
        except ValueError:
            pass

    # Also check a dedicated "years_in_business" column
    yib = str(row.get("years_in_business") or row.get("yearsInBusiness") or "").strip()
    try:
        if float(yib) >= 2:
            return True
    except (ValueError, TypeError):
        pass

    # High review count signals longevity
    if _has_review_count_20plus(row):
        return True

    return False


def score_lead(row: dict) -> tuple[int, list]:
    """
    Score a lead row 1-10.
    Returns (score, list_of_reasons).
    Score is capped at 10.
    """
    score = 0
    reasons = []

    if _has_email(row):
        score += 3
        reasons.append("+3 has email")

    if _has_owner_name(row):
        score += 2
        reasons.append("+2 has owner name")

    if _has_website(row):
        score += 1
        reasons.append("+1 has website")

    if _has_reviews(row):
        score += 2
        reasons.append("+2 has Google reviews")

    if _established_2plus_years(row):
        score += 2
        reasons.append("+2 in business 2+ years")

    # Floor at 1, cap at 10
    score = max(1, min(10, score))
    return score, reasons

# ─── CSV Helpers ─────────────────────────────────────────────────────────────

OUTPUT_COLUMNS = [
    "firstName", "companyName", "phone", "email",
    "city", "state", "industry",
    "quality_score", "is_duplicate", "skip_reason",
]

# Maps common CSV column aliases to our canonical names
COLUMN_ALIASES = {
    "first_name": "firstName",
    "name": "firstName",
    "owner_name": "firstName",
    "company": "companyName",
    "business_name": "companyName",
    "company_name": "companyName",
    "businessName": "companyName",
    "phone_number": "phone",
    "mobile": "phone",
    "email_address": "email",
    "e-mail": "email",
    "location": "city",
    "vertical": "industry",
    "niche": "industry",
    "website": "website",  # keep as-is for scoring
    "url": "website",
    "google_reviews": "google_reviews",
    "reviews": "google_reviews",
    "rating": "rating",
    "years_in_business": "years_in_business",
}


def normalize_row(row: dict) -> dict:
    """Rename aliased columns to canonical names."""
    normalized = {}
    for k, v in row.items():
        canonical = COLUMN_ALIASES.get(k.strip(), k.strip())
        normalized[canonical] = v
    return normalized


def read_csv(filepath: str) -> list[dict]:
    """Read a CSV file and return list of row dicts."""
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(normalize_row(row))
    return rows


def write_csv(filepath: str, rows: list[dict]) -> None:
    """Write rows to a CSV, ensuring all OUTPUT_COLUMNS are present."""
    # Collect all keys that exist in any row, plus our required columns
    all_keys = list(OUTPUT_COLUMNS)
    for row in rows:
        for k in row:
            if k not in all_keys:
                all_keys.append(k)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_score(csv_path: str) -> None:
    """Score all leads in a CSV. Output scored CSV. No dedup."""
    log.info(f"[SCORE] Reading {csv_path}")
    rows = read_csv(csv_path)
    log.info(f"[SCORE] {len(rows)} leads loaded")

    state = load_state()
    today_stats = state["daily"].setdefault(TODAY, {
        "processed": 0, "scored": 0, "passed": 0, "failed_quality": 0,
        "duplicates": 0, "score_distribution": {str(i): 0 for i in range(1, 11)},
        "by_vertical": {},
    })

    scored_rows = []
    for row in rows:
        q, reasons = score_lead(row)
        row["quality_score"] = q
        row["is_duplicate"] = "false"
        row["skip_reason"] = "" if q >= MIN_QUALITY_SCORE else f"quality_score={q} (min {MIN_QUALITY_SCORE})"
        row["_score_reasons"] = " | ".join(reasons)

        today_stats["processed"] += 1
        today_stats["scored"] += 1
        today_stats["score_distribution"][str(q)] = today_stats["score_distribution"].get(str(q), 0) + 1

        vertical = (row.get("industry") or "unknown").lower()
        today_stats["by_vertical"][vertical] = today_stats["by_vertical"].get(vertical, 0) + 1

        if q >= MIN_QUALITY_SCORE:
            today_stats["passed"] += 1
        else:
            today_stats["failed_quality"] += 1

        scored_rows.append(row)

    out_path = os.path.join(OPS_DIR, f"scored-leads-{TODAY}.csv")
    write_csv(out_path, scored_rows)

    state["total_processed"] += len(rows)
    state["total_scored"] += len(rows)
    state["total_passed"] += today_stats["passed"]
    state["total_failed_quality"] += today_stats["failed_quality"]
    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    passed = sum(1 for r in scored_rows if int(r["quality_score"]) >= MIN_QUALITY_SCORE)
    log.info(f"[SCORE] Done. {len(rows)} scored. {passed} pass (>= {MIN_QUALITY_SCORE}). Output: {out_path}")

    ntfy(
        NTFY_ACTIVITY,
        "Lead Quality Score Complete",
        f"{len(rows)} leads scored. {passed} passed quality filter (score >= {MIN_QUALITY_SCORE}).\nOutput: {out_path}",
    )


def cmd_dedup(csv_path: str) -> None:
    """Check CSV against GHL contacts. Flag duplicates. Write output CSV."""
    log.info(f"[DEDUP] Reading {csv_path}")
    rows = read_csv(csv_path)
    log.info(f"[DEDUP] {len(rows)} leads to check against GHL")

    state = load_state()
    today_stats = state["daily"].setdefault(TODAY, {
        "processed": 0, "scored": 0, "passed": 0, "failed_quality": 0,
        "duplicates": 0, "score_distribution": {str(i): 0 for i in range(1, 11)},
        "by_vertical": {},
    })

    seen_phones: set = set()
    seen_names: list = []
    result_rows = []
    dup_count = 0

    for i, row in enumerate(rows):
        phone = row.get("phone", "")
        company = row.get("companyName", "")

        # In-batch dedup first (free, no API call)
        is_dup, reason = check_duplicate_in_batch(phone, company, seen_phones, seen_names)

        if not is_dup:
            # GHL API dedup
            is_dup, reason = check_duplicate_against_ghl(phone, company)

        row["is_duplicate"] = "true" if is_dup else "false"
        row["skip_reason"] = reason if is_dup else ""
        row["quality_score"] = row.get("quality_score", "")

        if is_dup:
            dup_count += 1
            log.info(f"  [DUP] {company} | {phone} — {reason}")
        else:
            # Register in seen sets
            norm = normalize_phone(phone)
            if norm:
                seen_phones.add(norm)
            if company and company.strip():
                seen_names.append(company.strip().lower())

        result_rows.append(row)
        today_stats["processed"] += 1

        if (i + 1) % 25 == 0:
            log.info(f"  Progress: {i+1}/{len(rows)} checked, {dup_count} duplicates so far")

    today_stats["duplicates"] += dup_count
    state["total_processed"] += len(rows)
    state["total_duplicates_caught"] += dup_count
    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    out_path = os.path.join(OPS_DIR, f"scored-leads-{TODAY}.csv")
    write_csv(out_path, result_rows)

    log.info(f"[DEDUP] Done. {len(rows)} checked, {dup_count} duplicates caught. Output: {out_path}")
    ntfy(
        NTFY_ACTIVITY,
        "Dedup Complete",
        f"{len(rows)} leads checked. {dup_count} duplicates removed.\nOutput: {out_path}",
    )


def cmd_process(csv_path: str) -> None:
    """
    Full pipeline:
      1. Dedup against GHL + batch
      2. Score quality (1-10)
      3. Filter: keep only score >= 5 and not duplicate
      4. Write clean output CSV
    """
    log.info(f"[PROCESS] Starting full pipeline for {csv_path}")
    rows = read_csv(csv_path)
    log.info(f"[PROCESS] {len(rows)} leads loaded")

    state = load_state()
    today_stats = state["daily"].setdefault(TODAY, {
        "processed": 0, "scored": 0, "passed": 0, "failed_quality": 0,
        "duplicates": 0, "score_distribution": {str(i): 0 for i in range(1, 11)},
        "by_vertical": {},
    })

    seen_phones: set = set()
    seen_names: list = []
    result_rows = []
    clean_rows = []  # Only the ones that pass
    dup_count = 0
    low_quality_count = 0

    for i, row in enumerate(rows):
        phone = row.get("phone", "")
        company = row.get("companyName", "")

        # Step 1: Dedup
        is_dup, dup_reason = check_duplicate_in_batch(phone, company, seen_phones, seen_names)
        if not is_dup:
            is_dup, dup_reason = check_duplicate_against_ghl(phone, company)

        # Step 2: Score
        q, score_reasons = score_lead(row)

        # Step 3: Determine skip reason
        skip_reason = ""
        if is_dup:
            skip_reason = dup_reason
            dup_count += 1
        elif q < MIN_QUALITY_SCORE:
            skip_reason = f"quality_score={q} (min {MIN_QUALITY_SCORE})"
            low_quality_count += 1

        row["quality_score"] = q
        row["is_duplicate"] = "true" if is_dup else "false"
        row["skip_reason"] = skip_reason
        row["_score_reasons"] = " | ".join(score_reasons)

        # Update seen sets (even duplicates — to catch the first occurrence correctly)
        if not is_dup:
            norm = normalize_phone(phone)
            if norm:
                seen_phones.add(norm)
            if company and company.strip():
                seen_names.append(company.strip().lower())

        today_stats["processed"] += 1
        today_stats["scored"] += 1
        today_stats["score_distribution"][str(q)] = today_stats["score_distribution"].get(str(q), 0) + 1

        vertical = (row.get("industry") or "unknown").lower()
        today_stats["by_vertical"][vertical] = today_stats["by_vertical"].get(vertical, 0) + 1

        result_rows.append(row)

        if not skip_reason:
            today_stats["passed"] += 1
            clean_rows.append(row)
        else:
            today_stats["failed_quality"] += 1

        if (i + 1) % 25 == 0:
            log.info(
                f"  Progress: {i+1}/{len(rows)} | dups={dup_count} | "
                f"low_quality={low_quality_count} | clean={len(clean_rows)}"
            )

    today_stats["duplicates"] += dup_count

    state["total_processed"] += len(rows)
    state["total_scored"] += len(rows)
    state["total_passed"] += len(clean_rows)
    state["total_duplicates_caught"] += dup_count
    state["total_failed_quality"] += low_quality_count
    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    # Write full scored CSV (all rows including filtered)
    full_out = os.path.join(OPS_DIR, f"scored-leads-{TODAY}.csv")
    write_csv(full_out, result_rows)

    # Write clean CSV (blast-ready)
    clean_out = os.path.join(OPS_DIR, f"clean-leads-{TODAY}.csv")
    write_csv(clean_out, clean_rows)

    # Update report
    report = load_report()
    report["days"][TODAY] = {
        "total_input": len(rows),
        "duplicates_caught": dup_count,
        "low_quality_removed": low_quality_count,
        "clean_leads": len(clean_rows),
        "pass_rate": f"{(len(clean_rows)/len(rows)*100):.1f}%" if rows else "0%",
        "score_distribution": today_stats["score_distribution"],
        "by_vertical": today_stats["by_vertical"],
        "source_file": csv_path,
        "generated_at": datetime.now().isoformat(),
    }
    save_report(report)

    log.info(
        f"[PROCESS] Complete. In={len(rows)} | Dups={dup_count} | "
        f"LowQuality={low_quality_count} | Clean={len(clean_rows)}"
    )
    log.info(f"  Full output:  {full_out}")
    log.info(f"  Clean output: {clean_out}")

    ntfy(
        NTFY_ACTIVITY,
        "Lead Pipeline Complete",
        (
            f"Input: {len(rows)} leads\n"
            f"Duplicates removed: {dup_count}\n"
            f"Low quality removed: {low_quality_count}\n"
            f"Clean leads ready: {len(clean_rows)}\n"
            f"Pass rate: {(len(clean_rows)/len(rows)*100):.1f}%\n"
            f"File: {clean_out}"
        ),
    )


def cmd_audit() -> None:
    """
    Audit all GHL contacts for internal duplicates.
    Reports contacts that share a phone number or have fuzzy-matching names.
    Does NOT delete anything — Wallace reviews first.
    """
    log.info("[AUDIT] Fetching all GHL contacts...")
    contacts = ghl_list_all_contacts()
    log.info(f"[AUDIT] {len(contacts)} contacts fetched. Scanning for duplicates...")

    # Build index by phone
    phone_index: dict[str, list] = {}
    name_list: list[tuple[str, dict]] = []

    for c in contacts:
        norm = normalize_phone(c.get("phone", ""))
        if norm:
            phone_index.setdefault(norm, []).append(c)
        company = (c.get("companyName") or c.get("name") or "").strip()
        if company:
            name_list.append((company.lower(), c))

    # Phone duplicates
    phone_dups = {phone: cs for phone, cs in phone_index.items() if len(cs) > 1}

    # Fuzzy name duplicates (O(n^2) but GHL contacts lists are small enough)
    name_dups = []
    checked = set()
    for i, (name_a, contact_a) in enumerate(name_list):
        for j, (name_b, contact_b) in enumerate(name_list):
            if j <= i:
                continue
            key = tuple(sorted([contact_a.get("id", ""), contact_b.get("id", "")]))
            if key in checked:
                continue
            checked.add(key)
            ratio = fuzzy_ratio(name_a, name_b)
            if ratio >= FUZZY_NAME_THRESHOLD:
                name_dups.append({
                    "ratio": f"{ratio:.0%}",
                    "a": f"{name_list[i][1].get('companyName','')} (ID: {name_list[i][1].get('id','')})",
                    "b": f"{name_list[j][1].get('companyName','')} (ID: {name_list[j][1].get('id','')})",
                })

    # Print report
    print("\n" + "=" * 60)
    print("GHL CONTACT AUDIT REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Total contacts scanned: {len(contacts)}")
    print("=" * 60)

    print(f"\nPHONE DUPLICATES: {len(phone_dups)} groups")
    for phone, cs in phone_dups.items():
        print(f"  +1{phone}:")
        for c in cs:
            print(f"    - {c.get('companyName') or c.get('name','?')} | ID: {c.get('id','?')} | Email: {c.get('email','?')}")

    print(f"\nNAME FUZZY DUPLICATES: {len(name_dups)} pairs")
    for nd in name_dups:
        print(f"  [{nd['ratio']}] {nd['a']}")
        print(f"           {nd['b']}")

    print("\nNOTE: No contacts were deleted. Review manually before removing.\n")

    # ntfy summary
    ntfy(
        NTFY_SYSTEM,
        "GHL Audit Complete",
        (
            f"Scanned {len(contacts)} GHL contacts.\n"
            f"Phone duplicate groups: {len(phone_dups)}\n"
            f"Fuzzy name duplicate pairs: {len(name_dups)}\n"
            "Check terminal for full report."
        ),
        priority="default",
    )


def cmd_report() -> None:
    """Print daily scraper performance report from state and report files."""
    state = load_state()
    report = load_report()

    print("\n" + "=" * 60)
    print("SCRAPER PERFORMANCE REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # All-time totals
    print("\nALL-TIME TOTALS:")
    print(f"  Total leads processed:    {state.get('total_processed', 0):,}")
    print(f"  Total scored:             {state.get('total_scored', 0):,}")
    print(f"  Total passed (score 5+):  {state.get('total_passed', 0):,}")
    print(f"  Total failed quality:     {state.get('total_failed_quality', 0):,}")
    print(f"  Total duplicates caught:  {state.get('total_duplicates_caught', 0):,}")
    print(f"  Last run:                 {state.get('last_run', 'never')}")

    # Per-day breakdown
    days = report.get("days", {})
    if days:
        print(f"\nDAILY BREAKDOWN ({len(days)} days recorded):")
        for day in sorted(days.keys(), reverse=True)[:7]:  # Last 7 days
            d = days[day]
            print(f"\n  {day}:")
            print(f"    Input:      {d.get('total_input', 0):,}")
            print(f"    Dups:       {d.get('duplicates_caught', 0):,}")
            print(f"    Low quality:{d.get('low_quality_removed', 0):,}")
            print(f"    Clean:      {d.get('clean_leads', 0):,}")
            print(f"    Pass rate:  {d.get('pass_rate', '?')}")
            dist = d.get("score_distribution", {})
            if dist:
                print("    Score dist: ", end="")
                dist_parts = [f"{k}:{v}" for k, v in sorted(dist.items()) if v > 0]
                print(" | ".join(dist_parts))
            by_v = d.get("by_vertical", {})
            if by_v:
                print("    By vertical:", end="")
                v_parts = [f"{k}:{v}" for k, v in sorted(by_v.items(), key=lambda x: -x[1])[:5]]
                print("  ".join(v_parts))

    # Today's state
    today = state.get("daily", {}).get(TODAY, {})
    if today:
        print(f"\nTODAY ({TODAY}):")
        print(f"  Processed:       {today.get('processed', 0)}")
        print(f"  Scored:          {today.get('scored', 0)}")
        print(f"  Passed (5+):     {today.get('passed', 0)}")
        print(f"  Failed quality:  {today.get('failed_quality', 0)}")
        print(f"  Duplicates:      {today.get('duplicates', 0)}")
        dist = today.get("score_distribution", {})
        if any(v > 0 for v in dist.values()):
            print("  Score dist:")
            for score in sorted(dist.keys(), key=int):
                count = dist[score]
                bar = "#" * count if count <= 40 else "#" * 40 + f"…+{count-40}"
                print(f"    {score:>2}: {bar} ({count})")
    else:
        print(f"\nNo runs logged for today ({TODAY}) yet.")

    print()


def cmd_status() -> None:
    """Quick status from state file."""
    state = load_state()

    print("\n" + "=" * 50)
    print("LEAD QUALITY ENGINE — STATUS")
    print("=" * 50)
    print(f"  Last run:          {state.get('last_run', 'never')}")
    print(f"  Total processed:   {state.get('total_processed', 0):,}")
    print(f"  Total passed:      {state.get('total_passed', 0):,}")
    print(f"  Dups caught:       {state.get('total_duplicates_caught', 0):,}")
    print(f"  Low quality:       {state.get('total_failed_quality', 0):,}")

    today = state.get("daily", {}).get(TODAY, {})
    if today:
        print(f"\n  Today ({TODAY}):")
        print(f"    Processed:  {today.get('processed', 0)}")
        print(f"    Passed:     {today.get('passed', 0)}")
        print(f"    Dups:       {today.get('duplicates', 0)}")
    else:
        print(f"\n  No activity today ({TODAY})")

    print(f"\n  State:  {STATE_FILE}")
    print(f"  Report: {REPORT_FILE}")
    print(f"  Log:    {LOG_FILE}")
    print()

# ─── Main ────────────────────────────────────────────────────────────────────

USAGE = """
Lead Quality Engine — The Call Taker
=====================================
Usage:
  python3 lead-quality-engine.py score <csv>    Score all leads, output scored CSV
  python3 lead-quality-engine.py dedup <csv>    Dedup CSV against GHL contacts
  python3 lead-quality-engine.py process <csv>  Full pipeline: dedup + score + filter (5+)
  python3 lead-quality-engine.py audit          Audit GHL contacts for internal duplicates
  python3 lead-quality-engine.py report         Show daily scraper performance report
  python3 lead-quality-engine.py status         Show engine stats

Quality Scoring:
  +3  Has valid email
  +2  Has owner first name
  +1  Has website URL
  +2  Has Google reviews data
  +2  Business established 2+ years (inferred)
  --
  Min score to pass blast engines: 5
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "score":
        if len(sys.argv) < 3:
            print("Usage: lead-quality-engine.py score <csv_path>")
            sys.exit(1)
        csv_path = sys.argv[2]
        if not os.path.exists(csv_path):
            log.error(f"File not found: {csv_path}")
            sys.exit(1)
        cmd_score(csv_path)

    elif command == "dedup":
        if len(sys.argv) < 3:
            print("Usage: lead-quality-engine.py dedup <csv_path>")
            sys.exit(1)
        csv_path = sys.argv[2]
        if not os.path.exists(csv_path):
            log.error(f"File not found: {csv_path}")
            sys.exit(1)
        cmd_dedup(csv_path)

    elif command == "process":
        if len(sys.argv) < 3:
            print("Usage: lead-quality-engine.py process <csv_path>")
            sys.exit(1)
        csv_path = sys.argv[2]
        if not os.path.exists(csv_path):
            log.error(f"File not found: {csv_path}")
            sys.exit(1)
        cmd_process(csv_path)

    elif command == "audit":
        cmd_audit()

    elif command == "report":
        cmd_report()

    elif command == "status":
        cmd_status()

    else:
        print(f"Unknown command: {command}")
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
