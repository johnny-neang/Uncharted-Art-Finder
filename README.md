# Sacramento Artist Directory — UpperCloud Studio

A self-updating dashboard cataloging Sacramento-area artists and art agencies for the Arden Fair UnchARTed program. The pipeline runs **in Claude Code** when you ask for it; the dashboard lives at a public **Vercel URL** so you can show it to anyone, anywhere.

## How you use it

When you want fresh data, open this repo in Claude Code and type:

```
/refresh
```

That kicks off the pipeline — re-scrape rosters, score new candidates against your Claude subscription, scrape upcoming events, rebuild the dashboard, push to the repo. Vercel's git integration auto-deploys within ~30 seconds.

Then visit:

**<https://uncharted-art-finder.vercel.app>**

That's it. No cron, no Mac setup, no API keys. You only run `/refresh` when you actually want fresh data — before a client meeting, when you remember, every couple weeks.

## What the pipeline does

1. **Refreshes roster images** for the 21 canonical artists (re-scrapes their primary site / gallery rep / press page for two representative work photos)
2. **Discovers new artist candidates** from Wide Open Walls, Branded Arts, Groundswell, and Kevin Barry rosters — anyone not already in the canon
3. **Scores each new candidate** by calling Claude headlessly via the `claude` CLI: structured output covering Sacramento connection, family-mall fit, mural capacity, suggested tier, and an `add` / `watch` / `reject` recommendation. **Auth is your existing Pro/Max subscription — no API key, no per-token cost.**
4. **Scrapes upcoming events** from Sacramento365, Wide Open Walls, Crocker Art Museum, Verge
5. **Generates a daily markdown digest** at `data/digests/YYYY-MM-DD.md`
6. **Rebuilds `index.html`** from data files
7. **Commits + pushes** the updated data and dashboard. GitHub Actions takes over from there and deploys to Pages.

## What's here

```
.claude/commands/
  refresh.md                     /refresh slash command — the only thing you invoke
.github/workflows/
  (none — Vercel deploys from main on every push via git integration)
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
index.html                       generated dashboard, served by Pages
requirements.txt                 Python deps (auto-installed in Claude Code sandbox)
requirements-rendered.txt        optional Playwright dep for JS-rendered sources
```

## Optional: JavaScript-rendered sources

Some art sites render their listings client-side and serve a near-empty
shell to plain HTTP fetches. To auto-crawl those, install Playwright into
the venv:

```
.venv/bin/pip install -r requirements-rendered.txt
.venv/bin/playwright install chromium     # ~150MB, one time
```

Sources flagged `requires_js: true` in `data/sources.json` (or per-seed in
`data/manual_seeds.json`) will then use a headless chromium fetch
automatically. Without Playwright the pipeline still runs — those sources
log `[skip-js]` and the rest of the run proceeds normally.

**Limitations.** Headless rendering does *not* bypass anti-bot detection.
Sites that return "Access Denied" or "Just a moment" interstitials to
chromium (e.g. sacopenstudios.org as of 2026-05-26) are caught by the
`[render-block]` check and marked failed. Those stay `manual: true` in
sources.json — browse them by hand and seed interesting profiles via
`data/manual_seeds.json`.

## One-time setup

Already done — the repo is connected to a Vercel project (`uncharted-art-finder`) via git integration. Every push to `main` auto-deploys to <https://uncharted-art-finder.vercel.app>. No GitHub Actions workflow needed.

## Promoting a discovery to the canonical roster

Each `/refresh` run produces a digest summarizing what surfaced — new candidates with `add` / `watch` / `reject` recommendations from Claude. To promote one to the canonical 21-artist roster:

Just ask in Claude Code: *"Promote Maya Vu from discoveries to the roster, tier 2."*

I'll edit `data/artists.json`, remove them from `data/discoveries.json`, and run `/refresh` again. Or you can edit by hand using the existing entries as templates (`slug`, `name`, `tier`, `kind`, `medium`, `tags`, `summary`, `fit`, `suitability`, `primaryUrl`, `primaryHost`, `thumbs`).

## Why this works

- **Claude Code on the web uses your Pro/Max subscription** — same auth as anywhere else you use Claude. The `claude -p` headless invocation in `score_with_claude.py` is just shelling out to the same authenticated CLI.
- **The pipeline is git-native** — all state lives in `data/*.json`. Each run produces a clean diff. History is in the commit log.
- **Vercel hosts it free** on the team plan — gives you a real URL to share with clients, auto-deploys on push via git integration.
- **No infra to maintain** — no Anthropic API key, no cron job, no Supabase, no Mac launchd. The only moving piece is Vercel's git integration, which is configured once and runs forever.

## Brand

UpperCloud Studio editorial style — warm cream paper (#F5F1EA), Iowan Old Style serif headlines, Inter for UI, JetBrains Mono for metadata, with a deep gold (#B68A3F) and atmospheric sky-blue (#466F95) accent system.

---

UpperCloud Studio · Field Brief No. 014
