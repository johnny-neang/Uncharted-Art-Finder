---
description: Refresh the Sacramento artist directory — re-scrape rosters, score new candidates, rebuild dashboard, push (Vercel auto-deploys)
---

Run the daily refresh pipeline for the Sacramento artist directory.

## What this does

1. Fetches photos for any directory artist still missing 2 photos — artists already holding 2 cached photos are skipped, so existing artists/organizations are never re-scraped
2. Scans Wide Open Walls / Branded Arts / Groundswell / KBAA rosters for new artist candidates
3. Scores each new candidate using `claude -p` (your subscription auth)
4. Scrapes upcoming Sacramento art events
5. Builds today's digest at `data/digests/YYYY-MM-DD.md`
6. Rebuilds `index.html`
7. Commits + pushes to the repo; Vercel's git integration auto-deploys within ~30 seconds

## Photo sourcing (every artist gets 2 real photographs)

Image discovery is layered. For each artist/candidate the pipeline tries the **free** sources first, in order, and only falls through to the **paid** Apify tier once they've all come up short — until it has 2 unique real photos:

1. **Manual overrides** (free) — hand-curated URLs in `data/manual_artist_photos.json` (per slug)
2. **Instagram, free tier** — public profile rendered via Playwright; handles live in `data/instagram_handles.json`
3. **Page crawl** (free) — the artist's primary URL + sub-pages (multi-page, with a Playwright render fallback for lazy-loaded sites)
4. **Wayback Machine** (free) — for primary URLs that 404/timeout
5. **Instagram via Apify (paid BACKUP, last resort)** — the Apify Instagram scraper actor, invoked **only** after every free source above has failed to reach 2 photos **and** the `APIFY` env var is set. ~$0.20/profile. Used sparingly: it fires **at most once per artist** (every attempt is logged to `data/apify_attempts.json`) and **never for an artist whose photos are already complete**, so it never re-runs on existing artists. Pass `--apify-retry` to `refresh_images` to deliberately re-attempt artists already in that ledger.

Rules of the road, non-negotiable:
- **Only real photographs of the artist's work.** Never AI-generated, never interpretive SVG, never initials avatars. If 2 real photos can't be found, the slot renders a plain "Researching second photo" text placeholder — never fabricated imagery.
- **Apify is a last-resort backup, never the default.** The free tiers handle the vast majority. The pipeline exhausts every free source — free IG render, page crawl, Wayback — before it ever spends a cent on Apify, so a free method that *would* have found the photo always wins. Apify exists because Instagram periodically breaks the logged-out grid; it keeps recurring runs producing photos without hand-fixing the scraper. It silently no-ops when `APIFY` is unset, so an unset token simply skips the tier.
- **Spend stays bounded.** The daily cron runs without `--force`, so complete artists are skipped entirely, and the per-artist ledger means a stubborn artist costs at most one paid call ever (until you run `--apify-retry`). A persistently-hard artist is tried once, recorded, then left to the free tiers on every later run.

The `APIFY` token is read from the process environment, with a gitignored repo-root `.env` file (`APIFY=...`) as a fallback that never overrides an already-set env var. It must be present **wherever the scraper actually runs** — it is *not* read on Vercel (Vercel only serves the built site):
- **GitHub Actions daily cron** → add a repo secret `APIFY` (`gh secret set APIFY`); the workflow already passes it through.
- **Local `/refresh`** → put `APIFY=...` in the repo-root `.env`, or export it in your shell before running.

## Steps

Execute the orchestrator:

```bash
python3 -m scripts.run_daily
```

Then read today's digest at `data/digests/$(date -u +%Y-%m-%d).md` and summarize for the user in 4–6 lines:
- New candidates surfaced today (with names + recommendations)
- Add-worthy candidates this run, if any
- Roster image refresh stats (refreshed vs fell back to SVG)
- Number of upcoming events tracked
- The live URL: https://uncharted-art-finder.vercel.app

If any step in the pipeline errors, surface that — don't treat it as success. The orchestrator continues past per-step failures by design, so check the log output for `[err]` lines.

If you see Claude returning prose instead of JSON during scoring (a `[name] inner JSON parse failed` warning), the user may have a `Stop` hook in `~/.claude/settings.json` polluting headless calls. Note it in the summary so they can disable the hook before re-running.
