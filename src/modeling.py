"""Utilities for initializing language models with optional LoRA adapters."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from importlib import import_module
from typing import Any

import torch
from codex_ml.utils.error_log import log_error
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass(slots=True)
class LoRASettings:
    """Configuration bundle describing how to apply a LoRA adapter."""

    enabled: bool = False
    r: int = 8
    alpha: float = 16.0
    dropout: float = 0.0
    bias: str = "none"
    target_modules: Sequence[str] = ("q_proj", "v_proj")


@dataclass(slots=True)
class ModelConfig:
    """Declarative model initialisation parameters."""

    model_name_or_path: str
    tokenizer_name_or_path: str | None = None
    dtype: str = "float32"
    device: str = "auto"
    lora: LoRASettings = field(default_factory=LoRASettings)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> ModelConfig:
        """Create a :class:`ModelConfig` from an arbitrary mapping."""

        model_name = data.get("model_name") or data.get("model_name_or_path")
        model_name = model_name or data.get("pretrained_model_name_or_path")
        if not model_name:
            raise ValueError("model_name_or_path is required to load a model")
        tokenizer_name = data.get("tokenizer_name") or data.get("tokenizer_name_or_path")
        tokenizer_name = tokenizer_name or data.get("tokenizer")
        lora_data = data.get("lora") or {}
        if isinstance(lora_data, Mapping):
            lora_cfg = LoRASettings(
                enabled=bool(lora_data.get("enabled") or lora_data.get("enable")),
                r=int(lora_data.get("r", 8)),
                alpha=float(lora_data.get("lora_alpha", lora_data.get("alpha", 16.0))),
                dropout=float(lora_data.get("lora_dropout", lora_data.get("dropout", 0.0))),
                bias=str(lora_data.get("bias", "none")),
                target_modules=tuple(lora_data.get("target_modules", ("q_proj", "v_proj"))),
            )
        else:
            lora_cfg = LoRASettings()
        return cls(
            model_name_or_path=str(model_name),
            tokenizer_name_or_path=str(tokenizer_name) if tokenizer_name else None,
            dtype=str(data.get("dtype", data.get("precision", "float32"))),
            device=str(data.get("device", data.get("target_device", "auto"))),
            lora=lora_cfg,
        )


_DTYPE_ALIASES: Mapping[str, torch.dtype] = {
    "float32": torch.float32,
    "fp32": torch.float32,
    "float16": torch.float16,
    "fp16": torch.float16,
    "bfloat16": torch.bfloat16,
    "bf16": torch.bfloat16,
}


def resolve_dtype(dtype: str | None) -> torch.dtype:
    """Convert a user supplied dtype string to a :mod:`torch` dtype."""

    if dtype is None:
        return torch.float32
    key = dtype.lower()
    if key not in _DTYPE_ALIASES:
        raise ValueError(f"Unsupported dtype '{dtype}'. Expected one of {sorted(_DTYPE_ALIASES)}")
    return _DTYPE_ALIASES[key]


def resolve_device(device: str | None) -> str:
    """Resolve ``device`` to a backend understood by :mod:`torch`."""

    if device in (None, "auto"):
        if getattr(torch.cuda, "is_available", lambda: False)():
            return "cuda"
        backends = getattr(torch, "backends", None)
        if backends is not None:
            mps_backend = getattr(backends, "mps", None)
            if mps_backend is not None and getattr(mps_backend, "is_available", lambda: False)():
                return "mps"
        return "cpu"
    return device


def _load_lora_backend() -> tuple[Any, Any, Any | None]:
    """Return ``(LoraConfig, get_peft_model, TaskType)`` from :mod:`peft`."""

    try:
        peft_module = import_module("peft")
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised when peft missing
        raise RuntimeError(
            "LoRA requested but the optional 'peft' package is not installed."
        ) from exc
    try:
        lora_config = peft_module.LoraConfig
        get_peft_model = peft_module.get_peft_model
    except (
        AttributeError
    ) as exc:  # pragma: no cover - defensive guard against incompatible versions
        raise RuntimeError("Installed 'peft' package is missing required APIs.") from exc
    task_type = getattr(peft_module, "TaskType", None)
    return lora_config, get_peft_model, task_type


def apply_lora_if_configured(model: torch.nn.Module, settings: LoRASettings) -> torch.nn.Module:
    """Apply a LoRA adapter when ``settings.enabled`` is ``True``."""

    if not settings.enabled:
        return model
    lora_config_cls, get_peft_model, task_type = _load_lora_backend()
    lora_kwargs: MutableMapping[str, Any] = {
        "r": settings.r,
        "lora_alpha": settings.alpha,
        "lora_dropout": settings.dropout,
        "bias": settings.bias,
        "target_modules": tuple(settings.target_modules),
    }
    if task_type is not None:
        task_attr = getattr(task_type, "CAUSAL_LM", None)
        if task_attr is not None:
            lora_kwargs["task_type"] = task_attr
    config = lora_config_cls(**lora_kwargs)
    try:
        return get_peft_model(model, config)
    except Exception as exc:  # pragma: no cover - defensive logging guard
        log_error("modeling.lora", str(exc), "apply_lora_if_configured")
        raise


def load_model(
    model_name_or_path: str,
    *,
    dtype: str | None = None,
    device: str | None = None,
    lora: LoRASettings | Mapping[str, Any] | None = None,
    **model_kwargs: Any,
) -> torch.nn.Module:
    """Load a Hugging Face causal language model with optional LoRA adapters."""

    if isinstance(lora, LoRASettings):
        lora_settings = lora
    elif isinstance(lora, Mapping):
        lora_settings = LoRASettings(**lora)
    else:
        lora_settings = LoRASettings()
    resolved_dtype = resolve_dtype(dtype)
    resolved_device = resolve_device(device)
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path, torch_dtype=resolved_dtype, **model_kwargs
    )
    model = apply_lora_if_configured(model, lora_settings)
    return model.to(resolved_device)


def load_tokenizer(model_name_or_path: str) -> Any:
    """Load a tokenizer and ensure padding tokens are available."""

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    if getattr(tokenizer, "pad_token", None) is None:
        fallback = getattr(tokenizer, "eos_token", None) or getattr(tokenizer, "bos_token", None)
        if fallback is not None:
            tokenizer.pad_token = fallback
    tokenizer.padding_side = getattr(tokenizer, "padding_side", "right")
    return tokenizer


def load_model_and_tokenizer(
    config: ModelConfig | Mapping[str, Any],
) -> tuple[torch.nn.Module, Any]:
    """Load a model/tokenizer pair based on a :class:`ModelConfig` or mapping."""

    cfg = config if isinstance(config, ModelConfig) else ModelConfig.from_mapping(config)
    tokenizer_name = cfg.tokenizer_name_or_path or cfg.model_name_or_path
    model = load_model(
        cfg.model_name_or_path,
        dtype=cfg.dtype,
        device=cfg.device,
        lora=cfg.lora,
    )
    tokenizer = load_tokenizer(tokenizer_name)
    return model, tokenizer


__all__ = [
    "LoRASettings",
    "ModelConfig",
    "apply_lora_if_configured",
    "load_model",
    "load_model_and_tokenizer",
    "load_tokenizer",
    "resolve_device",
    "resolve_dtype",
]
