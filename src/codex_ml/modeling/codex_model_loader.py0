from __future__ import annotations

from typing import Any, Optional

from transformers import AutoModelForCausalLM

__all__ = ["load_model_with_optional_lora"]


def _maybe_import_peft():
    try:
        from peft import LoraConfig, get_peft_model  # type: ignore

        return LoraConfig, get_peft_model
    except Exception:  # pragma: no cover - optional dep
        return None, None


def load_model_with_optional_lora(
    name_or_path: str,
    *,
    dtype: Optional[str] = None,
    device_map: Optional[str] = None,
    lora_enabled: bool = False,
    lora_r: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.05,
    lora_target_modules: Optional[list[str]] = None,
    **kw: Any,
):
    """Load ``AutoModelForCausalLM`` and optionally apply LoRA adapters."""

    torch_dtype = getattr(__import__("torch"), dtype) if dtype else None
    model = AutoModelForCausalLM.from_pretrained(
        name_or_path, torch_dtype=torch_dtype, device_map=device_map, **kw
    )
    if not lora_enabled:
        return model
    LoraConfig, get_peft_model = _maybe_import_peft()
    if LoraConfig is None or get_peft_model is None:
        return model
    cfg = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=lora_target_modules or ["q_proj", "v_proj"],
        task_type="CAUSAL_LM",
    )
    return get_peft_model(model, cfg)

