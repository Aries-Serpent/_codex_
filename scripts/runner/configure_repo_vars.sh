#!/usr/bin/env bash
# Manage repository Actions variables using GH_PAT (preferred) or _CODEX_BOT_RUNNER (fallback).
# Supports:
#   - Curated variables:
#       RUNS_ON (JSON array string, e.g., '["self-hosted","linux"]')
#       OWNER_APPROVED_DURATION (mutually exclusive with OWNER_APPROVED_UNTIL)
#       OWNER_APPROVED_UNTIL (mutually exclusive with OWNER_APPROVED_DURATION)
#       PUSH_PLATFORMS (optional)
#   - Generic set:  --set NAME=VALUE   (repeatable)
#   - Delete var:   --delete NAME      (repeatable)
#
# Examples:
#   bash scripts/runner/configure_repo_vars.sh --owner Aries-Serpent --repo _codex_ \
#     --runs-on '["self-hosted","linux"]' --approval-duration "24h"
#   bash scripts/runner/configure_repo_vars.sh --owner Aries-Serpent --repo _codex_ \
#     --set FOO=bar --set FEATURE_FLAG=1
#   bash scripts/runner/configure_repo_vars.sh --owner Aries-Serpent --repo _codex_ \
#     --delete FOO --delete FEATURE_FLAG
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
# Arrays for generic set/delete
declare -a SET_PAIRS=()
declare -a DELETE_VARS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner) OWNER="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --runs-on) VAL_RUNS_ON="$2"; shift 2 ;;
    --approval-duration) VAL_APPROVAL_DURATION="$2"; shift 2 ;;
    --approval-until) VAL_APPROVAL_UNTIL="$2"; shift 2 ;;
    --push-platforms) VAL_PUSH_PLATFORMS="$2"; shift 2 ;;
    --set) SET_PAIRS+=("$2"); shift 2 ;;
    --delete) DELETE_VARS+=("$2"); shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
  continue

done

if [[ -z "${OWNER}" || -z "${REPO}" ]]; then
  echo "Usage: $0 --owner <owner> --repo <repo> [--runs-on 'JSON'] [--approval-duration '24h' | --approval-until 'YYYY-MM-DDTHH:MM:SSZ'] [--push-platforms 'linux/amd64,linux/arm64'] [--set NAME=VALUE ...] [--delete NAME ...]" >&2
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
BASE="${API}/repos/${OWNER}/${REPO}/actions/variables"

UP_LAST_STATUS=""
DEL_LAST_STATUS=""

upsert_var() {
  local name="$1"
  local value="$2"
  local rc=0
  UP_LAST_STATUS=""
  # Try PATCH (update existing)
  api_call PATCH "${BASE}/${name}" "$(jq -nc --arg v "${value}" '{value:$v}')" >/dev/null || rc=$?
  if [[ $rc -eq 0 ]]; then
    echo "[vars] Updated ${name}"
    UP_LAST_STATUS="updated"
    return 0
  fi
  # Try POST (create new)
  rc=0
  api_call POST "${BASE}" "$(jq -nc --arg n "${name}" --arg v "${value}" '{name:$n, value:$v}')" >/dev/null || rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "[vars] ERROR: Failed to upsert ${name}" >&2
    UP_LAST_STATUS="error"
    return 1
  fi
  echo "[vars] Created ${name}"
  UP_LAST_STATUS="created"
  return 0
}

delete_var() {
  local name="$1"
  local rc=0
  DEL_LAST_STATUS=""
  api_call DELETE "${BASE}/${name}" >/dev/null || rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "[vars] WARN: Failed to delete ${name} (may not exist or insufficient perms)." >&2
    DEL_LAST_STATUS="miss"
    return 1
  fi
  echo "[vars] Deleted ${name}"
  DEL_LAST_STATUS="deleted"
  return 0
}

created=()
updated=()
deleted=()
missed=()

track_status() {
  local status="$1"
  local name="$2"
  case "${status}" in
    created) created+=("${name}") ;;
    updated) updated+=("${name}") ;;
    deleted) deleted+=("${name}") ;;
    miss) missed+=("${name}") ;;
  esac
}

if [[ -n "${VAL_RUNS_ON}" ]]; then
  upsert_var "RUNS_ON" "${VAL_RUNS_ON}" || true
  track_status "${UP_LAST_STATUS}" "RUNS_ON"
fi
if [[ -n "${VAL_APPROVAL_DURATION}" ]]; then
  upsert_var "OWNER_APPROVED_DURATION" "${VAL_APPROVAL_DURATION}" || true
  track_status "${UP_LAST_STATUS}" "OWNER_APPROVED_DURATION"
fi
if [[ -n "${VAL_APPROVAL_UNTIL}" ]]; then
  upsert_var "OWNER_APPROVED_UNTIL" "${VAL_APPROVAL_UNTIL}" || true
  track_status "${UP_LAST_STATUS}" "OWNER_APPROVED_UNTIL"
fi
if [[ -n "${VAL_PUSH_PLATFORMS}" ]]; then
  upsert_var "PUSH_PLATFORMS" "${VAL_PUSH_PLATFORMS}" || true
  track_status "${UP_LAST_STATUS}" "PUSH_PLATFORMS"
fi

# Generic --set NAME=VALUE
for pair in "${SET_PAIRS[@]}"; do
  name="${pair%%=*}"
  value="${pair#*=}"
  if [[ -z "${name}" || "${name}" == "${value}" ]]; then
    echo "[vars] ERROR: --set requires NAME=VALUE (got: ${pair})" >&2
    continue
  fi
  upsert_var "${name}" "${value}" || true
  track_status "${UP_LAST_STATUS}" "${name}"
done

# Deletions
for name in "${DELETE_VARS[@]}"; do
  if [[ -z "${name}" ]]; then
    continue
  fi
  delete_var "${name}" || true
  track_status "${DEL_LAST_STATUS}" "${name}"
done

to_json_array() {
  if [[ $# -eq 0 ]]; then
    echo '[]'
    return
  fi
  printf '%s\n' "$@" | jq -R . | jq -s .
}

set_pairs_json="$(to_json_array "${SET_PAIRS[@]}")"
created_json="$(to_json_array "${created[@]}")"
updated_json="$(to_json_array "${updated[@]}")"
deleted_json="$(to_json_array "${deleted[@]}")"
missed_json="$(to_json_array "${missed[@]}")"

# Evidence
log_runner_evidence "configure_repo_vars" "$(jq -nc \
  --arg owner "${OWNER}" \
  --arg repo "${REPO}" \
  --arg runs_on "${VAL_RUNS_ON}" \
  --arg approval_duration "${VAL_APPROVAL_DURATION}" \
  --arg approval_until "${VAL_APPROVAL_UNTIL}" \
  --arg push_platforms "${VAL_PUSH_PLATFORMS}" \
  --argjson sets "${set_pairs_json}" \
  --argjson created "${created_json}" \
  --argjson updated "${updated_json}" \
  --argjson deleted "${deleted_json}" \
  --argjson missed "${missed_json}" \
  '{owner:$owner,repo:$repo,runs_on:$runs_on,approval_duration:$approval_duration,approval_until:$approval_until,push_platforms:$push_platforms,sets:$sets,created:$created,updated:$updated,deleted:$deleted,missed:$missed}')"

echo "[vars] Done."
