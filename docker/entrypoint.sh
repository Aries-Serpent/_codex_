#!/usr/bin/env bash
# Optional lightweight entrypoint: set defaults, handle signals via tini.
set -euo pipefail

# If a .env file exists, load it non-interactively (safe defaults)
if [ -f "/app/.env" ]; then
  # shellcheck disable=SC1091
  set -a; source /app/.env; set +a
fi

# If first arg looks like a flag, or is empty, default to uvicorn
if [ "${1:-}" = "" ] || [[ "${1:-}" == -* ]]; then
  exec /usr/bin/tini -- uvicorn src.codex.api.app:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --log-level "${LOG_LEVEL:-info}"
fi

# Otherwise, exec the provided command
exec /usr/bin/tini -- "$@"
