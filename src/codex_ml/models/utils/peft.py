"""Optional PEFT/LoRA integration helpers."""

from __future__ import annotations

from typing import Any, Optional

DEFAULT_TASK_TYPE = "CAUSAL_LM"


def apply_lora_if_available(
    model: Any,
    *,
    r: int = 8,
    alpha: int = 16,
    dropout: float = 0.05,
    task_type: Optional[str] = None,
) -> Any:
    """Wrap ``model`` with LoRA adapters when ``peft`` is installed.

    The helper keeps LoRA strictly optional—if ``peft`` (and its dependencies)
    are unavailable the function simply returns ``model`` unchanged. This keeps
    training code paths offline-friendly while enabling quick experimentation
    when the dependency is present.
    """

    try:  # pragma: no cover - optional dependency
        from peft import LoraConfig, get_peft_model  # type: ignore
    except Exception:  # pragma: no cover - dependency missing
        return model

    cfg = LoraConfig(
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        bias="none",
        task_type=task_type or DEFAULT_TASK_TYPE,
    )
    return get_peft_model(model, cfg)


__all__ = ["apply_lora_if_available"]
