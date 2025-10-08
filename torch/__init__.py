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
from types import ModuleType, SimpleNamespace
from typing import Any, Tuple

__all__: list[str]


def _load_real_module(name: str) -> ModuleType | None:
    module_path = Path(__file__).resolve()
    repo_root = module_path.parent.parent.resolve()
    removed: list[tuple[int, str]] = []
    for index in range(len(sys.path) - 1, -1, -1):
        entry = sys.path[index]
        try:
            entry_path = Path(entry).resolve()
        except Exception:  # pragma: no cover - defensive
            continue
        if entry_path == repo_root:
            removed.append((index, entry))
            del sys.path[index]
    original = sys.modules.pop(name, None)
    try:
        module = importlib.import_module(name)
        return module
    except Exception:  # pragma: no cover - real module unavailable
        if original is not None:
            sys.modules[name] = original
        return None
    finally:
        if original is not None and name not in sys.modules:
            sys.modules[name] = original
        for index, entry in sorted(removed):
            sys.path.insert(index, entry)


_real_module = _load_real_module("torch")

if _real_module is not None:
    globals().update(_real_module.__dict__)
    __all__ = list(
        getattr(
            _real_module,
            "__all__",
            [
                name
                for name in _real_module.__dict__
                if not name.startswith("__") or name in {"__version__", "__doc__"}
            ],
        )
    )
    __path__ = list(getattr(_real_module, "__path__", []))
    sys.modules[__name__] = _real_module
else:
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

    __version__ = "0.0"
    __all__.append("__version__")

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

    def _not_impl(*_args: Any, **_kwargs: Any) -> Tensor:  # pragma: no cover - guard
        raise NotImplementedError("torch operations not available in offline stub")

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

    class _Dataset:  # pragma: no cover - minimal stub
        def __iter__(self):
            return iter(())

        def __len__(self) -> int:
            return 0

    cuda = _CudaModule()
    utils_module = ModuleType("torch.utils")
    data_module = ModuleType("torch.utils.data")
    setattr(data_module, "Dataset", _Dataset)
    setattr(utils_module, "data", data_module)
    sys.modules["torch.utils"] = utils_module
    sys.modules["torch.utils.data"] = data_module
    utils = utils_module
    __version__ = "0.0.0-offline"

del _real_module
del _load_real_module
