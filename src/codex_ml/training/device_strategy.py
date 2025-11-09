"""Device and dtype placement utilities for training.

This module provides automatic dtype and device placement inference to fix
precision mismatch between GPU and CPU environments. It offers:

- Auto-detection of optimal dtype/device based on system capabilities
- Mixed precision configuration support
- Device placement strategies for models and tensors
- Registered strategies for different deployment scenarios
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from codex_ml.utils.optional import optional_import

torch, _HAS_TORCH = optional_import("torch")


@dataclass
class DeviceConfig:
    """Configuration for device and dtype placement.
    
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
    def auto_detect(cls) -> "DeviceConfig":
        """Auto-detect optimal dtype/device based on system capabilities.
        
        Detection logic:
        - CUDA available → use cuda with float16/bfloat16 based on capability
        - MPS available (Apple Silicon) → use mps with float32
        - CPU only → use cpu with float32
        
        Returns:
            DeviceConfig with auto-detected settings
        """
        if not _HAS_TORCH:
            # Fallback for environments without torch
            return cls(device="cpu", dtype="float32", mixed_precision=False)

        # Check for CUDA
        if torch.cuda.is_available():
            device = "cuda"
            # Check compute capability for bfloat16 support (Ampere and newer)
            try:
                capability = torch.cuda.get_device_capability()
                # Ampere (8.x) and newer support bfloat16 efficiently
                if capability[0] >= 8:
                    dtype = torch.bfloat16
                    autocast_dtype = torch.bfloat16
                else:
                    # Older GPUs use float16
                    dtype = torch.float16
                    autocast_dtype = torch.float16
                mixed_precision = True
            except Exception:
                # Fallback if capability check fails
                dtype = torch.float32
                autocast_dtype = torch.float16
                mixed_precision = False

        # Check for MPS (Apple Silicon)
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
            dtype = torch.float32  # MPS works best with float32
            mixed_precision = False
            autocast_dtype = None

        # Fallback to CPU
        else:
            device = "cpu"
            dtype = torch.float32
            mixed_precision = False
            autocast_dtype = None

        return cls(
            device=device,
            dtype=dtype,
            mixed_precision=mixed_precision,
            autocast_dtype=autocast_dtype,
        )

    def apply_to_model(self, model: Any) -> Any:
        """Apply dtype and device to model.
        
        Args:
            model: torch.nn.Module to move to device/dtype
            
        Returns:
            Model on target device with target dtype
            
        Raises:
            RuntimeError: If torch is not available
        """
        if not _HAS_TORCH:
            raise RuntimeError("torch is required for apply_to_model")

        # Move to device first
        model = model.to(self.device)
        
        # Apply dtype if not using mixed precision
        # (with mixed precision, we keep model in float32 and use autocast)
        if not self.mixed_precision and self.dtype != torch.float32:
            model = model.to(self.dtype)
        
        return model

    def apply_to_tensor(self, tensor: Any) -> Any:
        """Apply dtype and device to tensor.
        
        Args:
            tensor: torch.Tensor to move to device/dtype
            
        Returns:
            Tensor on target device with target dtype
            
        Raises:
            RuntimeError: If torch is not available
        """
        if not _HAS_TORCH:
            raise RuntimeError("torch is required for apply_to_tensor")

        # Move to device
        result = tensor.to(self.device)
        
        # Apply dtype if specified and not using mixed precision
        if not self.mixed_precision and self.dtype != torch.float32:
            result = result.to(self.dtype)
        
        return result

    def get_autocast_context(self, enabled: bool = True) -> Any:
        """Get autocast context manager for mixed precision training.
        
        Args:
            enabled: Whether to enable autocast (default: True)
            
        Returns:
            torch.autocast context manager or nullcontext
        """
        if not _HAS_TORCH:
            import contextlib
            return contextlib.nullcontext()

        if not enabled or not self.mixed_precision:
            import contextlib
            return contextlib.nullcontext()

        # Determine device type for autocast
        device_type = self.device.split(":")[0]  # "cuda:0" -> "cuda"
        
        if device_type == "cuda" and self.autocast_dtype:
            return torch.autocast(device_type=device_type, dtype=self.autocast_dtype)
        elif device_type in ("cpu", "mps"):
            # CPU and MPS have different autocast support
            try:
                return torch.autocast(device_type=device_type)
            except Exception:
                import contextlib
                return contextlib.nullcontext()
        else:
            import contextlib
            return contextlib.nullcontext()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            "device": self.device,
            "dtype": str(self.dtype) if hasattr(self.dtype, "__name__") else str(self.dtype),
            "mixed_precision": self.mixed_precision,
            "autocast_dtype": (
                str(self.autocast_dtype)
                if self.autocast_dtype and hasattr(self.autocast_dtype, "__name__")
                else str(self.autocast_dtype) if self.autocast_dtype else None
            ),
        }


class DeviceMapper:
    """Registry for device/dtype strategies.
    
    This class maintains a registry of named device configurations
    that can be reused across different training runs.
    
    Example:
        >>> # Register a custom strategy
        >>> config = DeviceConfig(device="cuda:1", dtype=torch.float16, mixed_precision=True)
        >>> DeviceMapper.register_strategy("gpu1_fp16", config)
        >>> 
        >>> # Retrieve and use the strategy
        >>> strategy = DeviceMapper.get_strategy("gpu1_fp16")
        >>> model = strategy.apply_to_model(model)
    """

    _strategies: Dict[str, DeviceConfig] = {}

    @classmethod
    def register_strategy(cls, name: str, config: DeviceConfig) -> None:
        """Register a device/dtype strategy.
        
        Args:
            name: Strategy name (e.g., "gpu_fp16", "cpu_inference")
            config: DeviceConfig instance
        """
        cls._strategies[name] = config

    @classmethod
    def get_strategy(cls, name: str) -> DeviceConfig:
        """Get a registered strategy by name.
        
        Args:
            name: Strategy name
            
        Returns:
            DeviceConfig instance
            
        Raises:
            KeyError: If strategy name not found
        """
        if name not in cls._strategies:
            raise KeyError(
                f"Strategy '{name}' not found. "
                f"Available strategies: {list(cls._strategies.keys())}"
            )
        return cls._strategies[name]

    @classmethod
    def list_strategies(cls) -> list[str]:
        """List all registered strategy names.
        
        Returns:
            List of strategy names
        """
        return list(cls._strategies.keys())

    @classmethod
    def clear_strategies(cls) -> None:
        """Clear all registered strategies (useful for testing)."""
        cls._strategies.clear()


# Register common strategies
def _register_default_strategies() -> None:
    """Register common device strategies."""
    if not _HAS_TORCH:
        return

    # Auto-detect strategy (default)
    DeviceMapper.register_strategy("auto", DeviceConfig.auto_detect())

    # CPU strategies
    DeviceMapper.register_strategy(
        "cpu_fp32", DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
    )

    # CUDA strategies (if available)
    if torch.cuda.is_available():
        DeviceMapper.register_strategy(
            "cuda_fp32",
            DeviceConfig(device="cuda", dtype=torch.float32, mixed_precision=False),
        )
        DeviceMapper.register_strategy(
            "cuda_fp16",
            DeviceConfig(
                device="cuda",
                dtype=torch.float16,
                mixed_precision=True,
                autocast_dtype=torch.float16,
            ),
        )
        # Register bfloat16 if supported
        try:
            capability = torch.cuda.get_device_capability()
            if capability[0] >= 8:
                DeviceMapper.register_strategy(
                    "cuda_bf16",
                    DeviceConfig(
                        device="cuda",
                        dtype=torch.bfloat16,
                        mixed_precision=True,
                        autocast_dtype=torch.bfloat16,
                    ),
                )
        except Exception:
            pass

    # MPS strategies (if available)
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        DeviceMapper.register_strategy(
            "mps_fp32", DeviceConfig(device="mps", dtype=torch.float32, mixed_precision=False)
        )


# Initialize default strategies on module import
_register_default_strategies()


def get_device_config(
    strategy: Optional[str] = None,
    device: Optional[str] = None,
    dtype: Optional[Any] = None,
    mixed_precision: Optional[bool] = None,
) -> DeviceConfig:
    """Get a DeviceConfig with flexible input options.
    
    This is a convenience function that supports multiple ways of specifying
    device configuration:
    
    1. By strategy name: get_device_config(strategy="cuda_fp16")
    2. By explicit params: get_device_config(device="cuda", dtype=torch.float16)
    3. Auto-detect: get_device_config() or get_device_config(strategy="auto")
    
    Args:
        strategy: Named strategy (e.g., "auto", "cuda_fp16", "cpu_fp32")
        device: Explicit device string (overrides strategy)
        dtype: Explicit dtype (overrides strategy)
        mixed_precision: Explicit mixed precision flag (overrides strategy)
        
    Returns:
        DeviceConfig instance
    """
    # If strategy is specified, start with that
    if strategy:
        try:
            config = DeviceMapper.get_strategy(strategy)
        except KeyError:
            warnings.warn(
                f"Strategy '{strategy}' not found, using auto-detect",
                UserWarning,
                stacklevel=2,
            )
            config = DeviceConfig.auto_detect()
    else:
        # No strategy, use auto-detect as base
        config = DeviceConfig.auto_detect()

    # Override with explicit parameters if provided
    if device is not None:
        config.device = device
    if dtype is not None:
        config.dtype = dtype
    if mixed_precision is not None:
        config.mixed_precision = mixed_precision

    return config
