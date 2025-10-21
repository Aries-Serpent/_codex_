#!/usr/bin/env bash
# Remove a GitHub Actions self-hosted runner (stop service if present) and deregister.
# Usage:
#   bash scripts/runner/actions_runner_remove.sh --url "https://github.com/Aries-Serpent/_codex_"
#
# Token logic:
# - Uses GH_PAT (preferred) or _CODEX_BOT_RUNNER (fallback) to request a short-lived remove token:
#   Repo URL → POST /repos/{owner}/{repo}/actions/runners/remove-token
#   Org URL  → POST /orgs/{org}/actions/runners/remove-token
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
# shellcheck source=evidence.sh
source "${SCRIPT_DIR}/evidence.sh"

RUNNER_URL=""
RUNNER_DIR="${HOME}/actions-runner"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url) RUNNER_URL="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac

done

if [[ -z "${RUNNER_URL}" ]]; then
  echo "Usage: $0 --url <https://github.com/org_or_repo>" >&2
  exit 2
fi

stop_service() {
  local svc="actions-runner@${USER}"
  if command -v systemctl >/dev/null 2>&1; then
    if [[ $(id -u) -eq 0 ]]; then
      systemctl stop "${svc}" 2>/dev/null || true
      systemctl disable "${svc}" 2>/dev/null || true
    elif command -v sudo >/dev/null 2>&1; then
      sudo systemctl stop "${svc}" 2>/dev/null || true
      sudo systemctl disable "${svc}" 2>/dev/null || true
    fi
  fi
}

stop_service

if [[ ! -d "${RUNNER_DIR}" ]]; then
  echo "[runner] ${RUNNER_DIR} not found; nothing to remove."
  exit 0
fi

pat="$(resolve_pat || true)"
if [[ -z "${pat}" ]]; then
  echo "[runner] ERROR: Need GH_PAT or _CODEX_BOT_RUNNER to obtain remove token." >&2
  exit 1
fi

path="${RUNNER_URL#*github.com/}"
owner="${path%%/*}"
rest="${path#*/}"
repo=""
if [[ "${rest}" != "${path}" && -n "${rest}" && "${rest}" != "${owner}" ]]; then
  repo="${rest%%/*}"
fi
if [[ -n "${repo}" ]]; then
  endpoint="https://api.github.com/repos/${owner}/${repo}/actions/runners/remove-token"
else
  endpoint="https://api.github.com/orgs/${owner}/actions/runners/remove-token"
fi

json="$(api_call POST "${endpoint}" || true)"
REMOVE_TOKEN="$(echo "${json}" | tr -d '\n' | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')"
if [[ -z "${REMOVE_TOKEN}" ]]; then
  echo "[runner] ERROR: Could not obtain remove token; ensure PAT permissions are sufficient." >&2
  exit 1
fi

echo "[runner] Deregistering runner from ${RUNNER_URL}"
(
  cd "${RUNNER_DIR}"
  ./config.sh remove --token "${REMOVE_TOKEN}" || true
)

echo "[runner] Cleaning files at ${RUNNER_DIR}"
rm -rf "${RUNNER_DIR}"

# Evidence
if command -v jq >/dev/null 2>&1; then
  log_runner_evidence "runner_remove" "$(jq -nc --arg url "${RUNNER_URL}" '{url:$url}')"
else
  log_runner_evidence "runner_remove" "{\"url\":\"${RUNNER_URL}\"}"
fi

echo "[runner] Done."
