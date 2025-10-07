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
    removed: list[tuple[int, str]] = []
    for index in range(len(sys.path) - 1, -1, -1):
        entry = sys.path[index]
        try:
            path_obj = Path(entry).resolve()
        except Exception:  # pragma: no cover - guard against non-path entries
            continue
        if path_obj == repo_root:
            removed.append((index, entry))
            del sys.path[index]

    original = sys.modules.pop(name, None)
    try:
        module = importlib.import_module(name)
        return module
    except Exception:  # pragma: no cover - fall back to stub on failure
        if original is not None:
            sys.modules[name] = original
        return None
    finally:
        if original is not None and name not in sys.modules:
            sys.modules[name] = original
        for index, entry in sorted(removed):
            sys.path.insert(index, entry)


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
        requested = Path(config_dir).expanduser()
        cwd = Path.cwd().resolve()
        cfg_dir = requested if requested.is_absolute() else (cwd / requested).resolve()
        if not cfg_dir.is_dir():
            repo_root = Path(__file__).resolve().parent.parent
            try:
                relative = requested.relative_to(cwd)
            except ValueError:
                relative = requested.name if requested.is_absolute() else requested
            candidate = (repo_root / relative).resolve()
            if candidate.is_dir():
                cfg_dir = candidate
            else:
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
        defaults = cfg.get("defaults")
        if isinstance(defaults, list):
            normalised: list[dict[str, object]] = []
            for item in defaults:
                if isinstance(item, dict):
                    normalised.append(dict(item))
                elif isinstance(item, str):
                    if item.strip() == "_self_":
                        normalised.append({"_self_": True})
                    else:
                        normalised.append({item: True})
                else:
                    normalised.append({str(item): True})
            OmegaConf.update(cfg, "defaults", normalised, merge=False)
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
