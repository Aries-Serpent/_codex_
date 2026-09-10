"""Lightweight repo-local torch stub for optional dependency gating.

This stub intentionally shadows a missing real PyTorch install in CI or docs jobs,
while delegating transparently to the real installation when it is available.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_real_module() -> ModuleType | None:
    current_dir = Path(__file__).resolve().parent
    excluded = {current_dir, current_dir.parent}
    search_paths = []
    for entry in sys.path:
        try:
            resolved = Path(entry).resolve()
        except (OSError, RuntimeError, TypeError, ValueError):
            continue
        if resolved not in excluded:
            search_paths.append(entry)
    spec = importlib.machinery.PathFinder().find_spec("torch", search_paths)
    if spec is None or spec.loader is None:
        return None
    origin = getattr(spec, "origin", None)
    if origin and Path(origin).resolve() == Path(__file__).resolve():
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["torch"] = module
    spec.loader.exec_module(module)
    return module


_real = _load_real_module()
if _real is not None:
    globals().update({k: getattr(_real, k) for k in dir(_real) if not k.startswith("__")})
    __all__ = [k for k in dir(_real) if not k.startswith("__")]
else:
    IS_CODEX_STUB = True
    __version__ = "stub"

    class Tensor:
        """Minimal Tensor stand-in for type resolution and guardrails."""

        shape: tuple[int, ...] = ()
        dtype: Any = "float32"
        device: str = "cpu"
        ndim: int = 0
        requires_grad: bool = False

        def __init__(self, value: Any = None, *args: Any, **kwargs: Any) -> None:
            self._value = value
            self.grad = None

        def __repr__(self) -> str:
            return f"Tensor({self._value!r})"

        def __bool__(self) -> bool:
            return bool(self._value)

        def __iter__(self):
            if self._value is None:
                return iter(())
            return iter(self._value)

        def to(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def cuda(self, *args: Any, **kwargs: Any) -> "Tensor":
            self.device = "cuda"
            return self

        def cpu(self, *args: Any, **kwargs: Any) -> "Tensor":
            self.device = "cpu"
            return self

        @property
        def float(self) -> "Tensor":
            return self

        @property
        def half(self) -> "Tensor":
            return self

        def detach(self) -> "Tensor":
            return self

        def clone(self) -> "Tensor":
            return self

        def contiguous(self) -> "Tensor":
            return self

        def numpy(self) -> Any:
            return self._value

        def item(self) -> Any:
            return self._value

        def tolist(self) -> Any:
            return self._value

        def backward(self, *args: Any, **kwargs: Any) -> None:
            return None

        def size(self, dim: int | None = None) -> Any:
            if dim is None:
                return self.shape
            if not self.shape:
                raise IndexError("dimension out of range")
            try:
                return self.shape[dim]
            except IndexError as exc:  # pragma: no cover - defensive
                raise IndexError("dimension out of range") from exc

        def dim(self) -> int:
            return self.ndim

        def numel(self) -> int:
            return 1 if self.shape == () else 1

        def view(self, *shape: Any) -> "Tensor":
            return self

        def reshape(self, *shape: Any) -> "Tensor":
            return self

        def squeeze(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def unsqueeze(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def expand(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def permute(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def transpose(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def flatten(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def sum(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def mean(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def var(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def max(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def min(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def abs(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def argmax(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def clamp(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def softmax(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def sigmoid(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def tanh(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def fill_(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def zero_(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def requires_grad_(self, value: bool = True) -> "Tensor":
            self.requires_grad = value
            return self

    class no_grad:
        def __enter__(self) -> "no_grad":
            return self

        def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            return None

    def tensor(data: Any = None, *args: Any, **kwargs: Any) -> Tensor:
        return Tensor(data)

    def randn(*shape: Any, **kwargs: Any) -> Tensor:
        return Tensor()

    def manual_seed(seed: Any, *args: Any, **kwargs: Any) -> None:
        return None

    def save(obj: Any, path: str | None = None, **kwargs: Any) -> None:
        return None

    def load(path: str | None = None, **kwargs: Any) -> Any:
        return None

    def zeros(*shape: Any, **kwargs: Any) -> Tensor:
        return Tensor()

    def ones(*shape: Any, **kwargs: Any) -> Tensor:
        return Tensor()

    float32 = "float32"
    float16 = "float16"
    bfloat16 = "bfloat16"
    __all__ = [
        "Tensor",
        "tensor",
        "randn",
        "manual_seed",
        "save",
        "load",
        "zeros",
        "ones",
        "float32",
        "float16",
        "bfloat16",
        "no_grad",
        "nn",
    ]

    def __getattr__(name: str) -> Any:
        if name == "nn":
            import importlib

            module = importlib.import_module(".nn", __name__)
            return module
        raise AttributeError(f"module 'torch' has no attribute {name!r}")

    # Keep the stub importable for type checkers and optional-dependency guards.
    import importlib

    nn = importlib.import_module(".nn", __name__)
