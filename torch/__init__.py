"""Compatibility shim that defers to real PyTorch when available.

This module exposes a lightweight stub only when the real dependency cannot be
imported. When PyTorch is installed we temporarily remove the repository root
from ``sys.path`` and re-import the actual package so production code continues
to work as expected.
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

    from types import SimpleNamespace
    from typing import Any, Tuple

    __version__ = "0.0"

    __all__ = [
        "Tensor",
        "tensor",
        "manual_seed",
        "cuda",
        "topk",
        "where",
        "zeros_like",
        "full_like",
        "full",
        "multinomial",
        "sort",
        "cumsum",
        "softmax",
        "cat",
    ]

    class Tensor:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self._args = args
            self._kwargs = kwargs

        def clone(self) -> "Tensor":  # pragma: no cover - simple stub
            return Tensor(*self._args, **self._kwargs)

        def size(self, dim: int | None = None):  # pragma: no cover - simple stub
            if dim is None:
                return (len(self._args),)
            return 1

        def to(self, *_args: Any, **_kwargs: Any) -> "Tensor":
            return self

        @property
        def device(self) -> str:  # pragma: no cover - simple stub
            return "cpu"

    def tensor(*args: Any, **kwargs: Any) -> Tensor:
        return Tensor(*args, **kwargs)

    def manual_seed(_seed: int) -> None:  # pragma: no cover - deterministic stub
        return None

    def topk(*args: Any, **kwargs: Any) -> Tuple[Tensor, Tensor]:
        return Tensor(*args, **kwargs), Tensor(*args, **kwargs)

    def where(*args: Any, **kwargs: Any) -> Tensor:
        return Tensor(*args, **kwargs)

    def zeros_like(*_args: Any, **_kwargs: Any) -> Tensor:
        return Tensor()

    def full_like(*_args: Any, **_kwargs: Any) -> Tensor:
        return Tensor()

    def full(shape: Tuple[int, ...], value: float, device: str | None = None) -> Tensor:
        return Tensor(shape, value, device=device)

    def multinomial(*_args: Any, **_kwargs: Any) -> Tensor:
        return Tensor()

    def sort(*_args: Any, **_kwargs: Any) -> Tuple[Tensor, Tensor]:
        return Tensor(), Tensor()

    def cumsum(*_args: Any, **_kwargs: Any) -> Tensor:
        return Tensor()

    def softmax(tensor_in: Tensor, dim: int = -1) -> Tensor:
        return tensor_in

    def cat(tensors: Any, dim: int = 0) -> Tensor:
        return Tensor(tensors, dim)

    class _CudaModule(SimpleNamespace):
        def is_available(self) -> bool:  # pragma: no cover - offline stub
            return False

        def manual_seed_all(self, _seed: int) -> None:  # pragma: no cover
            return None

    cuda = _CudaModule()
