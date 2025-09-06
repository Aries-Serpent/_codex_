#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
cd "$ROOT"

python -m venv .venv-smoke
source .venv-smoke/bin/activate
pip install --upgrade pip >/dev/null
pip install --no-cache-dir dist/*.whl >/dev/null
codex-infer --prompt "hello codex" --max-new-tokens 8 --device cpu || true
echo "Smoke run complete."
