#!/usr/bin/env bash
set -euo pipefail

# Standard environment toggles for local CI / Codex runs.
# - PIP_CACHE_DIR: ensures pip (and uv's pip interface) reuse a stable cache path.
# - NOX_PREFER_UV: opt-in to `uv`-backed workflows when available.
# - UV_SYNC_FILE: default sync target for `uv pip sync` (tests_sys session).
#
# Usage:
#   source tools/ci_env.sh
#   make fast-tests
#
# Refs:
#   Nox reuse & backends / --no-venv: official docs. :contentReference[oaicite:8]{index=8}
#   uv pip sync/compile (lockfile-driven installs). :contentReference[oaicite:9]{index=9}
#   pip cache env var (PIP_CACHE_DIR). :contentReference[oaicite:10]{index=10}

# Prefer a project-local cache to persist wheels across runs.
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-$(pwd)/.cache/pip}"

# Opt-in to uv as preferred backend and installer if available.
export NOX_PREFER_UV="${NOX_PREFER_UV:-1}"

# Default sync target if not already set; only used when file exists.
if [[ -z "${UV_SYNC_FILE:-}" ]]; then
  if [[ -f "requirements.txt" ]]; then
    export UV_SYNC_FILE="requirements.txt"
  fi
fi

echo "PIP_CACHE_DIR=${PIP_CACHE_DIR}"
echo "NOX_PREFER_UV=${NOX_PREFER_UV}"
echo "UV_SYNC_FILE=${UV_SYNC_FILE:-<unset>}"
