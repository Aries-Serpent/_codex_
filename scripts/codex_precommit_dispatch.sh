#!/usr/bin/env bash
set -Eeuo pipefail

# ---------- configuration knobs (override via env) ----------
: "${CODEX_PRECOMMIT_MODE:=auto}"     # auto | tox | nox | pytest
: "${CODEX_PRECOMMIT_STAGE:=commit}"  # commit | push (informational only)
: "${CODEX_KEEP_COVERAGE:=0}"         # 1 to preserve coverage; otherwise discard
: "${CODEX_VALIDATE_HEAD_LOG:=0}"     # 1 to validate .codex/action_log.ndjson parity (non-mutating)
: "${CODEX_TEST_PATHS:=tests}"        # what to test (space-separated ok)
# ------------------------------------------------------------

cleanup() {
  # Remove artifacts in repo (tox/nox keep theirs under .tox/.nox)
  if [[ "${CODEX_KEEP_COVERAGE}" != "1" ]]; then rm -f .coverage || true; fi
  rm -rf .artifacts parquet 2>/dev/null || true
  find . -type d \( -name "__pycache__" -o -name ".pytest_cache" \) -prune -exec rm -rf {} + 2>/dev/null || true
  git show HEAD:.codex/action_log.ndjson > .codex/action_log.ndjson 2>/dev/null || true
}
trap cleanup EXIT

die_with_prompt() {
  echo ""
  echo "=== CODEX_DEEP_RESEARCH_PROMPT_BEGIN ==="
  echo "You are ChatGPT 5. The pre-commit test hook failed in the _codex_ repo."
  echo "Context:"
  echo "- Stage: ${CODEX_PRECOMMIT_STAGE}"
  echo "- Mode requested: ${CODEX_PRECOMMIT_MODE}"
  echo "- keep_coverage: ${CODEX_KEEP_COVERAGE}"
  echo "- validate_head_log: ${CODEX_VALIDATE_HEAD_LOG}"
  echo "- Test paths: ${CODEX_TEST_PATHS}"
  echo ""
  echo "Observed failure:"
  echo "$1"
  echo ""
  echo "Tasks:"
  echo "1) Diagnose root cause from the failure above and repo config."
  echo "2) Propose a minimal patch to fix and keep the working tree clean."
  echo "3) If artifacts remain (.coverage, __pycache__, .pytest_cache), show commands to remove and how to prevent."
  echo "4) Provide an updated snippet for .pre-commit-config.yaml and supporting scripts/tox/nox if needed."
  echo "=== CODEX_DEEP_RESEARCH_PROMPT_END ==="
  exit 1
}

validate_head_log_non_mutating() {
  if [[ "${CODEX_VALIDATE_HEAD_LOG}" == "1" ]]; then
    if git cat-file -e HEAD 2>/dev/null && git ls-tree -r --name-only HEAD | grep -q '^\.codex/action_log\.ndjson$'; then
      tmp="$(mktemp)"
      git show HEAD:.codex/action_log.ndjson > "$tmp" || true
      if ! diff -q .codex/action_log.ndjson "$tmp" >/dev/null 2>&1; then
        rm -f "$tmp"
        die_with_prompt "action_log.ndjson differs from HEAD; refusing to mutate tracked file during pre-commit."
      fi
      rm -f "$tmp"
    fi
  fi
}

export PYTHONDONTWRITEBYTECODE=1

run_pytest_clean() {
  local cover_env=()
  if [[ "${CODEX_KEEP_COVERAGE}" != "1" ]]; then
    # Avoid creating coverage file in repo; use temp location
    cover_env=(COVERAGE_FILE="$(mktemp -u)")
  fi
  if ! env "${cover_env[@]}" pytest -q -p no:cacheprovider ${CODEX_TEST_PATHS}; then
    die_with_prompt "pytest failed. See output above."
  fi
}

run_tox_isolated() {
  if ! command -v tox >/dev/null 2>&1; then return 1; fi
  # prefer a dedicated env; fallback to generic py if defined
  if tox -l 2>/dev/null | grep -qx "precommit-tests"; then
    if ! tox -q -e precommit-tests; then
      die_with_prompt "tox -e precommit-tests failed."
    fi
    return 0
  elif tox -l 2>/dev/null | grep -qE '^(py|py3[0-9])$'; then
    # generic env exists; still okay, but tests may run in-place
    if ! tox -q -e py; then
      die_with_prompt "tox -e py failed."
    fi
    return 0
  fi
  return 1
}

run_nox_isolated() {
  if ! command -v nox >/dev/null 2>&1; then return 1; fi
  if nox -l 2>/dev/null | grep -qx "precommit_tests"; then
    if ! nox -s precommit_tests; then
      die_with_prompt "nox -s precommit_tests failed."
    fi
    return 0
  fi
  return 1
}

case "${CODEX_PRECOMMIT_MODE}" in
  tox)
    run_tox_isolated || die_with_prompt "Requested tox mode but tox env not available."
    ;;
  nox)
    run_nox_isolated || die_with_prompt "Requested nox mode but nox session not available."
    ;;
  pytest)
    run_pytest_clean
    ;;
  auto|*)
    if run_tox_isolated; then :
    elif run_nox_isolated; then :
    else
      run_pytest_clean
    fi
    ;;
esac

validate_head_log_non_mutating
