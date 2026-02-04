"""Compatibility wrapper that re-exports :mod:`codex_ml.training` package symbols."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

_PACKAGE_NAME = "codex_ml.training"
_PACKAGE_DIR = Path(__file__).resolve().with_name("training")
_PACKAGE_PARENT = str(_PACKAGE_DIR.parent.parent)
_SCRIPT_DIR = str(_PACKAGE_DIR.parent)


def _ensure_parent_on_path() -> None:
    """Ensure the project root is available on ``sys.path`` for package imports."""

    while _SCRIPT_DIR in sys.path:
        sys.path.remove(_SCRIPT_DIR)
    if _PACKAGE_PARENT not in sys.path:
        sys.path.insert(0, _PACKAGE_PARENT)


def _load_package() -> ModuleType:
    """Import the real :mod:`codex_ml.training` package for compatibility."""

    existing = sys.modules.get(_PACKAGE_NAME)
    if existing is not None and existing is not sys.modules.get(__name__):
        return existing

    _ensure_parent_on_path()
    module = importlib.import_module(_PACKAGE_NAME)

    if module is sys.modules.get(__name__):
        spec = importlib.util.spec_from_file_location(
            _PACKAGE_NAME,
            _PACKAGE_DIR / "__init__.py",
            submodule_search_locations=[str(_PACKAGE_DIR)],
        )
        if spec is None or spec.loader is None:  # pragma: no cover - defensive programming
            raise ImportError(f"Unable to load {_PACKAGE_NAME} package for compatibility shim")
        module = importlib.util.module_from_spec(spec)
        sys.modules[_PACKAGE_NAME] = module
        spec.loader.exec_module(module)
    return module


_package = _load_package()
sys.modules[_PACKAGE_NAME] = _package

__doc__ = _package.__doc__
__package__ = _package.__package__
__all__ = list(getattr(_package, "__all__", []))

for name in __all__:
    globals()[name] = getattr(_package, name)


def __getattr__(name: str) -> Any:
    return getattr(_package, name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_package)))


if __name__ == "__main__":
    raise SystemExit(
        "codex_ml.training is now a package; run `python -m codex_ml.training` "
        "or import `codex_ml.training` instead of executing training.py directly."
    )
