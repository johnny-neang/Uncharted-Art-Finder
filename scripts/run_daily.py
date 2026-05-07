"""Daily orchestrator. Calls each step in order with sane defaults.

Run on GitHub Actions cron. Locally:

    ANTHROPIC_API_KEY=... python -m scripts.run_daily

Steps:
  1. Refresh roster images for any artist whose cache is stale or empty
  2. Discover new artist candidates from configured rosters
  3. Score each new candidate via Claude API (skips if ANTHROPIC_API_KEY unset)
  4. Scrape upcoming events
  5. Build the digest markdown
  6. Rebuild index.html
  7. Post digest as GitHub Issue (skips if not in CI)
"""
from __future__ import annotations

import argparse
import os
import sys
import traceback
from datetime import date

from .common import logger, setup_logging


def step(name: str, fn):
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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--skip-discover", action="store_true")
    p.add_argument("--skip-events", action="store_true")
    p.add_argument("--skip-scoring", action="store_true")
    p.add_argument("--skip-issue", action="store_true")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    today = str(date.today())
    logger.info("[run] %s", today)

    from . import refresh_images, discover_artists, scrape_events
    from . import score_with_claude, build_digest, post_digest_issue, build_dashboard

    step("refresh roster images", lambda: refresh_images.main())

    if not args.skip_discover:
        step("discover new artist candidates", lambda: discover_artists.main())

    if not args.skip_scoring and os.environ.get("ANTHROPIC_API_KEY"):
        step("score candidates with Claude", lambda: score_with_claude.main())
    else:
        logger.info("[skip] scoring (ANTHROPIC_API_KEY not set or --skip-scoring)")

    if not args.skip_events:
        step("scrape upcoming events", lambda: scrape_events.main())

    step("build daily digest", lambda: build_digest.main())
    step("rebuild dashboard", lambda: build_dashboard.main())

    if not args.skip_issue:
        step("post digest issue", lambda: post_digest_issue.main())

    logger.info("[done] daily run complete")


if __name__ == "__main__":
    main()
