#!/usr/bin/env bash
# Codex environment maintenance (refresh phase)
#
# This script prepares the Python environment for the ChatGPT-Codex sandbox.
# Major capabilities:
#   * Enforces CPU-only torch wheels whenever GPU extras are not requested.
#   * Scrubs GPU packages from uv.lock by regenerating the lock against the
#     PyTorch CPU index.
#   * Synchronises dependencies with uv respecting CODEX_SYNC_GROUPS.
#   * Optionally installs pre-commit and records execution telemetry.
#   * Emits a machine-readable summary at .codex/cache/maintenance_summary.json.

set -euo pipefail

if [[ "${CODEX_DEBUG:-0}" == "1" ]]; then
  set -x
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PHASE="maintenance"

DEFAULT_GROUPS="base,cpu"
RAW_SYNC_GROUPS="${CODEX_SYNC_GROUPS:-$DEFAULT_GROUPS}"
IFS=',' read -ra _RAW_GROUPS <<<"$RAW_SYNC_GROUPS"
SELECTED_GROUPS=()
for entry in "${_RAW_GROUPS[@]}"; do
  trimmed="${entry//[[:space:]]/}"
  if [[ -n "$trimmed" ]]; then
    SELECTED_GROUPS+=("$trimmed")
  fi
done
if ((${#SELECTED_GROUPS[@]} == 0)); then
  SELECTED_GROUPS+=("base")
fi

if [[ -z "${CODEX_FORCE_CPU:-}" ]]; then
  CODEX_FORCE_CPU=1
  for group in "${SELECTED_GROUPS[@]}"; do
    if [[ "$group" == "gpu" ]]; then
      CODEX_FORCE_CPU=0
      break
    fi
  done
else
  CODEX_FORCE_CPU=${CODEX_FORCE_CPU}
fi

CODEX_OFFLINE="${CODEX_OFFLINE:-0}"
CODEX_TORCH_VERSION="${CODEX_TORCH_VERSION:-torch==2.8.0+cpu}"
TORCH_INDEX_URL="${TORCH_INDEX_URL:-https://download.pytorch.org/whl/cpu}"
GRACEFUL="${GRACEFUL:-0}"
CODEX_FAIL_ON_GPU_RESIDUE="${CODEX_FAIL_ON_GPU_RESIDUE:-0}"

if [[ -z "${CODEX_ENSURE_PRECOMMIT:-}" ]]; then
  if [[ -f "${REPO_ROOT}/.pre-commit-config.yaml" ]]; then
    CODEX_ENSURE_PRECOMMIT=1
  else
    CODEX_ENSURE_PRECOMMIT=0
  fi
fi

UV_BIN="${UV_BIN:-$(command -v uv || true)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
FAIL_LOG="${REPO_ROOT}/.codex/logs/command_failures.log"
SUMMARY_PATH="${REPO_ROOT}/.codex/cache/${PHASE}_summary.json"
mkdir -p "${REPO_ROOT}/.codex/logs" "${REPO_ROOT}/.codex/cache"
touch "$FAIL_LOG"

FAILED_COMMANDS=()
LOCK_GPU_TOKENS_BEFORE=()
LOCK_GPU_TOKENS_AFTER=()
GPU_RESIDUE_BEFORE=()
GPU_RESIDUE_AFTER=()
TORCH_INFO=""
PRECOMMIT_STATUS="skipped"
UV_VERSION=""

log() {
  printf '[codex:%s] %s\n' "$PHASE" "$*"
}

warn() {
  log "WARN: $*"
}

CURRENT_SECTION=""
SECTION_START=0

finish_section() {
  if [[ -n "$CURRENT_SECTION" ]]; then
    local elapsed=$(( $(date +%s) - SECTION_START ))
    log "Finished ${CURRENT_SECTION} (${elapsed}s)"
    CURRENT_SECTION=""
  fi
}

section() {
  local name="$1"
  finish_section
  CURRENT_SECTION="$name"
  SECTION_START=$(date +%s)
  log "--- ${name} ---"
}

record_failure() {
  local label="$1"
  local rc="$2"
  FAILED_COMMANDS+=("${label} (rc=${rc})")
  printf '%s %s exit=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$label" "$rc" >>"$FAIL_LOG"
}

run_cmd() {
  local label="$1"
  shift
  local allow_fail=0
  if [[ "$1" == "--allow-fail" ]]; then
    allow_fail=1
    shift
  fi
  log "▶ ${label}"
  local start_ts=$(date +%s)
  set +e
  "${@}"
  local rc=$?
  set -e
  local elapsed=$(( $(date +%s) - start_ts ))
  if (( rc != 0 )); then
    warn "Command failed (${label}, rc=${rc}, ${elapsed}s)"
    record_failure "$label" "$rc"
    if (( allow_fail == 0 )) && [[ "$GRACEFUL" != "1" ]]; then
      finish_section
      exit "$rc"
    fi
  else
    log "✔ ${label} (${elapsed}s)"
  fi
  return "$rc"
}

# Optional dependency parsing -------------------------------------------------

declare -A OPTIONAL_DEP_MAP=()
OPTIONAL_EXTRA_NAMES=()
PRECOMMIT_EXTRAS=()
PRECOMMIT_DECLARED=0

parse_optional_dependencies() {
  local pyproject="${REPO_ROOT}/pyproject.toml"
  OPTIONAL_DEP_MAP=()
  OPTIONAL_EXTRA_NAMES=()
  PRECOMMIT_EXTRAS=()
  [[ -f "$pyproject" ]] || return 0
  while IFS= read -r line; do
    local extra="${line%%:*}"
    local packages="${line#*:}"
    OPTIONAL_DEP_MAP["$extra"]="$packages"
    OPTIONAL_EXTRA_NAMES+=("$extra")
    if [[ "$packages" == *"pre-commit"* ]]; then
      PRECOMMIT_EXTRAS+=("$extra")
    fi
  done < <("$PYTHON_BIN" - "$pyproject" <<'PY'
import sys, re, ast
from pathlib import Path
path = Path(sys.argv[1])
try:
    text = path.read_text(encoding="utf-8")
except FileNotFoundError:
    sys.exit(0)
match = re.search(r'\[project\.optional-dependencies\](.*?)(\n\[|\Z)', text, re.S)
if not match:
    sys.exit(0)
body = match.group(1)
current = None
buffer = []
for line in body.splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        continue
    if stripped.endswith("[") and "=" in stripped:
        current = stripped.split("=", 1)[0].strip()
        buffer = []
        continue
    if stripped == "]":
        if current is not None:
            try:
                values = ast.literal_eval("[" + ",".join(buffer) + "]")
            except Exception:
                values = []
            normalized = []
            for item in values:
                if isinstance(item, str):
                    normalized.append(item)
            print(f"{current}:{'|'.join(normalized)}")
        current = None
        buffer = []
        continue
    if current is not None:
        buffer.append(stripped.rstrip(","))
PY
)
  if ((${#PRECOMMIT_EXTRAS[@]} > 0)); then
    PRECOMMIT_DECLARED=1
  fi
}

parse_optional_dependencies

# Sync argument helpers -------------------------------------------------------

SYNC_EXTRA_ARGS=()
SYNC_GROUP_ARGS=()
EXTRA_ORDERED=()
GROUP_ORDERED=()
declare -A EXTRA_SELECTED=()
declare -A GROUP_SELECTED=()

add_extra() {
  local name="$1"
  [[ -n "$name" ]] || return 0
  if [[ -n "${EXTRA_SELECTED[$name]:-}" ]]; then
    return 0
  fi
  EXTRA_SELECTED["$name"]=1
  EXTRA_ORDERED+=("$name")
  SYNC_EXTRA_ARGS+=("--extra" "$name")
}

add_group() {
  local name="$1"
  [[ -n "$name" ]] || return 0
  if [[ -n "${GROUP_SELECTED[$name]:-}" ]]; then
    return 0
  fi
  GROUP_SELECTED["$name"]=1
  GROUP_ORDERED+=("$name")
  SYNC_GROUP_ARGS+=("--group" "$name")
}

compute_sync_configuration() {
  SYNC_EXTRA_ARGS=()
  SYNC_GROUP_ARGS=()
  EXTRA_ORDERED=()
  GROUP_ORDERED=()
  EXTRA_SELECTED=()
  GROUP_SELECTED=()

  local have_cpu_extra=0
  for group in "${SELECTED_GROUPS[@]}"; do
    if [[ "$group" == "base" ]]; then
      continue
    fi
    if [[ -n "${OPTIONAL_DEP_MAP[$group]:-}" ]]; then
      if [[ "$group" == "gpu" && "$CODEX_FORCE_CPU" == "1" ]]; then
        continue
      fi
      add_extra "$group"
      if [[ "$group" == "cpu" ]]; then
        have_cpu_extra=1
      fi
    else
      add_group "$group"
    fi
  done

  if [[ "$CODEX_FORCE_CPU" == "1" && "$have_cpu_extra" == "0" && -n "${OPTIONAL_DEP_MAP[cpu]:-}" ]]; then
    log "CPU-only mode → ensuring 'cpu' extra is selected"
    add_extra "cpu"
  fi

  if [[ "$CODEX_ENSURE_PRECOMMIT" == "1" && "$PRECOMMIT_DECLARED" == "1" ]]; then
    local chosen=""
    for extra in "${PRECOMMIT_EXTRAS[@]}"; do
      chosen="$extra"
      break
    done
    if [[ -n "$chosen" && -z "${EXTRA_SELECTED[$chosen]:-}" ]]; then
      log "Including '${chosen}' extra to provide pre-commit"
      add_extra "$chosen"
    fi
  fi
}

compute_sync_configuration

# Utility helpers -------------------------------------------------------------

ensure_uv() {
  if [[ -n "$UV_BIN" && -x "$UV_BIN" ]]; then
    UV_VERSION="$($UV_BIN --version 2>/dev/null || true)"
    log "Found uv at ${UV_BIN} (${UV_VERSION})"
    return 0
  fi
  if [[ "$CODEX_OFFLINE" == "1" ]]; then
    warn "uv is not available and offline mode is enabled"
    record_failure "uv_missing_offline" 1
    return 1
  fi
  log "uv not detected → installing via ${PYTHON_BIN}"
  run_cmd "Install uv" "$PYTHON_BIN" -m pip install --upgrade uv
  UV_BIN="$(command -v uv || true)"
  if [[ -z "$UV_BIN" ]]; then
    warn "uv installation failed"
    record_failure "uv_install_failed" 1
    return 1
  fi
  UV_VERSION="$($UV_BIN --version 2>/dev/null || true)"
  log "uv version ${UV_VERSION} ready"
}

install_system_prereqs() {
  if [[ "$CODEX_OFFLINE" == "1" ]]; then
    log "Offline mode enabled; skipping apt dependencies"
    return 0
  fi
  if command -v apt-get >/dev/null 2>&1; then
    local apt_cmd=(apt-get)
    if (( EUID != 0 )) && command -v sudo >/dev/null 2>&1; then
      apt_cmd=(sudo apt-get)
    fi
    run_cmd "apt-get update" "${apt_cmd[@]}" update
    run_cmd "Install system packages" "${apt_cmd[@]}" install -y build-essential python3-dev python3-venv git git-lfs curl jq
  fi
}

detect_gpu_tokens_in_lock() {
  local lock_path="$1"
  [[ -f "$lock_path" ]] || return 0
  "$PYTHON_BIN" - "$lock_path" <<'PY'
import sys, re
from pathlib import Path
path = Path(sys.argv[1])
if not path.exists():
    sys.exit(0)
text = path.read_text(encoding="utf-8")
blocks = re.split(r"\n(?=\[\[package\]\])", text)
targets = set()
for block in blocks:
    match = re.search(r'name\s*=\s*"([^\"]+)"', block)
    if not match:
        continue
    name = match.group(1)
    lower = name.lower()
    version_match = re.search(r'version\s*=\s*"([^\"]+)"', block)
    version = version_match.group(1) if version_match else ""
    if lower.startswith("nvidia-") or lower.startswith("cuda-") or lower in {"triton", "torchtriton", "torch-triton"} or "+cu" in version.lower() or "+cuda" in version.lower():
        targets.add(f"{name}=={version}" if version else name)
if targets:
    print("\n".join(sorted(targets)))
PY
}

repair_lock_for_cpu() {
  local lock_path="${REPO_ROOT}/uv.lock"
  if [[ ! -f "$lock_path" ]]; then
    log "uv.lock not found; skipping lock scrub"
    return 0
  fi
  local before
  before=$(detect_gpu_tokens_in_lock "$lock_path" || true)
  if [[ -n "$before" ]]; then
    readarray -t LOCK_GPU_TOKENS_BEFORE <<<"$before"
  else
    LOCK_GPU_TOKENS_BEFORE=()
  fi
  if ((${#LOCK_GPU_TOKENS_BEFORE[@]} == 0)); then
    log "Lockfile already free of GPU packages"
    LOCK_GPU_TOKENS_AFTER=()
    return 0
  fi
  log "GPU packages detected in lockfile: ${LOCK_GPU_TOKENS_BEFORE[*]}"
  if [[ "$CODEX_FORCE_CPU" != "1" ]]; then
    warn "CPU enforcement disabled → leaving lock unchanged"
    LOCK_GPU_TOKENS_AFTER=("${LOCK_GPU_TOKENS_BEFORE[@]}")
    return 0
  fi
  if [[ "$CODEX_OFFLINE" == "1" ]]; then
    warn "Offline mode prevents lock regeneration"
    record_failure "lock_gpu_scrub_offline" 1
    LOCK_GPU_TOKENS_AFTER=("${LOCK_GPU_TOKENS_BEFORE[@]}")
    return 1
  fi
  local backup="${lock_path}.bak.$(date -u +%Y%m%dT%H%M%SZ)"
  cp "$lock_path" "$backup"
  log "Backup written to $backup"
  local lock_args=(lock --upgrade)
  lock_args+=(--index "$TORCH_INDEX_URL")
  lock_args+=(--index-strategy first-index)
  run_cmd "Regenerate uv.lock (CPU-first)" "$UV_BIN" "${lock_args[@]}"
  local after
  after=$(detect_gpu_tokens_in_lock "$lock_path" || true)
  if [[ -n "$after" ]]; then
    readarray -t LOCK_GPU_TOKENS_AFTER <<<"$after"
    warn "GPU packages remain in lockfile: ${LOCK_GPU_TOKENS_AFTER[*]}"
    if [[ "$CODEX_FAIL_ON_GPU_RESIDUE" == "1" ]]; then
      record_failure "lock_gpu_residue" 2
    fi
  else
    LOCK_GPU_TOKENS_AFTER=()
    log "Lockfile scrub completed"
  fi
}

sync_environment() {
  local sync_args=()
  if [[ "$CODEX_OFFLINE" == "1" ]]; then
    sync_args+=(--offline)
  fi
  if [[ "$CODEX_FORCE_CPU" == "1" ]]; then
    sync_args+=(--index "$TORCH_INDEX_URL")
  fi
  sync_args+=("${SYNC_EXTRA_ARGS[@]}")
  sync_args+=("${SYNC_GROUP_ARGS[@]}")
  run_cmd "uv sync" "$UV_BIN" sync "${sync_args[@]}"
}

check_torch_json() {
  "$UV_BIN" run -- python - "$CODEX_TORCH_VERSION" <<'PY'
import json, sys
expected_spec = sys.argv[1] if len(sys.argv) > 1 else ""
expected_version = ""
if expected_spec:
    parts = expected_spec.split("==", 1)
    if len(parts) == 2:
        expected_version = parts[1]
    else:
        expected_version = expected_spec
result = {
    "expected": expected_version or None,
}
try:
    import torch
except Exception as exc:  # pragma: no cover
    result["available"] = False
    result["error"] = str(exc)
    print(json.dumps(result))
    sys.exit(1)
result["available"] = True
result["version"] = getattr(torch, "__version__", None)
result["cuda_version"] = getattr(getattr(torch, "version", None), "cuda", None)
try:
    cuda_available = torch.cuda.is_available()
except Exception:
    cuda_available = False
result["cuda_available"] = bool(cuda_available)
try:
    mps_available = torch.backends.mps.is_available()
except Exception:
    mps_available = False
result["mps_available"] = bool(mps_available)
if expected_version:
    version = result["version"] or ""
    base_expected = expected_version.split("+", 1)[0]
    base_version = version.split("+", 1)[0]
    if version != expected_version and not (expected_version.endswith("+cpu") and version.endswith("+cpu") and base_version == base_expected):
        result["mismatch"] = True
        print(json.dumps(result))
        sys.exit(2)
if expected_version.endswith("+cpu") and (result["cuda_available"] or (result["cuda_version"] and not str(result["cuda_version"]).endswith("cpu"))):
    result["mismatch"] = True
    print(json.dumps(result))
    sys.exit(3)
print(json.dumps(result))
PY
}

ensure_torch_cpu() {
  local output
  local rc=0
  set +e
  output=$(check_torch_json)
  rc=$?
  set -e
  if (( rc == 0 )); then
    TORCH_INFO="$output"
    return 0
  fi
  warn "Torch verification failed (rc=${rc}); enforcing ${CODEX_TORCH_VERSION}"
  if [[ "$CODEX_OFFLINE" == "1" ]]; then
    warn "Offline mode prevents torch reinstallation"
    record_failure "torch_verify_offline" "$rc"
    TORCH_INFO="$output"
    return "$rc"
  fi
  run_cmd "Install ${CODEX_TORCH_VERSION}" "$UV_BIN" pip install --upgrade --no-deps --index-url "$TORCH_INDEX_URL" "$CODEX_TORCH_VERSION"
  set +e
  output=$(check_torch_json)
  rc=$?
  set -e
  TORCH_INFO="$output"
  if (( rc != 0 )); then
    record_failure "verify_torch_cpu" "$rc"
  fi
  return "$rc"
}

list_gpu_distributions() {
  "$UV_BIN" run -- python - <<'PY'
import importlib.metadata
prefixes = ("nvidia-", "cuda-", "pytorch-cuda", "pytorch-triton")
suffixes = ("-cu11", "-cu12", "-cuda", "-cudnn")
extras = {"triton", "torchtriton", "torch-triton", "torchvision-cu118", "torchaudio-cu118"}
targets = set()
for dist in importlib.metadata.distributions():
    name = dist.metadata.get("Name")
    if not name:
        continue
    lower = name.lower()
    if lower.startswith(prefixes) or lower in extras or any(lower.endswith(suf) for suf in suffixes):
        targets.add(name)
print("\n".join(sorted(targets)))
PY
}

purge_gpu_packages() {
  local before
  before=$(list_gpu_distributions || true)
  if [[ -n "$before" ]]; then
    readarray -t GPU_RESIDUE_BEFORE <<<"$before"
  else
    GPU_RESIDUE_BEFORE=()
  fi
  if [[ "$CODEX_FORCE_CPU" != "1" ]]; then
    GPU_RESIDUE_AFTER=("${GPU_RESIDUE_BEFORE[@]}")
    return 0
  fi
  if ((${#GPU_RESIDUE_BEFORE[@]} > 0)); then
    log "Removing GPU distributions: ${GPU_RESIDUE_BEFORE[*]}"
    run_cmd "Uninstall GPU distributions" "$UV_BIN" pip uninstall -y "${GPU_RESIDUE_BEFORE[@]}"
  fi
  local after
  after=$(list_gpu_distributions || true)
  if [[ -n "$after" ]]; then
    readarray -t GPU_RESIDUE_AFTER <<<"$after"
    warn "GPU distributions remain: ${GPU_RESIDUE_AFTER[*]}"
    if [[ "$CODEX_FAIL_ON_GPU_RESIDUE" == "1" ]]; then
      record_failure "gpu_residue_after_purge" 2
    fi
  else
    GPU_RESIDUE_AFTER=()
    log "No GPU distributions detected"
  fi
}

ensure_precommit() {
  if [[ "$CODEX_ENSURE_PRECOMMIT" != "1" ]]; then
    PRECOMMIT_STATUS="disabled"
    return 0
  fi
  if [[ ! -f "${REPO_ROOT}/.pre-commit-config.yaml" ]]; then
    PRECOMMIT_STATUS="missing-config"
    warn "pre-commit config not found; skipping installation"
    return 0
  fi
  local rc=0
  set +e
  "$UV_BIN" run -- python - <<'PY'
import sys
try:
    import pre_commit  # noqa: F401
except Exception:
    sys.exit(1)
PY
  rc=$?
  set -e
  if (( rc != 0 )); then
    if [[ "$CODEX_OFFLINE" == "1" ]]; then
      PRECOMMIT_STATUS="missing-offline"
      warn "Offline mode; cannot install pre-commit"
      record_failure "precommit_offline" 1
      return 1
    fi
    log "Installing pre-commit"
    run_cmd "Install pre-commit" "$UV_BIN" pip install --upgrade pre-commit
  fi
  run_cmd "pre-commit --version" "$UV_BIN" run -- pre-commit --version
  if (( rc != 0 )); then
    PRECOMMIT_STATUS="installed"
  else
    PRECOMMIT_STATUS="present"
  fi
}

write_summary() {
  local groups_serialized="$(printf '%s\n' "${SELECTED_GROUPS[@]}")"
  local extras_serialized="$(printf '%s\n' "${EXTRA_ORDERED[@]}")"
  local groups_flag_serialized="$(printf '%s\n' "${GROUP_ORDERED[@]}")"
  local lock_before_serialized="$(printf '%s\n' "${LOCK_GPU_TOKENS_BEFORE[@]}")"
  local lock_after_serialized="$(printf '%s\n' "${LOCK_GPU_TOKENS_AFTER[@]}")"
  local gpu_before_serialized="$(printf '%s\n' "${GPU_RESIDUE_BEFORE[@]}")"
  local gpu_after_serialized="$(printf '%s\n' "${GPU_RESIDUE_AFTER[@]}")"
  local failures_serialized="$(printf '%s\n' "${FAILED_COMMANDS[@]}")"
  local precommit_extras_serialized="$(printf '%s\n' "${PRECOMMIT_EXTRAS[@]}")"

  SUMMARY_PHASE="$PHASE" \
  SUMMARY_GROUPS="$groups_serialized" \
  SUMMARY_EXTRAS="$extras_serialized" \
  SUMMARY_GROUP_FLAGS="$groups_flag_serialized" \
  SUMMARY_LOCK_BEFORE="$lock_before_serialized" \
  SUMMARY_LOCK_AFTER="$lock_after_serialized" \
  SUMMARY_GPU_BEFORE="$gpu_before_serialized" \
  SUMMARY_GPU_AFTER="$gpu_after_serialized" \
  SUMMARY_FAILURES="$failures_serialized" \
  SUMMARY_TORCH_JSON="$TORCH_INFO" \
  SUMMARY_FORCE_CPU="$CODEX_FORCE_CPU" \
  SUMMARY_OFFLINE="$CODEX_OFFLINE" \
  SUMMARY_TORCH_SPEC="$CODEX_TORCH_VERSION" \
  SUMMARY_TORCH_INDEX="$TORCH_INDEX_URL" \
  SUMMARY_PRECOMMIT_STATUS="$PRECOMMIT_STATUS" \
  SUMMARY_PRECOMMIT_DECLARED="$PRECOMMIT_DECLARED" \
  SUMMARY_PRECOMMIT_EXTRAS="$precommit_extras_serialized" \
  SUMMARY_UV_VERSION="$UV_VERSION" \
  SUMMARY_PATH="$SUMMARY_PATH" "$PYTHON_BIN" - <<'PY'
import json, os, time, pathlib

def parse_lines(name):
    value = os.environ.get(name, "")
    if not value:
        return []
    return [line for line in value.splitlines() if line]

summary = {
    "phase": os.environ.get("SUMMARY_PHASE"),
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "force_cpu": os.environ.get("SUMMARY_FORCE_CPU") == "1",
    "offline": os.environ.get("SUMMARY_OFFLINE") == "1",
    "torch_spec": os.environ.get("SUMMARY_TORCH_SPEC"),
    "torch_index": os.environ.get("SUMMARY_TORCH_INDEX"),
    "uv_version": os.environ.get("SUMMARY_UV_VERSION"),
    "sync_groups": parse_lines("SUMMARY_GROUPS"),
    "sync_extras": parse_lines("SUMMARY_EXTRAS"),
    "sync_groups_flags": parse_lines("SUMMARY_GROUP_FLAGS"),
    "lock_gpu_before": parse_lines("SUMMARY_LOCK_BEFORE"),
    "lock_gpu_after": parse_lines("SUMMARY_LOCK_AFTER"),
    "gpu_residue_before": parse_lines("SUMMARY_GPU_BEFORE"),
    "gpu_residue_after": parse_lines("SUMMARY_GPU_AFTER"),
    "failures": parse_lines("SUMMARY_FAILURES"),
    "precommit_status": os.environ.get("SUMMARY_PRECOMMIT_STATUS"),
    "precommit_declared": os.environ.get("SUMMARY_PRECOMMIT_DECLARED") == "1",
    "precommit_extras": parse_lines("SUMMARY_PRECOMMIT_EXTRAS"),
}
raw_torch = os.environ.get("SUMMARY_TORCH_JSON")
if raw_torch:
    try:
        summary["torch"] = json.loads(raw_torch)
    except json.JSONDecodeError:
        summary["torch"] = {"raw": raw_torch, "error": "unparsed"}
else:
    summary["torch"] = None
path = pathlib.Path(os.environ["SUMMARY_PATH"])
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
PY
}

trap finish_section EXIT

section "Environment details"
log "repo=${REPO_ROOT}"
log "phase=${PHASE} force_cpu=${CODEX_FORCE_CPU} offline=${CODEX_OFFLINE}"
log "sync_groups=${SELECTED_GROUPS[*]} extras=${EXTRA_ORDERED[*]}"

section "uv availability"
ensure_uv

section "Lock hygiene"
repair_lock_for_cpu

section "Dependency synchronisation"
sync_environment
ensure_torch_cpu
purge_gpu_packages

section "Tooling"
ensure_precommit

section "Summary"
write_summary

FINAL_EXIT=0
if ((${#FAILED_COMMANDS[@]} > 0)); then
  FINAL_EXIT=1
fi
if [[ "$CODEX_FORCE_CPU" == "1" && "$CODEX_FAIL_ON_GPU_RESIDUE" == "1" ]]; then
  if ((${#LOCK_GPU_TOKENS_AFTER[@]} > 0)) || ((${#GPU_RESIDUE_AFTER[@]} > 0)); then
    FINAL_EXIT=1
  fi
fi
exit "$FINAL_EXIT"
