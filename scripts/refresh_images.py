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

from contextlib import nullcontext

from .common import (
    DATA, fetch_image, fetch_instagram_apify_backup, fetch_instagram_thumbs,
    fetch_thumbs, find_wayback_snapshot, get, load_json, logger, polite_delay,
    rendered_session, save_json, setup_logging,
)

MANUAL_PHOTOS_PATH = "manual_artist_photos.json"
INSTAGRAM_HANDLES_PATH = "instagram_handles.json"
APIFY_ATTEMPTS_PATH = "apify_attempts.json"

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


def refresh_one(slug: str, pages: list[str], target: int = 2, rf=None) -> list[dict]:
    """Walk the configured pages, gathering up to `target` *unique* thumbs.

    For each page: try direct HTTP. If it fails, fall back to Wayback
    Machine. Then fetch_thumbs follows internal links and (if `rf` is
    provided) re-renders via Playwright as a final fallback for lazy-loaded
    pages.
    """
    embedded: list[dict] = []
    for page in pages:
        if len(embedded) >= target:
            break
        logger.info("scrape %s", page)
        r = get(page)
        if not r:
            wayback = find_wayback_snapshot(page)
            if wayback:
                logger.info("  wayback %s", wayback[:90])
                r = get(wayback)
                if r:
                    page = wayback
        if not r:
            continue
        fresh = fetch_thumbs(
            r, page, want=target - len(embedded),
            existing=embedded, follow_links=True, max_subpages=3, rf=rf,
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
    p.add_argument("--apify-retry", action="store_true",
                   help="let the paid Apify backup re-attempt artists it has already "
                        "tried (default: each artist is tried at most once)")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()

    setup_logging(args.log)

    artists = load_json(DATA / "artists.json", []) or []
    cache = load_json(DATA / "artist_images.json", {}) or {}
    manual = (load_json(DATA / MANUAL_PHOTOS_PATH, {}) or {}).get("by_slug", {})
    ig_handles = (load_json(DATA / INSTAGRAM_HANDLES_PATH, {}) or {}).get("by_slug", {})
    # Ledger of slugs we've already spent a paid Apify call on, so the backup
    # fires at most once per artist. {"by_slug": {slug: "YYYY-MM-DD"}}.
    apify_attempts = (load_json(DATA / APIFY_ATTEMPTS_PATH, {}) or {}).get("by_slug", {})
    apify_attempts_dirty = False

    targets = [a for a in artists if not args.only or a["slug"] in args.only]

    # Open one Playwright session for all the lazy-load fallback fetches.
    # If Playwright isn't installed, rendered_session yields None and
    # fetch_thumbs silently skips the render fallback.
    needs_render = bool(targets)
    browser_ctx = rendered_session() if needs_render else nullcontext(None)

    with browser_ctx as rf:
        report = {"refreshed": [], "kept": [], "missed": [], "manual": [], "apify": []}
        for a in targets:
            slug = a["slug"]
            cached = cache.get(slug, {}).get("images", [])
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

            # Stage 2: Instagram, free tier only (Playwright render). The paid
            # Apify tier is deferred to Stage 4 so it never runs while a free
            # source below might still find the photo.
            ig_handle = ig_handles.get(slug)
            if ig_handle and len(images) < 2:
                images.extend(fetch_instagram_thumbs(
                    ig_handle, rf, want=2 - len(images), existing=images, allow_apify=False))

            # Stage 3: configured pages auto-crawl (with Playwright fallback).
            # Falls back to the artist's primaryUrl when no per-slug pages
            # are hand-configured — useful for promoted entries whose pages
            # haven't been added to PAGES_BY_SLUG yet.
            if len(images) < 2:
                pages = PAGES_BY_SLUG.get(slug, []) or ([a["primaryUrl"]] if a.get("primaryUrl") else [])
                if pages:
                    images.extend(refresh_one(slug, pages, target=2 - len(images), rf=rf))
                elif not manual_urls and not ig_handle:
                    logger.warning("no pages, manual URLs, or IG handle for %s", slug)

            # Stage 4: Apify IG scraper (paid) — true last resort, reached only
            # after every free source above came up short. Kept deliberately
            # sparing: it fires at most ONCE per artist (tracked in
            # data/apify_attempts.json) and never for an artist whose cache is
            # already complete — so it never re-runs on existing artists. Pass
            # --apify-retry to deliberately re-attempt stuck artists. No-ops
            # silently when the APIFY env var is unset.
            already_tried_apify = slug in apify_attempts
            if (ig_handle and len(images) < 2 and not has_2_unique
                    and (args.apify_retry or not already_tried_apify)):
                images.extend(fetch_instagram_apify_backup(
                    ig_handle, want=2 - len(images), existing=images))
                apify_attempts[slug] = str(date.today())  # record regardless of outcome
                apify_attempts_dirty = True
                report["apify"].append(slug)
            elif ig_handle and len(images) < 2 and already_tried_apify:
                logger.info("  apify: %s tried %s already — skipping paid retry "
                            "(use --apify-retry to force)", slug, apify_attempts.get(slug))

            if images:
                cache[slug] = {"name": a["name"], "images": images, "refreshed": str(date.today())}
                save_json(DATA / "artist_images.json", cache)
                report["refreshed"].append({"slug": slug, "count": len(images)})
            else:
                report["missed"].append(slug)

    if apify_attempts_dirty:
        save_json(DATA / APIFY_ATTEMPTS_PATH, {"by_slug": apify_attempts})

    logger.info("[done] refreshed=%d kept=%d missed=%d manual=%d apify_paid=%d",
                len(report["refreshed"]), len(report["kept"]),
                len(report["missed"]), len(report["manual"]), len(report["apify"]))
    if report["apify"]:
        logger.info("[apify] paid backup fired for: %s", ", ".join(report["apify"]))
    save_json(DATA / "_refresh_report.json", report)
    return report


if __name__ == "__main__":
    main()
