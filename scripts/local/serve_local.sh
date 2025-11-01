#!/usr/bin/env bash
# MSP Local Runner: start FastAPI gateway on 127.0.0.1:8080
# Usage:
#   scripts/local/serve_local.sh
#
# Notes:
# - Reads .env if present (MSP_* variables)
# - Binds to localhost only
# - OFFLINE guard enabled by default unless overridden

set -euo pipefail

# Project root = directory containing this script, ascend to repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

# Load .env if present
if [[ -f ".env" ]]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs)
  echo "Loaded environment from .env"
fi

# Set defaults (can be overridden via .env or export)
: "${MSP_OFFLINE:=1}"
: "${MSP_HOST:=127.0.0.1}"
: "${MSP_PORT:=8080}"
: "${MSP_LOG_LEVEL:=INFO}"
: "${MSP_MODEL_BACKEND:=mock}"

# Export for uvicorn
export MSP_OFFLINE MSP_HOST MSP_PORT MSP_LOG_LEVEL MSP_MODEL_BACKEND

# Create required directories
mkdir -p .codex/logs
mkdir -p .codex/tenants
mkdir -p artifacts/emb

echo "==================================="
echo "MSP Gateway - Local Server"
echo "==================================="
echo "Repository:   ${REPO_ROOT}"
echo "Host:         ${MSP_HOST}"
echo "Port:         ${MSP_PORT}"
echo "Offline Mode: ${MSP_OFFLINE}"
echo "Model:        ${MSP_MODEL_BACKEND}"
echo "Log Level:    ${MSP_LOG_LEVEL}"
echo ""
echo "Starting MSP Gateway on http://${MSP_HOST}:${MSP_PORT}"
echo "Press Ctrl+C to stop the server"
echo "==================================="
echo ""

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn not found. Install with:"
    echo "  pip install uvicorn fastapi"
    exit 1
fi

# Start uvicorn with proper signal handling
exec uvicorn services.msp_gateway.main:app \
    --host "${MSP_HOST}" \
    --port "${MSP_PORT}" \
    --log-level "${MSP_LOG_LEVEL,,}" \
    --no-access-log
