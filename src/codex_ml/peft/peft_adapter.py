from __future__ import annotations

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

from typing import Any, Dict, Optional

# Optional dependency: peft
try:  # pragma: no cover - optional dependency
    from peft import LoraConfig, get_peft_model  # type: ignore
except Exception:  # pragma: no cover - `peft` not installed
    LoraConfig = None  # type: ignore
    get_peft_model = None  # type: ignore

__all__ = ["apply_lora", "LoraConfig", "get_peft_model", "DEFAULT_CFG"]

# Baseline defaults; can be overridden via cfg or kwargs
DEFAULT_CFG: Dict[str, Any] = {
    "r": 8,
    "lora_alpha": 16,
    "lora_dropout": 0.05,
    "bias": "none",
    # task_type is handled specially; kept out of defaults to avoid surprising LoraConfig kwargs
    # "task_type": "CAUSAL_LM",
}


def apply_lora(model: Any, cfg: Optional[Dict[str, Any]] = None, /, **overrides: Any) -> Any:
    """Attach LoRA adapters via `peft` when available.

    Parameters
    ----------
    model:
        The base model to wrap with LoRA adapters.
    cfg:
        Optional configuration mapping. Supported keys mirror those of
        `peft.LoraConfig`, such as:
          - r, lora_alpha, lora_dropout, bias
          - target_modules, modules_to_save, init_lora_weights, etc.
          - task_type (default: "CAUSAL_LM")
    **overrides:
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
    """
    # Merge defaults + provided config + explicit overrides
    merged: Dict[str, Any] = dict(DEFAULT_CFG)
    if cfg:
        merged.update(cfg)
    if overrides:
        merged.update(overrides)

    # task_type is a top-level parameter for LoraConfig
    task_type = merged.get("task_type", "CAUSAL_LM")

    # If peft is not available, annotate and return original model
    if get_peft_model is None or LoraConfig is None:  # pragma: no cover
        try:
            setattr(model, "peft_config", dict(merged))
        except Exception:
            # Silently ignore attribute setting failures
            pass
        return model

    # Build kwargs for LoraConfig without duplicating task_type
    config_kwargs = dict(merged)
    config_kwargs.pop("task_type", None)

    try:
        config = LoraConfig(task_type=task_type, **config_kwargs)  # type: ignore[call-arg]
        adapted = get_peft_model(model, config)
        try:
            setattr(adapted, "peft_config", dict(merged))
        except Exception:
            pass
        return adapted
    except Exception:  # pragma: no cover - defensive fallback
        # If adaptation fails for any reason, return original model with config attached
        try:
            setattr(model, "peft_config", dict(merged))
        except Exception:
            pass
        return model
