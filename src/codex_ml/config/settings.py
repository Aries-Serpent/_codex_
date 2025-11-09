"""Settings and schema definitions for Codex ML configuration."""

from __future__ import annotations

import warnings
from functools import lru_cache
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

try:  # pragma: no cover - optional dependency shim
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal envs
    BaseSettings = BaseModel  # type: ignore[misc]

    def SettingsConfigDict(**config: Any) -> ConfigDict:  # type: ignore[misc]
        """Return a ``ConfigDict`` compatible with Pydantic's configuration API.
        Ignores unsupported keys like 'env_file' when pydantic_settings is unavailable.
        """
        if config.pop("env_file", None) is not None:
            warnings.warn(
                "env_file not supported when pydantic_settings unavailable",
                UserWarning,
                stacklevel=2,
            )
        # Filter out any keys that ConfigDict doesn't support to avoid TypeErrors
        try:
            return ConfigDict(**config)
        except TypeError as exc:
            # If ConfigDict rejects unknown keys, filter to known parameters
            valid_keys = {"extra", "arbitrary_types_allowed", "validate_assignment"}
            filtered = {k: v for k, v in config.items() if k in valid_keys}
            warnings.warn(
                f"Some config keys ignored when pydantic_settings unavailable: {exc}",
                UserWarning,
                stacklevel=2,
            )
            return ConfigDict(**filtered)


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


def eval_row_schema() -> dict:
    """Return the JSON Schema for :class:`EvalRow`."""

    return EvalRow.model_json_schema()


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached :class:`AppSettings` loaded from the environment."""

    return AppSettings()  # type: ignore[call-arg]
