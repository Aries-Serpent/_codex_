#!/usr/bin/env bash
# scripts/ci_local.sh
#
# Run CI checks locally using the same flags and commands as GitHub Actions.
# Each subcommand mirrors a specific CI workflow so failures surface before push.
#
# Usage:
#   bash scripts/ci_local.sh <subcommand> [options]
#
# Subcommands:
#   fast        Mirrors Art_Validation / validate.yml (fast mode)
#   quick       Mirrors Resilient Suite quick group (resilient_validation.yml)
#   slow        Mirrors Resilient Suite slow group
#   integration Mirrors Resilient Suite integration group
#   docs        Mirrors Resilient Suite documentation group
#   premerge    Mirrors Pre-Merge Validation (pre-merge-validation.yml)
#   lint        ruff + pre-commit on changed files only
#   all         Runs: fast + quick + premerge sequentially
#   help        Show this message
#
# Examples:
#   bash scripts/ci_local.sh fast
#   bash scripts/ci_local.sh all
#   bash scripts/ci_local.sh lint

set -euo pipefail

# ---------------------------------------------------------------------------
# Resolve repo root regardless of invocation directory.
# ---------------------------------------------------------------------------
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[PASS]${RESET}  $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[FAIL]${RESET}  $*" >&2; }

ci_header() {
  local title="$1"
  local workflow="$2"
  echo ""
  echo -e "${BOLD}${MAGENTA}╔══════════════════════════════════════════════════════╗${RESET}"
  echo -e "${BOLD}${MAGENTA}║  CI LOCAL: ${title}${RESET}"
  echo -e "${BOLD}${MAGENTA}║  Mirrors : ${workflow}${RESET}"
  echo -e "${BOLD}${MAGENTA}╚══════════════════════════════════════════════════════╝${RESET}"
  echo ""
}

# ---------------------------------------------------------------------------
# Activate .venv_ci if it exists; otherwise fall back to the active venv.
# Developers who want to use their own venv can simply activate it before
# running this script — the check below will leave it untouched.
# ---------------------------------------------------------------------------
activate_venv() {
  VENV_CI="$ROOT/.venv_ci"
  if [[ -d "$VENV_CI" && -z "${VIRTUAL_ENV:-}" ]]; then
    # shellcheck source=/dev/null
    source "$VENV_CI/bin/activate"
    info "Activated .venv_ci"
  elif [[ -n "${VIRTUAL_ENV:-}" ]]; then
    info "Using active venv: $VIRTUAL_ENV"
  else
    warn "No venv active and .venv_ci not found. Run: bash scripts/dev_env_setup.sh"
    warn "Continuing with system Python — results may differ from CI."
  fi
}

# ---------------------------------------------------------------------------
# Track overall pass/fail state across multiple subcommands (used by 'all').
# ---------------------------------------------------------------------------
OVERALL_PASS=true
declare -a RESULTS=()

record_result() {
  local label="$1"
  local code="$2"
  if [[ "$code" -eq 0 ]]; then
    RESULTS+=("${GREEN}PASS${RESET}  $label")
  else
    RESULTS+=("${RED}FAIL${RESET}  $label")
    OVERALL_PASS=false
  fi
}

print_summary() {
  echo ""
  echo -e "${BOLD}${CYAN}════════════════ SUMMARY ════════════════${RESET}"
  for r in "${RESULTS[@]}"; do
    echo -e "  $r"
  done
  echo -e "${BOLD}${CYAN}═════════════════════════════════════════${RESET}"
  if [[ "$OVERALL_PASS" == "true" ]]; then
    echo -e "${GREEN}${BOLD}All checks passed ✓${RESET}"
  else
    echo -e "${RED}${BOLD}One or more checks failed ✗${RESET}"
    return 1
  fi
}

# ---------------------------------------------------------------------------
# run_cmd: execute a command, capture its exit code, and emit pass/fail output.
# Unlike 'set -e', this lets us continue to the summary even after a failure.
# ---------------------------------------------------------------------------
run_cmd() {
  local label="$1"; shift
  echo -e "${CYAN}▶ $label${RESET}"
  echo -e "  ${YELLOW}$ $*${RESET}"
  set +e
  "$@"
  local exit_code=$?
  set -e
  if [[ $exit_code -eq 0 ]]; then
    success "$label"
  else
    error "$label (exit $exit_code)"
  fi
  return $exit_code
}

# ===========================================================================
# SUBCOMMAND: fast
# Mirrors: Art_Validation Pipeline / validate.yml (fast mode)
# ===========================================================================
cmd_fast() {
  ci_header "FAST VALIDATION" "validate.yml → Art_Validation Pipeline"
  activate_venv

  local exit_code=0

  # Step 1: pre-commit on changed files (same as run_validation.sh --fast)
  # CI runs pre-commit against files changed vs the base branch.
  local changed_files
  changed_files="$(git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only HEAD 2>/dev/null || echo "")"

  if [[ -n "$changed_files" ]]; then
    # shellcheck disable=SC2086
    run_cmd "pre-commit (changed files)" \
      pre-commit run --show-diff-on-failure --files $changed_files || exit_code=$?
  else
    warn "No changed files detected — skipping pre-commit step"
  fi

  # Step 2: pytest — exact targets from validate.yml
  run_cmd "pytest (fast targets)" \
    pytest \
      --junitxml=validation-junit.xml \
      --maxfail=1 \
      tests/test_session_logger_log_adapters.py \
      tests/test_session_query_cli.py \
      tests/utils/test_error_log.py \
      tests/smoke/test_artifacts_hash.py \
    || exit_code=$?

  record_result "fast (validate.yml)" "$exit_code"
  return $exit_code
}

# ===========================================================================
# SUBCOMMAND: quick
# Mirrors: Resilient Validation Suite — quick group (resilient_validation.yml)
# ===========================================================================
cmd_quick() {
  ci_header "QUICK TESTS" "resilient_validation.yml → quick group"
  activate_venv

  run_cmd "pytest (quick)" \
    pytest tests/ \
      -v \
      -m "not slow and not integration" \
      --timeout=60 \
      --tb=short \
      --maxfail=20
}

# ===========================================================================
# SUBCOMMAND: slow
# Mirrors: Resilient Validation Suite — slow group (resilient_validation.yml)
# ===========================================================================
cmd_slow() {
  ci_header "SLOW TESTS" "resilient_validation.yml → slow group"
  activate_venv

  run_cmd "pytest (slow)" \
    pytest tests/ \
      -v \
      -m "slow" \
      --timeout=600 \
      --maxfail=5 \
      --tb=short
}

# ===========================================================================
# SUBCOMMAND: integration
# Mirrors: Resilient Validation Suite — integration group (resilient_validation.yml)
# ===========================================================================
cmd_integration() {
  ci_header "INTEGRATION TESTS" "resilient_validation.yml → integration group"
  activate_venv

  run_cmd "pytest (integration)" \
    pytest tests/ \
      -v \
      -m "integration and not slow" \
      --timeout=300 \
      --tb=short \
      --maxfail=10
}

# ===========================================================================
# SUBCOMMAND: docs
# Mirrors: Resilient Validation Suite — documentation group (resilient_validation.yml)
# Note: npx markdown-link-check failures are non-blocking in CI (|| true).
# ===========================================================================
cmd_docs() {
  ci_header "DOCUMENTATION CHECKS" "resilient_validation.yml → documentation group"
  activate_venv

  local exit_code=0

  if command -v npx &>/dev/null; then
    # CI uses || true so link-check failures are non-blocking
    run_cmd "markdown-link-check" \
      bash -c 'npx markdown-link-check "docs/**/*.md" --retry --timeout 5000 || true'
  else
    warn "npx not found — skipping markdown-link-check (install Node.js to enable)"
  fi

  if [[ -f "$ROOT/scripts/validate_docs.py" ]]; then
    # Also non-blocking in CI
    run_cmd "validate_docs.py --fix" \
      bash -c 'python scripts/validate_docs.py --fix || echo "non-blocking"'
  else
    warn "scripts/validate_docs.py not found — skipping"
  fi

  record_result "docs (resilient_validation.yml)" "$exit_code"
  return $exit_code
}

# ===========================================================================
# SUBCOMMAND: premerge
# Mirrors: Pre-Merge Validation (pre-merge-validation.yml)
# ===========================================================================
cmd_premerge() {
  ci_header "PRE-MERGE VALIDATION" "pre-merge-validation.yml"
  activate_venv

  local exit_code=0

  # Step 1: auto_fix_common_issues --check-only (must pass for merge gate)
  if [[ -f "$ROOT/scripts/ci/auto_fix_common_issues.py" ]]; then
    run_cmd "auto_fix_common_issues --check-only" \
      python scripts/ci/auto_fix_common_issues.py --check-only || exit_code=$?
  else
    warn "scripts/ci/auto_fix_common_issues.py not found — skipping"
  fi

  # Step 2: pytest — pre-merge flags (non-blocking in CI via || true)
  run_cmd "pytest (pre-merge)" \
    bash -c 'pytest tests/ -v --tb=short -x --maxfail=3 --timeout=300 || true'

  # Step 3: ruff check — non-blocking in CI
  run_cmd "ruff check" \
    bash -c 'python -m ruff check src/ tests/ --output-format=github || true'

  record_result "premerge (pre-merge-validation.yml)" "$exit_code"
  return $exit_code
}

# ===========================================================================
# SUBCOMMAND: lint
# Runs ruff + pre-commit on changed files only (not a direct CI workflow mirror,
# but matches what both validate.yml and pre-merge-validation.yml do internally).
# ===========================================================================
cmd_lint() {
  ci_header "LINT (changed files)" "validate.yml + pre-merge-validation.yml"
  activate_venv

  local exit_code=0

  # ruff on src/ and tests/
  run_cmd "ruff check src/ tests/" \
    python -m ruff check src/ tests/ || exit_code=$?

  # pre-commit on changed files
  local changed_files
  changed_files="$(git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only HEAD 2>/dev/null || echo "")"

  if [[ -n "$changed_files" ]]; then
    # shellcheck disable=SC2086
    run_cmd "pre-commit (changed files)" \
      pre-commit run --show-diff-on-failure --files $changed_files || exit_code=$?
  else
    warn "No changed files detected — running pre-commit on all files"
    run_cmd "pre-commit (all files)" \
      pre-commit run --show-diff-on-failure --all-files || exit_code=$?
  fi

  record_result "lint" "$exit_code"
  return $exit_code
}

# ===========================================================================
# SUBCOMMAND: all
# Runs fast + quick + premerge sequentially; always prints the summary.
# ===========================================================================
cmd_all() {
  ci_header "ALL CHECKS (fast + quick + premerge)" "validate.yml + resilient_validation.yml + pre-merge-validation.yml"

  set +e

  cmd_fast
  record_result "fast" $?

  cmd_quick
  record_result "quick" $?

  cmd_premerge
  record_result "premerge" $?

  set -e

  print_summary
}

# ===========================================================================
# SUBCOMMAND: help
# ===========================================================================
cmd_help() {
  sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# //'
  echo ""
}

# ===========================================================================
# Entry point — dispatch to subcommand
# ===========================================================================
SUBCOMMAND="${1:-help}"
shift || true

case "$SUBCOMMAND" in
  fast)        cmd_fast        ;;
  quick)       cmd_quick       ;;
  slow)        cmd_slow        ;;
  integration) cmd_integration ;;
  docs)        cmd_docs        ;;
  premerge)    cmd_premerge    ;;
  lint)        cmd_lint        ;;
  all)         cmd_all         ;;
  help|--help|-h) cmd_help    ;;
  *)
    error "Unknown subcommand: $SUBCOMMAND"
    cmd_help
    exit 1
    ;;
esac
