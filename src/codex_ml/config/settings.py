"""
Settings Module

This module provides functionality for settings.

Usage:
    from config.settings import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import warnings  # noqa: E402
from functools import lru_cache  # noqa: E402
from typing import Any  # noqa: E402

from pydantic import BaseModel, ConfigDict, Field  # noqa: E402

try:  # pragma: no cover - optional dependency shim
    from pydantic_settings import BaseSettings as PydanticBaseSettings
    from pydantic_settings import SettingsConfigDict as PydanticSettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal envs
    PydanticBaseSettings = BaseModel

    def PydanticSettingsConfigDict(**config: Any) -> ConfigDict:
        """Return a ``ConfigDict`` compatible with Pydantic's configuration API.
        Ignores unsupported keys like 'env_file' when pydantic_settings is unavailable.
        """
        if config.pop("env_file", None) is not None:
            logger.debug("Ignoring env_file because pydantic_settings is unavailable")
        # Filter out any keys that ConfigDict doesn't support to avoid TypeErrors
        try:
            return ConfigDict(**config)  # type: ignore[typeddict-item]
        except TypeError as exc:
            type(exc).__name__
            logger.debug("TypeError: <ERROR_TYPE>")
            # If ConfigDict rejects unknown keys, filter to known parameters
            valid_keys = {"extra", "arbitrary_types_allowed", "validate_assignment"}
            filtered = {k: v for k, v in config.items() if k in valid_keys}
            warnings.warn(
                f"Some config keys ignored when pydantic_settings unavailable: {exc}",
                UserWarning,
                stacklevel=2,
            )
            return ConfigDict(**filtered)  # type: ignore[typeddict-item]

BaseSettings = PydanticBaseSettings
SettingsConfigDict = PydanticSettingsConfigDict


__all__ = ["AppSettings", "EvalRow", "eval_row_schema", "get_settings"]


class AppSettings(BaseSettings):
    """Application runtime settings sourced from the environment."""

    model_config = SettingsConfigDict(env_file=(".env",), extra="ignore")

    env: str = Field(default="dev", description="Deployment environment identifier")
    data_dir: str = Field(default="data", description="Default data directory")
    mlflow_dir: str = Field(default="mlruns", description="MLflow tracking directory")


class EvalRow(BaseModel):
    """Schema describing a single evaluation metric row."""

    step: int = Field(ge=1, description="Training step associated with the metrics")
    loss: float | None = Field(
        default=None,
        description="Loss metric recorded for the step, if available",
    )
    accuracy: float | None = Field(
        default=None,
        description="Accuracy metric recorded for the step, if available",
    )


def eval_row_schema() -> dict[str, Any]:
    """Return the JSON Schema for :class:`EvalRow`."""

    return EvalRow.model_json_schema()


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached :class:`AppSettings` loaded from the environment."""

    return AppSettings()
