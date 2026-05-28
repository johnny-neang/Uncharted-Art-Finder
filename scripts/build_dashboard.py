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
        new_thumbs = []
        for i, t in enumerate(a.get("thumbs", [])):
            if i < len(cached) and cached[i].get("data_uri"):
                new_thumbs.append({"label": t["label"], "img": cached[i]["data_uri"]})
            else:
                new_thumbs.append({"label": t["label"], "svg": t.get("svg")})
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


def filter_discoveries_for_display(discoveries: list[dict]) -> list[dict]:
    """Sort candidates for display. All states ship to the frontend — the
    dashboard filter chips control which are visible (default hides reject
    + archive). Sort by recommendation, then fit, then first_seen.
    """
    REC_ORDER = {"add": 0, "watch": 1, "pending": 2, "archive": 3, "reject": 4, "existing": 3}
    keepers = list(discoveries)
    keepers.sort(key=lambda c: (
        REC_ORDER.get(effective_rec(c), 5),
        -((c.get("score") or {}).get("family_fit", 0) or 0),
        c.get("first_seen", ""),
    ))
    return keepers


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(ROOT / "index.html"))
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    template = (TEMPLATES / "dashboard.html.tmpl").read_text()
    svg_lib = (TEMPLATES / "svg_library.js").read_text()

    artists_raw = load_json(DATA / "artists.json", []) or []
    images = load_json(DATA / "artist_images.json", {}) or {}
    discoveries_blob = load_json(DATA / "discoveries.json", {"candidates": []}) or {}
    events_blob = load_json(DATA / "events.json", {"events": []}) or {}

    artists = merge_artist_images(artists_raw, images)
    discoveries = filter_discoveries_for_display(discoveries_blob.get("candidates", []))
    events = filter_and_sort_events(events_blob.get("events", []))

    # Render the JS data blocks
    artists_js = f"const ARTISTS = {json.dumps(artists, indent=2, ensure_ascii=False)};"
    discoveries_js = f"window.DISCOVERIES = {json.dumps(discoveries, indent=2, ensure_ascii=False)};"
    events_js = f"window.EVENTS = {json.dumps(events, indent=2, ensure_ascii=False)};"

    # Substitute placeholders
    out = template
    out = out.replace("/* {{SVG_LIBRARY}} */", svg_lib)
    out = out.replace("/* {{ARTISTS_DATA}} */", artists_js)
    out = out.replace("/* {{DISCOVERIES_DATA}} */", discoveries_js)
    out = out.replace("/* {{EVENTS_DATA}} */", events_js)
    out = out.replace("{{LAST_REVIEWED}}", str(date.today()).replace("-", "·"))

    # Update the renderCard function to handle thumbs that are either svg-keyed or img data URIs.
    # The template's renderCard uses SVG[t.svg]; we extend it to also handle t.img.
    # Find the existing thumb-rendering line and replace with a richer one.
    needle = (
        'const art = SVG[t.svg] || `<svg viewBox="0 0 400 300">'
        '<rect width="400" height="300" fill="#EAE3D2"/></svg>`;'
    )
    if needle not in out:
        # The template may have been re-formatted by editors; do a more lenient replacement
        logger.warning("Could not locate exact thumb-render line; falling back to regex")
    replacement = (
        'const art = t.img\n'
        '      ? `<img src="${t.img}" alt="${t.label}" '
        'style="width:100%;height:100%;object-fit:cover;display:block;">`\n'
        '      : (SVG[t.svg] || `<svg viewBox="0 0 400 300">'
        '<rect width="400" height="300" fill="#EAE3D2"/></svg>`);'
    )
    out = out.replace(needle, replacement)

    # Write
    out_path = ROOT / args.out if not args.out.startswith("/") else type(ROOT)(args.out)
    out_path.write_text(out)
    logger.info("[done] wrote %s (%d KB)", out_path, len(out) // 1024)
    logger.info("       artists=%d  discoveries=%d  events=%d",
                len(artists), len(discoveries), len(events))


if __name__ == "__main__":
    main()
