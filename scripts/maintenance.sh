#!/usr/bin/env bash
# Maintenance Rev5.3++ (Unified Final – Patch 4B: Fallback Reintegration + Metrics Integrity)
#
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
set -Eeuo pipefail

############################################
# 0) Flags
############################################
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

if [[ -z "${CODEX_FORCE_CPU:-}" ]]; then
  if [[ ",${CODEX_SYNC_GROUPS}," == *",gpu,"* ]]; then export CODEX_FORCE_CPU=0; else export CODEX_FORCE_CPU=1; fi
fi
[[ "$CODEX_DEBUG" == "1" ]] && set -x

############################################
# 1) Logging & Aggregation
############################################
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

_cmd_index=0
run(){
  local cmd="$*"; _cmd_index=$((_cmd_index+1))
  local start=$(date +%s)
  set +e; bash -lc "$cmd" > >(tee /tmp/codex_maint_cmd_out.$$) 2>&1; local ec=$?; set -e
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
    set +e; ( set +e; bash -lc "$cmd" ) > /tmp/codex_retry_out.$$ 2>&1; ec=$?
    set -e
    cat /tmp/codex_retry_out.$$ >>"$SYNC_LOG"
    if (( ec == 0 )); then log "OK(retry t=$attempt) $cmd"; return 0; fi
    if (( attempt >= max )); then return $ec; fi
    sleep $(( attempt * 2 ))
    attempt=$(( attempt + 1 ))
  done
}

############################################
# 2) Timings & Context
############################################
_ts(){ [[ "$CODEX_METRICS_TIMINGS" == "1" ]] || return 0; date +%s; }
PHASE_START_TOTAL=$(_ts || echo 0)
PHASE_SYNC=0 PHASE_PURGE=0 PHASE_TOTAL=0
PHASE_MARK(){ [[ "$CODEX_METRICS_TIMINGS" == "1" ]] || return 0; local var="$1" start="$2" end=$(_ts); printf -v "$var" "%s" "$(( end - start ))"; export "$var"; }
finalize_timings(){ if [[ "$CODEX_METRICS_TIMINGS" == "1" ]]; then local end=$(_ts); PHASE_TOTAL=$(( end - PHASE_START_TOTAL )); else PHASE_TOTAL=0; fi; export PHASE_TOTAL; }
export_phase_vars(){ export PHASE_SYNC PHASE_PURGE PHASE_TOTAL; }

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

############################################
# 3) Virtual Env
############################################
if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate || maybe_fail "Activate .venv failed"
else
  python3 -m venv .venv || maybe_fail "Create .venv failed"
  # shellcheck disable=SC1091
  source .venv/bin/activate || maybe_fail "Activate new .venv failed"
fi
export UV_PYTHON
UV_PYTHON="$(command -v python)"

############################################
# 4) Vendor Helper + Preflight
############################################
FIRST_SYNC_DONE=1; export FIRST_SYNC_DONE
VENDOR_HELPER_PY='
import os, pkgutil, re, sys, pathlib, subprocess, importlib
MODE=sys.argv[1]
ignore_root=os.getenv("CODEX_VENDOR_NAMESPACE_IGNORE","1")=="1"
sync_log=pathlib.Path(".codex/cache/uv_sync_maint.log")
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
    combo=set()
    combo |= {p for p in d if p.startswith("nvidia-") or p in {"triton","torchtriton"}}
    combo |= im
    combo |= lg
    if ignore_root:
        combo={c for c in combo if c!="nvidia"}
    valid={c for c in combo if c in {"triton","torchtriton"} or c.startswith("nvidia-")}
    print(" ".join(sorted(valid)))
elif MODE=="residue":
    res=set()
    res |= {p for p in d if p.startswith("nvidia-") or p in {"triton","torchtriton"}}
    res |= im
    if ignore_root:
        res={r for r in res if r!="nvidia"}
    print(" ".join(sorted(res)))
else:
    print("")
'
python - <<'PY' >/dev/null 2>&1 && log_info "[vendor-helper] preflight ok" || log_info "[vendor-helper] preflight failed (continuing)"
import json,hashlib
import json as _probe
PY

vendor_collect(){ python -c "$VENDOR_HELPER_PY" collect; }
vendor_residue(){ python -c "$VENDOR_HELPER_PY" residue; }

uv_uninstall_noninteractive(){
  [[ $# -eq 0 ]] && return 0
  if command -v uv >/dev/null 2>&1; then
    if command -v yes >/dev/null 2>&1; then yes | uv pip uninstall "$@" || true
    else printf 'y\n%.0s' {1..80} | uv pip uninstall "$@" || true
    fi
  else
    python -m pip uninstall -y "$@" || true
  fi
}

############################################
# 5) Pyproject Sanitize (+cpu)
############################################
if [[ -f pyproject.toml ]] && grep -qE 'torch==[0-9]+\.[0-9]+\.[0-9]+\+cpu' pyproject.toml; then
  cp pyproject.toml ".codex/cache/pyproject.toml.maint.pre_sanitize.$(date +%s)" || true
  sed -E -i 's/(torch==[0-9]+\.[0-9]+\.[0-9]+)\+cpu/\1/g' pyproject.toml
  rm -f uv.lock
  log_info "Sanitized '+cpu' suffix from pyproject torch spec."
fi

############################################
# 6) Torch Ensure (CPU baseline)
############################################
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  export PIP_INDEX_URL="https://download.pytorch.org/whl/cpu"
  export PIP_EXTRA_INDEX_URL="https://pypi.org/simple"
  run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu \"torch==${CODEX_TORCH_VERSION_BASE}\""
  unset PIP_INDEX_URL PIP_EXTRA_INDEX_URL || true
fi

############################################
# 7) Safe Lock / Sync + Relock Counting
############################################
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
RELOCK_EVENTS=0 FALLBACK_EVENTS=0 VENDOR_PURGE_EVENTS=0
VENDOR_UNINSTALL_COUNT=0 FALLBACK_VENDOR_PURGED=0
export RELOCK_EVENTS FALLBACK_EVENTS VENDOR_PURGE_EVENTS VENDOR_UNINSTALL_COUNT FALLBACK_VENDOR_PURGED

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
      record_warn "lock" "Regenerating lock (auto)."
    else
      log_info "Regenerating lock (auto)."
    fi
    cpu_constrained_lock || maybe_fail "Lock regeneration failed"
  fi
  if [[ "$CODEX_USE_LOCKED_SYNC" == "1" && -f uv.lock && $relock_needed -eq 0 ]]; then
    if ! run_retry_log 2 "uv sync --locked"; then
      log_info "Locked sync failed; regenerating."
      cpu_constrained_lock || maybe_fail "Relock failed"
      RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )); export RELOCK_EVENTS
      cpu_constrained_sync || maybe_fail "Sync after relock failed"
    fi
  else
    cpu_constrained_sync || maybe_fail "Sync failed"
  fi
}

# Consolidated purge helper
purge_and_measure(){
  local mode="$1"; shift
  local vendor_list="$1"
  [[ -z "$vendor_list" ]] && { log_info "No vendor packages for $mode purge."; return 0; }
  if [[ "$mode" == "fallback" && "$CODEX_WARN_ON_FALLBACK" == "1" ]]; then
    record_warn "fallback" "Fallback purge: $vendor_list"
  else
    log_info "$mode purge: removing: $vendor_list"
  fi
  local uninstall_output
  uninstall_output=$(uv_uninstall_noninteractive $vendor_list 2>&1 || true)
  uninstall_output=$(printf "%s" "$uninstall_output" | tr -d '\r')
  local purged_count
  purged_count=$(printf "%s" "$uninstall_output" | grep -c '^- ')
  if (( purged_count > 0 )); then
    VENDOR_UNINSTALL_COUNT=$(( VENDOR_UNINSTALL_COUNT + purged_count ))
    if [[ "$mode" == "fallback" ]]; then
      FALLBACK_EVENTS=$(( FALLBACK_EVENTS + 1 ))
      FALLBACK_VENDOR_PURGED=1
    else
      VENDOR_PURGE_EVENTS=$(( VENDOR_PURGE_EVENTS + 1 ))
    fi
    export VENDOR_UNINSTALL_COUNT FALLBACK_EVENTS VENDOR_PURGE_EVENTS FALLBACK_VENDOR_PURGED
  fi
  local RESIDUE
  RESIDUE="$(vendor_residue)"
  if [[ -n "$RESIDUE" ]]; then
    record_warn "vendor_residue" "Residual vendor distributions: $RESIDUE"
    [[ "$CODEX_FAIL_ON_GPU_RESIDUE" == "1" ]] && echo "RESIDUAL_VENDOR=$RESIDUE" >>"$FAIL_FILE"
  else
    log_info "$mode purge successful (no residue)."
  fi
}

PH_SYNC_START=$(_ts || echo 0)
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_SKIP_UV_SYNC" == "1" ]]; then
  log_info "Skipping uv sync (CODEX_SKIP_UV_SYNC=1)"
else
  if [[ "$CODEX_OFFLINE" != "1" && -f pyproject.toml && $(command -v uv) ]]; then
    safe_lock_sync
    # Fallback detection (vendor wheels)
    if [[ "$CODEX_FORCE_CPU" == "1" ]] && grep -E 'Downloading nvidia-|Downloading triton ' "$SYNC_LOG" >/dev/null 2>&1; then
      case "$CODEX_VENDOR_LOG_ONLY_POLICY" in
        ignore) log_info "Vendor wheels observed (ignored policy)";;
        warn)
          if [[ "$CODEX_WARN_ON_FALLBACK" == "1" ]]; then record_warn "vendor_detect" "Vendor wheels observed."
          else log_info "Vendor wheels observed."
          fi
          ;;
        purge)
          if [[ "$CODEX_ABORT_ON_GPU_PULL" == "1" ]]; then die "Aborting due to vendor wheels (abort mode)."; fi
          if [[ "$CODEX_LIGHTWEIGHT_CPU_FALLBACK" == "1" ]]; then
            local_vendors="$(vendor_collect)"
            if [[ -n "$local_vendors" ]]; then
              purge_and_measure "fallback" "$local_vendors"
              run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu --force-reinstall \"torch==${CODEX_TORCH_VERSION_BASE}\""
              export CODEX_CPU_MINIMAL=1
              if [[ "$CODEX_RELOCK_AFTER_VENDOR_PURGE" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
                log_info "Relocking after fallback purge."
                cpu_constrained_lock && RELOCK_EVENTS=$(( RELOCK_EVENTS + 1 )) && export RELOCK_EVENTS
                cpu_constrained_sync || maybe_fail "Sync after fallback relock failed"
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
PHASE_MARK PHASE_SYNC "$PH_SYNC_START"

############################################
# 8) Minimal augmentation
############################################
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_CPU_MINIMAL" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  run "uv pip install --python \"$UV_PYTHON\" --no-deps transformers tokenizers safetensors accelerate || true"
fi

############################################
# 9) Vendor Purge (primary) – skip if fallback executed
############################################
PH_PURGE_START=$(_ts || echo 0)
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_VENDOR_PURGE" == "1" && "$FALLBACK_VENDOR_PURGED" != "1" ]]; then
  VENDOR_LIST="$(vendor_collect)"
  printf "%s\n" "$VENDOR_LIST" > .codex/cache/vendor_seen_maint.txt 2>/dev/null || true
  if [[ -n "$VENDOR_LIST" ]]; then
    log_info "Vendor purge (primary) removing: $VENDOR_LIST"
    uninstall_output=$(uv_uninstall_noninteractive $VENDOR_LIST 2>&1)
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
# 10) Orphan Namespace Cleanup
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
# 11) Torch Verification
############################################
python - <<PY
import sys
try:
    import torch
    v=torch.__version__
    print("[torch] version", v)
    if "+cpu" not in v:
        print("[torch][WARN] wheel missing +cpu tag")
except Exception as e:
    print("[torch][ERROR] import failed:", e)
    sys.exit(2)
PY
if (( $? != 0 )) && [[ "$CODEX_OFFLINE" != "1" ]]; then
  if (( VENDOR_UNINSTALL_COUNT > 0 )); then
    log_info "Torch import failed post vendor changes; reinstalling."
    run "uv pip install --python \"$UV_PYTHON\" --index-url https://download.pytorch.org/whl/cpu --force-reinstall \"torch==${CODEX_TORCH_VERSION_BASE}\""
  else
    record_warn "torch_verify" "Torch import failed without prior vendor purge."
  fi
fi

############################################
# 12) Pre-commit Hooks
############################################
if [[ -f .pre-commit-config.yaml && "$CODEX_ENSURE_PRECOMMIT" == "1" && "$CODEX_OFFLINE" != "1" ]]; then
  if ! command -v pre-commit >/dev/null 2>&1; then
    run "uv pip install --python \"$UV_PYTHON\" pre-commit || true"
  fi
  run "pre-commit install -f -t pre-commit -t pre-push -t prepare-commit-msg || true"
fi

############################################
# 13) Optional Ops
############################################
if [[ "${ENV_SNAPSHOT:-0}" == "1" ]]; then
  mkdir -p artifacts/env
  python --version > artifacts/env/python_version.txt 2>/dev/null || true
  pip freeze > artifacts/env/pip_freeze.txt 2>/dev/null || true
fi
if [[ "${TYPECHECK:-0}" == "1" ]] && command -v mypy >/dev/null 2>&1; then
  run "mypy src --ignore-missing-imports || true"
fi
if [[ "${SMOKE:-0}" == "1" ]]; then
  run "python - <<'PY'
import pathlib
for p in ('src','services/api'):
    if pathlib.Path(p).exists(): print('[smoke] present', p)
print('[smoke] done')
PY"
fi

############################################
# 14) Cache Prune
############################################
if [[ "$CODEX_CACHE_PRUNE" == "1" && "$CODEX_OFFLINE" != "1" && $(command -v uv) ]]; then
  run "uv cache prune || true"
fi

############################################
# 15) Lock Hash
############################################
calc_lockhash(){ ( sha256sum uv.lock 2>/dev/null || true; sha256sum pyproject.toml 2>/dev/null || true ) | sha256sum | awk '{print $1}'; }
if [[ "$CODEX_SUMMARY_INCLUDE_HASH" == "1" ]]; then
  calc_lockhash > .codex/cache/maintenance.locksum
  log "Locksum: $(cat .codex/cache/maintenance.locksum)"
fi

############################################
# 16) Aggregate Warning Flush
############################################
if [[ "$CODEX_WARN_AGGREGATE" == "1" && ${#WARN_EVENTS[@]} -gt 0 ]]; then
  : >"$WARN_FILE"
  i=0; for e in "${WARN_EVENTS[@]}"; do i=$((i+1)); printf '[%d] %s\n' "$i" "$e" >>"$WARN_FILE"; done
fi

############################################
# 17) Summary JSON
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
env_digest=""
if [[ "$CODEX_ENV_DIGEST" == "1" ]]; then
  env_digest=$(pip freeze 2>/dev/null | LC_ALL=C sort | sha256sum | awk '{print $1}')
fi

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
   "env_digest_enabled":os.getenv("CODEX_ENV_DIGEST")
 },
 "torch": torch_info,
 "counts":{
   "warnings": int("""$warn_count"""),
   "failed_commands": int("""$fail_count""" )
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
   "sync_s": int(os.getenv("PHASE_SYNC","0")),
   "purge_s": int(os.getenv("PHASE_PURGE","0")),
   "total_s": int(os.getenv("PHASE_TOTAL","0"))
 },
 "env_digest": """$env_digest"""
}
pathlib.Path(os.getenv("SUMMARY_JSON",".codex/cache/maintenance_summary.json")).write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
PY

if (( warn_count > 0 )); then
  log "Maintenance finished with warnings=$warn_count"
else
  log "Maintenance finished clean."
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
  die "Failures occurred and STRICT_SETUP=1"
fi
exit 0
