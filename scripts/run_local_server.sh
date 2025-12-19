#!/usr/bin/env bash
set -euo pipefail

export RATE_LIMIT_RATE=${RATE_LIMIT_RATE:-1000}
export RATE_LIMIT_BURST=${RATE_LIMIT_BURST:-1000}
export PYTHONPATH="$(pwd)${PYTHONPATH:+:$PYTHONPATH}"

python3 -m src.mcp.server.run --host 0.0.0.0 --port 8080
