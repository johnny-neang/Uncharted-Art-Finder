"""Ingest GitHub Issues into the curation pipeline.

Three issue templates feed three handlers:
  submission (seed.yml)   — adds a URL to manual_seeds.json for the next scrape
  promote (promote.yml)   — moves a discovery candidate into data/artists.json
  demote (demote.yml)     — moves an artist out of artists.json back to discoveries

The dashboard's CTAs ("Add URL", "Promote to Directory", "Move back to Candidates")
open the corresponding GitHub Issue with the slug/URL prefilled. This step runs
in the daily pipeline before ingest_seeds — it reads open issues via gh,
processes each by label, and closes the issue with an audit comment.

If gh isn't on PATH or isn't authenticated, this step skips cleanly.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import date
from urllib.parse import urlparse

from .common import DATA, load_json, logger, save_json, setup_logging

SEEDS_PATH = DATA / "manual_seeds.json"
ARTISTS_PATH = DATA / "artists.json"
DISCOVERIES_PATH = DATA / "discoveries.json"

LABELS = ("submission", "promote", "demote")


def _gh_available() -> bool:
    if not shutil.which("gh"):
        return False
    r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    return r.returncode == 0


def _list_open_issues_for_labels(labels: tuple[str, ...]) -> list[dict]:
    """Query open issues for each of the given labels via the gh CLI.
    Returns a deduped list with each issue's `labels` field attached."""
    out: dict[int, dict] = {}
    for label in labels:
        r = subprocess.run(
            ["gh", "issue", "list", "--label", label, "--state", "open",
             "--limit", "100", "--json", "number,title,body,author,createdAt,labels"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            logger.warning("[issues] gh list (label=%s) failed: %s", label, r.stderr[:200])
            continue
        try:
            for issue in json.loads(r.stdout):
                out[issue["number"]] = issue
        except json.JSONDecodeError as e:
            logger.warning("[issues] gh output not JSON for label=%s: %s", label, e)
    return list(out.values())


def _issue_label_set(issue: dict) -> set[str]:
    return {l["name"] for l in (issue.get("labels") or [])}


def _extract_section(body: str, heading: str) -> str | None:
    """Extract content under a markdown heading (### Heading) from a
    form-rendered issue body. Returns trimmed text or None if no content
    (e.g. GitHub renders empty fields as `_No response_`).
    """
    pattern = rf"###\s*{re.escape(heading)}\s*\n+([^\n#][^\n]*(?:\n(?![#-])[^\n]*)*)"
    m = re.search(pattern, body, re.IGNORECASE)
    if not m:
        return None
    val = m.group(1).strip()
    if not val or val.lower() in ("_no response_", "_none_"):
        return None
    return val


def parse_issue_body(body: str) -> dict:
    """Extract url, note, requires_js from a form-template-rendered issue body.

    GitHub form templates render as markdown like:
        ### URL
        https://www.instagram.com/some_artist/

        ### Note (optional)
        Spotted on IG

        ### Site needs JavaScript to render?
        - [x] Yes, the URL is JS-rendered
    """
    out = {"url": None, "note": None, "requires_js": False}

    # Match "### URL" section
    url_section = re.search(r"###\s*URL\s*\n+\s*([^\s]+)", body, re.IGNORECASE)
    if url_section:
        candidate = url_section.group(1).strip()
        if candidate.startswith(("http://", "https://")):
            out["url"] = candidate
    else:
        # Fallback: first URL in body
        m = re.search(r"https?://\S+", body)
        if m:
            out["url"] = m.group(0).rstrip(").,;\"'")

    note_section = re.search(
        r"###\s*Note[^\n]*\n+([^\n#][^\n]*(?:\n(?![#-])[^\n]*)*)",
        body, re.IGNORECASE,
    )
    if note_section:
        note = note_section.group(1).strip()
        if note and note.lower() != "_no response_":
            out["note"] = note[:280]

    if re.search(r"-\s*\[x\]\s*Yes,\s*the URL is JS-rendered", body, re.IGNORECASE):
        out["requires_js"] = True

    return out


def _slug_from_body(body: str) -> str | None:
    """Pull the slug from a promote/demote issue body. Tries the form
    section first, then falls back to scanning the title-line or body for
    a token matching the slugify shape."""
    val = _extract_section(body, "Candidate slug") or _extract_section(body, "Directory slug")
    if val:
        m = re.match(r"^[a-z0-9_]+", val.lower())
        if m:
            return m.group(0)
    return None


def _handle_promotion(issue: dict) -> bool:
    """Move a candidate from data/discoveries.json to data/artists.json.
    Returns True on success (issue should be closed)."""
    body = issue.get("body") or ""
    num = issue["number"]
    slug = _slug_from_body(body)
    if not slug:
        _comment_and_close(num, "Closing — no candidate slug found in issue body. Please re-open with the slug.")
        return False

    tier_str = _extract_section(body, "Tier") or "2"
    try:
        tier = int(tier_str.strip()[0])
        if tier not in (1, 2, 3):
            tier = 2
    except (ValueError, IndexError):
        tier = 2
    note = _extract_section(body, "Why promote") or ""

    discoveries = load_json(DISCOVERIES_PATH, {"candidates": []}) or {"candidates": []}
    artists = load_json(ARTISTS_PATH, []) or []

    candidate = next((c for c in discoveries.get("candidates", []) if c.get("slug") == slug), None)
    if not candidate:
        _comment_and_close(num, f"Closing — slug `{slug}` not found in discoveries.json. Maybe already promoted?")
        return False

    if any(a.get("slug") == slug for a in artists):
        _comment_and_close(num, f"Closing — `{slug}` is already in the directory.")
        return False

    score = candidate.get("score") or {}
    url = candidate.get("url") or ""
    primary_host = urlparse(url).netloc if url else ""

    thumbs = candidate.get("thumbs") or ([candidate["image"]] if candidate.get("image") else [])

    new_entry = {
        "n": max((a.get("n", 0) for a in artists), default=0) + 1,
        "slug": slug,
        "name": candidate.get("name") or slug,
        "tier": tier,
        "kind": score.get("kind") or "Artist",
        "medium": score.get("medium") or "Mixed media",
        "tags": score.get("suggested_tags") or [],
        "summary": score.get("one_line_summary") or candidate.get("seed_description") or "",
        "fit": score.get("family_fit") or 3,
        "suitability": score.get("suitability") or "",
        "primaryUrl": url,
        "primaryHost": primary_host,
        "thumbs": thumbs,
        "addedAt": str(date.today()),
        "status": "active",
        "promoted_from": {
            "source_name": candidate.get("source_name"),
            "first_seen": candidate.get("first_seen"),
            "issue": num,
        },
    }
    artists.append(new_entry)
    discoveries["candidates"] = [c for c in discoveries.get("candidates", []) if c.get("slug") != slug]

    save_json(ARTISTS_PATH, artists)
    save_json(DISCOVERIES_PATH, discoveries)

    msg = (
        f"Promoted **{new_entry['name']}** to the Directory as tier {tier} (entry #{new_entry['n']}).\n\n"
        f"Source: `{candidate.get('source_name')}`  ·  URL: {url}\n\n"
    )
    if note:
        msg += f"> {note}\n\n"
    msg += "Live on the dashboard at the next `/refresh` rebuild."
    _comment_and_close(num, msg)
    logger.info("[promote] #%d %s -> directory tier %d", num, slug, tier)
    return True


def _handle_demotion(issue: dict) -> bool:
    """Move an artist from data/artists.json to data/discoveries.json.
    Returns True on success (issue should be closed)."""
    body = issue.get("body") or ""
    num = issue["number"]
    slug = _slug_from_body(body)
    if not slug:
        _comment_and_close(num, "Closing — no directory slug found in issue body.")
        return False

    reason = _extract_section(body, "Reason") or ""

    discoveries = load_json(DISCOVERIES_PATH, {"candidates": []}) or {"candidates": []}
    artists = load_json(ARTISTS_PATH, []) or []

    artist = next((a for a in artists if a.get("slug") == slug), None)
    if not artist:
        _comment_and_close(num, f"Closing — slug `{slug}` not in directory. Maybe already demoted?")
        return False

    # If this slug already exists in discoveries (shouldn't, but defensive), bail.
    if any(c.get("slug") == slug for c in discoveries.get("candidates", [])):
        _comment_and_close(num, f"Closing — `{slug}` is already in discoveries.")
        return False

    candidate = {
        "slug": slug,
        "name": artist.get("name") or slug,
        "url": artist.get("primaryUrl") or "",
        "source_name": "demoted from directory",
        "image": (artist.get("thumbs") or [None])[0],
        "thumbs": artist.get("thumbs") or [],
        "first_seen": str(date.today()),
        "status": "pending",
        "manual_override": "watch",  # survives any auto-rejection filter
        "demoted_from_directory": {
            "n_original": artist.get("n"),
            "tier_original": artist.get("tier"),
            "reason": reason,
            "issue": num,
        },
    }
    discoveries.setdefault("candidates", []).append(candidate)
    artists = [a for a in artists if a.get("slug") != slug]

    save_json(ARTISTS_PATH, artists)
    save_json(DISCOVERIES_PATH, discoveries)

    msg = f"Moved **{artist.get('name')}** out of the Directory back into Recent Candidates.\n\n"
    if reason:
        msg += f"> {reason}\n\n"
    msg += "Live on the dashboard at the next `/refresh` rebuild."
    _comment_and_close(num, msg)
    logger.info("[demote] #%d %s -> discoveries", num, slug)
    return True


def _comment_and_close(issue_num: int, body: str) -> None:
    """Post a comment and close the issue. Best-effort — don't fail the step."""
    c = subprocess.run(
        ["gh", "issue", "comment", str(issue_num), "--body", body],
        capture_output=True, text=True,
    )
    if c.returncode != 0:
        logger.warning("[issues] comment failed on #%d: %s", issue_num, c.stderr[:200])
    cl = subprocess.run(
        ["gh", "issue", "close", str(issue_num), "--reason", "completed"],
        capture_output=True, text=True,
    )
    if cl.returncode != 0:
        logger.warning("[issues] close failed on #%d: %s", issue_num, cl.stderr[:200])


def _handle_submission(issue: dict, seeds: list[dict], existing_urls: set[str]) -> bool:
    """Add a URL to manual_seeds.json. Returns True if added (or already-queued)."""
    num = issue["number"]
    body = issue.get("body") or ""
    author = (issue.get("author") or {}).get("login", "?")
    parsed = parse_issue_body(body)
    if not parsed["url"]:
        logger.warning("[submission] #%d: no URL found in body", num)
        _comment_and_close(num, "Closing — no URL found in submission. Please re-open with a valid URL.")
        return False
    if parsed["url"] in existing_urls:
        logger.info("[submission] #%d: %s already queued — closing", num, parsed["url"][:60])
        _comment_and_close(num, f"Closing — `{parsed['url']}` is already in the seed queue.")
        return False

    seed = {
        "url": parsed["url"],
        "note": (parsed["note"] or f"Submitted via issue #{num} by @{author}"),
        "status": "pending",
        "source_name": f"submission #{num}",
    }
    if parsed["requires_js"]:
        seed["requires_js"] = True
    seeds.append(seed)
    existing_urls.add(parsed["url"])
    logger.info("[submission] #%d -> seeded %s (requires_js=%s)",
                num, parsed["url"][:70], parsed["requires_js"])
    _comment_and_close(
        num,
        (
            f"Added to the discovery seed queue. Will be ingested by the next `/refresh` and "
            f"scored against the Arden Fair UnchARTed criteria.\n\n"
            f"Tracking: `{parsed['url']}` — `requires_js={parsed['requires_js']}`"
        ),
    )
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=20, help="max issues to process per run")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    if not _gh_available():
        logger.info("[issues] gh CLI not available or not authenticated — skipping")
        return

    issues = _list_open_issues_for_labels(LABELS)
    if not issues:
        logger.info("[issues] no open issues with relevant labels (%s)", ", ".join(LABELS))
        return

    seeds_blob = load_json(SEEDS_PATH, {"seeds": []})
    seeds = seeds_blob.setdefault("seeds", [])
    existing_urls = {s["url"] for s in seeds}

    counts = {"submission": 0, "promote": 0, "demote": 0, "skipped": 0}
    for issue in issues[: args.max]:
        labels = _issue_label_set(issue)
        num = issue["number"]
        author = (issue.get("author") or {}).get("login", "?")
        logger.info("=== issue #%d by @%s [labels=%s] ===", num, author, ",".join(sorted(labels)))

        if "promote" in labels:
            if _handle_promotion(issue):
                counts["promote"] += 1
        elif "demote" in labels:
            if _handle_demotion(issue):
                counts["demote"] += 1
        elif "submission" in labels:
            if _handle_submission(issue, seeds, existing_urls):
                counts["submission"] += 1
        else:
            counts["skipped"] += 1
            logger.info("[issues] #%d: no relevant label", num)

    save_json(SEEDS_PATH, seeds_blob)
    logger.info(
        "[issues] processed: submission=%d promote=%d demote=%d skipped=%d",
        counts["submission"], counts["promote"], counts["demote"], counts["skipped"],
    )


if __name__ == "__main__":
    main()
