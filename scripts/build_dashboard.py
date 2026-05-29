"""Render index.html from data files + svg library + html template.

Reads:
  templates/dashboard.html.tmpl   the HTML template with {{...}} placeholders
  templates/svg_library.js        the inline SVG declarations
  data/artists.json               canonical artist roster
  data/artist_images.json         cached photos (data URIs) per artist slug
  data/discoveries.json           pending candidates (with optional Claude scores)
  data/events.json                upcoming events list

Writes:
  index.html                      self-contained dashboard, ready for GH Pages
"""
from __future__ import annotations

import argparse
import json
from datetime import date

from .common import (
    DATA, ROOT, TEMPLATES, is_quality_event, load_json, logger,
    parse_event_date, setup_logging,
)


def merge_artist_images(artists: list[dict], images: dict) -> list[dict]:
    """If a real photo exists for an artist, swap their thumbs[i].svg for img.

    Each artist's `thumbs[i]` becomes one of:
      - {label, svg: "<key>"}   when no real photo
      - {label, img: "data:..."} when a real photo is cached
    """
    out = []
    for a in artists:
        a = dict(a)
        cached = images.get(a["slug"], {}).get("images", [])
        src = a.get("thumbs", []) or []
        new_thumbs = []
        # Build thumbs from real photographic sources only. Hand-drawn
        # SVG illustrations from the legacy svg_library are no longer
        # rendered — we compile, we don't depict. An explicit
        # {placeholder, note} entry (e.g. a removed duplicate) passes
        # through so the template can render "Second image not available";
        # otherwise empty slots drop and render the "researching" treatment.
        for i in range(min(2, max(len(src), len(cached)))):
            label = "primary" if i == 0 else "secondary"
            t = src[i] if i < len(src) and isinstance(src[i], dict) else {}
            ci = cached[i] if i < len(cached) and isinstance(cached[i], dict) else {}
            if t.get("label"):
                label = t["label"]
            if t.get("placeholder"):
                new_thumbs.append({"label": label, "placeholder": True, "note": t.get("note")})
            elif t.get("data_uri") or t.get("img"):
                new_thumbs.append({"label": label, "img": t.get("data_uri") or t.get("img")})
            elif ci.get("data_uri"):
                new_thumbs.append({"label": label, "img": ci["data_uri"]})
            elif ci.get("placeholder"):
                new_thumbs.append({"label": label, "placeholder": True, "note": ci.get("note")})
            else:
                # No photo for this slot — drop it. The card will render
                # with however many real photos exist (0, 1, or 2).
                continue
        a["thumbs"] = new_thumbs
        out.append(a)
    return out


def effective_rec(c: dict) -> str:
    """manual_override > score.proceed_recommendation > 'pending'."""
    if c.get("manual_override"):
        return c["manual_override"]
    score = c.get("score") or {}
    return score.get("proceed_recommendation") or "pending"


def filter_and_sort_events(events: list[dict]) -> list[dict]:
    """Drop past + low-quality events; sort upcoming first.

    Backfills `date_iso` from `date_raw` on the fly for older events.json
    entries that were scraped before the parser existed. Events whose date
    can't be parsed are dropped — they're usually calendar-widget noise.
    Title QC (`is_quality_event`) catches calendar headers, UI labels,
    date-only "titles" and help text that slipped past the scraper.
    """
    today_iso = str(date.today())
    upcoming = []
    dropped_qc = 0
    for e in events:
        iso = e.get("date_iso") or parse_event_date(e.get("date_raw") or "")
        if not iso or iso < today_iso:
            continue
        if not is_quality_event(e):
            dropped_qc += 1
            logger.info("       qc-drop: %r", (e.get("title") or "")[:60])
            continue
        e = dict(e)
        e["date_iso"] = iso
        upcoming.append(e)
    if dropped_qc:
        logger.info("       qc-dropped %d low-quality events", dropped_qc)
    upcoming.sort(key=lambda e: e["date_iso"])
    return upcoming


def sort_discoveries_for_display(discoveries: list[dict]) -> list[dict]:
    """Sort candidates for the dashboard's Recent Candidates section.
    All states ship; the frontend filter chips control which are visible.
    Sort order: Claude recommendation (add → watch → pending → archive → reject),
    then family_fit descending, then first_seen ascending.
    """
    REC_ORDER = {"add": 0, "watch": 1, "pending": 2, "archive": 3, "existing": 3, "reject": 4}
    return sorted(discoveries, key=lambda c: (
        REC_ORDER.get(effective_rec(c), 5),
        -((c.get("score") or {}).get("family_fit", 0) or 0),
        c.get("first_seen", ""),
    ))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(ROOT / "index.html"))
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    template = (TEMPLATES / "dashboard.html.tmpl").read_text()
    # svg_library.js is intentionally not loaded — the dashboard renders
    # photographs only, no interpretive illustrations.
    svg_lib = "const SVG = {};"

    artists_raw = load_json(DATA / "artists.json", []) or []
    images = load_json(DATA / "artist_images.json", {}) or {}
    discoveries_blob = load_json(DATA / "discoveries.json", {"candidates": []}) or {}
    events_blob = load_json(DATA / "events.json", {"events": []}) or {}
    notes_blob = load_json(DATA / "notes.json", {"by_slug": {}}) or {}

    artists = merge_artist_images(artists_raw, images)
    discoveries = sort_discoveries_for_display(discoveries_blob.get("candidates", []))
    events = filter_and_sort_events(events_blob.get("events", []))

    # No exclusion: every artist + candidate renders. Cards with fewer than
    # 2 real photo thumbs show a typographic "researching second photo"
    # treatment in the empty slots (handled by the template's renderThumb).
    # The hidden-counter tokens show the "still researching" count, not a
    # hidden-from-view count — they're forward-looking.
    def _real_thumb_count(entry):
        return sum(
            1 for t in (entry.get("thumbs") or [])
            if (t.get("data_uri") or t.get("img"))
            and not t.get("placeholder")
            and not t.get("svg")
        )

    needs_research_dir = [a["slug"] for a in artists if _real_thumb_count(a) < 2]
    needs_research_cand = [c["slug"] for c in discoveries if _real_thumb_count(c) < 2]

    # Render the JS data blocks
    artists_js = f"const ARTISTS = {json.dumps(artists, indent=2, ensure_ascii=False)};"
    discoveries_js = f"window.DISCOVERIES = {json.dumps(discoveries, indent=2, ensure_ascii=False)};"
    events_js = f"window.EVENTS = {json.dumps(events, indent=2, ensure_ascii=False)};"
    notes_js = f"window.NOTES = {json.dumps(notes_blob.get('by_slug', {}), ensure_ascii=False)};"

    # Substitute placeholders
    out = template
    out = out.replace("/* {{SVG_LIBRARY}} */", svg_lib)
    out = out.replace("/* {{ARTISTS_DATA}} */", artists_js)
    out = out.replace("/* {{DISCOVERIES_DATA}} */", discoveries_js)
    out = out.replace("/* {{EVENTS_DATA}} */", events_js)
    out = out.replace("/* {{NOTES_DATA}} */", notes_js)
    out = out.replace("{{LAST_REVIEWED}}", str(date.today()).replace("-", "·"))
    out = out.replace("{{HIDDEN_DIRECTORY}}", str(len(needs_research_dir)))
    out = out.replace("{{HIDDEN_CANDIDATES}}", str(len(needs_research_cand)))

    # Write
    out_path = ROOT / args.out if not args.out.startswith("/") else type(ROOT)(args.out)
    out_path.write_text(out)
    logger.info("[done] wrote %s (%d KB)", out_path, len(out) // 1024)
    logger.info("       directory: rendered=%d researching=%d  | candidates: rendered=%d researching=%d  | events=%d",
                len(artists), len(needs_research_dir), len(discoveries), len(needs_research_cand), len(events))
    if needs_research_dir:
        logger.info("       researching directory: %s", ", ".join(needs_research_dir))
    if needs_research_cand:
        logger.info("       researching candidates (first 10): %s", ", ".join(needs_research_cand[:10]))


if __name__ == "__main__":
    main()
