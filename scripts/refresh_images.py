"""Refresh roster images: try a series of pages per artist, embed first 2 valid images."""
from __future__ import annotations

import argparse
from datetime import date

from .common import (
    DATA, extract_image_candidates, fetch_image, get, load_json, logger,
    polite_delay, save_json, setup_logging,
)

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


def refresh_one(slug: str, pages: list[str], target: int = 2) -> list[dict]:
    """Try each page in order, embed the first `target` quality images."""
    embedded: list[dict] = []
    for page in pages:
        if len(embedded) >= target:
            break
        logger.info("scrape %s", page)
        r = get(page)
        if not r:
            continue
        for img_url in extract_image_candidates(r.text, page):
            if len(embedded) >= target:
                break
            logger.info("  try %s", img_url[:90])
            res = fetch_image(img_url)
            if not res:
                continue
            uri, kb = res
            embedded.append({
                "data_uri": uri,
                "source_url": img_url,
                "source_page": page,
                "kb": kb,
            })
            logger.info("  ok (%dKB)", kb)
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

    targets = [a for a in artists if not args.only or a["slug"] in args.only]

    report = {"refreshed": [], "kept": [], "missed": []}
    for a in targets:
        slug = a["slug"]
        pages = PAGES_BY_SLUG.get(slug, [])
        if not pages:
            logger.warning("no pages configured for %s", slug)
            continue
        cached = cache.get(slug, {}).get("images", [])
        if cached and len(cached) >= 2 and not args.force:
            logger.info("=== %s (cached %d) ===", a["name"], len(cached))
            report["kept"].append(slug)
            continue

        logger.info("=== %s ===", a["name"])
        images = refresh_one(slug, pages)
        if images:
            cache[slug] = {"name": a["name"], "images": images, "refreshed": str(date.today())}
            save_json(DATA / "artist_images.json", cache)
            report["refreshed"].append({"slug": slug, "count": len(images)})
        else:
            report["missed"].append(slug)

    logger.info("[done] refreshed=%d kept=%d missed=%d",
                len(report["refreshed"]), len(report["kept"]), len(report["missed"]))
    save_json(DATA / "_refresh_report.json", report)
    return report


if __name__ == "__main__":
    main()
