"""OmegaConf shim that defers to the real package when available."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable, Mapping

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
            try:
                spec.loader.exec_module(module)  # type: ignore[arg-type]
            except Exception:  # pragma: no cover - fall back to stub on failure
                sys.modules.pop(loader_name, None)
                continue

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

    def _merge_dicts(base: Mapping[str, Any], other: Mapping[str, Any]) -> DictConfig:
        result = DictConfig(base)
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
            data = safe_load(content) or {}
            if not isinstance(data, Mapping):
                raise TypeError("OmegaConf.load expected mapping")
            return DictConfig(dict(data))

        @staticmethod
        def save(config: Mapping[str, Any], path: str | Path) -> None:
            Path(path).write_text(safe_dump(dict(config)), encoding="utf-8")

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


del _real_module
del _load_real_module
