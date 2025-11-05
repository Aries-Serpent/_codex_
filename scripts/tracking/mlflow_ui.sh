#!/usr/bin/env bash
# Launch MLflow UI against local file store (offline)
# Usage: ./scripts/tracking/mlflow_ui.sh

set -euo pipefail

# Default tracking URI to local file store
MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-file:./mlruns}"

echo "==> Launching MLflow UI (offline mode)"
echo "Tracking URI: ${MLFLOW_TRACKING_URI}"

# Ensure mlflow is installed
if ! command -v mlflow &> /dev/null; then
    echo "Error: mlflow not found. Install with: pip install mlflow"
    exit 1
fi

# Launch UI
echo "==> Starting MLflow UI server..."
echo "Access at: http://localhost:5000"
echo "Press Ctrl+C to stop"

mlflow ui --backend-store-uri "${MLFLOW_TRACKING_URI}" --port 5000
