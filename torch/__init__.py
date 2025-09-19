"""Compatibility shim that defers to real PyTorch when available.

This module exists so tests that do not depend on PyTorch can still execute in
environments where the dependency is unavailable. When PyTorch is installed we
remove the repository root from ``sys.path`` temporarily and import the real
package, preventing the stub from shadowing it. If the import fails we expose a
minimal subset of the API used by the lightweight tests.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import List

_repo_root = Path(__file__).resolve().parent.parent

_original_sys_path: List[str] = list(sys.path)
_filtered_sys_path: List[str] = []
for entry in _original_sys_path:
    resolved = Path(entry or ".").resolve()
    if resolved == _repo_root:
        continue
    _filtered_sys_path.append(entry)

_stub_module = sys.modules.get(__name__)

_real_torch: ModuleType | None = None
try:
    if _stub_module is not None:
        del sys.modules[__name__]
    sys.path = _filtered_sys_path
    _real_torch = importlib.import_module("torch")
except ImportError:
    _real_torch = None
finally:
    sys.path = _original_sys_path

if _real_torch is not None:
    sys.modules[__name__] = _real_torch
else:
    if _stub_module is not None:
        sys.modules[__name__] = _stub_module
    __version__ = "0.0"

    def manual_seed(seed: int) -> None:  # pragma: no cover - stub
        return None

    class _Cuda:
        @staticmethod
        def is_available() -> bool:
            return False

        @staticmethod
        def manual_seed_all(seed: int) -> None:  # pragma: no cover - stub
            return None

    cuda = _Cuda()

    __all__ = ["cuda", "manual_seed", "__version__"]
