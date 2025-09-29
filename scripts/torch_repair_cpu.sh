#!/usr/bin/env bash
set -euo pipefail
log() { printf '%s\n' "$*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/libtorch_policy.sh"
log "[*] Torch CPU repair starting"
if [ -d ".venv" ]; then . ".venv/bin/activate"; fi
PY=${UV_PYTHON:-}
if [ -z "${PY}" ] && [ -n "${VIRTUAL_ENV:-}" ]; then PY="$VIRTUAL_ENV/bin/python"; fi
PY=${PY:-python}
log "[*] Before reinstall:"
"$PY" - <<'PY'
try:
    import torch
    print("torch_version(before):", getattr(torch, "__version__", None))
    print("torch_cuda(before):", getattr(getattr(torch, "version", None), "cuda", None))
except Exception as exc:
    print("IMPORT_ERROR(before):", exc)
PY
REQ="${TORCH_REQUIREMENT:-torch}"
log "[*] Installing from PyTorch CPU index..."
PIP_INDEX_URL="${PIP_INDEX_URL:-https://download.pytorch.org/whl/cpu}" UV_PYTHON="$PY" uv pip install --reinstall "$REQ"
log "[*] After reinstall:"
"$PY" - <<'PY'
import torch
print("torch_version(after):", torch.__version__)
print("torch_cuda(after):", getattr(getattr(torch, "version", None), "cuda", None))
PY
log "[*] Policy check:"
set +e
component="$(choose_torch_policy_component)"
if [ "$component" = "module" ]; then
  torch_policy_module_check
else
  python scripts/torch_policy_check.py
fi
RC=$?
set -e
log "[*] Policy component used: ${component}"
if [ "$RC" -ne 0 ]; then
  echo "[repair][FAIL] Torch policy check still failing" >&2
  exit "$RC"
fi
log "[*] Torch CPU repair completed"
