"""Minimal model factory with dtype/device utilities and optional PEFT hooks."""

from __future__ import annotations

import logging
import os
from dataclasses import fields
from typing import Any, Callable, Dict, Mapping, MutableMapping, Optional

from .peft_hooks import LoraBuildCfg, build_lora

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - torch optional in lightweight envs
    torch = None  # type: ignore

logger = logging.getLogger(__name__)

ENV_ENABLE_PEFT = "CODEX_ML_ENABLE_PEFT"
_TRUE_LITERALS = {"1", "true", "yes", "on", "enable", "enabled"}


def _resolve_dtype(value: Any) -> Any:
    if value is None or torch is None:
        return value
    if isinstance(value, torch.dtype):
        return value
    if isinstance(value, str):
        token = value.replace("torch.", "").lower()
        alias = {
            "fp32": torch.float32,
            "float32": torch.float32,
            "fp16": torch.float16,
            "float16": torch.float16,
            "bf16": torch.bfloat16,
            "bfloat16": torch.bfloat16,
        }
        if token in alias:
            return alias[token]
        candidate = getattr(torch, token, None)
        if isinstance(candidate, torch.dtype):
            return candidate
    raise ValueError(f"Unsupported dtype value: {value!r}")


def _resolve_device(value: Any) -> Any:
    if value is None or torch is None:
        return value
    if isinstance(value, torch.device):
        return value
    if isinstance(value, str):
        token = value.strip().lower()
        if token == "auto":
            token = "cuda" if torch.cuda.is_available() else "cpu"
        return torch.device(token)
    return value


def _should_enable_peft(explicit: Optional[bool]) -> bool:
    if explicit is not None:
        return bool(explicit)
    env_value = os.getenv(ENV_ENABLE_PEFT)
    if not env_value:
        return False
    return env_value.strip().lower() in _TRUE_LITERALS


def _coerce_lora_cfg(cfg: Any) -> Optional[LoraBuildCfg]:
    if cfg is None:
        return None
    if isinstance(cfg, LoraBuildCfg):
        return cfg
    if isinstance(cfg, Mapping):
        allowed = {field.name for field in fields(LoraBuildCfg)}
        filtered: Dict[str, Any] = {
            key: value for key, value in cfg.items() if key in allowed
        }
        return LoraBuildCfg(**filtered)
    raise TypeError(
        "LoRA configuration must be a mapping or LoraBuildCfg instance; "
        f"received {type(cfg)!r}."
    )


def _call_builder(builder: Callable[..., Any], params: MutableMapping[str, Any]) -> Any:
    if not params:
        return builder()
    try:
        return builder(**params)
    except TypeError as exc:
        try:
            return builder(dict(params))
        except TypeError:
            raise exc


def create_model(
    builder: Callable[..., Any],
    *,
    config: Optional[Mapping[str, Any]] = None,
    dtype: Any = None,
    device: Any = None,
    enable_peft: Optional[bool] = None,
    lora_cfg: Any = None,
) -> Any:
    """Instantiate a model and optionally apply dtype/device and PEFT adapters."""

    options: Dict[str, Any] = dict(config or {})
    resolved_dtype = _resolve_dtype(dtype if dtype is not None else options.pop("dtype", None))
    resolved_device = _resolve_device(
        device if device is not None else options.pop("device", None)
    )
    lora_payload = lora_cfg if lora_cfg is not None else options.pop("lora", None)

    model = _call_builder(builder, options)

    if resolved_dtype is not None and hasattr(model, "to"):
        logger.debug("model_factory: applying dtype %s", resolved_dtype)
        model = model.to(dtype=resolved_dtype)
    if resolved_device is not None and hasattr(model, "to"):
        logger.debug("model_factory: moving model to %s", resolved_device)
        model = model.to(device=resolved_device)

    if _should_enable_peft(enable_peft):
        lora_config = _coerce_lora_cfg(lora_payload)
        if lora_config is not None:
            logger.debug("model_factory: applying LoRA adapters with config: %s", lora_config)
            model = build_lora(model, lora_config)
        else:
            logger.debug(
                "model_factory: PEFT enabled but no LoRA configuration provided; skipping"
            )
    else:
        logger.debug("model_factory: PEFT disabled; skipping LoRA application")

    return model


__all__ = ["create_model", "ENV_ENABLE_PEFT", "LoraBuildCfg"]
