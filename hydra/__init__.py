"""Hydra shim that prefers the real package when available."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import warnings
from functools import wraps
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

__all__: list[str]


def _load_real_hydra() -> ModuleType | None:
    """Attempt to load Hydra from outside the repository checkout."""


_HYDRA_EXTRA_MESSAGE = (
    "Hydra extras plugin (`hydra.extra`) is unavailable. Install the Codex test "
    "extras (e.g. `pip install -e '.[test]'`) or `hydra-core==1.3.2` before running "
    "Hydra-backed commands. Set CODEX_ALLOW_MISSING_HYDRA_EXTRA=1 to bypass this "
    "guard when stubbing Hydra for tests."
)


def _is_pytest_context() -> bool:
    return "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ


def _allow_missing_hydra_extra() -> bool:
    flag = os.environ.get("CODEX_ALLOW_MISSING_HYDRA_EXTRA")
    if flag is not None and flag.strip():
        return flag.strip().lower() not in {"0", "false", "no"}
    return _is_pytest_context()


def _handle_missing_hydra_extra(exc: Exception | None = None) -> None:
    if _allow_missing_hydra_extra():
        warnings.warn(_HYDRA_EXTRA_MESSAGE, RuntimeWarning, stacklevel=3)
        return
    raise ModuleNotFoundError(_HYDRA_EXTRA_MESSAGE) from exc


def _ensure_hydra_extra() -> None:
    last_exc: Exception | None = None
    for module_name in ("hydra.extra.pytest_plugin", "hydra.extra", "hydra_extra"):
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError as exc:  # pragma: no cover - guard for optional plugin
            last_exc = exc
            continue
        except Exception as exc:  # pragma: no cover - unexpected import failure
            last_exc = exc
            break
        else:
            return
    _handle_missing_hydra_extra(last_exc)


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
            origin_path = str(init_py)
            spec = importlib.util.spec_from_file_location(
                loader_name,
                init_py,
                submodule_search_locations=[str(package_dir)],
            )
        else:
            module_py = package_dir.with_suffix(".py")
            if not module_py.exists() or module_py.resolve() == module_path:
                continue
            origin_path = str(module_py)
            spec = importlib.util.spec_from_file_location(loader_name, module_py)

        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules.setdefault(loader_name, module)
            previous = sys.modules.get(name)
            try:
                sys.modules[name] = module
                spec.loader.exec_module(module)  # type: ignore[arg-type]
            except Exception:  # pragma: no cover - fall back to stub on failure
                if previous is not None:
                    sys.modules[name] = previous
                else:
                    sys.modules.pop(name, None)
                sys.modules.pop(loader_name, None)
                continue
            else:
                sys.modules.pop(loader_name, None)

            parent, _, _ = name.rpartition(".")
            module.__name__ = name
            module.__package__ = name if spec.submodule_search_locations else parent
            if spec.submodule_search_locations:
                module.__path__ = list(spec.submodule_search_locations)
            module.__loader__ = spec.loader
            module.__spec__ = importlib.util.spec_from_file_location(
                name,
                origin_path,
                submodule_search_locations=(
                    list(spec.submodule_search_locations)
                    if spec.submodule_search_locations
                    else None
                ),
            )
            sys.modules.pop(loader_name, None)
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
    _ensure_hydra_extra()
else:
    _handle_missing_hydra_extra()
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
