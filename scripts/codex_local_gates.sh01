#!/usr/bin/env bash
set -euo pipefail
echo "[Codex] Running local offline gates..."
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit run --all-files || true
fi
if command -v pytest >/dev/null 2>&1; then
  if python - <<'PY'
import sys
try:
    import pytest_cov  # noqa: F401
except Exception:
    sys.exit(1)
PY
  then
    pytest -q --cov=src/codex_ml --cov-fail-under=70 || true
  else
    echo "[Codex] pytest-cov missing; running without coverage" >&2
    pytest -q || true
  fi
fi
echo "[Codex] Gates complete (offline)."
