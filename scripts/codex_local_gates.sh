#!/usr/bin/env bash
set -euo pipefail

echo "[Codex] Running local offline gates..."

if [ -f "pyproject.toml" ]; then
  echo "[Codex] Ensuring development extras are installed (offline-friendly)..."
  python -m pip install --no-input --disable-pip-version-check -e .[dev] >/dev/null 2>&1 || \
    echo "[Codex] Failed to install dev extras (check Python/pip availability)."
fi

if command -v pre-commit >/dev/null 2>&1; then
  echo "[Codex] Running pre-commit hooks..."
  pre-commit run --all-files
else
  echo "[Codex] pre-commit not found on PATH; skipping hook execution."
fi

if command -v nox >/dev/null 2>&1; then
  echo "[Codex] Executing test suite via nox -s tests..."
  nox -s tests
else
  echo "[Codex] nox not available; skipping automated tests."
fi

python - <<'PYCODE'
"""Emit optional telemetry dependency status after gates."""
import importlib.util

optional_deps = ["psutil", "pynvml", "wandb", "mlflow"]
missing = [dep for dep in optional_deps if importlib.util.find_spec(dep) is None]
if missing:
    print(f"[Telemetry] Optional packages not installed: {', '.join(missing)}")
else:
    print("[Telemetry] All optional monitoring dependencies available.")
PYCODE

echo "[Codex] Gates complete (offline)."
