"""Settings and schema definitions for Codex ML configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

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
