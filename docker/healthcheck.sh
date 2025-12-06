#!/bin/bash
# Health check script for Docker container
# Returns 0 if healthy, 1 if unhealthy

python -c "import sys; from codex_ml.serving.health import health_check; result = health_check(); sys.exit(0 if result.get('status') == 'healthy' else 1)"
