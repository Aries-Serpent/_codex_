"""Compatibility package for the repository's shared utility modules.

The canonical implementation now lives under ``src/utils`` while some legacy
imports still resolve this package from the repo root.  Include both locations in
``__path__`` so ``utils.log_sanitizer`` and similar imports keep working across
sandbox and pytest execution contexts.
"""

from __future__ import annotations

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_src_utils_root = _pkg_root.parent / "src" / "utils"
_legacy_utils_root = _pkg_root.parent / "src" / "aries_serpent_core" / "utils"

__path__ = [str(_pkg_root)]
for candidate in (_src_utils_root, _legacy_utils_root):
    if candidate.is_dir():
        __path__.append(str(candidate))

from .safe_pickle import RestrictedUnpickler, safe_pickle_dump, safe_pickle_load
from .safe_torch_loader import safe_load
from .torch_resource_manager import cleanup_torch_resources, torch_resource_guard

__all__ = [
    "safe_load",
    "torch_resource_guard",
    "cleanup_torch_resources",
    "safe_pickle_load",
    "safe_pickle_dump",
    "RestrictedUnpickler",
]
