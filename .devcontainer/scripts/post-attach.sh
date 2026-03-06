#!/usr/bin/env bash
# .devcontainer/scripts/post-attach.sh
# ─────────────────────────────────────────────────────────────────────────────
# Runs every time a user/agent ATTACHES to the Codespace (new terminal, VS Code
# reconnect, etc.). Prints the Copilot agent quick-start banner.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

WORKSPACE="${CODESPACE_VSCODE_FOLDER:-/workspaces/_codex_}"

# Source env so token vars are visible
[ -f "$HOME/.codex_env" ] && source "$HOME/.codex_env" 2>/dev/null || true

# ── Server health ─────────────────────────────────────────────────────────────
SERVER_UP=false
curl -sf http://localhost:8765/api/health > /dev/null 2>&1 && SERVER_UP=true

# ── Banner ────────────────────────────────────────────────────────────────────
cat << 'BANNER'

╔══════════════════════════════════════════════════════════════════════════╗
║        🧠  CODEX — COPILOT AGENT CODESPACE  (S114)                      ║
╚══════════════════════════════════════════════════════════════════════════╝
BANNER

echo "  Workspace  : $WORKSPACE"
echo "  Python     : $(python --version 2>&1 | cut -d' ' -f2)"
echo "  Branch     : $(git -C "$WORKSPACE" rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
echo ""

# ── Service status ────────────────────────────────────────────────────────────
echo "  Services:"
if $SERVER_UP; then
    echo "    ✅  Cognitive Brain CLI API  → http://localhost:8765"
    echo "        BrainClient.is_available() → True"
else
    echo "    ❌  CLI API server NOT running"
    echo "        Restart: bash .devcontainer/scripts/post-start.sh"
fi
echo ""

# ── Token status ──────────────────────────────────────────────────────────────
echo "  Auth tokens:"
for VAR in CODEX_MASTER_KEY CODEX_BACKUP_KEY _GITHUB_APP_ID WEBHOOK_SECRET; do
    VAL="${!VAR:-}"
    if [ -n "$VAL" ]; then
        printf "    ✅  %-32s set\n" "$VAR"
    else
        printf "    ❌  %-32s NOT SET\n" "$VAR"
    fi
done
echo ""

# ── Quick-start commands ──────────────────────────────────────────────────────
cat << 'QUICKSTART'
  Quick-start:
    # Verify CLI server
    curl -s http://localhost:8765/api/health | python3 -m json.tool

    # Use BrainClient
    python3 -c "from codex.agents.brain_client import BrainClient; b=BrainClient(); print(b.is_available())"

    # Use GitHub App
    python3 -c "
    import os
    from codex.auth.github_app import GitHubApp, GitHubAppConfig, _resolve_github_token
    print('Token chain:')
    for val, name in _resolve_github_token():
        print(f'  {name}: {\"✅\" if val else \"❌\"}')"

    # Run auth tests
    python3 -m pytest tests/auth/ -q

  Docs:
    cat docs/agent/CODESPACE_COPILOT_AGENT_GUIDE.md
    cat docs/agent/GITHUB_APP_CLI_MAPPING.md
    cat docs/agent/COPILOT_TOKEN_GUIDE.md

══════════════════════════════════════════════════════════════════════════
QUICKSTART
