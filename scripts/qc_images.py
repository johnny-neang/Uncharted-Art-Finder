"""QC pass: guarantee every discovery candidate has a thumbnail.

Two-stage fallback:
  1. Refetch the candidate URL and try og:image + body images (same logic
     ingest_seeds uses for new seeds). Captures cases where the source page
     gained an image since first ingest, or where earlier runs predated the
     body-image fallback.
  2. For any candidate still without an image, render a deterministic SVG
     initials avatar (Gmail/Slack-style) so dashboard cards never go empty.

Runs in the orchestrator after discovery + scoring but before
build_dashboard, so the rendered HTML always has visuals.
"""
from __future__ import annotations

import argparse
import base64
import hashlib

from .common import (
    DATA, extract_image_candidates, extract_og_meta, fetch_image, get,
    load_json, logger, polite_delay, save_json, setup_logging,
)


# Curated palette — muted, gallery-friendly, all paired with cream text.
# Deterministic pick via slug hash so a given candidate's avatar is stable
# across runs (won't churn).
_PALETTE = (
    "#A8543A",  # terracotta
    "#5C7A55",  # sage
    "#6B4A6B",  # plum
    "#3A4A6B",  # navy
    "#A88A3A",  # mustard
    "#3A6B6B",  # teal
    "#7A3A3A",  # burgundy
    "#54585C",  # slate
    "#8A5A3A",  # umber
    "#3A6B4A",  # forest
    "#6B3A5C",  # mulberry
    "#5C5C3A",  # olive
)
_TEXT_FILL = "#FAF6F1"  # cream


def _initials(name: str) -> str:
    """Take the first letter of the first word and last word.

    "Rossi Sculpture Design" -> "RD"
    "Atlas Lab"              -> "AL"
    "Madonna"                -> "M"
    """
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:1].upper()
    return (parts[0][:1] + parts[-1][:1]).upper()


def _palette_color(seed: str) -> str:
    """Deterministically pick a palette color from a slug-like seed."""
    h = int(hashlib.sha1(seed.encode("utf-8")).hexdigest(), 16)
    return _PALETTE[h % len(_PALETTE)]


def initials_avatar(name: str, seed: str) -> dict:
    """Render a 480x480 SVG initials avatar and return it in the same shape
    as a fetched image (data_uri, source_url, kb, placeholder)."""
    initials = _initials(name)
    color = _palette_color(seed)
    # Smaller font for two-character initials so they fit comfortably
    font_size = 220 if len(initials) <= 1 else 200
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 480" width="480" height="480">'
        f'<rect width="480" height="480" fill="{color}"/>'
        f'<text x="240" y="240" text-anchor="middle" dominant-baseline="central" '
        f'font-family="\'DM Serif Display\', Georgia, serif" font-size="{font_size}" '
        f'font-weight="400" fill="{_TEXT_FILL}">{initials}</text>'
        f'</svg>'
    )
    raw = svg.encode("utf-8")
    data_uri = "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
    return {
        "data_uri": data_uri,
        "source_url": "generated:initials",
        "kb": len(raw) // 1024,
        "placeholder": True,
    }


def try_refetch(candidate: dict) -> dict | None:
    """Refetch the candidate URL and try og:image then body images.
    Returns an image dict (real, not placeholder) or None on failure."""
    url = candidate.get("url")
    if not url:
        return None
    r = get(url)
    if not r:
        return None
    og = extract_og_meta(r.text, url)
    if og.get("og_image"):
        res = fetch_image(og["og_image"])
        if res:
            uri, kb = res
            return {"data_uri": uri, "source_url": og["og_image"], "kb": kb}
    for img_url in extract_image_candidates(r.text, url, max_count=6):
        res = fetch_image(img_url)
        if res:
            uri, kb = res
            return {"data_uri": uri, "source_url": img_url, "kb": kb}
        polite_delay(0.2)
    return None


def needs_image(candidate: dict) -> bool:
    """True if the candidate has no image, or only a placeholder."""
    img = candidate.get("image")
    if not img:
        return True
    # If it's already a placeholder, leave it — we tried refetch on a prior
    # QC pass and it didn't work. Re-trying every run wastes network calls.
    # Operators can wipe the placeholder manually to force a retry.
    return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--no-refetch", action="store_true",
                   help="skip the network refetch step (initials only)")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    discoveries = load_json(DATA / "discoveries.json", {"candidates": []})
    candidates = discoveries.get("candidates", [])
    if not candidates:
        logger.info("[qc] no candidates")
        return

    refetched = 0
    initialed = 0
    skipped_placeholder = 0
    for c in candidates:
        img = c.get("image")
        if img and not img.get("placeholder"):
            continue  # has a real image, leave alone
        if img and img.get("placeholder"):
            skipped_placeholder += 1
            continue  # already gave it an initials fallback, don't churn

        # Stage 1: try a fresh fetch
        if not args.no_refetch:
            res = try_refetch(c)
            if res:
                c["image"] = res
                refetched += 1
                logger.info("[qc-refetched] %s (%dKB)", c["name"], res["kb"])
                continue

        # Stage 2: SVG initials avatar
        c["image"] = initials_avatar(c["name"], c.get("slug", c["name"]))
        initialed += 1
        logger.info("[qc-initials] %s", c["name"])

    save_json(DATA / "discoveries.json", discoveries)
    total_with_image = sum(1 for c in candidates if c.get("image"))
    logger.info("[qc-done] refetched=%d initials=%d skipped=%d  coverage=%d/%d",
                refetched, initialed, skipped_placeholder, total_with_image, len(candidates))


if __name__ == "__main__":
    main()
