"""Compatibility shim that defers to real PyTorch when available.

This module exists so tests that do not depend on PyTorch can still execute in
environments where the dependency is unavailable. When PyTorch is installed we
remove the repository root from ``sys.path`` temporarily and import the real
package, preventing the stub from shadowing it. If the import fails we expose a
minimal subset of the API used by the lightweight tests.
"""

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

    cuda = _CudaModule()

    cuda = _CudaModule()

del _real_module
del _load_real_module
