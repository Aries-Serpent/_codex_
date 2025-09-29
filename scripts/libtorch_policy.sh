#!/usr/bin/env bash
# Shared helpers for Torch policy validation flows.

# Decide which Torch policy component to use:
# - prefer Python module checker if available
# - otherwise fall back to the JSON-emitting script checker
choose_torch_policy_component() {
  python - <<'PY'
try:
    import codex_ml.utils.torch_checks as _C  # module-based checker
    print("module")
except Exception:
    print("script")
PY
}

torch_policy_module_check() {
  python - <<'PY'
from codex_ml.utils.torch_checks import inspect_torch, diagnostic_report
state = inspect_torch()
print("[torch-policy]", diagnostic_report(state))
import sys; sys.exit(0 if state.ok else 1)
PY
}
