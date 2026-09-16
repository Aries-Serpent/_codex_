"""Repo-local data assets are not an importable Python package.

This directory holds offline test fixtures and generated seed material, not the
real third-party ``datasets`` library. Import resolution from the repo root must
not silently mask the package installed in the active environment.

When the real dependency is present, prefer it. Otherwise raise a clear error that
points callers to ``pytest.importorskip("datasets")`` for optional test paths.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_MODULE_NAME = "datasets"


def _find_real_module():
    """Return the real third-party datasets package when one is installed."""
    search_paths: list[str] = []
    for entry in sys.path:
        if not entry:
            continue
        try:
            resolved = Path(entry).resolve()
        except (OSError, RuntimeError, TypeError, ValueError):
            continue
        if resolved == _REPO_ROOT or resolved == _REPO_ROOT.parent:
            continue
        if any(
            resolved == root or resolved.is_relative_to(root)
            for root in {_REPO_ROOT, _REPO_ROOT.parent}
        ):
            continue
        search_paths.append(entry)

    spec = importlib.machinery.PathFinder().find_spec(_MODULE_NAME, search_paths)
    if spec is None or spec.loader is None:
        return None
    origin = getattr(spec, "origin", None)
    if origin:
        try:
            origin_path = Path(origin).resolve()
        except (OSError, RuntimeError, TypeError, ValueError):
            origin_path = None
        if origin_path and (
            origin_path == Path(__file__).resolve()
            or origin_path.is_relative_to(_REPO_ROOT)
        ):
            return None
    return spec


_real_spec = _find_real_module()
if _real_spec is not None:
    module = importlib.util.module_from_spec(_real_spec)
    sys.modules[_MODULE_NAME] = module
    _real_spec.loader.exec_module(module)
    globals().update({k: getattr(module, k) for k in dir(module) if not k.startswith("__")})
    __all__ = list(getattr(module, "__all__", []))
else:
    raise ModuleNotFoundError(
        "The repo-local 'datasets' directory is not a Python package. "
        "Install the real 'datasets' library or use pytest.importorskip('datasets') "
        "for optional-dependency tests."
    )
