#!/bin/bash
# === BEGIN_CODEX_SESSION_LOGGING ===

# Best-effort session logging (safe no-op on failure)

# Requires Python available in PATH.

if command -v python3 >/dev/null 2>&1; then PYTHON=python3; else PYTHON=python; fi
: "${CODEX_SESSION_ID:=$(date +%s)}"
($PYTHON -m codex.logging.session_logger --event start --session-id "$CODEX_SESSION_ID") >/dev/null 2>&1 || true

# On exit, log end once.

trap '($PYTHON -m codex.logging.session_logger --event end --session-id "$CODEX_SESSION_ID") >/dev/null 2>&1 || true' EXIT

# === END_CODEX_SESSION_LOGGING ===


echo "=================================="
echo "Welcome to openai/codex-universal!"
echo "=================================="

/opt/codex/setup_universal.sh

echo "Environment ready. Dropping you into a bash shell."
exec bash --login "$@"
