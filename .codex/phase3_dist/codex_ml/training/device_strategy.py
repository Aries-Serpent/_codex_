"""Utilities for consistent device and dtype placement across training runs."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass
from typing import Any, Optional

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import torch

    # Verify torch is actually functional (not just a stub)
    _ = torch.float32  # Test access to a common attribute
    _HAS_TORCH = True
except (ImportError, AttributeError):  # pragma: no cover - defensive import guard
    torch = None  # type: ignore[assignment]
    _HAS_TORCH = False


def _torch_required() -> None:
    if torch is None:  # pragma: no cover - environment without torch
        raise RuntimeError("torch is required for device placement but is not installed")


def _supports_bfloat16() -> bool:
    """Check if bfloat16 is supported on current device."""
    if torch is None:
        return False
    try:
        if torch.cuda.is_available():
            # Check compute capability for bfloat16 support (Ampere and newer)
            try:
                capability = torch.cuda.get_device_capability()
                # Ampere (8.x) and newer support bfloat16 efficiently
                return capability[0] >= 8
            except (ValueError, TypeError, RuntimeError):
                logger.warning("Exception occurred", exc_info=True)
                # Try alternative check
                checker = getattr(torch.cuda, "is_bf16_supported", None)
                if callable(checker):
                    return bool(checker())
        if getattr(torch.backends, "mps", None):  # pragma: no branch - optional backend
            mps = torch.backends.mps
            return bool(getattr(mps, "is_built", lambda: False)())
    except (ImportError, AttributeError):  # pragma: no cover - conservative fallback
        return False
    return False


def _device_available(name: str) -> bool:
    """Check if a device is available."""
    if torch is None:
        return False
    try:
        if name == "cuda":
            return torch.cuda.is_available()
        if name == "mps":
            return hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    except Exception:  # pragma: no cover - safety net
        return False
    return name == "cpu"


@dataclass
class DeviceConfig:
    """Configuration bundle describing target device and dtype.

    Attributes:
        device: Target device ("cpu", "cuda", "mps", "cuda:0", etc.)
        dtype: Model dtype (torch.float32, torch.float16, torch.bfloat16)
        mixed_precision: Whether to use mixed precision training
        autocast_dtype: Dtype for autocast context (when mixed_precision=True)
    """

    device: str
    dtype: Any  # torch.dtype, but avoid hard dependency
    mixed_precision: bool = False
    autocast_dtype: Optional[Any] = None

    @classmethod
    def auto_detect(
        cls, *, prefer_mps: bool = True, allow_mixed_precision: bool = True
    ) -> DeviceConfig:
        """Infer an appropriate DeviceConfig for the current host.

        Detection logic:
        - CUDA available → use cuda with float16/bfloat16 based on capability
        - MPS available (Apple Silicon) → use mps with float32
        - CPU only → use cpu with float32

        Args:
            prefer_mps: Whether to prefer MPS over CPU if available
            allow_mixed_precision: Whether to enable mixed precision when supported

        Returns:
            DeviceConfig with auto-detected settings
        """
        _torch_required()
        if torch is None:
            raise RuntimeError("torch is required for device strategy operations")

        if _device_available("cuda"):
            device = "cuda"
            if allow_mixed_precision:
                if _supports_bfloat16():
                    return cls(
                        device=device,
                        dtype=torch.bfloat16,
                        mixed_precision=True,
                        autocast_dtype=torch.bfloat16,
                    )
                return cls(
                    device=device,
                    dtype=torch.float16,
                    mixed_precision=True,
                    autocast_dtype=torch.float16,
                )
            return cls(device=device, dtype=torch.float32, mixed_precision=False)

        if prefer_mps and _device_available("mps"):
            if allow_mixed_precision and _supports_bfloat16():
                return cls(
                    device="mps",
                    dtype=torch.bfloat16,
                    mixed_precision=True,
                    autocast_dtype=torch.bfloat16,
                )
            return cls(device="mps", dtype=torch.float32, mixed_precision=False)

        return cls(device="cpu", dtype=torch.float32, mixed_precision=False)

    def apply_to_model(self, model: Any) -> Any:
        """Move model to the configured device/dtype with graceful fallback.

        Args:
            model: Model to move

        Returns:
            Model on target device/dtype

        Raises:
            ValueError: If device specification is invalid
        """
        _torch_required()
        if torch is None:
            raise RuntimeError("torch is required for device strategy operations")

        try:
            target_device = torch.device(self.device)
        except Exception as exc:  # pragma: no cover - invalid device string
            raise ValueError(f"invalid device specification: {self.device}") from exc

        try:
            # In mixed precision mode, keep model in float32
            if self.mixed_precision:
                model = model.to(device=target_device, dtype=torch.float32)
            else:
                model = model.to(device=target_device, dtype=self.dtype)
            return model
        except (ValueError, TypeError, RuntimeError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            LOGGER.warning(
                "[codex] failed to place model on %s (%s); falling back to CPU fp32",
                self.device,
                exc,
            )
            return model.to(device=torch.device("cpu"), dtype=torch.float32)

    def apply_to_tensor(self, tensor: Any) -> Any:
        """Return tensor on the configured device and dtype.

        Args:
            tensor: Tensor to move

        Returns:
            Tensor on target device/dtype
        """
        _torch_required()
        if torch is None:
            raise RuntimeError("torch is required for device strategy operations")

        try:
            return tensor.to(device=torch.device(self.device), dtype=self.dtype)
        except (ValueError, TypeError, RuntimeError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            LOGGER.warning(
                "[codex] failed to move tensor to %s (%s); returning CPU copy",
                self.device,
                exc,
            )
            return tensor.to(device=torch.device("cpu"), dtype=torch.float32)


class DeviceMapper:
    """Lightweight registry for reusable DeviceConfig strategies."""

    _STRATEGIES: dict[str, DeviceConfig] = {}

    @classmethod
    def register_strategy(cls, name: str, config: DeviceConfig) -> None:
        """Register a named device strategy.

        Args:
            name: Strategy name
            config: Device configuration
        """
        key = name.strip().lower()
        if not key:
            raise ValueError("strategy name must be non-empty")
        cls._STRATEGIES[key] = config

    @classmethod
    def get_strategy(cls, name: str) -> DeviceConfig:
        """Get a registered device strategy.

        Args:
            name: Strategy name

        Returns:
            Device configuration

        Raises:
            KeyError: If strategy not found
        """
        key = name.strip().lower()
        try:
            return cls._STRATEGIES[key]
        except KeyError as exc:
            type(exc).__name__
            logger.debug("KeyError: <ERROR_TYPE>")
            raise KeyError(f"device strategy not registered: {name}") from exc

    @classmethod
    def list_strategies(cls) -> list[str]:
        """list all registered strategy names.

        Returns:
            list of strategy names
        """
        return sorted(cls._STRATEGIES.keys())


def get_device_config(
    device: Optional[str] = None,
    *,
    dtype: Optional[Any] = None,
    mixed_precision: Optional[bool] = None,
) -> DeviceConfig:
    """Get or create a DeviceConfig.

    If device is None, auto-detects optimal configuration.

    Args:
        device: Target device string or None for auto-detection
        dtype: Target dtype or None for auto-selection
        mixed_precision: Whether to use mixed precision or None for auto

    Returns:
        DeviceConfig instance
    """
    if device is None:
        return DeviceConfig.auto_detect()

    if dtype is None and _HAS_TORCH:
        dtype = torch.float32
    elif dtype is None:
        dtype = "float32"

    if mixed_precision is None:
        mixed_precision = False

    return DeviceConfig(device=device, dtype=dtype, mixed_precision=mixed_precision)


# Pre-register a default auto strategy at import time when torch is available.
if _HAS_TORCH:  # pragma: no branch - simple guard
    try:
        DeviceMapper.register_strategy("auto", DeviceConfig.auto_detect())
    except RuntimeError:  # pragma: no cover - guard when torch import works but usage fails
        logger.debug("Suppressed exception in handler", exc_info=True)
__all__ = ["DeviceConfig", "DeviceMapper", "get_device_config"]
