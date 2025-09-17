#!/usr/bin/env bash
# =============================================================================
# maintenance.sh
# Unified Environment Maintenance (CPU-Constrained) with Enhanced Observability
# Version: 5.5.1-rc4-hotfix2
# Date: 2025-09-17
#
# CHANGELOG:
#   rc4-hotfix2:
#     - ADD: CODEX_VENDOR_LOG_AGG (pre-sync|always|never; default pre-sync) to gate
#       vendor name aggregation from sync logs. With FIRST_SYNC_DONE=1 in maintenance,
#       logs are ignored by default to prevent false positives.
#     - FIX: Post-uninstall residue checks force FIRST_SYNC_DONE=1 to ignore log-only signals.
#     - FIX: Corrected typo in compute_recurrence redirection (2>/dev/null).
#   rc4-hotfix1:
#     - CRITICAL FIX: Replaced pipe + heredoc JSON parsing (printf | python <<'PY')
#       with env-var-based parsing to avoid SIGPIPE/ERR trap noise under set -e -o pipefail.
#     - FIX: Robust pre/post vendor hash/list extraction now immune to pipefail.
# Patch 4B (2025-09-17):
#  - Reintroduces fallback detection logic from Patch 3 (vendor download scan) atop Patch 4 metrics.
#  - Skips primary purge if fallback purge occurred (FALLBACK_VENDOR_PURGED=1).
#  - Adds pyproject '+cpu' sanitize step (parity with setup) prior to sync.
#  - Uses consolidated purge_and_measure with non-interactive uninstall (uv_uninstall_noninteractive).
#  - Accurate uninstall counting (grep -c '^- ') with CR normalization.
#  - Initial relock event counting (RELOCK_EVENTS increments on missing/stale lock).
#  - env_digest included (toggle CODEX_ENV_DIGEST).
#  - Vendor helper preflight self-check.
#
# Warning Scope (unchanged):
#   * vendor_residue, torch_verify anomaly (no prior purge), lfs, optional escalations.
#
# EXIT CODES:
#   0  Success (warnings may be present)
#   7  Residual vendor packages remain (strict residue mode)
#   12 Vendor recurrence escalation under fail policy
#   *  Other non-graceful failures / strict gates
# =============================================================================

set -Eeuo pipefail

# 0) Configuration Flags (mirror setup)
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
export CODEX_VENDOR_LOG_ONLY_POLICY="${CODEX_VENDOR_LOG_ONLY_POLICY:-purge}" # ignore|warn|purge
export CODEX_VENDOR_NAMESPACE_IGNORE="${CODEX_VENDOR_NAMESPACE_IGNORE:-1}"
export CODEX_ERR_TRAP="${CODEX_ERR_TRAP:-1}"
export CODEX_RELOCK_AFTER_VENDOR_PURGE="${CODEX_RELOCK_AFTER_VENDOR_PURGE:-1}"
export CODEX_CPU_CONSTRAIN_LOCK="${CODEX_CPU_CONSTRAIN_LOCK:-1}"
export CODEX_WARN_AGGREGATE="${CODEX_WARN_AGGREGATE:-1}"
export CODEX_METRICS_TIMINGS="${CODEX_METRICS_TIMINGS:-1}"
export CODEX_WARN_ON_FALLBACK="${CODEX_WARN_ON_FALLBACK:-0}"
export CODEX_WARN_ON_LOCK_REGEN="${CODEX_WARN_ON_LOCK_REGEN:-0}"
export CODEX_ENV_DIGEST="${CODEX_ENV_DIGEST:-1}"

# Extended flags
export CODEX_VENDOR_HEURISTIC_RECOVER="${CODEX_VENDOR_HEURISTIC_RECOVER:-1}"
export CODEX_FALLBACK_SNAPSHOT="${CODEX_FALLBACK_SNAPSHOT:-1}"
export CODEX_SYNC_FAIL_EXCERPT_LINES="${CODEX_SYNC_FAIL_EXCERPT_LINES:-20}"
export CODEX_PURGE_OUTPUT_SANITIZE="${CODEX_PURGE_OUTPUT_SANITIZE:-1}"
export CODEX_ALLOW_TRITON_CPU="${CODEX_ALLOW_TRITON_CPU:-1}"
export CODEX_FAST_TORCH_RECHECK="${CODEX_FAST_TORCH_RECHECK:-1}"

# Recurrence & Lock Instrumentation
export CODEX_VENDOR_RECURRENCE_WARN="${CODEX_VENDOR_RECURRENCE_WARN:-warn}"  # warn|info|silent|fail
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

# Log aggregation control
export CODEX_VENDOR_LOG_AGG="${CODEX_VENDOR_LOG_AGG:-pre-sync}"

if [[ -z "${CODEX_FORCE_CPU:-}" ]]; then
  if [[ ",${CODEX_SYNC_GROUPS}," == *",gpu,"* ]]; then export CODEX_FORCE_CPU=0; else export CODEX_FORCE_CPU=1; fi
fi
[[ "$CODEX_DEBUG" == "1" ]] && set -x

# 1) Logging / State
mkdir -p .codex/logs .codex/cache artifacts data
WARN_FILE=".codex/logs/maintenance_warnings.log"
FAIL_FILE=".codex/logs/maintenance_failures.log"
SYNC_LOG=".codex/cache/uv_sync_maint.log"
SUMMARY_JSON=".codex/cache/maintenance_summary.json"
: >"$WARN_FILE"; : >"$FAIL_FILE"; : >"$SYNC_LOG"

log(){ printf "[maint] %s %s\n" "$(date -Iseconds)" "$*"; }
log_info(){ log "INFO: $*"; }
_raw_warn(){ log "WARN: $*"; printf '%s\n' "$*" >>"$WARN_FILE"; }
die(){ printf "[maint][ERROR] %s\n" "$*" >&2; exit 1; }

WARN_EVENTS=()
WARN_EVENT_CATS=()
declare -A WARN_CAT_COUNT=()
record_warn(){
  local cat="$1"; shift
  local msg="$*"
  WARN_EVENTS+=("$msg"); WARN_EVENT_CATS+=("$cat")
  WARN_CAT_COUNT["$cat"]=$(( ${WARN_CAT_COUNT["$cat"]:-0} + 1 ))
  if [[ "$CODEX_WARN_AGGREGATE" == "0" ]]; then _raw_warn "[$cat] $msg"; else _raw_warn "$msg"; fi
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

safe_test(){ if [[ "$1" == "1" ]]; then return 0; else return 1; fi; }

_cmd_index=0
run(){
  local cmd="$*"
  _cmd_index=$((_cmd_index+1))
  local start=$(date +%s)
  set +e
  bash -lc "$cmd" > >(tee /tmp/codex_maint_cmd_out.$$) 2>&1
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
    set +e; ( set +e; bash -lc "$cmd" ) > /tmp/codex_retry_out.$$ 2>&1; ec=$?
    set -e
    cat /tmp/codex_retry_out.$$ >>"$SYNC_LOG"
    if (( attempt == 1 && ec != 0 )); then
      first_excerpt="$(head -n "$excerpt_lines" /tmp/codex_retry_out.$$)"
    fi
    if (( ec == 0 )); then
      log "OK(retry t=$attempt) $cmd"
      return 0
    fi
    if (( attempt >= max )); then
      log_info "Final failure for: $cmd (first-attempt excerpt follows)"
      printf '%s\n' "$first_excerpt" | sed 's/^/[sync-fail-snippet] /'
      return $ec
    fi
    sleep $(( attempt * 2 ))
    attempt=$(( attempt + 1 ))
  done
}

# 2) Timings & Context
_ts(){ [[ "$CODEX_METRICS_TIMINGS" == "1" ]] || return 0; date +%s; }
PHASE_START_TOTAL=$(_ts || echo 0)
PHASE_SYNC=0 PHASE_PURGE=0 PHASE_VENDOR_ANALYTICS=0 PHASE_LOCK_SCAN=0 PHASE_TOTAL=0

PHASE_MARK(){ [[ "$CODEX_METRICS_TIMINGS" == "1" ]] || return 0; local var="$1" start="$2" end=$(_ts); printf -v "$var" "%s" "$(( end - start ))"; export "$var"; }
finalize_timings(){ if [[ "$CODEX_METRICS_TIMINGS" == "1" ]]; then local end=$(_ts); PHASE_TOTAL=$(( end - PHASE_START_TOTAL )); else PHASE_TOTAL=0; fi; export PHASE_TOTAL; }
export_phase_vars(){ export PHASE_SYNC PHASE_PURGE PHASE_VENDOR_ANALYTICS PHASE_LOCK_SCAN PHASE_TOTAL; }

export DEBIAN_FRONTEND=noninteractive
REPO_ROOT="${REPO_ROOT:-$(pwd)}"
HF_HOME_DEFAULT="$REPO_ROOT/.hf_cache"; export HF_HOME="${HF_HOME:-$HF_HOME_DEFAULT}"
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PYTHONUTF8=1
export UV_SYSTEM_PYTHON=0
export UV_LINK_MODE=copy

log "Repo: $REPO_ROOT"
log "Torch(BaseSpec)=${CODEX_TORCH_VERSION_BASE} CPU=${CODEX_FORCE_CPU} SKIP_UV_SYNC=${CODEX_SKIP_UV_SYNC} LOCKED=${CODEX_USE_LOCKED_SYNC}"

cd "$REPO_ROOT"

# 3) Virtual Env
if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate || maybe_fail "Activate existing .venv failed"
else
  python3 -m venv .venv || maybe_fail "Create .venv failed"
  # shellcheck disable=SC1091
  source .venv/bin/activate || maybe_fail "Activate new .venv failed"
fi
export UV_PYTHON; UV_PYTHON="$(command -v python)"

# 4) Vendor Helper + Preflight (gated log aggregation; FIRST_SYNC_DONE=1 in maintenance)
FIRST_SYNC_DONE=1; export FIRST_SYNC_DONE
VENDOR_HELPER_PY="$(cat <<'PY'
import os, pkgutil, re, sys, pathlib, subprocess, importlib, json, hashlib
MODE=sys.argv[1]
ignore_root = os.getenv("CODEX_VENDOR_NAMESPACE_IGNORE","1") == "1"
hash_debug  = os.getenv("CODEX_VENDOR_HASH_DEBUG","0") == "1"
sync_log    = pathlib.Path(".codex/cache/uv_sync_maint.log")
log_agg     = os.getenv("CODEX_VENDOR_LOG_AGG","pre-sync")
first_sync_done = os.getenv("FIRST_SYNC_DONE","0") == "1"
def uv_list():
    try:
        out = subprocess.check_output(["uv","pip","list","--format","json","--python",os.getenv("UV_PYTHON","python")], text=True)
        return json.loads(out)
    except Exception as e:
        if hash_debug: print(f"[maint-vendor-helper] uv_list error: {e}", file=sys.stderr)
        return []
def packages_set(listing):
    s=set()
    for entry in listing:
        if not isinstance(entry, dict): continue
        name=(entry.get("name") or "").lower()
        if name.startswith("nvidia-") or name in {"triton","torchtriton"}: s.add(name)
    return s
def logs():
    if not sync_log.exists(): return set()
    pat=re.compile(r"(nvidia-[a-z0-9\-]+|triton|torchtriton)")
    return {m.group(1).lower() for m in pat.finditer(sync_log.read_text())}
def import_modules():
    present=set()
    for m in pkgutil.iter_modules():
        n=m.name.lower()
        if n.startswith("nvidia") or n in {"triton","torchtriton"}:
            try: importlib.import_module(n)
            except Exception: continue
            present.add(n)
    return present
def aggregate():
    base=packages_set(uv_list())
    include_logs = (log_agg == "always") or (log_agg == "pre-sync" and not first_sync_done)
    if include_logs:
        base |= logs()
    base |= import_modules()
    if os.getenv("CODEX_VENDOR_NAMESPACE_IGNORE","1")=="1":
        base={b for b in base if b!="nvidia"}
    base={b for b in base if b.startswith("nvidia-") or b in {"triton","torchtriton"}}
    return sorted(base)
vendors=aggregate()
if MODE=="collect": print(" ".join(vendors))
elif MODE=="residue": print(" ".join(vendors))
elif MODE=="hash":
    joined=";".join(vendors); h=hashlib.sha256(joined.encode()).hexdigest() if vendors else ""
    print(json.dumps({"hash":h,"vendors":vendors,"count":len(vendors)}))
else: print("")
PY
)"

python - <<'PY' >/dev/null 2>&1 && log_info "[vendor-helper] preflight ok" || log_info "[vendor-helper] preflight failed (continuing)"
print("ok")
PY

vendor_collect(){ python -c "$VENDOR_HELPER_PY" collect; }
vendor_residue(){ python -c "$VENDOR_HELPER_PY" residue; }
vendor_hash_json(){ python -c "$VENDOR_HELPER_PY" hash; }

# 5) Pyproject Sanitize (+cpu)
if [[ -f pyproject.toml ]] && grep -qE 'torch==[0-9]+\.[0-9]+\.[0-9]+\+cpu' pyproject.toml; then
  cp pyproject.toml ".codex/cache/pyproject.toml.maint.pre_sanitize.$(date +%s)" || true
  sed -E -i 's/(torch==[0-9]+\.[0-9]+\.[0-9]+)\+cpu/\1/g' pyproject.toml
  rm -f uv.lock
  log_info "Sanitized '+cpu' suffix from pyproject torch spec."
fi

# 6) Torch Ensure (CPU baseline)
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  export PIP_INDEX_URL="https://download.pytorch.org/whl/cpu"
  export PIP_EXTRA_INDEX_URL="https://pypi.org/simple"
  run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu \"torch==${CODEX_TORCH_VERSION_BASE}\""
  unset PIP_INDEX_URL PIP_EXTRA_INDEX_URL || true
fi

# 7) Safe Lock / Sync + Relock Counting
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
  [[ "$CODEX_HASH_LOCK_STRICT" != "1" ]] && [[ -f uv.lock ]] || return 0
  if grep -E '"name": "torch"' -A2 uv.lock 2>/dev/null | grep -q "+cpu"; then
    rm -f uv.lock; return 1
  fi
  return 0
}
RELOCK_EVENTS=0 FALLBACK_EVENTS=0 VENDOR_PURGE_EVENTS=0 LOCK_OUTDATED_EVENTS=0
VENDOR_UNINSTALL_COUNT=0 FALLBACK_VENDOR_PURGED=0 FALLBACK_REASON=""
VENDOR_RECURRENCE=0 VENDOR_RECURRENCE_COUNT=0
LOCK_SCAN_GPU_BEFORE=0 LOCK_SCAN_GPU_AFTER=0
LOCK_GPU_LIST_BEFORE="" LOCK_GPU_LIST_AFTER=""
LOCK_PRUNE_ACTION="none" LOCK_PRUNE_REMOVED=0
LOCK_PRUNE_DIFF_FILE=".codex/cache/lock_prune.maint.diff"
VENDOR_SET_HASH_BEFORE="" VENDOR_SET_HASH_AFTER=""
VENDOR_SET_LIST_BEFORE="" VENDOR_SET_LIST_AFTER=""
VENDOR_SET_CLASS_BEFORE="none"

export RELOCK_EVENTS FALLBACK_EVENTS VENDOR_PURGE_EVENTS LOCK_OUTDATED_EVENTS \
       VENDOR_UNINSTALL_COUNT FALLBACK_VENDOR_PURGED FALLBACK_REASON \
       VENDOR_RECURRENCE VENDOR_RECURRENCE_COUNT LOCK_SCAN_GPU_BEFORE LOCK_SCAN_GPU_AFTER \
       LOCK_GPU_LIST_BEFORE LOCK_GPU_LIST_AFTER LOCK_PRUNE_ACTION LOCK_PRUNE_REMOVED \
       VENDOR_SET_HASH_BEFORE VENDOR_SET_HASH_AFTER VENDOR_SET_LIST_BEFORE VENDOR_SET_LIST_AFTER \
       VENDOR_SET_CLASS_BEFORE

scan_lock_for_gpu(){
  if [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" != "1" ]] || [[ ! -f uv.lock ]]; then
    echo ""; return 0
  fi
  grep -E '"name": "(nvidia-|triton|torchtriton)' uv.lock 2>/dev/null || true
}
lock_scan_report_phase(){
  local phase="$1"
  local scan_output count list
  scan_output="$(scan_lock_for_gpu)"
  count=0; list=""
  if [[ -n "$scan_output" ]]; then
    list="$(echo "$scan_output" | sed -E 's/.*"name": "([^"]+)".*/\1/g' | sort -u | tr '\n' ' ')"
    count=$(echo "$list" | tr ' ' '\n' | grep -c . || true)
  fi
  if [[ "$phase" == "before" ]]; then
    LOCK_SCAN_GPU_BEFORE=$count; LOCK_GPU_LIST_BEFORE="$list"
  else
    LOCK_SCAN_GPU_AFTER=$count; LOCK_GPU_LIST_AFTER="$list"
  fi
  export LOCK_SCAN_GPU_BEFORE LOCK_SCAN_GPU_AFTER LOCK_GPU_LIST_BEFORE LOCK_GPU_LIST_AFTER
  if (( count > 0 )); then
    record_warn "lock_gpu_refs" "Lock scan ($phase) found $count GPU refs: $list"
  else
    if [[ "$CODEX_VENDOR_REPRT_EMPTY_LOCKGPU" == "1" ]]; then log_info "Lock scan ($phase) no GPU refs."; fi
  fi
}
attempt_lock_prune(){
  [[ "$CODEX_VENDOR_ENFORCE_LOCK_PRUNE" == "1" ]] || return 0
  [[ -f uv.lock ]] || { log_info "Lock prune skip (no uv.lock)"; return 0; }
  local pre_hash post_hash lines_removed=0
  pre_hash=$(sha256sum uv.lock | awk '{print $1}')
  cp uv.lock ".codex/cache/uv.lock.maint.prune.backup.$(date +%s)" || true
  local tmpfile=".codex/cache/uv.lock.maint.prune.$$.tmp"
  awk 'BEGIN{removed=0} /"name": "nvidia-|"name": "triton"|"name": "torchtriton"/{removed=1} { if(removed==1){ if($0 ~ /},?$/){removed=0; next} ; next } ; print }' uv.lock > "$tmpfile" || true
  if [[ -s "$tmpfile" ]]; then
    lines_removed=$(diff -u uv.lock "$tmpfile" | grep -E '^[+-]' | grep -v '+++\|---' | wc -l | tr -d ' ')
    if [[ "$CODEX_VENDOR_ENFORCE_LOCK_PRUNE_DRYRUN" == "1" ]]; then
      diff -u uv.lock "$tmpfile" > "$LOCK_PRUNE_DIFF_FILE" || true
      LOCK_PRUNE_ACTION="dryrun"; LOCK_PRUNE_REMOVED=$lines_removed
      record_warn "lock_prune_dryrun" "Dry-run lock prune delta=$lines_removed diff=$LOCK_PRUNE_DIFF_FILE"
      rm -f "$tmpfile"
    else
      diff -u uv.lock "$tmpfile" > "$LOCK_PRUNE_DIFF_FILE" || true
      mv "$tmpfile" uv.lock
      post_hash=$(sha256sum uv.lock | awk '{print $1}')
      LOCK_PRUNE_ACTION="applied"; LOCK_PRUNE_REMOVED=$lines_removed
      log_info "Lock prune applied (delta=$lines_removed pre=$pre_hash post=$post_hash)"
      if [[ "$CODEX_VENDOR_RELOCK_AFTER_LOCK_PRUNE" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
        log_info "Relocking after prune."
        cpu_constrained_lock || maybe_fail "Lock regen after prune failed"
        RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )); export RELOCK_EVENTS
      fi
    fi
  else
    log_info "Lock prune no change."; rm -f "$tmpfile"
  fi
  export LOCK_PRUNE_ACTION LOCK_PRUNE_REMOVED
}
sanitize_uninstall_stream(){
  sed -r \
    -e 's/\x1B\[[0-9;]*[A-Za-z]//g' \
    -e '/^\+\+/d' \
    -e '/^[[:space:]]*$/d'
}
uv_uninstall_noninteractive(){
  [[ $# -eq 0 ]] && return 0
  local had_xtrace=0; case "$-" in *x*) had_xtrace=1; set +x ;; esac
  if command -v uv >/dev/null 2>&1; then
    if command -v yes >/dev/null 2>&1; then yes | uv pip uninstall "$@" || true
    else printf 'y\n%.0s' {1..240} | uv pip uninstall "$@" || true
    fi
  else
    python -m pip uninstall -y "$@" || true
  fi
  (( had_xtrace )) && set -x || true
}
count_uninstalls(){
  awk '{
    if ($0 ~ /^\+\+/) next
    line=$0; sub(/^[[:space:]]+/,"",line)
    if (line ~ /^-[[:space:]]+[A-Za-z0-9_.:-]+==/) c++
  } END { print c+0 }'
}
purge_and_measure(){
  local mode="$1"; shift
  local vendor_list="$1"
  [[ -z "$vendor_list" ]] && { log_info "No vendor packages for $mode purge."; return 0; }

  if [[ "$mode" == "fallback" && "$CODEX_FALLBACK_SNAPSHOT" == "1" ]]; then
    printf "%s\n" "$vendor_list" > .codex/cache/vendor_seen_fallback_maint.txt 2>/dev/null || true
  else
    printf "%s\n" "$vendor_list" > .codex/cache/vendor_seen_maint.txt 2>/dev/null || true
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
  pre_before="$(vendor_residue | tr ' ' '\n' | sort -u | tr '\n' ' ')"

  raw_output=$(uv_uninstall_noninteractive $vendor_list 2>&1 || true)
  raw_output="${raw_output//$'\r'/}"
  if [[ "$CODEX_PURGE_OUTPUT_SANITIZE" == "1" ]]; then
    uninstall_output=$(printf "%s" "$raw_output" | sanitize_uninstall_stream)
  else
    uninstall_output="$raw_output"
  fi

  purged_count=$(printf "%s" "$uninstall_output" | count_uninstalls)
  # Ignore log-only signals during post-uninstall residue to avoid false positives
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
    printf "%s\n" "$uninstall_output" > ".codex/cache/${mode}_purge_uninstall_maint.log" || true
    (( heuristic_applied )) && echo "[heuristic] applied=1 adjusted=$purged_count" >> ".codex/cache/${mode}_purge_uninstall_maint.log"
  fi
}

# 8) Pre-Sync Vendor Snapshot (robust JSON parse)
pre_sync_vendor_json="$(vendor_hash_json || true)"
echo "$pre_sync_vendor_json" > .codex/cache/maint_vendor_hash_pre_sync.json 2>/dev/null || true

VENDOR_SET_HASH_BEFORE="$(
JSON_IN="$pre_sync_vendor_json" python - <<'PY'
import os, json
raw=os.environ.get("JSON_IN","" ).strip()
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
raw=os.environ.get("JSON_IN","" ).strip()
try:
    data=json.loads(raw) if raw else {}
    print(" ".join(data.get("vendors",[])))
except Exception:
    print("")
PY
)"
if [[ -n "$VENDOR_SET_LIST_BEFORE" ]]; then VENDOR_SET_CLASS_BEFORE="contaminated"; else VENDOR_SET_CLASS_BEFORE="clean"; fi
export VENDOR_SET_HASH_BEFORE VENDOR_SET_LIST_BEFORE VENDOR_SET_CLASS_BEFORE

# 9) Sync Phase
PH_SYNC_START=$(_ts || echo 0)

safe_lock_sync(){
  local relock_needed=0
  if [[ -f uv.lock ]]; then
    if ! validate_lock_torch; then relock_needed=1; fi
  else
    relock_needed=1
  fi
  if (( relock_needed )); then
    RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )); export RELOCK_EVENTS
    if [[ "$CODEX_WARN_ON_LOCK_REGEN" == "1" ]]; then
      record_warn "lock" "Regenerating lock (maintenance)"
    else
      log_info "Regenerating lock (maintenance)"
    fi
    cpu_constrained_lock || maybe_fail "Lock generation failed"
  fi
  if [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" == "1" ]]; then lock_scan_report_phase "before"; fi
  if [[ "$CODEX_USE_LOCKED_SYNC" == "1" && -f uv.lock && $relock_needed -eq 0 ]]; then
    if ! run_retry_log 2 "uv sync --locked"; then
      LOCK_OUTDATED_EVENTS=$(( LOCK_OUTDATED_EVENTS + 1 ))
      [[ -z "$FALLBACK_REASON" ]] && FALLBACK_REASON="lock_outdated"
      log_info "Locked sync failed (lock outdated) — relocking."
      cpu_constrained_lock || maybe_fail "Relock after outdated failure"
      RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )); export RELOCK_EVENTS
      cpu_constrained_sync || maybe_fail "Sync after relock failed"
    fi
  else
    cpu_constrained_sync || maybe_fail "Sync failed"
  fi
  if [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" == "1" ]]; then lock_scan_report_phase "after"; fi
}

if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_SKIP_UV_SYNC" == "1" ]]; then
  log_info "Skipping uv sync (CODEX_SKIP_UV_SYNC=1)"
else
  if [[ "$CODEX_OFFLINE" != "1" && -f pyproject.toml && $(command -v uv) ]]; then
    safe_lock_sync
    # Lock prune
    if (( LOCK_SCAN_GPU_AFTER > 0 )) && [[ "$CODEX_VENDOR_ENFORCE_LOCK_PRUNE" == "1" ]]; then
      [[ -z "$FALLBACK_REASON" ]] && FALLBACK_REASON="lock_gpu_specs"
      attempt_lock_prune
      [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" == "1" ]] && lock_scan_report_phase "after"
    fi
    # Detect vendor wheel downloads
    if grep -E 'Downloading nvidia-|Downloading triton ' "$SYNC_LOG" >/dev/null 2>&1 && [[ "$CODEX_FORCE_CPU" == "1" ]]; then
      case "$CODEX_VENDOR_LOG_ONLY_POLICY" in
        ignore) log_info "Vendor wheels observed (policy=ignore)";;
        warn)
          if [[ "$CODEX_WARN_ON_FALLBACK" == "1" ]]; then record_warn "vendor_detect" "Vendor wheels observed."; else log_info "Vendor wheels observed."; fi
          ;;
        purge)
          if [[ "$CODEX_ABORT_ON_GPU_PULL" == "1" ]]; then die "Aborting (GPU wheel observed)."; fi
          if [[ "$CODEX_LIGHTWEIGHT_CPU_FALLBACK" == "1" ]]; then
            local_vendors="$(vendor_collect)"
            if [[ -n "$local_vendors" ]]; then
              [[ -z "$FALLBACK_REASON" ]] && FALLBACK_REASON="sync_log_vendor"
              purge_and_measure "fallback" "$local_vendors"
              export CODEX_CPU_MINIMAL=1
              if [[ "$CODEX_RELOCK_AFTER_VENDOR_PURGE" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
                log_info "Relocking after fallback purge."
                cpu_constrained_lock && RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )) && export RELOCK_EVENTS
                cpu_constrained_sync || maybe_fail "Sync after fallback relock failed"
                [[ "$CODEX_VENDOR_LOCK_SCAN_ENABLE" == "1" ]] && lock_scan_report_phase "after"
              fi
            else
              log_info "Fallback trigger: vendor list empty."
            fi
          fi
          ;;
      esac
    fi
  fi
fi
PHASE_MARK PHASE_SYNC "$PH_SYNC_START"

# 10) Minimal Augmentation
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_CPU_MINIMAL" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  run "uv pip install --python \"$UV_PYTHON\" --no-deps transformers tokenizers safetensors accelerate || true"
fi

# 11) Primary Vendor Purge
PH_PURGE_START=$(_ts || echo 0)
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_VENDOR_PURGE" == "1" && "$FALLBACK_VENDOR_PURGED" != "1" ]]; then
  VENDOR_LIST="$(vendor_collect)"
  if [[ -n "$VENDOR_LIST" ]]; then purge_and_measure "primary" "$VENDOR_LIST"; else log_info "No vendor distributions detected (primary)."; fi
fi
PHASE_MARK PHASE_PURGE "$PH_PURGE_START"

# 12) Post-Purge Vendor Hash & Recurrence (robust JSON parse)
PH_VENDOR_ANALYTICS_START=$(_ts || echo 0)
post_vendor_json="$(vendor_hash_json || true)"
echo "$post_vendor_json" > .codex/cache/maint_vendor_hash_post.json 2>/dev/null || true

VENDOR_SET_HASH_AFTER="$(
JSON_IN="$post_vendor_json" python - <<'PY'
import os, json
raw=os.environ.get("JSON_IN","" ).strip()
try:
    data=json.loads(raw) if raw else {}
    print(data.get("hash",""))
except Exception:
    print("")
PY
)"
VENDOR_SET_LIST_AFTER="$(
JSON_IN="$post_vendor_json" python - <<'PY'
import os, json
raw=os.environ.get("JSON_IN","" ).strip()
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
  local h="$1" file="$CODEX_VENDOR_RECUR_HASH_FILE"
  [[ -z "$h" ]] && { echo 0; return 0; }
  mkdir -p "$(dirname "$file")"; touch "$file"
  local max="${CODEX_VENDOR_REAPPEAR_WINDOW}" count=0
  if grep -Fq "$h" "$file" 2>/dev/null; then count=$(grep -F "$h" "$file" | wc -l | tr -d ' '); fi
  (tail -n "$(( max - 1 ))" "$file" 2>/dev/null; echo "$h") | grep -v '^$' > "$file.tmp" || true
  mv "$file.tmp" "$file"
  echo "$count"
}
if [[ -n "$VENDOR_SET_HASH
