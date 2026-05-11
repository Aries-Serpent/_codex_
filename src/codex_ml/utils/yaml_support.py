"""
Yaml Support Module

This module provides functionality for yaml support.

Usage:
    from utils.yaml_support import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from types import ModuleType
from typing import IO, Any, Optional

_PY_YAML_INSTALL_HINT = 'pip install "PyYAML>=6.0"'

_yaml_module: Optional[ModuleType]
try:  # pragma: no cover - import guard
    import yaml as _yaml
except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
    _yaml_module = None
    _YAML_IMPORT_ERROR = exc
else:  # pragma: no cover - exercised when PyYAML installed
    _yaml_module = _yaml
    _YAML_IMPORT_ERROR = None  # type: ignore[assignment]


class MissingPyYAMLError(ModuleNotFoundError):
    """Raised when a YAML operation requires PyYAML but it is unavailable."""

    def __init__(self) -> None:
        hint = _PY_YAML_INSTALL_HINT
        super().__init__(
            f"PyYAML is required for this operation. Install it via ``{hint}`` to enable YAML parsing."  # noqa: E501
        )


YAMLErrorType: type[Exception]
if _yaml_module is not None:  # pragma: no cover - executed when PyYAML present
    YAMLErrorType = _yaml_module.YAMLError
else:  # pragma: no cover - avoids attribute errors when PyYAML missing

    class YAMLErrorType(RuntimeError):  # type: ignore[no-redef]
        """Placeholder exception used when PyYAML is unavailable."""


# Alias for backward compatibility
YAMLError = YAMLErrorType


def require_yaml() -> ModuleType:
    """Return the imported PyYAML module or raise ``MissingPyYAMLError``."""

    if _yaml_module is None:
        raise MissingPyYAMLError() from _YAML_IMPORT_ERROR
    return _yaml_module


def safe_load(stream: Any) -> Any:
    """Load YAML content using PyYAML's ``safe_load`` helper."""

    module = require_yaml()
    return module.safe_load(stream)


def safe_dump(data: Any, stream: IO[str] | None = None, **kwargs: Any) -> Any:
    """Serialize ``data`` to YAML using ``safe_dump`` when PyYAML is available."""

    module = require_yaml()
    return module.safe_dump(data, stream=stream, **kwargs)


def yaml_available() -> bool:
    """Return ``True`` when PyYAML was imported successfully."""

    return _yaml_module is not None


__all__ = [
    "MissingPyYAMLError",
    "YAMLError",
    "require_yaml",
    "safe_dump",
    "safe_load",
    "yaml_available",
]
