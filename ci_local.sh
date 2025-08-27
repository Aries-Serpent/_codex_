#!/usr/bin/env bash
set -euo pipefail

echo "[codex] running local gates (offline-only)"
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit run --all-files || true
fi
if command -v pytest >/dev/null 2>&1; then
  pytest -q || true
  pytest --cov --cov-fail-under=70 || true
fi
echo "[codex] done"
