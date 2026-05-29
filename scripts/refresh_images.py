"""Refresh roster images: try a series of pages per artist, embed first 2 valid images.

Two stages per artist:
  1. If data/manual_artist_photos.json has 2+ URLs for this slug, fetch
     those directly (skipping the auto-crawl). Used for artists with
     unreachable primaryUrls.
  2. Otherwise walk the configured PAGES_BY_SLUG list, using
     common.fetch_thumbs with follow_links=True (multi-page crawl) so
     each page contributes unique thumbs. URL + content dedup catches
     the same image being served from og:image and a body <img> tag.
"""
from __future__ import annotations

import argparse
from datetime import date

from .common import (
    DATA, fetch_image, fetch_thumbs, get, load_json, logger,
    polite_delay, save_json, setup_logging,
)

MANUAL_PHOTOS_PATH = "manual_artist_photos.json"

# Per-artist scrape pages. For each canonical roster artist,
# try these in order. Built from the Field Brief 014 source notes.
PAGES_BY_SLUG: dict[str, list[str]] = {
    "valenzuela": [
        "http://www.bryanvalenzuela.com/murals",
        "http://www.bryanvalenzuela.com/the-manycolored-threads-that-weave-the-collective-dream",
        "https://www.wideopenwalls.com/artists/bryan-valenzuela",
        "https://kevinbarry.com/artist/bryan-valenzuela/",
    ],
    "conrad": [
        "https://www.marenconrad.com/marrs",
        "https://www.marenconrad.com/murals",
        "https://www.marenconrad.com",
    ],
    "lc_studio": [
        "https://www.studio-tutto.com/portfolio",
        "https://www.studio-tutto.com",
        "https://www.studio-tutto.com/murals",
    ],
    "delgado": [
        "https://artbyraphael.com/murals",
        "https://artbyraphael.com",
        "https://artbyraphael.com/portfolio",
    ],
    "garibaldi": [
        "https://garibaldiarts.com/gallery",
        "https://garibaldiarts.com",
    ],
    "king": [
        "https://www.jayasart.com/muralsbyjaya",
        "https://www.jayasart.com",
    ],
    "grigio": [
        "https://www.grigioart.com/portfolio",
        "https://www.grigioart.com",
    ],
    "di_gregorio": [
        "https://www.josedigregorio.com/work",
        "https://www.josedigregorio.com",
    ],
    "crandall_bear": [
        "http://www.micahcrandallbear.com/paintings",
        "http://www.micahcrandallbear.com",
    ],
    "hart": [
        "https://galehart.com/sculpture",
        "https://galehart.com",
    ],
    "taylor": [
        "https://stephanietaylorart.com/portfolio/sacramento/",
        "https://stephanietaylorart.com/portfolio",
    ],
    "gamez": [
        "https://brandedarts.com/art/franceska-gamez/",
        "https://franceskagamez.com",
    ],
    "burner": [
        "https://brandedarts.com/art/shaun-burner/",
        "https://www.wideopenwalls.com/artists/shaun-burner",
    ],
    "kille": [
        "https://www.groundswellart.com/groundswell-gallery-at-fort-sutter-hotel-jeremiah-kille",
        "https://www.groundswellart.com/jeremiah-kille",
    ],
    "padilla": [
        "http://www.kinetikideas.com/portfolio",
        "http://www.kinetikideas.com",
    ],
    "huerta": [
        "https://viva-frida.com/gallery",
        "https://viva-frida.com",
    ],
    "horner": [
        "https://brandedarts.com/portfolio_page/waylon-horner/",
        "https://www.wideopenwalls.com/artists/waylon-horner",
    ],
    "skinner": [
        "https://www.theartofskinner.com/murals",
        "https://www.theartofskinner.com/paintings",
    ],
    "groundswell": [
        "https://www.groundswellart.com/eleanor",
        "https://www.groundswellart.com/projects",
    ],
    "wow": [
        "https://www.wideopenwalls.com/about",
        "https://www.wideopenwalls.com",
    ],
    "ninedot": [
        "https://ninedotarts.com/projects",
        "https://ninedotarts.com",
    ],
}


def _fetch_manual_photos(slug: str, urls: list[str], target: int = 2) -> list[dict]:
    """Fetch + embed each URL listed under this slug in manual_artist_photos.
    Returns up to `target` successfully-fetched image dicts. No dedup needed
    — the user curated the list."""
    out: list[dict] = []
    for u in urls:
        if len(out) >= target:
            break
        logger.info("  manual: %s", u[:90])
        res = fetch_image(u)
        if not res:
            logger.info("    fetch failed")
            continue
        uri, kb = res
        out.append({"data_uri": uri, "source_url": u, "source_page": "manual",
                    "kb": kb, "label": "primary" if not out else "secondary"})
        logger.info("    ok (%dKB)", kb)
        polite_delay(0.2)
    return out


def refresh_one(slug: str, pages: list[str], target: int = 2) -> list[dict]:
    """Walk the configured pages, gathering up to `target` *unique* thumbs.

    Uses common.fetch_thumbs with follow_links=True so each page contributes
    new images via sub-page crawling, while URL + content dedup catches the
    same image being served from multiple paths (the bug that put the same
    image at both [0] and [1] for 6 directory artists).
    """
    embedded: list[dict] = []
    for page in pages:
        if len(embedded) >= target:
            break
        logger.info("scrape %s", page)
        r = get(page)
        if not r:
            continue
        fresh = fetch_thumbs(
            r, page, want=target - len(embedded),
            existing=embedded, follow_links=True, max_subpages=3,
        )
        for t in fresh:
            t["source_page"] = page
        embedded.extend(fresh)
        polite_delay()
    return embedded


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--only", nargs="*", help="restrict to specific slugs")
    p.add_argument("--force", action="store_true", help="ignore cache and refetch")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()

    setup_logging(args.log)

    artists = load_json(DATA / "artists.json", []) or []
    cache = load_json(DATA / "artist_images.json", {}) or {}
    manual = (load_json(DATA / MANUAL_PHOTOS_PATH, {}) or {}).get("by_slug", {})

    targets = [a for a in artists if not args.only or a["slug"] in args.only]

    report = {"refreshed": [], "kept": [], "missed": [], "manual": []}
    for a in targets:
        slug = a["slug"]
        cached = cache.get(slug, {}).get("images", [])
        # Determine whether existing cache is good enough to skip
        has_2_unique = (
            len(cached) >= 2
            and len({c.get("data_uri", "")[:200] for c in cached}) >= 2
        )
        if has_2_unique and not args.force:
            logger.info("=== %s (cached %d unique) ===", a["name"], len(cached))
            report["kept"].append(slug)
            continue

        logger.info("=== %s ===", a["name"])

        # Stage 1: manual override
        manual_urls = manual.get(slug) or []
        images: list[dict] = []
        if len(manual_urls) >= 2:
            images = _fetch_manual_photos(slug, manual_urls, target=2)
            if len(images) >= 2:
                report["manual"].append(slug)

        # Stage 2: configured pages auto-crawl (if manual didn't yield 2)
        if len(images) < 2:
            pages = PAGES_BY_SLUG.get(slug, [])
            if pages:
                images.extend(refresh_one(slug, pages, target=2 - len(images)))
            elif not manual_urls:
                logger.warning("no pages or manual URLs configured for %s", slug)

        if images:
            cache[slug] = {"name": a["name"], "images": images, "refreshed": str(date.today())}
            save_json(DATA / "artist_images.json", cache)
            report["refreshed"].append({"slug": slug, "count": len(images)})
        else:
            report["missed"].append(slug)

    logger.info("[done] refreshed=%d kept=%d missed=%d manual=%d",
                len(report["refreshed"]), len(report["kept"]),
                len(report["missed"]), len(report["manual"]))
    save_json(DATA / "_refresh_report.json", report)
    return report


if __name__ == "__main__":
    main()
