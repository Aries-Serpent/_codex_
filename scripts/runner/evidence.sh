#!/usr/bin/env bash
# Append JSONL evidence entries for runner operations.
# Usage: log_runner_evidence ACTION DETAILS_JSON (DETAILS_JSON must be a single-line JSON object)
set -euo pipefail

EVIDENCE_DIR=".codex/evidence"
EVIDENCE_FILE="${EVIDENCE_DIR}/runner_ops.jsonl"

log_runner_evidence() {
  local action="$1"
  local details_json="$2"
  mkdir -p "${EVIDENCE_DIR}"
  local ts; ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  # Compose one-line JSON
  printf '{"ts":"%s","action":"%s","details":%s}\n' "${ts}" "${action}" "${details_json}" >> "${EVIDENCE_FILE}"
}
