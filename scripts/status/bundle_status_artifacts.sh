#!/usr/bin/env bash
set -euo pipefail

OUT="status_bundle_$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
tar -czf "$OUT" \
  audit_run_manifest.json \
  audit_artifacts \
  docs/templates/status/codex_status_template.schema_v1.2.json \
  docs/templates/status/example_report_v1.2.json || true

echo "[OK] Wrote $OUT"
