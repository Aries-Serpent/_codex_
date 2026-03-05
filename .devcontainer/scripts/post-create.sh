#!/usr/bin/env bash
# .devcontainer/scripts/post-create.sh
# ─────────────────────────────────────────────────────────────────────────────
# Phase 5+6 equivalent of copilot-setup-steps.yml
# Runs ONCE after update-content on first create, and after every rebuild.
#
# Mirrors:
#   - Phase 6: Set Codex Environment Variables
#   - Phase 6: Export Auth Tokens to Agent Environment
#   - Phase 6: Load Custom Agent Configuration
#   - Phase 7: Validate Environment Setup
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

WORKSPACE="${CODESPACE_VSCODE_FOLDER:-/workspaces/_codex_}"
cd "$WORKSPACE"

echo "══════════════════════════════════════════════════════════"
echo "  Codex Codespace — post-create (Phase 5+6+7)"
echo "══════════════════════════════════════════════════════════"

# ── Write persistent env vars to ~/.bashrc and ~/.profile ────────────────────
# This mirrors "Set Codex Environment Variables" from copilot-setup-steps.yml.
# In Codespaces, GITHUB_ENV does not exist — we write to shell profiles instead.

PROFILE_SNIPPET="$HOME/.codex_env"
cat > "$PROFILE_SNIPPET" << ENVEOF
# Codex Copilot Agent environment — written by post-create.sh
export CODEX_ENV="codespace-copilot-agent"
export CODEX_FORCE_CPU="1"
export RAG_EMBEDDING_PROVIDER="tfidf"
export CODEX_LOG_LEVEL="INFO"
export CODEX_DB_PATH="${WORKSPACE}/.codex/codex.db"
export CODEX_SESSION_LOG_DIR="${WORKSPACE}/.codex/sessions"
export CODEX_CLI_API_URL="http://localhost:8765"
export COPILOT_CLI_BASE_URL="http://localhost:8765"
export GITHUB_COPILOT_AGENT="true"
export PYTHONPATH="${WORKSPACE}/src:\${PYTHONPATH:-}"
export PYTHONUNBUFFERED="1"
export PIP_NO_INPUT="1"
export DEBIAN_FRONTEND="noninteractive"
export GIT_LFS_SKIP_SMUDGE="1"
ENVEOF

# Source from both bash profiles so env is available in all terminals
for RC in "$HOME/.bashrc" "$HOME/.profile" "$HOME/.bash_profile"; do
    if ! grep -q "codex_env" "$RC" 2>/dev/null; then
        echo "source ${PROFILE_SNIPPET}" >> "$RC"
    fi
done
echo "✅ Environment variables written to $PROFILE_SNIPPET"

# ── Auth token report ─────────────────────────────────────────────────────────
# Mirrors "Export Auth Tokens" step.
# Codespaces secrets are already in the environment — just report what's set.
echo ""
echo "── Auth token status ──────────────────────────────────────────────────"
_report_token() {
    local name="$1"
    local val="${!name:-}"
    if [ -n "$val" ]; then
        echo "  ✅ ${name} is set (${#val} chars)"
    else
        echo "  ❌ ${name} is NOT set"
        echo "     → Add it at: Settings → Codespaces → Secrets"
    fi
}
_report_token "CODEX_MASTER_KEY"
_report_token "CODEX_BACKUP_KEY"
_report_token "CODEX_ADMIN_KEY"
_report_token "GITHUB_APP_ID"
_report_token "GITHUB_APP_PRIVATE_KEY"
_report_token "WEBHOOK_SECRET"

# Write a non-secret summary to .codex/codespace_auth_status.json
AUTH_STATUS_FILE="${WORKSPACE}/.codex/codespace_auth_status.json"
python3 - << PYEOF
import json, os, time
secrets = [
    "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "CODEX_ADMIN_KEY",
    "GITHUB_APP_ID", "GITHUB_APP_PRIVATE_KEY", "GITHUB_APP_INSTALLATION_ID",
    "WEBHOOK_SECRET", "WEBHOOK_RECEIVER_URL",
]
status = {s: bool(os.environ.get(s)) for s in secrets}
data = {
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "environment": "codespace",
    "token_status": status,
    "all_required_set": all(status.get(k) for k in ["CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"]),
}
os.makedirs(os.path.dirname("${AUTH_STATUS_FILE}"), exist_ok=True)
with open("${AUTH_STATUS_FILE}", "w") as f:
    json.dump(data, f, indent=2)
print(f"  Auth status written → ${AUTH_STATUS_FILE}")
PYEOF

# ── Load agent context from .codex/agent_context.json ────────────────────────
# Mirrors "Inject Repo Variable Context" step.
if [ -f "${WORKSPACE}/.codex/agent_context.json" ]; then
    echo ""
    echo "── Repo variable context ──────────────────────────────────────────────"
    python3 - << 'PYEOF'
import json, os
ctx_path = os.path.join(os.environ.get("WORKSPACE", "/workspaces/_codex_"),
                        ".codex/agent_context.json")
try:
    with open(ctx_path) as f:
        ctx = json.load(f)
    print(f"  agent_context.json loaded — {len(ctx)} keys")
    for k, v in list(ctx.items())[:5]:
        print(f"    {k}: {str(v)[:60]}")
    if len(ctx) > 5:
        print(f"    … and {len(ctx)-5} more")
except Exception as e:
    print(f"  ⚠️  Could not load agent_context.json: {e}")
PYEOF
fi

# ── Load custom agent config ──────────────────────────────────────────────────
if [ -f "${WORKSPACE}/.codex/agent_environment_config.yaml" ]; then
    echo ""
    echo "── Custom agent config (.codex/agent_environment_config.yaml) ─────────"
    head -20 "${WORKSPACE}/.codex/agent_environment_config.yaml" || true
fi

# ── Validate environment ──────────────────────────────────────────────────────
echo ""
echo "── Environment validation ─────────────────────────────────────────────"
echo "  Python : $(python --version)"
echo "  Pip    : $(pip --version | cut -d' ' -f1-2)"
echo "  Node   : $(node --version 2>/dev/null || echo 'not installed')"
echo "  Rust   : $(rustc --version 2>/dev/null || echo 'not installed')"
echo "  gh CLI : $(gh --version 2>/dev/null | head -1 || echo 'not installed')"
echo "  ruff   : $(ruff --version 2>/dev/null || echo 'not installed')"
python3 -c "from codex.auth.github_app import GitHubApp; print('  auth.github_app: ✅ importable')" 2>/dev/null || \
    echo "  auth.github_app: ⚠️  not importable (run update-content)"
python3 -c "from codex.agents.brain_client import BrainClient; print('  brain_client: ✅ importable')" 2>/dev/null || \
    echo "  brain_client: ⚠️  not importable"

echo ""
echo "✅ post-create complete"
echo ""
echo "Next step: post-start.sh will launch the CLI API server on :8765"
