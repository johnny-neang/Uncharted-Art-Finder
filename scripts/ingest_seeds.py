"""Ingest manually-added artist URLs into the discoveries queue.

You find an interesting artist or studio on Instagram, Facebook, or anywhere
else the crawler can't reach. Drop the URL into `data/manual_seeds.json`:

    {
      "seeds": [
        {"url": "https://www.instagram.com/some_artist/", "note": "spotted on IG"}
      ]
    }

On the next `/refresh`, this step:
  1. Fetches each pending seed URL.
  2. Extracts OG meta tags (og:title, og:description, og:image) — these work
     on Instagram and Facebook without auth, because the platforms serve them
     to crawlers even behind login walls.
  3. Creates a discoveries.json candidate so Claude scores it like any other.
  4. Marks the seed processed (or failed with a reason).

Why this exists: Instagram and Facebook actively block HTML scraping. Trying
to crawl them produces a maintenance treadmill. OG tags are a stable public
contract — they don't break every few months.
"""
from __future__ import annotations

import argparse
import re
from contextlib import nullcontext
from datetime import date
from urllib.parse import urlparse

from .common import (
    DATA, extract_image_candidates, extract_og_meta, fetch_image, get,
    load_json, logger, polite_delay, rendered_session, save_json,
    setup_logging, slugify,
)


SEEDS_PATH = DATA / "manual_seeds.json"

# Generic site titles that OG returns when a profile isn't crawler-accessible
# (private/login-walled IG/FB profiles serve these as og:title).
GENERIC_TITLES = {
    "instagram", "facebook", "twitter", "x", "tiktok", "youtube",
    "linkedin", "threads", "log in", "login", "sign up", "log into facebook",
}


def _empty_seeds() -> dict:
    return {"seeds": []}


def derive_name_from_url_handle(url: str) -> str | None:
    """Extract a handle from a social-profile URL and titlecase it.

    instagram.com/rossi_sculpture_design/ -> "Rossi Sculpture Design"
    facebook.com/SomePage              -> "Some Page"
    Returns None for URLs without a usable handle (e.g. /p/<post>, /explore/).
    """
    path = urlparse(url).path.strip("/")
    if not path:
        return None
    handle = path.split("/")[0]
    # Skip non-profile prefixes
    if not handle or handle.lower() in (
        "p", "explore", "reel", "reels", "tv", "stories", "groups",
        "pages", "search", "watch", "marketplace", "events",
    ):
        return None
    parts = [p for p in re.split(r"[_.\-]+", handle) if p]
    if not parts:
        return None
    return " ".join(p.capitalize() for p in parts)


def derive_name(og: dict, url: str) -> str:
    """Pull a usable display name from OG meta, falling back to URL handle.

    Instagram pattern:  "Display Name (@handle) • Instagram photos and videos"
    Facebook pattern:   "Display Name | Facebook" / "Display Name - Facebook"
    Generic platform titles (just "Instagram" etc.) trigger URL-handle fallback,
    so private/login-walled profiles still yield a useful name.
    """
    title = (og.get("og_title") or og.get("html_title") or "").strip()

    # "Display Name (@handle)" pattern — most reliable when present
    m = re.match(r"^(.+?)\s*\(@[^)]+\)", title)
    if m:
        return m.group(1).strip()

    # Strip site suffix ("Some Name | Site")
    head = title
    for sep in (" • ", " | ", " - ", " — "):
        if sep in head:
            head, _, _ = head.partition(sep)
            head = head.strip()
            break

    # If what we got is a generic platform name, the page didn't really expose
    # the profile — fall back to the URL handle.
    if head.lower() in GENERIC_TITLES or not head:
        return derive_name_from_url_handle(url) or head or url

    return head


def ingest_one(seed: dict, rf) -> dict | None:
    """Fetch the seed URL and return a discoveries candidate, or None on failure.

    If the seed has `requires_js: true`, uses headless render via `rf`. If
    `requires_js` is set but Playwright isn't available, marks the seed
    failed (the caller asked for JS; falling back to plain get() would
    return useless content).
    """
    url = seed["url"]
    logger.info("=== seed: %s ===", url[:90])
    if seed.get("requires_js"):
        if rf is None:
            seed["status"] = "failed"
            seed["error"] = "requires_js but playwright unavailable"
            return None
        r = rf.fetch(url)
    else:
        r = get(url)
    if not r:
        seed["status"] = "failed"
        seed["error"] = "fetch failed (non-200 or network error)"
        return None

    og = extract_og_meta(r.text, url)
    name = derive_name(og, url)
    if not name or name == url:
        seed["status"] = "failed"
        seed["error"] = "could not derive a name from page meta"
        return None

    slug = slugify(name)
    # Gather up to 2 thumbs: try og:image first, then body images.
    # The directory cards display 2 side-by-side, so candidate cards should too.
    thumbs: list[dict] = []
    seen_sources: set[str] = set()

    def _try(img_url: str) -> None:
        if img_url in seen_sources or len(thumbs) >= 2:
            return
        seen_sources.add(img_url)
        res = fetch_image(img_url)
        if res:
            uri, kb = res
            label = "primary" if not thumbs else "secondary"
            thumbs.append({"data_uri": uri, "source_url": img_url, "kb": kb, "label": label})

    if og.get("og_image"):
        _try(og["og_image"])
    if len(thumbs) < 2:
        for img_url in extract_image_candidates(r.text, url, max_count=8):
            if len(thumbs) >= 2:
                break
            _try(img_url)
            polite_delay(0.2)
    img_obj = thumbs[0] if thumbs else None

    desc = (og.get("og_description") or "")[:280]

    candidate = {
        "slug": slug,
        "name": name,
        "url": url,
        "source_name": seed.get("source_name") or "manual seed",
        "image": img_obj,         # backward compat — first thumb or None
        "thumbs": thumbs,         # 0-2 real images; qc_images pads to 2 with initials variants
        "first_seen": str(date.today()),
        "status": "pending",
        "seed_note": seed.get("note"),
        "seed_description": desc or None,
    }

    seed["status"] = "processed"
    seed["candidate_slug"] = slug
    return candidate


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=20, help="max seeds to ingest per run")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    seeds_blob = load_json(SEEDS_PATH, _empty_seeds())
    seeds = seeds_blob.setdefault("seeds", [])
    if not seeds:
        logger.info("[seeds] no manual seeds queued")
        return

    artists = load_json(DATA / "artists.json", []) or []
    discoveries = load_json(DATA / "discoveries.json", {"candidates": [], "rejected_slugs": []})

    canon_slugs: set[str] = {a["slug"] for a in artists}
    rejected = set(discoveries.get("rejected_slugs", []))
    existing_slugs = {c["slug"] for c in discoveries.get("candidates", [])}

    ingested = 0
    needs_browser = any(s.get("requires_js") and s.get("status") in (None, "pending") for s in seeds)
    browser_ctx = rendered_session() if needs_browser else nullcontext(None)
    with browser_ctx as rf:
        if needs_browser and rf is None:
            logger.warning("[seeds] some seeds have requires_js but playwright is unavailable — they will fail")
        for seed in seeds:
            if ingested >= args.max:
                break
            if seed.get("status") not in (None, "pending"):
                continue

            cand = ingest_one(seed, rf)
            if cand is None:
                logger.warning("[seed-fail] %s: %s", seed["url"][:80], seed.get("error", "?"))
                continue

            if cand["slug"] in canon_slugs:
                seed["status"] = "skipped"
                seed["error"] = f"already in canonical roster ({cand['slug']})"
                logger.info("[skip] %s already in roster", cand["name"])
                continue
            if cand["slug"] in rejected:
                seed["status"] = "skipped"
                seed["error"] = "already in rejected_slugs"
                logger.info("[skip] %s previously rejected", cand["name"])
                continue
            if cand["slug"] in existing_slugs:
                seed["status"] = "skipped"
                seed["error"] = "already in discoveries"
                logger.info("[skip] %s already queued", cand["name"])
                continue

            discoveries.setdefault("candidates", []).append(cand)
            existing_slugs.add(cand["slug"])
            ingested += 1
            logger.info("[ingested] %s (img=%s)", cand["name"], "yes" if cand["image"] else "no")
            polite_delay(0.5)

    save_json(SEEDS_PATH, seeds_blob)
    save_json(DATA / "discoveries.json", discoveries)
    logger.info("[done] ingested %d seed(s); total queued: %d",
                ingested, len(discoveries.get("candidates", [])))


if __name__ == "__main__":
    main()
