#!/usr/bin/env bash
# .codex/scripts/maintenance.sh
# Enhanced maintenance script with fixed dequote_once function

set -Eeuo pipefail

# ----------------------------
# Enhanced controls
# ----------------------------
GRACEFUL="${CODEX_GRACEFUL:-1}"
STRICT_SETUP="${CODEX_STRICT_SETUP:-0}"
SMOKE="${CODEX_SMOKE:-0}"
ENV_SNAPSHOT="${CODEX_ENV_SNAPSHOT:-0}"
TYPECHECK="${CODEX_TYPECHECK:-0}"
CODEX_SYNC_GROUPS="${CODEX_SYNC_GROUPS:-base,cpu}"

# ----------------------------
# Logging infrastructure
# ----------------------------
mkdir -p .codex/logs .codex/cache
WARN_FILE=".codex/logs/maintenance_warnings.log"
: > "$WARN_FILE"

log()  { printf "[maint] %s %s\n" "$(date -Iseconds)" "$*"; }
warn() { log "WARN: $*"; printf "%s\n" "$*" >> "$WARN_FILE"; }
die()  { printf "[maint][ERROR] %s\n" "$*" >&2; exit 1; }
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

# FIXED: Define dequote_once function
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

log "Repo: $REPO_ROOT"
log "HF_HOME: $HF_HOME"

# ----------------------------
# GitHub token resolution (same as setup)
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
# GitHub token verification
# ----------------------------
section "Verifying GitHub token"
if [[ -n "${GH_TOKEN:-}" ]] && [[ "${CODEX_SKIP_GH_CHECK:-0}" != "1" ]]; then
  run "python - <<'PY'
import os, urllib.request, json
try:
    token = os.getenv('GH_TOKEN')
    req = urllib.request.Request('https://api.github.com/user')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('User-Agent', 'codex-maintenance/1.0')
    with urllib.request.urlopen(req, timeout=10) as response:
        scopes = response.headers.get('X-OAuth-Scopes', '(none)')
        r = response
        data = json.loads(r.read().decode('utf-8'))
        login = data.get('login')
    print('[secrets] GitHub token OK: user={}; scopes={}'.format(login, scopes))
except Exception as e:
    print('[secrets][WARN] GitHub token verification failed: {}'.format(e))
PY"
else
  warn "GitHub token check skipped (missing token or CODEX_SKIP_GH_CHECK=1)."
fi

# ----------------------------
# Lock awareness
# ----------------------------
section "Checking dependency lock status"
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

SETUP_LOCKSUM_FILE=".codex/cache/setup.locksum"
LAST_MAINT_FILE=".codex/cache/last_maint.locksum"
CURR_HASH="$(calc_lockhash)"
SETUP_HASH="$(cat "$SETUP_LOCKSUM_FILE" 2>/dev/null || echo none)"
LAST_MAINT_HASH="$(cat "$LAST_MAINT_FILE" 2>/dev/null || echo none)"

NEED_SYNC=0
if [[ "$CURR_HASH" != "$SETUP_HASH" ]]; then
  log "Lockfiles differ from setup snapshot: setup=$SETUP_HASH current=$CURR_HASH"
  NEED_SYNC=1
elif [[ "$CURR_HASH" != "$LAST_MAINT_HASH" ]]; then
  log "Lockfiles changed since last maintenance: last=$LAST_MAINT_HASH current=$CURR_HASH"
  NEED_SYNC=1
else
  log "Lockfiles unchanged; skipping dependency sync."
fi

# ----------------------------
# Python environment activation
# ----------------------------
section "Activating Python environment"
cd "$REPO_ROOT"

if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate || maybe_fail "Failed to activate .venv"
else
  warn ".venv not found — creating quick venv"
  run "python3 -m venv .venv"
  # shellcheck disable=SC1091
  source .venv/bin/activate || maybe_fail "Failed to activate new .venv"
  NEED_SYNC=1
fi

# Set UV_PYTHON to target the active venv
command -v python >/dev/null && export UV_PYTHON="$(command -v python)"

# ----------------------------
# Environment integrity check
# ----------------------------
section "Checking environment integrity"
run "python - <<'PY'
import sys, os
print('[maint] Python:', sys.version.split()[0])
print('[maint] Virtual env:', os.getenv('VIRTUAL_ENV', 'none'))
print('[maint] UV_PYTHON:', os.getenv('UV_PYTHON', 'none'))
try:
    import pip
    print('[maint] pip available:', pip.__version__)
except ImportError:
    print('[maint] pip not available in venv')
PY"

# ----------------------------
# Enhanced dependency sync with torch preservation
# ----------------------------
if (( NEED_SYNC )); then
  section "Syncing Python dependencies"
  log "Syncing Python deps according to CODEX_SYNC_GROUPS=[$CODEX_SYNC_GROUPS]..."
  
  # Check if torch is currently installed
  TORCH_INSTALLED=0
  if python -c "import torch; print(torch.__version__)" >/dev/null 2>&1; then
    TORCH_INSTALLED=1
    TORCH_VERSION=$(python -c "import torch; print(torch.__version__)" 2>/dev/null || echo "unknown")
    log "Found existing torch: $TORCH_VERSION"
  fi
  
  # GPU lock scrubbing
  _scrub_gpu_lock_if_needed() {
    local want_gpu=0
    local old_ifs="$IFS"
    IFS=',' read -ra _tok <<<"${CODEX_SYNC_GROUPS}"
    IFS="$old_ifs"
    local t
    for t in "${_tok[@]}"; do
      [[ "${t}" == "gpu" || "${t}" == "all" || "${t}" == "extras" ]] && want_gpu=1
    done
    if [[ -f "uv.lock" && ${want_gpu} -eq 0 ]]; then
      if grep -Eq '(^|\")nvidia-(cublas|cuda|cudnn|cufft|curand|cusolver|cusparse|cusparselt|nccl|nvjitlink)|(^|\")pytorch-cuda|(^|\")triton' uv.lock; then
        log "Detected GPU pins in uv.lock while CODEX_SYNC_GROUPS=[$CODEX_SYNC_GROUPS] excludes gpu; rebuilding lock..."
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
  
  _scrub_gpu_lock_if_needed
  
  # Base dependency sync - use full sync to keep torch
  if command -v uv >/dev/null 2>&1 && [[ -f "pyproject.toml" ]]; then
    run "uv sync"  # Keep all dependencies, including torch
  else
    run "python -m ensurepip -U || true"
    run "python -m pip install -U pip wheel"
    [[ -f "requirements.txt" ]] && run "pip install -r requirements.txt"
    [[ -f "docs/requirements.txt" ]] && run "pip install -r docs/requirements.txt"
    [[ -f "services/api/requirements.txt" ]] && run "pip install -r services/api/requirements.txt"
    if [[ -f "pyproject.toml" ]] && grep -q 'project' pyproject.toml 2>/dev/null; then
      run "pip install -e ."
    fi
  fi
  
  # Ensure CPU-only torch is installed regardless
  IFS=',' read -ra TOKENS <<<"$CODEX_SYNC_GROUPS"
  for t in "${TOKENS[@]}"; do
    if [[ "$t" == "cpu" ]]; then
      log "Installing/ensuring CPU-only torch..."
      run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu --no-deps --force-reinstall 'torch==2.8.0+cpu'"
      break
    fi
  done
  
  # Restore pre-commit if it exists in config
  if [[ -f ".pre-commit-config.yaml" ]]; then
    if ! command -v pre-commit >/dev/null 2>&1; then
      log "Restoring pre-commit after sync..."
      run "uv pip install --python \"$UV_PYTHON\" pre-commit"
    fi
  fi
else
  log "Python deps up-to-date."
fi

# ----------------------------
# Node workspace (install only on lock change)
# ----------------------------
section "Checking Node dependencies"
if [[ -f "package.json" ]]; then
  node_lockhash() {
    ( sha256sum package-lock.json 2>/dev/null || true
      sha256sum yarn.lock         2>/dev/null || true
      sha256sum pnpm-lock.yaml    2>/dev/null || true
    ) | sha256sum | awk '{print $1}'
  }
  
  CURR_NODE_HASH="$(node_lockhash)"
  LAST_NODE_FILE=".codex/cache/last_node.locksum"
  LAST_NODE_HASH="$(cat "$LAST_NODE_FILE" 2>/dev/null || echo none)"
  
  if [[ "$CURR_NODE_HASH" != "$LAST_NODE_HASH" ]]; then
    if command -v pnpm >/dev/null 2>&1 && [[ -f "pnpm-lock.yaml" ]]; then
      log "Installing Node deps via pnpm..."
      run "pnpm install --frozen-lockfile"
    elif command -v yarn >/dev/null 2>&1 && [[ -f "yarn.lock" ]]; then
      log "Installing Node deps via yarn..."
      run "yarn install --frozen-lockfile"
    else
      log "Installing Node deps via npm..."
      run "npm ci || npm install"
    fi
    echo "$CURR_NODE_HASH" > "$LAST_NODE_FILE"
  else
    log "Node deps up-to-date."
  fi
fi

# ----------------------------
# Git LFS sanity (warn-only)
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
# Budget calculations
# ----------------------------
section "Updating budget calculations"
OPENAI_RPM=${OPENAI_RPM:-6}
OPENAI_TPM=${OPENAI_TPM:-120000}
TOKENS_PER_MIN=$(( OPENAI_TPM / (OPENAI_RPM>0?OPENAI_RPM:1) ))

run "python - <<'PY'
import json, os, datetime as dt
rpm = int(os.getenv('OPENAI_RPM','6'))
tpm = int(os.getenv('OPENAI_TPM','120000'))
tok_per_call = tpm // (rpm if rpm > 0 else 1)
conc = int(os.getenv('CODEX_SAFE_CONCURRENCY','1'))
gh_conc = int(os.getenv('CODEX_MAX_CONCURRENCY','80'))
gh_rest = int(os.getenv('CODEX_REST_POINTS_PER_MIN','900'))
cs_rpm = int(os.getenv('CODEX_CODE_SEARCH_RPM','8'))
shard_days = int(os.getenv('CODEX_SEARCH_SHARD_DAYS','7'))
today = dt.date.today()
windows=[]
for i in range(8):
    end=today-dt.timedelta(days=i*shard_days)
    start=end-dt.timedelta(days=shard_days-1)
    windows.append(f'created:{start}..{end}')
json.dump({
  'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
  'openai': {'rpm': rpm, 'tpm': tpm, 'safe_tokens_per_call': tok_per_call, 'safe_concurrency': conc},
  'github': {'max_concurrency': gh_conc, 'rest_points_per_min': gh_rest, 'code_search_rpm': cs_rpm, 'search_shard_days': shard_days, 'search_windows': windows}
}, open('.codex/cache/run_budget.json','w'), indent=2)
print('[maint] wrote .codex/cache/run_budget.json')
PY"
log "Budget file: .codex/cache/run_budget.json"

# ----------------------------
# Optional features
# ----------------------------
if [[ "$ENV_SNAPSHOT" = "1" ]]; then
  section "Capturing environment snapshot"
  mkdir -p artifacts/env || true
  python --version > artifacts/env/python_version.txt || true
  pip freeze > artifacts/env/pip_freeze.txt || true
  uname -a > artifacts/env/uname.txt || true
  env | sort > artifacts/env/env_vars.txt || true
  log "Environment snapshot saved to artifacts/env/"
fi

if [[ "$TYPECHECK" = "1" ]] && command -v mypy >/dev/null 2>&1; then
  section "Running type checks"
  run "mypy src --ignore-missing-imports || true"
fi

if [[ "$SMOKE" = "1" ]]; then
  section "Running smoke checks"
  run "python - <<'PY'
try:
  import sys; print('python', sys.version.split()[0])
  import importlib.util, pathlib
  for p in ('src','services/api'):
    pp = pathlib.Path(p)
    if pp.exists():
      print('[smoke] found', p)
  print('[smoke] OK')
except Exception as e:
  print('[smoke][WARN]', e)
PY"
  
  # Enhanced torch verification with better error handling
  run "python - <<'PY'
import sys
try:
    import torch
    print('[smoke] torch:', torch.__version__, 'cuda available?:', torch.cuda.is_available())
    if hasattr(torch.version, 'cuda') and torch.version.cuda:
        print('[smoke][WARN] CUDA build of torch detected - should be CPU-only')
    else:
        print('[smoke] torch CPU build confirmed')
except ImportError:
    print('[smoke][WARN] torch not available in this environment')
except Exception as e:
    print('[smoke][WARN] torch check failed:', e)
PY"

  command -v ruff >/dev/null 2>&1 && run "ruff --version && ruff --select=E9,F63,F7,F82 --exit-zero ."
fi

# ----------------------------
# Final torch verification and repair
# ----------------------------
section "Verifying torch remains CPU-only"
run "python - <<'PY'
import sys
try:
    import torch
    print('[maint] torch:', torch.__version__, 'cuda available?:', torch.cuda.is_available())
    if hasattr(torch.version, 'cuda') and torch.version.cuda:
        print('WARN: CUDA build of torch detected - may need re-pinning to CPU')
    else:
        print('[maint] torch CPU build confirmed')
except ImportError:
    print('[maint] torch not available - ensuring CPU version is installed...')
    import subprocess, os
    try:
        uv_python = os.getenv('UV_PYTHON', 'python')
        subprocess.run([
            'uv', 'pip', 'install', '--python', uv_python,
            '--index-url', 'https://download.pytorch.org/whl/cpu',
            '--no-deps', '--force-reinstall', 'torch==2.8.0+cpu'
        ], check=True)
        print('[maint] torch CPU version installed successfully')
    except Exception as install_err:
        print('[maint][WARN] torch installation failed:', install_err)
except Exception as e:
    print('[maint][WARN] torch check failed:', e)
PY"

# ----------------------------
# Stamp maintenance completion
# ----------------------------
echo "$CURR_HASH" > "$LAST_MAINT_FILE"

section "Maintenance complete"
if [[ -s "$WARN_FILE" ]]; then
  log "Maintenance finished with warnings. See $WARN_FILE"
  log "Warning count: $(wc -l < "$WARN_FILE")"
else
  log "Maintenance finished clean."
fi
