"""Reusable model factory wiring dtype/device and optional PEFT hooks."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from codex_ml.modeling.codex_model_loader import load_model_with_optional_lora
from codex_ml.utils.optional import optional_import

LOGGER = logging.getLogger(__name__)

ENV_ENABLE_PEFT = "CODEX_ML_ENABLE_PEFT"


@dataclass(slots=True)
class PeftAdapterConfig:
    """Configuration options for optional LoRA/PEFT adapters."""

    path: Optional[str] = None
    r: int = 8
    alpha: int = 16
    dropout: float = 0.05
    target_modules: Optional[list[str]] = None


@dataclass(slots=True)
class ModelFactoryConfig:
    """Model creation parameters consumed by :func:`build_model`."""

    model_name_or_path: str
    dtype: Optional[str] = None
    device_map: Optional[str] = None
    enable_peft: bool = False
    peft: Optional[PeftAdapterConfig] = None
    loader_kwargs: dict[str, Any] = field(default_factory=dict)


def _peft_env_enabled() -> bool:
    """Return ``True`` when the environment allows PEFT hooks."""

    value = os.getenv(ENV_ENABLE_PEFT, "0").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _validate_dtype(dtype: Optional[str]) -> Optional[str]:
    """Ensure requested dtype exists when torch is installed."""

    if dtype is None:
        return None

    torch, has_torch = optional_import("torch")
    if not has_torch or torch is None:  # pragma: no cover - optional dependency
        raise RuntimeError("torch must be installed to request a dtype")

    if not hasattr(torch, dtype):
        raise ValueError(f"Unknown torch dtype '{dtype}'")

    return dtype


def build_model(
    config: ModelFactoryConfig,
    *,
    loader: Callable[..., Any] = load_model_with_optional_lora,
) -> Any:
    """Instantiate a model honoring dtype/device and optional PEFT hooks."""

    dtype = _validate_dtype(config.dtype)

    loader_kwargs: dict[str, Any] = dict(config.loader_kwargs)
    if dtype is not None:
        loader_kwargs["dtype"] = dtype
    if config.device_map is not None:
        loader_kwargs["device_map"] = config.device_map

    peft_cfg = config.peft
    peft_requested = config.enable_peft and peft_cfg is not None
    peft_allowed = peft_requested and _peft_env_enabled()

    if peft_requested and not peft_allowed:
        LOGGER.info(
            "PEFT requested for model '%s' but %s is not enabled; skipping adapters",
            config.model_name_or_path,
            ENV_ENABLE_PEFT,
        )

    if not peft_allowed:
        loader_kwargs.setdefault("lora_enabled", False)
    else:
        loader_kwargs.update(
            {
                "lora_enabled": True,
                "lora_path": peft_cfg.path,
                "lora_r": peft_cfg.r,
                "lora_alpha": peft_cfg.alpha,
                "lora_dropout": peft_cfg.dropout,
                "lora_target_modules": peft_cfg.target_modules,
            }
        )

    return loader(config.model_name_or_path, **loader_kwargs)


__all__ = [
    "ENV_ENABLE_PEFT",
    "ModelFactoryConfig",
    "PeftAdapterConfig",
    "build_model",
]
