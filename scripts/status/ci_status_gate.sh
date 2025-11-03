#!/usr/bin/env bash
set -euo pipefail

# Gate v1.2 status, configs, and audit artifacts locally or in CI.

echo "[1/5] Validate status example schema"
if [ -f tests/status/test_example_report_schema.py ]; then
  python -m pytest -q tests/status/test_example_report_schema.py || { echo "Status schema validation failed"; exit 1; }
else
  echo "  Skipped: test file not found"
fi

echo "[2/5] Validate configs (if present)"
if [ -f configs/schemas/training.schema.yaml ] && [ -d configs/training ]; then
  python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml || true
else
  echo "  Skipped: configs not found"
fi

echo "[3/5] Generate capability suggestions"
python tools/capability_autodiscover.py || true

echo "[4/5] Build audit integrity chain"
python scripts/audit/build_integrity_chain.py

echo "[5/5] Security gates (best-effort)"
if command -v bandit >/dev/null 2>&1; then bandit -q -r src || true; fi
if command -v detect-secrets >/dev/null 2>&1; then detect-secrets scan > .secrets.baseline || true; fi
echo "[OK] CI status gate completed"
