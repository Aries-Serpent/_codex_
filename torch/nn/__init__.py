"""Minimal ``torch.nn`` stub used when PyTorch is unavailable."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterable, Iterator


def _load_real_module() -> ModuleType | None:
    current_path = Path(__file__).resolve()
    current_dir = current_path.parent
    current_root = current_dir.parent
    search_paths = [
        p
        for p in sys.path
        if Path(p).resolve() not in {current_dir, current_root}
    ]
    spec = importlib.machinery.PathFinder().find_spec(__name__, search_paths)
    if spec is None or spec.loader is None:
        return None
    origin = getattr(spec, "origin", None)
    if origin and Path(origin).resolve() == current_path:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[__name__] = module
    try:
        spec.loader.exec_module(module)
    except Exception:  # pragma: no cover - exercised when PyTorch is broken/missing pieces
        sys.modules.pop(__name__, None)
        return None
    return module


_real = _load_real_module()

if _real is not None:  # pragma: no cover - exercised when PyTorch is installed
    globals().update({k: getattr(_real, k) for k in dir(_real) if not k.startswith("__")})
    __all__ = [k for k in dir(_real) if not k.startswith("__")]
else:  # pragma: no cover - used in the lightweight testing environment

    class Module:
        """Best-effort replacement for :class:`torch.nn.Module`."""

        training: bool

        def __init__(self) -> None:
            self.training = True

        def forward(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise NotImplementedError("torch stub does not implement Module.forward")

        def __call__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return self.forward(*args, **kwargs)

        def train(self, mode: bool = True) -> "Module":
            self.training = bool(mode)
            return self

        def eval(self) -> "Module":
            return self.train(False)

        def parameters(self) -> Iterable["Parameter"]:
            return ()

        def state_dict(self) -> dict[str, object]:
            return {}

        def load_state_dict(self, state_dict, strict: bool = True):  # type: ignore[no-untyped-def]
            return state_dict

        def to(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return self

        def cpu(self) -> "Module":
            return self

        def cuda(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise RuntimeError("CUDA is not available in the torch stub")

    class Parameter:
        """Very small stand-in for :class:`torch.nn.Parameter`."""

        def __init__(self, data=None, requires_grad: bool = True):
            self.data = data
            self.requires_grad = requires_grad

        def to(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return self

    def _iterate_tensors(sequence) -> Iterator[Parameter]:  # type: ignore[no-untyped-def]
        for value in sequence or ():
            if isinstance(value, Parameter):
                yield value

    class _UtilsModule(ModuleType):
        def __init__(self) -> None:
            super().__init__("torch.nn.utils")

        @staticmethod
        def clip_grad_norm_(parameters, max_norm, norm_type=2.0):  # type: ignore[no-untyped-def]
            total_params = sum(1 for _ in _iterate_tensors(parameters))
            return float(total_params)

    utils = _UtilsModule()
    sys.modules.setdefault("torch.nn.utils", utils)

    __all__ = ["Module", "Parameter", "utils"]

    package = sys.modules.setdefault(__name__, sys.modules[__name__])
    package.__path__ = [str(Path(__file__).resolve().parent)]
