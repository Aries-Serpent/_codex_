"""Compatibility shim that defers to real PyTorch when available.

This module exists so tests that do not depend on PyTorch can still execute in
environments where the dependency is unavailable. When PyTorch is installed we
remove the repository root from ``sys.path`` temporarily and import the real
package, preventing the stub from shadowing it. If the import fails we expose a
minimal subset of the API used by the lightweight tests.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib.abc import Loader
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Tuple

__all__: list[str]


def _load_real_module(name: str) -> ModuleType | None:
    module_path = Path(__file__).resolve()
    repo_root = module_path.parent.parent.resolve()
    module_parts = Path(*name.split("."))
    loader_name = f"_codex_real_{name.replace('.', '_')}"

    candidate_roots: list[Path] = []
    for entry in sys.path:
        try:
            path_obj = Path(entry).resolve()
        except Exception:  # pragma: no cover - guard against non-path entries
            continue
        if path_obj == repo_root:
            continue
        candidate_roots.append(path_obj)

    site_packages = [
        repo_root
        / ".venv"
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages",
        repo_root
        / "venv"
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages",
    ]
    candidate_roots.extend(site for site in site_packages if site.exists())

    seen: set[str] = set()
    unique_roots: list[Path] = []
    for root in candidate_roots:
        key = str(root)
        if key in seen:
            continue
        seen.add(key)
        unique_roots.append(root)

    for root in unique_roots:
        package_dir = root / module_parts
        init_py = package_dir / "__init__.py"
        if init_py.exists() and init_py.resolve() != module_path:
            spec = importlib.util.spec_from_file_location(
                loader_name,
                init_py,
                submodule_search_locations=[str(package_dir)],
            )
        else:
            module_py = package_dir.with_suffix(".py")
            if not module_py.exists() or module_py.resolve() == module_path:
                continue
            spec = importlib.util.spec_from_file_location(loader_name, module_py)

        if not spec or spec.loader is None:
            continue
        if not isinstance(spec.loader, Loader):
            continue

        loader = spec.loader
        module = importlib.util.module_from_spec(spec)
        module.__package__ = name
        module.__name__ = name
        if module.__spec__ is not None:
            module.__spec__.name = name
        sys.modules[loader_name] = module

        original_module = sys.modules.pop(name, None)
        removed_sys_path: list[tuple[int, str]] = []
        for index in range(len(sys.path) - 1, -1, -1):
            entry = sys.path[index]
            try:
                entry_path = Path(entry).resolve()
            except Exception:  # pragma: no cover - guard against invalid entries
                continue
            if entry_path == repo_root:
                removed_sys_path.append((index, entry))
                del sys.path[index]

        sys.modules[name] = module

        try:
            loader.exec_module(module)
        except Exception:  # pragma: no cover - fall back to stub on failure
            sys.modules.pop(loader_name, None)
            if original_module is not None:
                sys.modules[name] = original_module
            else:
                sys.modules.pop(name, None)
            for index, entry in sorted(removed_sys_path):
                sys.path.insert(index, entry)
            continue

        for index, entry in sorted(removed_sys_path):
            sys.path.insert(index, entry)
        sys.modules.pop(loader_name, None)
        return module
    return None


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
    __version__ = "0.0.0-offline"

del _real_module
del _load_real_module
