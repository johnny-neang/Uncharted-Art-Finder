---
description: Refresh the Sacramento artist directory — re-scrape rosters, score new candidates, rebuild dashboard, push (Vercel auto-deploys)
---

Run the daily refresh pipeline for the Sacramento artist directory.

## What this does

1. Fetches photos for any directory artist still missing 2 photos — artists already holding 2 cached photos are skipped, so existing artists/organizations are never re-scraped
2. Scans Wide Open Walls / Branded Arts / Groundswell / KBAA rosters for new artist candidates
3. Scores each new candidate **in-context** — Claude, running this skill, scores them directly (no headless `claude -p`, no separate CLI auth)
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

Scoring is done by **you** (Claude, executing this skill) in-context — do **not** shell out to `claude -p` (it needs separate CLI auth and was failing with a 401). Run the pipeline, score the candidates yourself, then rebuild and push. Use the repo venv (`./.venv/bin/python`) so dependencies resolve.

0. **Reconcile with `origin` FIRST — before running anything.** A daily GitHub Actions cron (`Daily data refresh · <date>`) and dashboard promote/demote commits push to `main` independently of you. If you run the local pipeline on a stale base and then rebase, you will (a) re-scrape artists the cron already completed today and (b) burn paid Apify calls if a transient local DNS blip makes the free image tiers look "empty" — exactly the spend the rules forbid. So always start by syncing:

   ```bash
   git fetch origin && git log --oneline HEAD..origin/main
   ```

   - **If `origin/main` already contains a `Daily data refresh · <today>` commit** (the cron beat you to it), the day's scraping is already done and authoritative. Do **NOT** re-run `run_daily`. Instead: `git reset --hard origin/main`, then go straight to **step 2** (score) → **step 3** (rebuild) → **step 4** (push). This is the common case for an afternoon/evening `/refresh`.
   - **If `origin/main` has only dashboard commits (or nothing) since your last sync**, fast-forward first (`git reset --hard origin/main` if you have no local commits, else `git pull --rebase --autostash`), *then* run the full pipeline in step 1. Running on the current roster matters — discovery/QC must see the latest promotions/demotions.
   - Never let the local pipeline's output overwrite the cron's same-day image/event data. When in doubt, the cron is authoritative for `artist_images.json` and `events.json`; you are authoritative only for the **scores** you add to `discoveries.json`.

1. **Run the pipeline** — everything except scoring and the push (skip this step if step 0 told you the cron already refreshed today):

   ```bash
   ./.venv/bin/python -m scripts.run_daily --skip-scoring --skip-push
   ```

   Watch the `apify_paid=` line in the `[done] refreshed=…` summary. If it's **non-zero**, confirm it was a genuinely photo-less artist and not a network/DNS failure faking out the free tiers — a burst of `[err] … Failed to resolve '…'` lines immediately before Apify fires means your local DNS dropped and the paid calls were wasted; abort, `git reset --hard origin/main`, and retry once the network is healthy rather than committing DNS-induced Apify spend.

2. **Score new candidates yourself.** List the ones that need a score:

   ```bash
   ./.venv/bin/python -m scripts.list_unscored
   ```

   For each candidate in that JSON, produce one score object matching the schema in **Scoring rubric** below. Collect them into a single `{ "slug": { …score… }, … }` object, write it to a temp file, and apply it (validated against the schema):

   ```bash
   ./.venv/bin/python -m scripts.apply_scores /tmp/scores.json
   ```

   If `list_unscored` returns `[]`, skip this step. `apply_scores` never overwrites a candidate that has a `manual_override`.

3. **Rebuild** the digest + dashboard so they reflect the new scores:

   ```bash
   ./.venv/bin/python -m scripts.build_digest && ./.venv/bin/python -m scripts.build_dashboard
   ```

4. **Commit + push** (Vercel auto-deploys from `main` within ~30s):

   ```bash
   git add data/ index.html && git commit -m "Daily refresh · $(date -u +%Y-%m-%d)" && git pull --rebase --autostash && git push
   ```

   **If the rebase hits a conflict, mind the inverted `--ours`/`--theirs` semantics.** During a rebase your commit is replayed *on top of* `origin/main`, so git's labels flip from what you'd expect: **`--ours` = the upstream cron/dashboard commit**, **`--theirs` = your local refresh work**. Getting this backwards silently drops your scores (and once did). Resolve per-file by intent, not by guessing the flag:
   - `data/discoveries.json`, `data/artists.json` → keep **your** version (`git checkout --theirs <file>`) — it carries the scores you just applied; the cron only bumps `last_run` here.
   - `data/artist_images.json`, `data/events.json` → keep the **cron's** version (`git checkout --ours <file>`) — it is authoritative for images/events.
   - `index.html` → never trust either side of an auto-merge; after resolving the data files, **rebuild it** (`./.venv/bin/python -m scripts.build_dashboard`) so it reflects the merged data, then `git add` everything and `GIT_EDITOR=true git rebase --continue`.
   - Then `git push`. If a *new* cron commit landed during resolution, repeat.

Then read today's digest at `data/digests/$(date -u +%Y-%m-%d).md` and summarize for the user in 4–6 lines:
- New candidates surfaced today (with names + recommendations)
- Add-worthy candidates this run, if any
- Roster image refresh stats (refreshed vs placeholdered)
- Number of upcoming events tracked
- The live URL: https://uncharted-art-finder.vercel.app

If any step errors, surface it — don't treat it as success. `run_daily` continues past per-step failures by design, so check the log for `[err]` lines, plus `apify_paid=` / `[qc-apify]` lines to confirm Apify stayed a last resort.

## Scoring rubric

You are scoring each candidate for UpperCloud Studio's Sacramento Artist Directory — the curation pipeline for **Arden Fair UnchARTed**, a public-art program at a family-friendly Sacramento mall. Produce **exactly one JSON object per candidate** with these fields (literal values only):

- `sacramento_connection`: `"yes"` (Sacramento area — Sacramento, Davis, Roseville, Folsom, Elk Grove, Yolo/Placer counties) | `"unclear"` | `"no"`
- `family_fit`: integer 1–5. 5 = vibrant, narrative, family-bright. 1 = dark/macabre/explicit/politically heated/drug-themed (the mall is family-friendly, not edgy).
- `mural_capacity`: `"proven"` (large public work in portfolio) | `"likely"` | `"studio_only"` | `"unknown"`
- `suggested_tier`: `1` (priority — proven, brand-recognized, ideal fit) | `2` (established) | `3` (agency/curator, not a single artist)
- `suggested_tags`: 3–5 short lowercase hyphenated tags (e.g. `"mural"`, `"abstract"`, `"encaustic"`, `"figurative"`, `"botanical"`)
- `one_line_summary`: dry editorial sentence, ≤200 chars
- `proceed_recommendation`: `"add"` (strong roster fit) | `"watch"` (interesting, queue) | `"reject"` (off-fit)
- `confidence`: `"low"` | `"medium"` | `"high"`
- `kind`: `"<Role> · <Locale>"`, e.g. `"Artist · Sacramento"`, `"Agency · Public Art Sacramento"`. If locale unknown, `"Artist"` or `"Studio"` alone. ≤80 chars
- `medium`: ` · `-separated primary media, 3–4 items, Title-Case, e.g. `"Mural · Mixed-media on canvas · Glass installation"`. ≤120 chars
- `suitability`: 1–2 dry, declarative sentences on fit for the family-retail public-art program. ≤240 chars

Score honestly on fit. If you're genuinely unsure of the Sacramento tie, use `"unclear"` rather than guessing `"yes"`. A candidate's `manual_override` (set by the user) always takes precedence and is preserved automatically.
