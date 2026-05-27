"""Ingest GitHub Issues (label: submission) into the manual_seeds.json queue.

The dashboard has an "Add a URL" link that opens a GitHub Issue using the
form template at .github/ISSUE_TEMPLATE/seed.yml. The form collects a URL,
optional note, and a requires_js checkbox; GitHub auto-labels the issue
`submission`.

This step (run before ingest_seeds in the daily pipeline) reads open
`submission` issues via the gh CLI, parses the form-rendered body, appends
each URL to data/manual_seeds.json, and closes the issue with a comment
naming the resulting candidate slug. The next ingest_seeds step picks
them up like any other manual seed.

If gh isn't on PATH or isn't authenticated, this step skips cleanly so
the rest of the pipeline isn't blocked.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import date

from .common import DATA, load_json, logger, save_json, setup_logging

SEEDS_PATH = DATA / "manual_seeds.json"
LABEL = "submission"


def _gh_available() -> bool:
    if not shutil.which("gh"):
        return False
    r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    return r.returncode == 0


def _list_open_submission_issues() -> list[dict]:
    r = subprocess.run(
        ["gh", "issue", "list", "--label", LABEL, "--state", "open",
         "--limit", "100", "--json", "number,title,body,author,createdAt"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.warning("[issues] gh list failed: %s", r.stderr[:200])
        return []
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as e:
        logger.warning("[issues] gh output not JSON: %s", e)
        return []


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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=20, help="max submissions to ingest per run")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    if not _gh_available():
        logger.info("[issues] gh CLI not available or not authenticated — skipping")
        return

    issues = _list_open_submission_issues()
    if not issues:
        logger.info("[issues] no open submission issues")
        return

    seeds_blob = load_json(SEEDS_PATH, {"seeds": []})
    seeds = seeds_blob.setdefault("seeds", [])
    existing_urls = {s["url"] for s in seeds}

    ingested = 0
    for issue in issues:
        if ingested >= args.max:
            break
        num = issue["number"]
        body = issue.get("body") or ""
        author = (issue.get("author") or {}).get("login", "?")
        logger.info("=== issue #%d by @%s ===", num, author)

        parsed = parse_issue_body(body)
        if not parsed["url"]:
            logger.warning("[issues] #%d: no URL found in body", num)
            _comment_and_close(num, "Closing — no URL found in submission. Please re-open with a valid URL.")
            continue

        if parsed["url"] in existing_urls:
            logger.info("[issues] #%d: %s already queued — closing", num, parsed["url"][:60])
            _comment_and_close(num, f"Closing — `{parsed['url']}` is already in the seed queue.")
            continue

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
        ingested += 1
        logger.info("[issues] #%d -> seeded %s (requires_js=%s)",
                    num, parsed["url"][:70], parsed["requires_js"])

        _comment_and_close(
            num,
            (
                f"Added to the discovery seed queue. Will be ingested by the next `/refresh` and "
                f"scored against the Arden Fair UnchARTed criteria.\n\n"
                f"Tracking: `{parsed['url']}` — `requires_js={parsed['requires_js']}`"
            ),
        )

    save_json(SEEDS_PATH, seeds_blob)
    logger.info("[issues] ingested %d submission(s); total seeds queued: %d",
                ingested, len(seeds))


if __name__ == "__main__":
    main()
