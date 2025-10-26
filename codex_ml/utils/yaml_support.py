"""Thin wrapper around :mod:`yaml` with sensible fallbacks."""

from __future__ import annotations

from typing import Any

__all__ = ["safe_load", "YAMLError", "MissingPyYAMLError"]


class MissingPyYAMLError(RuntimeError):
    """Raised when PyYAML is not installed but requested."""


try:  # pragma: no cover - yaml optional dependency
    import yaml
except Exception:  # pragma: no cover - fallback shim

    class YAMLError(RuntimeError):
        pass

    def safe_load(data: str) -> Any:
        raise MissingPyYAMLError("PyYAML is not installed")

else:
    from yaml import YAMLError as _YamlError  # type: ignore

    YAMLError = _YamlError

    def safe_load(data: str) -> Any:
        return yaml.safe_load(data)
