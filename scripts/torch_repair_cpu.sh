#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '%s\n' "$1"
}

log "[*] Torch CPU repair starting"

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  . ".venv/bin/activate"
fi

PY=${UV_PYTHON:-}
if [ -z "$PY" ] && [ -n "${VIRTUAL_ENV:-}" ]; then
  PY="$VIRTUAL_ENV/bin/python"
fi
if [ -z "$PY" ]; then
  PY=python
fi

log "[*] Verifying import before reinstall..."
"$PY" - <<'PY'
try:
    import torch
    print("torch_version(before):", torch.__version__)
    print("torch_cuda(before):", getattr(getattr(torch, "version", None), "cuda", None))
except Exception as exc:  # pragma: no cover - diagnostic only
    print("IMPORT_ERROR(before):", exc)
PY

log "[*] Forcing reinstall from PyTorch CPU index..."
PIP_INDEX_URL="https://download.pytorch.org/whl/cpu" \
UV_PYTHON="$PY" \
uv pip install --reinstall "torch==2.8.0"

log "[*] Verifying import after reinstall..."
"$PY" - <<'PY'
import torch
print("torch_version(after):", torch.__version__)
print("torch_cuda(after):", getattr(getattr(torch, "version", None), "cuda", None))
PY

log "[*] Running policy check..."
python scripts/torch_policy_check.py

log "[*] Torch CPU repair completed"
# Refs:
# - PyTorch CPU index: https://download.pytorch.org/whl/cpu
# - Get-started page (choose CPU): https://pytorch.org/get-started/locally/
