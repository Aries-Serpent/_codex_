"""Utilities for consistent device and dtype placement across training runs."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - defensive import guard
    torch = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)


def _torch_required() -> None:
    if torch is None:  # pragma: no cover - environment without torch
        raise RuntimeError("torch is required for device placement but is not installed")


def _supports_bfloat16() -> bool:
    if torch is None:
        return False
    try:
        if torch.cuda.is_available():
            checker = getattr(torch.cuda, "is_bf16_supported", None)
            if callable(checker):
                return bool(checker())
        if getattr(torch.backends, "mps", None):  # pragma: no branch - optional backend
            mps = torch.backends.mps
            return bool(getattr(mps, "is_built", lambda: False)())
    except Exception:  # pragma: no cover - conservative fallback
        return False
    return False


def _device_available(name: str) -> bool:
    if torch is None:
        return False
    try:
        if name == "cuda":
            return torch.cuda.is_available()
        if name == "mps":
            return getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_built()
    except Exception:  # pragma: no cover - safety net
        return False
    return name == "cpu"


@dataclass
class DeviceConfig:
    """Configuration bundle describing target device and dtype."""

    device: str
    dtype: "torch.dtype"
    mixed_precision: bool = False

    @classmethod
    def auto_detect(cls, *, prefer_mps: bool = True, allow_mixed_precision: bool = True) -> "DeviceConfig":
        """Infer an appropriate :class:`DeviceConfig` for the current host."""

        _torch_required()
        assert torch is not None  # for type checkers

        if _device_available("cuda"):
            device = "cuda"
            if allow_mixed_precision:
                if _supports_bfloat16():
                    return cls(device=device, dtype=torch.bfloat16, mixed_precision=True)
                return cls(device=device, dtype=torch.float16, mixed_precision=True)
            return cls(device=device, dtype=torch.float32, mixed_precision=False)

        if prefer_mps and _device_available("mps"):
            if allow_mixed_precision and _supports_bfloat16():
                return cls(device="mps", dtype=torch.bfloat16, mixed_precision=True)
            return cls(device="mps", dtype=torch.float32, mixed_precision=False)

        return cls(device="cpu", dtype=torch.float32, mixed_precision=False)

    def apply_to_model(self, model: "torch.nn.Module") -> "torch.nn.Module":
        """Move ``model`` to the configured device/dtype with graceful fallback."""

        _torch_required()
        assert torch is not None  # for type checkers

        try:
            target_device = torch.device(self.device)
        except Exception as exc:  # pragma: no cover - invalid device string
            raise ValueError(f"invalid device specification: {self.device}") from exc

        try:
            model = model.to(device=target_device, dtype=self.dtype)
            return model
        except Exception as exc:
            LOGGER.warning(
                "[codex] failed to place model on %s (%s); falling back to CPU fp32", self.device, exc
            )
            model = model.to(device=torch.device("cpu"), dtype=torch.float32)
            return model

    def apply_to_tensor(self, tensor: "torch.Tensor") -> "torch.Tensor":
        """Return ``tensor`` on the configured device and dtype."""

        _torch_required()
        assert torch is not None  # for type checkers

        try:
            return tensor.to(device=torch.device(self.device), dtype=self.dtype)
        except Exception as exc:
            LOGGER.warning(
                "[codex] failed to move tensor to %s (%s); returning CPU copy", self.device, exc
            )
            return tensor.to(device=torch.device("cpu"), dtype=torch.float32)


class DeviceMapper:
    """Lightweight registry for reusable :class:`DeviceConfig` strategies."""

    _STRATEGIES: Dict[str, DeviceConfig] = {}

    @classmethod
    def register_strategy(cls, name: str, config: DeviceConfig) -> None:
        key = name.strip().lower()
        if not key:
            raise ValueError("strategy name must be non-empty")
        cls._STRATEGIES[key] = config

    @classmethod
    def get_strategy(cls, name: str) -> DeviceConfig:
        key = name.strip().lower()
        try:
            return cls._STRATEGIES[key]
        except KeyError as exc:
            raise KeyError(f"device strategy not registered: {name}") from exc


# Pre-register a default auto strategy at import time when torch is available.
if torch is not None:  # pragma: no branch - simple guard
    try:
        DeviceMapper.register_strategy("auto", DeviceConfig.auto_detect())
    except RuntimeError:  # pragma: no cover - guard when torch import works but usage fails
        pass

__all__ = ["DeviceConfig", "DeviceMapper"]
