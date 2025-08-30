from __future__ import annotations

"""LoRA integration for Codex models.

When the optional ``peft`` package is available, this helper wraps a model with
low-rank adapters. Configuration can be supplied as a dictionary containing
``r``, ``lora_alpha``, ``lora_dropout`` and ``bias``. If ``peft`` is not
installed, the function returns the model unchanged.
"""

try:  # optional dependency
    from peft import LoraConfig, get_peft_model
except Exception:  # pragma: no cover - peft not installed
    LoraConfig = None  # type: ignore
    get_peft_model = None  # type: ignore


def apply_lora(model, cfg: dict | None = None):
    """Apply LoRA adapters via ``peft`` when available.

    Args:
        model: The base model to wrap.
        cfg: Optional configuration dictionary.

    Returns:
        The adapted model or the original model if ``peft`` is unavailable.
    """

    if get_peft_model is None:
        return model

    cfg = cfg or {"r": 8, "lora_alpha": 16, "lora_dropout": 0.05, "bias": "none"}
    try:
        config = LoraConfig(task_type="CAUSAL_LM", **cfg)
        return get_peft_model(model, config)
    except Exception:
        # Fall back to returning the original model but expose the attempted config
        setattr(model, "peft_config", cfg)
        return model
