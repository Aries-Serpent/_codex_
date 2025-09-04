#!/usr/bin/env bash
set -euo pipefail
pre-commit install
if [[ ! -f ".secrets.baseline" ]]; then
  echo "[hint] generating initial secrets baseline (.secrets.baseline)"
  detect-secrets scan > .secrets.baseline || true
fi
if [[ "${CODEX_ENV:-}" != "1" ]]; then
  echo "Skipping pre-commit run (CODEX_ENV!=1)"
  exit 0
fi
# local-only, non-fatal to preserve dev flow
pre-commit run -a || true
