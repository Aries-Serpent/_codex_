#!/usr/bin/env bash
set -euo pipefail

# Invariant banner
echo ">> Running Codex sequence locally (offline)."
echo ">> DO NOT ACTIVATE ANY GitHub Actions. All checks run here."

export CODEX_OFFLINE_CI=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export HF_HUB_DISABLE_TELEMETRY=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found." >&2
  exit 1
fi

python3 "${SCRIPT_DIR}/codex_seq_runner.py" "$@"
