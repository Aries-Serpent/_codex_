"""Hydra shim that prefers the real package when available."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import warnings
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterator, Sequence

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
    try:
        importlib.import_module("hydra.extra")
        return
    except ModuleNotFoundError as exc:  # pragma: no cover - optional plugin guard
        if importlib.util.find_spec("hydra.extra") is not None:
            _handle_missing_hydra_extra(exc)
            return
        _install_hydra_extra_stub(exc)
    except Exception as exc:  # pragma: no cover - guard for optional plugin
        _handle_missing_hydra_extra(exc)


def _install_hydra_extra_stub(original_exc: Exception) -> None:
    try:
        importlib.import_module("hydra_extra")
    except Exception as stub_exc:  # pragma: no cover - guard for optional plugin
        _handle_missing_hydra_extra(stub_exc)
        return

    try:
        importlib.import_module("hydra.extra")
    except Exception:  # pragma: no cover - guard for optional plugin
        _handle_missing_hydra_extra(original_exc)


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
    if not hasattr(_real_module, "_ensure_hydra_extra"):
        setattr(_real_module, "_ensure_hydra_extra", _ensure_hydra_extra)
    sys.modules[__name__] = _real_module
    _ensure_hydra_extra()
else:
    _handle_missing_hydra_extra()
    __all__ = ["main", "compose", "initialize_config_dir"]
    __path__ = [str(Path(__file__).resolve().parent)]

    _CONFIG_STACK: list[Path] = []

    def main(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                return func(*f_args, **f_kwargs)

            return wrapper

        return decorator

    @contextmanager
    def initialize_config_dir(
        *, version_base: str | None = None, config_dir: str | os.PathLike[str]
    ) -> Iterator[None]:
        cfg_dir = Path(config_dir).expanduser().resolve()
        if not cfg_dir.is_dir():
            raise FileNotFoundError(f"Hydra config directory not found: {cfg_dir}")
        _CONFIG_STACK.append(cfg_dir)
        try:
            yield
        finally:
            _CONFIG_STACK.pop()

    def compose(*, config_name: str, overrides: Sequence[str] | None = None):
        if not _CONFIG_STACK:
            raise RuntimeError(
                "initialize_config_dir must be used before compose in the Hydra stub"
            )
        cfg_dir = _CONFIG_STACK[-1]
        cfg_path = cfg_dir / f"{config_name}.yaml"
        if not cfg_path.exists():
            from hydra.errors import MissingConfigException

            raise MissingConfigException(
                missing_cfg_file=str(cfg_path),
                message=f"Config '{config_name}' not found under {cfg_dir}",
                config_name=config_name,
            )

        from codex_ml.utils.yaml_support import MissingPyYAMLError, safe_load
        from omegaconf import OmegaConf

        try:
            data = safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        except MissingPyYAMLError as exc:
            raise RuntimeError(
                "PyYAML is required to parse Hydra configuration files. Install PyYAML to use the stub compose API."
            ) from exc

        cfg = OmegaConf.create(data)
        for item in overrides or ():
            if "=" not in item:
                raise ValueError(f"Invalid Hydra override '{item}' (expected key=value)")
            key, value = item.split("=", 1)
            try:
                parsed = safe_load(value)
            except MissingPyYAMLError as exc:
                raise RuntimeError(
                    "PyYAML is required to parse Hydra overrides when using the stub compose API."
                ) from exc
            OmegaConf.update(cfg, key, parsed, merge=True)
        return cfg


del _real_module
del _load_real_module
