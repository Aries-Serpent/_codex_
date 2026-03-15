"""Lightweight stub for optional dependency ``torch``.

Runtime shim used in environments where the real PyTorch wheel is unavailable.
When PyTorch is installed we delegate to the actual library. Otherwise we
surface a clear ``ImportError`` so downstream modules can fall back to their
existing "PyTorch required" guardrails.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import NoReturn


def _load_real_module() -> ModuleType | None:
    current_path = Path(__file__).resolve()
    current_dir = current_path.parent
    current_root = current_dir.parent
    search_paths = [p for p in sys.path if Path(p).resolve() not in {current_dir, current_root}]
    spec = importlib.machinery.PathFinder().find_spec("torch", search_paths)
    if spec is None or spec.loader is None:
        return None
    origin = getattr(spec, "origin", None)
    if origin and Path(origin).resolve() == current_path:
        return None
    try:
        module = importlib.util.module_from_spec(spec)
        # Temporarily store this stub in sys.modules during loading
        stub_backup = sys.modules.get(__name__)
        sys.modules[__name__] = module
        try:
            spec.loader.exec_module(module)
            return module
        except (ImportError, OSError):
            # If torch fails to load, restore the stub
            if stub_backup is not None:
                sys.modules[__name__] = stub_backup
            else:
                sys.modules.pop(__name__, None)
            return None
    except Exception:
        # Any other error, just return None
        return None


_real = _load_real_module()

if _real is not None:
    globals().update({k: getattr(_real, k) for k in dir(_real) if not k.startswith("__")})
    __all__ = [k for k in dir(_real) if not k.startswith("__")]

    def __getattr__(name: str):  # type: ignore[misc]
        """Delegate attribute lookups to real torch; also handles subpackage access.

        PyTorch subpackages (e.g. ``torch.utils``, ``torch.nn``) are only
        populated in the package's namespace after they have been explicitly
        imported.  ``dir(torch)`` therefore does not list them even when the
        package is installed, so the ``globals().update()`` call above misses
        them.  This hook catches those accesses and imports the subpackage on
        demand.
        """
        # 1. Try the real module first (catches most cases after lazy init)
        try:
            val = getattr(_real, name)
            globals()[name] = val  # cache for subsequent access
            return val
        except AttributeError:
            pass
        # 2. Try importing as a subpackage (e.g. torch.utils, torch.nn)
        try:
            import importlib as _imp
            val = _imp.import_module(f"torch.{name}")
            globals()[name] = val
            return val
        except ImportError:
            pass
        raise AttributeError(f"module 'torch' has no attribute {name!r}")

else:  # pragma: no cover - exercised in minimal test envs
    _MISSING_MSG = (
        "PyTorch is not installed in this environment. Install torch to enable these features."
    )
    __all__: list[str] = ["nn", "utils", "Tensor"]
    IS_CODEX_STUB = True

    # Stub Tensor class with all common attributes mypy needs to resolve.
    # Covers every attribute referenced in src/ so mypy can type-check without
    # the real torch wheel installed.
    class Tensor:  # pragma: no cover
        """Stub Tensor class — all common attributes present for mypy resolution."""

        from typing import Any as _Any

        shape: tuple[int, ...] = ()
        dtype: "_Any" = None
        device: "_Any" = None
        ndim: int = 0
        requires_grad: bool = False
        grad: "_Any" = None
        data: "_Any" = None

        def __init__(self, *args: "_Any", **kwargs: "_Any") -> None: ...  # type: ignore[misc]

        def __iter__(self) -> "_Any": ...  # type: ignore[misc]
        def __len__(self) -> int: ...  # type: ignore[misc]
        def __getitem__(self, idx: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def __setitem__(self, idx: "_Any", val: "_Any") -> None: ...  # type: ignore[misc]
        def __add__(self, other: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def __radd__(self, other: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def __sub__(self, other: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def __mul__(self, other: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def __truediv__(self, other: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def __neg__(self) -> "Tensor": ...  # type: ignore[misc]
        def __matmul__(self, other: "_Any") -> "Tensor": ...  # type: ignore[misc]

        def to(self, *args: "_Any", **kwargs: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def cuda(self, device: "_Any" = None) -> "Tensor": ...  # type: ignore[misc]
        def cpu(self) -> "Tensor": ...  # type: ignore[misc]
        def float(self) -> "Tensor": ...  # type: ignore[misc]
        def half(self) -> "Tensor": ...  # type: ignore[misc]
        def double(self) -> "Tensor": ...  # type: ignore[misc]
        def int(self) -> "Tensor": ...  # type: ignore[misc]
        def long(self) -> "Tensor": ...  # type: ignore[misc]
        def bool(self) -> "Tensor": ...  # type: ignore[misc]
        def detach(self) -> "Tensor": ...  # type: ignore[misc]
        def clone(self) -> "Tensor": ...  # type: ignore[misc]
        def contiguous(self) -> "Tensor": ...  # type: ignore[misc]
        def numpy(self) -> "_Any": ...  # type: ignore[misc]
        def item(self) -> "_Any": ...  # type: ignore[misc]
        def tolist(self) -> "_Any": ...  # type: ignore[misc]
        def backward(self, *args: "_Any", **kwargs: "_Any") -> None: ...  # type: ignore[misc]

        def size(self, dim: "int | None" = None) -> "_Any": ...  # type: ignore[misc]
        def dim(self) -> int: ...  # type: ignore[misc]
        def numel(self) -> int: ...  # type: ignore[misc]

        def view(self, *shape: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def reshape(self, *shape: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def squeeze(self, dim: "int | None" = None) -> "Tensor": ...  # type: ignore[misc]
        def unsqueeze(self, dim: int) -> "Tensor": ...  # type: ignore[misc]
        def expand(self, *sizes: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def permute(self, *dims: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def transpose(self, dim0: int, dim1: int) -> "Tensor": ...  # type: ignore[misc]
        def flatten(self, *args: "_Any") -> "Tensor": ...  # type: ignore[misc]

        def sum(self, *args: "_Any", **kwargs: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def mean(self, *args: "_Any", **kwargs: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def var(self, *args: "_Any", **kwargs: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def max(self, *args: "_Any", **kwargs: "_Any") -> "_Any": ...  # type: ignore[misc]
        def min(self, *args: "_Any", **kwargs: "_Any") -> "_Any": ...  # type: ignore[misc]
        def abs(self) -> "Tensor": ...  # type: ignore[misc]
        def argmax(self, *args: "_Any", **kwargs: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def clamp(self, *args: "_Any", **kwargs: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def softmax(self, dim: int) -> "Tensor": ...  # type: ignore[misc]
        def sigmoid(self) -> "Tensor": ...  # type: ignore[misc]
        def tanh(self) -> "Tensor": ...  # type: ignore[misc]

        def fill_(self, value: "_Any") -> "Tensor": ...  # type: ignore[misc]
        def zero_(self) -> "Tensor": ...  # type: ignore[misc]
        def requires_grad_(self, requires_grad: bool = True) -> "Tensor": ...  # type: ignore[misc]

    def _raise_missing(*args, **kwargs):  # pragma: no cover
        raise AttributeError(_MISSING_MSG)

    # No-op seed function (tests call torch.manual_seed without needing real torch)
    def manual_seed(seed=None):  # pragma: no cover
        return None

    # Stub cuda sub-module used by torch.cuda.manual_seed_all etc.
    import types as _types
    cuda = _types.SimpleNamespace(
        is_available=lambda: False,
        manual_seed=lambda seed=None: None,
        manual_seed_all=lambda seed=None: None,
    )
    # Stub backends sub-module used by transformers' is_torch_mps_available()
    backends = _types.SimpleNamespace(
        mps=_types.SimpleNamespace(
            is_available=lambda: False,
            is_built=lambda: False,
        ),
        cudnn=_types.SimpleNamespace(
            enabled=False,
            benchmark=False,
            deterministic=False,
            is_available=lambda: False,
        ),
        cuda=_types.SimpleNamespace(is_available=lambda: False),
    )
    del _types  # keep namespace clean

    # Stub factory functions that tests commonly call via pytest.importorskip("torch")
    ones = _raise_missing
    zeros = _raise_missing
    randn = _raise_missing
    randint = _raise_missing
    tensor = _raise_missing
    arange = _raise_missing
    cat = _raise_missing
    stack = _raise_missing

    def __getattr__(name: str):
        """Provide stub submodules or raise AttributeError."""
        # Allow importing submodules
        if name in ("nn", "utils"):
            import importlib
            return importlib.import_module(f"torch.{name}")
        # Provide Tensor class for compatibility
        if name == "Tensor":
            return Tensor
        # Everything else raises error
        raise AttributeError(_MISSING_MSG)

    def __dir__() -> list[str]:  # pragma: no cover - simple stub helper
        return ["nn", "utils", "Tensor", "ones", "zeros", "randn", "randint", "tensor"]
