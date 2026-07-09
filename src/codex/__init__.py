"""Unified Codex namespace package.

This package maps `from codex.*` imports to actual modules in src/.
"""

from __future__ import annotations

# Re-export version if available
try:
    from codex_ml import __version__
except (ImportError, AttributeError):
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]

# Set __path__ to include the codex package directory so submodules can be found
import sys
from pathlib import Path

__path__ = [str(Path(__file__).parent)]

# Ensure src/ is in sys.path so relative imports work
_src = Path(__file__).parent.parent
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))
