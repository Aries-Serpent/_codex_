#!/usr/bin/env bash
set -euo pipefail

if [ -f "$(dirname "$0")/session_logging.sh" ]; then
  . "$(dirname "$0")/session_logging.sh"
  codex_session_start "$0" "$@"
  trap 'codex_session_end $?' EXIT
fi

python3 -m codex.logging.query_logs --help >/dev/null
echo "[OK] query_logs --help executed"
