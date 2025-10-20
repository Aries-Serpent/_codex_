#!/usr/bin/env bash
# Report current owner-approval status for a TOOL_KEY and exit with same code as guard.
# Usage:
#   scripts/ci/owner_approval_status.sh [tool_key]
# Env (optional):
#   WORKFLOW_NAME: label to include in evidence/status (default: $GITHUB_WORKFLOW or "local")
set -euo pipefail

TOOL_KEY="${1:-docker-build-push}"
WORKFLOW_NAME="${WORKFLOW_NAME:-${GITHUB_WORKFLOW:-local}}"

# Run guard to update evidence, but silence output. Preserve return code.
CODEX_EVIDENCE=1 WORKFLOW_NAME="${WORKFLOW_NAME}" TOOL_KEY="${TOOL_KEY}" bash scripts/ci/owner_approval_guard.sh >/dev/null 2>&1 || true
rc=$?

# Pull the latest evidence line (if any)
evidence_file=".codex/evidence/owner_approval.jsonl"
decision="" source="" expiry=""
if [ -f "${evidence_file}" ]; then
  last="$(tail -n1 "${evidence_file}" || true)"
  # naive JSON field extraction (no jq)
  decision="$(printf '%s' "${last}" | sed -n 's/.*"decision":"\([^"]*\)".*/\1/p')"
  source="$(printf '%s' "${last}" | sed -n 's/.*"source":"\([^"]*\)".*/\1/p')"
  expiry="$(printf '%s' "${last}" | sed -n 's/.*"expiry":"\([^"]*\)".*/\1/p')"
fi

echo "[status] workflow=${WORKFLOW_NAME} tool_key=${TOOL_KEY} decision=${decision:-unknown} source=${source:-unknown} expiry=${expiry:-}"
printf '{"workflow":"%s","tool_key":"%s","decision":"%s","source":"%s","expiry":"%s","rc":%d}\n' \
  "${WORKFLOW_NAME}" "${TOOL_KEY}" "${decision:-unknown}" "${source:-unknown}" "${expiry:-}" "${rc}"

exit "${rc}"
