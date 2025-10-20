#!/usr/bin/env bash
# docker/entrypoint.sh — normalize env, optional prestart, sane defaults for ASGI app
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
PRESTART_CMD="${PRESTART_CMD:-}"
DISABLE_TINI="${DISABLE_TINI:-0}"
# Default ASGI app can be overridden by env; mirrors Dockerfile CMD target
APP_MODULE="${APP_MODULE:-src.codex.api.app:app}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-info}"

cd "$APP_DIR"

# Load .env if present (non-destructive export)
if [ -f ".env" ]; then
  echo "[entrypoint] Loading environment from $APP_DIR/.env"
  set -a
  # shellcheck disable=SC1091
  . ".env"
  set +a
fi

# Optional prestart command (migrations, warmup, etc.)
if [ -n "$PRESTART_CMD" ]; then
  echo "[entrypoint] Running PRESTART_CMD"
  /bin/sh -c "$PRESTART_CMD"
fi

# Decide command:
# - If first arg is empty or a flag, default to uvicorn APP_MODULE at PORT with LOG_LEVEL.
# - If the command matches the Dockerfile's default uvicorn invocation, rebuild it using env overrides.
# - Else, respect explicit command.
if [ "${1:-}" = "" ] || [[ "${1:-}" == -* ]]; then
  set -- uvicorn "${APP_MODULE}" --host 0.0.0.0 --port "${PORT}" --log-level "${LOG_LEVEL}" "$@"
elif [ "${1:-}" = "uvicorn" ]; then
  DEFAULT_APP_MODULE="src.codex.api.app:app"
  if [ "$#" -eq 8 ] \
    && [ "${2:-}" = "${DEFAULT_APP_MODULE}" ] \
    && [ "${3:-}" = "--host" ] \
    && [ "${4:-}" = "0.0.0.0" ] \
    && [ "${5:-}" = "--port" ] \
    && [ "${6:-}" = "8000" ] \
    && [ "${7:-}" = "--log-level" ] \
    && [ "${8:-}" = "info" ]; then
    set -- uvicorn "${APP_MODULE}" --host 0.0.0.0 --port "${PORT}" --log-level "${LOG_LEVEL}"
  fi
fi

# Use tini (if not disabled) to reap zombies and forward signals.
if [ "$DISABLE_TINI" != "1" ] && command -v tini >/dev/null 2>&1; then
  exec "$(command -v tini)" -- "$@"
fi

exec "$@"
