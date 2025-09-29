#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
exec pytest "$@"
