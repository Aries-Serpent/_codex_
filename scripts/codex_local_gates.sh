#!/usr/bin/env bash
# Fail fast, including inside functions/subshells; print failing line & status.
set -Eeuo pipefail
trap 'code=$?; echo "[gates][ERROR] line ${BASH_LINENO[0]} exited with ${code}" >&2; exit $code' ERR

# Optional: uncomment for verbose debug
# set -x

echo "[gates] Running local offline gates..."

# Install dev dependencies (editable + extras)
python -m pip install --disable-pip-version-check -U pip setuptools wheel
python -m pip install -e .[dev]

# Sanity: dependency graph is consistent (non-zero on conflicts)
python -m pip check

# Rehash command cache in case PATH changed
hash -r

# Assert required CLIs exist (hard fail if any missing)
command -v pre-commit >/dev/null
command -v nox >/dev/null

echo "[gates] Verified CLI dependencies (pre-commit, nox)"

# Assert required python plugins import cleanly (hard fail if missing)
python - <<'PYCHECK'
import importlib, sys
missing = [m for m in ("pytest", "pytest_cov") if importlib.util.find_spec(m) is None]
if missing:
    print(f"[gates] missing python packages: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)
PYCHECK

echo "[gates] Running pre-commit hooks..."
# Pre-commit on all files (scoped by config)
pre-commit run --all-files

echo "[gates] Executing test suite via nox -s tests..."
# Run tests with coverage via nox
nox -s tests

python - <<'PYCODE'
import importlib
optional = ["psutil", "pynvml", "wandb", "mlflow"]
missing = [d for d in optional if importlib.util.find_spec(d) is None]
if missing:
    print(f"[Telemetry] Optional packages not installed: {', '.join(missing)}")
else:
    print("[Telemetry] All optional monitoring dependencies available.")
PYCODE

echo "[gates] Gates complete (offline)."
