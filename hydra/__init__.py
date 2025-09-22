"""Hydra shim that prefers the real package when available."""

from __future__ import annotations

import importlib.util
import sys
from functools import wraps
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

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
            spec = importlib.util.spec_from_file_location(loader_name, init_py)
        else:
            module_py = package_dir.with_suffix(".py")
            if not module_py.exists() or module_py.resolve() == module_path:
                continue
            spec = importlib.util.spec_from_file_location(loader_name, module_py)

        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules.setdefault(loader_name, module)
            try:
                spec.loader.exec_module(module)  # type: ignore[arg-type]
            except Exception:  # pragma: no cover - fall back to stub on failure
                sys.modules.pop(loader_name, None)
                continue
            return module
    return None


_real_module = _load_real_module("hydra")

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
    __all__ = ["main"]

    def main(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                return func(*f_args, **f_kwargs)

            return wrapper

        return decorator


del _real_module
del _load_real_module
