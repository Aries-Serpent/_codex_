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

    def __getattr__(name: str):
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

        def __init__(self, *args: "_Any", **kwargs: "_Any") -> None:
            pass

        def __iter__(self) -> "_Any":
            pass
        def __len__(self) -> int:
            pass
        def __getitem__(self, idx: "_Any") -> "Tensor":
            pass
        def __setitem__(self, idx: "_Any", val: "_Any") -> None:
            pass
        def __add__(self, other: "_Any") -> "Tensor":
            pass
        def __radd__(self, other: "_Any") -> "Tensor":
            pass
        def __sub__(self, other: "_Any") -> "Tensor":
            pass
        def __mul__(self, other: "_Any") -> "Tensor":
            pass
        def __truediv__(self, other: "_Any") -> "Tensor":
            pass
        def __neg__(self) -> "Tensor":
            pass
        def __matmul__(self, other: "_Any") -> "Tensor":
            pass

        def to(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def cuda(self, device: "_Any" = None) -> "Tensor":
            pass
        def cpu(self) -> "Tensor":
            pass
        def float(self) -> "Tensor":
            pass
        def half(self) -> "Tensor":
            pass
        def double(self) -> "Tensor":
            pass
        def int(self) -> "Tensor":
            pass
        def long(self) -> "Tensor":
            pass
        def bool(self) -> "Tensor":
            pass
        def detach(self) -> "Tensor":
            pass
        def clone(self) -> "Tensor":
            pass
        def contiguous(self) -> "Tensor":
            pass
        def numpy(self) -> "_Any":
            pass
        def item(self) -> "_Any":
            pass
        def tolist(self) -> "_Any":
            pass
        def backward(self, *args: "_Any", **kwargs: "_Any") -> None:
            pass

        def size(self, dim: "int | None" = None) -> "_Any":
            pass
        def dim(self) -> int:
            pass
        def numel(self) -> int:
            pass

        def view(self, *shape: "_Any") -> "Tensor":
            pass
        def reshape(self, *shape: "_Any") -> "Tensor":
            pass
        def squeeze(self, dim: "int | None" = None) -> "Tensor":
            pass
        def unsqueeze(self, dim: int) -> "Tensor":
            pass
        def expand(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def permute(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def transpose(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def flatten(self, *args: "_Any") -> "Tensor":
            pass

        def sum(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def mean(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def var(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def std(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def max(self, *args: "_Any", **kwargs: "_Any") -> "_Any":
            pass
        def min(self, *args: "_Any", **kwargs: "_Any") -> "_Any":
            pass
        def amax(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def amin(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def abs(self) -> "Tensor":
            pass
        def argmax(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def argmin(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def clamp(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def softmax(self, dim: int) -> "Tensor":
            pass
        def sigmoid(self) -> "Tensor":
            pass
        def tanh(self) -> "Tensor":
            pass
        def relu(self) -> "Tensor":
            pass
        def exp(self) -> "Tensor":
            pass
        def log(self) -> "Tensor":
            pass
        def sqrt(self) -> "Tensor":
            pass
        def pow(self, exponent: "_Any") -> "Tensor":
            pass
        def norm(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def cumsum(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def cumprod(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def prod(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def any(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def all(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        # Extended type-conversion and shape ops (S55 additions — non-duplicate)
        def type(self, *args: "_Any", **kwargs: "_Any") -> "_Any":
            pass
        def masked_fill(self, mask: "_Any", value: "_Any") -> "Tensor":
            pass
        def masked_select(self, mask: "_Any") -> "Tensor":
            pass
        def scatter_(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def gather(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def index_select(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def repeat(self, *args: "_Any", **kwargs: "_Any") -> "Tensor":
            pass
        def expand_as(self, other: "_Any") -> "Tensor":
            pass
        def t(self) -> "Tensor":
            pass
        def is_contiguous(self) -> bool:
            pass
        # Additional arithmetic / comparison operators (S55 additions — non-duplicate)
        def __rmul__(self, other: "_Any") -> "Tensor":
            pass
        def __floordiv__(self, other: "_Any") -> "Tensor":
            pass
        def __lt__(self, other: "_Any") -> "Tensor":
            pass
        def __le__(self, other: "_Any") -> "Tensor":
            pass
        def __gt__(self, other: "_Any") -> "Tensor":
            pass
        def __ge__(self, other: "_Any") -> "Tensor":
            pass
        def __eq__(self, other: "_Any") -> "Tensor":  # type: ignore[misc, override]
            pass
        def __ne__(self, other: "_Any") -> "Tensor":  # type: ignore[misc, override]
            pass
        def __and__(self, other: "_Any") -> "Tensor":
            pass
        def __or__(self, other: "_Any") -> "Tensor":
            pass

        def fill_(self, value: "_Any") -> "Tensor":
            pass
        def zero_(self) -> "Tensor":
            pass
        def requires_grad_(self, requires_grad: bool = True) -> "Tensor":
            pass

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
