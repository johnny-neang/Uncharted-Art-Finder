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


def initials_avatar(name: str, seed: str, variant: str = "primary") -> dict:
    """Render a 480x480 SVG initials avatar. Two visual variants:
      primary   — solid color background + cream initials
      secondary — cream background + palette-color outline + palette-color initials
                  (looks like a complementary mate when placed side by side)
    """
    initials = _initials(name)
    color = _palette_color(seed if variant == "primary" else seed + "_2")
    font_size = 220 if len(initials) <= 1 else 200
    if variant == "primary":
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 480" width="480" height="480">'
            f'<rect width="480" height="480" fill="{color}"/>'
            f'<text x="240" y="240" text-anchor="middle" dominant-baseline="central" '
            f'font-family="\'DM Serif Display\', Georgia, serif" font-size="{font_size}" '
            f'font-weight="400" fill="{_TEXT_FILL}">{initials}</text>'
            f'</svg>'
        )
    else:
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 480" width="480" height="480">'
            f'<rect width="480" height="480" fill="{_TEXT_FILL}"/>'
            f'<rect x="20" y="20" width="440" height="440" fill="none" stroke="{color}" stroke-width="4"/>'
            f'<text x="240" y="240" text-anchor="middle" dominant-baseline="central" '
            f'font-family="\'DM Serif Display\', Georgia, serif" font-size="{font_size}" '
            f'font-weight="400" fill="{color}">{initials}</text>'
            f'</svg>'
        )
    raw = svg.encode("utf-8")
    data_uri = "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
    return {
        "data_uri": data_uri,
        "source_url": f"generated:initials:{variant}",
        "kb": len(raw) // 1024,
        "placeholder": True,
        "label": variant,
    }


def try_refetch_thumbs(candidate: dict, want: int = 2) -> list[dict]:
    """Refetch the candidate URL and gather up to `want` real images.

    Walks og:image first, then body images, stopping after `want` successes.
    Returns a list of 0 to `want` image dicts (no placeholders here — the
    caller fills remaining slots with initials variants if needed).
    """
    url = candidate.get("url")
    if not url:
        return []
    r = get(url)
    if not r:
        return []
    out: list[dict] = []
    seen_sources: set[str] = set()

    def _try(img_url: str) -> None:
        if img_url in seen_sources:
            return
        seen_sources.add(img_url)
        res = fetch_image(img_url)
        if res:
            uri, kb = res
            out.append({"data_uri": uri, "source_url": img_url, "kb": kb, "label": "primary" if not out else "secondary"})

    og = extract_og_meta(r.text, url)
    if og.get("og_image"):
        _try(og["og_image"])
        if len(out) >= want:
            return out
    for img_url in extract_image_candidates(r.text, url, max_count=8):
        if len(out) >= want:
            break
        _try(img_url)
        polite_delay(0.2)
    return out


def candidate_thumbs(c: dict) -> list[dict]:
    """Read a candidate's `thumbs[]` if present, else fall back to wrapping
    the legacy single `image` field as a one-element list."""
    if c.get("thumbs"):
        return c["thumbs"]
    if c.get("image"):
        return [c["image"]]
    return []


def needs_image(candidate: dict) -> bool:
    """True if the candidate has fewer than 2 thumbs OR only placeholder thumbs.
    A real-image-then-placeholder pair still gets a refetch attempt for the
    placeholder slot, in case the page has a usable second image now."""
    thumbs = candidate_thumbs(candidate)
    if not thumbs:
        return True
    real = [t for t in thumbs if not t.get("placeholder")]
    if not real:
        # All placeholders — already tried, leave alone to avoid churn.
        return False
    if len(real) < 2:
        # Have one real, can try to find a second.
        return True
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

    refetched_thumbs_added = 0
    initials_added = 0
    skipped = 0
    for c in candidates:
        existing = candidate_thumbs(c)
        existing_real = [t for t in existing if not t.get("placeholder")]

        if not needs_image(c):
            skipped += 1
            continue

        # Stage 1: try to fetch up to 2 real images from the page
        new_thumbs: list[dict] = list(existing_real)  # keep what we already have
        if not args.no_refetch and len(new_thumbs) < 2:
            fresh = try_refetch_thumbs(c, want=2 - len(new_thumbs))
            for t in fresh:
                t["label"] = "primary" if not new_thumbs else "secondary"
                new_thumbs.append(t)
            if fresh:
                refetched_thumbs_added += len(fresh)
                logger.info("[qc-refetched] %s (+%d real thumb(s))", c["name"], len(fresh))

        # Stage 2: pad with initials variants until we have 2
        seed = c.get("slug", c["name"])
        while len(new_thumbs) < 2:
            variant = "primary" if not new_thumbs else "secondary"
            new_thumbs.append(initials_avatar(c["name"], seed, variant=variant))
            initials_added += 1

        c["thumbs"] = new_thumbs
        # Backward-compat: keep `image` pointing at the first real thumb
        # (or the primary placeholder if no real images exist).
        c["image"] = new_thumbs[0]

    save_json(DATA / "discoveries.json", discoveries)
    total_with_thumbs = sum(1 for c in candidates if c.get("thumbs"))
    logger.info("[qc-done] real_fetched=%d initials_filled=%d skipped=%d  coverage=%d/%d",
                refetched_thumbs_added, initials_added, skipped, total_with_thumbs, len(candidates))


if __name__ == "__main__":
    main()
