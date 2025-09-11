#!/usr/bin/env bash
set -euo pipefail
echo "[Codex] Running local offline gates..."
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit run --all-files
fi
if command -v pytest >/dev/null 2>&1; then
  pytest -q
  pytest --cov=src/codex_ml --cov-fail-under=70
fi
echo "[Codex] Gates complete (offline)."
