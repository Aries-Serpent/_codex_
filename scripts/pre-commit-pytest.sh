#!/usr/bin/env bash
set -euo pipefail

# temporary directory for isolated test run
TMP_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# copy repository excluding .git directory
rsync -a --exclude '.git' . "$TMP_DIR"/

(
    cd "$TMP_DIR"
    PYTHONDONTWRITEBYTECODE=1 pytest -q
)
