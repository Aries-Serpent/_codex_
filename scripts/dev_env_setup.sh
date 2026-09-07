#!/usr/bin/env bash
# scripts/dev_env_setup.sh
#
# Sets up a local Python virtual environment that matches the GitHub Actions CI
# environment as closely as possible, so developers can catch failures before pushing.
#
# Usage:
#   bash scripts/dev_env_setup.sh [--no-torch] [--no-node] [--clean] [--check-cache] [--help]
#
# Options:
#   --no-torch      Skip the PyTorch CPU install (saves ~1 GB, skips torch-dependent tests)
#   --no-node       Skip Node.js / markdown-link-check install
#   --clean         Purge pip download cache and delete .venv_ci, then reinstall
#   --check-cache   Show pip cache info and .venv_ci disk usage, then exit
#   --help          Show this message and exit

set -euo pipefail

# ---------------------------------------------------------------------------
# Resolve the repository root regardless of where the script is invoked from.
# ---------------------------------------------------------------------------
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT/.venv_ci"

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
header()  { echo -e "\n${BOLD}${CYAN}=== $* ===${RESET}\n"; }

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
INSTALL_TORCH=true
INSTALL_NODE=true
DO_CLEAN=false
CHECK_CACHE=false

for arg in "$@"; do
  case "$arg" in
    --no-torch)    INSTALL_TORCH=false ;;
    --no-node)     INSTALL_NODE=false  ;;
    --clean)       DO_CLEAN=true       ;;
    --check-cache) CHECK_CACHE=true    ;;
    --help)
      sed -n '2,16p' "${BASH_SOURCE[0]}" | sed 's/^# //'
      exit 0
      ;;
    *)
      error "Unknown option: $arg"
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# --check-cache: show pip cache info and .venv_ci disk usage, then exit
# ---------------------------------------------------------------------------
if [[ "$CHECK_CACHE" == "true" ]]; then
  header "Cache status"
  echo -e "${CYAN}pip download cache:${RESET}"
  pip cache info 2>/dev/null || echo "  (pip not found or pip cache not available)"
  echo ""
  echo -e "${CYAN}.venv_ci disk usage:${RESET}"
  if [[ -d "$VENV_DIR" ]]; then
    du -sh "$VENV_DIR" 2>/dev/null || echo "  (could not measure)"
  else
    echo "  .venv_ci does not exist"
  fi
  echo ""
  echo -e "  Run ${CYAN}bash scripts/dev_env_setup.sh --clean${RESET} to purge."
  exit 0
fi

# ---------------------------------------------------------------------------
# --clean: purge pip download cache and remove .venv_ci
# ---------------------------------------------------------------------------
if [[ "$DO_CLEAN" == "true" ]]; then
  header "Cleaning caches"
  info "Purging pip download cache ..."
  pip cache purge 2>/dev/null || true
  if [[ -d "$VENV_DIR" ]]; then
    info "Removing $VENV_DIR ..."
    rm -rf "$VENV_DIR"
    success "Removed $VENV_DIR"
  else
    info ".venv_ci not present — nothing to remove"
  fi
  success "Clean complete. Re-run without --clean to rebuild."
  exit 0
fi

# ---------------------------------------------------------------------------
# 1. Python version check
# CI targets Python 3.12; warn (but don't abort) on mismatch.
# ---------------------------------------------------------------------------
header "Python version check"

PYTHON_BIN=""
for candidate in python3.12 python3 python; do
  if command -v "$candidate" &>/dev/null; then
    PYTHON_BIN="$candidate"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  error "No Python interpreter found. Install Python 3.12."
  exit 1
fi

PYTHON_VERSION="$("$PYTHON_BIN" --version 2>&1 | awk '{print $2}')"
PYTHON_MAJOR_MINOR="${PYTHON_VERSION%.*}"

if [[ "$PYTHON_MAJOR_MINOR" != "3.12" ]]; then
  warn "CI uses Python 3.12, but found $PYTHON_VERSION."
  warn "Results may differ. Consider: pyenv install 3.12 && pyenv local 3.12"
else
  success "Python $PYTHON_VERSION (matches CI)"
fi

# ---------------------------------------------------------------------------
# 2. Create / reuse .venv_ci using a content hash to skip redundant installs.
# ---------------------------------------------------------------------------
header "Virtual environment: $VENV_DIR"

# Compute a hash of the files that define the install set.
LOCK_HASH=$(sha256sum "$ROOT/pyproject.toml" "$ROOT/requirements/lock.txt" 2>/dev/null \
  | sha256sum | cut -c1-16)
VENV_LOCK_FILE="$VENV_DIR/.install_hash"

SKIP_INSTALL=false
if [[ -d "$VENV_DIR" && -f "$VENV_LOCK_FILE" ]]; then
  if [[ "$(cat "$VENV_LOCK_FILE")" == "$LOCK_HASH" ]]; then
    SKIP_INSTALL=true
    success ".venv_ci is up-to-date (hash $LOCK_HASH) — skipping install"
  else
    info ".venv_ci exists but hash changed — reinstalling"
    rm -rf "$VENV_DIR"
  fi
fi

if [[ "$SKIP_INSTALL" == "false" && ! -d "$VENV_DIR" ]]; then
  info "Creating .venv_ci with $PYTHON_BIN ..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  success "Created $VENV_DIR"
fi

# Activate the venv for the rest of this script
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

PIP="$VENV_DIR/bin/pip"
PIP_CACHE_ARGS="--cache-dir ${HOME}/.cache/pip"

if [[ "$SKIP_INSTALL" == "true" ]]; then
  # Jump straight to verification
  :
else

# Always upgrade pip/setuptools/wheel to avoid resolver issues
info "Upgrading pip, setuptools, wheel ..."
"$PIP" install --quiet $PIP_CACHE_ARGS --upgrade pip setuptools wheel

# ---------------------------------------------------------------------------
# 3. Install pytest plugins FIRST
#
# CRITICAL: Plugins must be installed before the package itself.
# If they are installed after, pip may downgrade them to satisfy the
# package's looser constraints — causing subtle CI/local divergence.
# Source: resilient_validation.yml (install order is explicit there).
# ---------------------------------------------------------------------------
header "Step 1: Install pytest plugins aligned with project constraints"

info "Installing pytest plugin set from pyproject.toml-compatible ranges ..."
"$PIP" install --quiet $PIP_CACHE_ARGS \
  "pytest>=9.0.3,<10.0.0" \
  "pytest-timeout>=2.2.0,<3.0.0" \
  "pytest-xdist>=3.5.0,<4.0.0" \
  "pytest-cov>=4.1.0,<8.0.0" \
  "pytest-asyncio>=1.4.0,<2.0.0" \
  "pytest-mock>=3.15.1,<4.0.0" \
  "pytest-randomly>=3.15" \
  "pytest-rerunfailures>=16.6"

# Also install the pre-commit / typer / validate-pipeline deps from validate.yml
# The project bootstrap remains version-range-based instead of re-freezing older
# exact pins that drift from the canonical dependency metadata.
info "Installing validate.yml extra deps ..."
"$PIP" install --quiet $PIP_CACHE_ARGS \
  pre-commit==4.0.1 \
  typer==0.16.1

# Additional tools used in pre-merge-validation.yml
info "Installing ruff, pyyaml, nox ..."
"$PIP" install --quiet $PIP_CACHE_ARGS ruff pyyaml nox

success "Plugins installed"

# ---------------------------------------------------------------------------
# 4. Install the package in editable mode
#
# Done AFTER plugins so pip's dependency resolver cannot downgrade the
# pinned plugin versions while satisfying the package's own requirements.
# ---------------------------------------------------------------------------
header "Step 2: Install package (pip install -e .[dev])"

cd "$ROOT"

if "$PIP" install --quiet $PIP_CACHE_ARGS -e ".[dev]"; then
  success "pip install -e .[dev] succeeded"
else
  warn "pip install -e .[dev] failed, retrying without [dev] extras ..."
  "$PIP" install --quiet $PIP_CACHE_ARGS -e .
  warn "Installed without [dev] extras — some tests may be skipped"
fi

# ---------------------------------------------------------------------------
# 5. PyTorch CPU build (same index URL as CI resilient_validation.yml)
# Skip with --no-torch to save time / disk space.
# ---------------------------------------------------------------------------
if [[ "$INSTALL_TORCH" == "true" ]]; then
  header "Step 3: PyTorch CPU build"
  info "Installing torch, torchvision, torchaudio (CPU wheel) ..."
  info "(Use --no-torch to skip this ~1 GB download)"
  "$PIP" install --quiet $PIP_CACHE_ARGS \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu
  success "PyTorch CPU installed"
else
  warn "Skipping PyTorch install (--no-torch flag set)"
fi

# ---------------------------------------------------------------------------
# 6. Pre-commit hooks
# CI runs 'pre-commit run' as part of validate.yml; setting up hooks locally
# means the same checks fire automatically on every 'git commit'.
# ---------------------------------------------------------------------------
header "Step 4: Pre-commit hooks"

if command -v pre-commit &>/dev/null; then
  cd "$ROOT"
  pre-commit install --install-hooks
  success "pre-commit hooks installed"
else
  warn "pre-commit not found in PATH after install — check venv activation"
fi

# ---------------------------------------------------------------------------
# 7. Node.js / markdown-link-check (optional)
# CI resilient_validation.yml installs this for the documentation test group.
# ---------------------------------------------------------------------------
if [[ "$INSTALL_NODE" == "true" ]]; then
  header "Step 5: Node / markdown-link-check (documentation CI group)"

  if command -v npm &>/dev/null; then
    npm install -g markdown-link-check --quiet
    success "markdown-link-check installed"
  else
    warn "npm not found — skipping markdown-link-check."
    warn "Install Node.js (https://nodejs.org) then run: npm install -g markdown-link-check"
  fi
else
  warn "Skipping Node/markdown-link-check install (--no-node flag set)"
fi

# Record the install hash so future runs can skip reinstall.
echo "$LOCK_HASH" > "$VENV_LOCK_FILE"
info "Recorded install hash $LOCK_HASH → $VENV_LOCK_FILE"

fi  # end: SKIP_INSTALL == false

# ---------------------------------------------------------------------------
# 8. Verification — confirm all key tools are available
# ---------------------------------------------------------------------------
header "Verification"

TOOLS_OK=true
check_tool() {
  local tool="$1"
  local friendly="${2:-$1}"
  if command -v "$tool" &>/dev/null; then
    local ver
    ver="$("$tool" --version 2>&1 | head -1)" || ver="(version unknown)"
    success "$friendly: $ver"
  else
    error "$friendly not found in PATH"
    TOOLS_OK=false
  fi
}

check_tool python       "Python"
check_tool pytest       "pytest"
check_tool ruff         "ruff"
check_tool pre-commit   "pre-commit"
check_tool nox          "nox"

if command -v npx &>/dev/null; then
  success "npx (Node): $(npx --version 2>&1 | head -1)"
else
  warn "npx not available — 'documentation' CI group will be skipped locally"
fi

# ---------------------------------------------------------------------------
# 9. Summary
# ---------------------------------------------------------------------------

# Install git hooks (pre-push RVS pre-flight) — idempotent, safe to re-run
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$ROOT/scripts/install_hooks.sh" ]]; then
  bash "$ROOT/scripts/install_hooks.sh" || true
fi

header "Setup complete"

if [[ "$TOOLS_OK" == "true" ]]; then
  echo -e "${GREEN}${BOLD}All required tools verified.${RESET}"
else
  echo -e "${YELLOW}${BOLD}Some tools were not found — see warnings above.${RESET}"
fi

echo ""
echo -e "  Virtual env : ${CYAN}$VENV_DIR${RESET}"
echo -e "  Activate    : ${CYAN}source $VENV_DIR/bin/activate${RESET}"
echo -e "  Run CI checks locally:"
echo -e "    ${CYAN}bash scripts/ci_local.sh fast${RESET}      # Art_Validation / fast"
echo -e "    ${CYAN}bash scripts/ci_local.sh quick${RESET}     # Resilient Suite / quick"
echo -e "    ${CYAN}bash scripts/ci_local.sh premerge${RESET}  # Pre-Merge Validation"
echo -e "    ${CYAN}bash scripts/ci_local.sh all${RESET}       # fast + quick + premerge"
echo ""
