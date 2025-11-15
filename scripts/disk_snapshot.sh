#!/usr/bin/env bash
set -euo pipefail

echo "[disk] Virtualenv size (if present):"
du -sh .venv 2>/dev/null || echo "no .venv"

echo "[disk] Repo root size:"
du -sh "$(pwd)" | awk '{print "[disk-root] "$0}'

echo "[pip] Vendor package presence:"
pip list --format=columns | grep -E '^(nvidia-|triton|torchtriton|torch|transformers|tokenizers|safetensors|scipy|pandas|matplotlib|scikit-learn|statsmodels)\b' || true

echo "[df] Filesystem:"
df -h