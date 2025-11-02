#!/usr/bin/env bash
set -euo pipefail

if ! command -v detect-secrets >/dev/null 2>&1; then
  echo "[FAIL] detect-secrets not installed. Try: pip install detect-secrets"
  exit 1
fi

echo "[INFO] Scanning repository for secrets"
detect-secrets scan > .secrets.baseline
echo "[OK] Wrote .secrets.baseline"
echo "[NEXT] Audit baseline locally: detect-secrets audit .secrets.baseline"
