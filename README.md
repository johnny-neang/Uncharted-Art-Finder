# Sacramento Artist Directory — UpperCloud Studio

A self-updating, Pages-served dashboard cataloging Sacramento-area artists and art agencies for the Arden Fair UnchARTed program. Refreshes itself daily via GitHub Actions: re-fetches artist images, scans local rosters and press for new candidates, scores each with the Claude API, scrapes upcoming events, and posts a digest issue.

## What's here

```
.github/workflows/daily-digest.yml   the cron job (08:00 UTC daily)
scripts/                             the pipeline
  common.py                          shared HTTP / image / path helpers
  refresh_images.py                  re-fetches photos for the canonical roster
  discover_artists.py                scans rosters for new artist candidates
  scrape_events.py                   scrapes Sacramento art-event calendars
  score_with_claude.py               Claude API scoring of new candidates
  build_dashboard.py                 renders index.html from data/
  build_digest.py                    daily markdown digest
  post_digest_issue.py               posts digest as a GitHub Issue
  run_daily.py                       orchestrator that calls every step
data/
  artists.json                       canonical roster (21 artists/agencies)
  artist_images.json                 cached photos (base64 data URIs)
  discoveries.json                   queue of new candidates with Claude scores
  events.json                        upcoming events
  sources.json                       config: which URLs to scan
  digests/YYYY-MM-DD.md              daily digest archive
templates/
  dashboard.html.tmpl                HTML template with {{...}} markers
  svg_library.js                     42 hand-tuned SVG illustrations (fallback art)
index.html                           generated dashboard, served by GitHub Pages
requirements.txt                     Python deps
```

## One-time setup

The pipeline runs entirely on GitHub's runners — you don't need anything installed locally. Two clicks in repo settings:

### 1. Add the Anthropic API key

**Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your API key from console.anthropic.com |

The default model is **`claude-opus-4-7`**. To use a cheaper model, add a repo *variable* (not a secret):

**Settings → Secrets and variables → Actions → Variables → New repository variable**

| Name | Value |
|---|---|
| `CLAUDE_MODEL` | `claude-haiku-4-5` (or `claude-sonnet-4-6`) |

Cost note: at default settings (10 candidates/day × ~500 tokens) the daily Claude spend is on the order of pennies on Opus 4.7 and fractions of a cent on Haiku 4.5.

### 2. Enable GitHub Pages

**Settings → Pages → Build and deployment → Source: GitHub Actions**

The workflow handles the deployment itself. After the first run, the dashboard is live at:

```
https://<your-username>.github.io/<repo-name>/
```

## What runs daily

08:00 UTC every day (midnight Pacific PDT, 1am Pacific PST). The workflow:

1. **Refreshes roster images** — for each of the 21 canonical artists, scrapes their primary site / gallery rep / press page for two representative work photos, downloads, resizes to ~480px, base64-embeds.
2. **Discovers new artists** — scans Wide Open Walls / Branded Arts / Groundswell / Kevin Barry's roster pages, extracts candidate names + URLs, dedupes against the canonical roster, queues new ones with one image each.
3. **Scores discoveries with Claude** — every new candidate gets passed through Claude (Opus 4.7 by default) for a structured fit score: Sacramento connection, family-mall fit (1-5), mural capacity, suggested tier, suggested tags, one-line summary, and an `add` / `watch` / `reject` recommendation.
4. **Scrapes events** — pulls upcoming arts events from Sacramento365, Wide Open Walls, Crocker Art Museum, and Verge.
5. **Builds the daily digest** — markdown summary at `data/digests/YYYY-MM-DD.md`, posted as a GitHub Issue tagged `digest`.
6. **Rebuilds `index.html`** from data files.
7. **Commits + pushes** — workflow runs as `github-actions[bot]`. Then re-deploys Pages.

You wake up; you have a notification on a `digest` issue summarizing what surfaced. If a new candidate looks worth adding to the roster, edit `data/artists.json` and push — the next daily run will re-render the dashboard with them included.

## Manual trigger

You can also trigger the workflow on demand:

**Actions → Daily artist digest → Run workflow**

## Local development

If you want to run the pipeline locally:

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python -m scripts.run_daily
```

To skip steps (helpful when iterating):

```bash
python -m scripts.run_daily --skip-discover --skip-scoring --skip-events --skip-issue
```

To rebuild the dashboard from existing data files only:

```bash
python -m scripts.build_dashboard
```

## Promoting a discovery to the roster

When a `digest` issue surfaces a candidate worth adding:

1. Open `data/artists.json`
2. Add a new entry (use the existing entries as templates — you'll need `slug`, `name`, `tier`, `kind`, `medium`, `tags`, `summary`, `fit`, `suitability`, `primaryUrl`, `primaryHost`, `thumbs`)
3. Optionally remove the matching entry from `data/discoveries.json`
4. Optionally add the artist's slug to `PAGES_BY_SLUG` in `scripts/refresh_images.py` so future runs refresh their images
5. Commit + push. The next daily run rebuilds the dashboard with them.

## Brand

UpperCloud Studio editorial style — warm cream paper (#F5F1EA), Iowan Old Style serif headlines, Inter for UI, JetBrains Mono for metadata, with a deep gold (#B68A3F) and atmospheric sky-blue (#466F95) accent system.

---

UpperCloud Studio · Field Brief No. 014 · Self-updating since 2026
