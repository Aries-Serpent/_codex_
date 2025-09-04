#!/usr/bin/env bash
set -euo pipefail
if [[ "${CODEX_ENV:-}" != "1" ]]; then
  echo "Skipping quality gates (CODEX_ENV!=1)."
  exit 0
fi
pre-commit install
pre-commit run -a || true # non-fatal; issues are shown and can be fixed incrementally
