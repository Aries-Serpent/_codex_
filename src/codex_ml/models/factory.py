"""Minimal model factory with dtype/device utilities and optional PEFT hooks."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import fields
from typing import Any, Callable, Mapping, MutableMapping, Optional

try:  # pragma: no cover - optional transformers dependency
    from transformers import BitsAndBytesConfig
except Exception:  # pragma: no cover - transformers/quantization optional
    BitsAndBytesConfig = None

from .peft_hooks import LoraBuildCfg, build_lora

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - torch optional in lightweight envs
    torch = None  # type: ignore

logger = logging.getLogger(__name__)

ENV_ENABLE_PEFT = "CODEX_ML_ENABLE_PEFT"
ENV_ENABLE_PEFT_ALT = "CODEX_ENABLE_PEFT"
ENV_QUANTIZATION = "CODEX_ML_QUANTIZATION"
ENV_LORA_CONFIG = "CODEX_ML_LORA_CONFIG"
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
        if token == "auto":  # nosec B105 - device keyword, not a credential
            token = "cuda" if torch.cuda.is_available() else "cpu"
        return torch.device(token)
    return value


def _should_enable_peft(explicit: Optional[bool]) -> bool:
    if explicit is not None:
        return bool(explicit)
    env_value = os.getenv(ENV_ENABLE_PEFT) or os.getenv(ENV_ENABLE_PEFT_ALT)
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
        filtered: dict[str, Any] = {key: value for key, value in cfg.items() if key in allowed}
        return LoraBuildCfg(**filtered)
    raise TypeError(
        "LoRA configuration must be a mapping or LoraBuildCfg instance; " f"received {type(cfg)!r}."
    )


def validate_lora_config(cfg: Any) -> LoraBuildCfg:
    """Validate LoRA hyperparameters, returning a ``LoraBuildCfg``."""

    lora_cfg = _coerce_lora_cfg(cfg)
    if lora_cfg is None:
        raise ValueError("LoRA configuration is required when PEFT is enabled")

    errors = []
    if lora_cfg.r is not None and lora_cfg.r <= 0:
        errors.append("lora r must be > 0")
    if lora_cfg.alpha is not None and lora_cfg.alpha <= 0:
        errors.append("lora alpha must be > 0")
    if lora_cfg.dropout is not None and not (0 <= lora_cfg.dropout < 1):
        errors.append("lora dropout must be in [0, 1)")
    if errors:
        raise ValueError("; ".join(errors))
    return lora_cfg


def _load_lora_from_env() -> Optional[LoraBuildCfg]:
    payload = os.getenv(ENV_LORA_CONFIG)
    if not payload:
        return None
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in %s; ignoring", ENV_LORA_CONFIG)
        return None
    return _coerce_lora_cfg(data)


def _call_builder(builder: Callable[..., Any], params: MutableMapping[str, Any]) -> Any:
    if not params:
        return builder()
    try:
        return builder(**params)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        try:
            return builder(dict(params))
        except TypeError as e:
            logger.debug(f"TypeError: {e}")
            logger.warning(f"TypeError: {e}", exc_info=True)
            raise exc


def _apply_quantization_options(options: MutableMapping[str, Any], quantization: Any) -> None:
    """Normalize quantization hints into builder kwargs.

    Parameters
    ----------
    options:
        Mutable mapping of keyword arguments that will be forwarded to the
        builder.  The mapping is mutated in-place.
    quantization:
        Quantization specification supplied via ``config["quantization"]`` or
        the explicit ``quantization`` keyword argument.  Supports the
        following shapes:

        - ``"8bit"``/``"int8"``/``True`` → set ``load_in_8bit=True``
        - ``"4bit"``/``"int4"`` → set ``load_in_4bit=True``
        - Mapping with optional ``mode``/``variant`` keys in addition to the
          standard ``BitsAndBytesConfig`` parameters.  When the mapping
          contains keys beyond ``load_in_8bit``/``load_in_4bit`` the
          ``transformers`` ``BitsAndBytesConfig`` class is required; an
          informative ``RuntimeError`` is raised otherwise.
    """

    if quantization is None:
        return

    payload = quantization
    if payload is True:
        payload = "8bit"

    bool_flags: dict[str, bool] = {}
    config_payload: dict[str, Any] = {}

    if isinstance(payload, str):
        token = payload.strip().lower()
        if token in {"8bit", "int8"}:
            bool_flags["load_in_8bit"] = True
        elif token in {"4bit", "int4"}:
            bool_flags["load_in_4bit"] = True
        else:
            raise ValueError(f"Unsupported quantization mode: {payload!r}")
    elif isinstance(payload, Mapping):
        data = dict(payload)
        mode = data.pop("mode", None) or data.pop("variant", None)
        if mode is not None:
            _apply_quantization_options(options, str(mode))
        for key in ("load_in_8bit", "load_in_4bit"):
            if key in data:
                bool_flags[key] = bool(data.pop(key))
        config_payload = data
    else:
        raise TypeError(
            "quantization must be a string, mapping, or boolean flag; "
            f"received {type(payload)!r}"
        )

    for key, value in bool_flags.items():
        options.setdefault(key, value)

    if config_payload:
        if BitsAndBytesConfig is None:
            raise RuntimeError(
                "Quantization parameters require transformers.BitsAndBytesConfig; "
                "install the 'bitsandbytes' extras to enable quantization."
            )
        # Avoid overriding a user-specified config; merge instead when possible
        if "quantization_config" in options and isinstance(
            options["quantization_config"], BitsAndBytesConfig
        ):
            existing = options["quantization_config"]
            for key, value in config_payload.items():
                setattr(existing, key, value)
        else:
            options.setdefault("quantization_config", BitsAndBytesConfig(**config_payload))


def create_model(
    builder: Callable[..., Any],
    *,
    config: Optional[Mapping[str, Any]] = None,
    dtype: Any = None,
    device: Any = None,
    enable_peft: Optional[bool] = None,
    lora_cfg: Any = None,
    quantization: Any = None,
) -> Any:
    """Instantiate a model and optionally apply dtype/device and PEFT adapters."""

    options: dict[str, Any] = dict(config or {})
    quantization_payload = (
        quantization if quantization is not None else options.pop("quantization", None)
    )
    if quantization_payload is None:
        env_quant = os.getenv(ENV_QUANTIZATION)
        if env_quant:
            quantization_payload = env_quant
    if quantization_payload is not None:
        _apply_quantization_options(options, quantization_payload)
    resolved_dtype = _resolve_dtype(dtype if dtype is not None else options.pop("dtype", None))
    resolved_device = _resolve_device(device if device is not None else options.pop("device", None))
    lora_payload = lora_cfg if lora_cfg is not None else options.pop("lora", None)
    if lora_payload is None:
        lora_payload = _load_lora_from_env()

    model = _call_builder(builder, options)

    if resolved_dtype is not None and hasattr(model, "to"):
        logger.debug("model_factory: applying dtype %s", resolved_dtype)
        model = model.to(dtype=resolved_dtype)
    if resolved_device is not None and hasattr(model, "to"):
        logger.debug("model_factory: moving model to %s", resolved_device)
        model = model.to(device=resolved_device)

    if _should_enable_peft(enable_peft):
        try:
            lora_config = (
                validate_lora_config(lora_payload) if lora_payload is not None else LoraBuildCfg()
            )
        except ValueError as exc:
            logger.debug(f"ValueError: {exc}")
            logger.warning("Invalid LoRA configuration: %s. Disabling PEFT.", exc)
            lora_config = None
        if lora_config is not None:
            logger.debug("model_factory: applying LoRA adapters with config: %s", lora_config)
            model = build_lora(model, lora_config)
        else:
            logger.debug(
                "model_factory: PEFT enabled but no valid LoRA configuration provided; skipping"
            )
    else:
        logger.debug("model_factory: PEFT disabled; skipping LoRA application")

    return model


class _MockModel:
    """Minimal model stub for smoke testing dtype/device resolution."""

    def __init__(self, dtype: Any, device: Any) -> None:
        self.dtype = dtype
        self.device = device


def load_model(config: Optional[Mapping[str, Any]] = None) -> _MockModel:
    """Simplified model loader for smoke testing (validates dtype/device handling).

    This is a minimal stub that validates dtype and device resolution without
    requiring an actual model builder. Used primarily for CI/smoke tests.

    Parameters
    ----------
    config : Optional[Mapping[str, Any]]
        Configuration mapping that may contain 'dtype' and 'device' keys.
        - 'dtype': string like 'float32', 'fp16', 'bfloat16' or torch.dtype
        - 'device': string like 'cpu', 'cuda', 'auto' or torch.device

    Returns
    -------
    _MockModel
        A mock model object with resolved dtype and device attributes.
    """
    if config is None:
        config = {}

    resolved_dtype = _resolve_dtype(config.get("dtype"))
    resolved_device = _resolve_device(config.get("device"))

    logger.debug("load_model smoke test: dtype=%s, device=%s", resolved_dtype, resolved_device)

    return _MockModel(resolved_dtype, resolved_device)


__all__ = [
    "create_model",
    "load_model",
    "_MockModel",
    "ENV_ENABLE_PEFT",
    "ENV_QUANTIZATION",
    "ENV_LORA_CONFIG",
    "LoraBuildCfg",
    "validate_lora_config",
]
