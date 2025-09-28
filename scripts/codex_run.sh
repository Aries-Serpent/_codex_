set -euo pipefail
export MLFLOW_OFFLINE=${MLFLOW_OFFLINE:-1}
python -m pip install -e .[test] || python -m pip install -r requirements.lock || true
python scripts/codex_orchestrate.py --audit "_codex_status_update-0C_base_-2025-09-27.md" \
  --patches "_codex_codex-ready-sequence-and-patches-2025-09-27.md" --run-full 0
