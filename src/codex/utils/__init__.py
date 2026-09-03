"""Codex utilities namespace compatibility layer.

This package intentionally exposes the distributed legacy ``codex.utils`` module
name while the real implementation lives under ``aries_serpent_core.utils``.
The package path must include both locations so direct imports such as
``from codex.utils.path_utils import sanitize_filename`` resolve correctly.
"""

from __future__ import annotations

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_migrated_root = _pkg_root.parent.parent / "aries_serpent_core" / "utils"

__path__ = [str(_pkg_root)]
if _migrated_root.is_dir():
    __path__.append(str(_migrated_root))

try:  # pragma: no cover - optional migration surface
    from aries_serpent_core.utils import *  # noqa: F401,F403
    from aries_serpent_core.utils.path_utils import sanitize_filename, windows_safe_timestamp
except ImportError:  # pragma: no cover - compatibility fallback
    sanitize_filename = None  # type: ignore[assignment]
    windows_safe_timestamp = None  # type: ignore[assignment]

__all__ = [
    "sanitize_filename",
    "windows_safe_timestamp",
]
