"""Lightweight stub for optional dependency ``transformers``.

This module allows the offline test matrix to run without installing the
heavyweight Hugging Face stack.  When the real library is available it is
imported transparently; otherwise minimal stand-ins are provided so that
``pytest.importorskip("transformers")`` passes while still surfacing clear
errors if any functionality is exercised.
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
    search_paths = [p for p in sys.path if Path(p).resolve() != current_dir]
    spec = importlib.machinery.PathFinder().find_spec("transformers", search_paths)
    if spec is None or spec.loader is None:
        return None
    origin = getattr(spec, "origin", None)
    if origin and Path(origin).resolve() == current_path:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[__name__] = module
    spec.loader.exec_module(module)
    return module


class _Stub:
    def __init__(self, target: str) -> None:
        self._target = target

    def __call__(self, *args, **kwargs):  # pragma: no cover - defensive
        raise ImportError(
            f"Optional dependency '{self._target}' is not installed; "
            "install transformers to enable this functionality."
        )

    def __getattr__(self, name: str):  # pragma: no cover - defensive
        raise ImportError(
            f"Optional dependency '{self._target}' is not installed; "
            "install transformers to enable this functionality."
        )


_real = _load_real_module()

if _real is not None:
    globals().update({k: getattr(_real, k) for k in dir(_real) if not k.startswith("__")})
    __all__ = [k for k in dir(_real) if not k.startswith("__")]
else:  # pragma: no cover - exercised in minimal test envs
    AutoModelForCausalLM = _Stub("transformers.AutoModelForCausalLM")
    AutoTokenizer = _Stub("transformers.AutoTokenizer")
    __all__ = ["AutoModelForCausalLM", "AutoTokenizer"]
    __path__ = []  # type: ignore[assignment]
