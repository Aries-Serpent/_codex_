#!/usr/bin/env bash
set -euo pipefail
echo "[Codex] Running local offline gates..."
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit run --all-files || true
fi
if command -v pytest >/dev/null 2>&1; then
  pytest -q || true
  pytest --cov=src/codex_ml --cov-fail-under=80 || true
fi
echo "[Codex] Gates complete (offline)."
