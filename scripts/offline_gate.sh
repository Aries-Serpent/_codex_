#!/bin/bash
# Offline gate script for Zendesk Codex integration

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR"

echo "Running unit and e2e tests..."
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests

echo "All tests passed. Ready for manual review."
