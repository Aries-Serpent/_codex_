#!/usr/bin/env bash
set -euo pipefail

# temporary directory for isolated test run
TMP_DIR="$(mktemp -d)"

cleanup() {
    rm -f "$TMP_DIR/.coverage" .coverage 2>/dev/null || true
    rm -rf "$TMP_DIR/.pytest_cache" .pytest_cache 2>/dev/null || true
    find "$TMP_DIR" . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# copy repository excluding .git directory
rsync -a --exclude '.git' . "$TMP_DIR"/

(
    cd "$TMP_DIR"
    PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE=/tmp/coverage tox -q -e py
)
