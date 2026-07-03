#!/usr/bin/env bash
# simulate_ci_locally.sh — Run the EXACT same checks as GitHub Actions CI,
# locally, in the same order, using the same isolated venv strategy.
#
# Purpose
# -------
# Eliminates the "works on my machine / fails in CI" problem by reproducing
# the full CI pipeline in a local shell session.  This is especially important
# for catching the SHA-drift class of bugs where CI uses a GitHub merge-preview
# commit that has a different effective state than the local HEAD.
#
# What this script checks (in CI order)
# ──────────────────────────────────────
#  1. SHA drift diagnostic (local HEAD vs GITHUB_SHA env var, if set)
#  2. ruff — full-repo lint (E, F, I)
#  3. isort — import ordering
#  4. mypy — isolated venv, src/ only (mirrors mypy-baseline.yml exactly)
#  5. auto-fix gate — all 17 patterns via auto_fix_common_issues.py
#  6. pre-commit — fast hooks only (trailing-whitespace, end-of-file-fixer)
#
# Usage
# -----
#   bash scripts/ci/simulate_ci_locally.sh            # full check
#   bash scripts/ci/simulate_ci_locally.sh --fix      # auto-fix + recheck
#   bash scripts/ci/simulate_ci_locally.sh --fast     # skip mypy (slow)
#   bash scripts/ci/simulate_ci_locally.sh --json     # JSON report to stdout
#
# Exit codes
# ----------
#   0 — all checks passed
#   1 — one or more checks failed
#   2 — prerequisite tools missing

set -euo pipefail

# ── Config ─────────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MYPY_VENV="${TMPDIR:-/tmp}/mypy-ci-sim-venv"
PASS=0
FAIL=1
RESULTS=()     # "check_name:PASS|FAIL" pairs
AUTOFIX=false
FAST=false
JSON_MODE=false

# ── Parse args ──────────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --fix)  AUTOFIX=true ;;
    --fast) FAST=true ;;
    --json) JSON_MODE=true ;;
    --help|-h)
      head -40 "${BASH_SOURCE[0]}" | grep "^#" | sed 's/^# \?//'
      exit 0
      ;;
  esac
done

# ── ANSI colours ────────────────────────────────────────────────────────────
if [ -t 1 ]; then
  RED='\033[31m'; GREEN='\033[32m'; YELLOW='\033[33m'
  CYAN='\033[36m'; BOLD='\033[1m'; RESET='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; RESET=''
fi

# ── Helpers ─────────────────────────────────────────────────────────────────
step() {
  printf "\n${BOLD}${CYAN}▶ %s${RESET}\n" "$1"
}

ok()   { printf "  ${GREEN}✅ %s${RESET}\n" "$1";  RESULTS+=("$2:PASS"); }
fail() { printf "  ${RED}❌ %s${RESET}\n" "$1"; RESULTS+=("$2:FAIL"); }
info() { printf "  ${YELLOW}ℹ  %s${RESET}\n" "$1"; }

cd "$REPO_ROOT"

# ─────────────────────────────────────────────────────────────────────────────
# 0. SHA-drift diagnostic
# ─────────────────────────────────────────────────────────────────────────────
step "0. SHA drift diagnostic"
LOCAL_SHA="$(git log -1 --format=%H)"
GITHUB_SHA_ENV="${GITHUB_SHA:-}"
if [ -n "$GITHUB_SHA_ENV" ]; then
  if [ "$LOCAL_SHA" = "$GITHUB_SHA_ENV" ]; then
    ok "No SHA drift: git HEAD == GITHUB_SHA ($LOCAL_SHA)" "sha_drift"
  else
    fail "SHA drift: GITHUB_SHA=${GITHUB_SHA_ENV:0:12} ≠ git HEAD=${LOCAL_SHA:0:12}" "sha_drift"
    info "CI is running on a merge-preview commit — mypy counts may differ from local."
    info "This is the root cause of the '277 errors > baseline 0' class of surprises."
  fi
else
  info "Not in GitHub Actions (GITHUB_SHA not set). Checking local HEAD: ${LOCAL_SHA:0:12}"
  ok "Local HEAD: ${LOCAL_SHA:0:12}" "sha_drift"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 1. ruff — full-repo lint
# ─────────────────────────────────────────────────────────────────────────────
step "1. ruff (E/F/I — full repo)"
if python -m ruff check . --statistics 2>&1; then
  ok "ruff: 0 violations" "ruff"
else
  COUNT="$(python -m ruff check . 2>&1 | grep -c '^' || true)"
  fail "ruff: ${COUNT} violations found" "ruff"
  if $AUTOFIX; then
    info "Auto-fixing with: python -m ruff check . --fix"
    python -m ruff check . --fix
    info "Re-checking after fix…"
    if python -m ruff check . 2>&1; then
      ok "ruff: clean after auto-fix" "ruff_after_fix"
    else
      fail "ruff: still failing after auto-fix — manual intervention needed" "ruff_after_fix"
    fi
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 2. isort
# ─────────────────────────────────────────────────────────────────────────────
step "2. isort (import order)"
if python -m isort . --check-only --quiet 2>&1; then
  ok "isort: all imports sorted" "isort"
else
  fail "isort: unsorted imports detected" "isort"
  if $AUTOFIX; then
    info "Auto-fixing with: python -m isort ."
    python -m isort .
    ok "isort: fixed" "isort_after_fix"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 3. mypy — isolated venv (mirrors CI exactly)
# ─────────────────────────────────────────────────────────────────────────────
if $FAST; then
  info "Skipping mypy (--fast mode)"
  RESULTS+=("mypy:SKIP")
else
  step "3. mypy isolated-venv (mirrors mypy-baseline.yml)"
  info "Creating isolated venv at $MYPY_VENV …"
  python -m venv "$MYPY_VENV" --clear 2>/dev/null
  "$MYPY_VENV/bin/pip" install --quiet "mypy>=1.8.0" types-PyYAML types-requests

  BASELINE="$(cat .mypy_baseline 2>/dev/null || echo 0)"
  info "Baseline: $BASELINE errors"
  info "Running mypy on src/ …"

  MYPY_OUT="$("$MYPY_VENV/bin/python" scripts/ci/mypy_baseline.py 2>&1)"
  MYPY_EXIT=$?
  echo "$MYPY_OUT"

  if [ $MYPY_EXIT -eq 0 ]; then
    ok "mypy: passes baseline ($BASELINE)" "mypy"
  else
    fail "mypy: baseline exceeded" "mypy"
    info "Fix type errors, then run: python scripts/ci/mypy_baseline.py --update"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 4. auto-fix gate (all 17 patterns)
# ─────────────────────────────────────────────────────────────────────────────
step "4. auto-fix gate (17 patterns)"
AUTOFIX_CMD="python scripts/ci/auto_fix_common_issues.py"
if $AUTOFIX; then
  AUTOFIX_CMD="python scripts/ci/auto_fix_common_issues.py"
else
  AUTOFIX_CMD="python scripts/ci/auto_fix_common_issues.py --check-only"
fi

if eval "$AUTOFIX_CMD"; then
  ok "auto-fix gate: 17/17 patterns PASS" "autofix"
else
  fail "auto-fix gate: issues detected" "autofix"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 5. pre-commit fast hooks
# ─────────────────────────────────────────────────────────────────────────────
step "5. pre-commit (trailing-whitespace + end-of-file-fixer)"
if pre-commit run trailing-whitespace end-of-file-fixer --all-files 2>&1; then
  ok "pre-commit fast hooks: clean" "pre_commit"
else
  fail "pre-commit fast hooks: violations found" "pre_commit"
  if $AUTOFIX; then
    pre-commit run trailing-whitespace end-of-file-fixer --all-files || true
    ok "pre-commit: fixed" "pre_commit_after_fix"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
printf "\n${BOLD}%s${RESET}\n" "══════════════════════════════════════════════"
printf "${BOLD}  SIMULATE CI SUMMARY${RESET}\n"
printf "${BOLD}%s${RESET}\n" "══════════════════════════════════════════════"

TOTAL_PASS=0
TOTAL_FAIL=0
for entry in "${RESULTS[@]}"; do
  name="${entry%%:*}"
  status="${entry##*:}"
  if [ "$status" = "PASS" ] || [ "$status" = "SKIP" ]; then
    printf "  ${GREEN}✅ %s${RESET}\n" "$name"
    TOTAL_PASS=$((TOTAL_PASS + 1))
  else
    printf "  ${RED}❌ %s${RESET}\n" "$name"
    TOTAL_FAIL=$((TOTAL_FAIL + 1))
  fi
done

printf "\n  Passed: ${GREEN}%d${RESET}  Failed: ${RED}%d${RESET}\n\n" \
  "$TOTAL_PASS" "$TOTAL_FAIL"

if [ $TOTAL_FAIL -gt 0 ]; then
  printf "${RED}${BOLD}CI simulation FAILED — fix above errors before pushing.${RESET}\n\n"
  exit 1
else
  printf "${GREEN}${BOLD}✅ All CI checks passed locally!${RESET}\n\n"
  exit 0
fi
