"""Compatibility package for the legacy `codex.cli` import contract."""

from __future__ import annotations

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_migrated_root = _pkg_root.parent.parent / "aries_serpent_core"

__path__ = [str(_pkg_root)]
if _migrated_root.is_dir():
    __path__.append(str(_migrated_root))

from aries_serpent_core.cli import ALLOWED_TASKS, cli, logs  # noqa: F401
from aries_serpent_core.cli import _fix_pool  # noqa: F401

try:
    from aries_serpent_core.cli import app  # noqa: F401
except Exception:  # pragma: no cover - optional Typer app
    app = cli

try:
    from aries_serpent_core.cli import main  # noqa: F401
except Exception:  # pragma: no cover - legacy alias
    main = cli

__all__ = ["ALLOWED_TASKS", "app", "cli", "logs", "main", "_fix_pool"]
