from __future__ import annotations

"""LoRA integration for Codex models.

When the optional ``peft`` package is available, this helper wraps a model with
low-rank adapters. Configuration can be supplied either via a dictionary or
keyword arguments (``r``, ``lora_alpha``, ``lora_dropout`` and ``bias``). If
``peft`` is not installed, the function returns the model unchanged after
attaching the merged configuration for inspection.
"""

try:  # optional dependency
    from peft import LoraConfig, get_peft_model
except Exception:  # pragma: no cover - peft not installed
    LoraConfig = None  # type: ignore
    get_peft_model = None  # type: ignore


DEFAULT_CFG: dict = {
    "r": 8,
    "lora_alpha": 16,
    "lora_dropout": 0.05,
    "bias": "none",
}


def apply_lora(model, cfg: dict | None = None, **overrides):
    """Apply LoRA adapters via ``peft`` when available.

    Args:
        model: The base model to wrap.
        cfg: Optional configuration dictionary.
        **overrides: Keyword arguments that override configuration values.

    Returns:
        The adapted model or the original model if ``peft`` is unavailable.
        In all cases, the merged configuration is attached to the returned
        model under ``peft_config`` for inspection.
    """

    merged = {**DEFAULT_CFG, **(cfg or {}), **overrides}

    if get_peft_model is None:
        setattr(model, "peft_config", merged)
        return model

    try:
        config = LoraConfig(task_type="CAUSAL_LM", **merged)
        adapted = get_peft_model(model, config)
        setattr(adapted, "peft_config", merged)
        return adapted
    except Exception:
        setattr(model, "peft_config", merged)
        return model
