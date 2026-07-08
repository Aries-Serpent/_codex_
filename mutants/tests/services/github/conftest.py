"""
Conftest for tests/services/github — ensures src/ is on sys.path so that
``from services.github.client import ...`` resolves to src/services/github/client.py
and not to any root-level placeholder.

P19 shadow-import fix (S679): The root-level services/github/__init__.py is a
placeholder that can shadow src/services/github/ if REPO_ROOT is searched before
src/ on sys.path.  This conftest pins src/ at sys.path[0] and purges any wrong
``services`` or ``services.github`` cache entry before tests run.
"""

from __future__ import annotations

import pathlib
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_SRC = str(_REPO_ROOT / "src")

# Ensure src/ is first on sys.path.
sys.path[:] = [p for p in sys.path if p != _SRC]
sys.path.insert(0, _SRC)

# Also ensure repo root is at the end so ``src.services.*`` imports work.
_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.append(_REPO_ROOT_STR)

# Evict any stale services / services.github entries that point to the
# root-level placeholder instead of src/services/.
for _key in list(sys.modules.keys()):
    if _key == "services" or _key.startswith("services."):
        _mod = sys.modules[_key]
        _origin = getattr(_mod, "__file__", None) or ""
        if _origin and not _origin.startswith(_SRC):
            del sys.modules[_key]
