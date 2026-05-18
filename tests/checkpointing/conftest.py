"""Ensure the scripts/ package root is on sys.path before test collection.

Tests in this directory import top-level scripts directly (e.g.
``from list_checkpoints import ...``).  Centralising the path insertion here
prevents each test file from having module-level ``sys.path.insert`` calls.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_ROOT = str(Path(__file__).resolve().parents[2] / "scripts")
if _SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, _SCRIPTS_ROOT)
