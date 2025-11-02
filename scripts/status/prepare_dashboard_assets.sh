#!/usr/bin/env bash
set -euo pipefail

TS=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p dist
if [ -f status_dashboard.json ]; then
  cp status_dashboard.json "dist/status_dashboard_${TS}.json"
else
  echo '{}' > "dist/status_dashboard_${TS}.json"
fi
echo "[OK] Prepared dashboard asset at dist/status_dashboard_${TS}.json"
