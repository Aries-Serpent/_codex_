#!/usr/bin/env bash
set -euo pipefail

pre-commit run --all-files
pytest
python -m build -n
mypy src
tmpdir=$(mktemp -d)
python -m venv "$tmpdir/venv"
. "$tmpdir/venv/bin/activate"
pip install . >/dev/null
python -c 'import codex'
deactivate
rm -rf "$tmpdir"
