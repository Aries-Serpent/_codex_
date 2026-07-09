"""Model initialisation helpers for Codex training flows."""

from __future__ import annotations

import importlib
import inspect
import logging
import os
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)
try:  # pragma: no cover - optional dependency guard
    import torch
except (ImportError, AttributeError):  # pragma: no cover - propagate a friendly error later
    torch = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency guard
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        PreTrainedModel,
        PreTrainedTokenizerBase,
    )
except (
    ImportError,
    AttributeError,
):  # pragma: no cover - transformers unavailable; defer failure until use
    AutoModelForCausalLM = None  # type: ignore[misc,assignment]
    AutoTokenizer = None  # type: ignore[misc,assignment]
    PreTrainedModel = Any  # type: ignore[misc,assignment]
    PreTrainedTokenizerBase = Any  # type: ignore[misc,assignment]

try:  # pragma: no cover - PEFT is optional for non-LoRA runs
    from peft import LoraConfig, get_peft_model
except (
    ImportError,
    AttributeError,
):  # pragma: no cover - allow graceful degradation when PEFT is absent
    LoraConfig = None
    get_peft_model = None


LOGGER = logging.getLogger(__name__)

# Expose import_module for test monkeypatching compatibility.
import_module = importlib.import_module


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


def _needs_bf16(dtype_name: str | None, dtype_obj: Any) -> bool:
    names = {"bf16", "bfloat16"}
    if dtype_name and str(dtype_name).lower() in names:
        return True
    if torch is not None and dtype_obj is not None:
        bf16 = getattr(torch, "bfloat16", None)
        if bf16 is not None and dtype_obj == bf16:
            return True
    return False


def _assert_bf16_capability(
    requested_dtype: str | None,
    dtype_obj: Any,
    device: str,
    require: bool,
) -> None:
    """Validate bf16 support when required by configuration."""

    if not require or not _needs_bf16(requested_dtype, dtype_obj):
        return
    if torch is None:
        raise RuntimeError("bf16 requested but PyTorch is not installed")

    bf16 = getattr(torch, "bfloat16", None)
    if bf16 is None:
        raise RuntimeError("bf16 requested but this PyTorch build lacks torch.bfloat16")

    try:
        device_obj = torch.device(device)
    except (ConnectionError, TimeoutError):  # pragma: no cover - fall back to heuristic
        device_obj = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    try:
        a = torch.ones((2, 2), dtype=bf16, device=device_obj)
        b = torch.ones((2, 2), dtype=bf16, device=device_obj)
        _ = a @ b
    except (ConnectionError, TimeoutError) as exc:  # pragma: no cover - surface capability failure
        raise RuntimeError(
            f"Requested bf16 but device '{device_obj}' lacks bfloat16 support"
        ) from exc


def _ensure_torch() -> None:
    if torch is None:  # pragma: no cover - defensive guard
        raise RuntimeError("torch is required for model initialisation")


def _normalise_mapping(config: Mapping[str, Any]) -> MutableMapping[str, Any]:
    """Return a plain mutable mapping extracted from arbitrary OmegaConf containers."""

    if hasattr(config, "to_container"):
        try:
            return config.to_container(resolve=True)
        except Exception:  # pragma: no cover - fallback to stringification
            return dict(config)
    return dict(config)


def _resolve_value(mapping: Mapping[str, Any], *keys: str, default: Any | None = None) -> Any:
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
        type(exc).__name__
        logger.debug("KeyError: <ERROR_TYPE>")
        raise ValueError(
            f"Unsupported dtype '{name}'. Expected one of {sorted(_DTYPE_MAP)}"
        ) from exc


def _resolve_device(name: str | None) -> str:
    if not name or name == "auto":
        if torch is not None and getattr(torch.cuda, "is_available", lambda: False)():
            return "cuda"
        return "cpu"
    return name


def resolve_dtype(name: str | None) -> torch.dtype:
    return _resolve_dtype(name)


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
    bf16_require_capability: bool = False


def _coerce_config(config: Mapping[str, Any]) -> ModelInitConfig:
    mapping = _normalise_mapping(config)
    model_name = _resolve_value(
        mapping,
        "model_name",
        "name",
        "model_name_or_path",
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

    reproducibility_section = mapping.get("reproducibility")
    bf16_require = bool(mapping.get("bf16_require_capability", False))
    if isinstance(reproducibility_section, Mapping):
        bf16_require = bool(reproducibility_section.get("bf16_require_capability", bf16_require))

    return ModelInitConfig(
        model_name=str(model_name),
        tokenizer_name=str(tokenizer_name) if tokenizer_name else None,
        dtype=str(dtype),
        device=str(device),
        trust_remote_code=trust_remote_code,
        load_config=dict(load_config),
        lora=lora_settings,
        bf16_require_capability=bf16_require,
    )


def load_tokenizer(
    config: Mapping[str, Any] | ModelInitConfig,
) -> PreTrainedTokenizerBase:
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

    kwargs: dict[str, Any] = {}
    if trust_remote_code:
        kwargs["trust_remote_code"] = True

    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, **kwargs)  # nosec B615
        assert tokenizer is not None, f"Failed to load tokenizer {tokenizer_name}"
        # Set pad_token to eos_token if not already set (common default)
        if getattr(tokenizer, "pad_token", None) is None and getattr(tokenizer, "eos_token", None):
            LOGGER.warning(
                "Text backend '%s' has no pad token; falling back to EOS padding. "
                "This may affect training behaviour.",
                type(tokenizer).__name__,
            )
            tokenizer.pad_token = tokenizer.eos_token
        return tokenizer
    except (
        ConnectionError,
        TimeoutError,
    ) as exc:  # pragma: no cover - surface friendly error in tests
        raise RuntimeError(f"Failed to load tokenizer '{tokenizer_name}': {exc}") from exc


def _is_bf16_dtype(dtype_name: str | None, dtype_obj: Any) -> bool:
    requested = (dtype_name or "").lower() in {"bf16", "bfloat16"}
    if not requested and torch is not None and dtype_obj is not None:
        try:
            requested = dtype_obj == getattr(torch, "bfloat16", None)
        except (ConnectionError, TimeoutError):  # pragma: no cover - defensive
            requested = False
    return requested


def _ensure_bf16_capability(
    dtype_name: str | None,
    dtype_obj: Any,
    device_name: str,
    *,
    require_capability: bool,
) -> None:
    if not _is_bf16_dtype(dtype_name, dtype_obj):
        return

    enforced = require_capability or os.getenv("CODEX_BF16_REQUIRE_CAPABILITY", "").lower() in {
        "1",
        "true",
        "yes",
    }

    if torch is None:
        message = "Requested bf16 dtype but torch is not installed"
        if enforced:
            raise RuntimeError(message)
        LOGGER.warning("%s; continuing with requested dtype", message)
        return

    try:
        target = torch.device(device_name)
    except (ConnectionError, TimeoutError):  # pragma: no cover - fallback to cpu/cuda detection
        target = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    supported = False
    try:
        tensor = torch.zeros(1, dtype=torch.bfloat16, device=target)
        supported = tensor.dtype == torch.bfloat16
    except (ConnectionError, TimeoutError):
        logger.warning("Exception occurred", exc_info=True)
        supported = False

    if supported:
        return

    message = f"Requested bf16 but device '{device_name}' lacks support"
    if enforced:
        raise RuntimeError(message)
    LOGGER.warning("%s; continuing but results may be undefined", message)


def apply_lora_if_configured(model: PreTrainedModel, cfg: LoraSettings) -> PreTrainedModel:
    if not cfg.enabled:
        return model
    # Use module-level references to allow monkeypatching in tests.
    # Fall back to dynamic import when peft was not available at import time.
    lora_config_cls = LoraConfig
    get_peft_model_fn = get_peft_model
    if lora_config_cls is None or get_peft_model_fn is None:
        try:
            peft_module = import_module("peft")
            lora_config_cls = peft_module.LoraConfig
            get_peft_model_fn = peft_module.get_peft_model
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dep guard
            raise RuntimeError("peft is required for LoRA support but is not installed") from exc
    if lora_config_cls is None or get_peft_model_fn is None:  # pragma: no cover
        raise RuntimeError("peft is required for LoRA support but is not installed")

    lora_cfg = lora_config_cls(
        r=cfg.r,
        lora_alpha=cfg.alpha,
        lora_dropout=cfg.dropout,
        target_modules=list(cfg.target_modules),
        bias=cfg.bias,
        task_type=cfg.task_type,
    )
    return get_peft_model_fn(model, lora_cfg)


def load_model(
    config: Mapping[str, Any] | ModelInitConfig | str,
    *,
    dtype: str | None = None,
    device: str | None = None,
) -> PreTrainedModel:
    """Load a model and apply optional LoRA adapters based on configuration."""

    if AutoModelForCausalLM is None:  # pragma: no cover - transformers missing at runtime
        raise RuntimeError("transformers is required to load models")
    if isinstance(config, str):
        coerced = ModelInitConfig(
            model_name=config,
            dtype=dtype or "float32",
            device=device or "auto",
        )
    else:
        coerced = config if isinstance(config, ModelInitConfig) else _coerce_config(config)
    _ensure_torch()
    dtype = _resolve_dtype(coerced.dtype)
    device = _resolve_device(coerced.device)
    _assert_bf16_capability(coerced.dtype, dtype, device, coerced.bf16_require_capability)
    load_kwargs = dict(coerced.load_config)
    load_kwargs.setdefault("torch_dtype", dtype)
    load_kwargs.setdefault("low_cpu_mem_usage", True)
    if coerced.trust_remote_code:
        load_kwargs.setdefault("trust_remote_code", True)

    _ensure_bf16_capability(
        coerced.dtype,
        dtype,
        device,
        require_capability=coerced.bf16_require_capability,
    )

    from_pretrained = AutoModelForCausalLM.from_pretrained
    try:
        sig = inspect.signature(from_pretrained)
    except (TypeError, ValueError):  # pragma: no cover - signature may be unavailable
        sig = None
    if sig is not None and not any(
        param.kind == inspect.Parameter.VAR_KEYWORD for param in sig.parameters.values()
    ):
        load_kwargs = {k: v for k, v in load_kwargs.items() if k in sig.parameters}

    LOGGER.debug("Loading model '%s' with kwargs=%s", coerced.model_name, load_kwargs)
    try:
        model = from_pretrained(coerced.model_name, **load_kwargs)  # nosec B615
    except OSError as exc:  # pragma: no cover - offline friendly error propagation
        raise RuntimeError(
            f"Unable to load model '{coerced.model_name}'. "
            "Ensure the weights are available locally."
        ) from exc
    except (ValueError, TypeError) as exc:  # pragma: no cover - propagate with context
        raise RuntimeError(
            f"Unexpected error while loading model '{coerced.model_name}': {exc}"
        ) from exc

    try:
        model = model.to(device)  # type: ignore[attr-defined]
    except (ImportError, AttributeError) as exc:  # pragma: no cover - propagate but annotate
        raise RuntimeError(f"Failed to move model to device '{device}': {exc}") from exc

    if coerced.lora.enabled:
        LOGGER.info(
            "Applying LoRA adapters (r=%s, alpha=%s, dropout=%s, target_modules=%s)",
            coerced.lora.r,
            coerced.lora.alpha,
            coerced.lora.dropout,
            list(coerced.lora.target_modules),
        )
        model = apply_lora_if_configured(model, coerced.lora)

    return model


def load_model_and_tokenizer(
    config: Mapping[str, Any] | ModelInitConfig,
) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Convenience wrapper that returns both the model and tokenizer."""

    coerced = config if isinstance(config, ModelInitConfig) else _coerce_config(config)
    model = load_model(coerced)
    tokenizer = load_tokenizer(coerced)
    if getattr(tokenizer, "pad_token", None) is None and getattr(tokenizer, "eos_token", None):
        tokenizer.pad_token = tokenizer.eos_token
    if hasattr(tokenizer, "padding_side"):
        tokenizer.padding_side = "left"
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
    "ModelConfig",
    "ModelInitConfig",
    "load_model",
    "load_model_and_tokenizer",
    "load_tokenizer",
]
