#!/usr/bin/env bash
# .codex/scripts/setup.sh
# Enhanced deterministic bootstrap for ChatGPT-Codex with comprehensive error recovery 

set -Eeuo pipefail

# ----------------------------
# Enhanced controls
# ----------------------------
GRACEFUL="${CODEX_GRACEFUL:-1}"
STRICT_HASH="${CODEX_STRICT_HASH:-0}"
STRICT_SETUP="${CODEX_STRICT_SETUP:-0}"
CODEX_SYNC_GROUPS="${CODEX_SYNC_GROUPS:-base,cpu}"
ENV_SNAPSHOT="${CODEX_ENV_SNAPSHOT:-0}"
TYPECHECK="${CODEX_TYPECHECK:-0}"

# ----------------------------
# Logging infrastructure
# ----------------------------
mkdir -p .codex/logs .codex/cache
WARN_FILE=".codex/logs/setup_warnings.log"
: > "$WARN_FILE"

log()  { printf "[setup] %s %s\n" "$(date -Iseconds)" "$*"; }
warn() { log "WARN: $*"; printf "%s\n" "$*" >> "$WARN_FILE"; }
die()  { printf "[setup][ERROR] %s\n" "$*" >&2; exit 1; }
section() { log "=== $* ==="; }

maybe_fail() {
  local msg="$1"
  if [[ "$GRACEFUL" = "1" && "$STRICT_SETUP" = "0" ]]; then
    warn "$msg — continuing (GRACEFUL=1)"
  else
    die "$msg"
  fi
}

run() {
  set +e
  bash -lc "$*"
  local ec=$?
  set -e
  if (( ec != 0 )); then
    maybe_fail "Command failed (exit $ec): $*"
  fi
}

dequote_once() {
  local s="$1"
  case "$s" in
    \"*\"|\'*\') printf %s "${s:1:${#s}-2}";;
    *)           printf %s "$s";;
  esac
}

# ----------------------------
# Context setup
# ----------------------------
export DEBIAN_FRONTEND=noninteractive
REPO_ROOT_RAW="${REPO_ROOT:-$(pwd)}"
REPO_ROOT="$(dequote_once "$REPO_ROOT_RAW")"
case "$REPO_ROOT" in
  /*) : ;;
  *)  REPO_ROOT="$(pwd)";;
esac

HF_HOME_DEFAULT="${REPO_ROOT}/.hf_cache"
export HF_HOME="${HF_HOME:-$HF_HOME_DEFAULT}"
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PYTHONUTF8=1
export UV_SYSTEM_PYTHON=0
export UV_LINK_MODE=copy

mkdir -p "${REPO_ROOT}/artifacts" "${REPO_ROOT}/data" "${HF_HOME}"
log "Repo: $REPO_ROOT"
log "HF_HOME: $HF_HOME"

# ----------------------------
# GitHub token resolution
# ----------------------------
resolve_github_token() {
  local candidates=(GH_PAT GITHUB_TOKEN GH_TOKEN _CODEX_ACTION_RUNNER _CODEX_BOT_RUNNER CODEX_ENVIRONMENT_RUNNER)
  unset GH_TOKEN
  for name in "${candidates[@]}"; do
    local val="${!name-}"
    if [[ -n "${val:-}" ]]; then
      export GH_TOKEN="$val"
      export GITHUB_TOKEN="${GITHUB_TOKEN:-$val}"
      export CODEX_GH_TOKEN_SOURCE="$name"
      break
    fi
  done

  run "python - <<'PY'
import os, json, hashlib, pathlib
pathlib.Path('.codex/cache').mkdir(parents=True, exist_ok=True)
names = ['GH_PAT','GITHUB_TOKEN','GH_TOKEN','_CODEX_ACTION_RUNNER','_CODEX_BOT_RUNNER','CODEX_ENVIRONMENT_RUNNER','CODEX_RUNNER_TOKEN']
vals = {n: os.getenv(n) for n in names}
present = {n: (v is not None and v != '') for n,v in vals.items()}
group = ['GH_PAT','GITHUB_TOKEN','GH_TOKEN','_CODEX_ACTION_RUNNER','_CODEX_BOT_RUNNER','CODEX_ENVIRONMENT_RUNNER']
digests = {hashlib.sha256(vals[n].encode()).hexdigest() for n in group if vals.get(n)}
all_equal = (len(digests) <= 1)
json.dump({'present': present, 'all_equal_group': all_equal, 'source': os.getenv('CODEX_GH_TOKEN_SOURCE')}, open('.codex/cache/secrets.status.json','w'))
print('[secrets] GH token source:', os.getenv('CODEX_GH_TOKEN_SOURCE') or 'none')
print('[secrets] GH tokens all equal across aliases:', all_equal)
PY"
}
resolve_github_token

# ----------------------------
# System dependencies
# ----------------------------
section "Installing system dependencies"
if command -v apt-get >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1; then
    run "sudo apt-get update -y"
    run "sudo apt-get install -y --no-install-recommends python3 python3-venv python3-pip python3-dev build-essential pkg-config git git-lfs curl ca-certificates libffi-dev libssl-dev"
  else
    run "apt-get update -y"
    run "apt-get install -y --no-install-recommends python3 python3-venv python3-pip python3-dev build-essential pkg-config git git-lfs curl ca-certificates libffi-dev libssl-dev"
  fi
  run "git lfs install --skip-repo"
else
  log "apt-get not available; assuming base image already has essentials."
fi

# ----------------------------
# UV installation
# ----------------------------
section "Installing uv package manager"
if ! command -v uv >/dev/null 2>&1; then
  if command -v curl >/dev/null 2>&1; then
    run "curl -fsSL https://astral.sh/uv/install.sh | bash"
  fi
  if ! command -v uv >/dev/null 2>&1; then
    if command -v pipx >/dev/null 2>&1; then
      run "pipx install uv"
    else
      run "python3 -m pip install --user uv || true"
    fi
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi
command -v uv >/dev/null 2>&1 && log "uv: $(uv --version || true)"

# ----------------------------
# Virtual environment setup
# ----------------------------
section "Setting up Python virtual environment"
cd "$REPO_ROOT"

if [[ -f "uv.lock" || -f "pyproject.toml" ]] && command -v uv >/dev/null 2>&1; then
  run "uv venv --seed .venv"
  [[ ! -d .venv ]] && { warn "uv venv did not create .venv; falling back to python venv"; run "python3 -m venv .venv"; }
else
  run "python3 -m venv .venv"
fi

# shellcheck disable=SC1091
source ".venv/bin/activate" || maybe_fail "Failed to activate virtualenv"
export UV_PYTHON="$(command -v python)"

# ----------------------------
# Enhanced lock file repair
# ----------------------------
_fix_lock_constraints() {
  if [[ -f "uv.lock" ]]; then
    # Check for common lock file issues
    if grep -q "missing.*source" uv.lock || ! uv lock --dry-run >/dev/null 2>&1; then
      warn "Detected lock file issues, attempting comprehensive repair..."
      mkdir -p .codex/cache
      cp uv.lock ".codex/cache/uv.lock.broken.$(date +%s)" || true
      
      if [[ -f "pyproject.toml" ]]; then
        set +e
        # Try targeted package fixes first
        uv lock --upgrade-package duckdb >/dev/null 2>&1
        uv lock --upgrade-package torch >/dev/null 2>&1
        uv lock --upgrade >/dev/null 2>&1
        if [[ $? -ne 0 ]]; then
          warn "Lock upgrade failed, forcing clean rebuild"
          rm -f uv.lock
        fi
        set -e
      fi
    fi
  fi
}

# ----------------------------
# GPU package scrubbing
# ----------------------------
_scrub_gpu_lock_if_needed() {
  local want_gpu=0
  local OIFS="$IFS"
  IFS=',' read -ra _tok <<<"${CODEX_SYNC_GROUPS}"
  IFS="$OIFS"
  
  for t in "${_tok[@]}"; do
    [[ "${t}" == "gpu" || "${t}" == "all" || "${t}" == "extras" ]] && want_gpu=1
  done
  
  if [[ -f "uv.lock" && ${want_gpu} -eq 0 ]]; then
    if grep -Eq '(^|\")nvidia-(cublas|cuda|cudnn|cufft|curand|cusolver|cusparse|cusparselt|nccl|nvjitlink)|(^|\")pytorch-cuda|(^|\")triton' uv.lock; then
      log "Detected GPU pins in uv.lock while CODEX_SYNC_GROUPS=[${CODEX_SYNC_GROUPS}] excludes gpu; rebuilding lock..."
      mkdir -p .codex/cache || true
      cp uv.lock ".codex/cache/uv.lock.gpu.bak.$(date +%s)" || true
      set +e
      uv lock --upgrade
      local ec=$?
      set -e
      (( ec == 0 )) || warn "uv lock --upgrade failed; continuing with existing lock"
    fi
  fi
}

# ----------------------------
# Dependency sync with comprehensive fallbacks
# ----------------------------
section "Resolving extras from CODEX_SYNC_GROUPS='${CODEX_SYNC_GROUPS}'"
EXTRA_FLAGS=()
WANT_CPU=0
WANT_GPU=0
IFS=',' read -r -a TOKENS <<< "$CODEX_SYNC_GROUPS"
for t in "${TOKENS[@]}"; do
  case "$t" in
    base) : ;;
    +extras|all) EXTRA_FLAGS+=("--all-extras") ;;
    cpu) WANT_CPU=1 ;;
    gpu) WANT_GPU=1 ;;
    *)   EXTRA_FLAGS+=("--extra" "$t") ;;
  esac
done

_uv_sync_with_comprehensive_fallback() {
  [[ ! -f "pyproject.toml" ]] && { warn "pyproject.toml not found"; return 1; }
  
  # Enhanced lock repair
  _fix_lock_constraints
  
  # Try normal sync first
  if uv sync; then
    return 0
  fi
  
  warn "uv sync failed; attempting lock rebuild"
  mkdir -p .codex/cache
  [[ -f uv.lock ]] && cp uv.lock ".codex/cache/uv.lock.bad.$(date +%s)" || true
  rm -f uv.lock
  
  if uv lock && uv sync; then
    return 0
  fi
  
  warn "uv lock/sync still failing — falling back to editable install"
  # Build extras specification for pip install
  local EXTRAS_COMMA=""
  for flag in "${EXTRA_FLAGS[@]}"; do
    if [[ "$flag" == "--extra" ]]; then
      continue
    elif [[ "$flag" != "--all-extras" ]]; then
      EXTRAS_COMMA="${EXTRAS_COMMA:+$EXTRAS_COMMA,}$flag"
    fi
  done
  
  local EXTRAS_SPEC=""
  [[ -n "$EXTRAS_COMMA" ]] && EXTRAS_SPEC="[$EXTRAS_COMMA]"
  uv pip install --python "$UV_PYTHON" -e ".${EXTRAS_SPEC}" || warn "editable install failed"
}

section "Syncing project dependencies (with comprehensive recovery)"
_scrub_gpu_lock_if_needed
_uv_sync_with_comprehensive_fallback

if (( ${#EXTRA_FLAGS[@]} )); then
  run "uv sync ${EXTRA_FLAGS[*]} || true"
fi

# ----------------------------
# Enhanced torch CPU enforcement
# ----------------------------
if (( WANT_CPU == 1 )); then
  section "Installing and enforcing CPU-only torch"
  # First install from CPU index
  run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu torch"
  # Then force reinstall CPU-specific version
  run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu --no-deps --force-reinstall 'torch==2.8.0+cpu'"
fi

if (( WANT_GPU == 1 )); then
  section "GPU extras requested"
  if [[ -n "${TORCH_CUDA_INDEX:-}" ]]; then
    run "uv pip install --python \"$UV_PYTHON\" --index-url '${TORCH_CUDA_INDEX}' torch"
  else
    warn "GPU requested but no TORCH_CUDA_INDEX provided; skipping CUDA install."
  fi
fi

# ----------------------------
# Pre-commit setup
# ----------------------------
section "Setting up pre-commit hooks"
if [[ -f ".pre-commit-config.yaml" ]]; then
  run "uv pip install --python \"$UV_PYTHON\" pre-commit"
  run "pre-commit install -f -t pre-commit -t pre-push -t prepare-commit-msg"
fi

# ----------------------------
# Optional features
# ----------------------------
MODEL_NAME="${MODEL_NAME:-sshleifer/tiny-gpt2}"
if [[ "${TRANSFORMERS_PREWARM:-0}" = "1" ]]; then
  section "Pre-warming Hugging Face cache"
  run "python - <<'PY'
import os, sys
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    m=os.getenv('MODEL_NAME','sshleifer/tiny-gpt2')
    c=os.getenv('HF_HOME')
    AutoTokenizer.from_pretrained(m, cache_dir=c, trust_remote_code=False)
    AutoModelForCausalLM.from_pretrained(m, cache_dir=c, trust_remote_code=False)
    print('[setup] Cached:', m, '->', c)
except Exception as e:
    print('[setup][WARN] HF pre-warm skipped/failed:', e, file=sys.stderr)
PY"
else
  log "HF pre-warm skipped (set TRANSFORMERS_PREWARM=1 to enable)."
fi

# ----------------------------
# LFS check
# ----------------------------
section "Checking for large files not in LFS"
if command -v git >/dev/null 2>&1; then
  set +e
  git rev-list --objects --all 2>/dev/null | \
    git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' 2>/dev/null | \
    awk '$1=="blob" && $3 > 100*1024*1024 {print $4 " " $3}' | while read -r PATH SIZE; do
      if ! git lfs ls-files --name-only 2>/dev/null | grep -qx "$PATH"; then
        warn "Large blob not in LFS: $PATH ($SIZE bytes)"
      fi
    done
  set -e
fi

# ----------------------------
# Enhanced health checks
# ----------------------------
section "Health check (can import torch?)"
python - <<'PY'
import sys
try:
  import torch
  print("torch OK:", getattr(torch,"__version__",None), "cuda?", getattr(torch,"cuda",None) and torch.cuda.is_available())
  if hasattr(torch.version, 'cuda') and torch.version.cuda:
    print("WARN: CUDA build detected - this may cause issues in CPU-only environment")
  else:
    print("CPU-only torch confirmed")
except ImportError:
  print("WARN: torch not available - will be handled in maintenance")
except Exception as e:
  print("FATAL: torch check failed:", e, file=sys.stderr)
  raise SystemExit(3)
PY

# ----------------------------
# Environment snapshot (optional)
# ----------------------------
if [[ "${ENV_SNAPSHOT:-0}" = "1" ]]; then
  section "Capturing environment snapshot"
  mkdir -p artifacts/env
  python --version > artifacts/env/python_version.txt 2>/dev/null || true
  pip freeze > artifacts/env/pip_freeze.txt 2>/dev/null || true
  uname -a > artifacts/env/uname.txt 2>/dev/null || true
  env | sort > artifacts/env/env_vars.txt 2>/dev/null || true
  log "Environment snapshot saved to artifacts/env/"
fi

# ----------------------------
# Type checking (optional)
# ----------------------------
if [[ "${TYPECHECK:-0}" = "1" ]] && command -v mypy >/dev/null 2>&1; then
  section "Running type checks"
  run "mypy src --ignore-missing-imports --no-error-summary || true"
fi

# ----------------------------
# Cache key generation
# ----------------------------
section "Generating cache key"
calc_lockhash() {
( sha256sum uv.lock               2>/dev/null || true
  sha256sum pyproject.toml        2>/dev/null || true
  sha256sum requirements.txt      2>/dev/null || true
  sha256sum requirements-dev.txt  2>/dev/null || true
  sha256sum docs/requirements.txt 2>/dev/null || true
  sha256sum services/api/requirements.txt 2>/dev/null || true
  sha256sum package-lock.json     2>/dev/null || true
  sha256sum yarn.lock             2>/dev/null || true
  sha256sum pnpm-lock.yaml        2>/dev/null || true
) | sha256sum | awk '{print $1}'
}
echo "$(calc_lockhash)" > .codex/cache/setup.locksum
log "Cache key (locksum): $(cat .codex/cache/setup.locksum)"

# ----------------------------
# Final summary
# ----------------------------
section "Setup complete"
if [[ -s "$WARN_FILE" ]]; then
  log "Setup finished with warnings. See $WARN_FILE"
  log "Warning count: $(wc -l < "$WARN_FILE")"
else
  log "Setup finished clean."
fi
