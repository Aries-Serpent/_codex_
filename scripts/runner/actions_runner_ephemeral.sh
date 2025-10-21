#!/usr/bin/env bash
# Launch a single-use (ephemeral) self-hosted runner from the current machine.
# Requirements: curl, tar; NO systemd needed. Uses GH_PAT (preferred) or _CODEX_BOT_RUNNER.
#
# Usage (repo-level):
#   bash scripts/runner/actions_runner_ephemeral.sh \
#     --url "https://github.com/Aries-Serpent/_codex_" \
#     [--labels "linux,docker"] \
#     [--version "2.329.0"]
#
# Usage (org-level, picks any eligible job from org scope):
#   bash scripts/runner/actions_runner_ephemeral.sh \
#     --url "https://github.com/Aries-Serpent" \
#     [--labels "linux,docker"]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
# shellcheck source=evidence.sh
source "${SCRIPT_DIR}/evidence.sh"

RUNNER_URL=""
# Add a custom "linux" label by default to satisfy runs-on ["self-hosted","linux"] even if built-in shows as "Linux".
RUNNER_LABELS="linux"
RUNNER_VERSION="2.329.0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url) RUNNER_URL="$2"; shift 2 ;;
    --labels) RUNNER_LABELS="$2"; shift 2 ;;
    --version) RUNNER_VERSION="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "${RUNNER_URL}" ]]; then
  echo "Usage: $0 --url <https://github.com/org_or_repo> [--labels 'linux,docker'] [--version '2.329.0']" >&2
  exit 2
fi

require_cmd curl
require_cmd tar

TMP_DIR="$(mktemp -d -t gh-runner-XXXXXX)"
cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

cd "${TMP_DIR}"
PKG="actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
PKG_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${PKG}"
echo "[ephemeral] Downloading ${PKG_URL}"
curl -fsSL -o "${PKG}" "${PKG_URL}"
tar xzf "${PKG}"

# Registration token via API
pat="$(resolve_pat || true)"
if [[ -z "${pat}" ]]; then
  echo "[ephemeral] ERROR: GH_PAT or _CODEX_BOT_RUNNER must be set." >&2
  exit 1
fi
read -r owner repo <<<"$(parse_owner_repo "${RUNNER_URL}")"
if [[ -z "${owner}" ]]; then
  echo "[ephemeral] ERROR: Unable to parse owner from URL ${RUNNER_URL}" >&2
  exit 1
fi

if [[ -n "${repo}" ]]; then
  endpoint="https://api.github.com/repos/${owner}/${repo}/actions/runners/registration-token"
else
  endpoint="https://api.github.com/orgs/${owner}/actions/runners/registration-token"
fi
json="$(api_call POST "${endpoint}" || true)"
REG_TOKEN="$(echo "${json}" | tr -d '\n' | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')"
if [[ -z "${REG_TOKEN}" ]]; then
  echo "[ephemeral] ERROR: Failed to obtain registration token. Check PAT scopes." >&2
  exit 1
fi

# Avoid ICU dependency issues on minimal hosts during configuration and runtime
export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1

echo "[ephemeral] Configuring runner (ephemeral) for ${RUNNER_URL}"
if [[ -n "${RUNNER_LABELS}" ]]; then
  ./config.sh --unattended --ephemeral --url "${RUNNER_URL}" --token "${REG_TOKEN}" --labels "${RUNNER_LABELS}"
else
  ./config.sh --unattended --ephemeral --url "${RUNNER_URL}" --token "${REG_TOKEN}"
fi

# Evidence
if command -v jq >/dev/null 2>&1; then
  log_runner_evidence "runner_ephemeral_start" "$(jq -nc \
    --arg url "${RUNNER_URL}" \
    --arg labels "${RUNNER_LABELS}" \
    --arg version "${RUNNER_VERSION}" \
    '{url:$url,labels:$labels,version:$version,mode:"ephemeral"}')"
else
  log_runner_evidence "runner_ephemeral_start" "{\"url\":\"${RUNNER_URL}\",\"labels\":\"${RUNNER_LABELS}\",\"version\":\"${RUNNER_VERSION}\",\"mode\":\"ephemeral\"}"
fi

echo "[ephemeral] Starting runner. It will process a single job and exit automatically."
./run.sh
echo "[ephemeral] Runner exited (ephemeral job complete)."
