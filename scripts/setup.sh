#!/usr/bin/env bash
# Setup Bootstrap Rev5.3++ (Refactored Final – Patch 3: Warning-Free Flow)
#
# Patch 3 (2025-09-17):
#  - GOAL: Produce a "clean" run (zero warnings in normal, recoverable scenarios).
#  - FIX: Removed warning generation for expected / auto-recoverable flows
#         (lock regeneration, vendor fallback purge, CPU relock).
#  - FIX: Skip duplicate vendor purge if fallback already removed GPU wheels.
#  - FIX: More robust locked-sync gate; only attempt --locked when lock validates.
#  - FIX: Accurate vendor uninstall counting (counts individual packages).
#  - FIX: Residual vendor detection now ONLY warns if residue remains post-remediation.
#  - FIX: All remediation events downgraded to INFO (not warnings).
#  - IMP: Introduced EVENT_LEVEL env toggles (CODEX_WARN_ON_FALLBACK / CODEX_WARN_ON_LOCK_REGEN).
#  - IMP: Added safe_lock_sync() wrapper eliminating fail-soft warning on first retry path.
#  - IMP: Added metrics for remediation paths (relock_events, fallback_events).
#  - IMP: Torch verification only warns when unrecoverable anomaly persists.
#
# Default Behavior:
#  - If a lock mismatch occurs, lock is regenerated silently (info only).
#  - If GPU wheels are pulled inadvertently, they are purged + torch reinstalled (info only).
#  - Vendor purge step skipped when fallback already handled those wheels.
#
# To re-enable legacy warnings:
#  - export CODEX_WARN_ON_FALLBACK=1
#  - export CODEX_WARN_ON_LOCK_REGEN=1
#
# Environment Summary Additions (JSON):
#   remediation: { relock_events, fallback_events, vendor_purge_events }
#
set -Eeuo pipefail

############################################
# 0) Flags / Environment Controls
############################################
export GRACEFUL="${CODEX_GRACEFUL:-1}"
export STRICT_SETUP="${CODEX_STRRICT_SETUP:-${CODEX_STRICT_SETUP:-0}}"
export CODEX_DEBUG="${CODEX_DEBUG:-0}"
export CODEX_OFFLINE="${CODEX_OFFLINE:-0}"

export CODEX_SYNC_GROUPS="${CODEX_SYNC_GROUPS:-base,cpu}"
export CODEX_SYNC_EXTRAS="${CODEX_SYNC_EXTRAS:-}"
export CODEX_TORCH_VERSION_RAW="${CODEX_TORCH_VERSION:-2.8.0+cpu}"
export CODEX_TORCH_VERSION_BASE="${CODEX_TORCH_VERSION_RAW%%+*}"

export CODEX_ENSURE_PRECOMMIT="${CODEX_ENSURE_PRECOMMIT:-1}"
export CODEX_FAIL_ON_GPU_RESIDUE="${CODEX_FAIL_ON_GPU_RESIDUE:-0}"
export CODEX_LIGHTWEIGHT_CPU_FALLBACK="${CODEX_LIGHTWEIGHT_CPU_FALLBACK:-1}"
export CODEX_ABORT_ON_GPU_PULL="${CODEX_ABORT_ON_GPU_PULL:-0}"
export CODEX_SKIP_UV_SYNC="${CODEX_SKIP_UV_SYNC:-0}"
export CODEX_CPU_MINIMAL="${CODEX_CPU_MINIMAL:-0}"
export CODEX_VENDOR_PURGE="${CODEX_VENDOR_PURGE:-1}"
export CODEX_USE_LOCKED_SYNC="${CODEX_USE_LOCKED_SYNC:-1}"
export CODEX_VENDOR_LIST_STRICT="${CODEX_VENDOR_LIST_STRICT:-1}"
export CODEX_CACHE_PRUNE="${CODEX_CACHE_PRUNE:-1}"
export CODEX_HASH_LOCK_STRICT="${CODEX_HASH_LOCK_STRICT:-0}"
export CODEX_SUMMARY_INCLUDE_HASH="${CODEX_SUMMARY_INCLUDE_HASH:-1}"
export CODEX_LOCKED_SYNC_FALLBACK="${CODEX_LOCKED_SYNC_FALLBACK:-1}"
export CODEX_VENDOR_LOG_ONLY_POLICY="${CODEX_VENDOR_LOG_ONLY_POLICY:-purge}"
export CODEX_VENDOR_NAMESPACE_IGNORE="${CODEX_VENDOR_NAMESPACE_IGNORE:-1}"
export CODEX_ERR_TRAP="${CODEX_ERR_TRAP:-1}"
export CODEX_RELOCK_AFTER_VENDOR_PURGE="${CODEX_RELOCK_AFTER_VENDOR_PURGE:-1}"
export CODEX_CPU_CONSTRAIN_LOCK="${CODEX_CPU_CONSTRAIN_LOCK:-1}"
export CODEX_WARN_AGGREGATE="${CODEX_WARN_AGGREGATE:-1}"
export CODEX_METRICS_TIMINGS="${CODEX_METRICS_TIMINGS:-1}"

# New toggle flags controlling warning escalation for recoverable flows
export CODEX_WARN_ON_FALLBACK="${CODEX_WARN_ON_FALLBACK:-0}"
export CODEX_WARN_ON_LOCK_REGEN="${CODEX_WARN_ON_LOCK_REGEN:-0}"

if [[ -z "${CODEX_FORCE_CPU:-}" ]]; then
  CODEX_FORCE_CPU=1
fi

if [[ "$CODEX_DEBUG" == "1" ]]; then
  set -x
fi

# Normalise CODEX_SYNC_GROUPS / CODEX_SYNC_EXTRAS for downstream commands
DEFAULT_SYNC_GROUPS="base,cpu"
declare -a SYNC_GROUPS=()
declare -A SEEN_GROUP=()
IFS=',' read -ra RAW_GROUPS <<<"${CODEX_SYNC_GROUPS:-$DEFAULT_SYNC_GROUPS}"
for entry in "${RAW_GROUPS[@]}"; do
  trimmed="${entry//[[:space:]]/}"
  if [[ -n "$trimmed" && -z "${SEEN_GROUP[$trimmed]:-}" ]]; then
    SEEN_GROUP["$trimmed"]=1
    SYNC_GROUPS+=("$trimmed")
  fi
done
if ((${#SYNC_GROUPS[@]} == 0)); then
  SYNC_GROUPS=("base")
fi
if [[ "${CODEX_FORCE_CPU}" == "1" ]]; then
  for group in "${SYNC_GROUPS[@]}"; do
    if [[ "$group" == "gpu" ]]; then
      CODEX_FORCE_CPU=0
      break
    fi
  done
fi

# Extras (comma-separated)
declare -a SYNC_EXTRAS=()
declare -A SEEN_EXTRA=()
if [[ -n "$CODEX_SYNC_EXTRAS" ]]; then
  IFS=',' read -ra RAW_EXTRAS <<<"$CODEX_SYNC_EXTRAS"
  for entry in "${RAW_EXTRAS[@]}"; do
    trimmed="${entry//[[:space:]]/}"
    if [[ -n "$trimmed" && -z "${SEEN_EXTRA[$trimmed]:-}" ]]; then
      SEEN_EXTRA["$trimmed"]=1
      SYNC_EXTRAS+=("$trimmed")
    fi
  done
fi

# Rewrite env variables with normalised ordering
if ((${#SYNC_GROUPS[@]} > 0)); then
  CODEX_SYNC_GROUPS="$(IFS=','; printf '%s' "${SYNC_GROUPS[*]}")"
else
  CODEX_SYNC_GROUPS=""
fi
export CODEX_SYNC_GROUPS
if ((${#SYNC_EXTRAS[@]} > 0)); then
  CODEX_SYNC_EXTRAS="$(IFS=','; printf '%s' "${SYNC_EXTRAS[*]}")"
else
  CODEX_SYNC_EXTRAS=""
fi
export CODEX_SYNC_EXTRAS
export CODEX_FORCE_CPU

############################################
# 1) Logging & Event System
############################################
mkdir -p .codex/logs .codex/cache artifacts data
WARN_FILE=".codex/logs/setup_warnings.log"
FAIL_FILE=".codex/logs/command_failures.log"
SYNC_LOG=".codex/cache/uv_sync.log"
SUMMARY_JSON=".codex/cache/setup_summary.json"
: >"$WARN_FILE"; : >"$FAIL_FILE"; : >"$SYNC_LOG"

log()       { printf "[setup] %s %s\n" "$(date -Iseconds)" "$*"; }
log_info()  { log "INFO: $*"; }
_raw_warn() { log "WARN: $*"; printf '%s\n' "$*" >>"$WARN_FILE"; }
die()       { printf "[setup][ERROR] %s\n" "$*" >&2; exit 1; }

WARN_EVENTS=()
WARN_EVENT_CATS=()
declare -A WARN_CAT_COUNT=()

record_warn(){
  local cat="$1"; shift
  local msg="$*"
  WARN_EVENTS+=("$msg")
  WARN_EVENT_CATS+=("$cat")
  WARN_CAT_COUNT["$cat"]=$(( ${WARN_CAT_COUNT["$cat"]:-0} + 1 ))
  if [[ "$CODEX_WARN_AGGREGATE" == "0" ]]; then
    _raw_warn "[$cat] $msg"
  else
    _raw_warn "$msg"
  fi
}

maybe_fail(){
  local m="$1"
  if [[ "$GRACEFUL" == "1" && "$STRICT_SETUP" == "0" ]]; then
    record_warn "fail-soft" "$m — continuing"
  else
    die "$m"
  fi
}

if [[ "$CODEX_ERR_TRAP" == "1" ]]; then
  set -E
  trap 'ec=$?; [[ $ec -ne 0 ]] && log "ERR line=$LINENO ec=$ec cmd=${BASH_COMMAND}"' ERR
fi

_cmd_index=0
run(){
  local cmd="$*"; _cmd_index=$((_cmd_index+1))
  local start=$(date +%s)
  set +e; bash -lc "$cmd" > >(tee /tmp/codex_cmd_out.$$) 2>&1; local ec=$?; set -e
  local dur=$(( $(date +%s) - start ))
  if (( ec != 0 )); then
    printf "idx=%s ec=%s dur=%s cmd=%q\n" "$_cmd_index" "$ec" "$dur" "$cmd" >>"$FAIL_FILE"
    maybe_fail "Command failed (exit $ec): $cmd"
  else
    log "OK(t=${dur}s) $cmd"
  fi
  return $ec
}

run_retry_log(){
  local max="${1:-3}"; shift
  local cmd="$*"
  local attempt=1 ec=0
  while true; do
    set +e
    ( set +e; bash -lc "$cmd" ) > /tmp/codex_retry_out.$$ 2>&1
    ec=$?
    set -e
    cat /tmp/codex_retry_out.$$ >>"$SYNC_LOG"
    if (( ec == 0 )); then
      log "OK(retry t=$attempt) $cmd"
      return 0
    fi
    if (( attempt >= max )); then
      return $ec
    fi
    sleep $(( attempt * 2 ))
    attempt=$(( attempt + 1 ))
  done
}

join_args(){
  local out=()
  for arg in "$@"; do
    out+=("$(printf '%q' "$arg")")
  done
  local IFS=' '
  printf '%s' "${out[*]}"
}

############################################
# 2) Timings
############################################
_ts(){ [[ "$CODEX_METRICS_TIMINGS" == "1" ]] || return 0; date +%s; }
PHASE_START_TOTAL=$(_ts || echo 0)
PHASE_PREINSTALL=0
PHASE_LOCK=0
PHASE_PURGE=0
PHASE_TOTAL=0

PHASE_MARK(){
  [[ "$CODEX_METRICS_TIMINGS" == "1" ]] || return 0
  local var="$1" start="$2" end
  end=$(_ts)
  printf -v "$var" "%s" "$(( end - start ))"
  export "$var"
}

finalize_timings(){
  if [[ "$CODEX_METRICS_TIMINGS" == "1" ]]; then
    local end=$(_ts)
    PHASE_TOTAL=$(( end - PHASE_START_TOTAL ))
  else
    PHASE_TOTAL=0
  fi
  export PHASE_TOTAL
}

export_phase_vars(){
  export PHASE_PREINSTALL PHASE_LOCK PHASE_PURGE PHASE_TOTAL
}

############################################
# 3) Context
############################################
export DEBIAN_FRONTEND=noninteractive
REPO_ROOT="${REPO_ROOT:-$(pwd)}"
HF_HOME_DEFAULT="$REPO_ROOT/.hf_cache"
export HF_HOME="${HF_HOME:-$HF_HOME_DEFAULT}"
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PYTHONUTF8=1
export UV_SYSTEM_PYTHON=0
export UV_LINK_MODE=copy

log "Repo: $REPO_ROOT"
log "Torch(BaseSpec)=${CODEX_TORCH_VERSION_BASE} Raw=${CODEX_TORCH_VERSION_RAW}"
log "Mode: FORCE_CPU=${CODEX_FORCE_CPU} SKIP_UV_SYNC=${CODEX_SKIP_UV_SYNC} LOCKED=${CODEX_USE_LOCKED_SYNC} CPU_MINIMAL=${CODEX_CPU_MINIMAL}"
log "Fallback: LW=${CODEX_LIGHTWEIGHT_CPU_FALLBACK} ABORT_ON_GPU_PULL=${CODEX_ABORT_ON_GPU_PULL} PURGE=${CODEX_VENDOR_PURGE}"
log "Sync groups: ${CODEX_SYNC_GROUPS:-<none>}"
log "Sync extras: ${CODEX_SYNC_EXTRAS:-<none>}"

############################################
# 4) Vendor Helper (import success filter)
############################################
VENDOR_HELPER_PY='
import os, pkgutil, re, sys, pathlib, subprocess, importlib
MODE=sys.argv[1]
ignore_root=os.getenv("CODEX_VENDOR_NAMESPACE_IGNORE","1")=="1"
strict=os.getenv("CODEX_VENDOR_LIST_STRICT","1")=="1"
sync_log=pathlib.Path(".codex/cache/uv_sync.log")
first_sync_done=os.getenv("FIRST_SYNC_DONE","0")=="1"
fallback_set={
 "triton","torchtriton","nvidia-cublas-cu12","nvidia-cuda-cupti-cu12",
 "nvidia-cuda-nvrtc-cu12","nvidia-cuda-runtime-cu12","nvidia-cudnn-cu12",
 "nvidia-cufft-cu12","nvidia-cufile-cu12","nvidia-curand-cu12",
 "nvidia-cusolver-cu12","nvidia-cusparse-cu12","nvidia-cusparselt-cu12",
 "nvidia-nccl-cu12","nvidia-nvjitlink-cu12","nvidia-nvtx-cu12"
}
def uv_list():
    try:
        out=subprocess.check_output(["uv","pip","list","--format","json","--python",os.getenv("UV_PYTHON","python")], text=True)
        import json
        return {(p.get("name") or "").lower() for p in json.loads(out) if isinstance(p,dict)}
    except Exception:
        return set()
def logs():
    if not sync_log.exists(): return set()
    pat=re.compile(r"(nvidia-[a-z0-9\-]+|triton|torchtriton)")
    return {m.group(1).lower() for m in pat.finditer(sync_log.read_text())}
def import_modules():
    present=set()
    for m in pkgutil.iter_modules():
        n=m.name
        if n.startswith("nvidia") or n in {"triton","torchtriton"}:
            try:
                importlib.import_module(n)
            except Exception:
                continue
            present.add(n.lower())
    return present
d=uv_list(); lg=logs(); im=import_modules()
if MODE=="collect":
    combined=set()
    combined |= {p for p in d if p.startswith("nvidia-") or p in {"triton","torchtriton"}}
    combined |= im
    combined |= lg
    if not first_sync_done and not combined and strict and lg:
        combined |= fallback_set
    if ignore_root:
        combined={c for c in combined if c!="nvidia"}
    valid={c for c in combined if c in {"triton","torchtriton"} or c.startswith("nvidia-")}
    print(" ".join(sorted(valid)))
elif MODE=="residue":
    residue=set()
    residue |= {p for p in d if p.startswith("nvidia-") or p in {"triton","torchtriton"}}
    residue |= im
    if ignore_root:
        residue={r for r in residue if r!="nvidia"}
    print(" ".join(sorted(residue)))
else:
    print("")
'
vendor_collect(){ VENDOR_PHASE="${1:-normal}" python -c "$VENDOR_HELPER_PY" collect; }
vendor_residue(){ python -c "$VENDOR_HELPER_PY" residue; }

uv_uninstall_noninteractive(){
  [[ $# -eq 0 ]] && return 0
  if command -v uv >/dev/null 2>&1; then
    if command -v yes >/dev/null 2>&1; then yes | uv pip uninstall "$@" || true
    else printf 'y\n%.0s' {1..60} | uv pip uninstall "$@" || true
    fi
  else
    python -m pip uninstall -y "$@" || true
  fi
}

############################################
# 5) Token Advisory
############################################
resolve_github_token(){
  local names=(GH_PAT GITHUB_TOKEN GH_TOKEN _CODEX_ACTION_RUNNER _CODEX_BOT_RUNNER CODEX_ENVIRONMENT_RUNNER)
  unset GH_TOKEN
  for n in "${names[@]}"; do
    local v="${!n-}"
    if [[ -n "$v" ]]; then
      export GH_TOKEN="$v" GITHUB_TOKEN="${GITHUB_TOKEN:-$v}" CODEX_GH_TOKEN_SOURCE="$n"
      break
    fi
  done
  run "python - <<'PY'
import os,json,hashlib,pathlib
d=pathlib.Path('.codex/cache'); d.mkdir(parents=True, exist_ok=True)
names=['GH_PAT','GITHUB_TOKEN','GH_TOKEN','_CODEX_ACTION_RUNNER','_CODEX_BOT_RUNNER','CODEX_ENVIRONMENT_RUNNER','CODEX_RUNNER_TOKEN']
vals={k:os.getenv(k) for k in names}
present={k:(v not in (None,'')) for k,v in vals.items()}
group=[k for k in names if vals.get(k)]
digests={__import__('hashlib').sha256(vals[g].encode()).hexdigest() for g in group}
json.dump({'present':present,'unified':len(digests)<=1,'source':os.getenv('CODEX_GH_TOKEN_SOURCE')}, open('.codex/cache/secrets.status.json','w'))
print('[secrets] source:', os.getenv('CODEX_GH_TOKEN_SOURCE') or 'none','unified:',len(digests)<=1)
PY"
}
resolve_github_token

############################################
# 6) System Dependencies
############################################
if [[ "$CODEX_OFFLINE" != "1" ]] && command -v apt-get >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1; then
    run "sudo apt-get update -y"
    run "sudo apt-get install -y --no-install-recommends python3 python3-venv python3-pip python3-dev build-essential pkg-config git git-lfs curl ca-certificates libffi-dev libssl-dev"
  else
    run "apt-get update -y"
    run "apt-get install -y --no-install-recommends python3 python3-venv python3-pip python3-dev build-essential pkg-config git git-lfs curl ca-certificates libffi-dev libssl-dev"
  fi
  run "git lfs install --skip-repo"
fi

############################################
# 7) uv Ensure
############################################
if ! command -v uv >/dev/null 2>&1 && [[ "$CODEX_OFFLINE" != "1" ]]; then
  command -v curl >/dev/null 2>&1 && run "curl -fsSL https://astral.sh/uv/install.sh | bash || true"
  command -v uv >/dev/null 2>&1 || run "python3 -m pip install --user uv || true"
  export PATH="$HOME/.local/bin:$PATH"
fi
command -v uv >/dev/null 2>&1 && log "uv: $(uv --version || true)"

############################################
# 8) Virtual Env
############################################
if [[ ! -d .venv ]]; then
  if command -v uv >/dev/null 2>&1 && [[ -f pyproject.toml ]]; then
    run "uv venv --seed .venv || python3 -m venv .venv"
  else
    run "python3 -m venv .venv"
  fi
fi
# shellcheck disable=SC1091
source .venv/bin/activate || maybe_fail "Activate venv failed"
export UV_PYTHON
UV_PYTHON="$(command -v python)"

############################################
# 9) Sanitize pyproject (+cpu suffix)
############################################
if [[ -f pyproject.toml ]] && grep -qE 'torch==[0-9]+\.[0-9]+\.[0-9]+\+cpu' pyproject.toml; then
  cp pyproject.toml ".codex/cache/pyproject.toml.pre_sanitize.$(date +%s)" || true
  sed -E -i 's/(torch==[0-9]+\.[0-9]+\.[0-9]+)\+cpu/\1/g' pyproject.toml
  rm -f uv.lock
  log_info "Sanitized '+cpu' suffix from pyproject torch spec."
fi

############################################
# 10) Torch Preinstall
############################################
PH_PREINSTALL_START=$(_ts || echo 0)
SAVED_PIP_INDEX_URL=""
SAVED_PIP_EXTRA_INDEX_URL=""
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  export PIP_INDEX_URL="https://download.pytorch.org/whl/cpu"
  export PIP_EXTRA_INDEX_URL="https://pypi.org/simple"
  run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu \"torch==${CODEX_TORCH_VERSION_BASE}\""
  SAVED_PIP_INDEX_URL="$PIP_INDEX_URL"
  SAVED_PIP_EXTRA_INDEX_URL="$PIP_EXTRA_INDEX_URL"
fi
PHASE_MARK PHASE_PREINSTALL "$PH_PREINSTALL_START"

############################################
# 11) Lock & Sync (warning-free safe path)
############################################
UV_SYNC_ARGS=()
if [[ "$CODEX_OFFLINE" == "1" ]]; then
  UV_SYNC_ARGS+=(--offline)
fi
for group in "${SYNC_GROUPS[@]}"; do
  [[ -n "$group" ]] && UV_SYNC_ARGS+=(--group "$group")
done
for extra in "${SYNC_EXTRAS[@]}"; do
  [[ -n "$extra" ]] && UV_SYNC_ARGS+=(--extra "$extra")
done

uv_sync_command(){
  local mode="$1"
  shift || true
  local args=(uv sync)
  if [[ "$mode" == "locked" ]]; then
    args+=(--locked)
  fi
  args+=("${UV_SYNC_ARGS[@]}")
  join_args "${args[@]}"
}

cpu_constrained_lock(){
  if [[ "$CODEX_CPU_CONSTRAIN_LOCK" != "1" ]]; then
    run_retry_log 3 "$(join_args uv lock)" || return $?
    return 0
  fi
  local bak_idx="${PIP_INDEX_URL-}" bak_extra="${PIP_EXTRA_INDEX_URL-}"
  export PIP_INDEX_URL="https://download.pytorch.org/whl/cpu"; unset PIP_EXTRA_INDEX_URL || true
  run_retry_log 3 "$(join_args uv lock)" || return $?
  if [[ -n "$bak_idx" ]]; then
    export PIP_INDEX_URL="$bak_idx"
  else
    unset PIP_INDEX_URL || true
  fi
  if [[ -n "$bak_extra" ]]; then
    export PIP_EXTRA_INDEX_URL="$bak_extra"
  else
    unset PIP_EXTRA_INDEX_URL || true
  fi
  return 0
}

cpu_constrained_sync(){
  local locked_cmd="$(uv_sync_command locked)"
  local unlocked_cmd="$(uv_sync_command unlocked)"
  if [[ "$CODEX_CPU_CONSTRAIN_LOCK" != "1" ]]; then
    run_retry_log 3 "$locked_cmd || $unlocked_cmd" || return $?
    return 0
  fi
  local bak_idx="${PIP_INDEX_URL-}" bak_extra="${PIP_EXTRA_INDEX_URL-}"
  export PIP_INDEX_URL="https://download.pytorch.org/whl/cpu"; unset PIP_EXTRA_INDEX_URL || true
  run_retry_log 3 "$locked_cmd || $unlocked_cmd" || return $?
  if [[ -n "$bak_idx" ]]; then
    export PIP_INDEX_URL="$bak_idx"
  else
    unset PIP_INDEX_URL || true
  fi
  if [[ -n "$bak_extra" ]]; then
    export PIP_EXTRA_INDEX_URL="$bak_extra"
  else
    unset PIP_EXTRA_INDEX_URL || true
  fi
  return 0
}

validate_lock_torch(){
  [[ "$CODEX_HASH_LOCK_STRICT" != "1" ]] && [[ -f uv.lock ]] || return 0
  if grep -E '"name": "torch"' -A2 uv.lock 2>/dev/null | grep -q "+cpu"; then
    rm -f uv.lock
    return 1
  fi
  return 0
}

safe_lock_sync(){
  local relock_needed=0
  if [[ -f uv.lock ]]; then
    if ! validate_lock_torch; then
      relock_needed=1
    fi
  else
    relock_needed=1
  fi

  if (( relock_needed )); then
    if [[ "$CODEX_WARN_ON_LOCK_REGEN" == "1" ]]; then
      record_warn "lock" "Regenerating lock (auto)."
    else
      log_info "Regenerating lock (auto)."
    fi
    cpu_constrained_lock || maybe_fail "Lock generation failed"
  fi

  if [[ "$CODEX_USE_LOCKED_SYNC" == "1" && -f uv.lock && $relock_needed -eq 0 ]]; then
    local locked_cmd="$(uv_sync_command locked)"
    if ! run_retry_log 2 "$locked_cmd"; then
      log_info "Locked sync failed once; regenerating lock."
      cpu_constrained_lock || maybe_fail "Relock after failure failed"
      cpu_constrained_sync || maybe_fail "Sync after relock failed"
      return 0
    fi
  else
    cpu_constrained_sync || maybe_fail "Sync failed"
  fi
}

unset PIP_INDEX_URL PIP_EXTRA_INDEX_URL || true
FIRST_SYNC_DONE=0
export FIRST_SYNC_DONE
FALLBACK_VENDOR_PURGED=0
VENDOR_UNINSTALL_COUNT=0
RELOCK_EVENTS=0
FALLBACK_EVENTS=0
VENDOR_PURGE_EVENTS=0
export FALLBACK_VENDOR_PURGED VENDOR_UNINSTALL_COUNT RELOCK_EVENTS FALLBACK_EVENTS VENDOR_PURGE_EVENTS || true
PH_LOCK_START=$(_ts || echo 0)

if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_SKIP_UV_SYNC" == "1" ]]; then
  log_info "Skipping uv sync (CODEX_SKIP_UV_SYNC=1)"
else
  if [[ "$CODEX_OFFLINE" != "1" && -f pyproject.toml ]]; then
    if command -v uv >/dev/null 2>&1; then
      safe_lock_sync
      FIRST_SYNC_DONE=1; export FIRST_SYNC_DONE
      if [[ "$CODEX_FORCE_CPU" == "1" ]] && grep -E 'Downloading nvidia-|Downloading triton ' "$SYNC_LOG" >/dev/null 2>&1; then
        case "$CODEX_VENDOR_LOG_ONLY_POLICY" in
          ignore) log_info "Vendor wheels observed (ignored policy)";;
          warn)
            if [[ "$CODEX_WARN_ON_FALLBACK" == "1" ]]; then
              record_warn "vendor_detect" "Vendor wheels observed."
            else
              log_info "Vendor wheels observed."
            fi
            ;;
          purge)
            if [[ "$CODEX_ABORT_ON_GPU_PULL" == "1" ]]; then die "Aborting due to vendor wheels (abort mode)."; fi
            if [[ "$CODEX_LIGHTWEIGHT_CPU_FALLBACK" == "1" ]]; then
              local_vendors="$(vendor_collect normal)"
              if [[ -n "$local_vendors" ]]; then
                if [[ "$CODEX_WARN_ON_FALLBACK" == "1" ]]; then
                  record_warn "fallback" "Fallback purge: $local_vendors"
                else
                  log_info "Fallback purge: $local_vendors"
                fi
                before_count=$(echo "$local_vendors" | wc -w | awk '{print $1}')
                uv_uninstall_noninteractive $local_vendors
                VENDOR_UNINSTALL_COUNT=$(( VENDOR_UNINSTALL_COUNT + before_count ))
                FALLBACK_VENDOR_PURGED=1
                FALLBACK_EVENTS=$(( FALLBACK_EVENTS + 1 ))
                export VENDOR_UNINSTALL_COUNT FALLBACK_VENDOR_PURGED FALLBACK_EVENTS
                run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu --force-reinstall \"torch==${CODEX_TORCH_VERSION_BASE}\""
                export CODEX_CPU_MINIMAL=1
                if [[ "$CODEX_RELOCK_AFTER_VENDOR_PURGE" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
                  log_info "Relocking after fallback purge."
                  cpu_constrained_lock
                  cpu_constrained_sync
                  RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 ))
                  export RELOCK_EVENTS
                fi
              else
                log_info "Fallback triggered but vendor list empty."
              fi
            fi
            ;;
        esac
      fi
    fi
  fi
fi
PHASE_MARK PHASE_LOCK "$PH_LOCK_START"

if [[ -n "$SAVED_PIP_INDEX_URL" ]]; then
  export PIP_INDEX_URL="$SAVED_PIP_INDEX_URL"
else
  unset PIP_INDEX_URL || true
fi
if [[ -n "$SAVED_PIP_EXTRA_INDEX_URL" ]]; then
  export PIP_EXTRA_INDEX_URL="$SAVED_PIP_EXTRA_INDEX_URL"
else
  unset PIP_EXTRA_INDEX_URL || true
fi

############################################
# 12) Minimal augmentation
############################################
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_CPU_MINIMAL" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  run "uv pip install --python \"$UV_PYTHON\" --no-deps transformers tokenizers safetensors accelerate || true"
fi

############################################
# 13) Vendor Purge (skip if fallback already purged)
############################################
PH_PURGE_START=$(_ts || echo 0)
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_VENDOR_PURGE" == "1" && "$FALLBACK_VENDOR_PURGED" != "1" ]]; then
  VENDOR_LIST="$(vendor_collect normal)"
  printf "%s\n" "$VENDOR_LIST" > .codex/cache/vendor_seen.txt 2>/dev/null || true
  if [[ -n "$VENDOR_LIST" ]]; then
    log_info "Vendor purge (primary) removing: $VENDOR_LIST"
    uninstall_output=$(uv_uninstall_noninteractive $VENDOR_LIST 2>&1 || true)
    purged_count=$(echo "$uninstall_output" | awk '/^- /{c++} END{print c+0}')
    if (( purged_count > 0 )); then
      VENDOR_UNINSTALL_COUNT=$(( VENDOR_UNINSTALL_COUNT + purged_count ))
      VENDOR_PURGE_EVENTS=$(( VENDOR_PURGE_EVENTS + 1 ))
      export VENDOR_UNINSTALL_COUNT VENDOR_PURGE_EVENTS
    fi
    RESIDUE="$(vendor_residue)"
    if [[ -n "$RESIDUE" ]]; then
      record_warn "vendor_residue" "Residual vendor distributions: $RESIDUE"
      [[ "$CODEX_FAIL_ON_GPU_RESIDUE" == "1" ]] && echo "RESIDUAL_VENDOR=$RESIDUE" >>"$FAIL_FILE"
    else
      log_info "Vendor purge successful (no residue)."
    fi
  else
    log_info "No vendor distributions detected."
  fi
fi
PHASE_MARK PHASE_PURGE "$PH_PURGE_START"

############################################
# 14) Orphan Namespace Cleanup
############################################
python - <<'PY'
import sys,importlib,pathlib
removed=[]
for p in sys.path:
    if 'site-packages' not in p: continue
    base=pathlib.Path(p)
    nv=base/'nvidia'
    if nv.exists():
        if not any(nv.glob('*.py')) and sum(1 for _ in nv.rglob('*'))<=1:
            try: nv.rmdir(); removed.append(str(nv))
            except Exception: pass
    tr=base/'triton'
    if tr.exists():
        try: importlib.import_module('triton')
        except Exception:
            for ch in sorted(tr.rglob('*'),reverse=True):
                try:
                    if ch.is_file(): ch.unlink()
                    else: ch.rmdir()
                except Exception: pass
            try: tr.rmdir(); removed.append(str(tr))
            except Exception: pass
if removed:
    print("[cleanup] removed_orphans=", ",".join(removed))
PY

############################################
# 15) Torch Verification
############################################
torch_meta=$(python - <<'PY'
import json
info={"ok":True,"cpu_tag":False,"version":None}
try:
    import torch
    info["version"]=torch.__version__
    info["cpu_tag"]="+cpu" in info["version"]
except Exception:
    info["ok"]=False
print(json.dumps(info))
PY
)
torch_ok=$(echo "$torch_meta" | python -c 'import sys,json;print(json.load(sys.stdin)["ok"])')
torch_cpu_tag=$(echo "$torch_meta" | python -c 'import sys,json;print(json.load(sys.stdin)["cpu_tag"])')
if [[ "$torch_ok" != "True" || "$torch_cpu_tag" != "True" ]]; then
  if (( VENDOR_UNINSTALL_COUNT > 0 )); then
    log_info "Torch anomaly (ok=${torch_ok} cpu_tag=${torch_cpu_tag}); reinstalling."
    run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu --force-reinstall \"torch==${CODEX_TORCH_VERSION_BASE}\""
  else
    record_warn "torch_verify" "Torch anomaly without preceding vendor purge."
  fi
else
  log "Torch verified: $(echo "$torch_meta" | python -c 'import sys,json;print(json.load(sys.stdin)["version"])')"
fi

############################################
# 16) Pre-commit
############################################
if [[ -f .pre-commit-config.yaml && "$CODEX_ENSURE_PRECOMMIT" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  if ! command -v pre-commit >/dev/null 2>&1; then
    run "uv pip install --python \"$UV_PYTHON\" pre-commit || true"
  fi
  run "pre-commit install -f -t pre-commit -t pre-push -t prepare-commit-msg || true"
fi

############################################
# 17) Large File Scan (only warn on actual issue)
############################################
if command -v git >/dev/null 2>&1; then
  set +e
  git rev-list --objects --all 2>/dev/null | \
    git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' 2>/dev/null | \
    awk '$1=="blob" && $3>100*1024*1024 {print $4" "$3}' | while read -r P S; do
      if ! git lfs ls-files --name-only 2>/dev/null | grep -qx "$P"; then
        record_warn "lfs" "Large blob not in LFS: $P ($S bytes)"
      fi
    done
  set -e
fi

############################################
# 18) Cache Prune
############################################
if [[ "$CODEX_CACHE_PRUNE" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  if command -v uv >/dev/null 2>&1; then
    run "uv cache prune || true"
  fi
fi

############################################
# 19) Lock Hash
############################################
calc_lockhash(){ ( sha256sum uv.lock 2>/dev/null || true; sha256sum pyproject.toml 2>/dev/null || true ) | sha256sum | awk '{print $1}'; }
if [[ "$CODEX_SUMMARY_INCLUDE_HASH" == "1" ]]; then
  calc_lockhash > .codex/cache/setup.locksum
  log "Locksum: $(cat .codex/cache/setup.locksum)"
fi

############################################
# 20) Aggregated Warning Flush
############################################
if [[ "$CODEX_WARN_AGGREGATE" == "1" ]]; then
  if ((${#WARN_EVENTS[@]})); then
    : >"$WARN_FILE"
    i=0
    for e in "${WARN_EVENTS[@]}"; do i=$((i+1)); printf '[%d] %s\n' "$i" "$e" >>"$WARN_FILE"; done
  fi
fi

############################################
# 21) Summary JSON
############################################
finalize_timings
export_phase_vars

pairs=()
for k in "${!WARN_CAT_COUNT[@]}"; do pairs+=("$k" "${WARN_CAT_COUNT[$k]}"); done
export PAIRS="${pairs[*]}"
warn_cat_json=$(python - <<PY
import json,os
p=os.getenv("PAIRS","").split()
d={}
for i in range(0,len(p),2):
    if i+1<len(p): d[p[i]]=int(p[i+1])
print(json.dumps(d))
PY
)

TORCH_INFO=$(python - <<'PY'
import json,pkgutil,os,importlib
ignore_root=os.getenv("CODEX_VENDOR_NAMESPACE_IGNORE","1")=="1"
res=[]
for m in pkgutil.iter_modules():
    n=m.name
    if n in {"triton","torchtriton"}:
        try: importlib.import_module(n)
        except Exception: continue
        res.append(n)
    elif n.startswith("nvidia"):
        if ignore_root and n=="nvidia": continue
        if n.startswith("nvidia-"):
            try: importlib.import_module(n)
            except Exception: continue
            res.append(n)
data={"torch_version":"(unknown)","cuda_build":False,"cuda_available":False,"gpu_residue":sorted(set(res))}
try:
    import torch
    data["torch_version"]=torch.__version__
    data["cuda_build"]=bool(getattr(getattr(torch,'version',None),'cuda',None))
    data["cuda_available"]=bool(getattr(torch,'cuda',None) and torch.cuda.is_available())
except Exception: pass
print(json.dumps(data))
PY
)

warn_count=$(wc -l <"$WARN_FILE" 2>/dev/null || echo 0)
fail_count=$(wc -l <"$FAIL_FILE" 2>/dev/null || echo 0)

python - <<PY
import json,os,pathlib
torch_info=json.loads('''$TORCH_INFO''')
summary={
 "mode":{
   "sync_groups":os.getenv("CODEX_SYNC_GROUPS"),
   "sync_extras":os.getenv("CODEX_SYNC_EXTRAS"),
   "force_cpu":os.getenv("CODEX_FORCE_CPU"),
   "skip_uv_sync":os.getenv("CODEX_SKIP_UV_SYNC"),
   "cpu_minimal":os.getenv("CODEX_CPU_MINIMAL"),
   "abort_on_gpu_pull":os.getenv("CODEX_ABORT_ON_GPU_PULL"),
   "lightweight_fallback":os.getenv("CODEX_LIGHTWEIGHT_CPU_FALLBACK"),
   "vendor_purge":os.getenv("CODEX_VENDOR_PURGE"),
   "use_locked_sync":os.getenv("CODEX_USE_LOCKED_SYNC"),
   "vendor_list_strict":os.getenv("CODEX_VENDOR_LIST_STRICT"),
   "cache_prune":os.getenv("CODEX_CACHE_PRUNE"),
   "hash_lock_strict":os.getenv("CODEX_HASH_LOCK_STRICT"),
   "locked_sync_fallback":os.getenv("CODEX_LOCKED_SYNC_FALLBACK"),
   "vendor_log_only_policy":os.getenv("CODEX_VENDOR_LOG_ONLY_POLICY"),
   "vendor_namespace_ignore":os.getenv("CODEX_VENDOR_NAMESPACE_IGNORE"),
   "err_trap":os.getenv("CODEX_ERR_TRAP"),
   "relock_after_vendor_purge":os.getenv("CODEX_RELOCK_AFTER_VENDOR_PURGE"),
   "cpu_constrain_lock":os.getenv("CODEX_CPU_CONSTRAIN_LOCK"),
   "warn_aggregate":os.getenv("CODEX_WARN_AGGREGATE"),
   "warn_on_fallback":os.getenv("CODEX_WARN_ON_FALLBACK"),
   "warn_on_lock_regen":os.getenv("CODEX_WARN_ON_LOCK_REGEN")
 },
 "torch": torch_info,
 "counts":{
   "warnings": int("""$warn_count"""),
   "failed_commands": int("""$fail_count""")
 },
 "warnings_by_category": json.loads('''$warn_cat_json'''),
 "vendor_metrics":{
   "fallback_purged": os.getenv("FALLBACK_VENDOR_PURGED","0"),
   "uninstalled_total": int(os.getenv("VENDOR_UNINSTALL_COUNT","0"))
 },
 "remediation":{
   "relock_events": int(os.getenv("RELOCK_EVENTS","0")),
   "fallback_events": int(os.getenv("FALLBACK_EVENTS","0")),
   "vendor_purge_events": int(os.getenv("VENDOR_PURGE_EVENTS","0"))
 },
 "timings":{
   "preinstall_s": int(os.getenv("PHASE_PREINSTALL","0")),
   "lock_chain_s": int(os.getenv("PHASE_LOCK","0")),
   "purge_s": int(os.getenv("PHASE_PURGE","0")),
   "total_s": int(os.getenv("PHASE_TOTAL","0"))
 }
}
pathlib.Path(os.getenv("SUMMARY_JSON",".codex/cache/setup_summary.json")).write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
PY

if (( warn_count > 0 )); then
  log "Completed with warnings=$warn_count"
else
  log "Setup finished clean."
fi

if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_FAIL_ON_GPU_RESIDUE" == "1" ]]; then
  if python - <<'PY'
import pkgutil,sys,importlib
mods=[]
for m in pkgutil.iter_modules():
    n=m.name
    if n.startswith("nvidia-") or n in {"triton","torchtriton"}:
        try: importlib.import_module(n)
        except Exception: continue
        mods.append(n)
sys.exit(0 if not mods else 7)
PY
  then :; else die "Residual vendor packages remain (strict)."; fi
fi

if (( fail_count > 0 )) && [[ "$STRICT_SETUP" == "1" ]]; then
  die "Failures detected and STRICT_SETUP=1"
fi

exit 0
