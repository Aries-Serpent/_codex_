#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
PRESTART_CMD="${PRESTART_CMD:-}"
DISABLE_TINI="${DISABLE_TINI:-0}"

cd "$APP_DIR"

if [[ -f ".env" ]]; then
  echo "[entrypoint] Loading environment from $APP_DIR/.env"
  set -o allexport
  # shellcheck disable=SC1091
  source ".env"
  set +o allexport
fi

if [[ -n "$PRESTART_CMD" ]]; then
  echo "[entrypoint] Running PRESTART_CMD"
  /bin/sh -c "$PRESTART_CMD"
fi

if [[ "$DISABLE_TINI" != "1" ]] && command -v tini >/dev/null 2>&1; then
  exec "$(command -v tini)" -- "$@"
fi

exec "$@"
