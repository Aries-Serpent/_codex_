#!/usr/bin/env bash
set -euo pipefail

DATE_UTC=$(date -u +%Y-%m-%d)
TITLE="📍 \`_codex_\` : Status Update $(date -u +%Y-%m-%d-%H:%M:UTC)"
OUT=".codex/reports/daily/${DATE_UTC}.json"

python tools/status_report.py --title "$TITLE" --out "$OUT"
pytest -q tests/status/test_example_report_schema.py || { echo "Schema test failed"; exit 1; }
python tools/link_id_crossref.py --report "$OUT" || true
python scripts/audit/build_integrity_chain.py
echo "[OK] Full status cycle complete: $OUT"
