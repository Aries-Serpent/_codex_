#!/usr/bin/env bash
set -euo pipefail
DATE_UTC=$(date -u +%Y-%m-%d)
JSON="reports/daily/${DATE_UTC}.json"
MD="reports/daily/${DATE_UTC}.md"
python scripts/status/render_markdown_report.py --json "$JSON" --out "$MD"
echo "[OK] Wrote $MD"
