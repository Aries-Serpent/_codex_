"""Expose the real OmegaConf package when available, otherwise provide a stub."""

from __future__ import annotations

import os
import sys
from importlib.machinery import PathFinder
from importlib.util import module_from_spec
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable, Mapping


def _load_real_omegaconf() -> ModuleType | None:
    """Attempt to load OmegaConf from outside the repository checkout."""

    stub_package_dir = Path(__file__).resolve().parent
    package_name = __name__.split(".", 1)[0]
    search_paths: list[str] = []
    for entry in sys.path:
        try:
            resolved = Path(entry).resolve()
        except OSError:
            # Some entries (e.g. namespace packages) may not resolve to a path.
            search_paths.append(entry)
            continue

        if resolved == stub_package_dir:
            continue

        try:
            candidate = resolved / package_name
        except TypeError:
            # Non-path entries such as import hooks may not support division.
            search_paths.append(entry)
            continue

        if candidate == stub_package_dir:
            continue
        search_paths.append(entry)

    spec = PathFinder.find_spec(__name__, search_paths)
    if spec is None or spec.loader is None:
        return None

    module = module_from_spec(spec)
    sys.modules[__name__] = module
    spec.loader.exec_module(module)
    return module


_should_force_stub = bool(os.environ.get("CODEX_FORCE_OMEGACONF_STUB"))
_real_omegaconf = None if _should_force_stub else _load_real_omegaconf()

if _real_omegaconf is not None:
    __doc__ = _real_omegaconf.__doc__
    __all__ = getattr(_real_omegaconf, "__all__", None)
    __spec__ = _real_omegaconf.__spec__
    __loader__ = _real_omegaconf.__loader__
    __package__ = _real_omegaconf.__package__
    __path__ = getattr(_real_omegaconf, "__path__", None)
    __file__ = getattr(_real_omegaconf, "__file__", None)

    for name, value in _real_omegaconf.__dict__.items():
        if name in {
            "__doc__",
            "__all__",
            "__spec__",
            "__loader__",
            "__package__",
            "__path__",
            "__file__",
        }:
            continue
        globals()[name] = value
else:
    try:  # pragma: no cover - optional dependency
        from yaml import safe_dump as _yaml_safe_dump_impl  # type: ignore
        from yaml import safe_load as _yaml_safe_load_impl
    except Exception:  # pragma: no cover - fallback when PyYAML is absent
        import json

        def _yaml_safe_load(data: str) -> Any:
            if not data.strip():
                return {}
            return json.loads(data)

        def _yaml_safe_dump(data: Mapping[str, Any]) -> str:
            return json.dumps(data, indent=2, sort_keys=True)

    else:

        def _yaml_safe_load(data: str) -> Any:
            return _yaml_safe_load_impl(data)

        def _yaml_safe_dump(data: Mapping[str, Any]) -> str:
            return _yaml_safe_dump_impl(data)

    class DictConfig(dict):
        """Simple dictionary-backed stand-in for OmegaConf's DictConfig."""

    def _merge_dicts(base: dict[str, Any], other: Mapping[str, Any]) -> dict[str, Any]:
        result = dict(base)
        for key, value in other.items():
            if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
                result[key] = _merge_dicts(result[key], value)  # type: ignore[arg-type]
            else:
                result[key] = value
        return result

    class OmegaConf:
        @staticmethod
        def to_container(cfg: Any, *, resolve: bool = False) -> Any:  # noqa: D401 - compatibility
            if isinstance(cfg, DictConfig):
                return dict(cfg)
            return cfg

        @staticmethod
        def to_object(cfg: Any) -> Any:
            return OmegaConf.to_container(cfg)

        @staticmethod
        def create(initial: Mapping[str, Any] | None = None) -> DictConfig:
            return DictConfig(dict(initial or {}))

        @staticmethod
        def from_dotlist(overrides: Iterable[str]) -> DictConfig:
            data: dict[str, Any] = {}
            for item in overrides:
                if "=" not in item:
                    continue
                key, value = item.split("=", 1)
                data[key.strip()] = value.strip()
            return DictConfig(data)

        @staticmethod
        def structured(obj: Any) -> Any:
            return obj

        @staticmethod
        def set_struct(cfg: Any, flag: bool) -> None:  # pragma: no cover - compatibility no-op
            return None

        @staticmethod
        def load(path: str | Path) -> DictConfig:
            content = Path(path).read_text(encoding="utf-8")
            data = _yaml_safe_load(content) or {}
            if not isinstance(data, Mapping):
                raise TypeError("OmegaConf.load expected mapping")
            return DictConfig(dict(data))

        @staticmethod
        def save(config: Mapping[str, Any], path: str | Path) -> None:
            Path(path).write_text(_yaml_safe_dump(dict(config)), encoding="utf-8")
        @staticmethod
        def merge(*configs: Mapping[str, Any]) -> DictConfig:
            merged: dict[str, Any] = {}
            for cfg in configs:
                if cfg is None:
                    continue
                if not isinstance(cfg, Mapping):
                    raise TypeError("OmegaConf.merge expects mapping inputs")
                merged = _merge_dicts(merged, cfg)
            return DictConfig(merged)

    class _MissingType:
        def __repr__(self) -> str:  # pragma: no cover - trivial
            return "MISSING"

    MISSING: Any = _MissingType()

    __all__ = ["DictConfig", "OmegaConf", "MISSING"]
