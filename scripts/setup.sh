#!/usr/bin/env bash
# =============================================================================
# setup.sh
# Unified Environment Bootstrap (CPU-Constrained) with Enhanced Observability
# Version: 5.5.1-rc4-hotfix2
# Date: 2025-09-17
#
# CHANGELOG:
#   rc4-hotfix2:
#     - FIX: Eliminate false-positive vendor residue during setup by gating vendor
#       log aggregation to pre-sync only and forcing post-uninstall and post-purge
#       analytics to ignore logs (FIRST_SYNC_DONE=1 for residue/hash checks).
#       New env: CODEX_VENDOR_LOG_AGG=pre-sync|always|never (default pre-sync).
#   rc4-hotfix1:
#     - FIX: Replaced pipe + heredoc JSON parsing (printf | python <<'PY') with env-var-based
#       parsing to avoid SIGPIPE/ERR trap noise under set -e -o pipefail (parity with maintenance).
#     - KEEP: Earlier rc4 fixes (purge_and_measure ordering, lock outdated counters, etc.)
# =============================================================================

set -Eeuo pipefail

# 0) Config Flags
export GRACEFUL="${CODEX_GRACEFUL:-1}"
export STRICT_SETUP="${CODEX_STRRICT_SETUP:-${CODEX_STRICT_SETUP:-0}}"
export CODEX_DEBUG="${CODEX_DEBUG:-0}"
export CODEX_OFFLINE="${CODEX_OFFLINE:-0}"

export CODEX_SYNC_GROUPS="${CODEX_SYNC_GROUPS:-base,cpu}"
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
export CODEX_WARN_ON_FALLBACK="${CODEX_WARN_ON_FALLBACK:-0}"
export CODEX_WARN_ON_LOCK_REGEN="${CODEX_WARN_ON_LOCK_REGEN:-0}"
export CODEX_ENV_DIGEST="${CODEX_ENV_DIGEST:-1}"

export CODEX_VENDOR_HEURISTIC_RECOVER="${CODEX_VENDOR_HEURISTIC_RECOVER:-1}"
export CODEX_FALLBACK_SNAPSHOT="${CODEX_FALLBACK_SNAPSHOT:-1}"
export CODEX_SYNC_FAIL_EXCERPT_LINES="${CODEX_SYNC_FAIL_EXCERPT_LINES:-20}"
export CODEX_PURGE_OUTPUT_SANITIZE="${CODEX_PURGE_OUTPUT_SANITIZE:-1}"
export CODEX_ALLOW_TRITON_CPU="${CODEX_ALLOW_TRITON_CPU:-1}"
export CODEX_FAST_TORCH_RECHECK="${CODEX_FAST_TORCH_RECHECK:-1}"

export CODEX_VENDOR_RECURRENCE_WARN="${CODEX_VENDOR_RECURRENCE_WARN:-warn}"
export CODEX_VENDOR_REAPPEAR_WINDOW="${CODEX_VENDOR_REAPPEAR_WINDOW:-5}"
export CODEX_VENDOR_RECUR_HASH_FILE="${CODEX_VENDOR_RECUR_HASH_FILE:-.codex/cache/vendor_set.hashes}"
export CODEX_VENDOR_ENFORCE_LOCK_PRUNE="${CODEX_VENDOR_ENFORCE_LOCK_PRUNE:-0}"
export CODEX_VENDOR_ENFORCE_LOCK_PRUNE_DRYRUN="${CODEX_VENDOR_ENFORCE_LOCK_PRUNE_DRYRUN:-1}"
export CODEX_VENDOR_LOCK_GPU_PATTERN="${CODEX_VENDOR_LOCK_GPU_PATTERN:-\"name\": \"(nvidia-|triton|torchtriton)\"}"
export CODEX_VENDOR_LOCK_SCAN_ENABLE="${CODEX_VENDOR_LOCK_SCAN_ENABLE:-1}"
export CODEX_VENDOR_REPRT_EMPTY_LOCKGPU="${CODEX_VENDOR_REPRT_EMPTY_LOCKGPU:-0}"
export CODEX_VENDOR_REINSTALL_TORCH_ON_PURGE="${CODEX_VENDOR_REINSTALL_TORCH_ON_PURGE:-1}"
export CODEX_VENDOR_RELOCK_AFTER_LOCK_PRUNE="${CODEX_VENDOR_RELOCK_AFTER_LOCK_PRUNE:-1}"
export CODEX_VENDOR_HASH_DEBUG="${CODEX_VENDOR_HASH_DEBUG:-0}"
export CODEX_SYNC_RETRY_MAX="${CODEX_SYNC_RETRY_MAX:-3}"

export CODEX_VENDOR_LOG_AGG="${CODEX_VENDOR_LOG_AGG:-pre-sync}"

if [[ -z "${CODEX_FORCE_CPU:-}" ]]; then
  if [[ ",${CODEX_SYNC_GROUPS}," == *",gpu,"* ]]; then export CODEX_FORCE_CPU=0; else export CODEX_FORCE_CPU=1; fi
fi
[[ "$CODEX_DEBUG" == "1" ]] && set -x

# 1) Logging & Aggregation
mkdir -p .codex/logs .codex/cache artifacts data
WARN_FILE=".codex/logs/setup_warnings.log"
FAIL_FILE=".codex/logs/command_failures.log"
SYNC_LOG=".codex/cache/uv_sync.log"
SUMMARY_JSON=".codex/cache/setup_summary.json"
: >"$WARN_FILE"; : >"$FAIL_FILE"; : >"$SYNC_LOG"

log(){ printf "[setup] %s %s\n" "$(date -Iseconds)" "$*"; }
log_info(){ log "INFO: $*"; }
_raw_warn(){ log "WARN: $*"; printf '%s\n' "$*" >>"$WARN_FILE"; }
die(){ printf "[setup][ERROR] %s\n" "$*" >&2; exit 1; }

WARN_EVENTS=()
WARN_EVENT_CATS=()
declare -A WARN_CAT_COUNT=()

record_warn(){ local cat="$1"; shift; local msg="$*"; WARN_EVENTS+=("$msg"); WARN_EVENT_CATS+=("$cat"); WARN_CAT_COUNT["$cat"]=$(( ${WARN_CAT_COUNT["$cat"]:-0} + 1 )); if [[ "$CODEX_WARN_AGGREGATE" == "0" ]]; then _raw_warn "[$cat] $msg"; else _raw_warn "$msg"; fi; }
maybe_fail(){ local m="$1"; if [[ "$GRACEFUL" == "1" && "$STRICT_SETUP" == "0" ]]; then record_warn "fail-soft" "$m — continuing"; else die "$m"; fi; }

if [[ "$CODEX_ERR_TRAP" == "1" ]]; then
  set -E
  trap 'ec=$?; [[ $ec -ne 0 ]] && log "ERR line=$LINENO ec=$ec cmd=${BASH_COMMAND}"' ERR
fi

safe_test(){ if [[ "$1" == "1" ]]; then return 0; else return 1; fi; }

_cmd_index=0
run(){
  local cmd="$*"
  _cmd_index=$((_cmd_index+1))
  local start=$(date +%s)
  set +e
  bash -lc "$cmd" > >(tee /tmp/codex_cmd_out.$$) 2>&1
  local ec=$?
  set -e
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
  local max="${1:-${CODEX_SYNC_RETRY_MAX}}"; shift
  local cmd="$*"
  local attempt=1 ec=0 first_excerpt="" excerpt_lines="${CODEX_SYNC_FAIL_EXCERPT_LINES}"
  while true; do
    set +e
    ( set +e; bash -lc "$cmd" ) > /tmp/codex_retry_out.$$ 2>&1
    ec=$?
    set -e
    cat /tmp/codex_retry_out.$$ >>"$SYNC_LOG"
    if (( attempt == 1 && ec != 0 )); then first_excerpt="$(head -n "$excerpt_lines" /tmp/codex_retry_out.$$)"; fi
    if (( ec == 0 )); then log "OK(retry t=$attempt) $cmd"; return 0; fi
    if (( attempt >= max )); then log_info "Final failure for: $cmd (first-attempt excerpt follows)"; printf '%s\n' "$first_excerpt" | sed 's/^/[sync-fail-snippet] /'; return $ec; fi
    sleep $(( attempt * 2 )); attempt=$(( attempt + 1 ))
  done
}

# 2) Timings
_ts(){ [[ "$CODEX_METRICS_TIMINGS" == "1" ]] || return 0; date +%s; }
PHASE_START_TOTAL=$(_ts || echo 0)
PHASE_PREINSTALL=0 PHASE_LOCK=0 PHASE_PURGE=0 PHASE_VENDOR_ANALYTICS=0 PHASE_LOCK_SCAN=0 PHASE_TOTAL=0
PHASE_MARK(){ [[ "$CODEX_METRICS_TIMINGS" == "1" ]] || return 0; local var="$1" start="$2" end=$(_ts); printf -v "$var" "%s" "$(( end - start ))"; export "$var"; }
finalize_timings(){ if [[ "$CODEX_METRICS_TIMINGS" == "1" ]]; then local end=$(_ts); PHASE_TOTAL=$(( end - PHASE_START_TOTAL )); else PHASE_TOTAL=0; fi; export PHASE_TOTAL; }
export_phase_vars(){ export PHASE_PREINSTALL PHASE_LOCK PHASE_PURGE PHASE_VENDOR_ANALYTICS PHASE_LOCK_SCAN PHASE_TOTAL; }

# 3) Context
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

# 4) Vendor Helper – Python (log aggregation is gated by CODEX_VENDOR_LOG_AGG)
VENDOR_HELPER_PY="$(cat <<'PY'
import os, pkgutil, re, sys, pathlib, subprocess, importlib, json, hashlib
MODE=sys.argv[1]
ignore_root = os.getenv("CODEX_VENDOR_NAMESPACE_IGNORE","1") == "1"
strict      = os.getenv("CODEX_VENDOR_LIST_STRICT","1") == "1"
sync_log    = pathlib.Path(".codex/cache/uv_sync.log")
first_sync_done = os.getenv("FIRST_SYNC_DONE","0") == "1"
hash_debug  = os.getenv("CODEX_VENDOR_HASH_DEBUG","0") == "1"
log_agg     = os.getenv("CODEX_VENDOR_LOG_AGG","pre-sync")  # pre-sync|always|never

fallback_set = {
 "triton","torchtriton","nvidia-cublas-cu12","nvidia-cuda-cupti-cu12",
 "nvidia-cuda-nvrtc-cu12","nvidia-cuda-runtime-cu12","nvidia-cudnn-cu12",
 "nvidia-cufft-cu12","nvidia-cufile-cu12","nvidia-curand-cu12",
 "nvidia-cusolver-cu12","nvidia-cusparse-cu12","nvidia-cusparselt-cu12",
 "nvidia-nccl-cu12","nvidia-nvjitlink-cu12","nvidia-nvtx-cu12"
}
def uv_list():
    try:
        out = subprocess.check_output(
            ["uv","pip","list","--format","json","--python",os.getenv("UV_PYTHON","python")],
            text=True
        )
        return json.loads(out)
    except Exception as e:
        if hash_debug:
            print(f"[vendor-helper-debug] uv_list error: {e}", file=sys.stderr)
        return []
def packages_set(listing):
    s=set()
    for entry in listing:
        if not isinstance(entry, dict): continue
        name=(entry.get("name") or "").lower()
        if name.startswith("nvidia-") or name in {"triton","torchtriton"}:
            s.add(name)
    return s
def logs():
    if not sync_log.exists(): return set()
    pat = re.compile(r"(nvidia-[a-z0-9\\-]+|triton|torchtriton)")
    return {m.group(1).lower() for m in pat.finditer(sync_log.read_text())}
def import_modules():
    present=set()
    for m in pkgutil.iter_modules():
        n=m.name.lower()
        if n.startswith("nvidia") or n in {"triton","torchtriton"}:
            try:
                importlib.import_module(n)
            except Exception:
                continue
            present.add(n)
    return present
def aggregate():
    uv_l = uv_list()
    base = packages_set(uv_l)
    include_logs = (log_agg == "always") or (log_agg == "pre-sync" and not first_sync_done)
    if include_logs:
        base |= logs()
    base |= import_modules()
    if not first_sync_done and not base and strict and logs():
        base |= fallback_set
    if ignore_root:
        base={b for b in base if b != "nvidia"}
    base={b for b in base if b.startswith("nvidia-") or b in {"triton","torchtriton"}}
    return sorted(base)
vendors=aggregate()
if MODE=="collect":
    print(" ".join(vendors))
elif MODE=="residue":
    print(" ".join(vendors))
elif MODE=="hash":
    joined=";".join(vendors)
    h=hashlib.sha256(joined.encode()).hexdigest() if vendors else ""
    data={"hash":h,"vendors":vendors,"count":len(vendors)}
    print(json.dumps(data, ensure_ascii=False))
else:
    print("")
PY
)"

python - <<'PY' >/dev/null 2>&1 && log_info "[vendor-helper] preflight ok" || log_info "[vendor-helper] preflight failed (continuing)"
print("ok")
PY

vendor_collect(){ python -c "$VENDOR_HELPER_PY" collect; }
vendor_residue(){ python -c "$VENDOR_HELPER_PY" residue; }
vendor_hash_json(){ python -c "$VENDOR_HELPER_PY" hash; }

# 5) Uninstall & Parsing
sanitize_uninstall_stream(){ sed -r -e 's/\x1B\[[0-9;]*[A-Za-z]//g' -e '/^\+\+/d' -e '/^[[:space:]]*$/d'; }
uv_uninstall_noninteractive(){
  [[ $# -eq 0 ]] && return 0
  local had_xtrace=0; case "$-" in *x*) had_xtrace=1; set +x ;; esac
  if command -v uv >/dev/null 2>&1; then
    if command -v yes >/dev/null 2>&1; then yes | uv pip uninstall "$@" || true
    else printf 'y\n%.0s' {1..250} | uv pip uninstall "$@" || true
    fi
  else
    python -m pip uninstall -y "$@" || true
  fi
  (( had_xtrace )) && set -x || true
}
count_uninstalls(){ awk '{ if ($0 ~ /^\+\+/) next; line=$0; sub(/^[[:space:]]+/,"",line); if (line ~ /^-[[:space:]]+[A-Za-z0-9_.:-]+==/) c++ } END { print c+0 }'; }

# 6) purge_and_measure (defined BEFORE any use)
purge_and_measure(){
  local mode="$1"; shift
  local vendor_list="$1"
  [[ -z "$vendor_list" ]] && { log_info "No vendor packages for $mode purge."; return 0; }

  if [[ "$mode" == "fallback" && "$CODEX_FALLBACK_SNAPSHOT" == "1" ]]; then
    printf "%s\n" "$vendor_list" > .codex/cache/vendor_seen_fallback.txt 2>/dev/null || true
  else
    printf "%s\n" "$vendor_list" > .codex/cache/vendor_seen.txt 2>/dev/null || true
  fi

  if [[ "$mode" == "fallback" ]]; then
    FALLBACK_VENDOR_PURGED=1
    FALLBACK_EVENTS=$(( FALLBACK_EVENTS + 1 ))
    export FALLBACK_VENDOR_PURGED FALLBACK_EVENTS
    [[ -z "$FALLBACK_REASON" ]] && FALLBACK_REASON="sync_log_vendor"
  fi

  if [[ "$mode" == "fallback" && "$CODEX_WARN_ON_FALLBACK" == "1" ]]; then
    record_warn "fallback" "Fallback purge: $vendor_list"
  else
    log_info "$mode purge: removing: $vendor_list"
  fi

  local uninstall_output raw_output purged_count RESIDUE pre_before post_after heuristic_applied=0
  pre_before="$(FIRST_SYNC_DONE=1 python -c "$VENDOR_HELPER_PY" residue | tr ' ' '\n' | sort -u | tr '\n' ' ')"

  raw_output=$(uv_uninstall_noninteractive $vendor_list 2>&1 || true)
  raw_output=$(printf "%s" "$raw_output" | tr -d '\r')
  if [[ "$CODEX_PURGE_OUTPUT_SANITIZE" == "1" ]]; then
    uninstall_output=$(printf "%s" "$raw_output" | sanitize_uninstall_stream)
  else
    uninstall_output="$raw_output"
  fi

  purged_count=$(printf "%s" "$uninstall_output" | count_uninstalls)
  # Post-uninstall residue should ignore log-only signals to prevent false positives
  RESIDUE="$(FIRST_SYNC_DONE=1 python -c "$VENDOR_HELPER_PY" residue)"
  post_after="$(printf "%s" "$RESIDUE" | tr ' ' '\n' | sort -u | tr '\n' ' ')"

  if (( purged_count == 0 )) && [[ "$CODEX_VENDOR_HEURISTIC_RECOVER" == "1" ]]; then
    if [[ -n "$pre_before" && -z "$post_after" ]]; then
      purged_count=$(printf "%s" "$pre_before" | tr ' ' '\n' | grep -c . || true)
      heuristic_applied=1
      log_info "Heuristic vendor uninstall correction applied: inferred=$purged_count"
    fi
  fi

  if (( purged_count > 0 )); then
    VENDOR_UNINSTALL_COUNT=$(( VENDOR_UNINSTALL_COUNT + purged_count ))
    if [[ "$mode" == "primary" ]]; then
      VENDOR_PURGE_EVENTS=$(( VENDOR_PURGE_EVENTS + 1 ))
    fi
    export VENDOR_UNINSTALL_COUNT VENDOR_PURGE_EVENTS
  fi

  if [[ -n "$RESIDUE" && "$CODEX_ALLOW_TRITON_CPU" == "1" ]]; then
    local filtered
    filtered=$(printf "%s" "$RESIDUE" | tr ' ' '\n' | grep -v '^triton$' || true)
    if [[ -z "$filtered" ]]; then RESIDUE=""; fi
  fi

  if [[ -n "$RESIDUE" ]]; then
    record_warn "vendor_residue" "Residual vendor distributions: $RESIDUE"
    [[ "$CODEX_FAIL_ON_GPU_RESIDUE" == "1" ]] && echo "RESIDUAL_VENDOR=$RESIDUE" >>"$FAIL_FILE"
  else
    log_info "$mode purge successful (no residue)."
  fi

  if (( purged_count > 0 )) && [[ "$CODEX_VENDOR_REINSTALL_TORCH_ON_PURGE" == "1" ]] && [[ "$CODEX_OFFLINE" != "1" ]]; then
    run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu --force-reinstall \"torch==${CODEX_TORCH_VERSION_BASE}\""
  fi

  if [[ "$CODEX_DEBUG" == "1" ]]; then
    printf "%s\n" "$uninstall_output" > ".codex/cache/${mode}_purge_uninstall.log" || true
    (( heuristic_applied )) && echo "[heuristic] applied=1 adjusted=$purged_count" >> ".codex/cache/${mode}_purge_uninstall.log"
  fi
}

# 7) Token Advisory
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

# 8) System Dependencies
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

# 9) uv & Virtual Environment
if ! command -v uv >/dev/null 2>&1 && [[ "$CODEX_OFFLINE" != "1" ]]; then
  command -v curl >/dev/null 2>&1 && run "curl -fsSL https://astral.sh/uv/install.sh | bash || true"
  command -v uv >/dev/null 2>&1 || run "python3 -m pip install --user uv || true"
  export PATH="$HOME/.local/bin:$PATH"
fi
command -v uv >/dev/null 2>&1 && log "uv: $(uv --version || true)"

if [[ ! -d .venv ]]; then
  if command -v uv >/dev/null 2>&1 && [[ -f pyproject.toml ]]; then
    run "uv venv --seed .venv || python3 -m venv .venv"
  else
    run "python3 -m venv .venv"
  fi
fi
# shellcheck disable=SC1091
source .venv/bin/activate || maybe_fail "Activate venv failed"
export UV_PYTHON; UV_PYTHON="$(command -v python)"

# 10) pyproject Torch Spec Normalize
if [[ -f pyproject.toml ]] && grep -qE 'torch==[0-9]+\.[0-9]+\.[0-9]+\+cpu' pyproject.toml; then
  cp pyproject.toml ".codex/cache/pyproject.toml.pre_sanitize.$(date +%s)" || true
  sed -E -i 's/(torch==[0-9]+\.[0-9]+\.[0-9]+)\+cpu/\1/g' pyproject.toml
  rm -f uv.lock
  log_info "Sanitized '+cpu' suffix from pyproject torch spec."
fi

# 11) Torch Preinstall Anchor
PHASE_PREINSTALL_START=$(_ts || echo 0)
SAVED_PIP_INDEX_URL="" SAVED_PIP_EXTRA_INDEX_URL=""
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  export PIP_INDEX_URL="https://download.pytorch.org/whl/cpu"
  export PIP_EXTRA_INDEX_URL="https://pypi.org/simple"
  run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu \"torch==${CODEX_TORCH_VERSION_BASE}\""
  SAVED_PIP_INDEX_URL="$PIP_INDEX_URL"; SAVED_PIP_EXTRA_INDEX_URL="$PIP_EXTRA_INDEX_URL"
fi
PHASE_MARK PHASE_PREINSTALL "$PHASE_PREINSTALL_START"

# 12) Lock / Sync + Lock Scan / Prune
cpu_constrained_lock(){
  if [[ "$CODEX_CPU_CONSTRAIN_LOCK" != "1" ]]; then run_retry_log 3 "uv lock" || return $?; return 0; fi
  local bak_idx="${PIP_INDEX_URL-}" bak_extra="${PIP_EXTRA_INDEX_URL-}"
  export PIP_INDEX_URL="https://download.pytorch.org/whl/cpu"; unset PIP_EXTRA_INDEX_URL || true
  run_retry_log 3 "uv lock" || return $?
  [[ -n "$bak_idx" ]] && export PIP_INDEX_URL="$bak_idx" || unset PIP_INDEX_URL
  [[ -n "$bak_extra" ]] && export PIP_EXTRA_INDEX_URL="$bak_extra" || unset PIP_EXTRA_INDEX_URL
  return 0
}
cpu_constrained_sync(){
  if [[ "$CODEX_CPU_CONSTRAIN_LOCK" != "1" ]]; then run_retry_log 3 "uv sync --locked || uv sync" || return $?; return 0; fi
  local bak_idx="${PIP_INDEX_URL-}" bak_extra="${PIP_EXTRA_INDEX_URL-}"
  export PIP_INDEX_URL="https://download.pytorch.org/whl/cpu"; unset PIP_EXTRA_INDEX_URL || true
  run_retry_log 3 "uv sync --locked || uv sync" || return $?
  [[ -n "$bak_idx" ]] && export PIP_INDEX_URL="$bak_idx" || unset PIP_INDEX_URL
  [[ -n "$bak_extra" ]] && export PIP_EXTRA_INDEX_URL="$bak_extra" || unset PIP_EXTRA_INDEX_URL
  return 0
}
validate_lock_torch(){
  if [[ "$CODEX_HASH_LOCK_STRICT" != "1" ]] || [[ ! -f uv.lock ]]; then
    return 0
  fi
  if grep -E '"name": "torch"' -A2 uv.lock 2>/dev/null | grep -q "+cpu"; then
    rm -f uv.lock; return 1
  fi
  return 0
}

RELOCK_EVENTS=0 FALLBACK_EVENTS=0 VENDOR_PURGE_EVENTS=0 LOCK_OUTDATED_EVENTS=0
FALLBACK_VENDOR_PURGED=0 VENDOR_UNINSTALL_COUNT=0 FALLBACK_REASON=""
VENDOR_RECURRENCE=0 VENDOR_RECURRENCE_COUNT=0
LOCK_SCAN_GPU_BEFORE=0 LOCK_SCAN_GPU_AFTER=0
LOCK_GPU_LIST_BEFORE="" LOCK_GPU_LIST_AFTER=""
LOCK_PRUNE_ACTION="none" LOCK_PRUNE_REMOVED=0
LOCK_PRUNE_DIFF_FILE=".codex/cache/lock_prune.diff"
VENDOR_SET_HASH_BEFORE="" VENDOR_SET_LIST_BEFORE=""
VENDOR_SET_HASH_AFTER=""  VENDOR_SET_LIST_AFTER=""
VENDOR_SET_CLASS_BEFORE="none"
export RELOCK_EVENTS FALLBACK_EVENTS VENDOR_PURGE_EVENTS FALLBACK_VENDOR_PURGED VENDOR_UNINSTALL_COUNT FALLBACK_REASON VENDOR_RECURRENCE VENDOR_RECURRENCE_COUNT LOCK_SCAN_GPU_BEFORE LOCK_SCAN_GPU_AFTER LOCK_GPU_LIST_BEFORE LOCK_GPU_LIST_AFTER LOCK_PRUNE_ACTION LOCK_PRUNE_REMOVED LOCK_OUTDATED_EVENTS VENDOR_SET_HASH_BEFORE VENDOR_SET_HASH_AFTER VENDOR_SET_LIST_BEFORE VENDOR_SET_LIST_AFTER VENDOR_SET_CLASS_BEFORE

unset PIP_INDEX_URL PIP_EXTRA_INDEX_URL || true
FIRST_SYNC_DONE=0; export FIRST_SYNC_DONE
PH_LOCK_START=$(_ts || echo 0)

# Baseline vendor snapshot (robust JSON parse)
pre_sync_vendor_json="$(vendor_hash_json || true)"
echo "$pre_sync_vendor_json" > .codex/cache/vendor_hash_pre_sync.json 2>/dev/null || true
VENDOR_SET_HASH_BEFORE="$(
JSON_IN="$pre_sync_vendor_json" python - <<'PY'
import os, json
raw=os.environ.get("JSON_IN","").strip()
try:
    data=json.loads(raw) if raw else {}
    print(data.get("hash",""))
except Exception:
    print("")
PY
)"
VENDOR_SET_LIST_BEFORE="$(
JSON_IN="$pre_sync_vendor_json" python - <<'PY'
import os, json
raw=os.environ.get("JSON_IN","").strip()
try:
    data=json.loads(raw) if raw else {}
    print(" ".join(data.get("vendors",[])))
except Exception:
    print("")
PY
)"
if [[ -n "$VENDOR_SET_LIST_BEFORE" ]]; then VENDOR_SET_CLASS_BEFORE="contaminated"; else VENDOR_SET_CLASS_BEFORE="clean"; fi
export VENDOR_SET_HASH_BEFORE VENDOR_SET_LIST_BEFORE VENDOR_SET_CLASS_BEFORE

scan_lock_for_gpu(){
  if [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" != "1" ]] || [[ ! -f uv.lock ]]; then echo ""; return 0; fi
  grep -E '"name": "(nvidia-|triton|torchtriton)' uv.lock 2>/dev/null || true
}
lock_scan_report_phase(){
  local phase="$1" scan_output count list
  scan_output="$(scan_lock_for_gpu)"; count=0; list=""
  if [[ -n "$scan_output" ]]; then list="$(echo "$scan_output" | sed -E 's/.*"name": "([^"]+)".*/\1/g' | sort -u | tr '\n' ' ')"; count=$(echo "$list" | tr ' ' '\n' | grep -c . || true); fi
  if [[ "$phase" == "before" ]]; then LOCK_SCAN_GPU_BEFORE=$count; LOCK_GPU_LIST_BEFORE="$list"; else LOCK_SCAN_GPU_AFTER=$count; LOCK_GPU_LIST_AFTER="$list"; fi
  export LOCK_SCAN_GPU_BEFORE LOCK_SCAN_GPU_AFTER LOCK_GPU_LIST_BEFORE LOCK_GPU_LIST_AFTER
  if (( count > 0 )); then record_warn "lock_gpu_refs" "Lock scan ($phase) found $count GPU vendor refs: $list"; else if [[ "$CODEX_VENDOR_REPRT_EMPTY_LOCKGPU" == "1" ]]; then log_info "Lock scan ($phase) found no GPU vendor refs."; fi; fi
}
attempt_lock_prune(){
  [[ "$CODEX_VENDOR_ENFORCE_LOCK_PRUNE" == "1" ]] || return 0
  [[ -f uv.lock ]] || { log_info "Lock prune skipped (missing uv.lock)"; return 0; }
  local pre_hash post_hash lines_removed=0
  pre_hash=$(sha256sum uv.lock | awk '{print $1}')
  cp uv.lock ".codex/cache/uv.lock.prune.backup.$(date +%s)" || true
  local tmpfile=".codex/cache/uv.lock.prune.$$.tmp"
  awk 'BEGIN{removed=0} /"name": "nvidia-|\"name\": \"triton\"|\"name\": \"torchtriton\"/ { removed=1 } { if(removed==1){ if($0 ~ /},?$/){removed=0;next} ; next } ; print }' uv.lock > "$tmpfile" || true
  if [[ -s "$tmpfile" ]]; then
    lines_removed=$(diff -u uv.lock "$tmpfile" | grep -E '^[+-]' | grep -v '+++' | grep -v '---' | wc -l | tr -d ' ')
    if [[ "$CODEX_VENDOR_ENFORCE_LOCK_PRUNE_DRYRUN" == "1" ]]; then
      diff -u uv.lock "$tmpfile" > "$LOCK_PRUNE_DIFF_FILE" || true
      LOCK_PRUNE_ACTION="dryrun"; LOCK_PRUNE_REMOVED=$lines_removed
      record_warn "lock_prune_dryrun" "GPU lock entries found (delta=$lines_removed) dry-run diff=$LOCK_PRUNE_DIFF_FILE"
      rm -f "$tmpfile"
    else
      diff -u uv.lock "$tmpfile" > "$LOCK_PRUNE_DIFF_FILE" || true
      mv "$tmpfile" uv.lock
      post_hash=$(sha256sum uv.lock | awk '{print $1}')
      LOCK_PRUNE_ACTION="applied"; LOCK_PRUNE_REMOVED=$lines_removed
      log_info "Lock prune applied (delta=$lines_removed pre=$pre_hash post=$post_hash)"
      if [[ "$CODEX_VENDOR_RELOCK_AFTER_LOCK_PRUNE" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
        log_info "Relocking after lock prune."
        cpu_constrained_lock || maybe_fail "Lock regen after prune failed"
        RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )); export RELOCK_EVENTS
      fi
    fi
  else
    log_info "Lock prune no changes."; rm -f "$tmpfile"
  fi
  export LOCK_PRUNE_ACTION LOCK_PRUNE_REMOVED
}

# Lock/sync chain
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_SKIP_UV_SYNC" == "1" ]]; then
  log_info "Skipping uv sync (CODEX_SKIP_UV_SYNC=1)"
else
  if [[ "$CODEX_OFFLINE" != "1" && -f pyproject.toml && $(command -v uv) ]]; then
    # safe_lock_sync
    relock_needed=0
    if [[ -f uv.lock ]]; then
      if ! validate_lock_torch; then relock_needed=1; fi
    else
      relock_needed=1
    fi
    if (( relock_needed )); then
      RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )); export RELOCK_EVENTS
      if [[ "$CODEX_WARN_ON_LOCK_REGEN" == "1" ]]; then record_warn "lock" "Regenerating lock (auto)"; else log_info "Regenerating lock (auto)"; fi
      cpu_constrained_lock || maybe_fail "Lock generation failed"
    fi
    if [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" == "1" ]]; then lock_scan_report_phase "before"; fi
    if [[ "$CODEX_USE_LOCKED_SYNC" == "1" && -f uv.lock && $relock_needed -eq 0 ]]; then
      if ! run_retry_log 2 "uv sync --locked"; then
        LOCK_OUTDATED_EVENTS=$(( LOCK_OUTDATED_EVENTS + 1 )); export LOCK_OUTDATED_EVENTS
        [[ -z "$FALLBACK_REASON" ]] && FALLBACK_REASON="lock_outdated"
        log_info "Locked sync failed (lock outdated); regenerating & syncing."
        cpu_constrained_lock || maybe_fail "Relock after outdated failed"
        RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )); export RELOCK_EVENTS
        cpu_constrained_sync || maybe_fail "Sync after relock failed"
      fi
    else
      cpu_constrained_sync || maybe_fail "Sync failed"
    fi
    if [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" == "1" ]]; then lock_scan_report_phase "after"; fi

    # Optional lock prune
    if (( LOCK_SCAN_GPU_AFTER > 0 )) && [[ "$CODEX_VENDOR_ENFORCE_LOCK_PRUNE" == "1" ]]; then
      [[ -z "$FALLBACK_REASON" ]] && FALLBACK_REASON="lock_gpu_specs"
      attempt_lock_prune
      if [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" == "1" ]]; then lock_scan_report_phase "after"; fi
    fi

    # Vendor wheel detection via sync log (fallback)
    if grep -E 'Downloading nvidia-|Downloading triton ' "$SYNC_LOG" >/dev/null 2>&1 && [[ "$CODEX_FORCE_CPU" == "1" ]]; then
      case "$CODEX_VENDOR_LOG_ONLY_POLICY" in
        ignore) log_info "Vendor wheels observed (ignore policy)";;
        warn)
          if [[ "$CODEX_WARN_ON_FALLBACK" == "1" ]]; then record_warn "vendor_detect" "Vendor wheels observed."; else log_info "Vendor wheels observed."; fi
          ;;
        purge)
          if [[ "$CODEX_ABORT_ON_GPU_PULL" == "1" ]]; then die "Aborting (vendor wheel detected)."; fi
          if [[ "$CODEX_LIGHTWEIGHT_CPU_FALLBACK" == "1" ]]; then
            local_vendors="$(vendor_collect)"
            if [[ -n "$local_vendors" ]]; then
              [[ -z "$FALLBACK_REASON" ]] && FALLBACK_REASON="sync_log_vendor"
              purge_and_measure "fallback" "$local_vendors"
              export CODEX_CPU_MINIMAL=1
              if [[ "$CODEX_RELOCK_AFTER_VENDOR_PURGE" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
                log_info "Relocking after fallback purge."
                cpu_constrained_lock && RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )) && export RELOCK_EVENTS
                cpu_constrained_sync || maybe_fail "Sync post fallback relock failed"
                [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" == "1" ]] && lock_scan_report_phase "after"
              fi
            else
              log_info "Fallback branch: vendor list empty."
            fi
          fi
          ;;
      esac
    fi
  fi
fi
PHASE_MARK PHASE_LOCK "$PH_LOCK_START"

[[ -n "$SAVED_PIP_INDEX_URL" ]] && export PIP_INDEX_URL="$SAVED_PIP_INDEX_URL" || true
[[ -n "$SAVED_PIP_EXTRA_INDEX_URL" ]] && export PIP_EXTRA_INDEX_URL="$SAVED_PIP_EXTRA_INDEX_URL" || true

# 13) Minimal Augmentation
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_CPU_MINIMAL" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  run "uv pip install --python \"$UV_PYTHON\" --no-deps transformers tokenizers safetensors accelerate || true"
fi

# 14) Primary Vendor Purge
PH_PURGE_START=$(_ts || echo 0)
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_VENDOR_PURGE" == "1" && "$FALLBACK_VENDOR_PURGED" != "1" ]]; then
  VENDOR_LIST="$(vendor_collect)"
  if [[ -n "$VENDOR_LIST" ]]; then
    purge_and_measure "primary" "$VENDOR_LIST"
  else
    log_info "No vendor distributions detected (primary scan)."
  fi
fi
PHASE_MARK PHASE_PURGE "$PH_PURGE_START"

# 15) Vendor Recurrence Analysis (Post-Purge)
# Force post-purge analytics to treat logs as non-authoritative (ignore sync logs)
FIRST_SYNC_DONE=1; export FIRST_SYNC_DONE
PH_VENDOR_ANALYTICS_START=$(_ts || echo 0)
post_purge_vendor_json="$(vendor_hash_json || true)"
echo "$post_purge_vendor_json" > .codex/cache/vendor_hash_post_purge.json 2>/dev/null || true
VENDOR_SET_HASH_AFTER="$(
JSON_IN="$post_purge_vendor_json" python - <<'PY'
import os, json
raw=os.environ.get("JSON_IN","").strip()
try:
    data=json.loads(raw) if raw else {}
    print(data.get("hash",""))
except Exception:
    print("")
PY
)"
VENDOR_SET_LIST_AFTER="$(
JSON_IN="$post_purge_vendor_json" python - <<'PY'
import os, json
raw=os.environ.get("JSON_IN","").strip()
try:
    data=json.loads(raw) if raw else {}
    print(" ".join(data.get("vendors",[])))
except Exception:
    print("")
PY
)"
if [[ -z "$VENDOR_SET_HASH_AFTER" && -n "$VENDOR_SET_LIST_AFTER" ]]; then
  VENDOR_SET_HASH_AFTER="$(printf "%s" "$VENDOR_SET_LIST_AFTER" | tr ' ' '\n' | LC_ALL=C sort | tr '\n' ';' | sha256sum | awk '{print $1}')"
fi
export VENDOR_SET_HASH_AFTER VENDOR_SET_LIST_AFTER

compute_recurrence(){
  local h="$1"
  local file="$CODEX_VENDOR_RECUR_HASH_FILE"
  mkdir -p "$(dirname "$file")"
  touch "$file"
  local max="${CODEX_VENDOR_REAPPEAR_WINDOW}"
  local count=0
  if grep -Fq "$h" "$file" 2>/dev/null; then
    count=$(grep -F "$h" "$file" | wc -l | tr -d ' ')
  fi
  (tail -n "$(( max - 1 ))" "$file" 2>/dev/null; echo "$h") | grep -v '^$' > "$file.tmp" || true
  mv "$file.tmp" "$file"
  echo "$count"
}
if [[ -n "$VENDOR_SET_HASH_AFTER" ]]; then
  prev_recur=$(compute_recurrence "$VENDOR_SET_HASH_AFTER")
  if (( prev_recur > 0 )); then
    VENDOR_RECURRENCE=1
    VENDOR_RECURRENCE_COUNT=$(( prev_recur + 1 ))
    case "$CODEX_VENDOR_RECURRENCE_WARN" in
      warn) record_warn "vendor_recurrence" "Vendor set recurrence hash=$VENDOR_SET_HASH_AFTER count=$VENDOR_RECURRENCE_COUNT list=$VENDOR_SET_LIST_AFTER";;
      info) log_info "Vendor recurrence hash=$VENDOR_SET_HASH_AFTER count=$VENDOR_RECURRENCE_COUNT";;
      fail) record_warn "vendor_recurrence" "Vendor recurrence escalated hash=$VENDOR_SET_HASH_AFTER count=$VENDOR_RECURRENCE_COUNT"; die "Vendor recurrence fail policy (hash=$VENDOR_SET_HASH_AFTER)";;
      silent) ;;
      *) record_warn "vendor_recurrence" "Vendor set recurrence hash=$VENDOR_SET_HASH_AFTER count=$VENDOR_RECURRENCE_COUNT";;
    esac
  else
    VENDOR_RECURRENCE_COUNT=1
    log_info "Vendor set first appearance (post-purge) hash=$VENDOR_SET_HASH_AFTER"
  fi
else
  log_info "Post-purge vendor set empty (no hash)."
fi
export VENDOR_RECURRENCE VENDOR_RECURRENCE_COUNT
PHASE_MARK PHASE_VENDOR_ANALYTICS "$PH_VENDOR_ANALYTICS_START"

# 16) Orphan Namespace Cleanup
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

# 17) Torch Verification
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
if [[ "$CODEX_FAST_TORCH_RECHECK" == "1" ]]; then
  python - <<'PY' >/dev/null 2>&1 || echo "[setup][WARN] torch fast recheck failed post"
import torch,sys
assert "+cpu" in torch.__version__
PY
fi

# 18) Pre-commit
if [[ -f .pre-commit-config.yaml && "$CODEX_ENSURE_PRECOMMIT" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  if ! command -v pre-commit >/dev/null 2>&1; then
    run "uv pip install --python \"$UV_PYTHON\" pre-commit || true"
  fi
  run "pre-commit install -f -t pre-commit -t pre-push -t prepare-commit-msg || true"
fi

# 19) LFS Large Blob Advisory
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

# 20) Cache Prune
if [[ "$CODEX_CACHE_PRUNE" == "1" && "$CODEX_OFFLINE" != "1" && $(command -v uv) ]]; then
  run "uv cache prune || true"
fi

# 21) Lock Hash
calc_lockhash(){ ( sha256sum uv.lock 2>/dev/null || true; sha256sum pyproject.toml 2>/dev/null || true ) | sha256sum | awk '{print $1}'; }
if [[ "$CODEX_SUMMARY_INCLUDE_HASH" == "1" ]]; then
  calc_lockhash > .codex/cache/setup.locksum
  log "Locksum: $(cat .codex/cache/setup.locksum)"
fi

# 22) Aggregate Warnings
if [[ "$CODEX_WARN_AGGREGATE" == "1" && ${#WARN_EVENTS[@]} -gt 0 ]]; then
  : >"$WARN_FILE"
  i=0
  for e in "${WARN_EVENTS[@]}"; do
    i=$((i+1))
    printf '[%d] %s\n' "$i" "$e" >>"$WARN_FILE"
  done
fi

# 23) Summary JSON
finalize_timings
export_phase_vars
pairs=(); for k in "${!WARN_CAT_COUNT[@]}"; do pairs+=("$k" "${WARN_CAT_COUNT[$k]}"); done; export PAIRS="${pairs[*]}"
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
allow_triton=os.getenv("CODEX_ALLOW_TRITON_CPU","1")=="1"
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
if allow_triton:
    res=[r for r in res if r!="triton"]
data={"torch_version":"(unknown)","cuda_build":False,"cuda_available":False,"gpu_residue":sorted(set(res))}
try:
    import torch
    data["torch_version"]=torch.__version__
    data["cuda_build"]=bool(getattr(getattr(torch,'version',None),'cuda',None))
    data["cuda_available"]=bool(getattr(torch,'cuda',None) and torch.cuda.is_available())
except Exception:
    pass
print(json.dumps(data))
PY
)
warn_count=$(wc -l <"$WARN_FILE" 2>/dev/null || echo 0)
fail_count=$(wc -l <"$FAIL_FILE" 2>/dev/null || echo 0)
env_digest=""
if [[ "$CODEX_ENV_DIGEST" == "1" ]]; then env_digest=$(pip freeze 2>/dev/null | LC_ALL=C sort | sha256sum | awk '{print $1}'); fi

python - <<PY
import json,os,pathlib
torch_info=json.loads('''$TORCH_INFO''')
summary={
 "mode":{
   "sync_groups":os.getenv("CODEX_SYNC_GROUPS"),
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
   "warn_on_lock_regen":os.getenv("CODEX_WARN_ON_LOCK_REGEN"),
   "env_digest_enabled":os.getenv("CODEX_ENV_DIGEST"),
   "heuristic_recover":os.getenv("CODEX_VENDOR_HEURISTIC_RECOVER"),
   "fallback_snapshot":os.getenv("CODEX_FALLBACK_SNAPSHOT"),
   "purge_output_sanitize":os.getenv("CODEX_PURGE_OUTPUT_SANITIZE"),
   "allow_triton_cpu":os.getenv("CODEX_ALLOW_TRITON_CPU"),
   "sync_fail_excerpt_lines":os.getenv("CODEX_SYNC_FAIL_EXCERPT_LINES"),
   "vendor_recurrence_warn":os.getenv("CODEX_VENDOR_RECURRENCE_WARN"),
   "vendor_reappear_window":os.getenv("CODEX_VENDOR_REAPPEAR_WINDOW"),
   "lock_scan_enable":os.getenv("CODEX_VENDOR_LOCK_SCAN_ENABLE"),
   "lock_prune":os.getenv("CODEX_VENDOR_ENFORCE_LOCK_PRUNE"),
   "lock_prune_dryrun":os.getenv("CODEX_VENDOR_ENFORCE_LOCK_PRUNE_DRYRUN"),
   "vendor_log_agg":os.getenv("CODEX_VENDOR_LOG_AGG")
 },
 "torch": torch_info,
 "counts":{
   "warnings": int("""$warn_count"""),
   "failed_commands": int("""$fail_count""")
 },
 "warnings_by_category": json.loads('''$warn_cat_json'''),
 "vendor_metrics":{
   "fallback_purged": os.getenv("FALLBACK_VENDOR_PURGED","0"),
   "fallback_reason": os.getenv("FALLBACK_REASON",""),
   "uninstalled_total": int(os.getenv("VENDOR_UNINSTALL_COUNT","0")),
   "relock_events": int(os.getenv("RELOCK_EVENTS","0")),
   "fallback_events": int(os.getenv("FALLBACK_EVENTS","0")),
   "vendor_purge_events": int(os.getenv("VENDOR_PURGE_EVENTS","0")),
   "lock_outdated_events": int(os.getenv("LOCK_OUTDATED_EVENTS","0")),
   "vendor_set_hash_before": os.getenv("VENDOR_SET_HASH_BEFORE",""),
   "vendor_set_list_before": os.getenv("VENDOR_SET_LIST_BEFORE",""),
   "vendor_set_hash_after": os.getenv("VENDOR_SET_HASH_AFTER",""),
   "vendor_set_list_after": os.getenv("VENDOR_SET_LIST_AFTER",""),
   "vendor_recurrence": os.getenv("VENDOR_RECURRENCE","0"),
   "vendor_recurrence_count": os.getenv("VENDOR_RECURRENCE_COUNT","0"),
   "vendor_set_class_before": os.getenv("VENDOR_SET_CLASS_BEFORE",""),
   "triton_allowed": os.getenv("CODEX_ALLOW_TRITON_CPU","1"),
   "lock_prune_action": os.getenv("LOCK_PRUNE_ACTION","none"),
   "lock_prune_lines_removed": int(os.getenv("LOCK_PRUNE_REMOVED","0"))
 },
 "lock_scan":{
   "before_count": int(os.getenv("LOCK_SCAN_GPU_BEFORE","0")),
   "after_count": int(os.getenv("LOCK_SCAN_GPU_AFTER","0")),
   "before_list": os.getenv("LOCK_GPU_LIST_BEFORE",""),
   "after_list": os.getenv("LOCK_GPU_LIST_AFTER","")
 },
 "timings":{
   "preinstall_s": int(os.getenv("PHASE_PREINSTALL","0")),
   "lock_chain_s": int(os.getenv("PHASE_LOCK","0")),
   "purge_s": int(os.getenv("PHASE_PURGE","0")),
   "vendor_analytics_s": int(os.getenv("PHASE_VENDOR_ANALYTICS","0")),
   "total_s": int(os.getenv("PHASE_TOTAL","0"))
 },
 "env_digest": """$env_digest"""
}
pathlib.Path(os.getenv("SUMMARY_JSON",".codex/cache/setup_summary.json")).write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
PY

if (( warn_count > 0 )); then
  log "Completed with warnings=$warn_count"
else
  log "Setup finished clean."
fi

# 24) Strict Residue Enforcement
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_FAIL_ON_GPU_RESIDUE" == "1" ]]; then
  if python - <<'PY'
import pkgutil,sys,importlib,os
allow_triton=os.getenv("CODEX_ALLOW_TRITON_CPU","1")=="1"
mods=[]
for m in pkgutil.iter_modules():
    n=m.name
    if n.startswith("nvidia-") or n in {"triton","torchtriton"}:
        try: importlib.import_module(n)
        except Exception: continue
        if allow_triton and n=="triton": continue
        mods.append(n)
sys.exit(0 if not mods else 7)
PY
  then :; else die "Residual vendor packages remain (strict)."; fi
fi

# 25) Recurrence Fail Policy
if [[ "$VENDOR_RECURRENCE" == "1" && "$CODEX_VENDOR_RECURRENCE_WARN" == "fail" ]]; then
  die "Vendor recurrence detected under fail policy (hash=$VENDOR_SET_HASH_AFTER count=$VENDOR_RECURRENCE_COUNT)."
fi

# 26) Strict Failed Command Gate
fail_count=$(wc -l <"$FAIL_FILE" 2>/dev/null || echo 0)
if (( fail_count > 0 )) && [[ "$STRICT_SETUP" == "1" ]]; then
  die "Failures detected and STRICT_SETUP=1"
fi

exit 0
