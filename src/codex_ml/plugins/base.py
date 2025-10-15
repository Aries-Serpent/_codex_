from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePlugin(ABC):
    """Minimal plugin interface for Codex ML."""

    @abstractmethod
    def name(self) -> str:
        """Unique plugin name."""

    @abstractmethod
    def version(self) -> str:
        """Semantic version string for the plugin implementation."""

    def activate(self, app_ctx: dict[str, Any] | None = None) -> None:
        """Optional activation hook executed once the plugin is registered."""
        return


class TokenizerPlugin(BasePlugin):
    """Marker interface for tokenizer plugins."""


class MetricsPlugin(BasePlugin):
    """Marker interface for metrics/logging plugins."""


class ModelPlugin(BasePlugin):
    """Marker interface for model provider plugins."""


__all__ = [
    "BasePlugin",
    "TokenizerPlugin",
    "MetricsPlugin",
    "ModelPlugin",
]
