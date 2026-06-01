"""QC pass: ensure every candidate has up-to-2 unique, real photographs.

The pipeline is "compile, don't interpret" — we never generate, sketch, or
otherwise depict an artist's work. We only fetch real photos from the
artist's own source URL. If none is available, the candidate's thumbs
list is left empty and the dashboard renders a "No photo on file"
placeholder for that slot.

Key behaviors:
  - Refetches each candidate's URL and walks og:image + body images, stopping
    after 2 unique images via fetch_thumbs (dedups by URL *and* by data-URI
    content prefix so the same image at two URLs is also caught).
  - Detects existing duplicates (same image stored as both thumbs) and clears
    them so the refetch can repopulate cleanly. This is how the dedup-bug
    backfill happens.
  - No more interpretive SVG avatars — the previous initials-avatar fallback
    was removed because it filled the second slot with a non-photographic
    placeholder, which conflicted with the "compile information" mandate.

Runs in the orchestrator before build_dashboard so the rendered HTML
reflects the latest QC state.
"""
from __future__ import annotations

import argparse

from contextlib import nullcontext
from datetime import date

from .common import (
    DATA, fetch_image, fetch_instagram_apify_backup, fetch_instagram_thumbs,
    fetch_thumbs, get, load_json, logger, polite_delay, rendered_session,
    save_json, setup_logging,
)

MANUAL_PHOTOS_PATH = "manual_artist_photos.json"
APIFY_ATTEMPTS_PATH = "apify_attempts.json"


def try_refetch_thumbs(candidate: dict, want: int = 2, existing: list[dict] | None = None, rf=None) -> list[dict]:
    """Refetch the candidate URL and gather up to `want` *unique* images.

    Uses fetch_thumbs with follow_links=True (multi-page sub-page crawl)
    and an optional Playwright `rf` for lazy-loaded sites. `existing` seeds
    the URL + content dedup so we don't restore items already on the
    candidate.
    """
    url = candidate.get("url")
    if not url:
        return []
    return fetch_thumbs(
        get(url), url, want=want,
        existing=existing or [], follow_links=True, max_subpages=5, rf=rf,
    )


def fetch_manual_thumbs(urls: list[str], target: int = 2) -> list[dict]:
    """Fetch the user-curated URLs in order. No dedup — the user chose them."""
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
        out.append({"data_uri": uri, "source_url": u, "kb": kb,
                    "label": "primary" if not out else "secondary"})
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


def _has_clean_unique_thumbs(c: dict) -> bool:
    """True if the candidate already has 2 distinct real thumbs and we don't
    need to refetch. Uses both source_url and data_uri prefix as the
    uniqueness signal."""
    thumbs = (c.get("thumbs") or [])
    real = [t for t in thumbs if not t.get("placeholder") and (t.get("data_uri") or t.get("img"))]
    if len(real) < 2:
        return False
    urls = {t.get("source_url", "") for t in real if t.get("source_url")}
    uris = {(t.get("data_uri") or t.get("img") or "")[:200] for t in real}
    return len(urls) >= len(real) and len(uris) >= len(real)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--no-refetch", action="store_true",
                   help="skip the network refetch step (mark missing/dupe slots empty)")
    p.add_argument("--force", action="store_true",
                   help="refetch all candidates, even ones with clean unique thumbs")
    p.add_argument("--apify-retry", action="store_true",
                   help="let the paid Apify backup re-attempt candidates already in the ledger")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    discoveries = load_json(DATA / "discoveries.json", {"candidates": []})
    candidates = discoveries.get("candidates", [])
    if not candidates:
        logger.info("[qc] no candidates")
        return
    manual = (load_json(DATA / MANUAL_PHOTOS_PATH, {}) or {}).get("by_slug", {})
    ig_handles = (load_json(DATA / "instagram_handles.json", {}) or {}).get("by_slug", {})
    # Shared once-per-artist Apify ledger (the same file refresh_images uses) so
    # the paid backup fires at most once per slug across the whole pipeline.
    apify_attempts = (load_json(DATA / APIFY_ATTEMPTS_PATH, {}) or {}).get("by_slug", {})
    apify_attempts_dirty = False
    apify_calls: list[str] = []

    # Open one Playwright session for lazy-load fallbacks. Yields None
    # if Playwright isn't installed; fetch_thumbs silently skips render.
    browser_ctx = rendered_session() if candidates else nullcontext(None)

    refetched = 0
    manual_used = 0
    cleared_dupes = 0
    skipped = 0
    with browser_ctx as rf:
        for c in candidates:
            if not args.force and _has_clean_unique_thumbs(c):
                skipped += 1
                continue

            logger.info("=== %s ===", c["name"])
            existing = candidate_thumbs(c)
            existing_real = [t for t in existing if not t.get("placeholder")]

            # Detect existing duplicates and clear them down to one seed.
            if len(existing_real) >= 2:
                urls = {t.get("source_url", "") for t in existing_real if t.get("source_url")}
                uris = {(t.get("data_uri") or t.get("img") or "")[:200] for t in existing_real}
                if len(urls) < len(existing_real) or len(uris) < len(existing_real):
                    logger.info("[qc-dedupe] %s had duplicate thumbs; clearing", c["name"])
                    existing_real = existing_real[:1]
                    cleared_dupes += 1

            new_thumbs: list[dict] = list(existing_real)

            # Stage 1: manual override (per-slug user-curated URLs)
            manual_urls = manual.get(c.get("slug")) or []
            if manual_urls and len(new_thumbs) < 2:
                fresh_manual = fetch_manual_thumbs(manual_urls, target=2 - len(new_thumbs))
                new_thumbs.extend(fresh_manual)
                if fresh_manual:
                    manual_used += 1

            # Stage 2: Instagram, FREE tier only. The paid Apify tier is
            # deferred to Stage 4 so the free page crawl gets a turn first.
            ig_handle = ig_handles.get(c.get("slug"))
            if ig_handle and len(new_thumbs) < 2:
                ig_thumbs = fetch_instagram_thumbs(
                    ig_handle, rf, want=2 - len(new_thumbs), existing=new_thumbs, allow_apify=False)
                new_thumbs.extend(ig_thumbs)

            # Stage 3: auto-crawl with multi-page + Playwright fallback (free)
            fresh: list[dict] = []
            if not args.no_refetch and len(new_thumbs) < 2:
                fresh = try_refetch_thumbs(c, want=2 - len(new_thumbs), existing=new_thumbs, rf=rf)
                new_thumbs.extend(fresh)
                if fresh:
                    refetched += len(fresh)
                    logger.info("  +%d unique thumb(s)", len(fresh))

            # Stage 4: Apify IG scraper (paid) — LAST RESORT. Only after every
            # free source above came up short, and at most ONCE per artist
            # (shared apify_attempts.json ledger). --apify-retry forces it.
            slug = c.get("slug")
            if (ig_handle and len(new_thumbs) < 2 and not args.no_refetch
                    and (args.apify_retry or slug not in apify_attempts)):
                apify_attempts[slug] = str(date.today())  # record the paid attempt
                apify_attempts_dirty = True
                apify_calls.append(slug)
                ap_thumbs = fetch_instagram_apify_backup(ig_handle, want=2 - len(new_thumbs), existing=new_thumbs)
                new_thumbs.extend(ap_thumbs)
                if ap_thumbs:
                    refetched += len(ap_thumbs)
                    logger.info("  +%d unique thumb(s) via Apify (last resort)", len(ap_thumbs))
            elif (ig_handle and len(new_thumbs) < 2 and not args.no_refetch
                    and slug in apify_attempts and not args.apify_retry):
                logger.info("  apify: %s tried %s already — skipping paid retry (use --apify-retry)",
                            slug, apify_attempts.get(slug))

            for i, t in enumerate(new_thumbs):
                t["label"] = "primary" if i == 0 else "secondary"
            c["thumbs"] = new_thumbs
            c["image"] = new_thumbs[0] if new_thumbs else None

    save_json(DATA / "discoveries.json", discoveries)
    if apify_attempts_dirty:
        save_json(DATA / APIFY_ATTEMPTS_PATH, {"by_slug": apify_attempts})
    counts = {0: 0, 1: 0, 2: 0}
    for c in candidates:
        n = len(c.get("thumbs") or [])
        counts[min(n, 2)] = counts.get(min(n, 2), 0) + 1
    logger.info("[qc-done] refetched=%d manual=%d cleared_dupes=%d skipped=%d apify_paid=%d",
                refetched, manual_used, cleared_dupes, skipped, len(apify_calls))
    if apify_calls:
        logger.info("[qc-apify] paid backup fired for: %s", ", ".join(apify_calls))
    logger.info("[qc-coverage] 0-thumb=%d 1-thumb=%d 2-thumb=%d (of %d)",
                counts[0], counts[1], counts[2], len(candidates))


if __name__ == "__main__":
    main()
