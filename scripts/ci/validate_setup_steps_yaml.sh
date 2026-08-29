#!/usr/bin/env bash
# validate_setup_steps_yaml.sh
# CI guard for .github/workflows/copilot-setup-steps.yml.
# Repo contract: this workflow is intentionally path-gated. A workflow run that ends
# in GitHub's "action_required" state with 0 jobs is expected when no matching files
# changed. The validator should enforce required invariants rather than a stale
# historical snapshot or exact line count.
#
# Exits non-zero if any check fails.
# Called from validate.yml on every push touching this file.

set -euo pipefail

TARGET=".github/workflows/copilot-setup-steps.yml"
YAMLLINT_CFG=".yamllint.yml"
FAIL=0

echo "── Validating ${TARGET} (canonical: commit 12f7a861 / blob 8c84a8c1) ──"

# ── Check 1: Python YAML parse ────────────────────────────────────────────────
# Catches: orphaned run: keys, structural YAML errors
if python3 -c "import yaml; yaml.safe_load(open('${TARGET}'))" 2>&1; then
  echo "✅ Check 1/5: YAML parse (python yaml.safe_load)"
else
  echo "::error file=${TARGET}::YAML parse failure — likely orphaned run: key"
  echo "   Restore: git show 12f7a861:${TARGET} > ${TARGET} && python3 scripts/ci/patch_session_preload.py"
  FAIL=$((FAIL + 1))
fi

# ── Check 2: yamllint ─────────────────────────────────────────────────────────
# Catches: flow scalar brace syntax (|| { }) that crashes yamllint 1.38.0
if command -v yamllint >/dev/null 2>&1; then
  if yamllint -c "${YAMLLINT_CFG}" "${TARGET}" 2>&1; then
    echo "✅ Check 2/5: yamllint"
  else
    echo "::error file=${TARGET}::yamllint failed — likely || { } flow scalar in session preload run:"
    echo "   Fix: python3 scripts/ci/patch_session_preload.py"
    FAIL=$((FAIL + 1))
  fi
else
  echo "⚠️  yamllint not installed — skipping check 2/5"
fi

# ── Check 3: Session preload is block scalar ──────────────────────────────────
if grep -A4 "Session Context Pre-load" "${TARGET}" | grep -q "run: |"; then
  echo "✅ Check 3/5: session preload uses block scalar"
else
  echo "::error file=${TARGET}::Session preload is NOT using block scalar run: | form"
  echo "   Fix: python3 scripts/ci/patch_session_preload.py"
  FAIL=$((FAIL + 1))
fi

# ── Check 4: Canonical feature regression guard ───────────────────────────────
GUARD_FAIL=0

check_feature() {
  local pattern="$1"
  local label="$2"
  if grep -Eq "${pattern}" "${TARGET}"; then
    echo "  ✅ ${label}"
  else
    echo "  ::error file=${TARGET}::REGRESSION: ${label} missing"
    GUARD_FAIL=$((GUARD_FAIL + 1))
  fi
}

echo "── Canonical feature checks ──"
check_feature "cancel-in-progress: true"          "cancel-in-progress: true"
check_feature "vars.COPILOT_RUNNER_PROFILE"        "Dynamic runner (vars.COPILOT_RUNNER_PROFILE)"
check_feature 'NODE_VERSION: "22"'                 "NODE_VERSION: 22"
check_feature "rescue-comment:"                    "rescue-comment job"
check_feature "actions/checkout@(v5|9c091bb2)"     "Approved checkout reference"
check_feature "session_access_probe.py"            "Session Access Probe step"
check_feature "autonomous_rag_context.py"          "RAG Context Build step"
check_feature "DO NOT REFACTOR THIS STEP"          "Guard comment on preload step"

if [ "${GUARD_FAIL}" -gt 0 ]; then
  echo "::error::${GUARD_FAIL} canonical feature(s) missing — file has regressed from baseline"
  echo "   Restore: git show 12f7a861a067ed5d9f1e1939119325f896624588:${TARGET} > ${TARGET}"
  echo "   Then:    python3 scripts/ci/patch_session_preload.py"
  FAIL=$((FAIL + 1))
else
  echo "✅ Check 4/5: all canonical features present"
fi

# ── Check 5: File integrity / no-op contract ─────────────────────────────────
LINE_COUNT=$(wc -l < "${TARGET}")
# Intentionally lightweight: the workflow is path-gated and may legitimately be a
# no-op (GitHub status "action_required" with 0 jobs) when no files match the
# trigger filter. We only guard against obvious truncation, not a stale historical
# snapshot.
MIN_ALLOWED_LINES=180
if [ "${LINE_COUNT}" -lt "${MIN_ALLOWED_LINES}" ]; then
  echo "::error file=${TARGET}::Only ${LINE_COUNT} lines — expected >=${MIN_ALLOWED_LINES}. File may be truncated."
  FAIL=$((FAIL + 1))
else
  echo "✅ Check 5/5: line count ${LINE_COUNT} (expected ≥${MIN_ALLOWED_LINES}); path-gated no-op runs are expected by repo contract"
fi

# ── Result ────────────────────────────────────────────────────────────────────
echo ""
if [ "${FAIL}" -gt 0 ]; then
  echo "❌ ${FAIL} check(s) failed — canonical baseline: commit 12f7a861 / blob 8c84a8c1"
  echo "   See: docs/agent/COPILOT_SETUP_STEPS_GUARD.md"
  exit 1
fi

echo "✅ ${TARGET} passes all canonical baseline checks"
