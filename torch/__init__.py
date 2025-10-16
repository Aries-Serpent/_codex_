"""Lightweight stub for optional dependency ``torch``.

Runtime shim to provide a minimal PyTorch surface when the real wheel is
missing. The real PyTorch wheel is large and not always available in minimal
CI environments. This shim mirrors the behaviour of the ``transformers`` stub:
it delegates to the actual library when installed and otherwise exposes the
handful of symbols used in the offline smoke tests.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


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
    module = importlib.util.module_from_spec(spec)
    sys.modules[__name__] = module
    spec.loader.exec_module(module)
    return module


class _StubDType:
    def __init__(self, name: str) -> None:
        self._name = name

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<missing dtype {self._name}>"


_real = _load_real_module()

if _real is not None:
    globals().update({k: getattr(_real, k) for k in dir(_real) if not k.startswith("__")})
    __all__ = [k for k in dir(_real) if not k.startswith("__")]
else:  # pragma: no cover - exercised in minimal test envs
    float32 = _StubDType("torch.float32")
    float16 = _StubDType("torch.float16")
    bfloat16 = _StubDType("torch.bfloat16")
    utils = ModuleType("torch.utils")
    data = ModuleType("torch.utils.data")

    class Dataset:  # pragma: no cover - minimal stub
        pass

    data.Dataset = Dataset  # type: ignore[attr-defined]
    utils.data = data  # type: ignore[attr-defined]
    sys.modules.setdefault("torch.utils", utils)
    sys.modules.setdefault("torch.utils.data", data)

    __version__ = "0.0.0-stub"

    def manual_seed(seed: int) -> int:  # pragma: no cover - deterministic stub
        return seed

    class _CudaModule:
        @staticmethod
        def is_available() -> bool:
            return False

        @staticmethod
        def manual_seed_all(seed: int) -> None:
            return None

    cuda = _CudaModule()

    __all__ = ["bfloat16", "float16", "float32", "utils"]
    __path__ = []  # type: ignore[assignment]
