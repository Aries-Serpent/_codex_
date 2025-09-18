#!/usr/bin/env bash
# Lightweight validation runner for local development and CI.
#
# Usage examples:
#   ./scripts/run_validation.sh --fast            # quick lint + smoke tests
#   ./scripts/run_validation.sh --full            # install dev deps and run full suite
#   ./scripts/run_validation.sh --files tests/foo/test_bar.py::TestCase::test_it
#
# Behaviour can also be tweaked via environment variables:
#   VALIDATE_MODE   - default mode when no --fast/--full flag is provided (fast|full)
#   PYTEST_OPTS     - extra arguments forwarded to pytest invocations
#   TEST_FAST       - whitespace separated list of tests/py.test selectors for fast mode
#   HEAVY_DEPS      - optional pip packages installed only in full mode

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: $(basename "$0") [options]

Options:
  --fast             Run the lightweight validation suite (default)
  --full             Run the full validation suite, installing dev dependencies
  --files <items>    Comma or space separated list of pytest targets to execute
  -h, --help         Show this help text

Any additional arguments are forwarded to pytest. Environment variables
such as PYTEST_OPTS can also be used to supply extra pytest options.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="${ROOT}/.venv_validation"
REQ_DEV="${ROOT}/requirements-dev.txt"
LOG="${ROOT}/validation.log"
JUNIT_XML="${ROOT}/validation-junit.xml"
COVERAGE_XML="${ROOT}/coverage.xml"
HOOK_DIR="${ROOT}/.github/validate-hooks.d"

MODE="${VALIDATE_MODE:-fast}"
FILES=""
PYTEST_FORWARD=""
PYTEST_ENV_EXTRA="${PYTEST_OPTS:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      MODE="fast"
      ;;
    --full)
      MODE="full"
      ;;
    --files)
      shift
      if [[ $# -eq 0 ]]; then
        echo "error: --files requires an argument" >&2
        exit 1
      fi
      FILES="$1"
      ;;
    --files=*)
      FILES="${1#*=}"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      if [[ $# -gt 0 ]]; then
        PYTEST_FORWARD+=" $*"
      fi
      break
      ;;
    *)
      PYTEST_FORWARD+=" $1"
      ;;
  esac
  shift || true
done

# Consolidate pytest options from environment and trailing args.
if [[ -n "$PYTEST_ENV_EXTRA" ]]; then
  PYTEST_FORWARD+=" $PYTEST_ENV_EXTRA"
fi
PYTEST_FORWARD="${PYTEST_FORWARD# }"

cd "$ROOT"
: > "$LOG"
rm -f "$JUNIT_XML" "$COVERAGE_XML"
echo "Validation started at $(date -u +"%Y-%m-%dT%H:%M:%SZ")" | tee -a "$LOG"
echo "Mode: $MODE" | tee -a "$LOG"
if [[ -n "$FILES" ]]; then
  echo "Target selectors: $FILES" | tee -a "$LOG"
fi
if [[ -n "$PYTEST_FORWARD" ]]; then
  echo "Additional pytest options: $PYTEST_FORWARD" | tee -a "$LOG"
fi

# Ensure the virtual environment exists.
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

export PIP_DISABLE_PIP_VERSION_CHECK=1
python -m pip install -U pip setuptools wheel >>"$LOG" 2>&1

if [[ -f "$REQ_DEV" && "$MODE" == "full" ]]; then
  echo "Installing development requirements from $(basename "$REQ_DEV")" | tee -a "$LOG"
  pip install -r "$REQ_DEV" >>"$LOG" 2>&1
  if [[ -n "${HEAVY_DEPS:-}" ]]; then
    echo "Installing heavy optional dependencies: $HEAVY_DEPS" | tee -a "$LOG"
    # shellcheck disable=SC2086
    pip install $HEAVY_DEPS >>"$LOG" 2>&1
  fi
else
  echo "Installing minimal fast-mode tools (pytest, pre-commit)" | tee -a "$LOG"
  pip install pytest pre-commit typer >>"$LOG" 2>&1
fi

export VALIDATE_MODE="$MODE"

run_hook_dir() {
  local stage="$1"
  if [[ -d "$HOOK_DIR" ]]; then
    for hook in "$HOOK_DIR"/*; do
      [[ -f "$hook" && -x "$hook" ]] || continue
      echo "Running $stage hook: $(basename "$hook")" | tee -a "$LOG"
      "$hook" "$MODE" "$stage" 2>&1 | tee -a "$LOG"
    done
  fi
}

run_hook_dir "pre"

# Run pre-commit hooks against modified files only.
echo "Running pre-commit hooks" | tee -a "$LOG"
declare -a PRECOMMIT_FILES
mapfile -t TRACKED_CHANGES < <(git diff --name-only --diff-filter=ACMRTUXB HEAD)
mapfile -t UNTRACKED_CHANGES < <(git ls-files --others --exclude-standard)
declare -A SEEN_FILES=()
for item in "${TRACKED_CHANGES[@]}" "${UNTRACKED_CHANGES[@]}"; do
  [[ -z "${item:-}" ]] && continue
  case "$item" in
    .venv_validation/*|validation.log|validation-junit.xml|coverage.xml|validation_summary.json)
      continue
      ;;
  esac
  # Ignore deleted files and directories.
  if [[ ! -e "$item" ]]; then
    continue
  fi
  if [[ -z "${SEEN_FILES[$item]:-}" ]]; then
    PRECOMMIT_FILES+=("$item")
    SEEN_FILES[$item]=1
  fi
done

if [[ ${#PRECOMMIT_FILES[@]} -eq 0 ]]; then
  BASE_REF="${VALIDATE_BASE_REF:-}"
  if [[ -z "$BASE_REF" && -n "${GITHUB_BASE_REF:-}" ]]; then
    BASE_REF="$GITHUB_BASE_REF"
  fi
  if [[ -n "$BASE_REF" ]]; then
    if [[ "$BASE_REF" != origin/* ]]; then
      BASE_TARGET="origin/$BASE_REF"
    else
      BASE_TARGET="$BASE_REF"
    fi
    if git rev-parse --verify "$BASE_TARGET" >/dev/null 2>&1; then
      BASE_COMMIT=$(git merge-base HEAD "$BASE_TARGET" 2>/dev/null || true)
      if [[ -n "$BASE_COMMIT" ]]; then
        mapfile -t BASE_CHANGES < <(git diff --name-only --diff-filter=ACMRTUXB "$BASE_COMMIT" HEAD)
        for item in "${BASE_CHANGES[@]}"; do
          [[ -z "${item:-}" ]] && continue
          case "$item" in
            .venv_validation/*) continue ;;
          esac
          if [[ ! -e "$item" ]]; then
            continue
          fi
          if [[ -z "${SEEN_FILES[$item]:-}" ]]; then
            PRECOMMIT_FILES+=("$item")
            SEEN_FILES[$item]=1
          fi
        done
      fi
    fi
  fi
fi

if [[ ${#PRECOMMIT_FILES[@]} -eq 0 ]]; then
  echo "No tracked changes detected; skipping pre-commit" | tee -a "$LOG"
else
  echo "pre-commit targets: ${#PRECOMMIT_FILES[@]} file(s)" | tee -a "$LOG"
  set +e
  pre-commit run --show-diff-on-failure --files "${PRECOMMIT_FILES[@]}" 2>&1 | tee -a "$LOG"
  PRECOMMIT_STATUS=${PIPESTATUS[0]}
  set -e
  if [[ $PRECOMMIT_STATUS -ne 0 ]]; then
    echo "pre-commit checks failed -- see $LOG" | tee -a "$LOG"
    deactivate || true
    exit 2
  fi
fi

declare -a PYTEST_ARGS
PYTEST_ARGS+=("--junitxml=$JUNIT_XML" "--maxfail=1")

if [[ -n "$FILES" ]]; then
  IFS=', ' read -r -a FILE_ITEMS <<< "$FILES"
  PYTEST_ARGS+=("${FILE_ITEMS[@]}")
elif [[ "$MODE" == "fast" ]]; then
  FAST_SELECTOR="${TEST_FAST:-tests/test_session_logger_log_adapters.py tests/test_session_query_cli.py tests/utils/test_error_log.py tests/smoke/test_artifacts_hash.py}"
  # shellcheck disable=SC2206
  FAST_ITEMS=($FAST_SELECTOR)
  PYTEST_ARGS+=("${FAST_ITEMS[@]}")
else
  PYTEST_ARGS+=("tests")
fi

if [[ -n "$PYTEST_FORWARD" ]]; then
  # shellcheck disable=SC2206
  EXTRA_OPTS=($PYTEST_FORWARD)
  PYTEST_ARGS+=("${EXTRA_OPTS[@]}")
fi

# Ensure deterministic logging of command.
echo "Running pytest ${PYTEST_ARGS[*]}" | tee -a "$LOG"
set +e
pytest "${PYTEST_ARGS[@]}" 2>&1 | tee -a "$LOG"
PYTEST_STATUS=${PIPESTATUS[0]}
set -e
if [[ $PYTEST_STATUS -ne 0 ]]; then
  echo "pytest failed (exit $PYTEST_STATUS). See $LOG and $JUNIT_XML" | tee -a "$LOG"
  deactivate || true
  exit $PYTEST_STATUS
fi

if [[ "$MODE" == "full" ]]; then
  echo "Generating coverage report" | tee -a "$LOG"
  declare -a COVERAGE_ARGS
  COVERAGE_ARGS+=("--maxfail=1" "--cov=src" "--cov-report=xml:$COVERAGE_XML")
  if [[ -n "$PYTEST_FORWARD" ]]; then
    # shellcheck disable=SC2206
    EXTRA_COV_OPTS=($PYTEST_FORWARD)
    COVERAGE_ARGS+=("${EXTRA_COV_OPTS[@]}")
  fi
  set +e
  pytest "${COVERAGE_ARGS[@]}" 2>&1 | tee -a "$LOG"
  COVERAGE_STATUS=${PIPESTATUS[0]}
  set -e
  if [[ $COVERAGE_STATUS -ne 0 ]]; then
    echo "Coverage generation exited with $COVERAGE_STATUS (continuing)." | tee -a "$LOG"
  fi
fi

run_hook_dir "post"

echo "Validation successful" | tee -a "$LOG"
deactivate || true
exit 0
