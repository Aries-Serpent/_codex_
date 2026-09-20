"""Compatibility shim for repo-root tool entrypoints.

The canonical implementation lives under ``src/tools``; this root-level package
keeps legacy CLI paths such as ``python tools/template_lint.py`` working while
preserving the modern src-first layout.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

from src.tools.registry import ToolRegistry, get_registry, register_tool

_ROOT = Path(__file__).resolve().parents[1]
__path__ = [str(Path(__file__).resolve().parent), str(_ROOT / "src" / "tools")]
__all__ = ["ToolRegistry", "get_registry", "register_tool"]


def __getattr__(name: str):
    """Lazily resolve modules from the src-first tool tree."""
    if name.startswith("_"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        module = import_module(f"{__name__}.{name}")
    except ModuleNotFoundError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    globals()[name] = module
    return module
