from __future__ import annotations

"""Lightweight helper around optional ``peft`` LoRA utilities."""

try:  # optional dependency
    from peft import LoraConfig, get_peft_model
except Exception:  # pragma: no cover - ``peft`` not installed
    LoraConfig = None
    get_peft_model = None


def apply_lora(model, cfg: dict | None = None):
    """Attach LoRA adapters via ``peft`` when available.

    Parameters
    ----------
    model:
        The model to which LoRA adapters should be attached.
    cfg:
        Optional dictionary of hyper-parameters. Supported keys mirror those of
        :class:`peft.LoraConfig` such as ``r``, ``lora_alpha``, ``lora_dropout``,
        ``bias``, ``target_modules``, ``modules_to_save`` and
        ``init_lora_weights``.

    Returns
    -------
    The model wrapped with LoRA adapters when ``peft`` is installed.  If the
    dependency is missing or configuration fails, the original model is returned
    unchanged but will expose a ``peft_config`` attribute for introspection.
    """

    if get_peft_model is None:
        # ``peft`` not installed – surface config for callers to inspect
        setattr(model, "peft_config", cfg or {})
        return model

    defaults = {
        "r": 8,
        "lora_alpha": 16,
        "lora_dropout": 0.05,
        "bias": "none",
    }
    params = {**defaults, **(cfg or {})}

    try:
        config = LoraConfig(task_type="CAUSAL_LM", **params)
        model = get_peft_model(model, config)
        setattr(model, "peft_config", params)
        return model
    except Exception:
        # As a graceful fallback ensure the returned object exposes ``peft_config``
        setattr(model, "peft_config", params)
        return model
