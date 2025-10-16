from __future__ import annotations

import logging
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

torch, _HAS_TORCH = optional_import("torch")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")
if _HAS_TRANSFORMERS and transformers is not None:
    AutoModelForCausalLM = getattr(transformers, "AutoModelForCausalLM", None)
    AutoTokenizer = getattr(transformers, "AutoTokenizer", None)
    PreTrainedModel = getattr(transformers, "PreTrainedModel", Any)
    PreTrainedTokenizerBase = getattr(transformers, "PreTrainedTokenizerBase", Any)
    if AutoModelForCausalLM is None or AutoTokenizer is None:  # pragma: no cover - stubbed install
        _HAS_TRANSFORMERS = False
        AutoModelForCausalLM = None  # type: ignore[assignment]
        AutoTokenizer = None  # type: ignore[assignment]
        PreTrainedModel = Any  # type: ignore[assignment]
        PreTrainedTokenizerBase = Any  # type: ignore[assignment]
else:  # pragma: no cover - optional dependency
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]
    PreTrainedModel = Any  # type: ignore[assignment]
    PreTrainedTokenizerBase = Any  # type: ignore[assignment]

try:  # optional PEFT
    from peft import LoraConfig, PeftModel, get_peft_model
except Exception:  # pragma: no cover - optional
    LoraConfig = None
    PeftModel = None
    get_peft_model = None


LOGGER = logging.getLogger(__name__)

if _HAS_TORCH and torch is not None:
    _DTYPE_MAP: dict[str, Any] = {
        "auto": torch.float32,
        "fp32": torch.float32,
        "float32": torch.float32,
        "bf16": torch.bfloat16,
        "bfloat16": torch.bfloat16,
        "fp16": torch.float16,
        "float16": torch.float16,
        "half": torch.float16,
    }
else:  # pragma: no cover - torch unavailable in lightweight environments
    _DTYPE_MAP = {}


def _needs_bf16(dtype_name: str | None, dtype_obj: Any) -> bool:
    names = {"bf16", "bfloat16"}
    if dtype_name and str(dtype_name).lower() in names:
        return True
    if _HAS_TORCH and torch is not None and dtype_obj is not None:
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
    """Validate bf16 support before attempting to load a model."""

    if not require or not _needs_bf16(requested_dtype, dtype_obj):
        return
    if not (_HAS_TORCH and torch is not None):
        raise RuntimeError("bf16 requested but PyTorch is not installed")

    bf16 = getattr(torch, "bfloat16", None)
    if bf16 is None:
        raise RuntimeError("bf16 requested but this PyTorch build lacks torch.bfloat16")

    try:
        device_obj = torch.device(device)
    except Exception:  # pragma: no cover - defensive fallback when device parsing fails
        device_obj = torch.device("cuda" if torch.cuda and torch.cuda.is_available() else "cpu")

    try:
        a = torch.ones((2, 2), dtype=bf16, device=device_obj)
        b = torch.ones((2, 2), dtype=bf16, device=device_obj)
        _ = a @ b
    except Exception as exc:  # pragma: no cover - propagate user-friendly error
        raise RuntimeError(
            f"Requested bf16 but device '{device_obj}' lacks bfloat16 support"
        ) from exc


def _ensure_torch() -> None:
    if not (_HAS_TORCH and torch is not None):  # pragma: no cover - explicit guard for callers
        raise RuntimeError("torch is required for model initialisation")


def _normalise_mapping(config: Mapping[str, Any]) -> MutableMapping[str, Any]:
    if hasattr(config, "to_container"):
        try:
            return config.to_container(resolve=True)  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - fall back to simple dict conversion
            return dict(config)  # type: ignore[arg-type]
    return dict(config)


def _resolve_value(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _resolve_dtype(name: str | None) -> Any:
    _ensure_torch()
    if not name:
        return torch.float32
    key = str(name).lower()
    if key == "auto":
        return torch.float32
    try:
        return _DTYPE_MAP[key]
    except KeyError as exc:  # pragma: no cover - invalid dtype routed to caller
        raise ValueError(
            f"Unsupported dtype '{name}'. Expected one of {sorted(_DTYPE_MAP)}"
        ) from exc


def _resolve_device(name: str | None) -> str:
    if not name or name == "auto":
        cuda_available = False
        if _HAS_TORCH and torch is not None:
            cuda_is_available = getattr(torch.cuda, "is_available", None)
            if callable(cuda_is_available):
                cuda_available = bool(cuda_is_available())
        if cuda_available:
            return "cuda"
        return "cpu"
    return str(name)


@dataclass
class LoraSettings:
    enabled: bool = False
    r: int = 8
    alpha: int = 16
    dropout: float = 0.0
    target_modules: Sequence[str] = field(default_factory=lambda: ("q_proj", "v_proj"))
    bias: str = "none"
    task_type: str = "CAUSAL_LM"


@dataclass
class ModelInitConfig:
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
        "pretrained_model_name_or_path",
        "model_name_or_path",
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
    if AutoTokenizer is None:  # pragma: no cover - optional dependency missing
        raise RuntimeError("transformers is required to load tokenizers")

    coerced = config if isinstance(config, ModelInitConfig) else _coerce_config(config)
    tokenizer_name = coerced.tokenizer_name or coerced.model_name

    kwargs: dict[str, Any] = {}
    if coerced.trust_remote_code:
        kwargs["trust_remote_code"] = True

    revision = coerced.load_config.get("revision") or coerced.load_config.get("commit_id")
    if revision is None:
        kwargs["revision"] = get_hf_revision()

    try:
        return load_from_pretrained(AutoTokenizer, tokenizer_name, **kwargs)
    except Exception as exc:  # pragma: no cover - wrap dependency errors for clarity
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


def _coerce_torch_dtype(dtype: Any) -> Any:
    if dtype is None:
        return None
    if not isinstance(dtype, str):
        return dtype
    if not (_HAS_TORCH and torch is not None):
        raise RuntimeError("torch is required to resolve dtype strings")
    if dtype.lower() == "auto":
        return None
    mapping = {
        "fp32": torch.float32,
        "float32": torch.float32,
        "fp16": torch.float16,
        "float16": torch.float16,
        "half": torch.float16,
        "bf16": torch.bfloat16,
        "bfloat16": torch.bfloat16,
    }
    try:
        return mapping[dtype.lower()]
    except KeyError as exc:  # pragma: no cover - invalid dtype routed to caller
        raise ValueError(f"Unsupported dtype '{dtype}'. Expected one of {sorted(mapping)}") from exc


def load_model(
    config: Mapping[str, Any] | ModelInitConfig,
) -> PreTrainedModel:
    if AutoModelForCausalLM is None:  # pragma: no cover - transformers missing
        raise RuntimeError("transformers is required to load models")

    coerced = config if isinstance(config, ModelInitConfig) else _coerce_config(config)
    _ensure_torch()
    dtype_obj = _resolve_dtype(coerced.dtype)
    device = _resolve_device(coerced.device)
    _assert_bf16_capability(coerced.dtype, dtype_obj, device, coerced.bf16_require_capability)

    load_kwargs = dict(coerced.load_config)
    load_kwargs.setdefault("torch_dtype", dtype_obj)
    load_kwargs.setdefault("low_cpu_mem_usage", True)
    if coerced.trust_remote_code:
        load_kwargs.setdefault("trust_remote_code", True)

    revision = load_kwargs.pop("revision", None)
    commit_id = load_kwargs.pop("commit_id", None)
    if revision is None and commit_id is None:
        revision = get_hf_revision()
    if commit_id is not None:
        load_kwargs["commit_id"] = commit_id
    if revision is not None:
        load_kwargs["revision"] = revision

    LOGGER.debug("Loading model '%s' with kwargs=%s", coerced.model_name, load_kwargs)
    try:
        model = load_from_pretrained(
            AutoModelForCausalLM,
            coerced.model_name,
            **load_kwargs,
        )
    except OSError as exc:  # pragma: no cover - surface friendlier offline errors
        message = (
            f"Unable to load model '{coerced.model_name}'. "
            "Ensure the weights are available locally."
        )
        raise RuntimeError(message) from exc
    except Exception as exc:  # pragma: no cover - propagate with additional context
        raise RuntimeError(
            f"Unexpected error while loading model '{coerced.model_name}': {exc}"
        ) from exc

    try:
        model = model.to(device)
    except Exception as exc:  # pragma: no cover - device transfer failures
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


def _get_registry_factory(name: str):
    try:
        from codex_ml.models.loader_registry import get_model

        return get_model(name)
    except Exception:
        return None


def _invoke_registry(
    factory,
    *,
    dtype: str,
    device_map: str | None,
    lora: dict[str, Any] | None,
) -> tuple[Any, Any]:
    result = factory(
        dtype=dtype,
        device_map=device_map,
        lora=lora,
        include_tokenizer=True,
    )
    if isinstance(result, tuple) and len(result) == 2:
        return result
    if isinstance(result, dict):
        model = result.get("model")
        tokenizer = result.get("tokenizer")
        if model is not None and tokenizer is not None:
            return model, tokenizer
    model = getattr(result, "model", None)
    tokenizer = getattr(result, "tokenizer", None)
    if model is not None and tokenizer is not None:
        return model, tokenizer
    raise TypeError(
        "Registry factory must return (model, tokenizer) tuple, mapping, or an "
        "object with 'model'/'tokenizer' attributes."
    )


def load_model_and_tokenizer(
    config: Mapping[str, Any] | ModelInitConfig | str,
    *,
    dtype: str | Any = "auto",
    device_map: str = "auto",
    lora: dict[str, Any] | None = None,
) -> tuple[Any, Any]:
    if isinstance(config, (Mapping | ModelInitConfig)):
        coerced = config if isinstance(config, ModelInitConfig) else _coerce_config(config)
        model = load_model(coerced)
        tokenizer = load_tokenizer(coerced)
        return model, tokenizer

    model_name = str(config)
    factory = _get_registry_factory(model_name)
    if factory is not None:
        return _invoke_registry(factory, dtype=dtype, device_map=device_map, lora=lora)

    if not (_HAS_TORCH and _HAS_TRANSFORMERS):
        raise ImportError("torch and transformers are required for model loading")

    torch_dtype = _coerce_torch_dtype(dtype)
    revision = get_hf_revision()
    tok = load_from_pretrained(
        AutoTokenizer,
        model_name,
        use_fast=True,
        revision=revision,
    )
    model_kwargs: dict[str, Any] = {"device_map": device_map}
    if torch_dtype is not None:
        model_kwargs["torch_dtype"] = torch_dtype
    model = load_from_pretrained(
        AutoModelForCausalLM,
        model_name,
        revision=revision,
        **model_kwargs,
    )
    if lora and get_peft_model and LoraConfig:
        base_cfg = {
            "r": 8,
            "lora_alpha": 16,
            "lora_dropout": 0.0,
            "bias": "none",
            "task_type": "CAUSAL_LM",
        }
        base_cfg.update(lora)
        cfg = LoraConfig(**base_cfg)
        model = get_peft_model(model, cfg)
    # else: optional dependency missing; silently continue with base model
    return model, tok


__all__ = [
    "LoraSettings",
    "ModelInitConfig",
    "_assert_bf16_capability",
    "load_model",
    "load_model_and_tokenizer",
    "load_tokenizer",
]
