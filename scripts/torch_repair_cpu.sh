#!/usr/bin/env bash
set -euo pipefail
log() { printf '%s\n' "$*"; }
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
log "[*] Installing from PyTorch CPU index..."
PIP_INDEX_URL="https://download.pytorch.org/whl/cpu" UV_PYTHON="$PY" uv pip install --reinstall "torch"
log "[*] After reinstall:"
"$PY" - <<'PY'
import torch
print("torch_version(after):", torch.__version__)
print("torch_cuda(after):", getattr(getattr(torch, "version", None), "cuda", None))
PY
log "[*] Policy check:"
python scripts/torch_policy_check.py
log "[*] Torch CPU repair completed"
