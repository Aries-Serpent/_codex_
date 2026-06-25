"""
Tokenizer Hf Module

This module provides functionality for tokenizer hf.

Usage:
    from interfaces.tokenizer_hf import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import warnings  # noqa: E402
from typing import Any  # noqa: E402

from codex_ml.tokenization.hf_adapter import HFTokenizerAdapter as _HFTokenizerAdapter  # noqa: E402

try:  # pragma: no cover - optional torch dependency
    import torch
except (ImportError, AttributeError):  # pragma: no cover - defensive
    torch = None

try:  # pragma: no cover - optional import cycle guard
    from codex_ml.training.device_strategy import DeviceConfig
except (ImportError, AttributeError):  # pragma: no cover - fallback for lightweight environments
    DeviceConfig = None

warnings.warn(
    "codex_ml.interfaces.tokenizer_hf is deprecated; import HFTokenizerAdapter "
    "from codex_ml.tokenization.hf_adapter instead.",
    DeprecationWarning,
    stacklevel=2,
)

HFTokenizerAdapter = _HFTokenizerAdapter


def align_tensor_to_device(
    tensor: torch.Tensor,
    device_config: DeviceConfig | None,
    *,
    fallback_dtype: torch.dtype | None = None,
) -> Any:
    """Ensure tokenizer tensors respect the configured dtype/device."""

    if torch is None or device_config is None:
        return tensor
    target_device = torch.device(device_config.device)
    target_dtype = device_config.dtype if device_config.dtype is not None else fallback_dtype
    if target_dtype is None:
        return tensor.to(device=target_device)
    return tensor.to(device=target_device, dtype=target_dtype)


__all__ = ["HFTokenizerAdapter", "align_tensor_to_device"]
