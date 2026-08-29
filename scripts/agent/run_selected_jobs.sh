#!/usr/bin/env bash
# Agent-run harness: execute selected opt-in tasks (reads env flags set from PR checkboxes)
# Usage: set env vars before running, e.g.:
#  ACCELERATE_TEST=1 RUN_LORA_TESTS=1 SKIP_OPTIONAL=1 ./scripts/agent/run_selected_jobs.sh

set -euo pipefail

normalize_flag() {
  local raw="$1"
  local default="$2"
  local name="$3"

  if [ -z "${raw}" ]; then
    echo "${default}"
    return
  fi

  case "${raw}" in
    1|0)
      echo "${raw}"
      ;;
    true|TRUE|True|yes|YES|on|ON)
      echo "1"
      echo "[WARN] ${name} value '${raw}' is deprecated; use 1/0." >&2
      ;;
    false|FALSE|False|no|NO|off|OFF)
      echo "0"
      echo "[WARN] ${name} value '${raw}' is deprecated; use 1/0." >&2
      ;;
    *)
      echo "${default}"
      echo "[WARN] ${name} value '${raw}' is unrecognized; defaulting to ${default}." >&2
      ;;
  esac
}
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

# Probe agent environment
echo "[INFO] Probing agent environment..."
python scripts/agent/probe_env.py || true

# Docs build (safe default: SKIP_OPTIONAL=1)
SKIP_OPTIONAL=$(normalize_flag "${SKIP_OPTIONAL-}" "1" "SKIP_OPTIONAL")
FAIL_ON_MISSING=$(normalize_flag "${FAIL_ON_MISSING-}" "0" "FAIL_ON_MISSING")

echo "[INFO] Running docs build (SKIP_OPTIONAL=${SKIP_OPTIONAL}, FAIL_ON_MISSING=${FAIL_ON_MISSING})"
SKIP_OPTIONAL="${SKIP_OPTIONAL}" FAIL_ON_MISSING="${FAIL_ON_MISSING}" bash scripts/docs_build.sh

# Run full audit if requested
RUN_AUDIT=$(normalize_flag "${RUN_AUDIT-1}" "1" "RUN_AUDIT")
if [ "${RUN_AUDIT}" = "1" ]; then
  echo "[INFO] Running full audit runner"
  python scripts/space_traversal/audit_runner.py run
fi

# Run gated tests that require agent resources
ACCELERATE_TEST=$(normalize_flag "${ACCELERATE_TEST-0}" "0" "ACCELERATE_TEST")
if [ "${ACCELERATE_TEST}" = "1" ]; then
  echo "[INFO] Running distributed tests (ACCELERATE_TEST=1)"
  pytest -q tests/integration/test_distributed_init.py || true
fi

RUN_LORA_TESTS=$(normalize_flag "${RUN_LORA_TESTS-0}" "0" "RUN_LORA_TESTS")
if [ "${RUN_LORA_TESTS}" = "1" ]; then
  echo "[INFO] Running LoRA minimal tests (RUN_LORA_TESTS=1)"
  pytest -q tests/modeling/test_lora_minimal.py || true
fi

echo "[INFO] Agent-run completed. Artifacts: audit_artifacts/ .codex/reports/ audit_run_manifest.json"
