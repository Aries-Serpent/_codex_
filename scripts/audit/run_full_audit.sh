#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Capability autodiscovery"
python tools/capability_autodiscover.py

echo "[2/4] Capability scoring"
python tools/capability_score.py || true

echo "[3/4] Gaps analysis"
python tools/gaps_analyze.py || true

echo "[4/4] Build integrity chain"
python scripts/audit/build_integrity_chain.py

echo "[OK] Full audit completed"
