#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/tools/bootstrap_dev_env.sh"
pre-commit run --all-files
pytest
