#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Running fence integrity check"
python tools/validate_fences.py

echo "==> Running codex evaluator (samples/assistant_message_summary.sample.json)"
python tools/codex_evaluator.py --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json

echo "All local gates passed."
