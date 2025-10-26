#!/usr/bin/env bash
set -euo pipefail

echo "==> Running fence validator"
python tools/validate_fences.py

echo "==> Running codex evaluator (samples/assistant_message_summary.sample.json)"
python tools/codex_evaluator.py --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json

echo "==> Running selection guard (samples/assistant_message_summary.sample.json)"
python tools/selection_guard.py --rules manifests/selection_guard_rules.json --input samples/assistant_message_summary.sample.json --selected 3 || true
# (Selection index is illustrative; adjust --selected to the candidate you intend to choose.)

echo "All local gates passed."
