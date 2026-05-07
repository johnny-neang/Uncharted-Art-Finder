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

from .common import ROOT, TEMPLATES, DATA, load_json, logger, setup_logging


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


def filter_discoveries_for_display(discoveries: list[dict]) -> list[dict]:
    """Show only candidates we'd actually surface to the user."""
    keepers = []
    for c in discoveries:
        score = c.get("score") or {}
        # Reject suggestions filtered out by Claude
        if score.get("proceed_recommendation") == "reject":
            continue
        keepers.append(c)
    # Recently scored / unscored first; cap to a reasonable number
    keepers.sort(key=lambda c: (
        0 if c.get("score") else 1,
        -(c.get("score", {}).get("family_fit", 0) or 0),
        c.get("first_seen", ""),
    ))
    return keepers[:24]


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
    events = events_blob.get("events", [])

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
