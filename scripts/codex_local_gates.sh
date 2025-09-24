#!/usr/bin/env bash
# Hardened local gate: fail fast on any unmet prerequisite.
set -Eeuo pipefail
trap 'code=$?; echo "[Codex][gates][ERROR] line ${BASH_LINENO[0]} exited with ${code}" >&2; exit $code' ERR

# Optional: uncomment for verbose debugging
# set -x

echo "[Codex][gates] Running local offline gates..."

# Install dev dependencies (editable + extras)
python -m pip install --disable-pip-version-check -U pip setuptools wheel
python -m pip install -e .[dev]

# Sanity: dependency graph is consistent (non-zero on conflicts)
python -m pip check

# Configure Hugging Face caches/offline flags following the official guidance so
# Transformers never try to reach the network during gates. The environment
# variables mirror https://huggingface.co/docs/transformers/main/installation .
: "${HF_HOME:=${HOME}/.cache/huggingface}"
export HF_HOME
export HF_HUB_CACHE="${HF_HUB_CACHE:-${HF_HOME}/hub}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-${HF_HOME}/transformers}"
export HF_DATASETS_CACHE="${HF_DATASETS_CACHE:-${HF_HOME}/datasets}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export HF_DATASETS_OFFLINE="${HF_DATASETS_OFFLINE:-1}"

mkdir -p "$HF_HOME" "$HF_HUB_CACHE" "$TRANSFORMERS_CACHE" "$HF_DATASETS_CACHE"

python - <<'HFCONFIG'
"""Emit the effective offline cache configuration for quick debugging."""
import os

prefix = "[gates][HF]"
for key in (
    "HF_HOME",
    "HF_HUB_CACHE",
    "TRANSFORMERS_CACHE",
    "HF_DATASETS_CACHE",
    "TRANSFORMERS_OFFLINE",
    "HF_HUB_OFFLINE",
    "HF_DATASETS_OFFLINE",
):
    print(f"{prefix} {key}={os.getenv(key)}")
HFCONFIG

# Refresh command cache in case PATH changed during installs.
if command -v pyenv >/dev/null 2>&1; then
    pyenv rehash
fi
hash -r

for cli in pre-commit nox; do
    if ! command -v "$cli" >/dev/null 2>&1; then
        echo "[gates] Required CLI '$cli' not found on PATH after dev install." >&2
        exit 1
    fi
    echo "[gates] Verified CLI dependency: $cli"
done

python - <<'PYCHECK'
"""Ensure critical pytest plugins are importable before running gates."""
import importlib.util
import sys

missing = [name for name in ("pytest", "pytest_cov") if importlib.util.find_spec(name) is None]
if missing:
    print(f"[Codex][gates] Missing python packages: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)
PYCHECK

python - <<'TORCHCHECK'
"""Fail fast when PyTorch is a stub lacking torch.utils.data.Dataset."""
import sys
from codex_ml.utils.torch_checks import diagnostic_report, inspect_torch

status = inspect_torch()
print(f"[gates] Torch check: {diagnostic_report(status)}")
if not status.ok:
    print("[gates][ERROR] Incomplete PyTorch install detected."
          " Reinstall official CPU wheels via:"
          " python -m pip install torch torchvision torchaudio --index-url"
          " https://download.pytorch.org/whl/cpu",
          file=sys.stderr)
    sys.exit(1)
TORCHCHECK

echo "[gates] Running pre-commit hooks..."
pre-commit run --all-files

echo "[gates] Executing test suite via nox -s tests..."
nox -s tests

python - <<'PYCODE'
"""Report availability of optional telemetry dependencies."""
import importlib.util

optional = ["psutil", "pynvml", "wandb", "mlflow"]
missing = [dep for dep in optional if importlib.util.find_spec(dep) is None]
if missing:
    print(f"[Codex][Telemetry] Optional packages not installed: {', '.join(missing)}")
else:
    print("[Codex][Telemetry] All optional monitoring dependencies available.")
PYCODE

echo "[Codex][gates] Gates complete (offline)."