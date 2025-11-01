#!/bin/bash
# Serve MSP Gateway locally
# Run with: bash scripts/local/serve_local.sh

set -e

echo "==================================="
echo "MSP Gateway - Local Server"
echo "==================================="

# Set environment variables
export MSP_OFFLINE=1
export MSP_HOST=127.0.0.1
export MSP_PORT=8080
export MSP_LOG_LEVEL=INFO

# Create required directories
mkdir -p .codex/logs
mkdir -p .codex/tenants
mkdir -p artifacts/emb

echo "Starting MSP Gateway on http://${MSP_HOST}:${MSP_PORT}"
echo "Offline Mode: ${MSP_OFFLINE}"
echo ""
echo "Press Ctrl+C to stop the server"
echo "==================================="

# Start uvicorn
uvicorn services.msp_gateway.main:app \
    --host "${MSP_HOST}" \
    --port "${MSP_PORT}" \
    --log-level info \
    --no-access-log
