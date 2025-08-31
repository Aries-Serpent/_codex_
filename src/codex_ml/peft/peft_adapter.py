from __future__ import annotations

try:
    from peft import LoraConfig, get_peft_model  # optional dependency
except Exception:  # pragma: no cover
    LoraConfig = None
    get_peft_model = None


def apply_lora(model, cfg: dict | None = None, **overrides):
    """Attach LoRA adapters via :mod:`peft` when available.

    Parameters
    ----------
    model:
        The base model to wrap with LoRA adapters.
    cfg:
        Optional configuration mapping passed to :class:`peft.LoraConfig`.
    **overrides:
        Additional hyper-parameters (e.g. ``r``, ``lora_alpha``) that override
        both the defaults and ``cfg`` values.
    """

    merged = {"r": 8, "lora_alpha": 16, "lora_dropout": 0.05, "bias": "none"}
    if cfg:
        merged.update(cfg)
    if overrides:
        merged.update(overrides)

    task_type = merged.get("task_type", "CAUSAL_LM")
    config_data = merged.copy()
    config_data.pop("task_type", None)

    if get_peft_model is None or LoraConfig is None:  # pragma: no cover
        setattr(model, "peft_config", merged)
        return model

    try:
        config = LoraConfig(task_type=task_type, **config_data)
        adapted = get_peft_model(model, config)
        setattr(adapted, "peft_config", merged)
        return adapted
    except Exception:  # pragma: no cover
        setattr(model, "peft_config", merged)
        return model
