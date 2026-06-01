"""Apply agent-produced candidate scores to discoveries.json.

Because the /refresh skill is run by Claude directly, scoring happens in the
agent's own context (no headless `claude -p`, no separate CLI auth). The agent
produces a JSON object of {slug: <score fields>} and this script validates each
against the CandidateScore schema and merges it in. Same schema/result shape as
the old CLI path — only the producer changed — so build_digest / build_dashboard
consume it unchanged.

  python -m scripts.apply_scores scores.json
  python -m scripts.apply_scores -            # read JSON from stdin

Input shape:
  { "some-slug": { "sacramento_connection": "yes", "family_fit": 4, ... }, ... }
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from pydantic import ValidationError

from .common import DATA, load_json, logger, save_json, setup_logging
from .score_with_claude import CandidateScore  # single source of truth for the schema


def main():
    p = argparse.ArgumentParser()
    p.add_argument("scores", help="path to a JSON {slug: score} file, or - for stdin")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    raw = sys.stdin.read() if args.scores == "-" else open(args.scores, encoding="utf-8").read()
    try:
        scores = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("[apply-scores] input is not valid JSON: %s", e)
        sys.exit(1)
    if not isinstance(scores, dict):
        logger.error("[apply-scores] expected a JSON object {slug: {...}}, got %s", type(scores).__name__)
        sys.exit(1)

    discoveries = load_json(DATA / "discoveries.json", {"candidates": []}) or {"candidates": []}
    by_slug = {c.get("slug"): c for c in discoveries.get("candidates", [])}

    applied = errors = skipped = 0
    for slug, sc in scores.items():
        c = by_slug.get(slug)
        if not c:
            logger.warning("[skip] no candidate with slug %r", slug)
            skipped += 1
            continue
        if c.get("manual_override"):
            logger.info("[skip] %s has manual_override=%s — not overwriting", slug, c["manual_override"])
            skipped += 1
            continue
        try:
            validated = CandidateScore.model_validate(sc)
        except ValidationError as e:
            logger.error("[err] %s: invalid score — %s", slug, str(e).replace("\n", " ")[:240])
            errors += 1
            continue
        c["score"] = validated.model_dump()
        c["scored_at"] = str(date.today())
        c["scored_with"] = "claude-code-agent"
        applied += 1
        logger.info("  %s -> %s (fit %d, tier %d)", slug,
                    validated.proceed_recommendation, validated.family_fit, validated.suggested_tier)

    save_json(DATA / "discoveries.json", discoveries)
    logger.info("[apply-scores done] applied=%d errors=%d skipped=%d", applied, errors, skipped)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
