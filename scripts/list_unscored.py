"""List candidates that still need a score — input for in-agent scoring.

The /refresh skill is executed by Claude directly, so scoring is done by the
agent in-context (using the rubric in the skill) instead of shelling out to a
headless `claude -p`. This prints compact JSON of the candidates that need a
score — just the fields needed to score them — which the agent reads, scores,
and writes back via scripts.apply_scores.

  python -m scripts.list_unscored            # all unscored candidates
  python -m scripts.list_unscored --max 10   # cap the batch
"""
from __future__ import annotations

import argparse
import json

from .common import DATA, load_json, logger, setup_logging


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=25, help="max candidates to emit")
    p.add_argument("--log", default="WARNING")
    args = p.parse_args()
    setup_logging(args.log)

    discoveries = load_json(DATA / "discoveries.json", {"candidates": []}) or {}
    out = []
    for c in discoveries.get("candidates", []):
        # Skip ones the user has ruled on, and ones already scored.
        if c.get("manual_override") or c.get("score"):
            continue
        out.append({
            "slug": c.get("slug"),
            "name": c.get("name"),
            "url": c.get("url"),
            "source_name": c.get("source_name"),
            "seed_description": c.get("seed_description"),
            "seed_note": c.get("seed_note"),
        })
        if len(out) >= args.max:
            break

    logger.info("[list-unscored] %d candidate(s) need a score", len(out))
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
