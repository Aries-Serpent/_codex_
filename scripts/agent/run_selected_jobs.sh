#!/usr/bin/env bash
# Agent-run harness: execute selected opt-in tasks (reads env flags set from PR checkboxes)
# Usage: set env vars before running, e.g.:
#  ACCELERATE_TEST=1 RUN_LORA_TESTS=1 SKIP_OPTIONAL=1 ./scripts/agent/run_selected_jobs.sh

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

# Probe agent environment
echo "[INFO] Probing agent environment..."
python scripts/agent/probe_env.py || true

# Docs build (safe default: SKIP_OPTIONAL=1)
SKIP_OPTIONAL="${SKIP_OPTIONAL:-1}"
FAIL_ON_MISSING="${FAIL_ON_MISSING:-0}"

if [ "${SKIP_OPTIONAL}" = "1" ] || [ "${SKIP_OPTIONAL}" = "true" ]; then
  echo "[INFO] Running docs build (SKIP_OPTIONAL=${SKIP_OPTIONAL})"
  SKIP_OPTIONAL="${SKIP_OPTIONAL}" FAIL_ON_MISSING="${FAIL_ON_MISSING}" bash scripts/docs_build.sh
else
  echo "[INFO] SKIP_OPTIONAL unset/false: running strict docs build per env"
  SKIP_OPTIONAL="${SKIP_OPTIONAL}" FAIL_ON_MISSING="${FAIL_ON_MISSING}" bash scripts/docs_build.sh
fi

# Run full audit if requested
if [ "${RUN_AUDIT:-1}" = "1" ] || [ "${RUN_AUDIT:-1}" = "true" ]; then
  echo "[INFO] Running full audit runner"
  python scripts/space_traversal/audit_runner.py run
fi

# Run gated tests that require agent resources
if [ "${ACCELERATE_TEST:-0}" = "1" ] || [ "${ACCELERATE_TEST:-0}" = "true" ]; then
  echo "[INFO] Running distributed tests (ACCELERATE_TEST=1)"
  pytest -q tests/integration/test_distributed_init.py || true
fi

if [ "${RUN_LORA_TESTS:-0}" = "1" ] || [ "${RUN_LORA_TESTS:-0}" = "true" ]; then
  echo "[INFO] Running LoRA minimal tests (RUN_LORA_TESTS=1)"
  pytest -q tests/modeling/test_lora_minimal.py || true
fi

echo "[INFO] Agent-run completed. Artifacts: audit_artifacts/ reports/ audit_run_manifest.json"
