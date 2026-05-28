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

from .common import (
    DATA, fetch_thumbs, get, load_json, logger, save_json, setup_logging,
)


def try_refetch_thumbs(candidate: dict, want: int = 2, existing: list[dict] | None = None) -> list[dict]:
    """Refetch the candidate URL and gather up to `want` *unique* images.

    Uses the shared fetch_thumbs helper. Pass `existing` so the dedup
    catches images already on the candidate (the bug that caused 58/65
    candidates to have the same image twice — local dedup didn't know
    about the og:image we'd already stored at ingest time).
    """
    url = candidate.get("url")
    if not url:
        return []
    return fetch_thumbs(get(url), url, want=want, existing=existing or [])


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
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    discoveries = load_json(DATA / "discoveries.json", {"candidates": []})
    candidates = discoveries.get("candidates", [])
    if not candidates:
        logger.info("[qc] no candidates")
        return

    refetched_thumbs_added = 0
    cleared_dupes = 0
    skipped = 0
    for c in candidates:
        if not args.force and _has_clean_unique_thumbs(c):
            skipped += 1
            continue

        existing = candidate_thumbs(c)
        existing_real = [t for t in existing if not t.get("placeholder")]

        # Detect existing duplicates and clear them down to one seed.
        if len(existing_real) >= 2:
            urls = {t.get("source_url", "") for t in existing_real if t.get("source_url")}
            uris = {(t.get("data_uri") or t.get("img") or "")[:200] for t in existing_real}
            if len(urls) < len(existing_real) or len(uris) < len(existing_real):
                logger.info("[qc-dedupe] %s had duplicate thumbs; clearing for refetch", c["name"])
                existing_real = existing_real[:1]
                cleared_dupes += 1

        # Refetch up to 2 unique thumbs (the helper dedups against existing).
        new_thumbs: list[dict] = list(existing_real)
        if not args.no_refetch and len(new_thumbs) < 2:
            fresh = try_refetch_thumbs(c, want=2 - len(new_thumbs), existing=new_thumbs)
            new_thumbs.extend(fresh)
            if fresh:
                refetched_thumbs_added += len(fresh)
                logger.info("[qc-refetched] %s (+%d real thumb(s))", c["name"], len(fresh))

        # No interpretive placeholders. Empty list = "no photo on file"
        # treatment. Reassign labels based on final position.
        for i, t in enumerate(new_thumbs):
            t["label"] = "primary" if i == 0 else "secondary"
        c["thumbs"] = new_thumbs
        c["image"] = new_thumbs[0] if new_thumbs else None

    save_json(DATA / "discoveries.json", discoveries)
    real = sum(1 for c in candidates if c.get("thumbs"))
    logger.info("[qc-done] refetched=%d cleared_dupes=%d skipped=%d  coverage=%d/%d",
                refetched_thumbs_added, cleared_dupes, skipped, real, len(candidates))


if __name__ == "__main__":
    main()
