#!/bin/bash
# Health check script for Docker container
# Returns 0 if healthy, 1 if unhealthy

python -c "
import sys
try:
    from codex_ml.serving.health import health_check
    result = health_check()
    # The health_check() always returns a dict with 'status' key
    sys.exit(0 if result['status'] == 'healthy' else 1)
except ImportError as e:
    print(f'Health check module not available: {e}', file=sys.stderr)
    sys.exit(1)
except KeyError:
    print('Health check returned unexpected format', file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f'Health check failed: {e}', file=sys.stderr)
    sys.exit(1)
"
