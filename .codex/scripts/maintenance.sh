#!/usr/bin/env bash
# .codex/scripts/maintenance.sh
# Deterministic maintenance script aligned with setup.sh CPU/GPU reconciliation logic.

set -Eeuo pipefail

if [[ "${CODEX_DEBUG:-0}" == "1" ]]; then
  set -x
fi

GRACEFUL="${CODEX_GRACEFUL:-1}"
STRICT_SETUP="${CODEX_STRICT_SETUP:-0}"
SYNC_GROUPS="${CODEX_SYNC_GROUPS:-base,cpu}"
OFFLINE="${CODEX_OFFLINE:-0}"
ENSURE_PRECOMMIT="${CODEX_ENSURE_PRECOMMIT:-1}"
FAIL_ON_GPU_RESIDUE="${CODEX_FAIL_ON_GPU_RESIDUE:-0}"
TORCH_VERSION="${CODEX_TORCH_VERSION:-2.8.0+cpu}"
TORCH_INDEX_CPU="${CODEX_TORCH_INDEX_CPU:-https://download.pytorch.org/whl/cpu}"

mkdir -p .codex/logs .codex/cache
WARN_LOG=".codex/logs/maintenance_warnings.log"
FAIL_LOG=".codex/logs/command_failures.log"
SUMMARY_FILE=".codex/cache/maintenance_summary.json"
: >"${WARN_LOG}"
: >"${FAIL_LOG}"

COMMAND_FAILURES=0
SUMMARY_BUFFER=""
SUMMARY_LINES=()
CURRENT_SECTION=""
SECTION_START=0
SYNC_TOKENS=()
WANT_CPU=0
WANT_GPU=0
FORCE_CPU=0
GPU_PRESENT=0
GPU_PACKAGES=()
SKIPPED_PACKAGES_STR=""
LOCK_DIGEST=""
NEED_SYNC=1

log()  { printf "[maint] %s %s\n" "$(date -Iseconds)" "$*"; }
warn() { log "WARN: $*"; printf "%s\n" "$*" >>"${WARN_LOG}"; }
die()  { printf "[maint][ERROR] %s\n" "$*" >&2; exit 1; }

maybe_fail() {
  local msg="$1"
  if [[ "$GRACEFUL" == "1" && "$STRICT_SETUP" == "0" ]]; then
    warn "$msg — continuing (GRACEFUL=1)"
  else
    die "$msg"
  fi
}

cmd_to_string() {
  local str
  if (( $# == 0 )); then
    printf ''
    return
  fi
  printf -v str '%q ' "$@"
  printf '%s' "${str% }"
}

run() {
  local cmd="$*"
  log "\$ $cmd"
  set +e
  bash -lc "$cmd"
  local ec=$?
  set -e
  if (( ec != 0 )); then
    COMMAND_FAILURES=$((COMMAND_FAILURES + 1))
    printf "[maint][ERROR] Command failed (exit %s): %s\n" "$ec" "$cmd" | tee -a "${FAIL_LOG}" >&2
    maybe_fail "Command failed (exit $ec): $cmd"
  fi
}

dequote_once() {
  local s="$1"
  case "$s" in
    \"*\"|\'*\') printf %s "${s:1:${#s}-2}";;
    *)           printf %s "$s";;
  esac
}

section() {
  local name="$*"
  if [[ -n "$CURRENT_SECTION" ]]; then
    local elapsed=$(( $(date +%s) - SECTION_START ))
    log "--- Completed ${CURRENT_SECTION} in ${elapsed}s"
  fi
  CURRENT_SECTION="$name"
  SECTION_START=$(date +%s)
  log "=== $CURRENT_SECTION ==="
}

finish_sections() {
  if [[ -n "$CURRENT_SECTION" ]]; then
    local elapsed=$(( $(date +%s) - SECTION_START ))
    log "--- Completed ${CURRENT_SECTION} in ${elapsed}s"
    CURRENT_SECTION=""
  fi
}

record_summary() {
  local key="$1"
  local value="$2"
  SUMMARY_BUFFER+="${key}\t${value}\n"
}

append_summary_line() {
  SUMMARY_LINES+=("$1")
}

write_summary_file() {
  export SUMMARY_BUFFER
  python3 - "$SUMMARY_FILE" <<'PY'
import json, os, sys, pathlib
path = pathlib.Path(sys.argv[1])
buf = os.environ.get("SUMMARY_BUFFER", "")
entries = {}
for line in buf.splitlines():
    if "\t" not in line:
        continue
    key, value = line.split("\t", 1)
    entries[key] = value
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n")
print(f"[maint] Summary JSON saved to {path} ({len(entries)} fields)")
PY
}

finalize() {
  local ec=$1
  trap - EXIT
  finish_sections
  record_summary "command_failures" "$COMMAND_FAILURES"
  record_summary "exit_code" "$ec"
  write_summary_file
  if ((${#SUMMARY_LINES[@]})); then
    log "Summary:"
    local line
    for line in "${SUMMARY_LINES[@]}"; do
      log "  - $line"
    done
  fi
  exit "$ec"
}

trap 'finalize $?' EXIT

export DEBIAN_FRONTEND=noninteractive
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PYTHONUTF8=1
export UV_SYSTEM_PYTHON=0
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"

setup_context() {
  section "Preparing environment context"
  local raw_root="${REPO_ROOT:-$(pwd)}"
  local resolved="$(dequote_once "$raw_root")"
  case "$resolved" in
    /*) REPO_ROOT="$resolved" ;;
    *)  REPO_ROOT="$(pwd)" ;;
  esac
  cd "$REPO_ROOT"
  export REPO_ROOT
  export HF_HOME="${HF_HOME:-${REPO_ROOT}/.hf_cache}"
  mkdir -p "$REPO_ROOT/artifacts" "$REPO_ROOT/data" "$HF_HOME"
  log "Repo root: $REPO_ROOT"
  log "HF_HOME: $HF_HOME"
  record_summary "repo_root" "$REPO_ROOT"
  record_summary "hf_home" "$HF_HOME"
  append_summary_line "Repository: $REPO_ROOT"
}

parse_sync_groups() {
  local raw token trimmed
  IFS=',' read -r -a raw <<<"$SYNC_GROUPS"
  SYNC_TOKENS=()
  for token in "${raw[@]}"; do
    trimmed="${token//[[:space:]]/}"
    [[ -n "$trimmed" ]] && SYNC_TOKENS+=("$trimmed")
  done
  WANT_CPU=0
  WANT_GPU=0
  for token in "${SYNC_TOKENS[@]}"; do
    [[ "$token" == "cpu" ]] && WANT_CPU=1
    [[ "$token" == "gpu" ]] && WANT_GPU=1
  done
  if [[ -n "${CODEX_FORCE_CPU:-}" ]]; then
    if [[ "${CODEX_FORCE_CPU}" == "1" ]]; then
      FORCE_CPU=1
    else
      FORCE_CPU=0
    fi
  else
    FORCE_CPU=$(( WANT_GPU == 0 ? 1 : 0 ))
  fi
  record_summary "sync_groups" "$SYNC_GROUPS"
  record_summary "want_cpu" "$WANT_CPU"
  record_summary "want_gpu" "$WANT_GPU"
  record_summary "force_cpu" "$FORCE_CPU"
  append_summary_line "Dependency groups: $SYNC_GROUPS"
  if (( FORCE_CPU )); then
    append_summary_line "CPU enforcement enabled"
  else
    append_summary_line "GPU packages permitted"
  fi
}

detect_gpu_hardware() {
  GPU_PRESENT=0
  local source=""
  if command -v nvidia-smi >/dev/null 2>&1; then
    if nvidia-smi -L >/dev/null 2>&1; then
      GPU_PRESENT=1
      source="nvidia-smi"
    fi
  fi
  if (( GPU_PRESENT == 0 )) && [[ -c /dev/nvidia0 ]]; then
    GPU_PRESENT=1
    source="/dev/nvidia0"
  fi
  if (( GPU_PRESENT == 0 )) && command -v lspci >/dev/null 2>&1; then
    if lspci | grep -qi 'nvidia'; then
      GPU_PRESENT=1
      source="lspci"
    fi
  fi
  record_summary "gpu_hardware_detected" "$GPU_PRESENT"
  if (( GPU_PRESENT )); then
    log "GPU hardware detected via ${source:-unknown}"
  else
    log "No GPU hardware detected"
  fi
}

collect_gpu_lock_packages() {
  GPU_PACKAGES=()
  [[ -f uv.lock ]] || return
  mapfile -t GPU_PACKAGES < <(python3 - <<'PY'
import pathlib, re
path = pathlib.Path('uv.lock')
if not path.exists():
    raise SystemExit
text = path.read_text().splitlines()
packages = set()
for line in text:
    if line.startswith('name = '):
        name = line.split('=', 1)[1].strip().strip('"')
        lower = name.lower()
        if lower.startswith('nvidia-') or lower in {'triton', 'pytorch-triton', 'pytorch_cuda', 'pytorch-cuda'}:
            packages.add(name)
    match = re.search(r"name\s*=\s*\"([^\"]+)\"", line)
    if match:
        cand = match.group(1)
        lower = cand.lower()
        if lower.startswith('nvidia-') or lower in {'triton', 'pytorch-triton', 'pytorch_cuda', 'pytorch-cuda'}:
            packages.add(cand)
if packages:
    print("\n".join(sorted(packages)))
PY
  )
}

lock_torch_version() {
  [[ -f uv.lock ]] || { printf 'none'; return; }
  python3 - <<'PY'
import pathlib, sys
path = pathlib.Path('uv.lock')
if not path.exists():
    print('none')
    raise SystemExit
name_line = False
for line in path.read_text().splitlines():
    if line.startswith('[[package]]'):
        name_line = False
    elif line.startswith('name = "torch"'):
        name_line = True
    elif name_line and line.startswith('version = '):
        print(line.split('=',1)[1].strip().strip('"'))
        break
else:
    print('none')
PY
}

attempt_relock_torch_cpu() {
  (( FORCE_CPU )) || return
  [[ -f uv.lock ]] || return
  command -v uv >/dev/null 2>&1 || { warn "uv not available; cannot rewrite uv.lock"; return; }
  (( OFFLINE )) && { warn "Offline mode; skipping uv.lock rewrite"; return; }

  collect_gpu_lock_packages
  local torch_version_in_lock="$(lock_torch_version)"
  local need_relock=0
  if ((${#GPU_PACKAGES[@]})); then
    need_relock=1
  fi
  if [[ "$torch_version_in_lock" != "$TORCH_VERSION" ]]; then
    need_relock=1
  fi
  if (( need_relock == 0 )); then
    return
  fi

  log "Rewriting uv.lock to target torch ${TORCH_VERSION} from CPU index"
  mkdir -p .codex/cache
  local backup=".codex/cache/uv.lock.before_cpu.$(date +%s)"
  cp uv.lock "$backup" || true

  local cmd
  cmd=$(cmd_to_string \
    uv lock \
    --upgrade-package "torch==${TORCH_VERSION}" \
    --index "${TORCH_INDEX_CPU}" \
    --index "https://pypi.org/simple" \
    )
  run "$cmd"

  if [[ ! -f uv.lock ]]; then
    warn "uv lock rewrite removed lock file; restoring backup"
    cp "$backup" uv.lock || true
  fi

  collect_gpu_lock_packages
  record_summary "lock_torch_version" "$(lock_torch_version)"
  if ((${#GPU_PACKAGES[@]})); then
    warn "GPU packages still referenced in uv.lock: ${GPU_PACKAGES[*]}"
  else
    append_summary_line "uv.lock updated for CPU torch ${TORCH_VERSION}"
  fi
}

calc_lock_digest() {
  local digest
  digest=$(python3 - <<'PY'
import hashlib, pathlib
paths = [
    "uv.lock",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "docs/requirements.txt",
    "services/api/requirements.txt",
]
h = hashlib.sha256()
for rel in paths:
    p = pathlib.Path(rel)
    if not p.exists():
        continue
    h.update(rel.encode())
    h.update(b"\0")
    h.update(p.read_bytes())
print(h.hexdigest())
PY
  )
  LOCK_DIGEST="$digest"
  record_summary "lock_digest" "$digest"
}

determine_sync_requirement() {
  local setup_hash="$(cat .codex/cache/setup.locksum 2>/dev/null || echo none)"
  local maint_hash_file=".codex/cache/maintenance.locksum"
  local last_hash="$(cat "$maint_hash_file" 2>/dev/null || echo none)"
  NEED_SYNC=1
  if [[ "$setup_hash" == "none" && "$last_hash" == "none" ]]; then
    NEED_SYNC=1
  elif [[ "$LOCK_DIGEST" == "$setup_hash" && "$LOCK_DIGEST" == "$last_hash" ]]; then
    NEED_SYNC=0
  fi
  record_summary "need_sync" "$NEED_SYNC"
  if (( NEED_SYNC )); then
    log "Dependency sync required (current=$LOCK_DIGEST setup=$setup_hash last=$last_hash)"
  else
    log "Lock digest unchanged; skipping dependency sync"
  fi
}

dump_maintenance_hash() {
  local maint_hash_file=".codex/cache/maintenance.locksum"
  printf '%s\n' "$LOCK_DIGEST" >"$maint_hash_file"
}

ensure_uv_available() {
  section "Ensuring uv availability"
  if command -v uv >/dev/null 2>&1; then
    log "uv detected: $(uv --version || true)"
    return
  fi
  if (( OFFLINE )); then
    warn "uv not found and CODEX_OFFLINE=1; skipping installation"
    return
  fi
  if command -v curl >/dev/null 2>&1; then
    run "curl -fsSL https://astral.sh/uv/install.sh | bash"
  fi
  if ! command -v uv >/dev/null 2>&1; then
    if command -v pipx >/dev/null 2>&1; then
      run "pipx install uv"
    else
      run "python3 -m pip install --user uv || true"
      export PATH="$HOME/.local/bin:$PATH"
    fi
  fi
  if command -v uv >/dev/null 2>&1; then
    log "uv installed: $(uv --version || true)"
  else
    warn "uv not available after attempted installation"
  fi
}

setup_virtualenv() {
  section "Activating Python virtual environment"
  cd "$REPO_ROOT"
  if [[ -d .venv ]]; then
    :
  else
    warn ".venv missing; creating new virtual environment"
    if command -v uv >/dev/null 2>&1; then
      set +e
      uv venv --seed .venv >/dev/null 2>&1
      local ec=$?
      set -e
      if (( ec != 0 )); then
        warn "uv venv failed (exit $ec); falling back to python -m venv"
        python3 -m venv .venv || maybe_fail "Failed to create virtualenv"
      fi
    else
      python3 -m venv .venv || maybe_fail "Failed to create virtualenv"
    fi
  fi
  if [[ ! -d .venv ]]; then
    maybe_fail "Virtualenv creation failed; .venv missing"
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate || maybe_fail "Failed to activate .venv"
  export UV_PYTHON="$(command -v python)"
  log "Using Python interpreter: ${UV_PYTHON} ($(python --version 2>/dev/null | tr -d '\n'))"
  record_summary "python_executable" "$UV_PYTHON"
}

sync_python_dependencies() {
  (( NEED_SYNC )) || { log "Dependencies already synchronized"; return; }
  section "Synchronizing Python dependencies"
  collect_gpu_lock_packages
  local skip_packages=()
  if (( FORCE_CPU )); then
    skip_packages+=(torch)
    if ((${#GPU_PACKAGES[@]})); then
      skip_packages+=("${GPU_PACKAGES[@]}")
    fi
  fi

  if command -v uv >/dev/null 2>&1 && [[ -f pyproject.toml ]]; then
    local args=(uv sync --group base)
    local token
    for token in "${SYNC_TOKENS[@]}"; do
      case "$token" in
        base) : ;; 
        cpu|gpu|dev|test|tracking|docs|lint|analysis|benchmark|training)
          args+=(--group "$token") ;;
        all|all-groups|everything)
          args+=(--all-groups) ;;
        extras|+extras|all-extras)
          args+=(--all-extras) ;;
        extra:*)
          args+=(--extra "${token#extra:}") ;;
        +*)
          args+=(--extra "${token#+}") ;;
        *)
          args+=(--group "$token") ;;
      esac
    done
    local pkg
    for pkg in "${skip_packages[@]}"; do
      args+=(--no-install-package "$pkg")
    done
    (( OFFLINE )) && args+=(--offline)
    local cmd
    cmd=$(cmd_to_string "${args[@]}")
    run "$cmd"
  else
    if (( OFFLINE )); then
      warn "Offline mode without uv; skipping dependency installation"
    else
      log "Falling back to pip-based installation"
      run "python3 -m ensurepip -U || true"
      run "python3 -m pip install -U pip wheel"
      [[ -f requirements.txt ]] && run "pip install -r requirements.txt"
      [[ -f requirements-dev.txt ]] && run "pip install -r requirements-dev.txt"
      [[ -f docs/requirements.txt ]] && run "pip install -r docs/requirements.txt"
      [[ -f services/api/requirements.txt ]] && run "pip install -r services/api/requirements.txt"
      if [[ -f pyproject.toml ]]; then
        run "pip install -e ."
      fi
    fi
  fi
  SKIPPED_PACKAGES_STR="${skip_packages[*]}"
  record_summary "uv_skip_packages" "${SKIPPED_PACKAGES_STR:-none}"
  if [[ -n "$SKIPPED_PACKAGES_STR" ]]; then
    append_summary_line "uv sync skipped packages: ${SKIPPED_PACKAGES_STR}"
  fi
}

install_cpu_torch() {
  (( FORCE_CPU || WANT_CPU )) || return
  section "Ensuring CPU-only torch (${TORCH_VERSION})"
  if [[ -z "${UV_PYTHON:-}" ]]; then
    maybe_fail "UV_PYTHON not set; virtualenv not prepared"
    return
  fi
  local args=(uv pip install --python "$UV_PYTHON" --index-url "$TORCH_INDEX_CPU" "torch==${TORCH_VERSION}")
  (( OFFLINE )) && args+=(--offline)
  run "$(cmd_to_string "${args[@]}")"
  record_summary "torch_cpu_target" "$TORCH_VERSION"
}

purge_gpu_residue() {
  (( FORCE_CPU )) || return
  section "Removing GPU-oriented packages"
  if [[ -z "${UV_PYTHON:-}" ]]; then
    maybe_fail "UV_PYTHON not set; cannot inspect environment"
    return
  fi
  mapfile -t residue < <("${UV_PYTHON}" - <<'PY'
import importlib.metadata as md
names = set()
for dist in md.distributions():
    try:
        name = dist.metadata['Name']
    except KeyError:
        name = dist.metadata.get('Name') or dist.metadata.get('Summary')
        if not name:
            continue
    lower = name.lower()
    if lower.startswith('nvidia-') or lower in {'triton', 'pytorch-triton', 'pytorch_cuda', 'pytorch-cuda'}:
        names.add(name)
if names:
    print("\n".join(sorted(names)))
PY
  )
  if ((${#residue[@]} == 0)); then
    record_summary "gpu_residue_initial" "none"
    return
  fi
  local joined="${residue[*]}"
  log "Purging GPU packages: $joined"
  record_summary "gpu_residue_initial" "$joined"
  local uninstall_cmd=(uv pip uninstall --python "$UV_PYTHON" -y "${residue[@]}")
  (( OFFLINE )) && uninstall_cmd+=(--offline)
  run "$(cmd_to_string "${uninstall_cmd[@]}")"
  mapfile -t residue < <("${UV_PYTHON}" - <<'PY'
import importlib.metadata as md
names = set()
for dist in md.distributions():
    try:
        name = dist.metadata['Name']
    except KeyError:
        name = dist.metadata.get('Name') or dist.metadata.get('Summary')
        if not name:
            continue
    lower = name.lower()
    if lower.startswith('nvidia-') or lower in {'triton', 'pytorch-triton', 'pytorch_cuda', 'pytorch-cuda'}:
        names.add(name)
if names:
    print("\n".join(sorted(names)))
PY
  )
  if ((${#residue[@]} == 0)); then
    record_summary "gpu_residue_final" "none"
  else
    local remaining="${residue[*]}"
    record_summary "gpu_residue_final" "$remaining"
    warn "GPU packages remain after purge: $remaining"
    if [[ "$FAIL_ON_GPU_RESIDUE" == "1" ]]; then
      die "GPU residue persists after uninstall pass"
    fi
  fi
}

verify_torch_cpu() {
  section "Verifying torch"
  if [[ -z "${UV_PYTHON:-}" ]]; then
    maybe_fail "UV_PYTHON not set; cannot verify torch"
    return
  fi
  local output
  set +e
  output=$("${UV_PYTHON}" - <<'PY'
import json, sys
try:
    import torch
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
    sys.exit(1)
info = {
    "ok": True,
    "version": torch.__version__,
    "cuda_available": bool(torch.cuda.is_available()),
    "cuda_version": getattr(torch.version, "cuda", None),
}
try:
    import torch.backends.mps
    info["mps_available"] = bool(torch.backends.mps.is_available())
except Exception:
    info["mps_available"] = False
print(json.dumps(info))
PY
  )
  local ec=$?
  set -e
  if (( ec != 0 )); then
    printf "%s\n" "$output" >&2
    maybe_fail "Torch verification failed"
    return
  fi
  log "Torch status: $output"
  record_summary "torch_status" "$output"
  readarray -t summary_lines < <(python3 - <<'PY' "$output" "$TORCH_VERSION"
import json, sys
info = json.loads(sys.argv[1])
expected = sys.argv[2]
version = info.get('version', 'unknown')
cuda = info.get('cuda_available')
cuda_version = info.get('cuda_version')
print(f"Torch {version} (cuda_available={cuda}, cuda_version={cuda_version})")
print('match' if version == expected else 'mismatch')
PY
  )
  append_summary_line "${summary_lines[0]}"
  if [[ "${summary_lines[1]}" != "match" ]]; then
    warn "Installed torch version ${summary_lines[0]} does not match expected ${TORCH_VERSION}"
  fi
}

sync_node_dependencies() {
  [[ -f package.json ]] || return
  (( NEED_SYNC )) || { log "Node dependencies unchanged (skip due to NEED_SYNC=0)"; return; }
  section "Ensuring Node dependencies"
  if (( OFFLINE )); then
    log "Offline mode enabled; skipping Node dependency installation"
    return
  fi
  local hash
  hash=$(python3 - <<'PY'
import hashlib, pathlib
paths = ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
h = hashlib.sha256()
found = False
for rel in paths:
    p = pathlib.Path(rel)
    if not p.exists():
        continue
    found = True
    h.update(rel.encode())
    h.update(b"\0")
    h.update(p.read_bytes())
if not found:
    print('none')
else:
    print(h.hexdigest())
PY
  )
  local cache_file=".codex/cache/maintenance.node.lockhash"
  local last_hash="$(cat "$cache_file" 2>/dev/null || echo none)"
  if [[ "$hash" == "none" ]]; then
    log "No Node lockfile detected; skipping install"
    return
  fi
  if [[ "$hash" == "$last_hash" ]]; then
    log "Node lockfiles unchanged; skipping install"
    return
  fi
  if command -v pnpm >/dev/null 2>&1 && [[ -f pnpm-lock.yaml ]]; then
    run "pnpm install --frozen-lockfile"
  elif command -v yarn >/dev/null 2>&1 && [[ -f yarn.lock ]]; then
    run "yarn install --frozen-lockfile"
  else
    run "npm ci || npm install"
  fi
  echo "$hash" >"$cache_file"
}

setup_precommit() {
  [[ -f .pre-commit-config.yaml ]] || { log "No pre-commit config detected; skipping"; return; }
  if [[ "$ENSURE_PRECOMMIT" != "1" ]]; then
    log "CODEX_ENSURE_PRECOMMIT=0; skipping pre-commit setup"
    return
  fi
  section "Ensuring pre-commit hooks"
  local install_cmd=(uv pip install --python "$UV_PYTHON" pre-commit)
  (( OFFLINE )) && install_cmd+=(--offline)
  run "$(cmd_to_string "${install_cmd[@]}")"
  if command -v pre-commit >/dev/null 2>&1; then
    run "pre-commit install --install-hooks -t pre-commit -t pre-push || pre-commit install -t pre-commit -t pre-push"
  else
    warn "pre-commit executable unavailable after installation"
  fi
}

main() {
  setup_context
  parse_sync_groups
  record_summary "offline_mode" "$OFFLINE"
  record_summary "graceful" "$GRACEFUL"
  if (( OFFLINE )); then
    append_summary_line "Offline mode active"
  fi

  detect_gpu_hardware
  ensure_uv_available
  setup_virtualenv

  attempt_relock_torch_cpu
  calc_lock_digest
  determine_sync_requirement
  sync_python_dependencies

  install_cpu_torch
  purge_gpu_residue
  verify_torch_cpu

  sync_node_dependencies
  setup_precommit
  dump_maintenance_hash
}

main "$@"
