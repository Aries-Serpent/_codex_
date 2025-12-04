#!/usr/bin/env bash
set -euo pipefail

YAML_PATH="${1:-codex_task_sequence.yaml}"
AUDIT_PATH="${2:-_codex_status_update-2025-11-27.md}"

# Note: AUDIT_PATH is not yet wired directly; the YAML itself should reference
# the audit filename. This script is a convenience wrapper around the runner.

python tools/codex_task_sequence_runner.py \
  --yaml "${YAML_PATH}" \
  --repo-root "." \
  --change-log "codex_change_log.md" \
  --errors "codex_error_questions.md"
