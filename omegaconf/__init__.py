"""OmegaConf shim that defers to the real package when available."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable, Mapping

__all__: list[str]


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


_real_module = _load_real_module("omegaconf")

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
    from yaml import safe_dump, safe_load  # type: ignore

    __all__ = ["DictConfig", "OmegaConf", "MISSING"]

    class _MissingSentinel:
        def __repr__(self) -> str:  # pragma: no cover - simple repr
            return "MISSING"

    MISSING = _MissingSentinel()

    class DictConfig(dict):
        """Simple dictionary-backed stand-in for OmegaConf's DictConfig."""

        def __init__(self, initial: Mapping[str, Any] | None = None) -> None:
            super().__init__()
            if initial:
                for key, value in initial.items():
                    super().__setitem__(key, self._convert(value))

        @staticmethod
        def _convert(value: Any) -> Any:
            if isinstance(value, Mapping) and not isinstance(value, DictConfig):
                return DictConfig(value)
            if isinstance(value, list):
                # Convert list elements recursively for nested structures
                return [_to_dictconfig(v) for v in value]
            return value

        def __getattr__(self, item: str) -> Any:
            try:
                return self[item]
            except KeyError as exc:  # pragma: no cover - attribute fallback
                raise AttributeError(item) from exc

        def __setattr__(self, key: str, value: Any) -> None:
            if key.startswith("_"):
                super().__setattr__(key, value)
            else:
                self[key] = value

        def __setitem__(self, key: str, value: Any) -> None:
            super().__setitem__(key, self._convert(value))

        def __getitem__(self, key: str) -> Any:
            value = super().__getitem__(key)
            if isinstance(value, Mapping) and not isinstance(value, DictConfig):
                value = DictConfig(value)
                super().__setitem__(key, value)
            return value

        def get(self, key: str, default: Any = None) -> Any:
            if key in self:
                return self[key]
            return default

    def _to_dictconfig(value: Any) -> Any:
        if isinstance(value, DictConfig):
            return value
        if isinstance(value, Mapping):
            return DictConfig({k: _to_dictconfig(v) for k, v in value.items()})
        if isinstance(value, list):
            return [_to_dictconfig(v) for v in value]
        return value

    def _merge_dicts(base: Mapping[str, Any], other: Mapping[str, Any]) -> DictConfig:
        result: DictConfig = DictConfig(base)
        for key, value in other.items():
            if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
                result[key] = _merge_dicts(result[key], value)  # type: ignore[arg-type]
            else:
                result[key] = _to_dictconfig(value)
        return result

    class OmegaConf:
        @staticmethod
        def to_container(cfg: Any, *, resolve: bool = False) -> Any:  # noqa: D401 - compatibility
            if isinstance(cfg, DictConfig):
                return {k: OmegaConf.to_container(v, resolve=resolve) for k, v in cfg.items()}
            if isinstance(cfg, list):
                return [OmegaConf.to_container(v, resolve=resolve) for v in cfg]
            return cfg

        @staticmethod
        def to_object(cfg: Any) -> Any:
            return OmegaConf.to_container(cfg)

        @staticmethod
        def create(initial: Mapping[str, Any] | None = None) -> DictConfig:
            return DictConfig({k: _to_dictconfig(v) for k, v in (initial or {}).items()})

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
            data = safe_load(content) or {}
            if not isinstance(data, Mapping):
                raise TypeError("OmegaConf.load expected mapping")
            return OmegaConf.create(data)

        @staticmethod
        def save(config: Mapping[str, Any], path: str | Path) -> None:
            container = OmegaConf.to_container(config)
            Path(path).write_text(safe_dump(container), encoding="utf-8")

        @staticmethod
        def merge(*configs: Mapping[str, Any]) -> DictConfig:
            merged: DictConfig = DictConfig()
            for cfg in configs:
                if cfg is None:
                    continue
                if not isinstance(cfg, Mapping):
                    raise TypeError("OmegaConf.merge expects mapping inputs")
                merged = _merge_dicts(merged, cfg)
            return merged

        @staticmethod
        def update(cfg: DictConfig, key: str, value: Any, *, merge: bool = True) -> None:
            if not isinstance(cfg, DictConfig):
                raise TypeError("OmegaConf.update expects a DictConfig instance")
            parts = key.split(".") if key else []
            target: DictConfig = cfg
            for segment in parts[:-1]:
                next_value = target.get(segment)
                if not isinstance(next_value, Mapping):
                    next_value = DictConfig()
                    target[segment] = next_value
                if not isinstance(next_value, DictConfig):
                    next_value = DictConfig(dict(next_value))
                    target[segment] = next_value
                target = next_value
            if parts:
                final_key = parts[-1]
                target[final_key] = _to_dictconfig(value)
            elif merge:
                container = OmegaConf.to_container(value)
                if isinstance(container, Mapping):
                    for k, v in container.items():
                        target[k] = _to_dictconfig(v)
                else:
                    raise TypeError("OmegaConf.update without key requires mapping value")


del _real_module
del _load_real_module
