# [Integration]: LoRA adapter integration with graceful fallbacks
# Generated: 2025-08-31 08:51:51 | Author: mbaetiong
"""LoRA integration for Codex models.

This module provides a lightweight, optional integration with the `peft` package
to apply Low-Rank Adaptation (LoRA) adapters to models.

Features combined from both branches:
- Optional import of `peft` with graceful fallbacks when unavailable.
- Unified defaults with the ability to pass a configuration mapping and/or
  keyword overrides (e.g., r, lora_alpha, lora_dropout, bias, target_modules).
- Attaches the merged configuration to the returned model under `peft_config`
  for inspection regardless of whether adaptation was applied.
- Robust error handling: if adaptation fails, returns the original model with
  `peft_config` set.

Usage:
    adapted = apply_lora(model, {"r": 16, "lora_alpha": 32}, target_modules=["q_proj"])
    # or with overrides
    adapted = apply_lora(model, lora_dropout=0.1, bias="none")

If `peft` is not installed, the function returns the original model unchanged
after attaching the merged configuration for inspection.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import inspect  # noqa: E402
from typing import Any, Optional  # noqa: E402

from codex.logging.structured_logger import logger

# Optional dependency: peft
try:  # pragma: no cover - optional dependency
    from peft import LoraConfig, get_peft_model
except (ImportError, AttributeError):  # pragma: no cover - `peft` not installed
    LoraConfig = None
    get_peft_model = None

__all__ = ["DEFAULT_CFG", "LoraConfig", "apply_lora", "get_peft_model"]

# Baseline defaults; can be overridden via cfg or kwargs
DEFAULT_CFG: dict[str, Any] = {
    "r": 8,
    "lora_alpha": 16,
    "lora_dropout": 0.05,
    "bias": "none",
    "task_type": "CAUSAL_LM",
}


def apply_lora(model: Any, cfg: Optional[dict[str, Any]] = None, /, **overrides: Any) -> Any:
    """Attach LoRA adapters via `peft` when available.

    Parameters
    ----------
    model : Any
        The base model to wrap with LoRA adapters.
    cfg : Optional[dict[str, Any]], default=None
        Optional configuration mapping. Supported keys mirror those of
        `peft.LoraConfig`, such as:
          - r, lora_alpha, lora_dropout, bias
          - target_modules, modules_to_save, init_lora_weights, etc.
          - task_type (default: "CAUSAL_LM")
    **overrides : Any
        Keyword arguments that override both the defaults and `cfg` values.

    Returns
    -------
    Any
        The adapted model when `peft` is installed and adaptation succeeds.
        If the dependency is missing or configuration fails, the original model
        is returned unchanged, but will expose a `peft_config` attribute for
        introspection.

    Notes
    -----
    - The effective configuration (defaults merged with `cfg` and `overrides`)
      is attached to the returned object under `peft_config` for diagnostics.
    - The `task_type` value (if present) is used to initialize `LoraConfig` and
      is preserved in the attached `peft_config`.
    - Graceful fallback: if `peft` is unavailable or adaptation fails, returns
      the original model with configuration attached for inspection.

    Examples
    --------
    >>> # Basic usage with defaults
    >>> adapted = apply_lora(model)

    >>> # Custom configuration
    >>> config = {"r": 16, "lora_alpha": 32, "target_modules": ["q_proj", "v_proj"]}
    >>> adapted = apply_lora(model, config)

    >>> # Override parameters
    >>> adapted = apply_lora(model, lora_dropout=0.1, bias="lora_only")

    >>> # Check applied configuration
    >>> logger.info(adapted.peft_config)
    """
    # Merge defaults + provided config + explicit overrides
    merged: dict[str, Any] = dict(DEFAULT_CFG)
    if cfg:
        merged.update(cfg)
    if overrides:
        merged.update(overrides)

    # task_type is a top-level parameter for LoraConfig
    task_type = str(merged.get("task_type", "CAUSAL_LM"))

    # If peft is not available, annotate and return original model
    if get_peft_model is None or LoraConfig is None:  # pragma: no cover
        try:
            model.peft_config = dict(merged)
        except (ImportError, AttributeError):
            logger.warning("Exception occurred", exc_info=True)
            # Silently ignore attribute setting failures
        return model

    # Build kwargs for LoraConfig without duplicating task_type or control flags
    control_keys = {"task_type", "enabled"}
    config_kwargs = {k: v for k, v in merged.items() if k not in control_keys}
    if LoraConfig is not None:
        try:
            sig = inspect.signature(LoraConfig)
            # Check if **kwargs is in signature (VAR_KEYWORD parameter)
            has_var_keyword = any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            )
            if not has_var_keyword:
                # Only filter if there's no **kwargs (strict signature)
                valid_keys = set(sig.parameters)
                config_kwargs = {k: v for k, v in config_kwargs.items() if k in valid_keys}
        except (TypeError, ValueError):  # pragma: no cover - signature unavailable
            logger.debug("Suppressed exception in handler", exc_info=True)
    try:
        config = LoraConfig(task_type=task_type, **config_kwargs)
        adapted = get_peft_model(model, config)
        try:
            adapted.peft_config = dict(merged)
        except (ImportError, AttributeError):
            logger.warning("Exception occurred", exc_info=True)
            # Ignore attribute setting failures but continue with adapted model
        return adapted
    except (ImportError, AttributeError):  # pragma: no cover - defensive fallback
        # If adaptation fails for any reason, return original model with config attached
        try:
            model.peft_config = dict(merged)
        except (ImportError, AttributeError):
            logger.warning("Exception occurred", exc_info=True)
            # Ignore attribute setting failures in fallback case
        return model
