"""Generate a daily digest markdown file summarizing the day's findings."""
from __future__ import annotations

import argparse
from datetime import date

from .common import DATA, DIGESTS, load_json, logger, setup_logging


def build_digest(today: str) -> str:
    artists = load_json(DATA / "artists.json", []) or []
    images = load_json(DATA / "artist_images.json", {}) or {}
    discoveries = (load_json(DATA / "discoveries.json", {}) or {}).get("candidates", [])
    events = (load_json(DATA / "events.json", {}) or {}).get("events", [])
    refresh_report = load_json(DATA / "_refresh_report.json", {}) or {}

    new_today = [c for c in discoveries if c.get("first_seen") == today]
    scored_today = [c for c in discoveries if c.get("scored_at") == today]
    add_recos = [c for c in scored_today if (c.get("score") or {}).get("proceed_recommendation") == "add"]

    refreshed = refresh_report.get("refreshed", [])
    missed = refresh_report.get("missed", [])

    lines: list[str] = []
    lines.append(f"# Daily Digest · {today}")
    lines.append("")
    lines.append("UpperCloud Studio · Sacramento Artist Directory · Field Brief No. 014")
    lines.append("")

    # TL;DR
    lines.append("## TL;DR")
    lines.append("")
    lines.append(f"- **{len(new_today)}** new candidate{'s' if len(new_today) != 1 else ''} surfaced today")
    lines.append(f"- **{len(scored_today)}** candidate{'s' if len(scored_today) != 1 else ''} scored by Claude")
    lines.append(f"- **{len(add_recos)}** flagged as `add`-worthy")
    lines.append(f"- **{len(refreshed)}** roster image refresh{'es' if len(refreshed) != 1 else ''}, {len(missed)} fell back to SVG")
    lines.append(f"- **{len(events)}** upcoming Sacramento art events tracked")
    lines.append("")

    # New candidates
    if new_today:
        lines.append("## New candidates")
        lines.append("")
        for c in new_today:
            score = c.get("score") or {}
            rec = score.get("proceed_recommendation", "pending")
            fit = score.get("family_fit")
            sac = score.get("sacramento_connection", "?")
            tier = score.get("suggested_tier")
            summary = score.get("one_line_summary") or "(awaiting score)"
            lines.append(f"### {c['name']}")
            lines.append(f"- **Source:** [{c['source_name']}]({c['url']})")
            if score:
                lines.append(f"- **Claude rec:** `{rec}` · fit {fit}/5 · sacramento: {sac} · tier {tier}")
            lines.append(f"- {summary}")
            lines.append("")

    # Add-worthy
    if add_recos:
        lines.append("## Add-worthy this run")
        lines.append("")
        for c in add_recos:
            score = c["score"]
            lines.append(f"- **{c['name']}** ({score.get('family_fit')}/5) — {score.get('one_line_summary')}")
            lines.append(f"  Source: <{c['url']}>")
        lines.append("")

    # Image refresh
    lines.append("## Image refresh report")
    lines.append("")
    if refreshed:
        for r in refreshed:
            lines.append(f"- `{r['slug']}` — {r['count']} new image(s)")
    else:
        lines.append("- (no refreshes this run)")
    if missed:
        lines.append("")
        lines.append("**Fell back to SVG:** " + ", ".join(f"`{s}`" for s in missed))
    lines.append("")

    # Events
    if events:
        lines.append("## Events on the radar")
        lines.append("")
        for e in events[:10]:
            lines.append(f"- **{e.get('date_raw', 'TBD')}** — {e['title']} · [{e['source']}]({e['url']})")
        lines.append("")

    # Roster size
    lines.append("---")
    lines.append("")
    lines.append(f"Roster: **{len(artists)} artists/agencies** · Cached photos: **{sum(len(v.get('images', [])) for v in images.values())}** · Pending discoveries: **{len(discoveries)}**")
    lines.append("")
    lines.append("Live dashboard: ↗ `index.html` (GitHub Pages)")
    lines.append("Full discovery queue: `data/discoveries.json`")
    lines.append("")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=str(date.today()))
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    DIGESTS.mkdir(parents=True, exist_ok=True)
    md = build_digest(args.date)
    out = DIGESTS / f"{args.date}.md"
    out.write_text(md)
    logger.info("[done] wrote %s (%d bytes)", out, len(md))
    print(md)


if __name__ == "__main__":
    main()
