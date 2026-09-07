"""Compatibility namespace for repo-level tool modules.

`pytest.ini` keeps the project on a src-first import contract (`pythonpath = src ...`).
The historical tool modules still live under the repository-root `tools/` directory,
so this package overlays that directory onto the import path without changing the
repo's canonical package layout.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

from .registry import ToolRegistry, get_registry, register_tool

_ROOT = Path(__file__).resolve().parents[2]
__path__ = [str(Path(__file__).resolve().parent), str(_ROOT / "tools")]

__all__ = ["ToolRegistry", "get_registry", "register_tool"]


def __getattr__(name: str):
    """Lazily resolve repo-root tool modules for `from tools import ...` imports."""
    if name.startswith("_"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        module = import_module(f"{__name__}.{name}")
    except ModuleNotFoundError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    globals()[name] = module
    return module
