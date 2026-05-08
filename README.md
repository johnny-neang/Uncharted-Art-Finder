# Sacramento Artist Directory — UpperCloud Studio

A self-updating dashboard cataloging Sacramento-area artists and art agencies for the Arden Fair UnchARTed program. The pipeline runs **locally on your Mac**, scoring new candidates against your **Claude Pro/Max subscription** (no API key required), and pushes updated data + a regenerated dashboard to GitHub on each run.

## What it does daily

1. **Refreshes roster images** for the 21 canonical artists (re-scrapes their primary site / gallery rep / press page for two representative work photos)
2. **Discovers new artist candidates** from Wide Open Walls, Branded Arts, Groundswell, and Kevin Barry rosters — anyone not already in the canon
3. **Scores each new candidate** by calling Claude headlessly via the `claude` CLI: structured output covering Sacramento connection, family-mall fit, mural capacity, suggested tier, and an `add` / `watch` / `reject` recommendation
4. **Scrapes upcoming events** from Sacramento365, Wide Open Walls, Crocker Art Museum, Verge
5. **Generates a daily markdown digest** at `data/digests/YYYY-MM-DD.md`
6. **Rebuilds `index.html`** from data files
7. **Commits + pushes** the updated data and dashboard to your repo (GitHub Pages serves it)

## What's here

```
scripts/                         pipeline modules
  common.py                      shared HTTP / image / path helpers
  refresh_images.py              re-fetches photos for the canonical roster
  discover_artists.py            scans rosters for new artist candidates
  scrape_events.py               scrapes Sacramento art-event calendars
  score_with_claude.py           Claude Code CLI scoring (subscription auth)
  build_dashboard.py             renders index.html from data/
  build_digest.py                daily markdown digest
  run_daily.py                   orchestrator
data/
  artists.json                   canonical roster (21 artists/agencies)
  artist_images.json             cached photos (base64 data URIs)
  discoveries.json               queue of new candidates with Claude scores
  events.json                    upcoming events
  sources.json                   config: which URLs to scan
  digests/YYYY-MM-DD.md          daily digest archive
templates/
  dashboard.html.tmpl            HTML template with {{...}} markers
  svg_library.js                 hand-tuned SVG illustrations (fallback art)
  launchagent.plist.tmpl         launchd schedule template
index.html                       generated dashboard
run-daily.sh                     wrapper invoked by launchd or you
setup.sh                         one-time local install
requirements.txt                 Python deps
```

## One-time setup

Prerequisites:

- macOS
- **Python 3.11+** (`brew install python` if missing)
- **Claude Code** with you logged in via `claude login` — the pipeline uses your existing Pro/Max subscription, no API key required. Install: <https://claude.ai/code>
- **git** with push access to this repo (you already have this)

Then:

```bash
git clone <your-repo-url>
cd Uncharted-Art-Finder
./setup.sh
```

The setup script will:

1. Verify `python3` is available
2. Create a `.venv/` and install dependencies
3. Make `run-daily.sh` executable
4. Check that `claude` is on PATH
5. Optionally install a **launchd agent** that runs `run-daily.sh` daily at 9am

If launchd is enabled, the pipeline runs every morning. If your Mac is asleep at 9am, launchd runs it as soon as the Mac wakes.

## Running it manually

Any time:

```bash
./run-daily.sh
```

To skip steps while iterating:

```bash
./run-daily.sh --skip-discover --skip-events --skip-scoring --skip-push
```

To rebuild just `index.html` from existing data:

```bash
.venv/bin/python -m scripts.build_dashboard
```

To score the discovery queue without doing anything else:

```bash
.venv/bin/python -m scripts.score_with_claude
```

## Logs

If the launchd agent is running, output goes to:

```
~/Library/Logs/uppercloud-daily-digest.log
```

Tail it with `tail -f ~/Library/Logs/uppercloud-daily-digest.log`.

## Promoting a discovery to the roster

Every morning the pipeline writes `data/digests/YYYY-MM-DD.md` summarizing what surfaced — new candidates, scored, with `add` / `watch` / `reject` recs. To promote one to the canonical roster:

1. Open `data/artists.json`
2. Add a new entry (use the existing entries as templates — `slug`, `name`, `tier`, `kind`, `medium`, `tags`, `summary`, `fit`, `suitability`, `primaryUrl`, `primaryHost`, `thumbs`)
3. Optionally remove the matching entry from `data/discoveries.json`
4. Optionally add the artist's slug to `PAGES_BY_SLUG` in `scripts/refresh_images.py` so future runs refresh their images
5. The next run rebuilds the dashboard with them included.

## How scoring works

`scripts/score_with_claude.py` invokes:

```bash
claude -p "<artist info>" \
  --system-prompt "<curation rubric, JSON-only output instruction>" \
  --tools "" \
  --no-session-persistence \
  --output-format json
```

`--tools ""` disables all of Claude Code's built-in tools so the call is pure text-in / JSON-out — no shell, no edits, no MCP. The response goes into the wrapped JSON envelope; the script parses the inner JSON, validates against a Pydantic schema, and stores it on the candidate. Failures (parse errors, timeout, refusals) leave the candidate unscored — the next run retries.

Each scoring call costs whatever your subscription contract specifies — typically a few tenths of a cent — but is fully covered by your Pro/Max plan, with no per-token API charges.

If `claude` isn't on your PATH, scoring is skipped and the rest of the pipeline still runs. Other steps (image refresh, discovery, events, digest, dashboard) don't depend on it.

## Brand

UpperCloud Studio editorial style — warm cream paper (#F5F1EA), Iowan Old Style serif headlines, Inter for UI, JetBrains Mono for metadata, with a deep gold (#B68A3F) and atmospheric sky-blue (#466F95) accent system.

---

UpperCloud Studio · Field Brief No. 014 · Self-updating since 2026
