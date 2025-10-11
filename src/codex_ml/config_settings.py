"""Pydantic settings and schema helpers for Codex ML."""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application-level settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=(".env",), extra="ignore")

    env: str = "dev"
    data_dir: str = "data"
    mlflow_dir: str = "mlruns"


class EvalRow(BaseModel):
    """Schema describing a single evaluation record."""

    step: int = Field(ge=1)
    loss: float | None = None
    accuracy: float | None = None


def eval_row_schema() -> dict:
    """Return the JSON schema for :class:`EvalRow`."""

    return EvalRow.model_json_schema()


__all__ = ["AppSettings", "EvalRow", "eval_row_schema"]
