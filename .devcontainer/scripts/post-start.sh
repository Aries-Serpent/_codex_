#!/usr/bin/env bash
# .devcontainer/scripts/post-start.sh
# ─────────────────────────────────────────────────────────────────────────────
# Phase 7 equivalent of copilot-setup-steps.yml
# Runs every time the Codespace container STARTS (first create + every resume).
# Perfect for starting background services.
#
# Mirrors:
#   - "Start CLI API Server (background)" step
#   - Auth token forwarding to server process
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

WORKSPACE="${CODESPACE_VSCODE_FOLDER:-/workspaces/_codex_}"
CLI_API_PORT=8765
cd "$WORKSPACE"

# Source env profile so exported vars are available
# shellcheck source=/dev/null
[ -f "$HOME/.codex_env" ] && source "$HOME/.codex_env"

# ── 0. Install safe_git_show guard (mirrors copilot-setup-steps.yml) ──────────
if [ -f "${WORKSPACE}/scripts/ci/safe_git_show.sh" ]; then
    install -m 0755 "${WORKSPACE}/scripts/ci/safe_git_show.sh" /usr/local/bin/safe_git_show.sh 2>/dev/null \
        || { cp "${WORKSPACE}/scripts/ci/safe_git_show.sh" /usr/local/bin/safe_git_show.sh && chmod 0755 /usr/local/bin/safe_git_show.sh; } \
        || true
    ln -sf /usr/local/bin/safe_git_show.sh /usr/local/bin/safe_git_show 2>/dev/null || true
    echo "  ✅ safe_git_show installed on PATH"
else
    echo "  ⚠️  scripts/ci/safe_git_show.sh not found — safe_git_show unavailable"
fi

echo "══════════════════════════════════════════════════════════"
echo "  Codex Codespace — post-start"
echo "  Starting background services…"
echo "══════════════════════════════════════════════════════════"

# ── 1. Kill any stale server instance from a previous session ─────────────────
pkill -f "cli_api_server" 2>/dev/null || true
sleep 1

# ── 2. Ensure fastapi + uvicorn are available (idempotent) ────────────────────
pip install --cache-dir "$HOME/.cache/pip" \
    "fastapi>=0.110.0,<1.0" \
    "uvicorn[standard]>=0.29.0,<1.0" \
    "httpx>=0.27.0,<1.0" \
    --quiet 2>/dev/null || true

# ── 3. Start the Cognitive Brain CLI API server ────────────────────────────────
# Exactly mirrors the nohup block in copilot-setup-steps.yml.
# Auth tokens are forwarded explicitly (pattern from Phase 6 of setup-steps).
LOG_FILE="${WORKSPACE}/.codex/cli_api_server.log"
mkdir -p "$(dirname "$LOG_FILE")"

export CODEX_MASTER_KEY="${CODEX_MASTER_KEY:-}"
export CODEX_BACKUP_KEY="${CODEX_BACKUP_KEY:-}"
export AGENT_GITHUB_TOKEN="${GITHUB_TOKEN:-}"
export CODEX_DB_PATH="${WORKSPACE}/.codex/codex.db"
export CODEX_SESSION_LOG_DIR="${WORKSPACE}/.codex/sessions"
export PYTHONPATH="${WORKSPACE}/src:${PYTHONPATH:-}"

nohup uvicorn cognitive_app.src.server.cli_api_server:app \
    --host 0.0.0.0 \
    --port "${CLI_API_PORT}" \
    --log-level warning \
    > "$LOG_FILE" 2>&1 &
CLI_API_PID=$!
echo "$CLI_API_PID" > "${WORKSPACE}/.codex/cli_api_server.pid"
echo "  Started CLI API server (PID=${CLI_API_PID}) → $LOG_FILE"

# ── 4. Health-check with retry (matches setup-steps.yml 5-second retry loop) ──
SERVER_READY=0
for i in 1 2 3 4 5; do
    sleep 1
    if curl -sf "http://localhost:${CLI_API_PORT}/api/health" > /dev/null 2>&1; then
        SERVER_READY=1
        break
    fi
done

if [ "$SERVER_READY" = "1" ]; then
    echo "  ✅ CLI API server ready on http://localhost:${CLI_API_PORT}"
    # Auth token report (mirrors copilot-setup-steps.yml auth banner)
    if   [ -n "${CODEX_MASTER_KEY:-}" ]; then
        echo "  🔑 Auth: CODEX_MASTER_KEY active (full PAT — variables/secrets API ✅)"
    elif [ -n "${CODEX_BACKUP_KEY:-}" ]; then
        echo "  🔑 Auth: CODEX_BACKUP_KEY active (fallback PAT)"
    elif [ -n "${GITHUB_TOKEN:-}" ]; then
        echo "  🔑 Auth: GITHUB_TOKEN active (actions scope)"
    else
        echo "  ⚠️  No auth token — GitHub API calls will be rate-limited"
    fi
else
    echo "  ⚠️  CLI API server did not respond after 5 s"
    echo "  Check logs: cat ${LOG_FILE}"
    # Non-fatal — Copilot agent can still work without the server
fi

# ── 4b. Auto-update Codespace-scoped repo variables ──────────────────────────
# If running in a Codespace, construct the public forwarded URL and update
# the repo variable so GitHub webhooks can deliver to this Codespace.
# Also records the active Codespace name so tooling can reference it.
if [ -n "${CODESPACE_NAME:-}" ]; then
    PUBLIC_URL="https://${CODESPACE_NAME}-${CLI_API_PORT}.preview.app.github.dev/webhook/github"
    echo "  🌐 Codespace detected — updating Codespace-scoped repo variables"
    echo "     CODESPACE_NAME: ${CODESPACE_NAME}"
    echo "     WEBHOOK_RECEIVER_URL: ${PUBLIC_URL}"

    # Determine which token to use for gh CLI authentication
    GH_TOKEN_FOR_VAR=""
    if [ -n "${CODEX_MASTER_KEY:-}" ]; then
        GH_TOKEN_FOR_VAR="${CODEX_MASTER_KEY}"
        echo "     Token: CODEX_MASTER_KEY"
    elif [ -n "${GITHUB_TOKEN:-}" ]; then
        GH_TOKEN_FOR_VAR="${GITHUB_TOKEN}"
        echo "     Token: GITHUB_TOKEN"
    fi

    if [ -n "${GH_TOKEN_FOR_VAR}" ]; then
        # Update WEBHOOK_RECEIVER_URL
        if GH_TOKEN="${GH_TOKEN_FOR_VAR}" gh variable set WEBHOOK_RECEIVER_URL \
            --body "${PUBLIC_URL}" \
            --repo Aries-Serpent/_codex_ 2>&1; then
            echo "  ✅ WEBHOOK_RECEIVER_URL updated"
        else
            echo "  ⚠️  Failed to update WEBHOOK_RECEIVER_URL"
            echo "     Manual fix: gh variable set WEBHOOK_RECEIVER_URL --body '${PUBLIC_URL}' --repo Aries-Serpent/_codex_"
        fi

        # Update CODEX_ACTIVE_CODESPACE — records the current Codespace name
        # (changes on every new Codespace; stale after Codespace deletion)
        if GH_TOKEN="${GH_TOKEN_FOR_VAR}" gh variable set CODEX_ACTIVE_CODESPACE \
            --body "${CODESPACE_NAME}" \
            --repo Aries-Serpent/_codex_ 2>&1; then
            echo "  ✅ CODEX_ACTIVE_CODESPACE updated → ${CODESPACE_NAME}"
        else
            echo "  ⚠️  Failed to update CODEX_ACTIVE_CODESPACE"
            echo "     Manual fix: gh variable set CODEX_ACTIVE_CODESPACE --body '${CODESPACE_NAME}' --repo Aries-Serpent/_codex_"
        fi
    else
        echo "  ⚠️  No token available to update repo variables"
        echo "     Set CODEX_MASTER_KEY as a Codespace secret, then restart the Codespace."
        echo "     Manual fix: gh variable set WEBHOOK_RECEIVER_URL --body '${PUBLIC_URL}' --repo Aries-Serpent/_codex_"
        echo "     Manual fix: gh variable set CODEX_ACTIVE_CODESPACE --body '${CODESPACE_NAME}' --repo Aries-Serpent/_codex_"
    fi

    # Attempt to make port visible to the organization for webhook delivery.
    gh codespace ports visibility "${CLI_API_PORT}:org" -c "${CODESPACE_NAME}" 2>/dev/null || \
        echo "  ⚠️  Could not auto-set port ${CLI_API_PORT} to org visibility. Manually adjust it in the Ports panel if needed."
else
    echo "  ℹ️  Not running in Codespace — Codespace-scoped repo variables not updated"
fi

# ── 5. Verify GitHub App credentials are available ────────────────────────────
if [ -n "${_GITHUB_APP_ID:-}" ] && [ -n "${_GITHUB_APP_PRIVATE_KEY:-}" ]; then
    GITHUB_APP_ID="${_GITHUB_APP_ID}" GITHUB_APP_PRIVATE_KEY="${_GITHUB_APP_PRIVATE_KEY}" \
    python3 - << 'PYEOF' 2>/dev/null && echo "  ✅ GitHub App JWT generation: OK" || echo "  ⚠️  GitHub App JWT: check _GITHUB_APP_PRIVATE_KEY format"
import os
from codex.auth.github_app import GitHubApp, GitHubAppConfig
cfg = GitHubAppConfig(
    app_id=int(os.environ["GITHUB_APP_ID"]),
    private_key_pem=os.environ["GITHUB_APP_PRIVATE_KEY"],
)
app = GitHubApp(cfg)
jwt = app.generate_jwt()
assert len(jwt.split(".")) == 3
PYEOF
fi

# ── 6. Write Codespace environment report ────────────────────────────────────
CODESPACE_REPORT="${WORKSPACE}/.codex/.copilot-agent-environment-report.txt"
mkdir -p "$(dirname "${CODESPACE_REPORT}")"
{
  echo "# Copilot Agent Environment Report (Codespace)"
  echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# Codespace: ${CODESPACE_NAME:-local}"
  echo ""
  echo "## safe_git_show"
  if command -v safe_git_show >/dev/null 2>&1; then
    echo "STATUS=ready"
    echo "PATH=$(command -v safe_git_show)"
  else
    echo "STATUS=degraded"
    echo "REASON=safe_git_show not found on PATH"
  fi
  echo ""
  echo "## CLI API"
  if [ "$SERVER_READY" = "1" ]; then
    echo "STATUS=ready"
    echo "URL=http://localhost:${CLI_API_PORT}"
  else
    echo "STATUS=degraded"
    echo "REASON=CLI API did not become ready after 5s"
  fi
} > "${CODESPACE_REPORT}"
echo "  ✅ Environment report written → ${CODESPACE_REPORT}"

echo "✅ post-start complete"
