#!/usr/bin/env bash
# Drain queued workflow runs by repeatedly launching ephemeral runners.
# Requirements: GH_PAT or _CODEX_BOT_RUNNER; curl; jq (for counting).
#
# Example:
#   bash scripts/runner/drain_queue_ephemeral.sh \
#     --owner "Aries-Serpent" --repo "_codex_" \
#     [--labels "linux,docker"] \
#     [--version "2.329.0"]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

OWNER=""
REPO=""
# Add a custom "linux" label by default to satisfy runs-on ["self-hosted","linux"] even if built-in shows as "Linux".
RUNNER_LABELS="linux"
RUNNER_VERSION="2.329.0"
SLEEP_BETWEEN=3
MAX_ITER=50

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner) OWNER="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --labels) RUNNER_LABELS="$2"; shift 2 ;;
    --version) RUNNER_VERSION="$2"; shift 2 ;;
    --sleep) SLEEP_BETWEEN="$2"; shift 2 ;;
    --max) MAX_ITER="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "${OWNER}" || -z "${REPO}" ]]; then
  echo "Usage: $0 --owner <owner> --repo <repo> [--labels 'linux,docker'] [--version '2.329.0'] [--sleep 3] [--max 50]" >&2
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "[drain] ERROR: jq is required." >&2
  exit 1
fi

queued_count() {
  local url="https://api.github.com/repos/${OWNER}/${REPO}/actions/runs?status=queued&per_page=1"
  local json; json="$(api_call GET "${url}" || true)"
  if [[ -z "${json}" ]]; then
    echo 0
    return 0
  fi
  echo "${json}" | jq -r '.total_count // 0'
}

iter=0
while :; do
  count="$(queued_count)"
  echo "[drain] Queued runs: ${count}"
  if [[ "${count}" -le 0 ]]; then
    echo "[drain] Queue is empty. Done."
    break
  fi

  echo "[drain] Launching ephemeral runner to pick up next job..."
  if [[ -n "${RUNNER_LABELS}" ]]; then
    bash "${SCRIPT_DIR}/actions_runner_ephemeral.sh" \
      --url "https://github.com/${OWNER}/${REPO}" \
      --labels "${RUNNER_LABELS}" \
      --version "${RUNNER_VERSION}"
  else
    bash "${SCRIPT_DIR}/actions_runner_ephemeral.sh" \
      --url "https://github.com/${OWNER}/${REPO}" \
      --version "${RUNNER_VERSION}"
  fi

  iter=$((iter+1))
  if [[ "${iter}" -ge "${MAX_ITER}" ]]; then
    echo "[drain] Reached MAX iterations (${MAX_ITER}). Stopping."
    break
  fi
  sleep "${SLEEP_BETWEEN}"
done
