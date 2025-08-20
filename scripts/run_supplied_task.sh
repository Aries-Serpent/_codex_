#!/usr/bin/env bash
set -euo pipefail

export DO_NOT_ACTIVATE_GITHUB_ACTIONS=true
export SAFE_WRITE=true
export DRY_RUN=false

python tools/codex_supplied_task_runner.py --apply "$@"
