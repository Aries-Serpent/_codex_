#!/usr/bin/env bash
set -euo pipefail
# Deterministic bootstrap for local gates (pre-commit + pytest).
# Creates .venv if missing, upgrades pip, installs repo + dev deps,
# and ensures CLIs invoked by hooks are present.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$HERE"
VENV="${VENV:-.venv}"
PY="${PYTHON:-python3}"

if [[ ! -d "$VENV" ]]; then "$PY" -m venv "$VENV"; fi
source "$VENV/bin/activate"
python -m pip install --upgrade pip setuptools wheel
# Project + dev requirements via lockfile
if command -v uv >/dev/null 2>&1; then
  uv pip install --locked -r requirements.txt -r requirements-dev.txt
else
  pip install -r requirements.lock
fi
# Gate CLIs used by hooks / logs: pre-commit, yamllint, shellcheck, semgrep, pip-audit
pip install pre-commit yamllint shellcheck-py semgrep pip-audit
# Pre-install hook envs so first run is deterministic
pre-commit install --install-hooks --overwrite
echo "[bootstrap] Ready. Run: pre-commit run --all-files && pytest"
