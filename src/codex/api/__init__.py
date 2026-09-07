"""Compatibility exports for legacy `codex.api` imports."""

from __future__ import annotations

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_migrated_root = _pkg_root.parent.parent / "aries_serpent_core" / "api"

__path__ = [str(_pkg_root)]
if _migrated_root.is_dir():
    __path__.append(str(_migrated_root))

try:
    from aries_serpent_core.api import app  # noqa: F401
except Exception:  # pragma: no cover - optional app dependency
    app = None

__all__ = ["app"]
