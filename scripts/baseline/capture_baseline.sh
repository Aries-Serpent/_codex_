#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ART="${ROOT}/audit_artifacts"
BASE="${ART}/baselines"
STAMP="$(date -u +'%Y%m%d_%H%M%S')"
DEST="${BASE}/${STAMP}"

mkdir -p "${DEST}"
cp -v "${ART}"/*.json "${DEST}" || true
cp -v "${ROOT}/audit_run_manifest.json" "${DEST}/" || true

echo "[INFO] Baseline captured at ${DEST}"
