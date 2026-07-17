"""Conftest for tests directory — ensure src/ is at sys.path[0].

This module ensures src/services is found before root-level services/
(which is a placeholder).  Without this, imports like::

    from src.services.workflow import WorkflowInventory

will resolve to the root-level placeholder instead of src/services/workflow/.

This is a P19 shadow-import fix (S679).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = str(_REPO_ROOT / "src")

# Ensure src/ is first on sys.path.
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

# Purge any cached 'services' entry so the fresh import finds src/services/
if "services" in sys.modules:
    del sys.modules["services"]
if "services.workflow" in sys.modules:
    del sys.modules["services.workflow"]
