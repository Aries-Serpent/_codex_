#!/usr/bin/env bash
# Thin convenience wrapper for the unified Codex environment CLI.
# Usage examples:
#   ./run_codex_env.sh health
#   ./run_codex_env.sh task-sequence
#   ./run_codex_env.sh mltests -c infrastructure -c data
#   ./run_codex_env.sh bundle

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python -m codex_ml.cli.codex_env --repo-root "${REPO_ROOT}" "$@"
