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

echo "── Validating ${TARGET} (repo contract: path-gated workflow, action_required no-op is expected) ──"

# ── Check 1: Python YAML parse ────────────────────────────────────────────────
# Catches: orphaned run: keys, structural YAML errors
if python3 -c "import yaml; yaml.safe_load(open('${TARGET}'))" 2>&1; then
  echo "✅ Check 1/5: YAML parse (python yaml.safe_load)"
else
  echo "::error file=${TARGET}::YAML parse failure — likely orphaned run: key"
  echo "   Repair the workflow structure; do not treat a path-gated no-op as a regression."
  FAIL=$((FAIL + 1))
fi

# ── Check 2: yamllint ─────────────────────────────────────────────────────────
# Catches: flow scalar brace syntax (|| { }) that crashes yamllint 1.38.0
if command -v yamllint >/dev/null 2>&1; then
  if yamllint -c "${YAMLLINT_CFG}" "${TARGET}" 2>&1; then
    echo "✅ Check 2/5: yamllint"
  else
    echo "::error file=${TARGET}::yamllint failed — likely || { } flow scalar in session preload run:"
    echo "   Fix the workflow structure; a path-gated no-op is not a failure by itself."
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
    echo "   Fix the workflow structure; do not confuse path-gated no-ops with a regression."
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
  echo "::error::${GUARD_FAIL} required feature(s) missing — workflow no longer matches the repo contract"
  echo "   Repair the workflow, but do not equate a path-gated no-op with a failure."
  FAIL=$((FAIL + 1))
else
  echo "✅ Check 4/5: all required workflow features present"
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

# The workflow intentionally stores the LFS gate with a YAML scalar value of '1';
# allow both single- and double-quoted values so we do not regress on valid YAML.
if python3 - "$TARGET" <<'PY'
import pathlib, re, sys
path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding='utf-8')
if not re.search(r"GIT_LFS_SKIP_SMUDGE:\s*['\"]?1['\"]?", text):
    raise SystemExit(1)
PY
then
  echo "✅ LFS guard: skip-smudge flag uses a valid scalar form"
else
  echo "::error file=${TARGET}::LFS guard missing or malformed; expected GIT_LFS_SKIP_SMUDGE: '1' / \"1\""
  FAIL=$((FAIL + 1))
fi

# ── Result ────────────────────────────────────────────────────────────────────
echo ""
if [ "${FAIL}" -gt 0 ]; then
  echo "❌ ${FAIL} check(s) failed — workflow does not match the repo contract"
  echo "   Path-gated no-op runs are expected; fix the actual structural issue instead."
  exit 1
fi

echo "✅ ${TARGET} passes all required repo-contract checks"
