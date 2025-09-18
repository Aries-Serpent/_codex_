#!/usr/bin/env bash
# Lightweight validation runner for local dev and CI
# Usage:
#   ./scripts/run_validation.sh --fast            # quick checks only
#   ./scripts/run_validation.sh --full            # install dev deps & run full suite
#   ./scripts/run_validation.sh --files f1,f2     # run only given test files (comma-separated)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="${ROOT}/.venv_validation"
REQ_DEV="${ROOT}/requirements-dev.txt"
LOG="${ROOT}/validation.log"
HOOK_DIR="${ROOT}/.github/validate-hooks.d"

MODE="fast"
FILES=""
PYTEST_EXTRA_ENV=${PYTEST_EXTRA:-""}
PASSTHROUGH=()
SKIP_PRECOMMIT=${VALIDATE_SKIP_PRECOMMIT:-"0"}
SKIP_HOOKS=${VALIDATE_SKIP_HOOKS:-"0"}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      MODE="fast"
      shift
      ;;
    --full)
      MODE="full"
      shift
      ;;
    --files)
      shift
      if [[ $# -eq 0 ]]; then
        echo "Missing value for --files" >&2
        exit 1
      fi
      FILES="$1"
      shift
      ;;
    --files=*)
      FILES="${1#*=}"
      shift
      ;;
    --)
      shift
      PASSTHROUGH+=("$@")
      break
      ;;
    *)
      PASSTHROUGH+=("$1")
      shift
      ;;
  esac
done

{
  echo "Validation started at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Mode: $MODE"
} > "$LOG"

if [[ ! -d "$VENV_DIR" ]]; then
  python -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

pip install -U pip setuptools wheel >> "$LOG" 2>&1

if [[ -f "$REQ_DEV" && "$MODE" == "full" ]]; then
  echo "Installing dev requirements..." | tee -a "$LOG"
  pip install -r "$REQ_DEV" >> "$LOG" 2>&1
else
  echo "Installing fast-mode requirements..." | tee -a "$LOG"
  if ! pip install pytest pre-commit ruff >> "$LOG" 2>&1; then
    pip install pytest >> "$LOG" 2>&1
  fi
fi

if [[ "$SKIP_PRECOMMIT" == "1" ]]; then
  echo "VALIDATE_SKIP_PRECOMMIT=1 -> skipping pre-commit" | tee -a "$LOG"
elif command -v pre-commit >/dev/null 2>&1; then
  echo "Running pre-commit hooks..." | tee -a "$LOG"
  PRECOMMIT_STATUS=0

  # Collect local modifications (tracked + staged + untracked)
  declare -A _seen_files
  LOCAL_FILES=()
  while IFS= read -r file; do
    [[ -n "$file" ]] || continue
    [[ -n "${_seen_files[$file]:-}" ]] && continue
    _seen_files[$file]=1
    LOCAL_FILES+=("$file")
  done < <(git diff --name-only && git diff --cached --name-only && git ls-files --others --exclude-standard)

  if [[ ${#LOCAL_FILES[@]} -gt 0 ]]; then
    echo "  • linting local modifications (${#LOCAL_FILES[@]})" | tee -a "$LOG"
    if ! pre-commit run --show-diff-on-failure --files "${LOCAL_FILES[@]}" >> "$LOG" 2>&1; then
      PRECOMMIT_STATUS=2
    fi
  fi

  BASE_CANDIDATES=()
  [[ -n "${VALIDATE_BASE_REF:-}" ]] && BASE_CANDIDATES+=("$VALIDATE_BASE_REF")
  if UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null); then
    BASE_CANDIDATES+=("$UPSTREAM")
  fi
  [[ -n "${GITHUB_BASE_REF:-}" ]] && BASE_CANDIDATES+=("origin/${GITHUB_BASE_REF}")
  BASE_CANDIDATES+=("origin/HEAD" "origin/main" "origin/master" "HEAD^")

  HEAD_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "")
  BASE_COMMIT=""
  for candidate in "${BASE_CANDIDATES[@]}"; do
    [[ -n "$candidate" ]] || continue
    if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
      candidate_commit=$(git rev-parse "$candidate")
      if [[ -n "$candidate_commit" && "$candidate_commit" != "$HEAD_COMMIT" ]]; then
        BASE_COMMIT="$candidate_commit"
        break
      fi
    fi
  done

  if [[ -n "$BASE_COMMIT" ]]; then
    echo "  • linting diff $BASE_COMMIT..$HEAD_COMMIT" | tee -a "$LOG"
    if ! pre-commit run --show-diff-on-failure --from-ref "$BASE_COMMIT" --to-ref "$HEAD_COMMIT" >> "$LOG" 2>&1; then
      PRECOMMIT_STATUS=2
    fi
  elif [[ $PRECOMMIT_STATUS -eq 0 ]]; then
    echo "  • no base ref detected; linting all tracked files once" | tee -a "$LOG"
    if ! pre-commit run --show-diff-on-failure --all-files >> "$LOG" 2>&1; then
      PRECOMMIT_STATUS=2
    fi
  fi

  if [[ $PRECOMMIT_STATUS -ne 0 ]]; then
    echo "pre-commit checks failed -- see $LOG" | tee -a "$LOG"
    deactivate
    exit $PRECOMMIT_STATUS
  fi
else
  echo "pre-commit not installed; skipping hooks" | tee -a "$LOG"
fi

if [[ "$SKIP_HOOKS" != "1" && -d "$HOOK_DIR" ]]; then
  shopt -s nullglob
  HOOKS=("$HOOK_DIR"/*)
  shopt -u nullglob
  for hook in "${HOOKS[@]}"; do
    [[ -f "$hook" && -x "$hook" ]] || continue
    echo "Running validation hook $(basename "$hook")" | tee -a "$LOG"
    if ! "$hook" "$MODE" >> "$LOG" 2>&1; then
      echo "Hook $(basename "$hook") failed -- see $LOG" | tee -a "$LOG"
      deactivate
      exit 3
    fi
  done
fi

PYTEST_ARGS=("--junitxml=report.xml" "--maxfail=1" "-q")
if [[ -n "$FILES" ]]; then
  IFS=',' read -ra FARR <<< "$FILES"
  PYTEST_ARGS+=("${FARR[@]}")
elif [[ "$MODE" == "fast" ]]; then
  PYTEST_ARGS+=(
    "tests/test_ingestion_split_cache.py"
    "tests/test_query_logs_build_query.py"
    "tests/test_query_logs_tail.py"
    "tests/test_session_logger_log_adapters.py"
    "tests/security/test_log_redaction.py"
    "tests/test_session_query_cli.py"
    "tests/test_chat_session_exit.py"
    "tests/test_chat_session.py"
  )
else
  PYTEST_ARGS+=("tests")
fi

PYTEST_ENV_ARGS=()
if [[ -n "$PYTEST_EXTRA_ENV" ]]; then
  # shellcheck disable=SC2206  # we intentionally rely on word-splitting here
  PYTEST_ENV_ARGS=($PYTEST_EXTRA_ENV)
fi

unset CODEX_SESSION_ID

ALL_ARGS=("${PYTEST_ARGS[@]}" "${PYTEST_ENV_ARGS[@]}" "${PASSTHROUGH[@]}")

echo "Running pytest ${ALL_ARGS[*]}" | tee -a "$LOG"
set +e
pytest "${PYTEST_ARGS[@]}" "${PYTEST_ENV_ARGS[@]}" "${PASSTHROUGH[@]}" 2>&1 | tee -a "$LOG"
RET=${PIPESTATUS[0]}
set -e

if [[ $RET -ne 0 ]]; then
  echo "pytest failed (exit $RET). See $LOG and report.xml" | tee -a "$LOG"
  deactivate
  exit $RET
fi

if python -c "import coverage" >/dev/null 2>&1; then
  echo "Generating coverage..." | tee -a "$LOG"
  pytest --maxfail=1 --disable-warnings -q --cov=src --cov-report=xml:coverage.xml "${PYTEST_ENV_ARGS[@]}" "${PASSTHROUGH[@]}" >> "$LOG" 2>&1 || true
fi

{
  echo "Artifacts:"
  echo "  junit: report.xml"
  [[ -f coverage.xml ]] && echo "  coverage: coverage.xml"
  echo "Log: validation.log"
} >> "$LOG"

echo "Validation successful" | tee -a "$LOG"
deactivate
exit 0
