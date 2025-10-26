#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Running fence integrity check"
python tools/validate_fences.py

echo "==> Running codex evaluator (samples/assistant_message_summary.sample.json)"
python tools/codex_evaluator.py --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json

if python -c "import jsonschema" >/dev/null 2>&1; then
  echo "==> Running manifest schema checks"
  python tools/schema_validate.py \
    --data manifests/selection_guard_rules.json --schema schemas/selection_guard_rules.schema.json \
    --data manifests/codex_eval_rules.v3.json --schema schemas/codex_eval_rules.v3.schema.json
else
  echo '==> [info] Skipping schema checks (jsonschema not installed).'
fi

echo "==> Running selection guard (samples/assistant_message_summary.sample.json)"
python tools/selection_guard.py --rules manifests/selection_guard_rules.json --input samples/assistant_message_summary.sample.json --selected 3 || true
# (Selection index is illustrative; adjust --selected to the candidate you intend to choose.)

echo "All local gates passed."
