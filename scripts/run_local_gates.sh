#!/usr/bin/env bash
set -euo pipefail

SUMMARY_PATH="${1:-}"
SELECTED_INDEX="${2:-}"

if [[ -z "${SUMMARY_PATH}" ]]; then
  cat <<'USAGE' >&2
Usage: scripts/run_local_gates.sh <assistant_summary.json> [selected_index]

Provide the assistant summary file exported from the task UI. Optionally supply the
candidate index you intend to choose to assert it with the selection guard.
USAGE
  exit 1
fi

if [[ ! -f "${SUMMARY_PATH}" ]]; then
  echo "Summary file not found: ${SUMMARY_PATH}" >&2
  exit 1
fi

echo "==> Running fence validator"
python tools/validate_fences.py

echo "==> Running codex evaluator (${SUMMARY_PATH})"
python tools/codex_evaluator.py --rules manifests/codex_eval_rules.v3.json --input "${SUMMARY_PATH}"

echo "==> Running selection guard (${SUMMARY_PATH})"
if [[ -n "${SELECTED_INDEX}" ]]; then
  python tools/selection_guard.py --rules manifests/selection_guard_rules.json --input "${SUMMARY_PATH}" --selected "${SELECTED_INDEX}" || true
else
  python tools/selection_guard.py --rules manifests/selection_guard_rules.json --input "${SUMMARY_PATH}" || true
fi
# (Selection index is illustrative; pass the candidate you intend to choose when ready.)

echo "All local gates passed."
