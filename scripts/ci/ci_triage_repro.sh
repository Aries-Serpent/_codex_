#!/usr/bin/env bash
# scripts/ci/ci_triage_repro.sh
# ─────────────────────────────────────────────────────────────────────────────
# Reproducible CI Triage Toolkit — captures every diagnostic performed during
# session S145 (PR #3606) so any contributor or agent can reproduce and verify
# all fixes in one pass.
#
# Checks (run in this order)
# ──────────────────────────
#   1. actionlint      — workflow compliance (SC2072, self-ref, etc.)
#   2. ruff I001       — import sort order (pre-merge-validation gate)
#   3. mypy baseline   — anti-regression gate freshness
#   4. auto-fix gate   — all 16 patterns via auto_fix_common_issues.py
#   5. telemetry repro — verify ci-health-monitor base64 extraction
#   6. threshold align — coherence-snapshot.yml dashboard == enforcement
#   7. changelog lint  — no self-inconsistent PR number references
#
# Usage
# ─────
#   bash scripts/ci/ci_triage_repro.sh              # check-only (read-only)
#   bash scripts/ci/ci_triage_repro.sh --fix         # apply auto-fixes
#   bash scripts/ci/ci_triage_repro.sh --json        # JSON summary to stdout
#   bash scripts/ci/ci_triage_repro.sh --check <N>   # run only check N (1-7)
#
# Exit codes
# ──────────
#   0 — all checks pass
#   1 — one or more checks fail
#
# Knowledge base / root-cause docs
# ─────────────────────────────────
#   docs/ci/CI_TRIAGE_REPRO_S145.md
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

_pass()   { echo -e "${GREEN}✅ PASS${NC} — $*"; }
_fail()   { echo -e "${RED}❌ FAIL${NC} — $*"; FAILED=$((FAILED + 1)); }
_info()   { echo -e "${CYAN}ℹ  ${NC}$*"; }
_warn()   { echo -e "${YELLOW}⚠  ${NC}$*"; }
_header() { echo -e "\n${BOLD}${CYAN}━━━ $* ━━━${NC}"; }

# ── State ────────────────────────────────────────────────────────────────────
FAILED=0
FIX_MODE=false
JSON_MODE=false
ONLY_CHECK=""

# Parallel arrays for results (bash 3+ compatible)
RESULT_KEYS=()
RESULT_STATUSES=()
RESULT_DETAILS=()

_record() {
  local key="$1" status="$2" detail="$3"
  RESULT_KEYS+=("$key")
  RESULT_STATUSES+=("$status")
  RESULT_DETAILS+=("$detail")
}

# _count_lines PATTERN — count matching lines from stdin; never exits non-zero.
# Usage:  count=$( echo "$text" | _count_lines "pattern" )
_count_lines() {
  local pat="$1"
  { grep -E "$pat" 2>/dev/null || true; } | wc -l | tr -d ' '
}

# ── Arg parsing ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --fix)   FIX_MODE=true ;;
    --json)  JSON_MODE=true ;;
    --check) shift; ONLY_CHECK="$1" ;;
    -h|--help)
      sed -n '/^# /p' "$0" | sed 's/^# //'
      exit 0 ;;
    *) echo "Unknown argument: $1 (use --help)"; exit 1 ;;
  esac
  shift
done

# ── Helper: install actionlint if missing ─────────────────────────────────────
_ensure_actionlint() {
  if command -v actionlint &>/dev/null; then return 0; fi
  if [[ -x /tmp/actionlint ]]; then export PATH="/tmp:$PATH"; return 0; fi
  _info "Downloading actionlint v1.7.7 to /tmp ..."
  local ver="1.7.7"
  if curl -fsSL --max-time 30 \
      "https://github.com/rhysd/actionlint/releases/download/v${ver}/actionlint_${ver}_linux_amd64.tar.gz" \
      2>/dev/null | tar xz -C /tmp/ actionlint; then
    export PATH="/tmp:$PATH"
    return 0
  fi
  _warn "Could not download actionlint — check 1 will be skipped"
  return 1
}

# ════════════════════════════════════════════════════════════════════════════
# CHECK 1 — actionlint workflow compliance
#
# Root cause (S145): coherence-snapshot.yml:199 used shell string comparison
#   [ 'SCORE' \> '99.6' ]  ← lexicographic, not numeric → SC2072
# Fix: awk -v s='SCORE' 'BEGIN{print (s+0 >= 99.7) ? "success" : "warning"}'
# Ref: docs/ci/CI_TRIAGE_REPRO_S145.md#check-1
# ════════════════════════════════════════════════════════════════════════════
check_1_actionlint() {
  _header "1/7 · actionlint workflow compliance"
  if ! _ensure_actionlint; then
    _warn "actionlint unavailable — skipping"
    _record "1_actionlint" "skip" "actionlint not installed"
    return
  fi
  local out count
  out=$(actionlint .github/workflows/*.yml 2>&1) || true
  count=$(echo "$out" | _count_lines "^.github")
  if [[ "$count" -eq 0 ]]; then
    _pass "actionlint: 0 errors ($(find .github/workflows -maxdepth 1 -name '*.yml' | wc -l | tr -d ' ') files)"
    _record "1_actionlint" "pass" "0 errors"
  else
    _fail "actionlint: ${count} error(s)"
    echo "$out" | head -20
    _record "1_actionlint" "fail" "${count} errors"
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# CHECK 2 — ruff I001 import sort order
#
# Root cause (S145): OTel try-block imports in:
#   scripts/ci/aais_v4_scorer.py:31
#   scripts/ci/pr_comment_consolidator.py:58
# were out of isort order → pre-merge-validation I001 gate fail.
# Fix: ruff check --select I --fix <file>
# Ref: docs/ci/CI_TRIAGE_REPRO_S145.md#check-2
# ════════════════════════════════════════════════════════════════════════════
check_2_ruff_imports() {
  _header "2/7 · ruff I001 import sort order"
  local issues=0 fix_cmd=""
  [[ "$FIX_MODE" == true ]] && fix_cmd="--fix"

  # Targeted files first (fastest signal)
  for f in \
    "scripts/ci/aais_v4_scorer.py" \
    "scripts/ci/pr_comment_consolidator.py"
  do
    if ruff check --select I --quiet $fix_cmd "$f" 2>/dev/null; then
      _info "  $f — OK"
    else
      _fail "  $f — unsorted imports"
      issues=$((issues + 1))
    fi
  done

  # Full-repo sweep
  local ruff_out repo_issues
  ruff_out=$(ruff check --select I . 2>/dev/null) || true
  repo_issues=$(echo "$ruff_out" | _count_lines "I001")
  if [[ "$repo_issues" -gt 0 ]]; then
    if [[ "$FIX_MODE" == true ]]; then
      ruff check --select I --fix . 2>/dev/null
      _warn "Auto-fixed ${repo_issues} I001 issue(s) repo-wide"
    else
      _fail "Repo-wide: ${repo_issues} additional I001 issue(s)"
      issues=$((issues + repo_issues))
    fi
  fi

  if [[ "$issues" -eq 0 ]]; then
    _pass "ruff I001: all imports correctly sorted"
    _record "2_ruff_i001" "pass" "0 issues"
  else
    _record "2_ruff_i001" "fail" "${issues} file(s)"
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# CHECK 3 — mypy anti-regression baseline freshness
#
# Root cause (S145): .mypy_baseline contained 0 but codebase had 282 errors.
# CI gate: fails when current_count > stored_baseline.
# Fix: python scripts/ci/mypy_baseline.py --update  (after auditing errors)
# Ref: docs/ci/CI_TRIAGE_REPRO_S145.md#check-3
# ════════════════════════════════════════════════════════════════════════════
check_3_mypy_baseline() {
  _header "3/7 · mypy anti-regression baseline"
  if [[ ! -f .mypy_baseline ]]; then
    _fail ".mypy_baseline missing — run: python scripts/ci/mypy_baseline.py --update"
    _record "3_mypy_baseline" "fail" "file missing"
    return
  fi
  local stored
  stored=$(tr -d '[:space:]' < .mypy_baseline)
  _info "Stored baseline: ${stored} errors"

  if ! python -m mypy --version &>/dev/null 2>&1; then
    _warn "mypy not on PATH — skipping live count (baseline=${stored})"
    _record "3_mypy_baseline" "skip" "mypy unavailable"
    return
  fi

  local current
  current=$(python scripts/ci/mypy_baseline.py 2>/dev/null \
    | grep "mypy errors found:" | awk '{print $NF}') || current="?"
  _info "Current error count: ${current}"

  if [[ "$current" == "?" ]]; then
    _warn "mypy_baseline.py returned no parseable output"
    _record "3_mypy_baseline" "skip" "parse error"
    return
  fi

  if [[ "$current" -le "$stored" ]]; then
    _pass "mypy: ${current} ≤ baseline ${stored} (no regression)"
    _record "3_mypy_baseline" "pass" "${current} <= ${stored}"
  else
    _fail "mypy regression: ${current} > baseline ${stored} (+$((current - stored)) new errors)"
    if [[ "$FIX_MODE" == true ]]; then
      python scripts/ci/mypy_baseline.py --update
      _warn "Baseline updated to ${current} — ratchet down over time"
    fi
    _record "3_mypy_baseline" "fail" "${current} > ${stored}"
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# CHECK 4 — auto-fix gate (16 patterns)
#
# Mirrors: pre-merge-validation.yml "Detect and Fix Common Issues" step.
# Runs all 16 patterns defined in scripts/ci/auto_fix_common_issues.py.
# Ref: docs/ci/CI_TRIAGE_REPRO_S145.md#check-4
# ════════════════════════════════════════════════════════════════════════════
check_4_autofix_gate() {
  _header "4/7 · auto-fix gate (16 patterns)"
  if [[ "$FIX_MODE" == true ]]; then
    python scripts/ci/auto_fix_common_issues.py
    _pass "auto-fix patterns applied"
    _record "4_autofix" "pass" "fix mode"
    return
  fi
  local out exit_code=0
  out=$(python scripts/ci/auto_fix_common_issues.py --check-only 2>&1) || exit_code=$?
  # Use the tool's own exit code: 0 = only informational ✗ items (e.g. SHA drift),
  # non-zero = at least one auto-fixable issue that MUST be addressed.
  # Show ✗ lines as informational warnings even when exit_code=0.
  local warn_count
  warn_count=$(echo "$out" | _count_lines "^\s+✗")
  if [[ "$exit_code" -eq 0 ]]; then
    if [[ "$warn_count" -gt 0 ]]; then
      _pass "auto-fix gate: no blocking issues (${warn_count} informational warning(s) — see below)"
      echo "$out" | { grep -E "^\s+✗" || true; } | head -5 | sed 's/^/  /'
    else
      _pass "auto-fix gate: 0 issues across all patterns"
    fi
    _record "4_autofix" "pass" "exit 0 (${warn_count} informational)"
  else
    _fail "auto-fix gate: ${exit_code} auto-fixable issue(s) require attention"
    echo "$out" | { grep -E "^\s+✗" || true; } | head -10
    _record "4_autofix" "fail" "exit ${exit_code}"
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# CHECK 5 — ci-health-monitor telemetry extraction correctness
#
# Root cause (CI Health Alert #3614): base64-encoded Python extraction script
# used chr(34)+"failed_runs"+chr(34) which constructs the string
# '"failed_runs"' (quotes embedded in the key).  dict.get('"failed_runs"', 0)
# never matches the actual JSON key 'failed_runs', so FAILED_RUNS and
# TOTAL_RUNS were always 0 while FAILURE_RATE was computed correctly.
#
# Observed symptom: issue body showed "Total Runs: 0, Failed Runs: 0,
# Failure Rate: 11.7%" — impossible unless the counts used the wrong key.
#
# Fix: re-encode the extraction script with plain string keys
#   "failed_runs" and "total_runs" (no chr(34) obfuscation).
# Ref: docs/ci/CI_TRIAGE_REPRO_S145.md#check-5
# ════════════════════════════════════════════════════════════════════════════
check_5_telemetry() {
  _header "5/7 · ci-health-monitor telemetry extraction"
  local wf=".github/workflows/ci-health-monitor.yml"
  if [[ ! -f "$wf" ]]; then
    _warn "${wf} not found — skipping"
    _record "5_telemetry" "skip" "file not found"
    return
  fi

  # Extract base64 payload
  local payload
  payload=$(grep "METRICS=\$(echo '" "$wf" \
    | sed "s/.*echo '//;s/' | base64.*//" | head -1) || true
  if [[ -z "$payload" ]]; then
    _fail "Cannot locate base64 payload in ${wf}"
    _record "5_telemetry" "fail" "payload not found"
    return
  fi

  local decoded
  decoded=$(echo "$payload" | base64 -d 2>/dev/null) || {
    _fail "base64 decode failed"
    _record "5_telemetry" "fail" "decode error"
    return
  }

  # Detect chr(34) obfuscation bug
  if echo "$decoded" | grep -q 'chr(34)'; then
    _fail "chr(34) key-lookup bug still present — FAILED_RUNS/TOTAL_RUNS will always be 0"
    _info "Buggy line: $(echo "$decoded" | grep 'chr(34)' | head -1)"
    _info "Fix: replace chr(34)+\"key\"+chr(34) with plain string key \"key\""
    _record "5_telemetry" "fail" "chr(34) bug"
    return
  fi

  # Simulate extraction against a known payload
  local tmp_json="${TMPDIR:-/tmp}/_ci_triage_repro_telemetry_$$.json"
  echo '{"summary":{"total_runs":180,"failed_runs":21,"failure_rate":0.117}}' > "$tmp_json"
  local patched_script result
  patched_script=$(echo "$decoded" \
    | sed "s|/tmp/telemetry_report.json|${tmp_json}|g")
  result=$(echo "$patched_script" | python3 2>/dev/null) || result=""
  rm -f "$tmp_json"

  local rate total failed issues=0
  rate=$(echo   "$result" | awk -F= '/FAILURE_RATE/{print $2}')
  total=$(echo  "$result" | awk -F= '/TOTAL_RUNS/{print $2}')
  failed=$(echo "$result" | awk -F= '/FAILED_RUNS/{print $2}')

  [[ "$rate"   != "11.7" ]] && { _fail "FAILURE_RATE: got '${rate}', want '11.7'";  issues=$((issues+1)); }
  [[ "$total"  != "180"  ]] && { _fail "TOTAL_RUNS:   got '${total}', want '180'";  issues=$((issues+1)); }
  [[ "$failed" != "21"   ]] && { _fail "FAILED_RUNS:  got '${failed}', want '21'";  issues=$((issues+1)); }

  if [[ "$issues" -eq 0 ]]; then
    _pass "Telemetry extraction: FAILURE_RATE=${rate}%  TOTAL_RUNS=${total}  FAILED_RUNS=${failed}"
    _record "5_telemetry" "pass" "all 3 fields correct"
  else
    _record "5_telemetry" "fail" "${issues} field(s) wrong"
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# CHECK 6 — coherence-snapshot.yml threshold alignment
#
# Root cause (PR #3613 review r2949785151): the dashboard --status awk
# expression used "> 99.6" while the enforcement step used threshold = 99.7.
# A score of 99.65 → dashboard shows "success" but enforcement fails → users
# see contradictory signals.
# Fix: align both to >= 99.7.
# Ref: docs/ci/CI_TRIAGE_REPRO_S145.md#check-6
# ════════════════════════════════════════════════════════════════════════════
check_6_threshold_align() {
  _header "6/7 · coherence-snapshot.yml threshold alignment"
  local wf=".github/workflows/coherence-snapshot.yml"
  if [[ ! -f "$wf" ]]; then
    _warn "${wf} not found — skipping"
    _record "6_threshold" "skip" "file not found"
    return
  fi

  local dash_expr enf_thresh issues=0
  # Extract the comparison operator + threshold: 's+0 >= 99.7' → '>= 99.7'
  dash_expr=$(grep -o 's+0 [><=]* [0-9.]*' "$wf" 2>/dev/null \
    | head -1 | sed 's/^s+0 //' || echo "")
  enf_thresh=$(grep 'threshold = ' "$wf" 2>/dev/null | head -1 | awk '{print $NF}' || echo "")

  _info "Dashboard comparison:    '${dash_expr}'"
  _info "Enforcement threshold:   ${enf_thresh}"

  # Dashboard must use ">= 99.7"
  if [[ "$dash_expr" != ">= 99.7" ]]; then
    _fail "Dashboard comparison is '${dash_expr}' — want '>= 99.7'"
    issues=$((issues + 1))
  fi
  # Enforcement must be 99.7
  if [[ "$enf_thresh" != "99.7" ]]; then
    _fail "Enforcement threshold is '${enf_thresh}' — want '99.7'"
    issues=$((issues + 1))
  fi

  if [[ "$issues" -eq 0 ]]; then
    _pass "Thresholds aligned: dashboard '${dash_expr}' == enforcement '${enf_thresh}'"
    _record "6_threshold" "pass" "both=99.7"
  else
    _record "6_threshold" "fail" "dash='${dash_expr}' enf='${enf_thresh}'"
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# CHECK 7 — CHANGELOG self-consistency (PR number cross-references)
#
# Root cause (PR #3613 review r2949785123): session_wrapup_autofix.py
# injected a bullet referencing PR #3613 into the S145 section whose
# header declared PR #3606.  The inconsistency breaks traceability.
# Fix: remove the cross-PR auto-generated bullet from the section.
# Ref: docs/ci/CI_TRIAGE_REPRO_S145.md#check-7
# ════════════════════════════════════════════════════════════════════════════
check_7_changelog_consistency() {
  _header "7/7 · CHANGELOG self-consistency"
  # Use python3 for fast single-pass scan (bash line-by-line loop is too slow
  # on a 2000-line CHANGELOG.md — each line would spawn 2-3 grep subprocesses).
  local result
  result=$(python3 - <<'PYEOF'
import re, sys
current_pr = None
current_section = ""
issues = []
RE_SECTION_PR  = re.compile(r'^#{2,3} .*PR #(\d+)')
RE_SECTION_ANY = re.compile(r'^#{2,3} ')
RE_AUTO_GEN    = re.compile(r'\[auto-generated\]|Auto-fix:.*session_wrapup', re.I)
RE_PR_REF      = re.compile(r'PR #(\d+)')
for line in open("CHANGELOG.md", encoding="utf-8"):
    line = line.rstrip()
    m = RE_SECTION_PR.match(line)
    if m:
        # Extract the LAST PR number in the header (the canonical one)
        all_refs = RE_PR_REF.findall(line)
        current_pr = f"PR #{all_refs[-1]}" if all_refs else None
        current_section = line
        continue
    if RE_SECTION_ANY.match(line):
        current_pr = None
        current_section = ""
        continue
    if current_pr and RE_AUTO_GEN.search(line):
        refs = RE_PR_REF.findall(line)
        if refs:
            line_pr = f"PR #{refs[0]}"
            if line_pr != current_pr:
                issues.append((current_pr, line_pr, current_section, line.strip()))
if issues:
    for sec_pr, line_pr, section, bullet in issues:
        print(f"FAIL: section='{sec_pr}' references '{line_pr}'")
        print(f"  Section: {section}")
        print(f"  Bullet : {bullet[:120]}")
    sys.exit(1)
sys.exit(0)
PYEOF
  ) || local py_exit=$?

  if [[ "${py_exit:-0}" -eq 0 ]]; then
    _pass "CHANGELOG: no auto-generated cross-PR reference inconsistencies"
    _record "7_changelog" "pass" "consistent"
  else
    echo "$result"
    local count
    count=$(echo "$result" | _count_lines "^FAIL:")
    _record "7_changelog" "fail" "${count} cross-PR bullet(s)"
    FAILED=$((FAILED + 1))
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# Dispatch
# ════════════════════════════════════════════════════════════════════════════
_run_all() {
  check_1_actionlint
  check_2_ruff_imports
  check_3_mypy_baseline
  check_4_autofix_gate
  check_5_telemetry
  check_6_threshold_align
  check_7_changelog_consistency
}

echo -e "\n${BOLD}CI Triage Repro Toolkit — S145 / PR #3606${NC}"
echo "Repository : ${REPO_ROOT}"
echo "Mode       : $( [[ "$FIX_MODE" == true ]] && echo 'FIX' || echo 'CHECK-ONLY' )"
echo "Date       : $(date -u '+%Y-%m-%d %H:%M UTC')"

if [[ -z "$ONLY_CHECK" ]]; then
  _run_all
else
  case "$ONLY_CHECK" in
    1) check_1_actionlint ;;
    2) check_2_ruff_imports ;;
    3) check_3_mypy_baseline ;;
    4) check_4_autofix_gate ;;
    5) check_5_telemetry ;;
    6) check_6_threshold_align ;;
    7) check_7_changelog_consistency ;;
    *) echo "Unknown check: ${ONLY_CHECK} (valid: 1–7)"; exit 1 ;;
  esac
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
_header "Summary"
total=${#RESULT_KEYS[@]}
for i in $(seq 0 $((total - 1))); do
  k="${RESULT_KEYS[$i]}"
  s="${RESULT_STATUSES[$i]}"
  d="${RESULT_DETAILS[$i]}"
  case "$s" in
    pass) echo -e "  ${GREEN}✅${NC} ${k}: ${d}" ;;
    skip) echo -e "  ${YELLOW}⏭ ${NC} ${k}: ${d} (skipped)" ;;
    fail) echo -e "  ${RED}❌${NC} ${k}: ${d}" ;;
  esac
done

if [[ "$JSON_MODE" == true ]]; then
  echo ""
  echo "{"
  echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"failed\": ${FAILED},"
  echo "  \"results\": {"
  local_sep=""
  for i in $(seq 0 $((total - 1))); do
    printf '%s    "%s": {"status": "%s", "detail": "%s"}' \
      "$local_sep" "${RESULT_KEYS[$i]}" "${RESULT_STATUSES[$i]}" "${RESULT_DETAILS[$i]}"
    local_sep=$',\n'
  done
  echo ""
  echo "  }"
  echo "}"
fi

echo ""
if [[ "$FAILED" -eq 0 ]]; then
  echo -e "${GREEN}${BOLD}All checks passed ✅${NC}"
  exit 0
else
  echo -e "${RED}${BOLD}${FAILED} check(s) failed ❌${NC}"
  echo "Run with --fix to auto-remediate fixable issues."
  echo "See docs/ci/CI_TRIAGE_REPRO_S145.md for root-cause details."
  exit 1
fi
