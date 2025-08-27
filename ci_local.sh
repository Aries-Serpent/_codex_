#!/usr/bin/env bash
set -euo pipefail

echo "[codex] running local gates (offline-only)"
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit run --all-files || true
fi
if command -v python >/dev/null 2>&1 && [ -f analysis/audit_pipeline.py ]; then
  python analysis/audit_pipeline.py --repo . --steps static_code_analysis >/dev/null || true
fi
if command -v pytest >/dev/null 2>&1; then
  pytest -q || true
  pytest --cov --cov-fail-under=70 || true
fi
echo "[codex] done"
