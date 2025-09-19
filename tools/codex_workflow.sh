#!/usr/bin/env bash
# End-to-end wrapper (no GitHub Actions). Runs locally in the Codex env.
set -euo pipefail

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip wheel setuptools
python -m pip install pre-commit==4.0.1 pytest==8.4.1 pytest-cov==7.0.0 coverage

python tools/codex_workflow.py "$@"
