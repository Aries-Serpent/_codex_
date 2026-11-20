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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "${SCRIPT_DIR}/../.." rev-parse --show-toplevel)"
WORKSPACE="${CODESPACE_VSCODE_FOLDER:-${REPO_ROOT}}"
CLI_API_PORT="${CODEX_CLI_API_PORT_NUMBER:-8765}"
if [ -n "${CODEX_CLI_API_BIND_HOST:-}" ]; then
    CLI_API_BIND_HOST="$CODEX_CLI_API_BIND_HOST"
elif [ -n "${CODESPACE_NAME:-}" ]; then
    CLI_API_BIND_HOST="0.0.0.0"
else
    CLI_API_BIND_HOST="127.0.0.1"
fi
LOCAL_CLI_API_URL="http://127.0.0.1:${CLI_API_PORT}"
cd "$WORKSPACE"

if [ -x "${WORKSPACE}/.venv/bin/python" ]; then
    PYTHON_BIN="${WORKSPACE}/.venv/bin/python"
else
    PYTHON_BIN="$(command -v python3.12 || command -v python3)"
fi
if [ -x "${WORKSPACE}/.venv/bin/uvicorn" ]; then
    UVICORN_BIN="${WORKSPACE}/.venv/bin/uvicorn"
else
    UVICORN_BIN="$(command -v uvicorn || true)"
fi

# Source env profile so exported vars are available
# shellcheck source=/dev/null
[ -f "$HOME/.codex_env" ] && source "$HOME/.codex_env"

# ── 0. Install safe_git_show guard (mirrors copilot-setup-steps.yml) ──────────
LOCAL_BIN="${HOME}/.local/bin"
mkdir -p "$LOCAL_BIN"
if [ -f "${WORKSPACE}/scripts/ci/safe_git_show.sh" ] && \
    install -m 0755 "${WORKSPACE}/scripts/ci/safe_git_show.sh" "${LOCAL_BIN}/safe_git_show"; then
    export PATH="${LOCAL_BIN}:${PATH}"
    echo "  ✅ safe_git_show installed at ${LOCAL_BIN}/safe_git_show"
else
    echo "  ⚠️  safe_git_show unavailable; startup continues in degraded mode"
fi

echo "══════════════════════════════════════════════════════════"
echo "  Codex Codespace — post-start"
echo "  Starting background services…"
echo "══════════════════════════════════════════════════════════"

CODEX_STATE_DIR="${CODEX_STATE_DIR:-${HOME}/.codex}"
export CODEX_RUNTIME_DIR="${CODEX_RUNTIME_DIR:-${CODEX_STATE_DIR}/runtime}"
mkdir -p "$CODEX_STATE_DIR" "$CODEX_RUNTIME_DIR"

# ── 1. Stop only services previously started by this workspace ────────────────
SERVER_PID_FILE="${CODEX_RUNTIME_DIR}/cli_api_server.pid"
UI_PID_FILE="${CODEX_RUNTIME_DIR}/cognitive_app.pid"
pid_is_workspace_process() {
    local pid="$1" marker="$2" command_line process_cwd
    [[ "$pid" =~ ^[0-9]+$ ]] || return 1
    [ -r "/proc/${pid}/cmdline" ] || return 1
    command_line="$(tr '\0' ' ' < "/proc/${pid}/cmdline")"
    process_cwd="$(readlink "/proc/${pid}/cwd" 2>/dev/null || true)"
    [[ "$command_line" == *"$marker"* ]] && \
        { [ "$process_cwd" = "$WORKSPACE" ] || [[ "$process_cwd" == "$WORKSPACE"/* ]]; }
}
stop_owned_process() {
    local pid_file="$1" marker="$2" label="$3" pid
    [ -f "$pid_file" ] || return 0
    pid="$(cat "$pid_file")"
    if pid_is_workspace_process "$pid" "$marker"; then
        kill "$pid" 2>/dev/null || true
        for _ in 1 2 3 4 5; do
            kill -0 "$pid" 2>/dev/null || break
        done
        kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" 2>/dev/null || true
        echo "  ✅ Stopped previous ${label} (PID=${pid})"
    else
        echo "  ⚠️  Ignoring stale or unrelated ${label} PID file"
    fi
    rm -f "$pid_file"
}
stop_owned_process "$SERVER_PID_FILE" "cognitive_app.src.server.cli_api_server:app" "CLI API server"
stop_owned_process "$UI_PID_FILE" "npm run dev" "Cognitive App"


# ── 2. Verify the lock-restored server runtime without mutating it ────────────
"$PYTHON_BIN" -c 'import fastapi, httpx, uvicorn'

# ── 3. Start the Cognitive Brain CLI API server ────────────────────────────────
# Exactly mirrors the nohup block in copilot-setup-steps.yml.
# Auth tokens are forwarded explicitly (pattern from Phase 6 of setup-steps).
LOG_FILE="${CODEX_RUNTIME_DIR}/cli_api_server.log"
mkdir -p "$(dirname "$LOG_FILE")" "$CODEX_STATE_DIR"

export CODEX_MASTER_KEY="${CODEX_MASTER_KEY:-}"
export CODEX_BACKUP_KEY="${CODEX_BACKUP_KEY:-}"
export AGENT_GITHUB_TOKEN="${GITHUB_TOKEN:-}"
export CODEX_DB_PATH="${CODEX_DB_PATH:-${CODEX_STATE_DIR}/codex.db}"
export CODEX_RUNTIME_DIR="${CODEX_RUNTIME_DIR:-${CODEX_STATE_DIR}/runtime}"
export CODEX_SESSION_LOG_DIR="${CODEX_SESSION_LOG_DIR:-${CODEX_STATE_DIR}/sessions}"
export PYTHONPATH="${WORKSPACE}/src:${PYTHONPATH:-}"
if [ -n "${CODESPACE_NAME:-}" ]; then
    CODESPACES_DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-preview.app.github.dev}"
    CODESPACE_UI_ORIGIN="https://${CODESPACE_NAME}-5173.${CODESPACES_DOMAIN}"
    CODEX_ALLOWED_ORIGINS="${CODEX_ALLOWED_ORIGINS:-http://localhost:5173,http://127.0.0.1:5173}"
    case ",${CODEX_ALLOWED_ORIGINS}," in
        *,"${CODESPACE_UI_ORIGIN}",*) ;;
        *) CODEX_ALLOWED_ORIGINS="${CODEX_ALLOWED_ORIGINS},${CODESPACE_UI_ORIGIN}" ;;
    esac
    export CODEX_ALLOWED_ORIGINS
fi

UI_BOOTSTRAP_BROWSER="$("$PYTHON_BIN" -c 'import secrets; print(secrets.token_urlsafe(32))')"
UI_BOOTSTRAP_MCP="$("$PYTHON_BIN" -c 'import secrets; print(secrets.token_urlsafe(32))')"
export CODEX_UI_BOOTSTRAP_TOKENS="${UI_BOOTSTRAP_BROWSER},${UI_BOOTSTRAP_MCP}"
UI_BOOTSTRAP_BROWSER_FILE="${CODEX_RUNTIME_DIR}/ui_bootstrap_browser"
UI_BOOTSTRAP_MCP_FILE="${CODEX_RUNTIME_DIR}/ui_bootstrap_mcp"
umask 077
printf '%s' "$UI_BOOTSTRAP_BROWSER" > "$UI_BOOTSTRAP_BROWSER_FILE"
printf '%s' "$UI_BOOTSTRAP_MCP" > "$UI_BOOTSTRAP_MCP_FILE"
chmod 0600 "$UI_BOOTSTRAP_BROWSER_FILE" "$UI_BOOTSTRAP_MCP_FILE"

if [ -n "$UVICORN_BIN" ]; then
    UVICORN_COMMAND=("$UVICORN_BIN")
else
    UVICORN_COMMAND=("$PYTHON_BIN" "-m" "uvicorn")
fi
export CODEX_STARTUP_NONCE="$("$PYTHON_BIN" -c 'import secrets; print(secrets.token_urlsafe(18))')"
nohup "${UVICORN_COMMAND[@]}" cognitive_app.src.server.cli_api_server:app \
    --host "${CLI_API_BIND_HOST}" \
    --port "${CLI_API_PORT}" \
    --log-level warning \
    > "$LOG_FILE" 2>&1 &
CLI_API_PID=$!
echo "$CLI_API_PID" > "$SERVER_PID_FILE"
echo "  Started CLI API server (PID=${CLI_API_PID}) → $LOG_FILE"

# ── 4. Health-check with retry (matches setup-steps.yml 5-second retry loop) ──
SERVER_READY=0
for i in 1 2 3 4 5; do
    sleep 1
    if ! kill -0 "$CLI_API_PID" 2>/dev/null; then
        break
    fi
    HEALTH_NONCE="$(
        "$PYTHON_BIN" -c 'import json, urllib.request, sys; print(json.load(urllib.request.urlopen(sys.argv[1], timeout=2)).get("startup_nonce", ""))' \
            "${LOCAL_CLI_API_URL}/api/health" 2>/dev/null || true
    )"
    if [ -n "$HEALTH_NONCE" ] && [ "$HEALTH_NONCE" = "$CODEX_STARTUP_NONCE" ]; then
        SERVER_READY=1
        break
    fi
done

if [ "$SERVER_READY" = "1" ]; then
    echo "  ✅ CLI API server ready on ${LOCAL_CLI_API_URL}"
    echo "  🔐 UI launch capability stored at ${UI_BOOTSTRAP_BROWSER_FILE} (mode 0600)"
    echo "     Append #codex_ui_bootstrap=<file-contents> to the Vite/Cognitive App URL."
    # Auth token report (mirrors copilot-setup-steps.yml auth banner)
    if   [ -n "${CODEX_MASTER_KEY:-}" ]; then
        echo "  🔑 Auth: CODEX_MASTER_KEY configured; live validity requires credential probe"
    elif [ -n "${CODEX_BACKUP_KEY:-}" ]; then
        echo "  🔑 Auth: CODEX_BACKUP_KEY configured; live validity requires credential probe"
    elif [ -n "${GITHUB_TOKEN:-}" ]; then
        echo "  🔑 Auth: GITHUB_TOKEN configured; live permissions require credential probe"
    else
        echo "  ⚠️  No auth token — GitHub API calls will be rate-limited"
    fi
else
    echo "  ❌ CLI API server failed ownership/health verification" >&2
    echo "  Check logs: cat ${LOG_FILE}" >&2
    if kill -0 "$CLI_API_PID" 2>/dev/null; then
        kill "$CLI_API_PID" 2>/dev/null || true
    fi
    rm -f "$SERVER_PID_FILE"
    exit 1
fi

# ── 4b. Start the Cognitive App when enabled by the Codespace contract ────────
if [ "${CODEX_START_COGNITIVE_APP:-true}" = "true" ]; then
    UI_PORT="${CODEX_COGNITIVE_APP_PORT_NUMBER:-5173}"
    UI_LOG_FILE="${CODEX_RUNTIME_DIR}/cognitive_app.log"
    if [ -n "${CODESPACE_NAME:-}" ]; then
        UI_BIND_HOST="${CODEX_COGNITIVE_APP_BIND_HOST:-0.0.0.0}"
    else
        UI_BIND_HOST="${CODEX_COGNITIVE_APP_BIND_HOST:-127.0.0.1}"
    fi
    (
        cd "${WORKSPACE}/cognitive_app"
        exec npm run dev -- --host "$UI_BIND_HOST" --port "$UI_PORT"
    ) > "$UI_LOG_FILE" 2>&1 &
    UI_PID=$!
    echo "$UI_PID" > "$UI_PID_FILE"
    UI_READY=0
    for _ in 1 2 3 4 5 6 7 8; do
        sleep 1
        if ! kill -0 "$UI_PID" 2>/dev/null; then
            break
        fi
        if "$PYTHON_BIN" -c 'import urllib.request, sys; urllib.request.urlopen(sys.argv[1], timeout=2).read(1)' \
            "http://127.0.0.1:${UI_PORT}/" 2>/dev/null; then
            UI_READY=1
            break
        fi
    done
    if [ "$UI_READY" != "1" ]; then
        echo "  ❌ Cognitive App failed health verification" >&2
        echo "  Check logs: cat ${UI_LOG_FILE}" >&2
        kill "$UI_PID" 2>/dev/null || true
        rm -f "$UI_PID_FILE"
        exit 1
    fi
    echo "  ✅ Cognitive App ready on port ${UI_PORT}"
fi

# ── 4c. Auto-update Codespace-scoped repo variables ──────────────────────────
# If running in a Codespace, construct the public forwarded URL and update
# the repo variable so GitHub webhooks can deliver to this Codespace.
# Also records the active Codespace name so tooling can reference it.
if [ -n "${CODESPACE_NAME:-}" ] && [ "${CODEX_SYNC_CODESPACE_WEBHOOKS:-false}" = "true" ]; then
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
    echo "  ℹ️  Codespace webhook/port synchronization not enabled; no hosted mutation performed"
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
CODESPACE_REPORT="${CODEX_RUNTIME_DIR}/copilot-agent-environment-report.txt"
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
    echo "URL=${LOCAL_CLI_API_URL}"
  else
    echo "STATUS=degraded"
    echo "REASON=CLI API did not become ready after 5s"
  fi
  echo ""
  echo "## Cognitive App"
  if [ "${CODEX_START_COGNITIVE_APP:-true}" = "true" ] && [ "${UI_READY:-0}" = "1" ]; then
    echo "STATUS=ready"
    echo "URL=http://127.0.0.1:${UI_PORT}"
  else
    echo "STATUS=disabled"
  fi
} > "${CODESPACE_REPORT}"
echo "  ✅ Environment report written → ${CODESPACE_REPORT}"

echo "✅ post-start complete"
