#!/usr/bin/env bash
set -euo pipefail

cleanup() {
    rm -f .coverage 2>/dev/null || true
    rm -rf .pytest_cache .artifacts parquet 2>/dev/null || true
    find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
    GIT_LFS_SKIP_SMUDGE=1 git checkout -- .codex/action_log.ndjson 2>/dev/null || true
}
trap cleanup EXIT

export PYTHONDONTWRITEBYTECODE=1
pytest -q -p no:cacheprovider
