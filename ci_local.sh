#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/tools/bootstrap_dev_env.sh"
source "$HERE/.venv/bin/activate" 2>/dev/null || true
.venv/bin/pre-commit run --all-files
.venv/bin/pytest

