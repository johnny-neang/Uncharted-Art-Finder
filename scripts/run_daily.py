"""Daily orchestrator. Designed to run locally — by hand or via launchd.

    python3 -m scripts.run_daily

Scoring uses the Claude Code CLI (`claude -p`), so it runs against your
existing Claude Pro/Max subscription auth — no ANTHROPIC_API_KEY needed.

Steps:
  1. Refresh roster images for any artist whose cache is stale or empty
  2. Discover new artist candidates from configured rosters
  3. Score each new candidate via Claude Code CLI (subscription-auth)
  4. Scrape upcoming Sacramento art events
  5. Build the daily markdown digest
  6. Rebuild index.html from data/
  7. Optionally git-commit and push so the GH Pages dashboard updates
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import traceback
from datetime import date

from .common import ROOT, logger, setup_logging


def step(name: str, fn) -> bool:
    """Run a step; capture exceptions so one failure doesn't kill the run.

    Each step's main() runs with a clean argv so its argparse doesn't inherit
    run_daily's flags.
    """
    logger.info("=" * 60)
    logger.info(f"[step] {name}")
    logger.info("=" * 60)
    saved = sys.argv
    sys.argv = [name]
    try:
        fn()
        logger.info(f"[ok] {name}")
        return True
    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"[err] {name}: {e}")
        traceback.print_exc(file=sys.stderr)
        return False
    finally:
        sys.argv = saved


def commit_and_push(today: str) -> None:
    """git add data/ index.html; commit; push. Best-effort: don't crash on failure."""
    if not shutil.which("git"):
        logger.info("[skip] git not on PATH")
        return

    def run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=check)

    run(["git", "add", "data/", "index.html"])
    diff = run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        logger.info("[git] no changes to commit")
        return

    msg = f"Daily digest · {today}"
    commit = run(["git", "commit", "-m", msg])
    if commit.returncode != 0:
        logger.warning("[git] commit failed: %s", (commit.stderr or commit.stdout)[:200])
        return
    logger.info("[git] committed: %s", msg)

    push = run(["git", "push"])
    if push.returncode != 0:
        logger.warning("[git] push failed (commit kept locally): %s", (push.stderr or push.stdout)[:200])
        return
    logger.info("[git] pushed")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--skip-issues", action="store_true")
    p.add_argument("--skip-seeds", action="store_true")
    p.add_argument("--skip-discover", action="store_true")
    p.add_argument("--skip-events", action="store_true")
    p.add_argument("--skip-scoring", action="store_true")
    p.add_argument("--skip-push", action="store_true", help="don't auto-commit/push")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    today = str(date.today())
    logger.info("[run] %s", today)

    from . import refresh_images, ingest_issues, ingest_seeds, discover_artists, scrape_events
    from . import score_with_claude, qc_images, build_digest, build_dashboard

    step("refresh roster images", lambda: refresh_images.main())

    if not args.skip_issues:
        step("ingest dashboard submissions (issues)", lambda: ingest_issues.main())

    if not args.skip_seeds:
        step("ingest manual seeds", lambda: ingest_seeds.main())

    if not args.skip_discover:
        step("discover new artist candidates", lambda: discover_artists.main())

    if not args.skip_scoring:
        step("score candidates (claude CLI)", lambda: score_with_claude.main())

    if not args.skip_events:
        step("scrape upcoming events", lambda: scrape_events.main())

    step("qc thumbnails (refetch + initials fallback)", lambda: qc_images.main())
    step("build daily digest", lambda: build_digest.main())
    step("rebuild dashboard", lambda: build_dashboard.main())

    if not args.skip_push:
        step("git commit + push", lambda: commit_and_push(today))

    logger.info("[done] daily run complete")


if __name__ == "__main__":
    main()
