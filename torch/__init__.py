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

    # Stub Tensor class for compatibility with scipy and other libraries
    class Tensor:  # pragma: no cover
        """Stub Tensor class to prevent errors in scipy array API compat checks."""
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
