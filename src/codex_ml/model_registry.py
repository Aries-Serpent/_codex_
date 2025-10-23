"""High-level model registry helpers with device/dtype convenience.

This module provides a lightweight wrapper around :mod:`codex_ml.models.registry`
that keeps the public surface compact for callers that only need to
instantiate a model with predictable device and dtype semantics.  Optional
LoRA adapter activation is supported when the underlying model exposes the
``load_adapter``/``set_active_adapters`` interface used by the PEFT library.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Optional, Union

import torch
from codex_ml.models import registry as _registry

__all__ = ["ModelRequest", "get_model", "list_models", "register_model"]


@dataclass(frozen=True)
class ModelRequest:
    """Capture parameters passed to :func:`get_model` for introspection."""

    name: str
    device: Optional[Union[str, torch.device]] = None
    dtype: Optional[Union[str, torch.dtype]] = None
    lora_adapter: Optional[str] = None
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
        if self.config:
            payload["config"] = dict(self.config)
        return payload


def _normalise_device(device: Union[str, object, None]) -> Union[str, None]:
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


def _normalise_dtype(dtype: Union[str, object, None]) -> Union[str, None]:
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
        except Exception:
            adapter_name = None
        else:
            set_active = getattr(model, "set_active_adapters", None)
            if callable(set_active) and adapter_name is not None:
                try:
                    set_active(adapter_name)
                    return
                except Exception:
                    pass
    try:
        setattr(model, "lora_adapter_path", adapter_path)
    except Exception:
        # Silently ignore failures; attaching metadata is best effort.
        pass


def _prepare_config(
    name: str,
    config: Mapping[str, Any] | None,
    device: Union[str, torch.device, None],
    dtype: Union[str, torch.dtype, None],
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
    *,
    device: Union[str, torch.device, None] = "cpu",
    dtype: Union[str, torch.dtype, None] = torch.float32,
    lora_adapter: str | None = None,
    config: Mapping[str, Any] | None = None,
) -> Any:
    """Instantiate a model registered under ``name``.

    Parameters
    ----------
    name:
        Registry identifier for the desired model.
    device:
        Target device for the model.  ``torch.device`` objects are converted to a
        canonical string form that the lower-level registry understands.
    dtype:
        Desired ``torch.dtype`` or string alias (``"fp16"``, ``torch.float16``).
    lora_adapter:
        Optional path to a LoRA adapter checkpoint.  When provided the helper
        attempts to call ``load_adapter``/``set_active_adapters`` on the
        underlying model.  Failure to load the adapter is treated as a warning
        rather than an error to keep the helper resilient in partially
        configured environments.
    config:
        Additional configuration dictionary forwarded to the registered
        builder.  Values supplied here take precedence over the helper
        defaults.
    """

    prepared_cfg = _prepare_config(name, config, device, dtype)
    model = _registry.get_model(name, prepared_cfg)

    # Ensure dtype/device are applied even when the builder ignores overrides.
    normalised_dtype = _normalise_dtype(dtype)
    if normalised_dtype:
        torch_dtype = getattr(torch, normalised_dtype, None)
        if torch_dtype is not None:
            try:
                model = model.to(dtype=torch_dtype)
            except Exception:
                pass
    normalised_device = _normalise_device(device)
    if isinstance(normalised_device, str):
        try:
            model = model.to(device=normalised_device)
        except Exception:
            pass

    if lora_adapter:
        _activate_lora_adapter(model, lora_adapter)
    try:
        setattr(model, "request_metadata", ModelRequest(name, device, dtype, lora_adapter, config))
    except Exception:
        # Attaching metadata is best-effort only.
        pass
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
