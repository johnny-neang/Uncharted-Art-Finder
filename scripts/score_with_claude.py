"""Score discovered artist candidates using the local Claude Code CLI.

Calls `claude -p` headlessly so scoring runs against the user's existing
Claude subscription auth (Pro/Max). No ANTHROPIC_API_KEY needed.

If `claude` isn't on PATH the step is skipped without failing the run.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from .common import DATA, load_json, logger, save_json, setup_logging

CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")
TIMEOUT_S = int(os.environ.get("CLAUDE_TIMEOUT", "120"))


class CandidateScore(BaseModel):
    sacramento_connection: Literal["yes", "no", "unclear"]
    family_fit: int = Field(ge=1, le=5)
    mural_capacity: Literal["proven", "likely", "studio_only", "unknown"]
    suggested_tier: Literal[1, 2, 3]
    suggested_tags: list[str] = Field(max_length=6)
    one_line_summary: str = Field(max_length=240)
    proceed_recommendation: Literal["add", "watch", "reject"]
    confidence: Literal["low", "medium", "high"]
    # New fields (added 2026-05-27) — populate the directory-style rich card
    # when a candidate is rendered alongside canonical roster entries.
    kind: str = Field(max_length=80)
    medium: str = Field(max_length=120)
    suitability: str = Field(max_length=240)


SYSTEM_PROMPT = """You are an evaluation tool for UpperCloud Studio's Sacramento Artist Directory — the curation pipeline for Arden Fair UnchARTed, a public-art program at a family-friendly Sacramento mall.

Score each candidate on these axes:

- sacramento_connection: "yes" (Sacramento area = Sacramento, Davis, Roseville, Folsom, Elk Grove, Yolo/Placer counties) | "unclear" | "no"
- family_fit: integer 1-5. 5 = vibrant, narrative, family-bright. 1 = dark/macabre/explicit/politically heated/drug-themed. The mall is family-friendly, not edgy.
- mural_capacity: "proven" (large public work in portfolio) | "likely" | "studio_only" | "unknown"
- suggested_tier: 1 (priority — proven, brand-recognized, ideal fit) | 2 (established) | 3 (agency/curator, not a single artist)
- suggested_tags: 3-5 short lowercase hyphenated tags (e.g. "mural", "abstract", "encaustic", "figurative", "botanical")
- one_line_summary: dry editorial sentence, max 200 chars
- proceed_recommendation: "add" (strong roster fit) | "watch" (interesting, queue) | "reject" (off-fit)
- confidence: "low" | "medium" | "high"

Three additional fields render the candidate alongside the canonical directory entries — use the same editorial idiom as these existing examples from the roster:

- kind: a short noun phrase classifying the entity. Pattern: "<Role> · <Locale>". Examples from the roster: "Artist · Sacramento", "Studio · Sacramento + Yountville", "Agency · Public Art Sacramento". Use the inferred locale; if unknown, write "Artist" or "Studio" alone. Max 80 chars.
- medium: a short ` · `-separated list of primary working media, max 3-4 items. Examples: "Mural · Mixed-media on canvas · Glass installation", "Mural · Resin · Encaustic", "Public art · Sculpture". Title-case each term. Max 120 chars.
- suitability: a 1-2 sentence editorial paragraph (dry, declarative, no marketing language) explaining how this artist fits or doesn't fit the Arden Fair UnchARTed program. Examples: "Native to the program. Returning artist would anchor any 2026 cycle.", "Naturalistic motifs and warm palette read well in family-retail. Proven scale.", "Studio-scale practice; would need a commission liaison for mall-scale public work." Max 240 chars.

Respond with EXACTLY ONE JSON object matching this schema and nothing else — no prose, no preamble, no markdown fences. Use only the literal values listed above."""


def claude_available() -> bool:
    return shutil.which(CLAUDE_BIN) is not None


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        # remove first ``` line and trailing ```
        lines = text.split("\n")
        if lines[-1].strip().startswith("```"):
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        text = "\n".join(lines).strip()
    return text


def score_candidate(c: dict) -> CandidateScore | None:
    # Include any context we already harvested (OG description from manual
    # seeds, or seed notes the user added). These often resolve Claude's
    # "sacramento: unclear" guess into a confirmed yes.
    extra_lines = []
    if c.get("seed_description"):
        extra_lines.append(f"Page description: {c['seed_description']}")
    if c.get("seed_note"):
        extra_lines.append(f"Submitter note: {c['seed_note']}")
    extras = ("\n" + "\n".join(extra_lines)) if extra_lines else ""

    user_prompt = (
        f"Artist: {c['name']}\n"
        f"URL: {c['url']}\n"
        f"Source roster: {c['source_name']}"
        f"{extras}\n\n"
        f"Score this candidate for the Arden Fair UnchARTed program."
    )
    try:
        result = subprocess.run(
            [
                CLAUDE_BIN,
                "-p", user_prompt,
                "--system-prompt", SYSTEM_PROMPT,
                "--tools", "",
                "--no-session-persistence",
                "--output-format", "json",
            ],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        logger.warning("[%s] claude timed out after %ds", c["name"], TIMEOUT_S)
        return None
    except FileNotFoundError:
        logger.warning("`%s` not found on PATH", CLAUDE_BIN)
        return None

    if result.returncode != 0:
        logger.warning("[%s] claude exited %d: %s", c["name"], result.returncode, result.stderr[:300])
        return None

    try:
        envelope = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        logger.warning("[%s] outer JSON parse failed: %s", c["name"], e)
        return None

    if envelope.get("is_error"):
        logger.warning("[%s] claude returned is_error: %s", c["name"], envelope.get("result", "")[:200])
        return None

    inner_text = _strip_fences(envelope.get("result", ""))
    try:
        inner = json.loads(inner_text)
        score = CandidateScore.model_validate(inner)
        cost = envelope.get("total_cost_usd", 0) or 0
        logger.info("  %s -> %s (fit %d, tier %d) [$%.4f]",
                    c["name"], score.proceed_recommendation, score.family_fit,
                    score.suggested_tier, cost)
        return score
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning("[%s] inner JSON parse failed: %s | text=%r", c["name"], e, inner_text[:200])
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=20, help="max candidates to score per run")
    p.add_argument("--rescore", action="store_true", help="rescore even already-scored candidates")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    if not claude_available():
        logger.warning("`%s` not on PATH — skipping scoring step. Install Claude Code (https://claude.ai/code) and run `claude login` to enable.", CLAUDE_BIN)
        return

    discoveries = load_json(DATA / "discoveries.json", {"candidates": []})
    candidates = discoveries.get("candidates", [])
    if not candidates:
        logger.info("no candidates to score")
        return

    # Honor manual overrides — never re-score these, and add reject/existing
    # to rejected_slugs so future discovery passes skip them.
    rejected = set(discoveries.get("rejected_slugs", []))
    for c in candidates:
        # archive is the new name for "existing"; treat both as terminal
        if c.get("manual_override") in ("reject", "existing", "archive"):
            rejected.add(c["slug"])
    discoveries["rejected_slugs"] = sorted(rejected)

    scored_count = 0
    for c in candidates:
        if scored_count >= args.max:
            break
        if c.get("manual_override"):
            logger.info("[skip] %s (manual_override=%s)", c["name"], c["manual_override"])
            continue
        if c.get("score") and not args.rescore:
            continue

        logger.info("=== %s ===", c["name"])
        score = score_candidate(c)
        if score is None:
            continue

        c["score"] = score.model_dump()
        c["scored_at"] = str(date.today())
        c["scored_with"] = "claude-code-cli"
        scored_count += 1
        save_json(DATA / "discoveries.json", discoveries)
        time.sleep(0.4)

    save_json(DATA / "discoveries.json", discoveries)  # persist rejected_slugs even if 0 scored
    logger.info("[done] scored %d candidate(s)", scored_count)


if __name__ == "__main__":
    main()
