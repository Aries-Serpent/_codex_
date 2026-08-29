#!/usr/bin/env bash
set -euo pipefail
CFG="${1:-visual_baseline/thresholds.json}"
TEMPLATE="${2:-report_template_themed.html}"
BASE="${3:-visual_baseline/${TEMPLATE%.*}/LATEST.png}"
CANDIDATE="${4:-.codex/reports/daily/$(date -u +%Y-%m-%d).png}"
python tools/visual_compare_config.py --config "${CFG}" --template "${TEMPLATE}" --baseline "${BASE}" --candidate "${CANDIDATE}"
