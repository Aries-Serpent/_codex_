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
_report_token "_GITHUB_APP_ID"
_report_token "_GITHUB_APP_PRIVATE_KEY"
_report_token "WEBHOOK_SECRET"

# Write a non-secret summary to .codex/codespace_auth_status.json
AUTH_STATUS_FILE="${WORKSPACE}/.codex/codespace_auth_status.json"
python3 - << PYEOF
import json, os, time
secrets = [
    "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "CODEX_ADMIN_KEY",
    "_GITHUB_APP_ID", "_GITHUB_APP_PRIVATE_KEY", "_GITHUB_APP_INSTALLATION_ID",
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

# ── L6 agent venv (.venv_agent) ─────────────────────────────────────────────
# Mirror the GitHub Actions L6b cache locally so the agent env is always ready.
# The volume `codex-agent-venv` persists across rebuilds — only re-installs
# when requirements/agent.txt or pyproject.toml have changed.
echo ""
echo "── Copilot agent venv (.venv_agent) ───────────────────────────────────"
AGENT_VENV="${WORKSPACE}/.venv_agent"
AGENT_REQ="${WORKSPACE}/requirements/agent.txt"
AGENT_STAMP="${WORKSPACE}/.venv_agent/.build-stamp"
CURRENT_HASH=$(sha256sum "${AGENT_REQ}" "${WORKSPACE}/pyproject.toml" 2>/dev/null | sha256sum | cut -d' ' -f1)

needs_build=false
if [ ! -d "${AGENT_VENV}" ] || [ ! -x "${AGENT_VENV}/bin/python" ]; then
    needs_build=true
    echo "  Agent venv missing or broken — building"
elif [ ! -f "${AGENT_STAMP}" ] || [ "$(cat ${AGENT_STAMP})" != "${CURRENT_HASH}" ]; then
    needs_build=true
    echo "  Agent requirements changed — rebuilding"
else
    echo "  Agent venv up-to-date ✅ (hash: ${CURRENT_HASH:0:12}…)"
fi

if [ "$needs_build" = "true" ]; then
    [ -d "${AGENT_VENV}" ] && { chmod -R u+w "${AGENT_VENV}" 2>/dev/null || true; rm -rf "${AGENT_VENV}"; }
    python -m venv "${AGENT_VENV}"
    "${AGENT_VENV}/bin/pip" install --cache-dir ~/.cache/pip -U pip setuptools wheel --quiet
    "${AGENT_VENV}/bin/pip" install --cache-dir ~/.cache/pip -r "${AGENT_REQ}" --quiet
    "${AGENT_VENV}/bin/pip" install --cache-dir ~/.cache/pip -e ".[dev]" --no-deps --quiet
    echo "${CURRENT_HASH}" > "${AGENT_STAMP}"
    echo "  Agent venv built ✅"
fi
echo "AGENT_VENV_PATH=${AGENT_VENV}" >> "${PROFILE_SNIPPET}"
echo "  AGENT_VENV_PATH=${AGENT_VENV}"

# ── cognitive_app npm dependencies ──────────────────────────────────────────
# node_modules volume persists; only re-installs when package.json changes.
echo ""
echo "── cognitive_app npm dependencies ─────────────────────────────────────"
if [ -f "${WORKSPACE}/cognitive_app/package.json" ]; then
    cd "${WORKSPACE}/cognitive_app"
    # Fast path: skip install if node_modules already up-to-date
    if [ ! -d node_modules ] || [ package.json -nt node_modules/.install-stamp 2>/dev/null ]; then
        echo "  Running npm install (cache: ~/.npm)…"
        npm install --prefer-offline --cache ~/.npm --loglevel=warn
        touch node_modules/.install-stamp
        echo "  npm install complete ✅"
    else
        echo "  node_modules up-to-date ✅"
    fi
    cd "${WORKSPACE}"
else
    echo "  cognitive_app/package.json not found — skipping"
fi

echo ""
echo "✅ post-create complete"
echo ""
echo "Next step: post-start.sh will launch the CLI API server on :8765"
