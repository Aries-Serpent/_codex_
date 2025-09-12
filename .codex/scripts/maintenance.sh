#!/usr/bin/env bash
# .codex/scripts/maintenance.sh
# Runs on every task after a cached container resume. Network is guaranteed ON.

set -Eeuo pipefail

# ----------------------------
# Graceful controls (safe defaults)
# ----------------------------
GRACEFUL="${CODEX_GRACEFUL:-1}"         # 1=continue on non-critical errors, 0=die
STRICT_SETUP="${CODEX_STRICT_SETUP:-0}" # 1=fail on any maintenance step failure
SMOKE="${CODEX_SMOKE:-0}"               # 1=run quick smoke checks
# Match setup: default to CPU-only groups to avoid CUDA pulls.
CODEX_SYNC_GROUPS="${CODEX_SYNC_GROUPS:-base,cpu}"

# ----------------------------
# Helpers & logs
# ----------------------------
mkdir -p .codex/logs .codex/cache
WARN_FILE=".codex/logs/maintenance_warnings.log"
: > "$WARN_FILE"

log()  { printf "[maint] %s %s\n" "$(date -Iseconds)" "$*"; }
warn() { log "WARN: $*"; printf "%s\n" "$*" >> "$WARN_FILE"; }
die()  { printf "[maint][ERROR] %s\n" "$*" >&2; exit 1; }

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
  local s="$1"
  case "$s" in
    \"*\"|\'*\') printf %s "${s:1:${#s}-2}";;
    *)           printf %s "$s";;
  esac
}

# ----------------------------
# Context
# ----------------------------
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

# Live token check (safe)
if [[ -n "${GITHUB_TOKEN:-${GH_TOKEN:-}}" && "${CODEX_SKIP_GH_CHECK:-0}" != "1" ]]; then
  run "python - <<'PY'
import os, json, urllib.request, ssl
token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
if not token:
    print('[secrets][WARN] No GitHub token present'); raise SystemExit(0)
try:
    ctx = ssl.create_default_context()
    req = urllib.request.Request('https://api.github.com/user', headers={
        'Authorization': 'token ' + token,
        'User-Agent': 'codex-env-check'
    })
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        scopes = r.headers.get('X-OAuth-Scopes','')
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
# Lock awareness (unified with setup)
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
# Python env activation (create if missing)
# ----------------------------
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

# ----------------------------
# Selective dependency sync helpers (same as setup)
# ----------------------------
_uv_sync_base_only() {
  if command -v uv >/dev/null 2>&1 && [[ -f "pyproject.toml" ]]; then
    run "uv sync --no-dev"
  else
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

_uv_sync_selective() {
  local IFS=,
  read -ra TOKENS <<< "${CODEX_SYNC_GROUPS:-base,cpu}"

  local did_dev=0
  local want_all_groups=0
  local want_all_extras=0
  local extras_flags=()
  local group_flags=()
  local want_cpu_torch=0
  local want_gpu=0

  for t in "${TOKENS[@]}"; do
    case "$t" in
      all)        want_all_groups=1 ;;
      +extras)    want_all_extras=1 ;;
      dev)        did_dev=1 ;;
      cpu)        want_cpu_torch=1 ;;
      gpu)        want_gpu=1 ;;
      base)       : ;;
      *)          group_flags+=("--group" "$t") ;;
    esac
  done

  (( want_all_extras )) && extras_flags+=(--all-extras)
  (( want_all_groups )) && group_flags=("--all-groups")

  if command -v uv >/dev/null 2>&1 && [[ -f "pyproject.toml" ]]; then
    if (( did_dev )) || (( ${#group_flags[@]} )); then
      run "uv sync ${group_flags[*]:-} ${extras_flags[*]:-}"
    fi
  fi

  if (( want_cpu_torch )); then
    run "uv pip install --index-url https://download.pytorch.org/whl/cpu torch"
  fi

  if (( want_gpu )); then
    warn "GPU group requested but Codex has no GPU; skipping CUDA installs."
  fi
}

# ----------------------------
# Dependency sync (only when needed)
# ----------------------------
if (( NEED_SYNC )); then
  log "Syncing Python deps according to CODEX_SYNC_GROUPS=[${CODEX_SYNC_GROUPS}]..."
  _uv_sync_base_only
  _uv_sync_selective
else
  log "Python deps up-to-date."
fi

# ----------------------------
# Node workspace (install only on lock change)
# ----------------------------
node_lockhash() {
  ( sha256sum package-lock.json 2>/dev/null || true
    sha256sum yarn.lock         2>/dev/null || true
    sha256sum pnpm-lock.yaml    2>/dev/null || true
  ) | sha256sum | awk '{print $1}'
}

if [[ -f "package.json" ]]; then
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
# Budget hints
# ----------------------------
OPENAI_RPM=${OPENAI_RPM:-6}
OPENAI_TPM=${OPENAI_TPM:-120000}
TOKENS_PER_MIN=$(( OPENAI_TPM / (OPENAI_RPM>0?OPENAI_RPM:1) ))
SAFE_TOKENS_PER_CALL=$(( TOKENS_PER_MIN < 8000 ? TOKENS_PER_MIN : 8000 ))
SAFE_CONCURRENCY=$(( OPENAI_RPM>1 ? OPENAI_RPM-1 : 1 ))

export CODEX_SAFE_TOKENS_PER_CALL="${SAFE_TOKENS_PER_CALL}"
export CODEX_SAFE_CONCURRENCY="${SAFE_CONCURRENCY}"
export CODEX_MAX_CONCURRENCY=${CODEX_MAX_CONCURRENCY:-80}
export CODEX_REST_POINTS_PER_MIN=${CODEX_REST_POINTS_PER_MIN:-900}
export CODEX_CODE_SEARCH_RPM=${CODEX_CODE_SEARCH_RPM:-8}
export CODEX_SEARCH_SHARD_DAYS=${CODEX_SEARCH_SHARD_DAYS:-7}

run "python - <<'PY'
import os, json, datetime as dt, pathlib
pathlib.Path('.codex/cache').mkdir(parents=True, exist_ok=True)
rpm = int(os.getenv('OPENAI_RPM','6'))
tpm = int(os.getenv('OPENAI_TPM','120000'))
tok_per_call = int(os.getenv('CODEX_SAFE_TOKENS_PER_CALL','4000'))
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
# Optional quick smoke tests
# ----------------------------
if [[ "$SMOKE" = "1" ]]; then
  log "Running smoke checks..."
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
  command -v ruff >/dev/null 2>&1 && run "ruff --version && ruff --select=E9,F63,F7,F82 --exit-zero ."
fi

# ----------------------------
# Stamp last maintenance hash
# ----------------------------
echo "$CURR_HASH" > "$LAST_MAINT_FILE"

# ----------------------------
# Finish
# ----------------------------
if [[ -s "$WARN_FILE" ]]; then
  log "Maintenance finished with warnings. See $WARN_FILE"
else
  log "Maintenance finished clean."
fi
