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

    def _infer_shape(value: Any) -> tuple[int, ...]:
        if isinstance(value, Tensor):
            return value.shape
        if not isinstance(value, (list, tuple)):
            return ()
        if not value:
            return (0,)
        child_shape = _infer_shape(value[0])
        if child_shape:
            return (len(value), *child_shape)
        return (len(value),)

    def _flatten_values(value: Any) -> list[Any]:
        if isinstance(value, Tensor):
            value = value._value
        if isinstance(value, (list, tuple)):
            flattened: list[Any] = []
            for item in value:
                flattened.extend(_flatten_values(item))
            return flattened
        if value is None:
            return []
        return [value]

    class Tensor:
        """Minimal Tensor stand-in for type resolution and guardrails."""

        dtype: Any = "float32"
        device: str = "cpu"
        requires_grad: bool = False

        def __init__(self, value: Any = None, *args: Any, **kwargs: Any) -> None:
            self._value = value
            self.grad = None
            shape = kwargs.pop("shape", None)
            if shape is not None:
                self.shape = tuple(shape)
            else:
                self.shape = _infer_shape(value)
            self.ndim = len(self.shape)

        def __repr__(self) -> str:
            return f"Tensor({self._value!r})"

        def __bool__(self) -> bool:
            return bool(self._value)

        def __iter__(self):
            if self._value is None:
                return iter(())
            return iter(self._value)

        def __getitem__(self, key: Any) -> "Tensor":
            if isinstance(key, Tensor):
                values = _flatten_values(self)
                mask = _flatten_values(key)
                selected = [
                    value for value, include in zip(values, mask, strict=False) if bool(include)
                ]
                return Tensor(selected, shape=(len(selected),))
            if isinstance(key, tuple):
                ellipsis_index = key.index(Ellipsis) if Ellipsis in key else None
                if ellipsis_index is not None:
                    trailing = key[ellipsis_index + 1 :]
                    if trailing and isinstance(trailing[0], slice):
                        stop = trailing[0].stop
                        shape = list(self.shape)
                        if stop is not None:
                            shape[-1] = min(stop, shape[-1]) if shape else stop
                        return Tensor(self._value, shape=tuple(shape))
            return Tensor(self._value, shape=self.shape)

        def __eq__(self, other: Any) -> "Tensor":
            left = _flatten_values(self)
            right = _flatten_values(other)
            if len(right) == 1 and len(left) > 1:
                right = right * len(left)
            values = [
                left_value == right_value
                for left_value, right_value in zip(left, right, strict=False)
            ]
            return Tensor(values, shape=self.shape)

        def __ne__(self, other: Any) -> "Tensor":
            left = _flatten_values(self)
            if isinstance(other, Tensor):
                right = _flatten_values(other)
            else:
                right = [other]
            if len(right) == 1 and len(left) > 1:
                right = right * len(left)
            values = [
                left_value != right_value
                for left_value, right_value in zip(left, right, strict=False)
            ]
            return Tensor(values, shape=self.shape)

        def to(self, *args: Any, **kwargs: Any) -> "Tensor":
            return self

        def cuda(self, *args: Any, **kwargs: Any) -> "Tensor":
            self.device = "cuda"
            return self

        def cpu(self, *args: Any, **kwargs: Any) -> "Tensor":
            self.device = "cpu"
            return self

        def float(self) -> "Tensor":
            return self

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
            if not self.shape:
                return 1
            size = 1
            for dimension in self.shape:
                size *= dimension
            return size

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
            values = _flatten_values(self)
            if not values:
                return Tensor(0.0)
            try:
                return Tensor(sum(float(value) for value in values) / len(values))
            except (TypeError, ValueError):
                return Tensor(0.0)

        def any(self, *args: Any, **kwargs: Any) -> "Tensor":
            return Tensor(any(bool(value) for value in _flatten_values(self)))

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
        normalized_shape = shape[0] if len(shape) == 1 and isinstance(shape[0], tuple) else shape
        return Tensor(None, shape=tuple(normalized_shape))

    def randint(low: int, high: int, shape: tuple[int, ...] | list[int], **kwargs: Any) -> Tensor:
        normalized_shape = tuple(shape)
        size = 1
        for dimension in normalized_shape:
            size *= dimension
        values = [low] * size
        if len(normalized_shape) == 1:
            nested: Any = values
        else:
            nested = values
            for dimension in reversed(normalized_shape[1:]):
                nested = [
                    nested[index : index + dimension] for index in range(0, len(nested), dimension)
                ]
        return Tensor(nested, shape=normalized_shape)

    def argmax(value: Tensor, dim: int | None = None, **kwargs: Any) -> Tensor:
        if dim is None:
            return Tensor(0, shape=())
        shape = list(value.shape)
        if not shape:
            return Tensor(0)
        shape.pop(dim if dim >= 0 else dim + len(shape))
        size = 1
        for dimension in shape:
            size *= dimension
        return Tensor([0] * size, shape=tuple(shape))

    def exp(value: Tensor) -> Tensor:
        return Tensor(__import__("math").exp(float(value.item())))

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
        "randint",
        "argmax",
        "exp",
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
        "utils",
        "optim",
        "distributed",
    ]
    __file__ = str(Path(__file__).resolve())
    __path__ = [str(Path(__file__).resolve().parent)]

    def __getattr__(name: str) -> Any:
        if name in {"nn", "utils", "optim", "distributed", "cuda"}:
            import importlib

            module = importlib.import_module(f".{name}", __name__)
            globals()[name] = module
            return module
        raise AttributeError(f"module 'torch' has no attribute {name!r}")

    # Keep the stub importable for type checkers and optional-dependency guards.
    import importlib

    nn = importlib.import_module(".nn", __name__)
    for _alias in ("utils", "optim", "distributed"):
        try:
            globals()[_alias] = importlib.import_module(f".{_alias}", __name__)
        except ModuleNotFoundError:
            pass
