#!/bin/bash
# Offline gate script for Zendesk Codex integration

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR"

echo "Running offline Zendesk smoke tests..."
OFFLINE_TESTS=(
  "tests/unit/test_zendesk_models.py"
  "tests/e2e_offline/test_diff_and_apply.py"
)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q "${OFFLINE_TESTS[@]}"

echo "All offline smoke tests passed. Ready for manual review."
