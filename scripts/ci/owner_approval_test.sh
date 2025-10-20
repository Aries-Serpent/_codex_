#!/usr/bin/env bash
# Local test harness for the owner approval guard.
# Usage:
#   scripts/ci/owner_approval_test.sh [tool_key]
# Examples:
#   scripts/ci/owner_approval_test.sh docker-build-push
#   OWNER_APPROVED_DURATION=24h scripts/ci/owner_approval_test.sh docker-build-push
set -euo pipefail

TOOL_KEY="${1:-docker-build-push}"

echo "[test] TOOL_KEY=${TOOL_KEY}"
echo "[test] Env overrides: OWNER_APPROVED_UNTIL='${OWNER_APPROVED_UNTIL:-}' OWNER_APPROVED_DURATION='${OWNER_APPROVED_DURATION:-}'"
if [ -f ".github/OWNER_APPROVAL.yml" ]; then
  echo "[test] File-based config present (.github/OWNER_APPROVAL.yml)"
else
  echo "[test] File-based config missing (.github/OWNER_APPROVAL.yml not found)"
fi

TOOL_KEY="${TOOL_KEY}" bash scripts/ci/owner_approval_guard.sh
rc=$? || true

if [ $rc -eq 0 ]; then
  echo "[test] RESULT: APPROVED"
else
  echo "[test] RESULT: DENIED (rc=$rc)"
fi
exit $rc
