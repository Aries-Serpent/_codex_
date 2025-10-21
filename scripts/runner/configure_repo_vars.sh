#!/usr/bin/env bash
# Configure repository Actions variables using GH_PAT (preferred) or _CODEX_BOT_RUNNER (fallback).
# NO NEW VARIABLE NAMES ARE INTRODUCED — this only sets values for existing/agreed names:
#   - RUNS_ON (JSON array string, e.g., '["self-hosted","linux"]')
#   - OWNER_APPROVED_DURATION (mutually exclusive with OWNER_APPROVED_UNTIL)
#   - OWNER_APPROVED_UNTIL (mutually exclusive with OWNER_APPROVED_DURATION)
#   - PUSH_PLATFORMS (optional)
#
# Examples:
#   bash scripts/runner/configure_repo_vars.sh --owner Aries-Serpent --repo _codex_ --runs-on '["self-hosted","linux"]' --approval-duration "24h"
#   bash scripts/runner/configure_repo_vars.sh --owner Aries-Serpent --repo _codex_ --approval-until "2025-10-21T00:00:00Z"
#   bash scripts/runner/configure_repo_vars.sh --owner Aries-Serpent --repo _codex_ --push-platforms "linux/amd64,linux/arm64"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
# shellcheck source=evidence.sh
source "${SCRIPT_DIR}/evidence.sh"

if ! command -v jq >/dev/null 2>&1; then
  echo "[vars] ERROR: jq is required for configure_repo_vars" >&2
  exit 1
fi

OWNER=""
REPO=""
VAL_RUNS_ON=""
VAL_APPROVAL_DURATION=""
VAL_APPROVAL_UNTIL=""
VAL_PUSH_PLATFORMS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner) OWNER="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --runs-on) VAL_RUNS_ON="$2"; shift 2 ;;
    --approval-duration) VAL_APPROVAL_DURATION="$2"; shift 2 ;;
    --approval-until) VAL_APPROVAL_UNTIL="$2"; shift 2 ;;
    --push-platforms) VAL_PUSH_PLATFORMS="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
  continue

done

if [[ -z "${OWNER}" || -z "${REPO}" ]]; then
  echo "Usage: $0 --owner <owner> --repo <repo> [--runs-on 'JSON'] [--approval-duration '24h' | --approval-until 'YYYY-MM-DDTHH:MM:SSZ'] [--push-platforms 'linux/amd64,linux/arm64']" >&2
  exit 2
fi

if [[ -n "${VAL_RUNS_ON}" ]]; then
  if ! echo "${VAL_RUNS_ON}" | jq -e 'type=="array"' >/dev/null 2>&1; then
    echo "[vars] ERROR: --runs-on must be a JSON array string, e.g., '[\"self-hosted\",\"linux\"]'." >&2
    exit 1
  fi
fi

if [[ -n "${VAL_APPROVAL_DURATION}" && -n "${VAL_APPROVAL_UNTIL}" ]]; then
  echo "[vars] ERROR: Provide only one of --approval-duration or --approval-until." >&2
  exit 1
fi

API="https://api.github.com"
PATCH_VAR="${API}/repos/${OWNER}/${REPO}/actions/variables"
CREATE_VAR="${API}/repos/${OWNER}/${REPO}/actions/variables"

upsert_var() {
  local name="$1"
  local value="$2"
  # Try PATCH
  local rc=0
  api_call PATCH "${PATCH_VAR}/${name}" "$(jq -nc --arg v "${value}" '{value:$v}')" >/dev/null || rc=$?
  if [[ $rc -eq 0 ]]; then
    echo "[vars] Updated ${name}"
    return 0
  fi
  # Try POST (create)
  rc=0
  api_call POST "${CREATE_VAR}" "$(jq -nc --arg n "${name}" --arg v "${value}" '{name:$n, value:$v}')" >/dev/null || rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "[vars] ERROR: Failed to upsert ${name}" >&2
    return 1
  fi
  echo "[vars] Created ${name}"
}

changed=()

if [[ -n "${VAL_RUNS_ON}" ]]; then
  upsert_var "RUNS_ON" "${VAL_RUNS_ON}" && changed+=("RUNS_ON")
fi
if [[ -n "${VAL_APPROVAL_DURATION}" ]]; then
  upsert_var "OWNER_APPROVED_DURATION" "${VAL_APPROVAL_DURATION}" && changed+=("OWNER_APPROVED_DURATION")
fi
if [[ -n "${VAL_APPROVAL_UNTIL}" ]]; then
  upsert_var "OWNER_APPROVED_UNTIL" "${VAL_APPROVAL_UNTIL}" && changed+=("OWNER_APPROVED_UNTIL")
fi
if [[ -n "${VAL_PUSH_PLATFORMS}" ]]; then
  upsert_var "PUSH_PLATFORMS" "${VAL_PUSH_PLATFORMS}" && changed+=("PUSH_PLATFORMS")
fi

changed_json="$(printf '%s\n' "${changed[@]:-}" | jq -R . | jq -s .)"

# Evidence
log_runner_evidence "configure_repo_vars" "$(jq -nc \
  --arg owner "${OWNER}" \
  --arg repo "${REPO}" \
  --arg runs_on "${VAL_RUNS_ON}" \
  --arg approval_duration "${VAL_APPROVAL_DURATION}" \
  --arg approval_until "${VAL_APPROVAL_UNTIL}" \
  --arg push_platforms "${VAL_PUSH_PLATFORMS}" \
  --argjson changed "${changed_json}" \
  '{owner:$owner,repo:$repo,runs_on:$runs_on,approval_duration:$approval_duration,approval_until:$approval_until,push_platforms:$push_platforms,changed:$changed}')"

echo "[vars] Done."
