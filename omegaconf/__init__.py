"""Expose the real OmegaConf package when available, otherwise provide a stub."""

from __future__ import annotations

import os
import sys
from importlib.machinery import PathFinder
from importlib.util import module_from_spec
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_real_omegaconf() -> ModuleType | None:
    """Attempt to load OmegaConf from outside the repository checkout."""

    stub_dir = Path(__file__).resolve().parent
    repo_root = stub_dir.parent
    search_paths: list[str] = []
    for entry in sys.path:
        try:
            resolved = Path(entry).resolve()
        except OSError:
            # Some entries (e.g. namespace packages) may not resolve to a path.
            search_paths.append(entry)
            continue

        try:
            if resolved == repo_root:
                continue
            if resolved == stub_dir or resolved.is_relative_to(stub_dir):
                continue
        except AttributeError:
            resolved_str = os.fsdecode(resolved)
            stub_prefix = os.fsdecode(stub_dir) + os.sep
            if resolved == repo_root or resolved == stub_dir:
                continue
            if resolved_str.startswith(stub_prefix):
                continue
        search_paths.append(entry)

    spec = PathFinder.find_spec(__name__, search_paths)
    if spec is None or spec.loader is None:
        return None

    module = module_from_spec(spec)
    sys.modules[__name__] = module
    spec.loader.exec_module(module)
    return module


_should_force_stub = bool(os.environ.get("CODEX_FORCE_OMEGACONF_STUB"))
_real_omegaconf = None if _should_force_stub else _load_real_omegaconf()

if _real_omegaconf is not None:
    __doc__ = _real_omegaconf.__doc__
    __all__ = getattr(_real_omegaconf, "__all__", None)
    __spec__ = _real_omegaconf.__spec__
    __loader__ = _real_omegaconf.__loader__
    __package__ = _real_omegaconf.__package__
    __path__ = getattr(_real_omegaconf, "__path__", None)
    __file__ = getattr(_real_omegaconf, "__file__", None)

    for name, value in _real_omegaconf.__dict__.items():
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

    class _MissingType:
        def __repr__(self) -> str:  # pragma: no cover - trivial
            return "MISSING"

    MISSING: Any = _MissingType()

    __all__ = ["MISSING"]
