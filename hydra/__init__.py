"""Expose the real Hydra package when available, otherwise provide a stub."""

from __future__ import annotations

import os
import sys
from importlib.machinery import PathFinder
from importlib.util import module_from_spec
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


def _load_real_hydra() -> ModuleType | None:
    """Attempt to load Hydra from outside the repository checkout."""

    stub_package_dir = Path(__file__).resolve().parent
    package_name = __name__.split(".", 1)[0]
    search_paths: list[str] = []
    for entry in sys.path:
        try:
            resolved = Path(entry).resolve()
        except OSError:
            # Some entries (e.g. namespace packages) may not resolve to a path.
            search_paths.append(entry)
            continue

        if resolved == stub_package_dir:
            continue

        try:
            candidate = resolved / package_name
        except TypeError:
            # Non-path entries such as import hooks may not support division.
            search_paths.append(entry)
            continue

        if candidate == stub_package_dir:
            continue
        search_paths.append(entry)

    spec = PathFinder.find_spec(__name__, search_paths)
    if spec is None or spec.loader is None:
        return None

    module = module_from_spec(spec)
    sys.modules[__name__] = module
    spec.loader.exec_module(module)
    return module


_should_force_stub = bool(os.environ.get("CODEX_FORCE_HYDRA_STUB"))
_real_hydra = None if _should_force_stub else _load_real_hydra()

if _real_hydra is not None:
    __doc__ = _real_hydra.__doc__
    __all__ = getattr(_real_hydra, "__all__", None)
    __spec__ = _real_hydra.__spec__
    __loader__ = _real_hydra.__loader__
    __package__ = _real_hydra.__package__
    __path__ = getattr(_real_hydra, "__path__", None)
    __file__ = getattr(_real_hydra, "__file__", None)

    for name, value in _real_hydra.__dict__.items():
        if name in {
            "__doc__",
            "__all__",
            "__spec__",
            "__loader__",
            "__package__",
            "__path__",
            "__file__",
        }:
            continue
        globals()[name] = value
else:

    def main(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func

        return decorator

    __all__ = ["main"]
