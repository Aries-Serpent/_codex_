#!/usr/bin/env bash
set -euo pipefail

DATE=$(date -u +%Y-%m-%d)
REPORT=".codex/reports/daily/${DATE}.json"

if [ ! -f "$REPORT" ]; then
  echo "[FAIL] Missing ${REPORT}. Generate skeleton first."
  exit 1
fi

# Optional merges if artifacts exist
MERGE_ARGS=()

if [ -f "coverage_modules.json" ]; then
  MERGE_ARGS+=( "--in" "coverage_modules.json:snapshot.tests_gates.coverage_by_module" )
fi

if [ -f "perf_snapshot.json" ]; then
  MERGE_ARGS+=( "--in" "perf_snapshot.json:automation.performance" )
fi

if [ -f "schema_validation_results.json" ]; then
  python tools/schema_results_to_status.py --report "$REPORT" --results schema_validation_results.json
fi

if [ ${#MERGE_ARGS[@]} -gt 0 ]; then
  python tools/report_merge.py --report "$REPORT" "${MERGE_ARGS[@]}"
fi

echo "[OK] Enriched ${REPORT}"
