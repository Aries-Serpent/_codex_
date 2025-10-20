#!/usr/bin/env bash
# Write the latest owner-approval decision to the job summary and echo JSON.
# Usage (CI): bash scripts/ci/owner_approval_summary.sh [tool_key]
set -euo pipefail

TOOL_KEY="${1:-docker-build-push}"
WORKFLOW_NAME="${WORKFLOW_NAME:-${GITHUB_WORKFLOW:-local}}"

# Ensure the guard has been evaluated at least once in this run for fresh evidence
CODEX_EVIDENCE=1 WORKFLOW_NAME="${WORKFLOW_NAME}" TOOL_KEY="${TOOL_KEY}" bash scripts/ci/owner_approval_guard.sh >/dev/null 2>&1 || true

evidence_file=".codex/evidence/owner_approval.jsonl"
line=""
if [ -f "${evidence_file}" ]; then
  line="$(tail -n1 "${evidence_file}" || true)"
fi

decision="$(printf '%s' "${line}" | sed -n 's/.*"decision":"\([^"]*\)".*/\1/p')"
source="$(printf '%s' "${line}" | sed -n 's/.*"source":"\([^"]*\)".*/\1/p')"
expiry="$(printf '%s' "${line}" | sed -n 's/.*"expiry":"\([^"]*\)".*/\1/p')"
repo="$(printf '%s' "${line}" | sed -n 's/.*"repo":"\([^"]*\)".*/\1/p')"
ref="$(printf '%s' "${line}" | sed -n 's/.*"ref":"\([^"]*\)".*/\1/p')"
actor="$(printf '%s' "${line}" | sed -n 's/.*"actor":"\([^"]*\)".*/\1/p')"
run_id="$(printf '%s' "${line}" | sed -n 's/.*"run_id":"\([^"]*\)".*/\1/p')"
attempt="$(printf '%s' "${line}" | sed -n 's/.*"run_attempt":"\([^"]*\)".*/\1/p')"

json="$(printf '{"workflow":"%s","tool_key":"%s","repo":"%s","ref":"%s","actor":"%s","run_id":"%s","attempt":"%s","decision":"%s","source":"%s","expiry":"%s"}' \
  "${WORKFLOW_NAME}" "${TOOL_KEY}" "${repo}" "${ref}" "${actor}" "${run_id}" "${attempt}" "${decision:-unknown}" "${source:-unknown}" "${expiry:-}")"

echo "${json}"

# Write to step summary when available
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "## Owner approval status"
    echo ""
    echo "- Workflow: ${WORKFLOW_NAME}"
    echo "- Tool key: ${TOOL_KEY}"
    echo "- Repo: ${repo} (${ref})"
    echo "- Actor: ${actor}"
    echo "- Decision: ${decision:-unknown}"
    echo "- Source: ${source:-unknown}"
    echo "- Expiry: ${expiry:-}"
    echo ""
    echo "<details><summary>JSON</summary>"
    echo ""
    echo '```json'
    echo "${json}"
    echo '```'
    echo "</details>"
  } >> "${GITHUB_STEP_SUMMARY}"
fi
