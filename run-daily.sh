#!/bin/bash
# Wrapper invoked by launchd (or manually). Runs the daily pipeline with the
# repo's venv if one exists, falling back to system python3.
#
# launchd's PATH is minimal, so we explicitly add the locations where Homebrew,
# pyenv, nvm, and Claude Code typically live.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.nvm/versions/node/$(ls -1 $HOME/.nvm/versions/node 2>/dev/null | tail -1)/bin:$HOME/.local/bin:$PATH"

# Use the repo's venv if it exists
if [ -x "$REPO_DIR/.venv/bin/python3" ]; then
  PY="$REPO_DIR/.venv/bin/python3"
else
  PY="$(command -v python3 || true)"
fi

if [ -z "$PY" ]; then
  echo "[run-daily] python3 not found on PATH" >&2
  exit 1
fi

echo "[run-daily] $(date) — using $PY"
exec "$PY" -m scripts.run_daily "$@"
