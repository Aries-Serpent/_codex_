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

RUNNER_URL=""
RUNNER_DIR="${HOME}/actions-runner"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      RUNNER_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "${RUNNER_URL}" ]]; then
  echo "Usage: $0 --url <https://github.com/org_or_repo>" >&2
  exit 2
fi

resolve_pat() {
  if [[ -n "${GH_PAT:-}" ]]; then
    echo "${GH_PAT}"
  elif [[ -n "${_CODEX_BOT_RUNNER:-}" ]]; then
    echo "${_CODEX_BOT_RUNNER}"
  else
    echo ""
  fi
}

parse_owner_repo() {
  local url="$1"
  local path="${url#*github.com/}"
  local owner="${path%%/*}"
  local rest="${path#*/}"
  local repo=""
  if [[ "${rest}" != "${path}" && -n "${rest}" && "${rest}" != "${owner}" ]]; then
    repo="${rest%%/*}"
  fi
  echo "${owner}" "${repo}"
}

get_remove_token() {
  local url="$1"
  local pat="$2"
  local owner repo endpoint
  read -r owner repo <<<"$(parse_owner_repo "${url}")"
  if [[ -z "${owner}" ]]; then
    echo ""
    return 0
  fi
  if [[ -n "${repo}" ]]; then
    endpoint="https://api.github.com/repos/${owner}/${repo}/actions/runners/remove-token"
  else
    endpoint="https://api.github.com/orgs/${owner}/actions/runners/remove-token"
  fi
  local json
  json="$(curl -fsSL -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${pat}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "${endpoint}" || true)"
  echo "${json}" | tr -d '\n' | sed -n 's/.*"token":"\([^"]*\)".*/\1/p'
}

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

PAT="$(resolve_pat || true)"
if [[ -z "${PAT}" ]]; then
  echo "[runner] ERROR: Need GH_PAT or _CODEX_BOT_RUNNER to obtain remove token." >&2
  exit 1
fi

REMOVE_TOKEN="$(get_remove_token "${RUNNER_URL}" "${PAT}")"
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
echo "[runner] Done."
