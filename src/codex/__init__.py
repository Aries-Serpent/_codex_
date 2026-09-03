"""Unified Codex namespace package.

This package maps `from codex.*` imports to actual modules in src/.
"""

from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

# Re-export version if available
try:
    __version__ = version("codex-ml")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]

# Include both the live `codex` package directory and the migrated
# `aries_serpent_core` namespace so legacy `codex.*` imports continue to work
# while the codebase is being transitioned.
_src_root = Path(__file__).resolve().parent.parent
_legacy_root = _src_root / "aries_serpent_core"
__path__ = [str(Path(__file__).resolve().parent)]
if _legacy_root.is_dir():
    __path__.append(str(_legacy_root))

# Ensure src/ is in sys.path so relative imports work
if str(_src_root) not in sys.path:
    sys.path.insert(0, str(_src_root))
