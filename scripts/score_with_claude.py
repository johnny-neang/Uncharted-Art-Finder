"""Score discovered artist candidates using the Claude API.

Reads pending candidates from data/discoveries.json, scores each one with
structured outputs (Pydantic + messages.parse()), writes the scores back
in place. Skips candidates already scored.

Defaults to claude-opus-4-7. Override with CLAUDE_MODEL env var if cost
becomes a concern (e.g. CLAUDE_MODEL=claude-haiku-4-5).
"""
from __future__ import annotations

import argparse
import os
import time
from datetime import date
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

from .common import DATA, load_json, logger, save_json, setup_logging

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-7")

SYSTEM_PROMPT = """You are an art-program advisor for UpperCloud Studio, evaluating artist candidates for the Arden Fair UnchARTed program in Sacramento, California.

PROGRAM CONTEXT
Arden Fair is a regional family-friendly shopping mall in Sacramento. The UnchARTed program commissions local and regional artists for permanent indoor murals and rotating installations. The audience is broad and family-skewing: weekend shoppers, families with children, mall-walking seniors, teens. The program prioritizes Sacramento rooting, visible local pride, and welcoming, conversation-starting work.

YOUR TASK
For each candidate surfaced from a Sacramento gallery roster or press source, decide whether they belong on the working shortlist, and score them on these axes:

1. SACRAMENTO CONNECTION — is this person a Sacramento-area visual artist or art organization? "Yes" = clear local rooting (Sacramento, Davis, Roseville, Folsom, Elk Grove, Yolo/Placer counties). "Unclear" = artist works in CA broadly but Sacramento connection isn't visible. "No" = clearly elsewhere or non-art.

2. FAMILY-MALL FIT (1-5) — would this work read well on a Saturday afternoon at Arden Fair?
   5 = ideal: vibrant, narrative, accessible, civic-minded, family-bright
   4 = strong fit with selective curation
   3 = neutral; depends on which pieces get installed
   2 = challenging; some work could fit but most won't
   1 = wrong context; conceptually pointed, dark, explicit, politically heated, drug-themed, or otherwise mismatched
   The mall is family-friendly, not edgy. Symbolist/dark/macabre work, even when masterful, scores low here. Bright, narrative, figurative, botanical, pop-bright, geometric, or culturally celebratory work scores high.

3. MURAL & SCALE CAPACITY — is there demonstrated large-scale public work?
   "proven" = murals or large public commissions in their portfolio
   "likely" = studio practice that could scale (large canvases, installation work)
   "studio_only" = small-format paintings, photography, illustration
   "unknown" = portfolio not visible enough to judge

4. SUGGESTED TIER:
   Tier 1 — Priority. Named, brand-recognized, proven mural-scale, strong fit. The few you'd commission first.
   Tier 2 — Established. Solid portfolio, locally rooted, would round out the roster.
   Tier 3 — Agency or curator. Not a single artist; a gallery, festival, or art-consulting agency.

5. PROCEED RECOMMENDATION:
   "add" = strong enough to add to the working roster after a cursory human check
   "watch" = interesting; queue for a deeper look but don't commit yet
   "reject" = clear miss (off-geo, wrong medium, wrong context)

6. TAGS — 3-5 short, lowercase, hyphenated descriptors that capture medium and style. Examples: "mural", "studio", "figurative", "abstract", "color-field", "encaustic", "aerosol", "cartoon", "surreal", "botanical", "cultural", "civic", "agency".

7. ONE-LINE SUMMARY — a single sentence (max 160 chars) that captures the artist's signature in our voice: dry, editorial, factual.

Respond only via the structured output schema."""


class CandidateScore(BaseModel):
    sacramento_connection: Literal["yes", "no", "unclear"]
    family_fit: int = Field(ge=1, le=5)
    mural_capacity: Literal["proven", "likely", "studio_only", "unknown"]
    suggested_tier: Literal[1, 2, 3]
    suggested_tags: list[str] = Field(max_length=6)
    one_line_summary: str = Field(max_length=200)
    proceed_recommendation: Literal["add", "watch", "reject"]
    confidence: Literal["low", "medium", "high"]


def score_candidate(client: anthropic.Anthropic, candidate: dict) -> CandidateScore | None:
    """Score one candidate via Claude API with structured output."""
    user_prompt = (
        f"Candidate name: {candidate['name']}\n"
        f"Source URL: {candidate['url']}\n"
        f"Source roster: {candidate['source_name']}\n\n"
        f"This candidate was discovered on a Sacramento gallery/press roster. "
        f"Score them for the Arden Fair UnchARTed program."
    )
    try:
        response = client.messages.parse(
            model=MODEL,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
            output_format=CandidateScore,
        )
        usage = response.usage
        logger.info(
            "  scored %s | in=%d cache_r=%d cache_w=%d out=%d",
            candidate["name"],
            usage.input_tokens,
            usage.cache_read_input_tokens or 0,
            usage.cache_creation_input_tokens or 0,
            usage.output_tokens,
        )
        return response.parsed_output
    except anthropic.AuthenticationError:
        logger.error("Invalid ANTHROPIC_API_KEY")
        raise
    except anthropic.APIError as e:
        logger.warning("Claude API error scoring %s: %s", candidate["name"], e)
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=20, help="max candidates to score per run")
    p.add_argument("--rescore", action="store_true", help="rescore even already-scored candidates")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY env var not set")
        return

    discoveries = load_json(DATA / "discoveries.json", {"candidates": []})
    candidates = discoveries.get("candidates", [])
    if not candidates:
        logger.info("no candidates to score")
        return

    client = anthropic.Anthropic()
    logger.info("scoring with model: %s", MODEL)

    scored_count = 0
    for c in candidates:
        if scored_count >= args.max:
            break
        if c.get("score") and not args.rescore:
            continue

        logger.info("=== %s ===", c["name"])
        score = score_candidate(client, c)
        if score is None:
            continue

        c["score"] = score.model_dump()
        c["scored_at"] = str(date.today())
        c["scored_with"] = MODEL
        scored_count += 1
        # Persist after each scoring so a crash doesn't lose work
        save_json(DATA / "discoveries.json", discoveries)
        time.sleep(0.4)

    logger.info("[done] scored %d candidate(s)", scored_count)


if __name__ == "__main__":
    main()
