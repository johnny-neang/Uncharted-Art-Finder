---
description: Refresh the Sacramento artist directory — re-scrape rosters, score new candidates, rebuild dashboard, push to GH Pages
---

Run the daily refresh pipeline for the Sacramento artist directory.

## What this does

1. Re-fetches photos for the 21 canonical artists (only fetches if cache is empty)
2. Scans Wide Open Walls / Branded Arts / Groundswell / KBAA rosters for new artist candidates
3. Scores each new candidate using `claude -p` (your subscription auth)
4. Scrapes upcoming Sacramento art events
5. Builds today's digest at `data/digests/YYYY-MM-DD.md`
6. Rebuilds `index.html`
7. Commits + pushes to the repo so GitHub Pages deploys the update

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
- The live URL: https://johnny-neang.github.io/Uncharted-Art-Finder/

If any step in the pipeline errors, surface that — don't treat it as success. The orchestrator continues past per-step failures by design, so check the log output for `[err]` lines.

If you see Claude returning prose instead of JSON during scoring (a `[name] inner JSON parse failed` warning), the user may have a `Stop` hook in `~/.claude/settings.json` polluting headless calls. Note it in the summary so they can disable the hook before re-running.
