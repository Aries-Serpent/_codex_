#!/usr/bin/env bash
# Simple virtualenv bootstrapper for local tasks.
# Usage: tools/codex_exec.sh <python-module-or-script> [args...]
set -euo pipefail
if [ ! -d .venv ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q -r requirements.txt >/dev/null 2>&1 || true
else
  source .venv/bin/activate
fi
exec "$@"
