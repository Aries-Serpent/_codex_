"""Model initialization helpers for Codex training flows."""

from __future__ import annotations

import logging
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from typing import Any

try:  # pragma: no cover - optional dependency guard
    import torch
except Exception:  # pragma: no cover - propagate a friendly error later
    torch = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency guard
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        PreTrainedModel,
        PreTrainedTokenizerBase,
    )
except Exception:  # pragma: no cover - transformers unavailable; defer failure until use
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]
    PreTrainedModel = Any  # type: ignore[assignment]
    PreTrainedTokenizerBase = Any  # type: ignore[assignment]

try:  # pragma: no cover - PEFT is optional for non-LoRA runs
    from peft import LoraConfig, get_peft_model
except Exception:  # pragma: no cover - allow graceful degradation when PEFT is absent
    LoraConfig = None  # type: ignore[assignment]
    get_peft_model = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)


if torch is not None:
    _DTYPE_MAP: dict[str, torch.dtype] = {
        "fp32": torch.float32,
        "float32": torch.float32,
        "bf16": torch.bfloat16,
        "bfloat16": torch.bfloat16,
        "fp16": torch.float16,
        "float16": torch.float16,
        "half": torch.float16,
    }
else:  # pragma: no cover - torch missing in lightweight environments
    _DTYPE_MAP = {}


def _ensure_torch() -> None:
    if torch is None:  # pragma: no cover - defensive guard
        raise RuntimeError("torch is required for model initialisation")


def _normalise_mapping(config: Mapping[str, Any]) -> MutableMapping[str, Any]:
    """Return a plain mutable mapping extracted from arbitrary OmegaConf containers."""

    if hasattr(config, "to_container"):
        try:
            return config.to_container(resolve=True)  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - fallback to stringification
            return dict(config)  # type: ignore[arg-type]
    return dict(config)


def _resolve_value(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _resolve_dtype(name: str | None) -> torch.dtype:
    _ensure_torch()
    if not name:
        return torch.float32
    try:
        return _DTYPE_MAP[name.lower()]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported dtype '{name}'. Expected one of {sorted(_DTYPE_MAP)}"
        ) from exc


def _resolve_device(name: str | None) -> str:
    if not name or name == "auto":
        if torch is not None and getattr(torch.cuda, "is_available", lambda: False)():
            return "cuda"
        return "cpu"
    return name


@dataclass
class LoraSettings:
    """Configuration for optional LoRA/PEFT adaptation."""

    enabled: bool = False
    r: int = 8
    alpha: int = 16
    dropout: float = 0.0
    target_modules: Sequence[str] = field(default_factory=lambda: ("q_proj", "v_proj"))
    bias: str = "none"
    task_type: str = "CAUSAL_LM"


@dataclass
class ModelInitConfig:
    """High-level configuration for model + tokenizer initialisation."""

    model_name: str
    tokenizer_name: str | None = None
    dtype: str = "float32"
    device: str = "auto"
    trust_remote_code: bool = False
    load_config: Mapping[str, Any] = field(default_factory=dict)
    lora: LoraSettings = field(default_factory=LoraSettings)


def _coerce_config(config: Mapping[str, Any]) -> ModelInitConfig:
    mapping = _normalise_mapping(config)
    model_name = _resolve_value(
        mapping,
        "model_name",
        "name",
        "pretrained_model_name_or_path",
    )
    if not model_name:
        raise ValueError("model_name (or name/pretrained_model_name_or_path) must be provided")
    tokenizer_name = _resolve_value(mapping, "tokenizer_name", "tokenizer")
    dtype = _resolve_value(mapping, "dtype", "torch_dtype", default="float32")
    device = _resolve_value(mapping, "device", default="auto")
    trust_remote_code = bool(_resolve_value(mapping, "trust_remote_code", default=False))

    lora_section = mapping.get("lora") or {}
    if not isinstance(lora_section, Mapping):
        raise TypeError("model.lora must be a mapping when provided")
    lora_settings = LoraSettings(
        enabled=bool(
            _resolve_value(mapping, "use_lora", default=False)
            or _resolve_value(lora_section, "enabled", default=False)
        ),
        r=int(_resolve_value(mapping, "lora_rank", "r", default=lora_section.get("r", 8))),
        alpha=int(
            _resolve_value(mapping, "lora_alpha", default=lora_section.get("lora_alpha", 16))
        ),
        dropout=float(lora_section.get("lora_dropout", 0.0)),
        target_modules=tuple(
            lora_section.get("target_modules")
            or mapping.get("lora_target_modules")
            or ("q_proj", "v_proj")
        ),
        bias=str(lora_section.get("bias", "none")),
        task_type=str(lora_section.get("task_type", "CAUSAL_LM")),
    )

    load_config = mapping.get("load_config") or mapping.get("load_kwargs") or {}
    if not isinstance(load_config, Mapping):
        raise TypeError("load_config/load_kwargs must be a mapping when provided")

    return ModelInitConfig(
        model_name=str(model_name),
        tokenizer_name=str(tokenizer_name) if tokenizer_name else None,
        dtype=str(dtype),
        device=str(device),
        trust_remote_code=trust_remote_code,
        load_config=dict(load_config),
        lora=lora_settings,
    )


def load_tokenizer(config: Mapping[str, Any] | ModelInitConfig) -> PreTrainedTokenizerBase:
    """Load a tokenizer matching the model configuration."""

    if AutoTokenizer is None:  # pragma: no cover - transformers missing at runtime
        raise RuntimeError("transformers is required to load tokenizers")
    if isinstance(config, ModelInitConfig):
        tokenizer_name = config.tokenizer_name or config.model_name
        trust_remote_code = config.trust_remote_code
    else:
        coerced = _coerce_config(config)
        tokenizer_name = coerced.tokenizer_name or coerced.model_name
        trust_remote_code = coerced.trust_remote_code

    try:
        return AutoTokenizer.from_pretrained(tokenizer_name, trust_remote_code=trust_remote_code)
    except Exception as exc:  # pragma: no cover - surface friendly error in tests
        raise RuntimeError(f"Failed to load tokenizer '{tokenizer_name}': {exc}") from exc


def _apply_lora(model: PreTrainedModel, cfg: LoraSettings) -> PreTrainedModel:
    if not cfg.enabled:
        return model
    if LoraConfig is None or get_peft_model is None:  # pragma: no cover - optional dep guard
        raise RuntimeError("peft is required for LoRA support but is not installed")
    lora_cfg = LoraConfig(
        r=cfg.r,
        lora_alpha=cfg.alpha,
        lora_dropout=cfg.dropout,
        target_modules=list(cfg.target_modules),
        bias=cfg.bias,
        task_type=cfg.task_type,
    )
    return get_peft_model(model, lora_cfg)


def load_model(config: Mapping[str, Any] | ModelInitConfig) -> PreTrainedModel:
    """Load a model and apply optional LoRA adapters based on configuration."""

    if AutoModelForCausalLM is None:  # pragma: no cover - transformers missing at runtime
        raise RuntimeError("transformers is required to load models")
    coerced = config if isinstance(config, ModelInitConfig) else _coerce_config(config)
    _ensure_torch()
    dtype = _resolve_dtype(coerced.dtype)
    device = _resolve_device(coerced.device)
    load_kwargs = dict(coerced.load_config)
    load_kwargs.setdefault("torch_dtype", dtype)
    load_kwargs.setdefault("trust_remote_code", coerced.trust_remote_code)

    LOGGER.debug("Loading model '%s' with kwargs=%s", coerced.model_name, load_kwargs)
    try:
        model = AutoModelForCausalLM.from_pretrained(coerced.model_name, **load_kwargs)
    except OSError as exc:  # pragma: no cover - offline friendly error propagation
        raise RuntimeError(
            f"Unable to load model '{coerced.model_name}'. "
            "Ensure the weights are available locally."
        ) from exc
    except Exception as exc:  # pragma: no cover - propagate with context
        raise RuntimeError(
            f"Unexpected error while loading model '{coerced.model_name}': {exc}"
        ) from exc

    try:
        model = model.to(device)
    except Exception as exc:  # pragma: no cover - propagate but annotate
        raise RuntimeError(f"Failed to move model to device '{device}': {exc}") from exc

    if coerced.lora.enabled:
        LOGGER.info(
            "Applying LoRA adapters (r=%s, alpha=%s, dropout=%s, target_modules=%s)",
            coerced.lora.r,
            coerced.lora.alpha,
            coerced.lora.dropout,
            list(coerced.lora.target_modules),
        )
        model = _apply_lora(model, coerced.lora)

    return model


def load_model_and_tokenizer(
    config: Mapping[str, Any] | ModelInitConfig,
) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Convenience wrapper that returns both the model and tokenizer."""

    coerced = config if isinstance(config, ModelInitConfig) else _coerce_config(config)
    model = load_model(coerced)
    tokenizer = load_tokenizer(coerced)
    return model, tokenizer


ModelConfig = ModelInitConfig
LoRASettings = LoraSettings

# ``ModelConfig`` and ``LoRASettings`` were the public names in earlier releases.
# Keep exporting them (alongside ``_DTYPE_MAP``) so downstream code continues to
# import the documented symbols without modification.


__all__ = [
    "_DTYPE_MAP",
    "LoRASettings",
    "LoraSettings",
    "ModelInitConfig",
    "ModelConfig",
    "load_model",
    "load_model_and_tokenizer",
    "load_tokenizer",
]
