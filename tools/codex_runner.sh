#!/usr/bin/env bash
set -euo pipefail

# DO NOT ACTIVATE ANY GitHub Actions files. Local only.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/.." && pwd)"

cd "$root"

if [[ ! -d .venv ]]; then
  python -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pytest pytest-cov pre-commit black isort flake8 mypy charset-normalizer chardet

# Optional: first-time pre-commit install (local)
pre-commit install || true

python tools/codex_task_runner.py "$@"
