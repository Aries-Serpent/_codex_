#!/usr/bin/env bash
set -euo pipefail

echo "[*] Torch CPU repair starting"

# Activate local venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

PY="${UV_PYTHON:-${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}}"
PY="${PY:-python}"

echo "[*] Verifying import before reinstall..."
"$PY" - <<'PY'
try:
    import torch
    print("torch_version(before):", torch.__version__)
    print("torch_cuda(before):", getattr(getattr(torch, "version", None), "cuda", None))
except Exception as e:
    print("IMPORT_ERROR(before):", e)
PY

echo "[*] Forcing reinstall from PyTorch CPU index..."
PIP_INDEX_URL="https://download.pytorch.org/whl/cpu" \
UV_PYTHON="${PY}" \
uv pip install --reinstall "torch==2.8.0"

echo "[*] Verifying import after reinstall..."
"$PY" - <<'PY'
import torch
print("torch_version(after):", torch.__version__)
print("torch_cuda(after):", getattr(getattr(torch, "version", None), "cuda", None))
PY

echo "[*] Running policy check..."
python scripts/torch_policy_check.py

echo "[*] Torch CPU repair completed"

