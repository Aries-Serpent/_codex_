"""Model registry facade."""

from __future__ import annotations

from codex_ml.models.registry import (
    get_model,
    list_models,
    model_registry,
    register_model,
)

__all__ = ["get_model", "list_models", "model_registry", "register_model"]
