#!/bin/bash
# One-time local setup for the UpperCloud daily digest pipeline.
#
# Creates a Python venv, installs deps, makes run-daily.sh executable,
# and (optionally) installs a launchd job that runs the pipeline daily at 9am.
#
# Idempotent: safe to re-run.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

# ---------- pretty ----------
GREEN=$'\033[0;32m'; YELLOW=$'\033[0;33m'; RED=$'\033[0;31m'; RESET=$'\033[0m'
ok()   { echo "${GREEN}✓${RESET} $*"; }
warn() { echo "${YELLOW}!${RESET} $*"; }
fail() { echo "${RED}✗${RESET} $*"; exit 1; }
hdr()  { echo; echo "─── $* ───"; }

# ---------- 1. Python ----------
hdr "Python"
if ! command -v python3 >/dev/null 2>&1; then
  fail "python3 not found. Install via 'brew install python' or python.org and re-run."
fi
PY_VERSION=$(python3 --version 2>&1)
ok "found $PY_VERSION"

# ---------- 2. venv + deps ----------
hdr "Python virtualenv & dependencies"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  ok "created .venv"
else
  ok ".venv already present"
fi
# shellcheck source=/dev/null
source .venv/bin/activate
python3 -m pip install --upgrade pip --quiet
python3 -m pip install -r requirements.txt --quiet
ok "installed requirements.txt into .venv"
deactivate

# ---------- 3. wrapper script ----------
hdr "Wrapper script"
chmod +x run-daily.sh
ok "made run-daily.sh executable"

# ---------- 4. Claude Code ----------
hdr "Claude Code CLI (for scoring)"
if command -v claude >/dev/null 2>&1; then
  ok "claude CLI found at $(command -v claude)"
  echo
  echo "  If you haven't yet logged into your Claude subscription:"
  echo "    claude login"
  echo
  echo "  Test scoring works headlessly:"
  echo "    claude -p 'say JSON: {\"ok\": true}' --tools '' --no-session-persistence --output-format json"
else
  warn "claude CLI not found."
  echo
  echo "  Install Claude Code: https://claude.ai/code"
  echo "  Then run 'claude login' to authenticate with your subscription."
  echo
  echo "  The pipeline will still run without it — scoring will simply skip."
fi

# ---------- 5. launchd job ----------
hdr "Daily schedule (launchd)"
echo "Install a launchd agent that runs the pipeline daily at 9am? [y/N]"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST_PATH="$PLIST_DIR/studio.uppercloud.daily-digest.plist"
  mkdir -p "$PLIST_DIR"
  mkdir -p "$HOME/Library/Logs"

  sed \
    -e "s|__REPO__|$REPO_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    templates/launchagent.plist.tmpl > "$PLIST_PATH"
  ok "wrote $PLIST_PATH"

  if launchctl list | grep -q studio.uppercloud.daily-digest; then
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
  fi
  launchctl load "$PLIST_PATH"
  ok "loaded launchd agent"
  echo
  echo "  Manual run any time:    ./run-daily.sh"
  echo "  Inspect logs:           tail -f ~/Library/Logs/uppercloud-daily-digest.log"
  echo "  Reschedule (e.g. 8am):  edit templates/launchagent.plist.tmpl, re-run setup.sh"
  echo "  Disable:                launchctl unload $PLIST_PATH"
else
  echo "  Skipped. Run the pipeline manually whenever:"
  echo "    ./run-daily.sh"
fi

hdr "Done"
ok "Setup complete. First run:"
echo "    ./run-daily.sh"
