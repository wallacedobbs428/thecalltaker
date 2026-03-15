"""
LOCAL vs NATIONAL LEAD DETECTION — The Call Taker
=================================================
Determines if a lead is local to Middle Tennessee (within ~1 hour of Brentwood, TN)
based on area code, zip code, or city name.

Usage:
    from local_detect import is_local, get_lead_city

    if is_local(contact):
        # Use in-person appointment CTA
    else:
        # Use Zoom demo / free pilot CTA
"""

# Nashville-area / Middle TN area codes
LOCAL_AREA_CODES = {"615", "629"}

# Middle TN zip code prefixes (370xx - 381xx covers Nashville metro + surrounding)
LOCAL_ZIP_PREFIXES = {
    "370", "371", "372", "373", "374", "375", "376", "377", "378", "379",
    "380", "381",
}

# Cities within ~1 hour of Brentwood, TN (lowercase for matching)
LOCAL_CITIES = {
    "brentwood", "nashville", "franklin", "murfreesboro", "hendersonville",
    "gallatin", "lebanon", "smyrna", "la vergne", "lavergne", "spring hill",
    "columbia", "dickson", "clarksville", "mount juliet", "mt juliet",
    "mt. juliet", "antioch", "hermitage", "donelson", "bellevue",
    "goodlettsville", "white house", "portland", "springfield",
    "shelbyville", "tullahoma", "manchester", "cookeville",
    "nolensville", "thompsons station", "thompson's station", "fairview",
    "pegram", "kingston springs", "white bluff", "ashland city",
    "greenbrier", "cross plains", "millersville", "old hickory",
    "madison", "berry hill", "oak hill", "forest hills", "belle meade",
    "green hills", "sylvan park", "east nashville", "germantown",
    "the nations", "12 south", "12south", "sobro", "gulch",
    "music row", "midtown", "west end", "hillsboro village",
}


def _extract_area_code(phone):
    """Extract 3-digit area code from a phone number string."""
    if not phone:
        return None
    digits = "".join(c for c in str(phone) if c.isdigit())
    # +1XXXXXXXXXX or 1XXXXXXXXXX
    if len(digits) == 11 and digits[0] == "1":
        return digits[1:4]
    # XXXXXXXXXX
    if len(digits) == 10:
        return digits[0:3]
    return None


def _extract_zip_prefix(zipcode):
    """Extract first 3 digits of a zip code."""
    if not zipcode:
        return None
    digits = "".join(c for c in str(zipcode) if c.isdigit())
    if len(digits) >= 3:
        return digits[:3]
    return None


def _normalize_city(city):
    """Normalize city name for matching."""
    if not city:
        return ""
    return city.lower().strip().replace("-", " ").replace(",", "").split(",")[0].strip()


def is_local(contact):
    """
    Determine if a GHL contact is local to Middle Tennessee.

    Checks (in order):
    1. Phone area code (615, 629)
    2. Zip code (370xx-381xx)
    3. City name match

    Args:
        contact: dict with GHL contact fields (phone, postalCode, city, address1City, etc.)

    Returns:
        bool: True if the contact is local to Middle TN
    """
    if not contact or not isinstance(contact, dict):
        return False

    # Check phone area code
    for phone_field in ("phone", "additionalPhones"):
        phone = contact.get(phone_field, "")
        if isinstance(phone, list):
            for p in phone:
                ac = _extract_area_code(p if isinstance(p, str) else str(p))
                if ac in LOCAL_AREA_CODES:
                    return True
        else:
            ac = _extract_area_code(phone)
            if ac in LOCAL_AREA_CODES:
                return True

    # Check zip code
    for zip_field in ("postalCode", "address1Zip", "zip"):
        zipcode = contact.get(zip_field, "")
        prefix = _extract_zip_prefix(zipcode)
        if prefix in LOCAL_ZIP_PREFIXES:
            return True

    # Check city name
    for city_field in ("city", "address1City", "locationCity"):
        city = _normalize_city(contact.get(city_field, ""))
        if city in LOCAL_CITIES:
            return True
        # Partial match for variations like "Nashville, TN"
        for local in LOCAL_CITIES:
            if local in city or city in local:
                return True

    # Check state + generic Nashville reference in tags
    tags = contact.get("tags", [])
    if isinstance(tags, list):
        for tag in tags:
            tag_lower = str(tag).lower()
            if tag_lower in ("nashville", "middle-tn", "local-lead", "local"):
                return True

    return False


def get_lead_city(contact):
    """Extract the best city name from a contact for personalization."""
    for field in ("city", "address1City", "locationCity"):
        city = contact.get(field, "")
        if city and isinstance(city, str) and city.strip():
            return city.strip()
    return ""


def is_local_by_phone(phone):
    """Quick check: is this phone number a Nashville-area code?"""
    ac = _extract_area_code(phone)
    return ac in LOCAL_AREA_CODES


def is_local_by_city(city):
    """Quick check: is this city in the local list?"""
    return _normalize_city(city) in LOCAL_CITIES
