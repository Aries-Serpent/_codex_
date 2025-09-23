#!/usr/bin/env bash
# Hardened local gate: fail fast on any unmet prerequisite.
set -Eeuo pipefail
trap 'code=$?; echo "[Codex][gates][ERROR] line ${BASH_LINENO[0]} exited with ${code}" >&2; exit $code' ERR

# Uncomment for verbose debugging
# set -x

echo "[Codex] Running local offline gates..."

python -m pip install --disable-pip-version-check -U pip setuptools wheel
python -m pip install -e .[dev]
python -m pip check

# Refresh command cache in case PATH changed during installs.
hash -r

for cli in pre-commit nox; do
  if ! command -v "$cli" >/dev/null 2>&1; then
    echo "[Codex][gates] Required CLI '$cli' not found on PATH after dev install." >&2
    exit 1
  fi
  echo "[Codex] Verified CLI dependency: $cli"
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

echo "[Codex] Running pre-commit hooks..."
pre-commit run --all-files

echo "[Codex] Executing test suite via nox -s tests..."
nox -s tests

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
