#!/usr/bin/env python3
"""Regression guard for the public site's Higgsfield-only technology visuals."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse


WEBSITE = Path(__file__).resolve().parents[1]
INDEX = WEBSITE / "index.html"
MANIFEST = WEBSITE / "assets" / "higgsfield" / "approved-assets.json"
SHARED_LOADER = WEBSITE / "higgsfield-media.js"
BANNED_PUBLIC_ASSETS = (
    "hero-phone.jpeg",
    "gideon-service-homepage-hero.png",
    "gideon-service-homepage-hero.webp",
    "gideon-service-mobile-hero.png",
    "gideon-service-mobile-hero.webp",
    "gideon-hologram.png",
    "gideon-hologram.webp",
    "jessica-hologram-clean.png",
    "jessica-hologram.jpg",
    "hvac-hero.jpeg",
    "hvac-hero.jpg",
    "og-image.png",
    "ai-vs-answering-service-og.png",
    "hvac-missed-calls-og.png",
    "plumbers-ai-answering-og.png",
    "og-default.png",
)
MEDIA_REFERENCE = re.compile(
    r'''(?:src|srcset|poster|content|href)\s*=\s*["']([^"']+\.(?:png|jpe?g|webp|gif|svg|mp4|webm)(?:\?[^"']*)?)["']''',
    re.I,
)
ASSET_REFERENCE = re.compile(
    r'''(?:https://thecalltaker\.com)?(/assets/[^"'()\s]+\.(?:png|jpe?g|webp|gif|svg|mp4|webm)(?:\?[^"'()\s]*)?)''',
    re.I,
)


def main() -> int:
    index = INDEX.read_text(encoding="utf-8")
    loader = SHARED_LOADER.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = manifest.get("assets", [])
    asset_ids = {asset.get("asset_id") for asset in assets}
    assert None not in asset_ids, "every manifest asset needs an asset_id"
    assert len(asset_ids) == len(assets), "manifest asset ids must be unique"
    manifest_sources = {asset.get("website_src") for asset in assets}
    assert None not in manifest_sources, "every manifest asset needs a website_src"
    assert len(manifest_sources) == len(assets), "manifest website sources must be unique"
    for asset in assets:
        assert asset.get("origin") == "higgsfield", f"asset origin is not Higgsfield: {asset.get('asset_id')}"
        assert asset.get("approval_status") == "approved", f"asset is not approved: {asset.get('asset_id')}"
        assert asset.get("qa_status") == "pass", f"asset did not pass QA: {asset.get('asset_id')}"
        assert re.fullmatch(r"[a-f0-9]{64}", asset.get("sha256", ""), re.I), f"invalid asset hash: {asset.get('asset_id')}"
        assert re.fullmatch(
            r"/assets/higgsfield/published/[a-z0-9._-]+\.(mp4|webm|jpg|jpeg|png|webp)",
            asset["website_src"],
            re.I,
        ), f"asset source is outside the approved website directory: {asset.get('asset_id')}"

    public_html = tuple(WEBSITE.rglob("*.html"))
    non_higgsfield_media = []
    for path in public_html:
        text = path.read_text(encoding="utf-8")
        for asset in BANNED_PUBLIC_ASSETS:
            assert asset not in text, f"public HTML still references non-Higgsfield visual: {path}: {asset}"
        for media_url in MEDIA_REFERENCE.findall(text):
            basename = media_url.split("?", 1)[0].rsplit("/", 1)[-1]
            is_brand_icon = basename.startswith("favicon") or basename == "apple-touch-icon.png"
            media_path = urlparse(media_url).path
            is_higgsfield = media_path.startswith("/assets/higgsfield/published/") and media_path in manifest_sources
            if not is_brand_icon and not is_higgsfield:
                non_higgsfield_media.append((path, media_url))
        for media_url in ASSET_REFERENCE.findall(text):
            media_path = urlparse(media_url).path
            if not (media_path.startswith("/assets/higgsfield/published/") and media_path in manifest_sources):
                non_higgsfield_media.append((path, media_url))
        if "og:image:width" in text or "og:image:height" in text:
            assert 'property="og:image"' in text, f"orphaned social-image dimensions remain: {path}"
    assert not non_higgsfield_media, f"non-Higgsfield public media references remain: {non_higgsfield_media[:5]}"

    assert 'id="phone"' not in index, "deployed homepage still renders the fake phone UI"
    assert '<div class="phone-screen">' not in index, "fake phone screen remains visible"
    for legacy_phone_css in (
        "PHONE ANIMATION",
        ".phone-screen",
        ".phone-notch",
        ".screen-state",
        ".ring-btn",
        ".phone-readout",
    ):
        assert legacy_phone_css not in index, f"dormant fake-phone styling remains: {legacy_phone_css}"
    for legacy_tech_theater in ('ENTER THE VAULT', 'id="gHudFrame"', 'id="gDepthCanvas"', 'id="gFigure"'):
        assert legacy_tech_theater not in index, f"dormant fake technology theater remains: {legacy_tech_theater}"
    lower_index = index.lower()
    for legacy_tech_css in (
        "time vault",
        ".g-vault",
        "hologram",
        ".g-hud",
        ".g-depth",
        ".g-figure",
        ".g-projection",
        ".g-scanline",
        ".g-tap-gate",
    ):
        assert legacy_tech_css not in lower_index, f"dormant fake-technology styling remains: {legacy_tech_css}"

    slots = re.findall(r'<div class="higgsfield-media-slot"(?P<attrs>.*?)></div>', index, re.S)
    assert len(slots) == 3, f"expected 3 Higgsfield slots, found {len(slots)}"
    assert all(" hidden" in attrs for attrs in slots), "unbound slots must fail closed"
    for requirement in (
        "asset.origin === 'higgsfield'",
        "asset.approval_status === 'approved'",
        "asset.qa_status === 'pass'",
        "asset.sha256",
        "/assets/higgsfield/approved-assets.json",
        "assets\\/higgsfield\\/published",
    ):
        assert requirement in loader, f"loader missing proof gate: {requirement}"

    assert manifest["schema_version"] == "tct_higgsfield_website_asset_manifest.v1"
    assert isinstance(manifest["provider_actions_performed"], bool)
    if not assets:
        assert manifest["status"] == "fail_closed_no_approved_assets"
        assert manifest["provider_actions_performed"] is False
    manifest_slots = {item["slot_id"]: item for item in manifest["slots"]}
    assert set(manifest_slots) == {
        "homepage-service-hero",
        "callback-window-story",
        "one-minute-explainer",
        "site-social-preview",
        "ai-receptionist-hero",
        "paid-landing-hero",
        "pricing-plan-story",
    }
    for slot_id, item in manifest_slots.items():
        asset_id = item["asset_id"]
        if asset_id is None:
            assert item["status"] == "awaiting_approved_higgsfield_asset"
            continue
        assert asset_id in asset_ids, f"slot references unknown asset: {slot_id}: {asset_id}"
        asset = next(asset for asset in assets if asset["asset_id"] == asset_id)
        assert asset["capability_family"] == item["capability_family"], f"capability mismatch: {slot_id}"

    assert manifest["binding_requirements"]["origin"] == "higgsfield"
    assert manifest["binding_requirements"]["approval_status"] == "approved"
    assert manifest["binding_requirements"]["qa_status"] == "pass"

    expected_page_slots = {
        "index.html": {"homepage-service-hero", "callback-window-story", "one-minute-explainer"},
        "ai-receptionist/index.html": {"ai-receptionist-hero"},
        "paid.html": {"paid-landing-hero"},
        "pricing.html": {"pricing-plan-story"},
    }
    for page, expected_slots in expected_page_slots.items():
        text = (WEBSITE / page).read_text(encoding="utf-8")
        assert '<script src="/higgsfield-media.js" defer></script>' in text, f"shared loader missing: {page}"
        assert '<link rel="stylesheet" href="/higgsfield-media.css">' in text, f"shared media CSS missing: {page}"
        page_slots = set(re.findall(r'data-higgsfield-slot="([^"]+)"', text))
        assert page_slots == expected_slots, f"unexpected Higgsfield slots on {page}: {page_slots}"

    for backup in ("index-old-vault.html", "index-pre-conversion-backup.html"):
        text = (WEBSITE / backup).read_text(encoding="utf-8")
        assert '.gideon-hero{display:none!important}' in text
        assert '<meta name="robots" content="noindex,nofollow">' in text

    print({
        "status": "pass",
        "higgsfield_slots": len(slots),
        "public_higgsfield_slots": sum(len(item) for item in expected_page_slots.values()),
        "public_html_scanned": len(public_html),
        "non_higgsfield_media_references": len(non_higgsfield_media),
        "manifest_asset_count": len(assets),
        "fake_phone_ui_visible": False,
        "fake_phone_ui_css_present": False,
        "legacy_tech_theater_css_present": False,
        "provider_calls": False,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
