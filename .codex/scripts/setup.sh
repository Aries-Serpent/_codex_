#!/usr/bin/env bash
# .codex/scripts/setup.sh
# Deterministic, cache-friendly bootstrap for the Codex container with graceful fallbacks.

set -Eeuo pipefail

# ----------------------------
# Graceful mode controls
# ----------------------------
GRACEFUL="${CODEX_GRACEFUL:-1}"         # 1=continue on non-critical errors, 0=die
STRICT_HASH="${CODEX_STRICT_HASH:-0}"   # 1=fail on runner SHA mismatch
STRICT_SETUP="${CODEX_STRICT_SETUP:-0}" # 1=fail on any setup step failure
# Default to CPU-only groups in Codex to avoid pulling CUDA stacks.
# Valid tokens: base, dev, cpu, gpu, all, +extras
CODEX_SYNC_GROUPS="${CODEX_SYNC_GROUPS:-base,cpu}"

# ----------------------------
# Helpers & logging
# ----------------------------
mkdir -p .codex/logs .codex/cache
WARN_FILE=".codex/logs/setup_warnings.log"
: > "$WARN_FILE"

log()  { printf "[setup] %s %s\n" "$(date -Iseconds)" "$*"; }
warn() { log "WARN: $*"; printf "%s\n" "$*" >> "$WARN_FILE"; }
die()  { printf "[setup][ERROR] %s\n" "$*" >&2; exit 1; }

maybe_fail() {
  local msg="$1"
  if [[ "$GRACEFUL" = "1" && "$STRICT_SETUP" = "0" ]]; then
    warn "$msg — continuing (GRACEFUL=1)"
  else
    die  "$msg"
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
  # Remove a single pair of surrounding quotes (if present)
  local s="$1"
  case "$s" in
    \"*\"|\'*\') printf %s "${s:1:${#s}-2}";;
    *)           printf %s "$s";;
  esac
}

# ----------------------------
# Basic context + dirs
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
export UV_SYSTEM_PYTHON=1
export UV_LINK_MODE=copy

mkdir -p "${REPO_ROOT}/artifacts" "${REPO_ROOT}/data" "${HF_HOME}"

log "Repo: $REPO_ROOT"
log "HF_HOME: $HF_HOME"

# ----------------------------
# Secrets: resolve GitHub token (never print values)
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
# Runner integrity (warn by default)
# ----------------------------
if [[ -n "${CODEX_RUNNER_SHA256:-}" ]]; then
  RUNNER_BIN="${RUNNER_BIN:-/usr/local/bin/codex-runner}"
  if [[ -f "$RUNNER_BIN" ]]; then
    have_sha="$(sha256sum "$RUNNER_BIN" | awk '{print $1}')"
    if [[ "$have_sha" != "$CODEX_RUNNER_SHA256" ]]; then
      if [[ "$STRICT_HASH" = "1" ]]; then
        die "Runner SHA256 mismatch (STRICT_HASH=1)"
      else
        warn "Runner SHA256 mismatch — continuing (STRICT_HASH=0)"
      fi
    else
      log "Runner SHA256 OK."
    fi
  else
    warn "Runner binary not found at $RUNNER_BIN — skipping hash check."
  fi
fi

# ----------------------------
# System deps (idempotent)
# ----------------------------
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
# Install uv (preferred) with fallbacks
# ----------------------------
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
# Python env (prefer uv + lockfile)
# ----------------------------
cd "$REPO_ROOT"

if [[ -f "uv.lock" || -f "pyproject.toml" ]] && command -v uv >/dev/null 2>&1; then
  run "uv venv .venv"
  [[ ! -d .venv ]] && { warn "uv venv did not create .venv; falling back to python venv"; run "python3 -m venv .venv"; }
else
  run "python3 -m venv .venv"
fi

# shellcheck disable=SC1091
source .venv/bin/activate || maybe_fail "Failed to activate virtualenv"

# ----------------------------
# Selective dependency sync helpers
# ----------------------------
_uv_sync_base_only() {
  if command -v uv >/dev/null 2>&1 && [[ -f "pyproject.toml" ]]; then
    run "uv sync --no-dev"
  else
    # Fallback: pip based install
    run "python -m ensurepip -U || true"
    run "python -m pip install -U pip wheel"
    [[ -f "requirements.txt" ]]                 && run "pip install -r requirements.txt"
    [[ -f "docs/requirements.txt" ]]            && run "pip install -r docs/requirements.txt"
    [[ -f "services/api/requirements.txt" ]]    && run "pip install -r services/api/requirements.txt"
    if [[ -f "pyproject.toml" ]] && grep -q 'project' pyproject.toml 2>/dev/null; then
      run "pip install -e ."
    fi
  fi
}

# Detect stale CUDA/GPU pins in uv.lock and rebuild lock if we're in CPU-only mode
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
      (( ec == 0 )) || warn "uv lock --upgrade failed; continuing with existing lock (may still install CUDA wheels)"
    fi
  fi
}

_uv_sync_selective() {
  # Parse CODEX_SYNC_GROUPS and install dependency groups correctly.
  # Reference: uv "Locking and syncing" — use --group / --all-groups for optional-dependencies.
  local raw="${CODEX_SYNC_GROUPS:-base,cpu}"
  local OIFS="$IFS"
  IFS=, read -ra TOKENS <<<"$raw"
  IFS="$OIFS"

  local group_flags=()
  local want_cpu_torch=0
  local want_gpu=0

  for t in "${TOKENS[@]}"; do
    case "$t" in
      base) : ;;
      +extras|all)
        group_flags+=(--all-groups)
        ;;
      cpu)
        group_flags+=(--group "$t")
        want_cpu_torch=1
        ;;
      gpu)
        group_flags+=(--group "$t")
        want_gpu=1
        ;;
      *)
        group_flags+=(--group "$t")
        ;;
    esac
  done

  if command -v uv >/dev/null 2>&1 && [[ -f "pyproject.toml" ]]; then
    if (( ${#group_flags[@]} )); then
      run "uv sync ${group_flags[@]}"
    fi
  fi

  if (( want_cpu_torch )); then
    run "uv pip install --index-url https://download.pytorch.org/whl/cpu torch"
  fi

  if (( want_gpu )); then
    warn "GPU requested but Codex runners are CPU-only; skipping CUDA installs."
  fi
}

# ----------------------------
# Sync dependencies (base, then selective groups)
# ----------------------------
_scrub_gpu_lock_if_needed
_uv_sync_base_only
_uv_sync_selective

# ----------------------------
# Pre-commit hooks (optional)
# ----------------------------
if [[ -f ".pre-commit-config.yaml" ]]; then
  if command -v uv >/dev/null 2>&1; then
    run "uv pip install pre-commit"
  else
    run "python -m ensurepip -U || true"
    run "python -m pip install -U pip pre-commit"
  fi
  run "pre-commit install -f -t pre-commit -t pre-push -t prepare-commit-msg"
fi

# ----------------------------
# Hugging Face cache pre-warm (optional, gated by TRANSFORMERS_PREWARM=1)
# ----------------------------
MODEL_NAME="${MODEL_NAME:-sshleifer/tiny-gpt2}"
if [[ "${TRANSFORMERS_PREWARM:-0}" = "1" ]]; then
  run "cat > .codex/cache/_hf_prewarm.py <<'PY'
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
  run "python .codex/cache/_hf_prewarm.py"
else
  log "HF pre-warm skipped (set TRANSFORMERS_PREWARM=1 to enable)."
  fi

  # ----------------------------
  # LFS sanity: warn on >100MB non-LFS blobs
  # ----------------------------
if command -v git >/dev/null 2>&1; then
  set +e
  git rev-list --objects --all | \
    git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
    awk '$1=="blob" && $3 > 100*1024*1024 {print $4 " " $3}' | while read -r PATH SIZE; do
      if ! git lfs ls-files --name-only | grep -qx "$PATH"; then
        warn "Large blob not in LFS: $PATH ($SIZE bytes)"
      fi
    done
  set -e
  fi

  # ----------------------------
  # Enforce CPU-only torch build
  # ----------------------------
  run "uv pip install --index-url https://download.pytorch.org/whl/cpu \
      --no-deps --force-reinstall 'torch==2.8.0+cpu'"
  python - <<'PY'
import torch, sys
print('torch:', torch.__version__, 'cuda available?:', torch.cuda.is_available())
if torch.version.cuda:
    print('ERROR: CUDA build of torch detected in CPU CI')
    sys.exit(1)
PY

  # ----------------------------
  # Cache key stamp (unified with maintenance)
  # ----------------------------
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
if [[ -s "$WARN_FILE" ]]; then
  log "Setup finished with warnings. See $WARN_FILE"
else
  log "Setup finished clean."
fi
