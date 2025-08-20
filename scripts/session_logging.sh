#!/usr/bin/env bash
# Backwards compatibility wrapper for session logging.
# Sources session_hooks.sh which implements the actual logic.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./session_hooks.sh
. "$SCRIPT_DIR/session_hooks.sh"
