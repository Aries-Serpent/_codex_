"""High-level model registry helpers with device/dtype convenience.

This module provides a lightweight wrapper around :mod:`codex_ml.models.registry`
that keeps the public surface compact for callers that only need to
instantiate a model with predictable device and dtype semantics.  Optional
LoRA adapter activation is supported when the underlying model exposes the
``load_adapter``/``set_active_adapters`` interface used by the PEFT library.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections.abc import Mapping, MutableMapping, Sequence  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

import torch  # noqa: E402
from codex_ml.models import registry as _registry  # noqa: E402
from codex_ml.models.utils.peft import apply_lora_if_available  # noqa: E402

__all__ = ["LoraRequest", "ModelRequest", "get_model", "list_models", "register_model"]


@dataclass(frozen=True)
class LoraRequest:
    """Immutable representation of LoRA/PEFT parameters."""

    enabled: bool
    rank: int = 8
    alpha: int = 16
    dropout: float = 0.05
    task_type: str | None = None
    target_modules: Sequence[str] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "enable": self.enabled,
            "r": int(self.rank),
            "alpha": int(self.alpha),
            "dropout": float(self.dropout),
        }
        if self.task_type is not None:
            payload["task_type"] = self.task_type
        if self.target_modules is not None:
            payload["target_modules"] = list(self.target_modules)
        return payload


@dataclass(frozen=True)
class ModelRequest:
    """Capture parameters passed to :func:`get_model` for introspection."""

    name: str
    device: Optional[str | torch.device] = None
    dtype: Optional[str | torch.dtype] = None
    lora_adapter: Optional[str] = None
    # Use the new immutable LoRA request container
    lora: Optional[LoraRequest] = None
    # Keep config last to preserve the intended field order
    config: Mapping[str, Any] | None = None

    def as_config(self) -> dict[str, Any]:
        """Return a serialisable dictionary describing the request."""

        payload: dict[str, Any] = {"name": self.name}
        if self.device is not None:
            payload["device"] = str(self.device)
        if self.dtype is not None:
            payload["dtype"] = str(self.dtype)
        if self.lora_adapter is not None:
            payload["lora_adapter"] = self.lora_adapter
        if self.lora is not None:
            payload["lora"] = {
                "enabled": self.lora.enabled,
                "rank": self.lora.rank,
                "alpha": self.lora.alpha,
                "dropout": self.lora.dropout,
                "task_type": self.lora.task_type,
                "target_modules": (
                    list(self.lora.target_modules) if self.lora.target_modules is not None else None
                ),
            }
        if self.config:
            payload["config"] = dict(self.config)
        if self.lora is not None:
            payload["lora"] = self.lora.as_dict()
        return payload


def _normalise_device(device: str | object | None) -> str | None:
    if device is None:
        return None
    if isinstance(device, str):
        return device
    dev_type = getattr(device, "type", None)
    dev_index = getattr(device, "index", None)
    if isinstance(dev_type, str):
        if dev_index in (None, -1):
            return dev_type
        return f"{dev_type}:{dev_index}"
    return str(device)


def _normalise_dtype(dtype: str | object | None) -> str | None:
    if dtype is None:
        return None
    if isinstance(dtype, str):
        text = dtype.strip()
    else:
        text = str(dtype).strip()
        if text.startswith("<") and text.endswith(">"):
            parts = text.split()
            if parts:
                text = parts[-1].rstrip(">")
    if not text:
        return None
    attr = text.split(".")[-1]
    return attr or text


def _activate_lora_adapter(model: Any, adapter_path: str) -> None:
    """Best-effort activation of a LoRA adapter."""

    load_adapter = getattr(model, "load_adapter", None)
    if callable(load_adapter):
        try:
            adapter_name = load_adapter(adapter_path)
        except (IOError, OSError):
            logger.warning("Exception occurred", exc_info=True)
        else:
            set_active = getattr(model, "set_active_adapters", None)
            if callable(set_active) and adapter_name is not None:
                try:
                    set_active(adapter_name)
                    return
                except (IOError, OSError) as e:
                    type(e).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    try:
        model.lora_adapter_path = adapter_path
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        # Silently ignore failures; attaching metadata is best effort.


def _to_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    try:
        return bool(value)
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return default


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return default


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return default


def _normalise_target_modules(value: Any) -> Sequence[str] | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple, set)):
        modules = [str(item).strip() for item in value if str(item).strip()]
        return tuple(modules) if modules else None
    if isinstance(value, str):
        modules = [part.strip() for part in value.split(",") if part.strip()]
        return tuple(modules) if modules else None
    return None


def _extract_lora_request(config: Mapping[str, Any] | None) -> LoraRequest | None:
    if not isinstance(config, Mapping):
        return None

    candidate: Mapping[str, Any] | None = None
    for key in ("lora", "peft"):
        maybe = config.get(key)
        if isinstance(maybe, Mapping):
            candidate = maybe
            break

    if candidate is not None:
        enabled = _to_bool(candidate.get("enable"), False)
        enabled = _to_bool(candidate.get("enabled"), enabled)
        enabled = _to_bool(candidate.get("use"), enabled)
        if not enabled:
            return LoraRequest(enabled=False)
        rank = _to_int(
            candidate.get("r", candidate.get("rank", candidate.get("lora_r", 8))),
            8,
        )
        alpha = _to_int(candidate.get("alpha", candidate.get("lora_alpha", 16)), 16)
        dropout = _to_float(candidate.get("dropout", candidate.get("lora_dropout", 0.05)), 0.05)
        task_type_value = candidate.get("task_type")
        task_type = str(task_type_value) if task_type_value is not None else None
        target_modules = _normalise_target_modules(candidate.get("target_modules"))
        return LoraRequest(
            enabled=True,
            rank=rank,
            alpha=alpha,
            dropout=dropout,
            task_type=task_type,
            target_modules=target_modules,
        )

    # Fallback to legacy flat keys (lora_enable/lora_r/etc.).
    if any(key in config for key in ("lora_enable", "lora_r", "lora_alpha", "lora_dropout")):
        enabled = _to_bool(config.get("lora_enable"), False)
        rank = _to_int(config.get("lora_r", 8), 8)
        alpha = _to_int(config.get("lora_alpha", 16), 16)
        dropout = _to_float(config.get("lora_dropout", 0.05), 0.05)
        return LoraRequest(
            enabled=enabled,
            rank=rank,
            alpha=alpha,
            dropout=dropout,
            task_type=None,
            target_modules=None,
        )

    return None


def _prepare_config(
    name: str,
    config: Mapping[str, Any] | None,
    device: str | torch.device | None,
    dtype: str | torch.dtype | None,
) -> dict[str, Any]:
    cfg: dict[str, Any]
    if isinstance(config, MutableMapping):
        cfg = dict(config)
    elif config is None:
        cfg = {}
    else:
        cfg = dict(config)
    normalised_device = _normalise_device(device)
    if normalised_device is not None:
        cfg.setdefault("device", normalised_device)
    normalised_dtype = _normalise_dtype(dtype)
    if normalised_dtype is not None and hasattr(torch, "dtype"):
        cfg.setdefault("dtype", normalised_dtype)
    return cfg


def get_model(
    name: str,
    config: Mapping[str, Any] | None = None,
    *,
    device: str | torch.device | None = "cpu",
    dtype: str | torch.dtype | None = torch.float32,
    lora_adapter: str | None = None,
) -> Any:
    """Instantiate a model registered under ``name``.

    Parameters
    ----------
    name:
        Registry identifier for the desired model.
    config:
        Additional configuration dictionary forwarded to the registered
        builder.  Values supplied here take precedence over the helper
        defaults. May be passed as a positional argument for backward
        compatibility.
    device:
        Target device for the model.  ``torch.device`` objects are converted to a
        canonical string form that the lower-level registry understands.
        Keyword-only parameter.
    dtype:
        Desired ``torch.dtype`` or string alias (``"fp16"``, ``torch.float16``).
        Keyword-only parameter.
    lora_adapter:
        Optional path to a LoRA adapter checkpoint.  When provided the helper
        attempts to call ``load_adapter``/``set_active_adapters`` on the
        underlying model.  Failure to load the adapter is treated as a warning
        rather than an error to keep the helper resilient in partially
        configured environments. Keyword-only parameter.
    """

    prepared_cfg = _prepare_config(name, config, device, dtype)
    lora_request = _extract_lora_request(config)
    model = _registry.get_model(name, prepared_cfg)

    # Ensure dtype/device are applied even when the builder ignores overrides.
    normalised_dtype = _normalise_dtype(dtype)
    if normalised_dtype:
        torch_dtype = getattr(torch, normalised_dtype, None)
        if torch_dtype is not None:
            try:
                model = model.to(dtype=torch_dtype)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    normalised_device = _normalise_device(device)
    if isinstance(normalised_device, str):
        try:
            model = model.to(device=normalised_device)
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

    if lora_adapter:
        _activate_lora_adapter(model, lora_adapter)
    if lora_request and lora_request.enabled:
        already_wrapped = getattr(model, "peft_config", None) is not None
        if not already_wrapped:
            model = apply_lora_if_available(
                model,
                r=lora_request.rank,
                alpha=lora_request.alpha,
                dropout=lora_request.dropout,
                task_type=lora_request.task_type,
                target_modules=lora_request.target_modules,
            )
    try:
        model.request_metadata = ModelRequest(
            name=name,
            device=device,
            dtype=dtype,
            lora_adapter=lora_adapter,
            lora=lora_request,
            config=config,
        )
    except (ConnectionError, TimeoutError):
        logger.warning("Exception occurred", exc_info=True)
        # Attaching metadata is best-effort only.

    # Note: legacy _apply_lora(model, lora_settings) removed; LoRA is applied above.
    return model


def register_model(name: str, obj: Any | None = None, *, override: bool = False) -> Any:
    """Proxy for :func:`codex_ml.models.registry.register_model`."""

    return _registry.register_model(name, obj, override=override)


def list_models() -> list[str]:
    """Return available model registrations."""

    return _registry.list_models()


def ensure_ml_artifacts_dir(root: str | Path) -> Path:
    """Create and return a directory suitable for model artefacts."""

    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    return path
