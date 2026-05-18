"""Ensure the scripts/ package root is on sys.path before test collection.

Tests in this directory import top-level modules from scripts/ directly
(e.g. ``from run_sweep import ...``).  Rather than each test file inserting
the path itself, this conftest handles it once so the individual test
modules only need plain imports.

This centralised management also prevents future path-shadow regressions:
if a new ``scripts/<name>/`` subdirectory would shadow a ``src/`` package,
it only needs to be fixed here rather than in N test files.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_ROOT = str(Path(__file__).resolve().parents[2] / "scripts")
if _SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, _SCRIPTS_ROOT)
