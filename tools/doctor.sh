#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
import importlib, json, shutil
mods = ["pytest","pre_commit","pip_audit","semgrep"]
status = {m: bool(importlib.util.find_spec(m)) for m in mods}
bins = {b: bool(shutil.which(b)) for b in ["git","python","bash"]}
print(json.dumps({"python_ok": True, "mods": status, "bins": bins}, indent=2))
PY
. ./.venv/bin/activate || true
.venv/bin/pre-commit run --all-files || true
.venv/bin/pytest -q || true

