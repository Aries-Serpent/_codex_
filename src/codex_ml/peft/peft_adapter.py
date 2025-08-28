from __future__ import annotations

try:
    from peft import LoraConfig, get_peft_model  # optional dependency
except Exception:  # pragma: no cover
    LoraConfig = None
    get_peft_model = None


def apply_lora(model, cfg: dict | None = None):
    """Attach LoRA adapters via `peft` when available; otherwise return model unchanged."""
    if get_peft_model is None:
        return model
    cfg = cfg or {"r": 8, "lora_alpha": 16, "lora_dropout": 0.05, "bias": "none"}
    try:
        config = LoraConfig(task_type="CAUSAL_LM", **cfg)
        return get_peft_model(model, config)
    except Exception:
        # As a graceful fallback ensure the returned object exposes `peft_config`
        setattr(model, "peft_config", cfg)
        return model
