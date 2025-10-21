#!/usr/bin/env bash
# Bootstrap a GitHub Actions self-hosted runner under the current user.
# Requirements: curl, tar; optional: systemd for service management.
#
# Usage:
#   bash scripts/runner/actions_runner_bootstrap.sh \
#     --url "https://github.com/Aries-Serpent" \
#     [--token "<REGISTRATION_TOKEN>"] \
#     --labels "self-hosted,linux,docker" \
#     --version "2.329.0" \
#     --svc "systemd"
#
# Token logic:
# - If --token is omitted, the script will auto-request a short-lived
#   registration token using GH_PAT (preferred) or _CODEX_BOT_RUNNER (fallback)
#   against the provided --url.
#   Repo URL → POST /repos/{owner}/{repo}/actions/runners/registration-token
#   Org URL  → POST /orgs/{org}/actions/runners/registration-token
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
# shellcheck source=evidence.sh
source "${SCRIPT_DIR}/evidence.sh"

RUNNER_URL=""
RUNNER_TOKEN=""
RUNNER_LABELS="self-hosted,linux"
RUNNER_VERSION="2.329.0"
SERVICE_MODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url) RUNNER_URL="$2"; shift 2 ;;
    --token) RUNNER_TOKEN="$2"; shift 2 ;;
    --labels) RUNNER_LABELS="$2"; shift 2 ;;
    --version) RUNNER_VERSION="$2"; shift 2 ;;
    --svc) SERVICE_MODE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac

done

if [[ -z "${RUNNER_URL}" ]]; then
  echo "Usage: $0 --url <https://github.com/org_or_repo> [--token <REGISTRATION_TOKEN>] [--labels ...] [--version ...] [--svc systemd]" >&2
  exit 2
fi

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command '$1' not found" >&2
    exit 1
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

RUNNER_DIR="${HOME}/actions-runner"
mkdir -p "${RUNNER_DIR}"
cd "${RUNNER_DIR}"

require_cmd curl
require_cmd tar

PKG="actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
PKG_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${PKG}"

if [[ ! -f "${PKG}" ]]; then
  echo "[runner] Downloading ${PKG_URL}"
  curl -fsSL -o "${PKG}" "${PKG_URL}"
else
  echo "[runner] Using cached ${PKG}"
fi

tar xzf "${PKG}"

# Resolve registration token if not provided
if [[ -z "${RUNNER_TOKEN}" ]]; then
  pat="$(resolve_pat || true)"
  if [[ -z "${pat}" ]]; then
    echo "[runner] ERROR: No --token provided and neither GH_PAT nor _CODEX_BOT_RUNNER are set." >&2
    exit 1
  fi
  echo "[runner] Requesting registration token for ${RUNNER_URL}"
  read -r owner repo <<<"$(parse_owner_repo "${RUNNER_URL}")"
  if [[ -z "${owner}" ]]; then
    echo "[runner] ERROR: Unable to parse owner from URL ${RUNNER_URL}" >&2
    exit 1
  fi
  if [[ -n "${repo}" ]]; then
    endpoint="https://api.github.com/repos/${owner}/${repo}/actions/runners/registration-token"
  else
    endpoint="https://api.github.com/orgs/${owner}/actions/runners/registration-token"
  fi
  json="$(api_call POST "${endpoint}" || true)"
  RUNNER_TOKEN="$(echo "${json}" | tr -d '\n' | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')"
  if [[ -z "${RUNNER_TOKEN}" ]]; then
    echo "[runner] ERROR: Failed to obtain a registration token. Ensure PAT has sufficient permissions." >&2
    exit 1
  fi
fi

echo "[runner] Configuring runner:"
echo "  URL    : ${RUNNER_URL}"
echo "  Labels : ${RUNNER_LABELS}"
./config.sh --unattended --replace --url "${RUNNER_URL}" --token "${RUNNER_TOKEN}" --labels "${RUNNER_LABELS}"

# Evidence
if command -v jq >/dev/null 2>&1; then
  log_runner_evidence "runner_bootstrap" "$(jq -nc \
    --arg url "${RUNNER_URL}" \
    --arg labels "${RUNNER_LABELS}" \
    --arg version "${RUNNER_VERSION}" \
    '{url:$url,labels:$labels,version:$version}')"
else
  log_runner_evidence "runner_bootstrap" "{\"url\":\"${RUNNER_URL}\",\"labels\":\"${RUNNER_LABELS}\",\"version\":\"${RUNNER_VERSION}\"}"
fi

install_service() {
  local svc_user="$1"
  local template_path="${SCRIPT_DIR}/_svc_template.actions-runner@.service"
  local svc_dir="/etc/systemd/system"
  local svc_file="actions-runner@.service"

  if [[ $(id -u) -eq 0 ]]; then
    if [[ -f "${template_path}" ]]; then
      install -m 0644 -T "${template_path}" "${svc_dir}/${svc_file}"
    else
      cat > "${svc_dir}/${svc_file}" <<'UNIT'
[Unit]
Description=GitHub Actions Runner for %i
After=network.target docker.service
Wants=docker.service

[Service]
User=%i
WorkingDirectory=%h/actions-runner
Environment=DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
ExecStart=%h/actions-runner/run.sh
KillMode=process
TimeoutStopSec=10
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
    fi
    systemctl daemon-reload
    systemctl enable "actions-runner@${svc_user}"
    systemctl start "actions-runner@${svc_user}"
    systemctl status "actions-runner@${svc_user}" --no-pager || true
  else
    if ! command -v sudo >/dev/null 2>&1; then
      echo "Systemd service install requires root privileges or sudo access." >&2
      echo "To run interactively: ./run.sh" >&2
      exit 1
    fi
    if [[ -f "${template_path}" ]]; then
      sudo install -m 0644 -T "${template_path}" "${svc_dir}/${svc_file}"
    else
      sudo tee "${svc_dir}/${svc_file}" >/dev/null <<'UNIT'
[Unit]
Description=GitHub Actions Runner for %i
After=network.target docker.service
Wants=docker.service

[Service]
User=%i
WorkingDirectory=%h/actions-runner
Environment=DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
ExecStart=%h/actions-runner/run.sh
KillMode=process
TimeoutStopSec=10
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
    fi
    sudo systemctl daemon-reload
    sudo systemctl enable "actions-runner@${svc_user}"
    sudo systemctl start "actions-runner@${svc_user}"
    sudo systemctl status "actions-runner@${svc_user}" --no-pager || true
  fi
}

if [[ "${SERVICE_MODE}" == "systemd" ]]; then
  echo "[runner] Installing systemd service actions-runner@${USER}"
  install_service "${USER}"
else
  echo "[runner] Starting interactively with ./run.sh (Ctrl+C to stop)"
  ./run.sh
fi
