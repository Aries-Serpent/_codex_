#!/usr/bin/env bash
# Usage: tools/timeout_wrapper.sh <seconds> -- <cmd> [args...]
set -euo pipefail

t="${1:-120}"; shift
if [[ "${1:-}" != "--" ]]; then
  echo "usage: $0 <seconds> -- <cmd> [args...]" >&2; exit 2
fi
shift
cmd=("$@")
(
  "${cmd[@]}"
) &
pid=$!
(
  secs=$t; while (( secs > 0 )); do sleep 1; ((secs--)); done;
  if kill -0 "$pid" 2>/dev/null; then
    echo "[timeout_wrapper] Timeout after ${t}s: ${cmd[*]}";
    kill -TERM "$pid" || true;
  fi
) &
wait "$pid" || exit $?
