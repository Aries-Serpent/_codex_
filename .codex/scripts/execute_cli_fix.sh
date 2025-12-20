#!/usr/bin/env bash
set -euo pipefail

echo "== Gate 0: Preconditions =="
python --version
python -m pip --version

echo "== Gate 1: Install package editable =="
python -m pip install -e ".[test]"

echo "== Gate 2: Verify deterministic imports =="
python - <<'PY'
from codex.cli import cli, app, main
print("codex.cli.cli:", type(cli))
print("codex.cli.app:", type(app))
print("codex.cli.main callable:", callable(main))
PY

echo "== Gate 3: Validate export surface =="
if [ -f ".codex/scripts/validate_cli_exports.py" ]; then
    python .codex/scripts/validate_cli_exports.py
else
    echo "Warning: .codex/scripts/validate_cli_exports.py not found; skipping export surface validation."
fi

echo "== Gate 4: Run failing test module =="
pytest tests/cli/test_codex_cli.py -q

echo "✅ All gates passed"
