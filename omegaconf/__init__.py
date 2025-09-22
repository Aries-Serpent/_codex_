"""Minimal OmegaConf stub for offline testing."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from yaml import safe_dump, safe_load  # type: ignore

__all__ = ["DictConfig", "OmegaConf"]


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
        data = safe_load(content) or {}
        if not isinstance(data, Mapping):
            raise TypeError("OmegaConf.load expected mapping")
        return DictConfig(dict(data))

    @staticmethod
    def save(config: Mapping[str, Any], path: str | Path) -> None:
        Path(path).write_text(safe_dump(dict(config)), encoding="utf-8")

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
