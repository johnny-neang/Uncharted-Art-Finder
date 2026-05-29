"""One-pass remediation for cross-card duplicate images.

The fetch pipeline only dedups *within* a single card, so a shared asset
(a broken-grid Instagram promo graphic, a group-show event photo) could land
as the same image on many different cards. This script finds those, removes
them, and refills each emptied slot — preferring a real photo via the Apify
Instagram backup (for cards with an IG handle, when APIFY is set), otherwise a
"Second image not available" placeholder.

Policy (matches the product decision):
  - Denylisted junk images (data/image_denylist.json) → removed from every card.
  - Any *other* image shared across >1 card → kept on its most-likely owner
    (source-url host matching its own site, else the first slug), placeholdered
    on the rest.
  - Emptied slot refill: Apify IG backup if handle + APIFY present and the
    result is unique & not denylisted; otherwise a placeholder.

Directory artists are consolidated into data/artist_images.json (their
artists.json `thumbs` is cleared so the cache is the single source); candidates
are written back to data/discoveries.json `thumbs`.

Usage:
  python -m scripts.dedupe_images                # dry run — report only
  python -m scripts.dedupe_images --apply        # write changes (Apify if APIFY set)
  python -m scripts.dedupe_images --apply --placeholder-only   # never call Apify
"""
from __future__ import annotations

import argparse
import hashlib
from contextlib import nullcontext
from datetime import date
from urllib.parse import urlparse

from .common import (
    DATA, fetch_instagram_apify_backup, fetch_instagram_thumbs, fetch_thumbs,
    get, load_json, logger, rendered_session, save_json, setup_logging,
)

PLACEHOLDER_NOTE_SECONDARY = "Second image not available"
PLACEHOLDER_NOTE_PRIMARY = "Image not available"


def _md5(s: str | None) -> str | None:
    return hashlib.md5(s.encode("utf-8", errors="ignore")).hexdigest() if s else None


def _uri(t: dict) -> str | None:
    return (t.get("data_uri") or t.get("img")) if isinstance(t, dict) else None


def _host(url: str | None) -> str:
    try:
        return urlparse(url or "").netloc.lower().replace("www.", "")
    except Exception:
        return ""


def _placeholder(slot: int) -> dict:
    note = PLACEHOLDER_NOTE_PRIMARY if slot == 0 else PLACEHOLDER_NOTE_SECONDARY
    return {"placeholder": True, "note": note,
            "label": "primary" if slot == 0 else "secondary"}


def _effective_images(slug, artist, cache):
    """Directory artist's rendered real images, in slot order, with the
    source_url carried for owner detection. Prefers artists.json thumbs, then
    the artist_images cache (mirrors build_dashboard.merge_artist_images)."""
    src = artist.get("thumbs") or []
    cim = cache.get(slug, {}).get("images", [])
    out = []
    for i in range(2):
        t = src[i] if i < len(src) and isinstance(src[i], dict) else {}
        ci = cim[i] if i < len(cim) and isinstance(cim[i], dict) else {}
        if _uri(t):
            out.append({"data_uri": _uri(t), "source_url": t.get("source_url", "")})
        elif ci.get("data_uri"):
            out.append({"data_uri": ci["data_uri"], "source_url": ci.get("source_url", "")})
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    p.add_argument("--placeholder-only", action="store_true",
                   help="never call Apify; placeholder every emptied slot")
    p.add_argument("--only", nargs="*",
                   help="limit refill+write to these slugs (cross-card detection stays global)")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    import os
    apify_ready = bool(os.environ.get("APIFY")) and not args.placeholder_only

    artists = load_json(DATA / "artists.json", []) or []
    cache = load_json(DATA / "artist_images.json", {}) or {}
    disc = load_json(DATA / "discoveries.json", {"candidates": []}) or {}
    cands = disc.get("candidates", [])
    ig = (load_json(DATA / "instagram_handles.json", {}) or {}).get("by_slug", {})
    denylist = set((load_json(DATA / "image_denylist.json", {}) or {}).get("by_md5", {}).keys())

    arts_by_slug = {a["slug"]: a for a in artists}
    cands_by_slug = {c["slug"]: c for c in cands}

    # ---- Build a unified view of every card's real images ----
    # card: {slug, kind, name, ig, primary_host, images:[{data_uri, source_url, md5}]}
    cards = {}
    for slug, a in arts_by_slug.items():
        imgs = _effective_images(slug, a, cache)
        for im in imgs:
            im["md5"] = _md5(im["data_uri"])
        cards[("dir", slug)] = {
            "slug": slug, "kind": "dir", "name": a.get("name", slug), "url": a.get("primaryUrl"),
            "ig": ig.get(slug), "primary_host": _host(a.get("primaryUrl")), "images": imgs,
        }
    for slug, c in cands_by_slug.items():
        imgs = []
        for t in (c.get("thumbs") or []):
            if isinstance(t, dict) and not t.get("placeholder") and _uri(t):
                imgs.append({"data_uri": _uri(t), "source_url": t.get("source_url", ""), "md5": _md5(_uri(t))})
        cards[("cand", slug)] = {
            "slug": slug, "kind": "cand", "name": c.get("name", slug), "url": c.get("url"),
            "ig": ig.get(slug), "primary_host": _host(c.get("url")), "images": imgs,
        }

    # ---- Find cross-card duplicate md5s (excluding denylisted, handled separately) ----
    md5_to_cards = {}
    for key, card in cards.items():
        for im in card["images"]:
            md5_to_cards.setdefault(im["md5"], set()).add(key)
    shared = {m: ks for m, ks in md5_to_cards.items() if m not in denylist and len(ks) > 1}

    # For each shared (real) image, pick the owner: a card whose source_url host
    # matches its own primary host, else the alphabetically-first slug.
    owner_of = {}
    for m, keys in shared.items():
        owners = []
        for key in keys:
            card = cards[key]
            srcs = [im["source_url"] for im in card["images"] if im["md5"] == m]
            if card["primary_host"] and any(_host(s) == card["primary_host"] for s in srcs):
                owners.append(key)
        owner_of[m] = (sorted(owners)[0] if owners else sorted(keys, key=lambda k: k[1])[0])

    # ---- Decide each card's final image set ----
    used_md5 = set()  # md5s we KEEP, to prevent re-introducing a cross-card dup
    # First pass: keep non-junk, non-loser images; collect their md5s.
    for key, card in cards.items():
        kept = []
        for im in card["images"]:
            m = im["md5"]
            if m in denylist:
                continue  # junk — drop everywhere
            if m in shared and owner_of[m] != key:
                continue  # duplicate kept elsewhere
            kept.append(im)
        card["kept"] = kept
        for im in kept:
            used_md5.add(im["md5"])

    # ---- Refill emptied slots: Apify (if eligible) else placeholder ----
    plan = {"removed": 0, "free_filled": 0, "apify_filled": 0, "placeholdered": 0,
            "free_cards": [], "apify_cards": [], "ph_cards": []}

    # Mark untouched cards (no duplicate/junk, or excluded by --only) so they're
    # left exactly as-is.
    only = set(args.only) if args.only else None
    affected = []
    for key, card in cards.items():
        removed = len(card["images"]) - len(card["kept"])
        if removed == 0 or (only is not None and card["slug"] not in only):
            card["final"] = None
        else:
            affected.append((key, card))

    # A Playwright session powers the FREE tiers (IG grid render + crawl render
    # fallback). Apify (paid) is only ever reached after both come up short.
    browser = rendered_session() if (affected and args.apply and not args.placeholder_only) else nullcontext(None)
    with browser as rf:
        for key, card in affected:
            before = len(card["images"])
            kept = list(card["kept"])
            plan["removed"] += before - len(kept)
            target = before  # restore only the slots that were filled before

            def _existing():
                return [{"data_uri": im["data_uri"], "source_url": im.get("source_url", "")} for im in kept]

            def _add(items):
                n = 0
                for g in (items or []):
                    if len(kept) >= target:
                        break
                    uri = (g.get("data_uri") or g.get("img")) if isinstance(g, dict) else None
                    gm = _md5(uri)
                    if not gm or gm in denylist or gm in used_md5:
                        continue  # junk, or would re-create a cross-card duplicate
                    used_md5.add(gm)
                    kept.append({"data_uri": uri, "source_url": g.get("source_url", ""), "md5": gm})
                    n += 1
                return n

            if args.apply and not args.placeholder_only:
                free_n = 0
                # FREE tier 1: re-render the logged-out IG grid (may serve real
                # posts now; the old junk graphic is denylisted either way).
                if card["ig"] and len(kept) < target:
                    try:
                        free_n += _add(fetch_instagram_thumbs(
                            card["ig"], rf, want=target - len(kept), existing=_existing(), allow_apify=False))
                    except Exception as e:
                        logger.warning("[free-ig] %s: %s", card["slug"], str(e)[:120])
                # FREE tier 2: crawl the card's own site (+ render fallback).
                if card["url"] and len(kept) < target:
                    try:
                        free_n += _add(fetch_thumbs(
                            get(card["url"]), card["url"], want=target - len(kept),
                            existing=_existing(), follow_links=True, max_subpages=4, rf=rf))
                    except Exception as e:
                        logger.warning("[crawl] %s: %s", card["slug"], str(e)[:120])
                if free_n:
                    plan["free_filled"] += free_n
                    plan["free_cards"].append(card["slug"])
                # LAST RESORT: Apify (paid) — only if free tiers left us short.
                if card["ig"] and apify_ready and len(kept) < target:
                    try:
                        a_n = _add(fetch_instagram_apify_backup(card["ig"], want=target, existing=_existing()))
                    except Exception as e:
                        logger.warning("[apify] %s: %s", card["slug"], str(e)[:120])
                        a_n = 0
                    if a_n:
                        plan["apify_filled"] += a_n
                        plan["apify_cards"].append(card["slug"])

            # Placeholder any slot still empty after all tiers.
            final = list(kept)
            while len(final) < target:
                final.append(_placeholder(len(final)))
                plan["placeholdered"] += 1
                if card["slug"] not in plan["ph_cards"]:
                    plan["ph_cards"].append(card["slug"])
            card["final"] = final

    # ---- Report ----
    mode = "apply" if args.apply else "dry-run"
    n_affected = len(affected)
    logger.info("[plan] mode=%s apify_ready=%s affected_cards=%d removed=%d  free_filled=%d apify_filled=%d placeholdered=%d",
                mode, apify_ready, n_affected, plan["removed"],
                plan["free_filled"], plan["apify_filled"], plan["placeholdered"])
    if plan["free_cards"]:
        logger.info("[plan] refilled FREE (%d): %s", len(plan["free_cards"]), ", ".join(sorted(plan["free_cards"])))
    if plan["apify_cards"]:
        logger.info("[plan] refilled via Apify LAST RESORT (%d): %s", len(plan["apify_cards"]), ", ".join(sorted(plan["apify_cards"])))
    if plan["ph_cards"]:
        logger.info("[plan] placeholdered (%d): %s", len(plan["ph_cards"]), ", ".join(sorted(plan["ph_cards"])))
    if not args.apply:
        ig_elig = sorted({c["slug"] for k, c in affected if c["ig"]})
        logger.info("[dry-run] no fetching, no files written. On --apply: %d affected cards, "
                    "%d with an IG handle will try FREE tiers then Apify-last-resort, the rest placeholder.",
                    n_affected, len(ig_elig))
        return

    # ---- Write back ----
    for (kind, slug), card in cards.items():
        final = card["final"]
        if final is None:
            continue  # untouched card
        # Build stored thumbs
        stored = []
        for i, im in enumerate(final):
            label = "primary" if i == 0 else "secondary"
            if im.get("placeholder"):
                stored.append({"placeholder": True, "note": im["note"], "label": label})
            else:
                e = {"data_uri": im["data_uri"], "label": label}
                if im.get("source_url"):
                    e["source_url"] = im["source_url"]
                stored.append(e)
        if kind == "dir":
            cache[slug] = {"name": card["name"], "images": stored, "refreshed": str(date.today())}
            if slug in arts_by_slug:
                arts_by_slug[slug]["thumbs"] = []  # cache is now authoritative
        else:
            c = cands_by_slug[slug]
            c["thumbs"] = stored
            c["image"] = stored[0] if stored else None

    save_json(DATA / "artist_images.json", cache)
    save_json(DATA / "artists.json", artists)
    save_json(DATA / "discoveries.json", disc)
    logger.info("[done] wrote artist_images.json, artists.json, discoveries.json")


if __name__ == "__main__":
    main()
