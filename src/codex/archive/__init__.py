"""Compatibility exports for legacy `codex.archive` imports."""

from __future__ import annotations

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_migrated_root = _pkg_root.parent.parent / "aries_serpent_core" / "archive"

__path__ = [str(_pkg_root)]
if _migrated_root.is_dir():
    __path__.append(str(_migrated_root))

try:
    from aries_serpent_core.archive import ArchiveService, restore, store  # noqa: F401
except Exception:  # pragma: no cover - keep compatibility package import-safe
    ArchiveService = None
    restore = store = None

__all__ = ["ArchiveService", "restore", "store"]
